"""Regression cases for visible defects: future glyphs, parts and early fills."""
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import stroke_assets
from video_job import find_font
from video_verifier import match_reveal_to_tip


class DrawingContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.directory=Path(self.temporary.name)
        font,index=find_font({})
        stroke_assets.configure_assets(self.directory,font,index)

    def tearDown(self):
        self.temporary.cleanup()

    def test_adjacent_characters_never_borrow_previous_glyph_strokes(self):
        metadata=stroke_assets.build_text('text','今晚，花十分钟',85)
        maps=np.load(self.directory/'text.npz')
        alpha=np.array(Image.open(self.directory/'text.png'))[:,:,3]
        self.assertTrue(np.isfinite(maps['reveal'][alpha>0]).all())
        for character in metadata['characters']:
            mask=(maps['owners']==character['index'])&(alpha>0)
            if mask.any():
                self.assertGreaterEqual(float(maps['reveal'][mask].min())+1e-7,character['start'])
                self.assertLessEqual(float(maps['reveal'][mask].max()),character['end']+1e-7)
        distances,_=match_reveal_to_tip(metadata,maps['reveal'],alpha>0,{'ink'})
        self.assertLess(distances.max(),9)

    def test_text_keeps_complete_glyphs_including_bottoms_and_bearings(self):
        font_path,font_index=find_font({})
        cases=[('把顺利，留给准备',84),('允许事情出错',72),('gypj，准备好了。',60)]
        for index,(text,size) in enumerate(cases):
            font=ImageFont.truetype(font_path,size,index=font_index)
            metadata=stroke_assets.build_text('complete-'+str(index),text,size)
            actual=Image.open(self.directory/('complete-'+str(index)+'.png')).getchannel('A')
            reference=Image.new('L',(actual.width+400,actual.height+400))
            drawing=ImageDraw.Draw(reference)
            cursor=0.
            for character in text:
                drawing.text((200+round(cursor),200),character,font=font,fill=255)
                cursor+=font.getlength(character)
            origin_x,origin_y=metadata['text_origin']
            expected=reference.crop((200-origin_x,200-origin_y,
                                     200-origin_x+actual.width,200-origin_y+actual.height))
            self.assertEqual(np.count_nonzero(np.array(reference)),np.count_nonzero(np.array(actual)),text)
            np.testing.assert_array_equal(np.array(actual)>0,np.array(expected)>0,err_msg=text)
            left,top,right,bottom=actual.getbbox()
            self.assertGreaterEqual(min(left,top,actual.width-right,actual.height-bottom),5)

    def make_figure(self):
        image=Image.new('RGBA',(180,260))
        draw=ImageDraw.Draw(image)
        draw.ellipse((60,10,120,70),fill='#EAC4A5',outline='#252B39',width=4)
        draw.rectangle((83,70,97,90),fill='#EAC4A5',outline='#252B39',width=3)
        draw.rectangle((40,90,140,180),fill='#F1924A',outline='#252B39',width=4)
        draw.rectangle((55,180,80,250),fill='#557B8D',outline='#252B39',width=4)
        draw.rectangle((100,180,125,250),fill='#557B8D',outline='#252B39',width=4)
        path=self.directory/'source.png';image.save(path)
        parts=[{'id':name,'polygon':[[0,top],[1,top],[1,bottom],[0,bottom]]}
               for name,top,bottom in [('head',0,.28),('neck',.28,.345),('torso',.345,.695),('legs',.695,1)]]
        return path,parts

    def test_part_isolation_outline_then_fill_and_lifted_travel(self):
        path,parts=self.make_figure()
        metadata=stroke_assets.build_illustration('figure',path,180,260,parts=parts)
        maps=np.load(self.directory/'figure.npz')
        alpha=np.array(Image.open(self.directory/'figure.png'))[:,:,3]
        for part in metadata['parts']:
            owned=(maps['owners']==part['index'])&(alpha>0)
            ink=owned&(maps['ink_weight']>0)
            fill=owned&(maps['ink_weight']<1)
            if ink.any():
                self.assertGreaterEqual(float(maps['ink'][ink].min())+1e-7,part['outline_start'])
            if fill.any():
                self.assertGreaterEqual(float(maps['color'][fill].min())+1e-7,part['fill_start'])
                self.assertGreaterEqual(float(maps['color'][fill].min()),.60)
        fill=(alpha>0)&(maps['ink_weight']<.99)
        distances,radii=match_reveal_to_tip(metadata,maps['color'],fill,{'color'})
        self.assertTrue((distances<=radii+.04).all())
        self.assertTrue(any(segment['kind']=='travel' for segment in metadata['segments']))
        drawing=[segment for segment in metadata['segments'] if segment['kind']=='ink']
        self.assertGreater(len(drawing),4)

    def test_missing_or_incomplete_semantic_parts_stop_build(self):
        path,parts=self.make_figure()
        with self.assertRaisesRegex(ValueError,'require'):
            stroke_assets.build_illustration('missing',path,180,260)
        with self.assertRaisesRegex(ValueError,'cover every'):
            stroke_assets.build_illustration('incomplete',path,180,260,parts=parts[:2])

    def test_prop_seen_between_hair_stays_in_later_prop_part(self):
        image=Image.new('RGBA',(80,80))
        drawing=ImageDraw.Draw(image)
        drawing.rectangle((10,10,60,60),fill='#203A56')
        drawing.rectangle((22,22,32,32),fill='#EEA050')
        source=self.directory/'overlap.png';image.save(source)
        contour=Image.new('L',(80,80))
        contour_draw=ImageDraw.Draw(contour)
        contour_draw.rectangle((10,10,60,60),outline=255,width=3)
        contour_draw.rectangle((22,22,32,32),outline=255,width=2)
        contour.save(self.directory/'contour.png')
        whole=[[0,0],[1,0],[1,1],[0,1]]
        metadata=stroke_assets.build_illustration('overlap',source,80,80,parts=[
            {'id':'head','polygon':whole,'exclude_hsv':[[20,60,.24,.3]]},
            {'id':'umbrella','polygon':whole}],outline_mask_path=self.directory/'contour.png')
        maps=np.load(self.directory/'overlap.npz')
        self.assertEqual(maps['owners'][25,25],1)
        self.assertGreaterEqual(float(maps['color'][25,25])+1e-7,metadata['parts'][1]['fill_start'])


if __name__=='__main__':
    unittest.main()
