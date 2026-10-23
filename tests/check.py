"""Load the lists into real uBlock Origin and check live YouTube pages.

For every page, the same metrics are taken without and with the lists.
The check fails when:
  - uBO rejects a filter line,
  - anything a list should hide is still visible with the lists loaded,
  - a metric is zero on every page even without the lists (YouTube changed
    its markup or blocked the runner, so the check can no longer see it).

Run: UBO_PATH=path/to/uBlock0.chromium uv run --with playwright==1.49.0 python tests/check.py
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LISTS = ['list.txt', 'playables.txt', 'comments.txt']
UBO = os.environ['UBO_PATH']
Q = '?hl=en&gl=US'
MOBILE_UA = ('Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36')

MODES = {
    'desktop': dict(viewport={'width': 1400, 'height': 900}),
    'mobile': dict(viewport={'width': 412, 'height': 900}, user_agent=MOBILE_UA),
}
PAGES = {
    'desktop': ['/results' + Q + '&search_query=minecraft', '/@mkbhd/featured' + Q,
                '/@madseasonshow/shorts' + Q, '/playables' + Q, '/watch' + Q + '&v=jNQXAC9IVRw'],
    'mobile': ['/results' + Q + '&search_query=minecraft', '/@mkbhd/featured' + Q],
}
# Metrics a list must drive to zero. Each must be non-zero somewhere without the lists.
METRICS = """() => {
  const vis = e => e.checkVisibility();
  const count = sel => [...document.querySelectorAll(sel)].filter(vis).length;
  const labelled = re => [...document.querySelectorAll(
      'yt-tab-shape, yt-chip-cloud-chip-renderer, ytm-chip-cloud-chip-renderer, ' +
      'ytd-guide-entry-renderer, ytd-mini-guide-entry-renderer, ytm-pivot-bar-item-renderer')]
    .filter(e => vis(e) && re.test(e.textContent)).length;
  return {
    shorts_links: count('a[href^="/shorts/"]'),
    shorts_labels: labelled(/^\\s*Shorts\\s*$/),
    // A tab whose label is hidden but which still takes up space (and links to /shorts).
    empty_tabs: [...document.querySelectorAll('yt-tab-shape[tab-title]')]
      .filter(e => vis(e) && !e.innerText.trim()).length,
    playables_links: count('a[href^="/playables/"]'),
    comments: count('#comments'),
  };
}"""
# Metrics the pages above must show without the lists. empty_tabs is zero
# without the lists too, and mobile has no Playables or comments on these pages.
SEEN = {
    'desktop': {'shorts_links', 'shorts_labels', 'playables_links', 'comments'},
    'mobile': {'shorts_links', 'shorts_labels'},
}


def run(mode, filters):
    """Return {page: metrics} for one browser session, plus uBO's filter counts."""
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            tempfile.mkdtemp(), headless=True, channel='chromium', locale='en-US',
            ignore_default_args=['--disable-extensions'],
            args=['--disable-features=ExtensionManifestV2Disabled,ExtensionManifestV2Unsupported',
                  f'--disable-extensions-except={UBO}', f'--load-extension={UBO}'],
            **MODES[mode])
        # Skip the EU consent interstitial.
        ctx.add_cookies([{'name': 'SOCS', 'value': 'CAI', 'domain': '.youtube.com', 'path': '/'}])
        bg = ctx.background_pages[0] if ctx.background_pages else ctx.wait_for_event('backgroundpage')
        dash_url = f"chrome-extension://{bg.url.split('/')[2]}/1p-filters.html"
        dash = ctx.new_page()
        dash.goto(dash_url)
        time.sleep(1.5)
        counts = None
        if filters:
            send = "m => vAPI.messaging.send('dashboard', m)"
            dash.evaluate(send, {'what': 'writeUserFilters', 'content': filters})
            # "My filters" starts disabled in a fresh profile.
            dash.evaluate(send, {'what': 'applyFilterListSelection', 'toSelect': ['user-filters'],
                                 'toImport': '', 'toRemove': []})
            dash.evaluate(send, {'what': 'reloadAllFilters'})
            time.sleep(4)
            # The reload can close the dashboard tab, so read the counts from a new one.
            dash = ctx.new_page()
            dash.goto(dash_url)
            time.sleep(1.5)
            counts = dash.evaluate(send, {'what': 'getLists'})['available']['user-filters']
        host = 'https://m.youtube.com' if mode == 'mobile' else 'https://www.youtube.com'
        page, out = ctx.new_page(), {}
        for path in PAGES[mode]:
            page.goto(host + path, wait_until='load')
            page.wait_for_timeout(5000)
            for _ in range(3):  # trigger lazy-loaded shelves and comments
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(1500)
            page.evaluate('window.scrollTo(0, 0)')
            page.wait_for_timeout(800)
            out[path.split('?')[0]] = page.evaluate(METRICS)
        ctx.close()
        return out, counts


def main():
    filters = '\n'.join((ROOT / name).read_text() for name in LISTS)
    rules = sum(1 for line in filters.splitlines() if line.strip() and not line.startswith('!'))
    problems = []
    for mode in MODES:
        base, _ = run(mode, None)
        hidden, counts = run(mode, filters)
        print(mode, json.dumps({'without': base, 'with': hidden, 'filters': counts}, indent=1))
        if counts.get('entryUsedCount') != rules:
            problems.append(f'{mode}: uBO accepted {counts.get("entryUsedCount")} of {rules} filters')
        for page, metrics in hidden.items():
            for metric, n in metrics.items():
                if n:
                    problems.append(f'{mode} {page}: {metric} = {n} with the lists loaded')
        for metric in SEEN[mode]:
            if not any(m[metric] for m in base.values()):
                problems.append(f'{mode}: {metric} is 0 on every page even without the lists; '
                                'the check is blind to it (markup changed or runner blocked)')
    print('\n'.join(problems) or 'OK')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
