from pathlib import Path
import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from paint_motion import build_painting

import stroke_paths as stroke_utils

ASSET_DIRECTORY = None
FONT_PATH = None
FONT_INDEX = 0


def configure_assets(directory, font_path, font_index=0):
    global ASSET_DIRECTORY, FONT_PATH, FONT_INDEX
    ASSET_DIRECTORY = Path(directory)
    ASSET_DIRECTORY.mkdir(parents=True, exist_ok=True)
    FONT_PATH = str(font_path)
    FONT_INDEX = int(font_index)


def lengths(points):
    return stroke_utils.calculate_lengths(points)


def ordered_paths(mask):
    skeleton = stroke_utils.thin_ink(mask)
    paths = [np.array(path) for path in stroke_utils.trace_strokes(skeleton)]
    covered = np.zeros(skeleton.shape, dtype=bool)
    for path in paths:
        coordinates = np.rint(path).astype(int)
        covered[coordinates[:, 1], coordinates[:, 0]] = True
    # Follow only adjacent leftover pixels. A branch starts a new physical stroke.
    pending = set(zip(*np.where(skeleton & ~covered)))
    while pending:
        point = min(pending)
        chain = []
        while point in pending:
            pending.remove(point)
            y, x = point
            chain.append([x, y])
            neighbors = sorted((y+dy, x+dx) for dy in (-1,0,1) for dx in (-1,0,1)
                               if (dy or dx) and (y+dy, x+dx) in pending)
            if not neighbors:
                break
            point = neighbors[0]
        if len(chain) == 1:
            chain.append([chain[0][0]+.01, chain[0][1]])
        paths.append(np.array(chain, dtype=float))
    if not paths:
        ys, xs = np.where(mask)
        if not len(xs):
            return []
        paths = [np.array([[xs[0],ys[0]],[xs[0]+.01,ys[0]]],dtype=float)]
    covered[:] = False
    for path in paths:
        coordinates = np.rint(path).astype(int)
        covered[coordinates[:,1],coordinates[:,0]] = True
    # Keep broad stroke tips within nib distance without connecting across blank paper.
    while True:
        distance, nearest = ndimage.distance_transform_edt(~covered, return_indices=True)
        distance[~mask] = 0
        y, x = np.unravel_index(np.argmax(distance), mask.shape)
        if distance[y,x] <= 7:
            break
        anchor = np.array([nearest[1,y,x],nearest[0,y,x]],dtype=float)
        extension = np.linspace(anchor,[x,y],max(2,math.ceil(distance[y,x])+1))
        coordinates = np.rint(extension).astype(int)
        if not mask[coordinates[:,1],coordinates[:,0]].all():
            extension = np.array([[x,y],[x+.01,y]],dtype=float)
            coordinates = np.rint(extension).astype(int)
        paths.append(extension)
        covered[coordinates[:,1],coordinates[:,0]] = True
    oriented = [path if tuple(path[0][::-1]) <= tuple(path[-1][::-1]) else path[::-1] for path in paths]
    return sorted(oriented,key=lambda path:(round(path[:,1].min()/16),path[:,0].min()))


def time_paths(paths, shape, start=0., duration=1.):
    reveal = np.full(shape, np.inf, dtype=np.float32)
    segments = []
    weights = [max(1., lengths(path)[-1]) for path in paths]
    travel_weights = [max(3., np.linalg.norm(paths[i + 1][0] - paths[i][-1]) * .22) for i in range(len(paths) - 1)]
    total = sum(weights) + sum(travel_weights)
    cursor = start
    for index, (path, weight) in enumerate(zip(paths, weights)):
        path_length = lengths(path)
        interval = duration * weight / max(1, total)
        for point, distance in zip(path, path_length):
            x, y = np.rint(point).astype(int)
            if 0 <= y < shape[0] and 0 <= x < shape[1]:
                reveal[y, x] = min(reveal[y, x], cursor + interval * distance / max(.001, path_length[-1]))
        segments.append({'kind':'ink','start':cursor,'end':cursor + interval,'points':path.tolist(),'lengths':path_length.tolist()})
        cursor += interval
        if index + 1 < len(paths):
            transit = duration * travel_weights[index] / max(1, total)
            segments.append({'kind':'travel','start':cursor,'end':cursor + transit,'points':[path[-1].tolist(),paths[index + 1][0].tolist()]})
            cursor += transit
    if np.isfinite(reveal).any():
        _, nearest = ndimage.distance_transform_edt(~np.isfinite(reveal), return_indices=True)
        reveal = reveal[nearest[0], nearest[1]]
    return reveal, segments


