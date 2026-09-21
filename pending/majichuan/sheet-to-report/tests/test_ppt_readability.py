import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from chapter_pptx_readability import cover_lines,prepare_scene,negative_caption,units

class ReadabilityTest(unittest.TestCase):
    def test_cover_prefers_semantic_boundaries_and_preserves_words(self):
        for title,width,size in [('全渠道经营复盘｜2025-06（合成练习\n数据）',1110,64),('2025-06经营复盘｜规模、渠道与退款',1110,64),('全渠道经营复盘｜2025-06（合成练习数据）',700,66)]:
            wrapped=cover_lines(title,width,size,245)
            self.assertEqual(''.join(wrapped.split()),''.join(title.split()))
            self.assertTrue(all(units(row)<=width/size*.88 for row in wrapped.splitlines()))
        self.assertIn('\n（合成练习数据）',cover_lines('全渠道经营复盘｜2025-06（合成练习数据）',1110,64,245))
        self.assertEqual(cover_lines('Business Review',1110,64,245),'Business Review')

    def test_signed_caption_is_bound_and_chart_stays_native(self):
        view={'kind':'bar','labels':['内容种草','付费广告'],'series':[{'label':'收入差','values':[1490839.38,-565390.51],'unit':'元'}]}
        projection={'slides':[{'kind':'chart'}],'chart_views':{'c':view},'selection':{'config':{'palette':{'ink':'15324D'}}}}
        scene={'source':'fixed','scene':[[{'kind':'chart','id':'c','x':65,'y':207,'w':1135,'h':383}]]}
        before=json.dumps((projection,scene),ensure_ascii=False)
        prepared=prepare_scene(projection,scene)
        self.assertEqual(before,json.dumps((projection,scene),ensure_ascii=False))
        chart,caption=prepared['scene'][0]
        self.assertEqual(chart['kind'],'chart');self.assertEqual(chart['id'],'c')
        self.assertEqual(caption['t'],'负向项：付费广告 -565,390.51元')
        self.assertLessEqual(caption['y']+caption['h'],chart['y'])
        self.assertEqual(chart['y']+chart['h'],590)

    def test_positive_charts_do_not_change(self):
        view={'kind':'bar','labels':['a'],'series':[{'label':'v','values':[1],'unit':'元'}]}
        p={'slides':[{'kind':'chart'}],'chart_views':{'c':view},'selection':{'config':{'palette':{'ink':'15324D'}}}}
        s={'scene':[[{'kind':'chart','id':'c','x':65,'y':207,'w':1135,'h':383}]]}
        self.assertEqual(prepare_scene(p,s),s)

    def test_capacity_does_not_silently_clip(self):
        with self.assertRaises(ValueError):cover_lines('经营复盘'*30,200,64,100)

if __name__=='__main__':unittest.main()
