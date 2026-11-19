# Homebrew Channel theme for the Claude app and T3 Code

An animated theme inspired by the channel menu of The Homebrew Channel on the Nintendo Wii:
deep-blue water, bubbles rising behind the chat, and Wii-blue accents. It comes in 13 colors.

This is a fork of [FrankieFms/homebrew-t3code](https://github.com/FrankieFms/homebrew-t3code),
the T3 Code theme, with a version added for Claude Code sessions in the Claude desktop and
mobile apps.

![Homebrew Channel theme preview](assets/previews/homebrew-default.png)

[Watch the bubbles move](https://github.com/user-attachments/assets/86e67ddb-d4e9-418d-bb89-1a16cfbeafbb)
(T3 Code version).

## Install in the Claude app

In a Claude Code terminal session, type:

```
/plugin install homebrew-channel --marketplace wypiek/homebrew-claude
```

Answer `y` to add the marketplace, then pick the user scope. The theme then shows in every
Claude Code session in the Claude desktop and mobile apps, including the desktop app's Code tab.

**Change the color:** type `/homebrew-color` to list the colors, then `/homebrew-color pink`
(or any other) to switch. The choice is saved for later sessions.

**Update:**

```bash
claude plugin update homebrew-channel@homebrew-claude
```

**Uninstall:**

```bash
claude plugin uninstall homebrew-channel@homebrew-claude
```

The Claude app takes a theme as colors plus an animated background, so the water and bubbles
are redrawn as vector art and the panels are see-through. The app has no custom CSS, so the
glossy HBC bars on buttons and the selected thread are T3 Code only. Dark only; with reduced
motion turned on in your system, the bubbles stay still. More in
[claude-app/README.md](claude-app/README.md).

## Install in T3 Code

[![Latest release](https://img.shields.io/github/v/release/FrankieFms/homebrew-t3code?label=release)](https://github.com/FrankieFms/homebrew-t3code/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/FrankieFms/homebrew-t3code/total?label=downloads)](https://github.com/FrankieFms/homebrew-t3code/releases)

1. Download a theme from the list below.
2. In T3 Code, open **Settings** and go to **Appearance**.
3. Import a theme and pick the file you downloaded.

All themes are dark only, so set T3 Code to dark mode. In T3 Code, the sidebar and chat box
sit on dark HBC-style bars, and the selected thread uses the steel-blue focus bar from the
original menu.

## Themes

Each color has its own recolored water, tinted bubbles and matching accent. The previews
are from T3 Code; the download links are T3 Code theme files. In the Claude app, pick a
color with `/homebrew-color`.

| | | |
|:-:|:-:|:-:|
| <img src="assets/previews/homebrew-default.png" alt="Homebrew Channel theme preview"><br>**Homebrew Channel**<br><sub>The original</sub><br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel.json) | <img src="assets/previews/homebrew-no-bg.png" alt="No Background theme preview"><br>**No Background**<br><sub>Navy gradient, no image</sub><br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-no-background.json) | <img src="assets/previews/homebrew-pink.png" alt="Pink theme preview"><br>**Pink**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-pink.json) |
| <img src="assets/previews/homebrew-red.png" alt="Red theme preview"><br>**Red**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-red.json) | <img src="assets/previews/homebrew-orange.png" alt="Orange theme preview"><br>**Orange**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-orange.json) | <img src="assets/previews/homebrew-gold.png" alt="Gold theme preview"><br>**Gold**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-gold.json) |
| <img src="assets/previews/homebrew-yellow.png" alt="Yellow theme preview"><br>**Yellow**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-yellow.json) | <img src="assets/previews/homebrew-green.png" alt="Green theme preview"><br>**Green**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-green.json) | <img src="assets/previews/homebrew-teal.png" alt="Teal theme preview"><br>**Teal**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-teal.json) |
| <img src="assets/previews/homebrew-indigo.png" alt="Indigo theme preview"><br>**Indigo**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-indigo.json) | <img src="assets/previews/homebrew-purple.png" alt="Purple theme preview"><br>**Purple**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-purple.json) | <img src="assets/previews/homebrew-magenta.png" alt="Magenta theme preview"><br>**Magenta**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-magenta.json) |
| <img src="assets/previews/homebrew-grey.png" alt="Grey theme preview"><br>**Grey**<br>[Download](https://github.com/FrankieFms/homebrew-t3code/releases/latest/download/homebrew-channel-grey.json) |  |  |

<details>
<summary>Install from a terminal</summary>

Set `theme` to the name of the file you want, without `.json`, such as `homebrew-channel-pink`.

macOS:

```sh
theme=homebrew-channel
base=https://github.com/FrankieFms/homebrew-t3code/releases/latest/download
curl -fsSLO "$base/$theme.json"
t3 theme set "./$theme.json"
```

Windows (PowerShell):

```powershell
$theme = "homebrew-channel"
$base = "https://github.com/FrankieFms/homebrew-t3code/releases/latest/download"
Invoke-WebRequest "$base/$theme.json" -OutFile "$theme.json"
t3 theme set ".\$theme.json"
```

Can't find `t3`? Use `~/.t3/bin/t3` on macOS or `%USERPROFILE%\.t3\bin\t3.cmd` on Windows.

</details>

## Updating in T3 Code

T3 Code does not update themes by itself. To get a newer version, download the
theme again and import it. See the [releases](https://github.com/FrankieFms/homebrew-t3code/releases)
for what changed.

## Uninstalling from T3 Code

Pick another theme in **Settings** > **Appearance**, or run `t3 theme clear`.

## Development

Building the themes and the Claude app plugin, adding a color, performance notes and
releases are in
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

Bug reports, fixes and color ideas are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits and license

The Homebrew Channel is by Team Twiizers, now [fail0verflow](https://github.com/fail0verflow).
This theme is a fan tribute and is not affiliated with fail0verflow, Nintendo, T3 Code or
Anthropic. The T3 Code theme is by [FrankieFms](https://github.com/FrankieFms).

The bubble animation is a CSS translation of `bubbles.c`, and the background and bubble
images come from The Homebrew Channel's source code at
[fail0verflow/hbc](https://github.com/fail0verflow/hbc). Both are released under the GNU
General Public License, version 2 or later. They have been changed for this theme: the
images are recolored and converted to WebP, and the animation is adapted to run as CSS.
For the Claude app, the water and bubbles are redrawn as SVG and the animation runs in it.

Because it builds on that code, this theme is also released under the
[GNU General Public License, version 2 or later](LICENSE).

### For fail0verflow

If you are part of fail0verflow, or otherwise hold rights in The Homebrew Channel, and have
any concerns about this theme, open an issue or email
[contact@frankiefms.com](mailto:contact@frankiefms.com). That includes a missing or wrong credit, a change you would like made, or a
request to take the theme down. Any request will be honored.
