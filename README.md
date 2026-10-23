# Hide YouTube Shorts with uBlock Origin

Filter lists for [uBlock Origin](https://github.com/gorhill/uBlock) that remove YouTube Shorts from youtube.com and m.youtube.com. Two optional lists hide Playables (mini games) and comments.

The lists are checked against live YouTube every week, so breakage after a YouTube update is caught and fixed quickly.

## Subscribe

In uBlock Origin, open the Dashboard, go to **Filter lists**, scroll to the bottom, tick **Import...**, paste a link below and click **Apply changes**.

| List | Hides | Link |
| --- | --- | --- |
| Shorts | Shorts shelves on the homepage, subscriptions, search, channel pages and under videos; single Shorts in feeds and search results; the Shorts tab on channels; the Shorts button in the sidebar and the mobile bottom bar; the Shorts filter chip; Shorts notifications | `https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/list.txt` |
| Playables (optional) | Playables shelves, game cards and the sidebar entry | `https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/playables.txt` |
| Comments (optional) | The comment section under videos and the comment button on Shorts | `https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/comments.txt` |

Shorts you have watched stay visible on your History page.

uBlock Origin downloads updates on its own every few days. To get a fix right away, click **Update now** on the Filter lists page.

## Something still shows

- **Check that uBlock Origin is on for YouTube.** Click its icon on a YouTube page. If the big power button is grey, filtering is paused for the site.
- **Update the lists.** Click **Update now** on the Filter lists page.
- **Brave: a blank space where the Shorts tab was.** Brave Shields has its own "YouTube Shorts" list, which hides only the tab's text and leaves an empty, clickable slot. This list removes the whole tab, so the gap means uBlock Origin isn't filtering the page. See the first point.

If none of that helps, [open an issue](https://github.com/bpavlina/ublock-hide-yt-shorts/issues/new?template=shorts-not-being-filtered.md) with the page URL, a screenshot, your browser, and whether you're on desktop or mobile.

## Credits

Based on [gijsdev/ublock-hide-yt-shorts](https://github.com/gijsdev/ublock-hide-yt-shorts) and its continuation [i5heu/ublock-hide-yt-shorts](https://github.com/i5heu/ublock-hide-yt-shorts).

Not affiliated with, endorsed by or associated with Alphabet Inc., Google LLC or YouTube.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

See [LICENSE.md](LICENSE.md).
