"""Build marker passes and reveal pixels only where the moving tip has passed."""
import math
import numpy as np
from scipy import ndimage
from PIL import Image


def path_lengths(points):
    return np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]


def stamp(mask, point, radius, target, value):
    x, y = point
    left, right = max(0, math.floor(x - radius)), min(mask.shape[1], math.ceil(x + radius) + 1)
    top, bottom = max(0, math.floor(y - radius)), min(mask.shape[0], math.ceil(y + radius) + 1)
    if right <= left or bottom <= top:
        return
    ys, xs = np.ogrid[top:bottom, left:right]
    footprint = ((xs - x) ** 2 + (ys - y) ** 2 <= radius ** 2) & mask[top:bottom, left:right]
    patch = target[top:bottom, left:right]
    patch[footprint] = np.minimum(patch[footprint], value)


def regional_passes(mask, region_id):
    ys, xs = np.where(mask)
    coordinates = np.c_[xs, ys].astype(float)
    center = coordinates.mean(axis=0)
    if len(coordinates) < 50:
        point = coordinates[np.argmin(np.linalg.norm(coordinates - center, axis=1))]
        return [(np.array([point, point + [.3, .2]]), 10.0)]
    eigenvalues, eigenvectors = np.linalg.eigh(np.cov(coordinates.T))
    axis = eigenvectors[:, -1]
    angle = math.atan2(axis[1], axis[0]) + .16 * math.sin(region_id * 1.71)
    direction = np.array([math.cos(angle), math.sin(angle)])
    across = np.array([-direction[1], direction[0]])
    along_values = (coordinates - center) @ direction
    across_values = (coordinates - center) @ across
    radius = float(np.clip(math.sqrt(len(coordinates)) / 7, 10, 20))
    lower, upper = across_values.min(), across_values.max()
    rows = max(1, math.ceil((upper - lower) / (radius * 1.35)))
    offsets = np.linspace(lower + min(radius * .42, (upper - lower) / 2),
                          upper - min(radius * .42, (upper - lower) / 2), rows)
    passes = []
    for row_index, offset in enumerate(offsets):
        band = np.abs(across_values - offset) <= radius * .86
        projected = np.sort(np.unique(np.rint(along_values[band])))
        if not len(projected):
            continue
        runs = np.split(projected, np.where(np.diff(projected) > radius * 1.7)[0] + 1)
        if row_index % 2:
            runs = runs[::-1]
        for run in runs:
            first, last = run[0] - 1, run[-1] + 1
            count = max(2, math.ceil((last - first) / 2.5) + 1)
            along = np.linspace(first, last, count)
            if row_index % 2:
                along = along[::-1]
            bend = 1.5 * np.sin(np.linspace(0, math.pi, count))
            points = center + along[:, None] * direction + (offset + bend)[:, None] * across
            passes.append((points, radius))
    return passes


def build_painting(fill_mask, previous_tip, start, duration=6.9, pixels=None):
    if not fill_mask.any():
        return np.full(fill_mask.shape, np.inf, dtype=np.float32), [], {
            'region_count': 0, 'brush_pass_count': 0, 'maximum_brush_radius': 0}
    # Palette components keep clothes, skin and furniture in separate painting passes.
    palette = np.array(Image.fromarray(pixels[:, :, :3]).quantize(colors=8, method=Image.Quantize.FASTOCTREE))
    solid_interior = ndimage.distance_transform_edt(fill_mask & (pixels[:, :, 3] > 240)) > 3
    labels = np.zeros(fill_mask.shape, dtype=np.int32)
    count = 0
    for color_id in np.unique(palette):
        grouped = ndimage.binary_closing((palette == color_id) & solid_interior, iterations=3)
        components, component_count = ndimage.label(grouped)
        sizes = np.bincount(components.ravel())
        for component in range(1, component_count + 1):
            if sizes[component] < 220:
                continue
            count += 1
            labels[components == component] = count
    if count == 0:
        labels, count = ndimage.label(fill_mask)
    _, nearest = ndimage.distance_transform_edt(labels == 0, return_indices=True)
    labels = labels[nearest[0], nearest[1]]
    pending = [label for label in range(1, count + 1) if np.any(fill_mask & (labels == label))]
    centers = {label: ndimage.center_of_mass(fill_mask & (labels == label)) for label in pending}
    previous = np.asarray(previous_tip, dtype=float)
    operations = []
    covered = np.full(fill_mask.shape, np.inf, dtype=np.float32)
    while pending:
        region_id = min(pending, key=lambda label: (round(centers[label][0]/16),centers[label][1]))
        pending.remove(region_id)
        mask = (labels == region_id) & fill_mask
        passes = regional_passes(mask, region_id)
        for points, radius in passes:
            distance = np.linalg.norm(previous - points[0])
            # A lifted tip travels between passes; each pass itself leaves a solid marker footprint.
            operations.append({'kind':'travel', 'points':np.array([previous, points[0]]), 'weight':max(3.0, distance * .38)})
            lengths = path_lengths(points)
            operations.append({'kind':'color', 'points':points, 'lengths':lengths, 'radius':radius,
                               'region':region_id, 'weight':max(10.0, lengths[-1])})
            for point in points:
                stamp(mask, point, radius, covered, 0)
            previous = points[-1]
        remaining = mask & ~np.isfinite(covered)
        while remaining.any():
            ys, xs = np.where(remaining)
            nearest = np.argmin((xs - previous[0]) ** 2 + (ys - previous[1]) ** 2)
            point = np.array([xs[nearest], ys[nearest]], dtype=float)
            points = np.array([point, point + [.5, .3]])
            operations.append({'kind':'travel','points':np.array([previous, point]), 'weight':max(3.0,np.linalg.norm(point - previous) * .38)})
            operations.append({'kind':'color','points':points,'lengths':path_lengths(points),'radius':15.,'region':region_id,'weight':10.})
            stamp(mask, point, 15, covered, 0)
            stamp(mask, points[-1], 15, covered, 0)
            previous = points[-1]
            remaining = mask & ~np.isfinite(covered)
    total_weight = sum(operation['weight'] for operation in operations)
    reveal_times = np.full(fill_mask.shape, np.inf, dtype=np.float32)
    segments = []
    cursor = start
    for operation in operations:
        interval = duration * operation['weight'] / total_weight
        points = operation['points']
        segment = {'kind':operation['kind'],'start':cursor,'end':cursor + interval,'points':points.tolist()}
        if operation['kind'] == 'color':
            lengths = operation['lengths']
            segment.update(lengths=lengths.tolist(),radius=operation['radius'],region=operation['region'])
            mask = (labels == operation['region']) & fill_mask
            for point, distance in zip(points, lengths):
                timestamp = cursor + interval * distance / max(.001,lengths[-1])
                stamp(mask, point, operation['radius'], reveal_times, timestamp)
        segments.append(segment)
        cursor += interval
    assert np.isfinite(reveal_times[fill_mask]).all(), 'Unpainted pixels must receive a real brush pass.'
    return reveal_times, segments, {'region_count':count,'brush_pass_count':sum(s['kind'] == 'color' for s in segments),
                                   'maximum_brush_radius':max(s.get('radius',0) for s in segments)}
