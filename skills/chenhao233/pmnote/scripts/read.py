"""Read PMNote public works, work thoughts, interviews and AI tools; Python 3.9+, no login."""
import argparse
import base64
import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
import urllib.error
import urllib.request
from urllib.parse import parse_qs, urlsplit

BASE = 'https://pmnote.ai'
COMMUNITY_ORIGIN = 'https://thilhtqbtpxbgszpnlwn.supabase.co'
UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')


class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urlsplit(req.full_url), urlsplit(newurl)
        old_origin = (old.scheme.lower(), old.hostname, old.port)
        new_origin = (new.scheme.lower(), new.hostname, new.port)
        if old_origin != new_origin:
            raise urllib.error.HTTPError(req.full_url, code, 'Cross-origin redirect blocked', headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request(url, payload=None, headers=None):
    data = None if payload is None else json.dumps(payload).encode()
    options = {'User-Agent': 'PMNote-Skill/1.2', **(headers or {})}
    if data is not None:
        options['Content-Type'] = 'application/json'
    # One retry for transient transport errors, never for an HTTP denial.
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, data=data, headers=options)
            with urllib.request.build_opener(SameOriginRedirect()).open(req, timeout=25) as response:
                raw = response.read(10_000_001)
            if len(raw) > 10_000_000:
                raise ValueError('Public response exceeds 10 MB; nothing truncated')
            return raw.decode('utf-8')
        except urllib.error.HTTPError as error:
            raise ValueError('Public source HTTP ' + str(error.code)) from None
        except (urllib.error.URLError, TimeoutError):
            if attempt:
                raise ValueError('Public source unavailable; no current result verified') from None


def get_json(url):
    return json.loads(request(url))


def label(value):
    return str(value or '').replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ').replace('\r', ' ').replace('<', '&lt;').replace('>', '&gt;')


def canonical(entry_id):
    if not UUID.fullmatch(entry_id):
        raise ValueError('Invalid public interview id')
    return BASE + '/community/experiences/#entry=' + entry_id


