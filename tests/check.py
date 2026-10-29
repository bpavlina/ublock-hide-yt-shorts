"""Load the lists into real uBlock Origin and check YouTube pages.

Every page is measured twice, without and with the lists, in two ways:

Offline, against saved copies of YouTube pages in tests/fixtures. The pages
never change between runs, so ordinary content (regular videos, other tabs,
other sidebar entries, chips, player and Shorts buttons) must be exactly the
same with and without the lists.

Live, against youtube.com and m.youtube.com, which change all the time. Here
ordinary content may vary between the two loads, so it only has to keep at
least half.

Both fail when anything a list should hide is still visible. Live also fails
when a page doesn't load, when uBO rejects or drops a filter line, or when
something the check looks for is missing on every page even without the lists
(YouTube changed its markup or blocked the runner).

Run:      UBO_PATH=path/to/uBlock0.chromium uv run --with playwright==1.49.0 python tests/check.py
Options:  --offline   only the saved pages (fast, no network)
          --snapshot  save the live pages (as loaded without the lists) as new fixtures
YT_COOKIES=cookies.json adds signed-in pages (subscriptions, History) for a throwaway
account; SCRUB=regex removes matching text (the account's name, email) from snapshots.
Local only; never give CI real cookies.
"""
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / 'tests' / 'fixtures'
LISTS = ['list.txt', 'playables.txt', 'comments.txt']
UBO = os.environ['UBO_PATH']
COOKIES = os.environ.get('YT_COOKIES')
Q = '?hl=en&gl=US'
MOBILE_UA = ('Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36')

MODES = {
    'desktop': dict(viewport={'width': 1400, 'height': 900}),
    'mobile': dict(viewport={'width': 412, 'height': 900}, user_agent=MOBILE_UA),
}
HOSTS = {'desktop': 'https://www.youtube.com', 'mobile': 'https://m.youtube.com'}
# Page -> ordinary content that must stay visible in both live runs. It proves the
# page really loaded (not an error or bot check) and the lists don't hide too much.
WATCH_LINKS = 'a[href^="/watch"]'
SHORTS_LINKS = 'a[href^="/shorts/"]'
PAGES = {
    'desktop': {
        '/' + Q: 'ytd-guide-entry-renderer',
        '/results' + Q + '&search_query=minecraft': 'ytd-video-renderer ' + WATCH_LINKS,
        '/@mkbhd/featured' + Q: WATCH_LINKS,
        '/@madseasonshow/shorts' + Q: 'yt-tab-shape[tab-title="Videos"]',
        '/playables' + Q: 'ytd-rich-grid-renderer',
        # A video whose related list includes single Shorts (they don't show up on every video).
        '/watch' + Q + '&v=w_Hh5REKwn8': '#movie_player',
        '/shorts/Y8IJi7iP5vk' + Q: 'reel-action-bar-view-model like-button-view-model',
    },
    'mobile': {
        '/' + Q: 'ytm-pivot-bar-item-renderer',
        '/results' + Q + '&search_query=minecraft': 'ytm-video-with-context-renderer ' + WATCH_LINKS,
        '/@mkbhd/featured' + Q: WATCH_LINKS,
        '/playables' + Q: 'ytm-rich-grid-renderer',
        '/watch' + Q + '&v=dQw4w9WgXcQ': 'ytm-slim-video-metadata-section-renderer',
    },
}
if COOKIES:
    for pages in PAGES.values():
        pages['/feed/subscriptions' + Q] = WATCH_LINKS
        # History keeps watched Shorts on purpose, so its Shorts are the content to keep.
        pages['/feed/history' + Q] = SHORTS_LINKS
# Pages where some metrics are expected to stay visible.
ALLOW = {'/feed/history': {'shorts_links', 'shorts_chip'}}

