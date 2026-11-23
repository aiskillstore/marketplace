"""Check explicit, version-bound SFX and seam review records; never edits a draft."""
from __future__ import annotations
import argparse, json, hashlib, math
from pathlib import Path
from types import SimpleNamespace

def load(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)

def template(input_path, report_path, qc_path, seam_scan=None):
    report=load(report_path)
    if report['output_sha256']!=sha(input_path):raise ValueError('Stale edit report')
    effects=[x for x in report.get('sfx',[]) if x.get('mix_role')=='sfx']
    from picture_range import required_ranges
    primary = load(seam_scan).get('primary_video_track_id') if seam_scan else None
    ranges = required_ranges(report, primary)
    return dict(schema_version=1,input_sha256=sha(input_path),edit_report_sha256=sha(report_path),
        qc_sha256=sha(qc_path),seam_scan=str(Path(seam_scan).resolve()) if seam_scan else None,
        seam_decisions=None,audition_manifests=[],
        picture_ranges=[dict(range_id=r['range_id'],scan='',decisions='') for r in ranges],
        sfx=[dict(segment_id=e['segment_id'],event_id=e.get('event_id'),target_us=e['target_us'],
                  anchor='',event_class=e.get('event_class'),
                  candidates_compared=[{'selection_evidence':''},{'selection_evidence':''}],
                  attack_checked=False,scene_relevance_checked=False,dialogue_clear=False,
                  listened_solo=False,listened_ab=False,decision='pending',reason='',measurement_exception_reason='') for e in effects],
        sfx_density_exception='',qc_resolutions=[],scope='Fill only after actual picture/listening review. Agent review is allowed; this is not a new user approval request.')

def candidate_identity(path, event):
    path=Path(path).resolve(strict=True)
    evidence=load(path)
    if evidence.get('schema_version')!=1:raise ValueError('Unsupported selection evidence schema')
    row,source,measured=evidence['plan_sfx_row'],evidence['source'],evidence['measurements']
    if Path(row['selection_evidence']).resolve()!=path:raise ValueError('Selection evidence self-reference differs')
    if Path(row['path']).resolve()!=Path(measured['path']).resolve():raise ValueError('Selected WAV and measurement path differ')
    if sha(source['path'])!=source['sha256']:raise ValueError('Original candidate source changed')
    if sha(row['path'])!=row['sha256'] or measured.get('sha256')!=row['sha256']:
        raise ValueError('Selected candidate WAV or measurement hash changed')
    for key in ('selected_start_us','selected_end_us','confirmed_attack_us'):
        if type(source.get(key)) is not int:raise ValueError('Invalid source range/attack: '+key)
    for key in ('source_start_us','source_duration_us','attack_offset_us','target_us'):
        if type(row.get(key)) is not int:raise ValueError('Invalid selected range: '+key)
    start,end,attack=source['selected_start_us'],source['selected_end_us'],source['confirmed_attack_us']
    if not 0<=start<=attack<end or row['source_start_us']!=0:
        raise ValueError('Candidate source range does not contain its confirmed attack')
    if row['attack_offset_us']!=attack-start or not 0<=row['attack_offset_us']<row['source_duration_us']:
        raise ValueError('Candidate attack offset differs from its selected range')
    if measured.get('analyzed_duration_us')!=row['source_duration_us'] or measured.get('silent') is not False:
        raise ValueError('Candidate duration or audible-signal measurement differs')
    if row['target_us']!=event.get('input_target_us'):
        raise ValueError('Candidate must use the exact input-timeline anchor of the selected SFX')
    for key in ('event_id','event_class'):
        if evidence.get(key)!=row.get(key) or row.get(key)!=event.get(key):
            raise ValueError('Candidate event differs: '+key)
    if any(key in source for key in ('salient_attacks_us','salient_attack_offsets_us','attack_body_ms','selection_end_us','fade_out_us')):
        attacks, offsets = source.get('salient_attacks_us'), source.get('salient_attack_offsets_us')
        body, selection_end = source.get('attack_body_ms'), source.get('selection_end_us')
        declared_fade = source.get('fade_out_us')
        if type(selection_end) is not int or selection_end != end or type(declared_fade) is not int:
            raise ValueError('Candidate advanced selection/fade declaration is incomplete')
        if not isinstance(attacks,list) or not isinstance(offsets,list) or not isinstance(body,(int,float)) or isinstance(body,bool) or not math.isfinite(body) or body < 0:
            raise ValueError('Candidate multi-attack body declaration is invalid')
        if any(type(t) is not int or not start <= t < end for t in attacks):
            raise ValueError('Candidate salient attack is outside its selected source range')
        if attacks != sorted(set([attack,*attacks])) or offsets != [t-start for t in attacks]:
            raise ValueError('Candidate salient attack offsets differ from source times')
        hold = round(body*1000)
        rate = measured.get('analysis_rate')
        if not isinstance(rate,(int,float)) or rate <= 0:
            raise ValueError('Candidate multi-attack measurement rate is invalid')
        available = row['source_duration_us']-(attacks[-1]-start)-hold
        if end < attacks[-1]+hold or available < -math.ceil(1e6/rate):
            raise ValueError('Candidate selection truncates a declared attack body')
        fade = row.get('fade_out_us')
        if type(fade) is not int or fade != declared_fade or not 0 <= fade <= max(0,available):
            raise ValueError('Candidate fade attenuates a declared attack body')
    return source['sha256'],start,end,attack


