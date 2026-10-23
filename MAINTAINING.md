# Maintaining the lists

YouTube changes its markup every few months, and a list that stops matching fails silently. This file covers how the lists are built, how they are tested, and what to do when the weekly check fails.

## The lists

| File | Hides |
| --- | --- |
| `list.txt` | Shorts: shelves, single Shorts in feeds and search, the channel tab, the sidebar entry, filter chips, notifications, mobile bottom-bar button |
| `playables.txt` | Playables: homepage shelves, game cards, the sidebar entry, mobile chip |
| `comments.txt` | The comment section under videos and the comment button on Shorts |

Each list has a header. `Expires: 4 days` tells uBlock Origin how often to re-download it, so a fix reaches subscribers within about four days. When you change a list, update `Version` and `Last modified`.

## Writing rules

Prefer, in this order:

1. **Element names and attributes**, e.g. `ytd-reel-shelf-renderer`, `yt-tab-shape[tab-title="Shorts"]`, `[overlay-style="SHORTS"]`. These are plain CSS. uBO hands them to the browser, they apply before the page draws, and they work in every UI language.
2. **Native `:has()`** to hide a container from something inside it, e.g. `ytd-rich-item-renderer:has(ytm-shorts-lockup-view-model)`. Use it instead of uBO's `:upward()`, which runs in JavaScript.
3. **`:has-text()`** only when nothing else identifies the element (currently the filter chips). It runs in JavaScript on every page change and only matches English text.

Always hide the outer element, not just its label. A rule that hides only a tab's text leaves an empty slot that still takes space and still links to Shorts. Brave Shields' own "YouTube Shorts" list does exactly this with the channel tab, so with uBO paused, Brave users see a blank gap between "Videos" and the next tab.

Exclude the history page (`:matches-path(/^(?!\/feed\/history)/)`) from rules that hide shelves, so Shorts you watched still show in your history.

## The check

`tests/check.py` loads all three lists into real uBlock Origin in a headless Chromium and visits live YouTube pages on desktop and mobile: search results, a channel's Home tab, a channel opened on its Shorts tab, the Playables page and a watch page. It measures each page twice, once without the lists and once with them, and fails when:

- uBO rejects a filter line,
- a Shorts or Playables link, or a "Shorts" tab, chip or sidebar entry, is still visible with the lists loaded,
- a channel tab is visible with an empty label,
- a page doesn't load (HTTP error, wrong site) or loses its normal content, such as video results or the player, in either run,
- something the check looks for is missing on every page even without the lists. That means YouTube changed its markup or blocked the runner, and the check can no longer see it.

When a leak is found, the output includes the element path of up to three leaked links, which is usually enough to write the fix.

### Running it locally

Download the Chromium build of uBlock Origin from its [releases](https://github.com/gorhill/uBlock/releases) (the workflow pins the version in `UBO_VERSION`), unzip it, then:

```
UBO_PATH=path/to/uBlock0.chromium uv run --with playwright==1.49.0 python tests/check.py
```

Install the browser once with `uvx --from playwright==1.49.0 playwright install chromium`. Playwright 1.49 is pinned because its Chromium still runs uBO's Manifest V2 build.

A full run takes about four minutes.

### Signed-in pages

Some pages only exist when signed in, such as the subscriptions feed. To check them, use a throwaway Google account, never your own, and export its cookies as Playwright JSON (a list of cookie objects for `.youtube.com` and `.google.com`). Then:

```
YT_COOKIES=path/to/cookies.json UBO_PATH=... uv run --with playwright==1.49.0 python tests/check.py
```

This adds `/feed/subscriptions` on desktop and mobile. Keep it local. Don't put account cookies in GitHub secrets.

Google blocks sign-in from browsers that Playwright launches. Sign in with a normally launched Chromium-based browser started with `--remote-debugging-port`, then read the cookies over that port with `playwright.chromium.connect_over_cdp`.

## The weekly workflow

`.github/workflows/check.yml` runs the check every Monday, on every push that changes a list, the test or the workflow, and on demand from the Actions tab. Each run installs Chromium and the pinned uBO release, then runs the check while signed out.

When a scheduled run fails, the workflow opens one issue labelled `check-failed` with a link to the run. Later failures don't open more issues while that one is open. Close the issue once the fix is pushed and the next run passes.

GitHub turns scheduled workflows off in a public repository after 60 days without commits, and sends an email first. Re-enable the workflow from the Actions tab, or push any commit.

## When the check fails

1. Open the failed run and read the last lines of the "Check" step.
2. **Leak** (`shorts_links = 3 with the lists loaded` plus `at ...` paths): find the outer element in the path, write a rule for it following the order above, then run the check locally.
3. **Blind** (`... is 0 on every page even without the lists`): YouTube changed or removed the element the check counts, or served the runner a different page. Open the page in a browser and compare it with the selectors in `METRICS` in `tests/check.py`.
4. **Normal content missing**: a page didn't load properly, or a list now hides too much. Run locally to tell which.
5. **Filter rejected** (`uBO accepted 26 of 27 filters`): a syntax error in a list.

YouTube serves different layouts to different accounts and regions, so a pass doesn't prove every layout is covered. User reports with a screenshot and URL (the issue template asks for both) cover what the check can't see.