class PublicConfig(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.values = dict(attrs)


class Interviews:
    def __init__(self):
        parser = PublicConfig()
        parser.feed(request(BASE + '/community/experiences/'))
        attrs = getattr(parser, 'values', {})
        url, key = attrs.get('data-community-url', ''), attrs.get('data-community-key', '')
        if url != COMMUNITY_ORIGIN or not key:
            raise ValueError('Public interview connection missing; use the website browser')
        # Only the publishable value already shipped to anonymous website visitors.
        # It stays in memory; no account token, cookie or private configuration is read.
        self.url = url + '/functions/v1/community'
        self.headers = {'Origin': BASE, 'apikey': key}

    def call(self, action, payload):
        if action not in ('interviews_list', 'interviews_detail'):
            raise ValueError('Only anonymous public reads are supported')
        return json.loads(request(self.url, {'action': action, 'payload': payload}, self.headers))

    def listing(self, query=''):
        if len(query) > 200:
            raise ValueError('Use short generic topic keywords')
        items, seen, total = [], set(), None
        for page in range(500):
            result = self.call('interviews_list', {'page': page, 'q': query})
            if not isinstance(result.get('items'), list) or not isinstance(result.get('hasMore'), bool):
                raise ValueError('Incomplete public interview list')
            if len(result['items']) > 20 or (result['hasMore'] and not result['items']):
                raise ValueError('Invalid public interview page; no pagination progress')
            if total is None:
                total = result.get('total')
            if result.get('total') != total:
                raise ValueError('Interview list changed while paging; retry a new snapshot')
            for item in result['items']:
                validate_interview(item)
                if item['id'] in seen:
                    raise ValueError('Duplicate interview while paging')
                seen.add(item['id'])
                items.append(item)
            if not result['hasMore']:
                # Older live deployments expose hasMore without a total.
                # When supplied, total is an additional completeness check.
                if total is not None and (not isinstance(total, int) or total != len(items)):
                    raise ValueError('Incomplete interview coverage')
                return items
        raise ValueError('Interview pagination limit reached; incomplete result rejected')

    def detail(self, entry_id):
        canonical(entry_id)
        item = self.call('interviews_detail', {'id': entry_id})
        validate_interview(item)
        if item['id'] != entry_id:
            raise ValueError('Interview detail identity mismatch')
        return item


def validate_interview(item):
    canonical(item.get('id', ''))
    if item.get('status') != 'published' or not item.get('sharer') or not (item.get('title') or item.get('originalTitle')):
        raise ValueError('Not a published attributed interview')


def interview_markdown(item):
    validate_interview(item)
    lines = ['# ' + label(item.get('title') or item['originalTitle']), '',
             '原文：' + canonical(item['id']), '分享人 @' + label(item['sharer']), '',
             '内容范围：PMNote 当前公开分享文字；面试题与作者复盘按原文区分，不代表 Hao 本人的经历或建议。', '']
    for key, title in [('company', '公司'), ('role', '原岗位'), ('roundLabel', '轮次'), ('recruitmentType', '招聘类型'), ('interviewDate', '面试时间'), ('outcome', '结果')]:
        if item.get(key):
            lines.append(title + '：' + label(item[key]))
    if item.get('summary'):
        lines += ['', item['summary'], '']
    sections = item.get('sections') or []
    if sections:
        for section in sections:
            lines += ['## ' + label(section['heading']), '']
            lines += ['- ' + text for text in section['items']]
            lines += ['']
    elif isinstance(item.get('body'), str) and item['body'].strip():
        lines += [item['body'], '']
    else:
        raise ValueError('Public interview body missing; title is not evidence')
    return '\n'.join(lines)


def tool_text(slug):
    if not re.fullmatch(r'[a-z0-9-]+', slug):
        raise ValueError('Invalid tool slug')
    index = get_json(BASE + '/agent/knowledge/index.json')
    url = BASE + '/tools/' + slug + '/'
    entries = [row for row in index['entries'] if row['canonical'] == url]
    if len(entries) != 1:
        raise ValueError('No published tool text found; use the current tool directory')
    read_url = entries[0]['readUrl']
    if not re.fullmatch(re.escape(BASE) + r'/agent/knowledge/pages/[a-f0-9]+\.md', read_url):
        raise ValueError('Unexpected public tool read URL')
    body = request(read_url)
    if url not in body or len(body.split('---', 1)[-1].strip()) < 80:
        raise ValueError('Tool source body or canonical missing')
    return body


LIBRARY = '/community/library/data/'
MEDIA = ('article', 'video', 'podcast', 'news')
ROLES = ('', 'industry-observation', 'game-pm-practice', 'general-ai-governance', 'secondary-related')
PLATFORMS = {'bilibili': 'B站', 'xiaoyuzhou': '小宇宙', 'zhihu': '知乎', 'pmnote': '站内'}


def work_path(work_id):
    if not isinstance(work_id, str) or not 0 < len(work_id) <= 512 or any(ord(c) < 32 for c in work_id):
        raise ValueError('Invalid work identity')
    key = base64.urlsafe_b64encode(work_id.encode('utf-8')).decode('ascii').rstrip('=')
    return LIBRARY + 'works/' + key + '.json'


def search_key(value):
    value = unicodedata.normalize('NFKC', str(value)).lower()
    return ''.join(c for c in value if not c.isspace() and unicodedata.category(c)[0] not in ('P', 'Z'))


def source_url(value, *, allow_http=False):
    if not isinstance(value, str):
        raise ValueError('Missing public source URL')
    url = BASE + value if value.startswith('/') and not value.startswith('//') else value
    parsed = urlsplit(url)
    schemes = ('http', 'https') if allow_http else ('https',)
    if parsed.scheme not in schemes or not parsed.hostname or parsed.username or parsed.password or any(c.isspace() for c in url):
        raise ValueError('Invalid public source URL')
    return url


def target_url(identity):
    if identity.startswith('local:'):
        return identity[6:]
    platform, _, external = identity.partition(':')
    prefixes = {'bilibili': 'https://www.bilibili.com/video/',
                'xiaoyuzhou': 'https://www.xiaoyuzhoufm.com/episode/',
                'zhihu': 'https://zhuanlan.zhihu.com/p/'}
    return prefixes.get(platform, '') + external + ('/' if platform == 'bilibili' else '') if platform in prefixes else ''


def publication_key(value):
    if not value:
        return value
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        datetime.date.fromisoformat(value)
        return value
    date = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('Publication instant has no timezone')
    return date.astimezone(datetime.timezone.utc)


def publication_day(value):
    date = publication_key(value)
    if isinstance(date, datetime.datetime):
        return date.astimezone(datetime.timezone(datetime.timedelta(hours=8))).date().isoformat()
    return date or ''


def thought_title(identity):
    if not isinstance(identity, str) or not re.fullmatch(r'thought-[1-9][0-9]*', identity):
        raise ValueError('Invalid thought identity')
    return '工作思考 · 第' + identity[8:] + '期'


def primary_url(targets, media='all'):
    """Match the website reading intent without linking a metadata intermediary."""
    direct = []
    for target in targets:
        url = source_url(target['url'])
        parsed = urlsplit(url)
        query = parse_qs(parsed.query)
        if parsed.hostname == 'pmnote.ai' and parsed.path == '/community/library/' and ('work' in query or query.get('panel') == ['sources']):
            continue
        direct.append(target)
    playable = [t for t in direct if not (t.get('local', t.get('platform') == 'pmnote') and t['mediaType'] == 'podcast')]
    matches = [t for t in playable if media == 'all' or t['mediaType'] == media]
    chosen = next((t for t in matches if t.get('local', t.get('platform') == 'pmnote')), None)
    chosen = chosen or next(iter(matches), None) or next(iter(playable), None) or next(iter(direct), None)
    if chosen is None:
        raise ValueError('No direct public reading target')
    return source_url(chosen['url'])


def work_listing_markdown(work, media='all'):
    thought = work['id'].startswith('thought-')
    title = thought_title(work['id']) if thought else work['title']
    day = '' if thought else publication_day(work.get('publishedAt'))
    return '- [' + label(title) + '](' + primary_url(work['targets'], media) + ')' + (' · 发布于 ' + day if day else '')


class Works:
    """Read versioned public metadata, never platform bodies or private data.

    site_dir is an explicit offline candidate mode: it never falls back online.
    """
    def __init__(self, site_dir=None):
        self.site_dir = Path(site_dir).resolve() if site_dir else None
        self.index = self.load(LIBRARY + 'index.json')
        data = self.index
        if data.get('version') != 8 or data.get('full') is not True:
            raise ValueError('Unsupported or partial work index; use the website, not a stale index')
        if not isinstance(data.get('works'), list) or not isinstance(data.get('topics'), list):
            raise ValueError('Incomplete work index')
        self.topics = dict(data['topics'])
        if len(self.topics) != len(data['topics']) or len(self.topics) > 30:
            raise ValueError('Invalid work topics')
        self.redirects = data.get('redirects', {})
        if not isinstance(self.redirects, dict):
            raise ValueError('Invalid work redirects')
        self.works = [self.unpack(row) for row in data['works']]
        self.by_id = {w['id']: w for w in self.works}
        targets = [t for w in self.works for t in w['targets']]
        counts = data.get('counts', {})
        if (len(self.by_id) != len(self.works) or counts.get('works') != len(self.works)
                or counts.get('platformVariants') != sum(not t['local'] for t in targets)
                or counts.get('localTargets') != sum(t['local'] for t in targets)
                or len({t['id'] for t in targets}) != len(targets)):
            raise ValueError('Incomplete or duplicate work/variant coverage')
        for old in self.redirects:
            self.resolve(old)
        self.search_text = {w['id']: search_key(w['title'] + w['summary']) + w['searchExtra'] + search_key(' '.join(
            [w['id'], w['role'], *[self.topics[t] for t in w['topics']],
             *[v for t in w['targets'] for v in (t['id'], t['url'], t['platform'], PLATFORMS.get(t['platform'], ''), t['mediaType'])]]))
            for w in self.works}

    def load(self, path):
        if not path.startswith(LIBRARY) or '?' in path or '#' in path:
            raise ValueError('Unexpected work metadata path')
        if not self.site_dir:
            return get_json(BASE + path)
        file = (self.site_dir / path.lstrip('/')).resolve()
        if self.site_dir not in file.parents:
            raise ValueError('Work path escapes local candidate')
        try:
            raw = file.read_bytes()
        except OSError:
            raise ValueError('Local candidate metadata unavailable; no online fallback') from None
        if len(raw) > 10_000_000:
            raise ValueError('Work metadata exceeds 10 MB; nothing truncated')
        return json.loads(raw)

    def unpack(self, row):
        if not isinstance(row, list) or len(row) not in (9, 10):
            raise ValueError('Unexpected compact work row')
        identity, title, summary, media, topics, date, packed, role, extra = row[:9]
        work_path(identity)
        if (not isinstance(title, str) or not title or not isinstance(summary, str)
                or not isinstance(extra, str) or type(media) is not int or not 0 < media < 8
                or type(topics) is not int or not 0 <= topics < 2 ** len(self.topics)
                or type(role) is not int or not 0 <= role < len(ROLES) or not isinstance(packed, list)):
            raise ValueError('Invalid compact work fields')
        if type(date) in (int, float):
            date = datetime.datetime.fromtimestamp(date / 1000, datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        if not isinstance(date, str):
            raise ValueError('Invalid work publication date')
        publication_key(date)
        targets = []
        for target in packed:
            if not isinstance(target, list) or len(target) not in (2, 3):
                raise ValueError('Invalid work target')
            tid, flags = target[:2]
            tid = identity if tid == 0 else tid
            if not isinstance(tid, str) or type(flags) is not int or flags not in (0, 1, 2, 4, 5, 6):
                raise ValueError('Invalid work target identity/media')
            href = target[2] if len(target) == 3 else target_url(tid)
            source_url(href)
            local = bool(flags & 4)
            if local != tid.startswith('local:'):
                raise ValueError('Work target local identity mismatch')
            targets.append({'id': tid, 'url': href, 'mediaType': MEDIA[flags & 3], 'local': local,
                            'platform': 'pmnote' if local else tid.split(':', 1)[0]})
        if not targets:
            raise ValueError('Work has no public targets')
        return {'id': identity, 'title': title, 'summary': summary,
                'types': [name for i, name in enumerate(MEDIA) if media & (1 << i)],
                'topics': [name for i, name in enumerate(self.topics) if topics & (1 << i)],
                'publishedAt': date, 'role': ROLES[role], 'searchExtra': extra, 'targets': targets,
                'readUrl': BASE + work_path(identity)}

    def resolve(self, identity):
        work_path(identity)
        seen = set()
        while identity in self.redirects:
            if identity in seen:
                raise ValueError('Cyclic work redirect')
            seen.add(identity)
            identity = self.redirects[identity]
            work_path(identity)
        if identity not in self.by_id:
            raise ValueError('No current public work found; do not restore it from an old index')
        return identity

    def listing(self, query='', media='all', topic='all'):
        if len(query) > 200 or media not in ('all', 'article', 'video', 'podcast'):
            raise ValueError('Use a short title/topic search and a supported media type')
        topic = 'ai' if topic == 'ai-for-game-pm' else topic
        if topic != 'all' and topic not in self.topics:
            raise ValueError('Unknown work topic')
        tokens = [search_key(t) for t in query.split() if search_key(t)]
        matches = []
        for w in self.works:
            text = self.search_text[w['id']]
            if (media == 'all' or media in w['types']) and (topic == 'all' or topic in w['topics']) and all(t in text for t in tokens):
                matches.append(w)
        return matches

    def detail(self, identity):
        identity = self.resolve(identity)
        payload = self.load(work_path(identity))
        work = payload.get('work', {})
        if payload.get('schemaVersion') != 1 or payload.get('workId') != identity or work.get('id') != identity:
            raise ValueError('Work detail identity mismatch')
        if not isinstance(payload.get('platformVariants'), list) or not isinstance(payload.get('localTargets'), list):
            raise ValueError('Missing platform/local work details')
        expected = {t['id']: t for t in self.by_id[identity]['targets']}
        variants = payload['platformVariants'] + payload['localTargets']
        if len(variants) != len(expected) or {v.get('variantId') for v in variants} != set(expected):
            raise ValueError('Incomplete work version details')
        for v in variants:
            t = expected[v['variantId']]
            if (v.get('workId') != identity or v.get('url') != t['url'] or v.get('mediaType') != t['mediaType']
                    or v.get('platform') != t['platform'] or not isinstance(v.get('title'), str)
                    or not isinstance(v.get('summary'), str) or not isinstance(v.get('publishedAt'), (str, type(None)))):
                raise ValueError('Work version identity or metadata mismatch')
        if work.get('title') != self.by_id[identity]['title'] or publication_key(work.get('date', '')) != publication_key(self.by_id[identity]['publishedAt']):
            raise ValueError('Work changed between index and detail; retry a new current snapshot')
        if not isinstance(work.get('aliases'), list) or not all(isinstance(t, str) for t in work['aliases']):
            raise ValueError('Missing original title aliases')
        if work.get('thought') is not None or identity.startswith('thought-'):
            thought_markdown(work)
        return payload  # Keep all original fields, audio, dates, provenance and summaries.


class ThoughtHtml(HTMLParser):
    """Convert the site's small static allowlist, preserving paragraph/link order."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.stack = [], []
        self.quote = 0
        self.links = 0
        self.lists = []

    def handle_starttag(self, tag, attrs):
        if tag not in ('h3', 'p', 'hr', 'blockquote', 'a', 'strong', 'em', 'ul', 'ol', 'li'):
            raise ValueError('Unsupported thought body HTML; no partial body returned')
        if tag == 'hr':
            self.parts.append('\n\n---\n\n')
            return
        if tag == 'li' and (not self.stack or self.stack[-1] not in ('ul', 'ol')):
            raise ValueError('List item outside a thought list')
        self.stack.append(tag)
        if tag == 'h3': self.parts.append('\n\n## ')
        elif tag == 'p': self.parts.append('\n\n' + ('> ' if self.quote else ''))
        elif tag == 'blockquote': self.quote += 1
        elif tag == 'strong': self.parts.append('**')
        elif tag == 'em': self.parts.append('*')
        elif tag in ('ul', 'ol'):
            start = dict(attrs).get('start', '1')
            if not re.fullmatch(r'[1-9][0-9]{0,5}', start):
                raise ValueError('Invalid thought list start')
            self.lists.append({'tag': tag, 'next': int(start)})
            self.parts.append('\n')
        elif tag == 'li':
            current = self.lists[-1]
            marker = str(current['next']) + '. ' if current['tag'] == 'ol' else '- '
            self.parts.append('\n' + '    ' * (len(self.lists) - 1) + marker)
            current['next'] += 1
        elif tag == 'a':
            # Historical author references may use HTTP. Preserve them as
            # Markdown destinations only; canonical sources and fetches stay HTTPS.
            href = source_url(dict(attrs).get('href'), allow_http=True)
            # URL punctuation must not escape the Markdown destination.
            href = href.replace('(', '%28').replace(')', '%29')
            self.parts.append('[')
            self.stack.append(href)
            self.links += 1

    def handle_endtag(self, tag):
        if tag == 'a':
            if len(self.stack) < 2 or self.stack[-2] != 'a': raise ValueError('Unbalanced thought link')
            href = self.stack.pop()
            self.parts.append('](' + href + ')')
        if not self.stack or self.stack.pop() != tag:
            raise ValueError('Unbalanced thought body HTML')
        if tag == 'blockquote': self.quote -= 1
        elif tag == 'strong': self.parts.append('**')
        elif tag == 'em': self.parts.append('*')
        elif tag in ('h3', 'p'): self.parts.append('\n\n')
        elif tag in ('ul', 'ol'):
            if not self.lists or self.lists.pop()['tag'] != tag:
                raise ValueError('Unbalanced thought list')
            self.parts.append('\n')
        elif tag == 'li': self.parts.append('\n')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag != 'hr': self.handle_endtag(tag)

    def handle_data(self, data):
        if not self.stack and not data.strip(): return
        # Preserve source text without allowing it to invent Markdown markup.
        self.parts.append(label(data).replace('*', '\\*').replace('`', '\\`'))

    def body(self):
        if self.stack: raise ValueError('Incomplete thought body HTML')
        text = re.sub(r'\n{3,}', '\n\n', ''.join(self.parts)).strip()
        if len(text) < 80: raise ValueError('Thought body missing; a title or excerpt is not a full issue')
        return text


def thought_markdown(work):
    thought = work.get('thought')
    if not isinstance(thought, dict) or type(thought.get('issue')) is not int or work.get('id') != 'thought-' + str(thought['issue']):
        raise ValueError('Thought identity mismatch')
    day = work.get('date', '')
    if day in (None, '') and work.get('dateBasis') == 'unknown':
        pass
    else:
        try:
            if datetime.date.fromisoformat(day).isoformat() != day: raise ValueError()
        except (ValueError, TypeError):
            raise ValueError('Thought writing date missing or invalid') from None
        if work.get('dateBasis') != 'archive-content-match':
            raise ValueError('Thought writing date lacks an archive basis')
    original = source_url(thought.get('sourceUrl'))
    if not urlsplit(original).fragment or not re.fullmatch(r'[a-f0-9]{64}', thought.get('bodyHash', '')):
        raise ValueError('Thought source anchor or body identity missing')
    html = thought.get('bodyHtml')
    if not isinstance(html, str): raise ValueError('Thought full body missing')
    parser = ThoughtHtml()
    parser.feed(html)
    parser.close()
    body = parser.body()
    return '\n'.join(['# ' + thought_title(work['id']), '', '作者：Hao',
                      '站内原位阅读：' + BASE + '/community/library/?thought=' + work['id'],
                      '公开正文：' + BASE + work_path(work['id']), '原始来源：' + original, '',
                      '范围：本站已审核的整期工作思考；引用来源按正文保留。', '', body])


def work_markdown(payload, media='all'):
    w = payload['work']
    if w.get('thought') is not None or w['id'].startswith('thought-'):
        return thought_markdown(w)
    lines = ['# ' + label(w['title']), '', '原文：' + primary_url(payload['platformVariants'] + payload['localTargets'], media)]
    day = publication_day(w.get('date'))
    if day:
        lines.append('发布于：' + day)
    lines += ['范围：作品与各平台版本的公开元数据；摘要不是全文或节目转写。', '', '## 原题与别名']
    lines += ['- ' + label(title) for title in w['aliases']]
    for v in payload['platformVariants'] + payload['localTargets']:
        lines += ['', '## ' + label(v['title']), '平台：' + PLATFORMS.get(v['platform'], v['platform']),
                  '形式：' + v['mediaType'], '原文：' + source_url(v['url'])]
        day = publication_day(v.get('publishedAt'))
        if day:
            lines.append('发布于：' + day)
        if v.get('updatedAt'):
            lines.append('修订：' + v['updatedAt'] + '（不替代发布日期）')
        if v.get('durationSeconds') is not None:
            lines.append('来源时长（秒）：' + str(v['durationSeconds']))
        if v.get('summary'):
            lines += ['', '来源摘要：', v['summary']]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='kind', required=True)
    interviews = sub.add_parser('interviews')
    interviews.add_argument('--search', default='')
    interviews.add_argument('--id')
    tools = sub.add_parser('tool')
    tools.add_argument('slug')
    works = sub.add_parser('works', help='Search current unified works or read every version of one work')
    works.add_argument('--search', default='')
    works.add_argument('--id')
    works.add_argument('--type', choices=('all', 'article', 'video', 'podcast'), default='all')
    works.add_argument('--topic', default='all')
    works.add_argument('--json', action='store_true', help='Keep complete original detail fields')
    works.add_argument('--site-dir', type=Path, help='Maintainer: explicit offline built-site directory; never falls back online')
    args = parser.parse_args()
    if args.kind == 'works':
        library = Works(args.site_dir)
        if args.id:
            payload = library.detail(args.id)
            print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else work_markdown(payload, args.type))
        else:
            items = library.listing(args.search, args.type, args.topic)
            if args.json:
                print(json.dumps({'revision': library.index['revision'], 'counts': library.index['counts'], 'items': items}, ensure_ascii=False, indent=2))
            else:
                for w in items:
                    print(work_listing_markdown(w, args.type))
                    print('  work ID: ' + w['id'] + ' · ' + '/'.join(w['types']))
    elif args.kind == 'tool':
        print(tool_text(args.slug))
    elif args.id:
        print(interview_markdown(Interviews().detail(args.id)))
    else:
        for item in Interviews().listing(args.search):
            print('- [' + label(item.get('title') or item['originalTitle']) + '](' + canonical(item['id']) + ') · 分享人 @' + label(item['sharer']))
            print('  正文读取：python3 <Skill目录>/scripts/read.py interviews --id ' + item['id'])


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError) as error:
        raise SystemExit(str(error))
