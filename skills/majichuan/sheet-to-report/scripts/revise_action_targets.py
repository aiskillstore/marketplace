"""Action-only revision; frozen calculation provenance and budgets are preserved."""
import argparse
import copy
from pathlib import Path
from html_analysis import read, verify, compose, sealed, skill_manifest, write_new, file_sha256, canonical_sha256
from action_target_contract import validate_target


def revise(model, proposal, correction, output):
    verify(model)
    verify(model['snapshot'])
    if canonical_sha256(proposal) != model['proposal_sha256']:
        raise ValueError('必须提供源模型对应的原始提案')
    if set(correction) != {'source_model_sha256', 'actions'} or correction['source_model_sha256'] != model['sha256']:
        raise ValueError('行动修订来源不匹配')
    if len(correction['actions']) != len(proposal['actions']):
        raise ValueError('本入口不能增加或删除行动')
    for old, new in zip(proposal['actions'], correction['actions']):
        if {k:v for k,v in new.items() if k not in {'target', 'target_refs', 'suggested_role'}} != {k:v for k,v in old.items() if k not in {'target', 'target_refs', 'suggested_role'}}:
            raise ValueError('本入口只允许修订行动对象及建议协同角色')
    revised_proposal = {**copy.deepcopy(proposal), 'actions': copy.deepcopy(correction['actions'])}
    revised = compose(model['snapshot'], revised_proposal)
    if 'summary_revision' in model:
        revised['summary_revision'] = copy.deepcopy(model['summary_revision'])
    for action in revised['actions']:
        refs = {r for c in revised['chapters'] if c['id'] in action['chapter_ids'] for r in c['evidence_ids']}
        validate_target(action, revised['snapshot'], refs, require_binding=True)
    for key in model:
        if key not in {'actions', 'proposal_sha256', 'sha256', 'action_revision'} and revised.get(key) != model[key]:
            raise ValueError('行动修订意外改变其他内容: '+key)
    revised['action_revision'] = {'kind':'action-target/1', 'source_model_sha256':model['sha256'],
        'calculation_snapshot_sha256':model['snapshot']['sha256'], 'execution_skill':skill_manifest(),
        'correction_sha256':canonical_sha256(correction), 'additional_calculations':0}
    revised = sealed(revised)
    from html_chapter_renderer import render
    page = render(revised)
    destination = Path(output)/('final-'+revised['sha256'][:16])
    destination.mkdir(parents=True, exist_ok=False)
    write_new(destination/'report_model.json', revised)
    write_new(destination/'proposal.json', revised_proposal)
    (destination/'report.html').write_text(page,encoding='utf-8')
    write_new(destination/'html_qa.json', {'contract':'passed','model_sha256':revised['sha256'],
        'html_sha256':file_sha256(destination/'report.html'),'visual':'not_verified','human_review':'pending',
        'action_target_binding':'passed','additional_calculations':0})
    return destination


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    for name in ['model','proposal','correction','output']:p.add_argument('--'+name,required=True)
    a=p.parse_args()
    print(revise(read(a.model),read(a.proposal),read(a.correction),a.output))