METRICS = """keep => {
  const vis = e => e.checkVisibility();
  const all = sel => [...document.querySelectorAll(sel)].filter(vis);
  const count = sel => all(sel).length;
  const label = e => e.textContent.trim();
  const shorts = sel => all(sel).filter(e => label(e) === 'Shorts').length;
  const plain = e => e.querySelector('a[href^="/watch"]') &&
    !e.querySelector('a[href^="/shorts/"], a[href^="/playables"]');
  return {
    // Must be zero with the lists loaded.
    shorts_links: count('a[href^="/shorts/"]'),
    shorts_tab: shorts('yt-tab-shape'),
    shorts_chip: shorts('yt-chip-cloud-chip-renderer, ytm-chip-cloud-chip-renderer'),
    shorts_guide: shorts('ytd-guide-entry-renderer, ytd-mini-guide-entry-renderer'),
    shorts_pivot: shorts('ytm-pivot-bar-item-renderer'),
    // A tab whose label is hidden but which still takes up space (and links to /shorts).
    empty_tabs: all('yt-tab-shape[tab-title]').filter(e => !e.innerText.trim()).length,
    playables_links: count('a[href^="/playables"]'),  // game cards and the sidebar entry
    comments: count('#comments'),
    comment_buttons: count('reel-action-bar-view-model button[aria-label*="comment" i]'),
    // Ordinary content, by kind. Must not change on the saved pages.
    ordinary: {
      videos: all('ytd-video-renderer, ytd-rich-item-renderer, ytd-compact-video-renderer, ' +
        'yt-lockup-view-model, ytm-video-with-context-renderer, ytm-rich-item-renderer, ' +
        'ytm-compact-video-renderer').filter(plain).length,
      tabs: all('yt-tab-shape').filter(e => e.getAttribute('tab-title') !== 'Shorts').length,
      nav: all('ytd-guide-entry-renderer, ytd-mini-guide-entry-renderer, ytm-pivot-bar-item-renderer')
        .filter(e => !/^(Shorts|Playables)$/.test(label(e))).length,
      chips: all('yt-chip-cloud-chip-renderer, ytm-chip-cloud-chip-renderer, chip-view-model')
        .filter(e => !/^(Shorts|(YouTube )?Playables)$/.test(label(e))).length,
      // The main player, not the hover preview inside a Short.
      player: all('#movie_player').filter(e => !e.closest('ytm-shorts-lockup-view-model')).length,
      shorts_buttons: all('reel-action-bar-view-model > *')
        .filter(e => !e.querySelector('[aria-label*="comment" i]')).length,
    },
    kept: count(keep),
    // Where leaked links sit, so a failure report says what to fix.
    where: all('a[href^="/shorts/"], a[href^="/playables"]').slice(0, 3)
      .map(e => { const c = []; for (; e && e !== document.body && c.length < 10; e = e.parentElement)
        c.push(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '')); return c.join(' < '); }),
  };
}"""
# Metrics the live pages must show without the lists, so each rule is really
# exercised. empty_tabs is zero without the lists too; comments.txt is desktop only.
SEEN = {
    'desktop': {'shorts_links', 'shorts_tab', 'shorts_chip', 'shorts_guide',
                'playables_links', 'comments', 'comment_buttons'},
    'mobile': {'shorts_links', 'shorts_tab', 'shorts_pivot', 'playables_links'},
}


def page_name(path):
    return path.split('?')[0]


def fixture_file(mode, path):
    slug = re.sub(r'[^a-z0-9]+', '-', page_name(path).lower()).strip('-') or 'home'
    return FIXTURES / f'{mode}-{slug}.html'


