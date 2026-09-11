"""Recompose chart choices from frozen evidence without rewriting business conclusions."""
import argparse
import copy
from pathlib import Path
from html_analysis import read,verify,compose,sealed,skill_manifest,write_new,file_sha256,canonical_sha256


def revise(model,proposal,correction,output):
    verify(model);verify(model['snapshot'])
    if canonical_sha256(proposal)!=model['proposal_sha256']:
        raise ValueError('必须提供源模型对应的原始提案')
    if set(correction)!={'source_model_sha256','charts'} or correction['source_model_sha256']!=model['sha256']:
        raise ValueError('图表修订来源或字段不匹配')
    replacements=correction['charts']
    ids={c['id'] for c in proposal['chapters']}
    if not isinstance(replacements,dict) or not replacements or not set(replacements)<=ids:
        raise ValueError('图表修订只能引用既有章节')
    revised_proposal=copy.deepcopy(proposal)
    for chapter in revised_proposal['chapters']:
        if chapter['id'] in replacements:
            chapter['charts']=copy.deepcopy(replacements[chapter['id']])
    revised=compose(model['snapshot'],revised_proposal)
    for key in ('action_revision','summary_revision','chart_revision'):
        if key in model:revised[key]=copy.deepcopy(model[key])
    for key in model:
        if key not in {'chapters','chart_views','proposal_sha256','sha256'} and revised.get(key)!=model[key]:
            raise ValueError('图表修订意外改变其他内容: '+key)
    for old,new in zip(model['chapters'],revised['chapters']):
        if {k:v for k,v in old.items() if k!='charts'}!={k:v for k,v in new.items() if k!='charts'}:
            raise ValueError('图表修订不得改变正文、结论或证据范围')
    revised['chart_revision']={'kind':'chart-selection/1','source_model_sha256':model['sha256'],
        'calculation_snapshot_sha256':model['snapshot']['sha256'],'execution_skill':skill_manifest(),
        'correction_sha256':canonical_sha256(correction),'additional_calculations':0}
    revised=sealed(revised)
    from html_chapter_renderer import render
    page=render(revised)
    dest=Path(output)/('final-'+revised['sha256'][:16]);dest.mkdir(parents=True,exist_ok=False)
    write_new(dest/'report_model.json',revised);write_new(dest/'proposal.json',revised_proposal)
    (dest/'report.html').write_text(page,encoding='utf-8')
    write_new(dest/'html_qa.json',{'contract':'passed','model_sha256':revised['sha256'],
        'html_sha256':file_sha256(dest/'report.html'),'visual':'not_verified','human_review':'pending','additional_calculations':0})
    return dest


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['model','proposal','correction','output']:p.add_argument('--'+name,required=True)
    a=p.parse_args();print(revise(read(a.model),read(a.proposal),read(a.correction),a.output))
