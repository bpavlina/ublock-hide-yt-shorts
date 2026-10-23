# Hide YouTube Shorts with uBlock Origin

Filter lists for [uBlock Origin](https://github.com/gorhill/uBlock) that remove YouTube Shorts from youtube.com and m.youtube.com. Two optional lists hide Playables (mini games) and comments.

YouTube changes its pages often, and a change can stop a rule from working. The lists are tested against live YouTube every week. If something still shows, see [Something still shows](#something-still-shows).

## Subscribe

With uBlock Origin installed, click **Subscribe** next to a list and confirm in the page uBlock Origin opens.

If that doesn't work, open the uBlock Origin Dashboard, go to **Filter lists**, scroll to the bottom, tick **Import…**, paste the list's address and click **Apply changes**.

| List | Hides | Subscribe | Address |
| --- | --- | --- | --- |
| Shorts | Shorts shelves on the homepage, subscriptions, search, channel pages and under videos; single Shorts in feeds and search results; the Shorts tab on channels; the Shorts button in the sidebar and the mobile bottom bar; the Shorts filter chip; Shorts notifications | [Subscribe](https://subscribe.adblockplus.org/?location=https%3A%2F%2Fraw.githubusercontent.com%2Fbpavlina%2Fublock-hide-yt-shorts%2Fmaster%2Flist.txt&title=Hide%20YouTube%20Shorts) | `https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/list.txt` |
| Playables (optional) | Playables shelves, game cards and the sidebar entry | [Subscribe](https://subscribe.adblockplus.org/?location=https%3A%2F%2Fraw.githubusercontent.com%2Fbpavlina%2Fublock-hide-yt-shorts%2Fmaster%2Fplayables.txt&title=Hide%20YouTube%20Playables) | `https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/playables.txt` |
| Comments (optional) | Desktop only: the comment section under videos and the comment button on Shorts | [Subscribe](https://subscribe.adblockplus.org/?location=https%3A%2F%2Fraw.githubusercontent.com%2Fbpavlina%2Fublock-hide-yt-shorts%2Fmaster%2Fcomments.txt&title=Hide%20YouTube%20comments) | `https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/comments.txt` |

Shorts you have watched stay visible on your History page.

With automatic updates on, uBlock Origin updates these lists about every four days. To get a fix right away, click the clock icon next to the list on the Filter lists page, click **Update now**, then reload YouTube.

The Shorts list works in every language YouTube offers, including those that translate "Shorts", such as Japanese (ショート) and Afrikaans (Kortvideo's).

## Something still shows

- Open uBlock Origin on a YouTube page. If the big power button is grey, filtering is paused for the site; click it and reload.
- In the same popup, check that cosmetic filtering isn't turned off for YouTube: the eye icon (under "More" if the icons are hidden) must not be crossed out. If it is, click it, click the padlock to save, and reload.
- In the Dashboard, on the Filter lists page, check that the list is ticked and that "Parse and enforce cosmetic filters" is on.
- Update the list as described above, then reload YouTube.
- In Brave, a blank space where the Shorts tab used to be comes from Brave Shields' own "YouTube Shorts" list, which hides only the tab's text. This list removes the whole tab, so the gap usually means uBlock Origin isn't filtering the page. Check the points above.

If none of that helps, [open an issue](https://github.com/bpavlina/ublock-hide-yt-shorts/issues/new?template=shorts-not-being-filtered.md) with the page URL, a screenshot, your browser, and whether you're on desktop or mobile.

## Credits

Based on [gijsdev/ublock-hide-yt-shorts](https://github.com/gijsdev/ublock-hide-yt-shorts) and its continuation [i5heu/ublock-hide-yt-shorts](https://github.com/i5heu/ublock-hide-yt-shorts).

Not affiliated with, endorsed by or associated with Alphabet Inc., Google LLC or YouTube.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

See [LICENSE.md](LICENSE.md).