def snapshot_html(html):
    """Shrink a rendered page to what the filters can see: drop scripts, links, SVG
    drawings, iframes and image addresses, and remove the test account's identity (SCRUB)."""
    html = re.sub(r'<script\b.*?</script>|<link\b[^>]*>|<iframe\b.*?</iframe>', '', html, flags=re.S | re.I)
    html = re.sub(r'(<svg\b[^>]*>).*?</svg>', r'\1</svg>', html, flags=re.S | re.I)
    # Image addresses aren't needed, and one of them is the test account's avatar.
    html = re.sub(r'(<img\b[^>]*?)\s(?:src|srcset)="[^"]*"', r'\1', html, flags=re.I)
    html = re.sub(r'(<img\b[^>]*?)\s(?:src|srcset)="[^"]*"', r'\1', html, flags=re.I)
    html = re.sub(r'https?://[^"\'()\s&]*(?:ggpht\.com|googleusercontent\.com|ytimg\.com)[^"\'()\s&]*', '', html)
    if os.environ.get('SCRUB'):
        html = re.sub(os.environ['SCRUB'], 'x', html, flags=re.I)
    return html


def run(mode, filters, offline=False, snapshot=False):
    """Load every page of `mode` once with `filters` as My filters.
    Returns ({page: metrics}, uBO's counts for My filters)."""
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            tempfile.mkdtemp(), headless=True, channel='chromium', locale='en-US',
            ignore_default_args=['--disable-extensions'],
            args=['--disable-features=ExtensionManifestV2Disabled,ExtensionManifestV2Unsupported',
                  f'--disable-extensions-except={UBO}', f'--load-extension={UBO}'],
            **MODES[mode])
        # Skip the EU consent interstitial.
        ctx.add_cookies([{'name': 'SOCS', 'value': 'CAI', 'domain': '.youtube.com', 'path': '/'}])
        if COOKIES and not offline:
            ctx.add_cookies(json.loads(Path(COOKIES).read_text()))
        bg = ctx.background_pages[0] if ctx.background_pages else ctx.wait_for_event('backgroundpage')
        dash_url = f"chrome-extension://{bg.url.split('/')[2]}/1p-filters.html"
        dash = ctx.new_page()
        dash.goto(dash_url)
        time.sleep(1.5)
        # Both runs use the same setup: uBO's default lists plus "My filters" (which
        # starts disabled in a fresh profile), so they differ only by our lists.
        send = "m => vAPI.messaging.send('dashboard', m)"
        dash.evaluate(send, {'what': 'writeUserFilters', 'content': filters})
        dash.evaluate(send, {'what': 'applyFilterListSelection', 'toSelect': ['user-filters'],
                             'merge': True, 'toImport': '', 'toRemove': []})
        dash.evaluate(send, {'what': 'reloadAllFilters'})
        time.sleep(4)
        # The reload can close the dashboard tab, so read the counts from a new one.
        dash = ctx.new_page()
        dash.goto(dash_url)
        time.sleep(1.5)
        counts = dash.evaluate(send, {'what': 'getLists'})['available']['user-filters']

        host, page, out = HOSTS[mode], ctx.new_page(), {}
        if offline:
            saved = {}
            for f in sorted(FIXTURES.glob(f'{mode}-*.html')):
                html = f.read_text()
                saved[re.match(r'<!-- url: (\S+) -->', html)[1]] = html
            # Serve the saved pages at their real addresses (so uBO applies its
            # hostname and path rules) and block everything else.
            page.route('**/*', lambda route: route.fulfill(
                body=saved[route.request.url], content_type='text/html; charset=utf-8')
                if route.request.url in saved else route.abort())
            for url in saved:
                page.goto(url, wait_until='load')
                page.wait_for_timeout(1500)  # let uBO's procedural filters run
                path = url[len(host):]
                out[page_name(path)] = page.evaluate(METRICS, PAGES[mode].get(path, 'body'))
            ctx.close()
            return out, counts

        for path, keep in PAGES[mode].items():
            # Google sometimes rate-limits CI runners (429 and a /sorry/ page); wait it out.
            for wait in (30, 90, None):
                resp = page.goto(host + path, wait_until='load')
                if not (resp and resp.status == 429) or wait is None:
                    break
                print(f'{mode} {path}: rate-limited, retrying in {wait}s', flush=True)
                time.sleep(wait)
            if not resp or resp.status >= 400 or not page.url.startswith(host):
                raise SystemExit(f'{mode} {path}: got {resp and resp.status} at {page.url}')
            page.wait_for_timeout(5000)
            for _ in range(3):  # trigger lazy-loaded shelves and comments
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(1500)
            page.evaluate('window.scrollTo(0, 0)')
            page.wait_for_timeout(800)
            out[page_name(path)] = page.evaluate(METRICS, keep)
            if snapshot:
                FIXTURES.mkdir(exist_ok=True)
                fixture_file(mode, path).write_text(
                    f'<!-- url: {host + path} -->\n' + snapshot_html(page.content()))
        ctx.close()
        return out, counts