def save_asset(name, pixels, reveal, segments, extra=None):
    Image.fromarray(pixels).save(ASSET_DIRECTORY / f'{name}.png')
    np.savez_compressed(ASSET_DIRECTORY / f'{name}.npz', reveal=reveal.astype(np.float32))
    metadata = {'name':name,'width':pixels.shape[1],'height':pixels.shape[0],'segments':segments,**(extra or {})}
    (ASSET_DIRECTORY / f'{name}.json').write_text(json.dumps(metadata,ensure_ascii=False))
    return metadata


def measure_text(text, font, margin=5):
    """Reserve actual glyph bearings and descenders, not the nominal font size."""
    placements, cursor = [], 0.
    for character in text:
        placements.append((character, round(cursor), font.getbbox(character)))
        cursor += font.getlength(character)
    left = min([0] + [x + bounds[0] for _, x, bounds in placements])
    top = min([0] + [bounds[1] for _, _, bounds in placements])
    right = max([math.ceil(cursor)] + [x + bounds[2] for _, x, bounds in placements])
    bottom = max([0] + [bounds[3] for _, _, bounds in placements])
    return {'width': right-left+2*margin, 'height': bottom-top+2*margin,
            'origin': [margin-left, margin-top], 'placements': placements}


def build_text(name, text, size, color='#302C26'):
    font = ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)
    layout = measure_text(text, font)
    width, height = layout['width'], layout['height']
    layer = Image.new('RGBA',(width,height))
    glyphs = []
    for character, offset, bounds in layout['placements']:
        glyph = Image.new('L',(max(1,bounds[2]-bounds[0]),max(1,bounds[3]-bounds[1])))
        glyph_draw = ImageDraw.Draw(glyph)
        glyph_draw.text((-bounds[0],-bounds[1]),character,font=font,fill=255)
        mask = np.array(glyph) > 30
        paths = ordered_paths(mask)
        left = layout['origin'][0]+offset+bounds[0]
        top = layout['origin'][1]+bounds[1]
        glyphs.append((character, left, top, np.array(glyph), paths))
        ink = Image.new('RGBA',glyph.size,color)
        ink.putalpha(glyph)
        layer.alpha_composite(ink,(left,top))
    pixels = np.array(layer)
    reveal = np.full((height, width), np.inf, dtype=np.float32)
    owners = np.full((height, width), -1, dtype=np.int16)
    segments, character_intervals = [], []
    weights = [max(4., sum(lengths(path)[-1] for path in paths)) for _, _, _, _, paths in glyphs]
    cursor = 0.
    for index, ((character, left, top, glyph, paths), weight) in enumerate(zip(glyphs, weights)):
        interval = weight / sum(weights)
        if paths:
            local, strokes = time_paths(paths, glyph.shape, cursor, interval * .94)
            glyph_height, glyph_width = glyph.shape
            mask = glyph > 0
            patch = reveal[top:top+glyph_height, left:left+glyph_width]
            patch[mask] = local[mask]
            owners[top:top+glyph_height, left:left+glyph_width][mask] = index
            for stroke in strokes:
                stroke['points'] = (np.array(stroke['points']) + [left, top]).tolist()
                stroke['character_index'] = index
            segments.extend(strokes)
        character_intervals.append({'index':index,'character':character,'start':cursor,'end':cursor+interval})
        cursor += interval
    metadata = save_asset(name,pixels,reveal,segments,{'type':'handwritten_text','text':text,'font_size':size,
                          'text_origin':layout['origin'],'safe_margin':5,'characters':character_intervals})
    np.savez_compressed(ASSET_DIRECTORY / f'{name}.npz', reveal=reveal, owners=owners)
    return metadata


