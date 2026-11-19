# Development

## Project layout

```
themes/                  Ready-to-use theme files. Built by scripts/build-theme.py,
                         except homebrew-channel-colors.json: the base palette the
                         build reads, edited by hand. It is not a theme to install.
src/
  hbc-bubbles-fast.css   The rising background bubbles, GPU-friendly. Used by default.
  hbc-bubbles.css        The original bubble animation, kept for switching back.
  hbc-theme.css          The Homebrew Channel styling for T3 Code's layout.
scripts/
  build-theme.py         Holds the palettes and the list of themes. Merges them with
                         the CSS, backgrounds and bubbles into themes/.
  make-backgrounds.py    Makes the recolored WebP backgrounds and tinted bubbles.
                         Needs Pillow.
assets/
  source/                The original Homebrew Channel background and bubble art.
  generated/             The WebP backgrounds and tinted bubbles the themes embed.
  previews/              Screenshots of each theme for the README.
```

The dark palette of the main theme comes from `themes/homebrew-channel-colors.json`.
Every color variation is tinted from it.

## Build

After editing a CSS file or a palette, rebuild the themes and apply one:

```sh
python scripts/build-theme.py
t3 theme set ./themes/homebrew-channel.json
```

`t3 theme set` publishes the file under its file name as the theme id and makes it
the active theme. `t3 theme show` prints the active theme. Published copies live in
`~/.t3/userdata/themes/` on macOS and `%USERPROFILE%\.t3\userdata\themes\` on Windows.
After the first publish, switch by id: `t3 theme set homebrew-channel-pink`.

The build script minifies the CSS inside each theme file. The files in `src/` keep their comments.

## Claude app

`claude-app/` is the same look as a Claude Code plugin for the Claude desktop and
mobile apps. The app cannot embed pictures in a theme, so
`scripts/build-claude-mod.py` redraws the water and bubbles as an animated SVG. It
reads the palettes and `THEMES` from `build-theme.py`, the recoloring settings from
`make-backgrounds.py` and the bubble layout from `src/hbc-bubbles-fast.css`, and
writes `claude-app/hooks/variants.ts`. Run it after changing any of those (Python
3.10 or later; Node, if installed, checks every palette):

```sh
python scripts/build-claude-mod.py
claude plugin validate claude-app
claude plugin test claude-app
```

To try a change, install from your local copy once (`claude plugin marketplace add
.` then `claude plugin install homebrew-channel@homebrew-claude`) and run
`/reload-plugins` after each build. Check a normal and a narrow window, and the
mobile app if you can.

## Install every theme

macOS:

```sh
for f in themes/*.json; do
  case "$f" in *-colors.json) continue ;; esac
  t3 theme set "$f"
done
t3 theme set homebrew-channel
```

Windows PowerShell:

```powershell
Get-ChildItem themes\*.json -Exclude *-colors.json | ForEach-Object { t3 theme set $_.FullName }
t3 theme set homebrew-channel
```

## Add a color variation

1. Add a background entry to `VARIATIONS` and a bubble entry to `BUBBLE_TINTS`
   in `scripts/make-backgrounds.py`.
2. Add a palette and a `variation(...)` entry to `THEMES` in `scripts/build-theme.py`,
   and a description and preview image to `DESCRIPTIONS` in the same file.
3. Run both scripts:

   ```sh
   pip install pillow
   python scripts/make-backgrounds.py
   python scripts/build-theme.py
   ```

## Performance

The bubbles move with GPU-composited `translate` animations, and the theme uses no
`backdrop-filter` blur. On a typical desktop, T3 Code's power use stays low to moderate
while idle. Scrolling and moving the mouse raise it for a moment, as in any app.

The original bubble animation is closer to the Homebrew Channel but repaints the whole
window every frame. To switch back to it, see the comment at the top of
`src/hbc-bubbles-fast.css` and `CSS_FILES` in `scripts/build-theme.py`.

## Release a new version

Rebuild the themes, commit them to `main`, then push a version tag:

```sh
git tag v1.2.3   # the next version number
git push origin v1.2.3
```

`.github/workflows/release.yml` then creates a release with every theme file attached.
The download links in the README always point to the latest release.

## Limits

- Color values must be hex (`#rgb` or `#rrggbb`).
- The `css` field holds at most 50,000 characters. The build script stops if a theme is longer.
- CSS `url()` accepts only `data:` URLs, so the backgrounds and bubbles are embedded.
- CSS cannot reach the terminal text, the file tree or diff internals. Those use the color roles.