def compare(mode, base, hidden, exact):
    """Problems found by comparing one mode's runs without (base) and with (hidden) the lists."""
    problems = []
    for page in base:
        before, after = base[page], hidden[page]
        allowed = ALLOW.get(page, set())
        if exact:
            for kind, n in before['ordinary'].items():
                if after['ordinary'][kind] != n:
                    problems.append(f'{mode} {page} (saved): ordinary {kind} went from {n} to '
                                    f'{after["ordinary"][kind]} with the lists; a rule hides too much')
        elif not before['kept']:
            problems.append(f'{mode} {page}: normal content missing without the lists '
                            '(page failed to load or changed)')
        elif after['kept'] * 2 < before['kept']:
            problems.append(f'{mode} {page}: normal content dropped from {before["kept"]} to '
                            f'{after["kept"]} with the lists (page failed to load, or a list hides too much)')
        for metric, n in after.items():
            if metric in ('ordinary', 'kept', 'where'):
                continue
            if metric in allowed:
                if exact and n != before[metric]:
                    problems.append(f'{mode} {page} (saved): {metric} went from {before[metric]} to {n}, '
                                    'but this page should keep them')
            elif n:
                problems.append(f'{mode} {page}{" (saved)" if exact else ""}: {metric} = {n} with the lists loaded')
                problems += [f'    at {w}' for w in after['where']]
    return problems


def main():
    offline_only, snapshot = '--offline' in sys.argv, '--snapshot' in sys.argv
    problems = []
    for name in LISTS:
        if not any(line.strip() and not line.startswith('!') for line in (ROOT / name).read_text().splitlines()):
            problems.append(f'{name} has no rules')
    filters = '\n'.join((ROOT / name).read_text() for name in LISTS)
    # uBO counts one entry per hostname and drops lines it rejects or that repeat.
    rules = sum(len(line.split('##')[0].split(',')) for line in filters.splitlines()
                if line.strip() and not line.startswith('!'))

    for mode in MODES:
        base, _ = run(mode, '', offline=True)
        hidden, counts = run(mode, filters, offline=True)
        print(mode, 'saved pages', json.dumps({'without': base, 'with': hidden}, indent=1))
        if not base:
            problems.append(f'{mode}: no saved pages in {FIXTURES}')
        if counts.get('entryUsedCount') != rules:
            problems.append(f'{mode}: uBO kept {counts.get("entryUsedCount")} of {rules} filters '
                            '(a line was rejected or is a duplicate)')
        problems += compare(mode, base, hidden, exact=True)
        if offline_only:
            continue

        base, _ = run(mode, '', snapshot=snapshot)
        hidden, _ = run(mode, filters)
        print(mode, 'live', json.dumps({'without': base, 'with': hidden}, indent=1))
        problems += compare(mode, base, hidden, exact=False)
        for metric in SEEN[mode]:
            if not any(m[metric] for m in base.values()):
                problems.append(f'{mode}: {metric} is 0 on every page even without the lists; '
                                'the check is blind to it (markup changed or runner blocked)')
    print('\n'.join(problems) or 'OK')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