def build_brush(name, width, height, color, style='highlight', line_width=None):
    if style == 'highlight':
        radius = min(20, height / 2.4)
        xs = np.linspace(radius,width - radius,max(5,math.ceil(width / 3)))
        amplitude = max(0,height / 2 - radius)
        ys = height / 2 + amplitude * np.sin((xs - radius) / 17 * math.pi)
        points = np.c_[xs,ys]
    elif style == 'underline':
        radius = (line_width or 5) / 2
        xs = np.linspace(4,width - 4,max(3,math.ceil(width / 2)))
        points = np.c_[xs,height / 2 + 2 * np.sin(xs / max(1,width) * math.pi * 1.4)]
    elif style == 'circle':
        radius = (line_width or 5) / 2
        theta = np.linspace(-math.pi / 3,5 * math.pi / 3,max(50,round((width + height) / 2)))
        points = np.c_[width / 2 + (width / 2 - radius - 3) * np.cos(theta),height / 2 + (height / 2 - radius - 3) * np.sin(theta)]
    elif style == 'box':
        radius = (line_width or 4) / 2
        corners = np.array([[5,5],[width-6,4],[width-5,height-6],[4,height-5],[5,5]],dtype=float)
        points = np.vstack([np.linspace(a,b,max(2,round(np.linalg.norm(b-a)/2))) for a,b in zip(corners[:-1],corners[1:])])
    else:
        raise ValueError(style)
    rgba = np.zeros((height,width,4),dtype=np.uint8)
    rgba[:,:,:3] = tuple(int(color[index:index+2],16) for index in (1,3,5))
    reveal = np.full((height,width),np.inf,dtype=np.float32)
    distances = lengths(points)
    yy,xx = np.ogrid[:height,:width]
    for point,distance in zip(points,distances):
        footprint = (xx-point[0])**2 + (yy-point[1])**2 <= radius**2
        reveal[footprint] = np.minimum(reveal[footprint],distance/max(.01,distances[-1]))
    rgba[:,:,3] = np.isfinite(reveal).astype(np.uint8)*255
    segments=[{'kind':'brush','start':0.,'end':1.,'points':points.tolist(),'lengths':distances.tolist(),'radius':radius}]
    return save_asset(name,rgba,reveal,segments,{'type':'marker_'+style})


