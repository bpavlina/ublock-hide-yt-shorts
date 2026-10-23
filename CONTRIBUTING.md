# Contributing

I only want to state a couple of rules when submitting a pull request:

## Keep each list to its subject
Shorts rules go in `list.txt`, Playables rules in `playables.txt`, comment rules in `comments.txt`. Nothing else.

## Never change the metadata on top of the list
*Metadata = Title, Version, Last modified etc. on the top of the list.*

This will only be done by one of the maintainers. You may or may not be the only pull request accepted between a version bump for example.

## Always include the full subdomain
Don't start your filter with `youtube.com` but with either `www.youtube.com` or `m.youtube.com`.
This is to prevent hiding elements on other subdomains like `studio.youtube.com`.

## Don't make your selector more complicated than it needs to be
Don't keep unnecessary `.style-scope` classes in your filter, for example.

## Select elements specific to the list's subject
Use elements or attributes that only appear for Shorts, Playables or comments, depending on the list (for example `ytm-shorts-lockup-view-model` or `[overlay-style="SHORTS"]`). Check that ordinary videos and unrelated buttons stay visible.

## Avoid :has-text() and :upward()
Use element names, attributes and native `:has()` where you can. They run as plain CSS. Prefer ones that don't change with the UI language. Use `:has-text()` only when nothing else identifies the element.

## Hide the whole element
Hide the outer element, not just its label, or an empty slot is left behind.

## Point to the specific elements
It's not always immediately clear what elements you're talking about. Try to include a screenshot of the elements or a link to a specific page where you will find the elements.
## Run the check before opening a pull request
With the Chromium build of uBlock Origin unzipped somewhere, run `UBO_PATH=path/to/uBlock0.chromium uv run --with playwright==1.49.0 python tests/check.py`. Add `--offline` to test only against the saved pages in `tests/fixtures`, which takes about a minute.
