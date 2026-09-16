"""Add authored headings without changing frozen analysis or earlier revisions."""
import argparse
import copy
from pathlib import Path
from html_analysis import read, verify, compose, sealed, skill_manifest, write_new, file_sha256, canonical_sha256
from summary_contract import validate_summary


def revise(model, proposal, correction, output):
    verify(model)
    verify(model['snapshot'])
    if canonical_sha256(proposal) != model['proposal_sha256']:
        raise ValueError('必须提供源模型对应的原始提案')
    if set(correction) != {'source_model_sha256', 'headlines'} or correction['source_model_sha256'] != model['sha256']:
        raise ValueError('摘要修订来源不匹配')
    if not isinstance(correction['headlines'], list) or len(correction['headlines']) != len(proposal['summary']):
        raise ValueError('摘要标题与原结论必须逐条对应，不能增删结论')
    revised_proposal = copy.deepcopy(proposal)
    for item, headline in zip(revised_proposal['summary'], correction['headlines']):
        item['headline'] = headline
    revised = compose(model['snapshot'], revised_proposal)
    # Previous revision records are provenance, not freshly calculated content.
    for key in ('action_revision', 'summary_revision'):
        if key in model:
            revised[key] = copy.deepcopy(model[key])
    for key in model:
        if key not in {'summary', 'proposal_sha256', 'sha256'} and revised.get(key) != model[key]:
            raise ValueError('摘要修订意外改变其他内容: '+key)
    for old, new in zip(model['summary'], revised['summary']):
        if {k:v for k,v in old.items() if k != 'headline'} != {k:v for k,v in new.items() if k != 'headline'}:
            raise ValueError('摘要正文或来源不得改变')
    revised['summary_revision'] = {'kind':'summary-headline/1', 'source_model_sha256':model['sha256'],
        'calculation_snapshot_sha256':model['snapshot']['sha256'], 'execution_skill':skill_manifest(),
        'correction_sha256':canonical_sha256(correction), 'additional_calculations':0}
    validate_summary(revised)
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
        'summary_headlines':'passed','additional_calculations':0})
    return destination


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    for name in ['model','proposal','correction','output']:p.add_argument('--'+name,required=True)
    a=p.parse_args()
    print(revise(read(a.model),read(a.proposal),read(a.correction),a.output))