def build_illustration(name, source_path, max_width, max_height, crop=None, parts=None, outline_mask_path=None):
    artwork=Image.open(source_path).convert('RGBA')
    source_size = artwork.size
    if crop is not None:
        left, top, right, bottom = crop
        if not (0 <= left < right <= artwork.width and 0 <= top < bottom <= artwork.height):
            raise ValueError('Artwork crop must stay inside the source image')
        artwork = artwork.crop(tuple(crop))
    if artwork.getextrema()[3] == (255, 255):
        rgb = np.array(artwork)[:, :, :3]
        alpha = np.rint(np.clip((253-rgb.min(axis=2).astype(float))/18, 0, 1)*255).astype(np.uint8)
        artwork = Image.fromarray(np.dstack([rgb, alpha]))
    scale = min(max_width/artwork.width, max_height/artwork.height)
    artwork = artwork.resize((max(1,round(artwork.width*scale)),max(1,round(artwork.height*scale))),Image.Resampling.LANCZOS)
    pixels=np.array(artwork)
    maximum=pixels[:,:,:3].max(axis=2)
    alpha=pixels[:,:,3]
    red,green,blue=[pixels[:,:,channel].astype(float) for channel in range(3)]
    cool_ink=(blue>=red+4)&(blue>=green-4)&(red<218)
    dark=((maximum<125)|cool_ink)&(alpha>30)
    depth=ndimage.distance_transform_edt(dark)
    outline=dark&(depth<5.2)
    ink_weight=dark.astype(float)*np.clip((6.-depth)/1.,0,1)
    if outline_mask_path is not None:
        explicit = Image.open(outline_mask_path).convert('L')
        if explicit.size != source_size:
            raise ValueError('Outline mask must match source image dimensions before crop')
        if crop is not None:
            explicit = explicit.crop(tuple(crop))
        explicit = explicit.resize(artwork.size,Image.Resampling.NEAREST)
        outline = (np.array(explicit)>127)&(alpha>0)
        ink_weight = outline.astype(float)
    fill_mask=(alpha>0)&(ink_weight<.99)
    ys, xs = np.where(alpha > 0)
    if not len(xs):
        raise ValueError('Illustration is empty after background removal')
    if not parts:
        raise ValueError('Illustrations require model-designed semantic parts with ordered normalized polygons')
    owners = np.full(alpha.shape, -1, dtype=np.int16)
    part_masks, names = [], []
    for index, part in enumerate(parts):
        if not part.get('id') or part['id'] in names:
            raise ValueError('Every semantic part needs a unique id')
        names.append(part['id'])
        region = Image.new('L', artwork.size)
        polygon = np.asarray(part['polygon'], dtype=float)
        if len(polygon)<3 or not ((polygon>=0)&(polygon<=1)).all():
            raise ValueError('Part polygons must have >=3 normalized vertices')
        ImageDraw.Draw(region).polygon([tuple(point) for point in polygon * [artwork.width-1,artwork.height-1]],fill=255)
        mask = (np.array(region)>0)&(alpha>0)&(owners<0)
        # Preserve held objects and other occluding shapes for their own semantic part.
        for excluded_polygon in part.get('exclude_polygons', []):
            excluded_polygon = np.asarray(excluded_polygon, dtype=float)
            if len(excluded_polygon)<3 or not ((excluded_polygon>=0)&(excluded_polygon<=1)).all():
                raise ValueError('Excluded polygons must have >=3 normalized vertices')
            excluded_region = Image.new('L', artwork.size)
            ImageDraw.Draw(excluded_region).polygon([tuple(point) for point in excluded_polygon * [artwork.width-1,artwork.height-1]],fill=255)
            mask &= np.array(excluded_region)==0
        # A background prop visible between curls belongs to the prop, not the head polygon.
        for exclusion in part.get('exclude_hsv', []):
            if len(exclusion)!=4 or not (0<=exclusion[0]<=exclusion[1]<=360 and 0<=exclusion[2]<=1 and 0<=exclusion[3]<=1):
                raise ValueError('exclude_hsv requires [hue_min, hue_max, saturation_min, value_min]')
            hsv=np.asarray(artwork.convert('RGB').convert('HSV'),dtype=float)
            hue=hsv[:,:,0]*360/255
            excluded=(hue>=exclusion[0])&(hue<=exclusion[1])&(hsv[:,:,1]>=exclusion[2]*255)&(hsv[:,:,2]>=exclusion[3]*255)
            mask &= ~excluded
        if not mask.any():
            raise ValueError(f'Empty semantic part: {part["id"]}')
        owners[mask] = index
        part_masks.append(mask)
    if ((alpha>0)&(owners<0)).any():
        raise ValueError('Semantic parts do not cover every visible pixel; inspect and repair masks')
    for part, mask in zip(parts, part_masks):
        if not (outline & mask).any():
            raise ValueError('Part has no drawable outline; prepare a contour layer/mask before generation: '+part['id'])
    ink_reveal = np.full(alpha.shape,np.inf,dtype=np.float32)
    color_reveal = np.full(alpha.shape,np.inf,dtype=np.float32)
    segments, part_reports = [], []
    part_paths = [ordered_paths(outline&mask) for mask in part_masks]
    ink_weights = [sum(max(1.,lengths(path)[-1]) for path in paths) for paths in part_paths]
    ink_duration = .59 if fill_mask.any() else 1.
    cursor = 0.
    previous_tip = np.array([xs.mean(),ys.mean()])
    for index,(mask,paths,weight) in enumerate(zip(part_masks,part_paths,ink_weights)):
        interval = ink_duration*weight/max(1.,sum(ink_weights))
        local,strokes = time_paths(paths,alpha.shape,cursor,interval*.96)
        ink_reveal[mask] = local[mask]
        for stroke in strokes:
            stroke.update(part_id=names[index],part_index=index,phase='outline')
        segments.extend(strokes)
        part_reports.append({'id':names[index],'index':index,'outline_start':cursor,'outline_end':cursor+interval})
        if paths:
            previous_tip=paths[-1][-1]
        cursor+=interval
    fill_weights = [math.sqrt(int((mask&fill_mask).sum())) for mask in part_masks]
    fill_start = ( .61 if sum(ink_weights) else 0. ) if fill_mask.any() else 1.
    cursor=fill_start
    painting={'region_count':0,'brush_pass_count':0,'maximum_brush_radius':0}
    for index,(mask,weight) in enumerate(zip(part_masks,fill_weights)):
        interval=(1.-fill_start)*weight/max(1.,sum(fill_weights))
        local,strokes,statistics=build_painting(mask&fill_mask,previous_tip,cursor,interval*.96,pixels)
        color_reveal[mask]=local[mask]
        for stroke in strokes:
            stroke.update(part_id=names[index],part_index=index,phase='fill')
        segments.extend(strokes)
        part_reports[index].update(fill_start=cursor,fill_end=cursor+interval)
        if strokes:
            previous_tip=np.array(strokes[-1]['points'][-1])
        for field in ('region_count','brush_pass_count'):
            painting[field]+=statistics[field]
        painting['maximum_brush_radius']=max(painting['maximum_brush_radius'],statistics['maximum_brush_radius'])
        cursor+=interval
    # A two-channel reveal retains sharp contours before the localized color passes.
    Image.fromarray(pixels).save(ASSET_DIRECTORY/f'{name}.png')
    np.savez_compressed(ASSET_DIRECTORY/f'{name}.npz',ink=ink_reveal,color=color_reveal,ink_weight=ink_weight.astype(np.float32),owners=owners)
    metadata={'name':name,'type':'illustration','source':str(source_path),'width':artwork.width,'height':artwork.height,'segments':segments,'painting':painting,'parts':part_reports}
    (ASSET_DIRECTORY/f'{name}.json').write_text(json.dumps(metadata))
    return metadata
