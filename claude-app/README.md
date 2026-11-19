# Homebrew Channel for the Claude app

The Homebrew Channel look for Claude Code sessions in the Claude desktop and
mobile apps: the deep-blue underwater background, bubbles rising and swaying as
they do on the Wii, and Wii-blue accents. It comes in the same 13 colors as the
T3 Code theme.

This is a Claude Code plugin. The app cannot load pictures into a theme, so the
water and bubbles are redrawn as vector art by `scripts/build-claude-mod.py`.

## Install

In a Claude Code terminal session, type:

```
/plugin install homebrew-channel --marketplace wypiek/homebrew-claude
```

Answer `y` to add the marketplace, then pick the user scope. The look then shows
in every Claude Code session in the desktop and mobile apps.

From a local copy of this repository instead:

```bash
claude plugin marketplace add /path/to/homebrew-claude
```

```bash
claude plugin install homebrew-channel@homebrew-claude
```

## Change the color

Type `/homebrew-color` to list the colors, and `/homebrew-color pink` (or any
other) to switch. The choice is saved as the plugin's `color` setting.

Colors: default, no-background, pink, red, yellow, green, purple, orange, grey,
teal, gold, magenta, indigo.

The look is dark only. If you have asked your system to reduce motion, the
bubbles stay still.

## Credits and license

The bubbles are translated from `bubbles.c` of
[The Homebrew Channel](https://github.com/fail0verflow/hbc) by Team Twiizers
(fail0verflow), GPL-2.0-or-later, so this plugin is GPL-2.0-or-later too.
