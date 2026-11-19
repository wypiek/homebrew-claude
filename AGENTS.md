# Notes for maintainers and AI agents

This repository is a T3 Code theme that recreates the look of The Homebrew
Channel (HBC) on the Wii. Read this before changing anything.

## How it fits together

```
src/*.css  +  themes/homebrew-channel-colors.json  +  assets/generated/*.webp
                              |
                  scripts/build-theme.py
                              |
                   themes/<theme-id>.json   (13 themes, committed)
                              |
     git tag vX.Y.Z  ->  .github/workflows/release.yml  ->  GitHub release
```

- `src/hbc-theme.css`: the HBC styling for T3 Code's layout. Shared by every theme.
- `src/hbc-bubbles-fast.css`: the rising bubbles. This is what the build uses.
- `src/hbc-bubbles.css`: the original, more accurate bubble animation. Kept for
  switching back, not built.
- `scripts/build-theme.py`: holds every palette and the `THEMES` list, and
  writes `themes/*.json`. Its docstring explains the build.
- `scripts/make-backgrounds.py`: recolors the water and tints the bubbles into
  `assets/generated/`. Only needed when the art or a color changes.
- `scripts/check-selectors.js`: paste into T3 Code's DevTools console after a
  T3 Code update to check the theme's selectors still match.
- `docs/DEVELOPMENT.md`: build, add a color, release steps and limits.
- `claude-app/`: the same look as a Claude Code plugin for the Claude desktop
  and mobile apps. `scripts/build-claude-mod.py` writes its
  `hooks/variants.ts` (never edit that by hand) from the palettes, `THEMES`,
  the bubble CSS and `make-backgrounds.py`'s settings. Rebuild it whenever
  those change. Its scene must stay pure vector SVG under 131,072 characters.

## Rules

- **Never edit `themes/*.json` by hand**, except `homebrew-channel-colors.json`,
  the base palette. Edit `src/` or `scripts/`, run
  `python scripts/build-theme.py`, and commit the rebuilt files with the change.
- **Stay close to the original HBC look.** Colors and gradients in the
  "Homebrew Channel art" section of `src/hbc-theme.css` were measured from the
  HBC image files. Do not restyle them to taste.
- **Dark only.** There is no light mode. Do not add light palettes or
  `:root:not(.dark)` rules.
- **Use T3 Code's stable selectors.** The list comes from T3 Code's theme guide.
  Other class names and attributes change between releases. If a rule truly
  needs a selector outside the list, say so in its comment and add it to
  `scripts/check-selectors.js`.
- **Keep power use low.** The bubbles animate behind the whole window, and T3
  Code restyles the four bubble layers on every frame. So:
  - no `backdrop-filter`,
  - animate only `transform`, `translate` or `opacity`,
  - keep bubble images as WebP at quality 90, the smallest size without banding.
- **Stay under 50,000 characters of CSS per theme.** The build stops if a theme
  goes over. The embedded images take most of that budget.
- **Theme CSS cannot load files.** `url()` only takes `data:` URLs. No
  `@import`, no `image-set()`.
- **License.** The bubbles are translated from HBC's `bubbles.c` and the art
  comes from [fail0verflow/hbc](https://github.com/fail0verflow/hbc). Both are
  GPL-2.0-or-later, so this project is too. Keep the credit comments at the top
  of the bubble CSS files. Do not add Nintendo assets.

## Things that are easy to get wrong

- **Focus rings.** T3 Code draws keyboard focus as a Tailwind ring, which is a
  `box-shadow`. Any rule here that sets `box-shadow` on a focusable element must
  start with
  `var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000)`,
  written out in full. A custom property holding those values resolves on the
  root, where they are empty.
- **The sidebar has two forms.** Docked, its glass is on
  `[data-slot="sidebar-inner"]`. In a narrow window it opens as an overlay with
  no `sidebar-inner`, which gets its own solid background. Test both.
- **Theme ids are file names.** Renaming a theme leaves users with a stale copy
  of the old id. Avoid renames, and explain any rename in the release notes.
- **`homebrew-channel-colors.json` is not a theme.** The release workflow leaves
  it out on purpose.
- **Bubble accuracy is a deliberate compromise.** `hbc-bubbles-fast.css` sways
  each layer of 10 bubbles as one, because the per-bubble sway in
  `hbc-bubbles.css` repainted the whole window every frame. Only switch back if
  T3 Code makes that cheaper, and measure first with a DevTools Performance
  trace.

## Checking a change

You cannot see T3 Code from a script. After building:

1. Run `t3 theme set ./themes/homebrew-channel.json`.
2. Check a normal window and a narrow one, with the sidebar open and closed.
3. Use the keyboard to tab through the sidebar and buttons, to check focus rings.
4. If colors changed, check a few color variations.

If you are an AI agent, ask the maintainer to check the result and send
screenshots.

## Git

- Commit messages are imperative ("Fix sidebar overlay in narrow windows").
- Do not add AI co-author or "Generated with" lines to commits or pull requests.
- Releases: push a `v*` tag on `main`. The workflow attaches every theme.