def check_review(input_path, report_path, qc_path, review_path, seam_scan=None):
    report,qc,review=load(report_path),load(qc_path),load(review_path)
    issues=[]
    if report.get('output_sha256')!=sha(input_path):raise ValueError('Edit report is stale')
    for key,path in [('input_sha256',input_path),('edit_report_sha256',report_path),('qc_sha256',qc_path)]:
        if review.get(key)!=sha(path):raise ValueError('Review hash differs: '+key)
    if qc.get('input_sha256')!=sha(input_path):raise ValueError('QC is stale')
    effects={e['segment_id']:e for e in report.get('sfx',[]) if e.get('mix_role')=='sfx'}
    beats={b['id']:b for b in report.get('beat_events',[])}
    for event in effects.values():
        selection=event.get('selection_evidence')
        if not selection or not Path(selection).is_file() or sha(selection)!=event.get('selection_evidence_sha256'):
            issues.append(event['segment_id']+': measured source selection evidence missing or changed')
        beat=beats.get(event.get('event_id'))
        if not beat or beat.get('sound_action')!='sfx':issues.append(event['segment_id']+': bind SFX event_id to a beat with sound_action=sfx')
        elif not beat.get('screen_change') and not beat.get('dialogue_anchor'):
            issues.append(event['segment_id']+': beat has no observed picture or word anchor')
    for beat in beats.values():
        # Legacy non-SFX/BGM-only plans do not acquire a new audio review requirement.
        if not effects and beat.get('sound_action') != 'sfx':continue
        if beat.get('sound_action') not in ('sfx','original','bgm_change','silence'):
            issues.append(beat['id']+': choose a concrete sound_action')
        elif beat['sound_action']=='sfx' and not any(e.get('event_id')==beat['id'] for e in effects.values()):
            issues.append(beat['id']+': planned SFX has no rendered audio segment')
    if effects and 30_000_000 <= report.get('duration_us',0) <= 60_000_000 and len(effects)<3 and not review.get('sfx_density_exception'):
        issues.append('Fewer than three independent SFX: record concrete story/original-sound reason instead of adding arbitrary sounds')
    rows=review.get('sfx',[])
    if len(rows)!=len(effects) or {r.get('segment_id') for r in rows}!=set(effects):
        raise ValueError('Review must cover every new SFX exactly once')
    auditions={}
    for raw in review.get('audition_manifests',[]):
        path=Path(raw).resolve(strict=True); value=load(path)
        from audio_audition import verify_manifest
        verify_manifest(path)
        if value.get('kind') != 'native_sfx_audition' or value.get('status') != 'rendered':
            raise ValueError('Expected completed native SFX audition evidence')
        if value.get('input_sha256')!=sha(input_path) or value.get('edit_report_sha256')!=sha(report_path):
            raise ValueError('Audition belongs to another version')
        for dep,checksum in value.get('dependencies',{}).items():
            if not Path(dep).is_file() or sha(dep)!=checksum:raise ValueError('Audition dependency changed: '+dep)
        for event in value.get('events',[]):
            selected=effects.get(event.get('segment_id'))
            if selected is None or event.get('event_id')!=selected.get('event_id') or event.get('target_us')!=selected.get('target_us'):
                raise ValueError('Audition event identity or target differs from the edit report')
            if event['segment_id'] in auditions:raise ValueError('Duplicate audition event: '+event['segment_id'])
            auditions[event['segment_id']]=event
    for row in rows:
        key=row['segment_id'];event=effects[key]
        if row.get('target_us')!=event['target_us']:raise ValueError('SFX review target changed: '+key)
        if row.get('decision')!='pass':issues.append(key+': pending SFX decision')
        if any(row.get(k) is not True for k in ('attack_checked','scene_relevance_checked','dialogue_clear','listened_solo','listened_ab')):
            issues.append(key+': actual solo/AB/anchor/dialogue review incomplete')
        if not row.get('anchor') or not row.get('reason'):issues.append(key+': concrete anchor/reason missing')
        if row.get('event_id')!=event.get('event_id') or row.get('event_class')!=event.get('event_class'):
            issues.append(key+': review event identity changed')
        candidates=row.get('candidates_compared',[])
        if not isinstance(candidates,list) or len(candidates)<2:
            issues.append(key+': provide two prepared candidate selection evidence objects')
        else:
            identities=[]
            for index,candidate in enumerate(candidates,1):
                try:
                    if not isinstance(candidate,dict) or set(candidate)!={'selection_evidence'}:
                        raise ValueError('Use an object containing only selection_evidence')
                    identity=candidate_identity(candidate['selection_evidence'],event)
                    identities.append(identity)
                except (OSError,ValueError,KeyError,TypeError) as exc:
                    issues.append(f'{key}: candidate {index} evidence invalid: {exc}')
            if len(set(identities))<2:
                issues.append(key+': compare two different source hashes/ranges/attacks, not repeated paths')
            else:
                try:
                    selected=candidate_identity(event['selection_evidence'],event)
                    if selected not in identities:issues.append(key+': compared candidates must include the final selected SFX')
                except (OSError,ValueError,KeyError,TypeError) as exc:
                    issues.append(key+': final selection evidence invalid: '+str(exc))
        if key not in auditions:issues.append(key+': native solo/with/without audition evidence missing')
        else:
            for warning in auditions[key].get('warnings',[]):
                if warning in ('very_low_solo_attack_check_source_selection_and_attack', 'possible_masking_compare_AB_or_duck_competing_layer'):
                    if not row.get('measurement_exception_reason'):
                        issues.append(key+': '+warning+'; fix source/duck or explain the actual AB result')
    from picture_range import required_ranges, validate_range
    primary = load(seam_scan).get('primary_video_track_id') if seam_scan else None
    expected_ranges = required_ranges(report, primary)
    supplied_ranges = review.get('picture_ranges', [])
    indexed_ranges = {r.get('range_id'):r for r in supplied_ranges if isinstance(r,dict)}
    if len(indexed_ranges)!=len(supplied_ranges) or set(indexed_ranges)!={r['range_id'] for r in expected_ranges}:
        raise ValueError('Picture range reviews must match every bridge/reframe operation exactly once')
    if expected_ranges and not seam_scan:
        issues.append('Picture range reviews require a bound seam scan and primary video track')
    for expected in expected_ranges:
        supplied = indexed_ranges[expected['range_id']]
        if not supplied.get('scan') or not supplied.get('decisions'):
            issues.append(expected['range_id']+': continuous picture range or decisions missing')
            continue
        scan_path = Path(supplied['scan']).resolve(strict=True)
        scan = load(scan_path)
        for field in ('range_id','operation','start_us','end_us','track_id','primary_video_track_id'):
            if scan.get(field)!=expected.get(field):
                raise ValueError('Picture range identity differs from edit report: '+expected['range_id']
                                 +f'; {field}: {scan.get(field)!r} != {expected.get(field)!r}')
        if scan.get('input_sha256')!=sha(input_path) or scan.get('edit_report_sha256')!=sha(report_path):
            raise ValueError('Picture range belongs to another edited timeline or edit report')
        result = validate_range(SimpleNamespace(scan=scan_path,decisions=supplied['decisions']))
        issues += [expected['range_id']+': '+issue for issue in result['issues']]
    if seam_scan:
        from seam_review import validate_review
        scan_path=Path(seam_scan).resolve(strict=True);scan=load(scan_path)
        if not review.get('seam_scan') or Path(review['seam_scan']).resolve()!=scan_path:
            raise ValueError('Review seam_scan path differs from the supplied scan')
        if scan.get('input_sha256')!=sha(input_path) or scan.get('edit_report_sha256')!=sha(report_path):
            raise ValueError('Seam scan belongs to another edited timeline or edit report')
        required=scan.get('required_review_count',0)
        if required and not review.get('seam_decisions'):issues.append('seam decisions missing')
        elif review.get('seam_decisions'):
            result=validate_review(SimpleNamespace(scan=scan_path,decisions=review['seam_decisions']))
            issues += result.get('issues',[])
    resolutions=review.get('qc_resolutions',[])
    for issue in qc.get('issues',[]):
        if not any(r.get('issue')==issue and r.get('decision')=='accepted_with_evidence' and r.get('reason') and r.get('evidence') for r in resolutions):
            issues.append('QC unresolved: '+issue)
    return dict(status='needs_review' if issues else 'passed',issues=issues,
        input_sha256=sha(input_path),review_sha256=sha(review_path),sfx_count=len(effects),
        picture_range_count=len(expected_ranges),
        evidence_scope='Hash-bound declared human/agent observations plus actual generated evidence; software cannot prove semantic suitability or honesty of listening declarations')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True);parser.add_argument('--edit-report',required=True)
    parser.add_argument('--qc',required=True);parser.add_argument('--seam-scan')
    parser.add_argument('--review');parser.add_argument('--template')
    args=parser.parse_args()
    try:
        if bool(args.review)==bool(args.template):raise ValueError('Choose --review or --template')
        if args.template:
            save(args.template,template(args.input,args.edit_report,args.qc,args.seam_scan))
            result={'status':'review_required','template':str(Path(args.template).resolve())}
        else:result=check_review(args.input,args.edit_report,args.qc,args.review,args.seam_scan)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (OSError,ValueError,KeyError,TypeError) as exc:parser.exit(1,'Review check unavailable: '+str(exc)+'\n')

if __name__=='__main__':main()
