# uBlock filter list to hide all YouTube Shorts

A maintained [uBlock Origin](https://github.com/gorhill/uBlock) filter list to hide all traces of YouTube shorts videos.

Copy the link below, go to uBlock Origin > Dashboard > Filter lists, scroll to the bottom, and paste the link underneath the 'Import...' heading:  
`https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/list.txt`

[> uBlock Origin subscribe link <](ubo:subscribe?location=https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/list.txt) (does not work on GitHub)

## Bonus: hide YouTube Comments

`https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/comments.txt`

[> uBlock Origin subscribe link <](ubo:subscribe?location=https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/comments.txt) (does not work on GitHub)

## Bonus: hide YouTube Playables
`https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/playables.txt`

[> uBlock Origin subscribe link <](ubo:subscribe?location=https://raw.githubusercontent.com/bpavlina/ublock-hide-yt-shorts/master/playables.txt) (does not work on GitHub)

## Maintenance

Forked from [i5heu/ublock-hide-yt-shorts](https://github.com/i5heu/ublock-hide-yt-shorts), itself a continuation of [gijsdev/ublock-hide-yt-shorts](https://github.com/gijsdev/ublock-hide-yt-shorts). This fork merges the rules from both and prefers plain CSS selectors over `:has-text()`, so they work in any UI language and cost less to run.

## Checks

A GitHub Action (`.github/workflows/check.yml`) loads the lists into real uBlock Origin every Monday, and on every change to a list, then visits a few YouTube pages on desktop and mobile. It fails if anything the lists should hide is still visible, or if the pages no longer show the elements it looks for. Run it locally with:

```
UBO_PATH=path/to/uBlock0.chromium uv run --with playwright==1.49.0 python tests/check.py
```

## No affiliation to Alphabet, YouTube or Google

This project is an independent, open-source initiative and is not affiliated with, endorsed by, sponsored by, or associated with Alphabet Inc., Google LLC, or YouTube.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

See [LICENSE.md](LICENSE.md)
