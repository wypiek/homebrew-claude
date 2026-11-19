"""Build the Homebrew Channel look for the Claude app (claude-app/).

What it does
    The Claude desktop and mobile apps take a theme from a Claude Code mod:
    a color palette, plus an animated SVG "scene" drawn behind the
    conversation. A scene cannot hold pictures, so the HBC water and bubbles
    are redrawn here as vector art:
      - the water is a gradient measured from assets/source/background_wide.png
        (WATER_STOPS), with faint light rays,
      - the bubbles are vector copies of the three HBC bubble images, at the
        same sizes, positions, rise speeds, delays and sway as
        src/hbc-bubbles-fast.css, which this script reads.
    Every color variation in build-theme.py's THEMES becomes a variant, with
    its water and bubbles recolored the way make-backgrounds.py recolors the
    WebP art, so the two stay in step.

Inputs
    scripts/build-theme.py        THEMES and the palettes
    scripts/make-backgrounds.py   VARIATIONS and BUBBLE_TINTS (read, not run)
    src/hbc-bubbles-fast.css      bubble layout and timing

Outputs
    claude-app/hooks/variants.ts            Never edit by hand.
    claude-app/.claude-plugin/plugin.json   Only the color picker's options.

Run it after changing a palette, THEMES, the bubble CSS or this file:

    python scripts/build-claude-mod.py

If Node is installed it also checks every variant's palette with
claude-app/hooks/make-colors.js and stops on one the app would not paint.
"""

import ast
import colorsys
import importlib.util
import json
import re
import shutil
import subprocess
from math import cos, radians, sin, tan
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "claude-app"
OUTPUT = MOD / "hooks" / "variants.ts"
MANIFEST = MOD / ".claude-plugin" / "plugin.json"
BUBBLE_CSS = ROOT / "src" / "hbc-bubbles-fast.css"
SCENE_MAX_LENGTH = 131_072

# The scene is drawn in a 16:9 box, the shape of the HBC background, and
# scaled to cover the window from the top, as the T3 Code theme fits the
# image to the window's width.
WIDTH, HEIGHT = 1600, 900

# Average color across rows of assets/source/background_wide.png, from top
# (0) to bottom (1). Below 0.87 the art is black.
WATER_STOPS = [
    (0.00, "#1775a4"), (0.10, "#166f9b"), (0.20, "#13628a"), (0.30, "#105375"),
    (0.40, "#0d425d"), (0.50, "#093044"), (0.60, "#06202c"), (0.70, "#031219"),
    (0.80, "#010608"), (0.87, "#000000"),
]
# The light rays and the glow under the surface, before recoloring.
RAY_COLOR = "#7cc7ee"
# The No Background theme's navy gradient (NAVY_BACKDROP in build-theme.py).
NAVY_STOPS = [(0.0, "#13263a"), (0.6, "#0d1824"), (1.0, "#08111a")]

# Colors of the HBC bubble art (assets/source/bubbles), before tinting:
# a dark-blue body, a lighter rim and a white cap where light hits the top.
BUBBLE_COLORS = {
    "bd": "#0f4766", "bm": "#1e6890", "bl": "#33a4e3",
    "hw": "#eff8fd", "hm": "#cce8f8", "hb": "#1a90d0",
}
# bubble2.png and bubble3.png are the same bubble as bubble1.png, fainter.
BUBBLE_STRENGTH = {"1": 1.0, "2": 0.5, "3": 0.25}

SOURCE_HUE = 199  # make-backgrounds.py's SOURCE_HUE: the hue of the water art.


def load_build_theme():
    spec = importlib.util.spec_from_file_location("build_theme", ROOT / "scripts" / "build-theme.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_assignments(path: Path, names: set) -> dict:
    """Read literal assignments from a script without running it, since
    make-backgrounds.py needs Pillow."""
    values = {}
    for node in ast.parse(path.read_text("utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in names:
                values[target.id] = ast.literal_eval(node.value)
    missing = names - values.keys()
    if missing:
        raise SystemExit(f"make-backgrounds.py: could not read {', '.join(sorted(missing))}.")
    return values


def recolor(color: str, hue: float, saturation: float, value: float) -> str:
    """make-backgrounds.py's recolor() for one color: shift the hue from the
    art's own, scale saturation and value."""
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + (hue - SOURCE_HUE) / 360) % 1
    r, g, b = colorsys.hsv_to_rgb(h, min(1.0, s * saturation), min(1.0, v * value))
    return "#" + "".join(f"{round(c * 255):02x}" for c in (r, g, b))


def mix(a: str, b: str, amount: float) -> str:
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(ca, cb))


# ---------- Bubble layout, read from the CSS ----------

def read_bubble_layers() -> list:
    css = BUBBLE_CSS.read_text("utf-8")
    layers = []
    for selector in ("html::before", "html::after", "body::before", "body::after"):
        # The layer's own rule: the shared rules above it list it too.
        blocks = [b for b in re.findall(r"^" + re.escape(selector) + r" \{(.*?)\n\}", css, re.S | re.M)
                  if "background-size" in b]
        if len(blocks) != 1:
            raise SystemExit(f"{BUBBLE_CSS.name}: expected one {selector} rule with bubbles.")
        body = blocks[0]
        images = re.findall(r"var\(--bubble-(\d)\)", body)
        sizes = [float(s) for s in re.findall(r"(\d+(?:\.\d+)?)px", re.search(r"background-size:([^;]+);", body).group(1))]
        positions = re.findall(r"([\d.]+)vw ([\d.]+)vh", body)
        rise = re.search(r"hbc-rise ([\d.]+)s linear (-?[\d.]+)s", body)
        sway = re.search(r"hbc-sway-(left|right) ([\d.]+)s ease-in-out (-?[\d.]+)s", body)
        if not (len(images) == len(sizes) == len(positions) and rise and sway):
            raise SystemExit(f"{BUBBLE_CSS.name}: could not read the bubbles of {selector}.")
        layers.append({
            "bubbles": [
                (image, size, float(x) / 100 * WIDTH, float(y) / 100 * HEIGHT)
                for image, size, (x, y) in zip(images, sizes, positions)
            ],
            "rise": (float(rise.group(1)), float(rise.group(2))),
            "sway": (sway.group(1), float(sway.group(2)), float(sway.group(3))),
        })
    return layers


# ---------- The scene ----------

def n(value: float) -> str:
    """A short number for the SVG."""
    return f"{value:.1f}".rstrip("0").rstrip(".")


def stops(pairs, opacity=None) -> str:
    return "".join(
        f'<stop offset="{n(offset * 100)}%" stop-color="{color}"'
        + (f' stop-opacity="{opacity}"' if opacity is not None else "") + "/>"
        for offset, color in pairs
    )


def light_rays() -> str:
    """Faint shafts of light fanning down from above the surface, as in the
    HBC art. Fixed, not random, so every build is the same."""
    origin_x, origin_y = WIDTH / 2, -1400
    shafts = []
    for i in range(21):
        spread = (i - 10) / 10                    # -1 .. 1 across the fan
        wobble = ((i * 37) % 11 - 5) / 5          # -1 .. 1, uneven spacing
        angle = spread * 0.36 + wobble * 0.02
        width = 8 + ((i * 53) % 7) * 5            # 8 .. 38 at the top
        top_y, bottom_y = 0, 760
        def x_at(y, side):
            return origin_x + tan(angle) * (y - origin_y) + side * width * (y - origin_y) / (0 - origin_y) / 2
        points = [
            (x_at(top_y, -1), top_y), (x_at(top_y, 1), top_y),
            (x_at(bottom_y, 1), bottom_y), (x_at(bottom_y, -1), bottom_y),
        ]
        strength = 0.35 + ((i * 29) % 5) * 0.12
        shafts.append(
            f'<path d="M{" L".join(f"{n(x)} {n(y)}" for x, y in points)}Z" fill-opacity="{n(strength)}"/>'
        )
    return f'<g fill="url(#ray)">{"".join(shafts)}</g>'


def crescent(start: float, end: float, inner: float) -> str:
    """A crescent inside the unit circle, along its edge from angle start to
    end (degrees, clockwise from 3 o'clock), thickest in the middle."""
    edge = 0.9
    a = (edge * cos(radians(start)), edge * sin(radians(start)))
    b = (edge * cos(radians(end)), edge * sin(radians(end)))
    p = lambda pt: f"{pt[0]:.3f} {pt[1]:.3f}"
    return f"M{p(a)}A{edge} {edge} 0 0 1 {p(b)}A{inner} {inner} 0 0 0 {p(a)}Z"


# The HBC bubble, drawn once around (0, 0) with radius 1 and placed with a
# transform: a thin rim, a second fainter rim a little off-centre, a shine
# along the top left and a glint along the bottom.
BUBBLE_SHAPES = (
    '<circle r="1" fill="url(#rim)"/>'
    '<circle cx="0.06" r="0.84" fill="none" stroke="{bl}" stroke-width="0.05" stroke-opacity="{inner}"/>'
    f'<path d="{crescent(-195, -55, 1.15)}" fill="url(#shine)"/>'
    f'<path d="{crescent(40, 140, 1.4)}" fill="url(#glint)"/>'
)


def bubble(image: str, size: float, x: float, y: float) -> str:
    """One bubble. (x, y) is its top-left corner, as the CSS
    background-position puts it."""
    radius = size * 0.44
    cx, cy = x + size / 2, y + size / 2
    strength = BUBBLE_STRENGTH[image]
    shapes = BUBBLE_SHAPES.replace("{inner}", n(0.2 * strength))
    return (
        f'<g transform="translate({n(cx)} {n(cy)}) scale({radius:.2f})" fill-opacity="{n(strength)}">'
        f"{shapes}</g>"
    )


def scene_template(layers: list) -> str:
    """The scene with {token} placeholders for every color that changes
    between variants. register.tsx fills them in."""
    groups = []
    styles = [
        "svg{background:#000}",
        f"@keyframes rise{{from{{transform:translateY({HEIGHT}px)}}to{{transform:translateY(-{HEIGHT}px)}}}}",
        "@keyframes swayleft{from{transform:translateX(-3px)}to{transform:translateX(3px)}}",
        "@keyframes swayright{from{transform:translateX(3px)}to{transform:translateX(-3px)}}",
    ]
    for index, layer in enumerate(layers):
        rise_time, rise_delay = layer["rise"]
        direction, sway_time, sway_delay = layer["sway"]
        styles.append(f".r{index}{{animation:rise {n(rise_time)}s linear {n(rise_delay)}s infinite}}")
        styles.append(
            f".s{index}{{animation:sway{direction} {n(sway_time)}s ease-in-out {n(sway_delay)}s infinite alternate}}"
        )
        drawn = "".join(bubble(*b) for b in layer["bubbles"])
        groups.append(f'<g class="r{index}"><g class="s{index}">{drawn}</g></g>')

    rim = [(0, "{bd}", 0), (0.6, "{bd}", 0.06), (0.8, "{bm}", 0.3), (0.9, "{bl}", 0.32),
           (0.96, "{hm}", 0.38), (1, "{bl}", 0.08)]
    shine = [(0, "{hw}", 0.1), (0.3, "{hw}", 0.9), (0.6, "{hm}", 0.55), (1, "{hb}", 0)]
    glint = [(0, "{hm}", 0), (0.5, "{hw}", 0.8), (1, "{hm}", 0)]

    def alpha_stops(pairs):
        return "".join(
            f'<stop offset="{n(o * 100)}%" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in pairs
        )

    defs = (
        "<defs>"
        '<linearGradient id="water" x1="0" y1="0" x2="0" y2="1">{water}</linearGradient>'
        f'<linearGradient id="ray" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="760">'
        '<stop offset="0" stop-color="{ray}" stop-opacity="0.16"/>'
        '<stop offset="0.45" stop-color="{ray}" stop-opacity="0.07"/>'
        '<stop offset="1" stop-color="{ray}" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="glow" cx="0.5" cy="0" r="0.6">'
        '<stop offset="0" stop-color="{ray}" stop-opacity="0.18"/>'
        '<stop offset="1" stop-color="{ray}" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="shade" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="160">'
        '<stop offset="0.25" stop-color="#051423" stop-opacity="0.62"/>'
        '<stop offset="1" stop-color="#051423" stop-opacity="0"/></linearGradient>'
        f'<radialGradient id="rim">{alpha_stops(rim)}</radialGradient>'
        f'<linearGradient id="shine" x1="0" y1="0.6" x2="1" y2="0.4">{alpha_stops(shine)}</linearGradient>'
        f'<linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">{alpha_stops(glint)}</linearGradient>'
        "</defs>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"'
        ' preserveAspectRatio="xMidYMin slice">'
        f"<style>{''.join(styles)}</style>"
        f"{defs}"
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#water)"/>'
        "{rays}"
        f'<rect width="{WIDTH}" height="160" fill="url(#shade)"/>'
        f'<g opacity="0.85">{"".join(groups)}</g>'
        "</svg>"
    )


RAYS = (
    f'<rect width="{WIDTH}" height="{n(HEIGHT * 0.55)}" fill="url(#glow)"/>' + light_rays()
)


# ---------- Variants ----------

def anchors(palette: dict) -> dict:
    """The app's six grays from a T3 Code palette."""
    return {
        "surface-0": palette["canvas"],
        "surface-1": palette["surface"],
        "surface-2": palette["surfaceRaised"],
        "surface-3": palette["input"],
        "text-primary": palette["text"],
        "text-secondary": mix(palette["text"], palette["textMuted"], 0.45),
        "text-muted": palette["textMuted"],
    }


def glass_tint(spec: dict) -> str:
    """The see-through panel color: --hbc-glass from the theme's CSS."""
    match = re.search(r"--hbc-glass:\s*rgba\((\d+),\s*(\d+),\s*(\d+)", spec.get("css") or "")
    if match:
        return "#" + "".join(f"{int(c):02x}" for c in match.groups())
    return "#0d1824"


def variant(spec: dict, backgrounds: dict, bubble_tints: dict) -> dict:
    key = spec["id"].removeprefix("homebrew-channel").removeprefix("-") or "default"
    palette = spec["dark"]
    tokens = {}

    if spec["background"]:
        water = backgrounds.get(spec["background"])
        if water is None:
            raise SystemExit(f"{spec['id']}: {spec['background']} is not in make-backgrounds.py's VARIATIONS.")
        shift = (water["hue"], water["saturation"], water["value"])
        tokens["water"] = stops([(o, recolor(c, *shift)) for o, c in WATER_STOPS])
        tokens["ray"] = recolor(RAY_COLOR, *shift)
        tokens["rays"] = RAYS
    else:
        tokens["water"] = stops(NAVY_STOPS)
        tokens["ray"] = RAY_COLOR
        tokens["rays"] = ""

    tint = bubble_tints.get(spec["bubbles"])
    for name, color in BUBBLE_COLORS.items():
        tokens[name] = recolor(color, tint[0], tint[1], 1.0) if tint else color

    return {
        "id": key,
        "name": spec["name"],
        "glass": glass_tint(spec),
        "anchors": anchors(palette),
        "roles": {
            "accent": palette["accent"],
            "danger": palette["error"],
            "warning": palette["warning"],
            # The T3 Code palette has no green or purple role; these keep
            # their meaning in every variation.
            "success": "#3ccf6e",
            "pro": "#a78bfa",
        },
        "tokens": tokens,
    }


def check_with_node(variants: list) -> None:
    node = shutil.which("node")
    if not node:
        print("Node not found: skipped the palette check.")
        return
    script = (
        "const { makeColors } = await import(process.argv[1]);"
        "const variants = JSON.parse(process.argv[2]); let bad = 0;"
        "for (const v of variants) {"
        "  const { problems } = makeColors({ label: v.name, only: 'dark', roles: v.roles,"
        "    dark: { gray: { anchors: v.anchors } } });"
        "  for (const p of problems) {"
        "    if (p.startsWith(\"Desktop won't paint\")) { bad++; console.log(v.id + ': ' + p) }"
        "  }"
        "}"
        "process.exit(bad ? 1 : 0)"
    )
    checked = [{k: v[k] for k in ("id", "name", "roles", "anchors")} for v in variants]
    result = subprocess.run(
        [node, "--input-type=module", "-e", script,
         (MOD / "hooks" / "make-colors.js").as_uri(), json.dumps(checked)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SystemExit("Palette check failed:\n" + result.stdout + result.stderr)
    print(f"Checked {len(variants)} palettes with make-colors.js.")


def main() -> None:
    build_theme = load_build_theme()
    assigned = read_assignments(ROOT / "scripts" / "make-backgrounds.py", {"VARIATIONS", "BUBBLE_TINTS"})
    layers = read_bubble_layers()
    template = scene_template(layers)
    variants = [variant(spec, assigned["VARIATIONS"], assigned["BUBBLE_TINTS"])
                for spec in build_theme.THEMES]

    for v in variants:
        scene = template
        for name, value in v["tokens"].items():
            scene = scene.replace("{" + name + "}", value)
        leftover = re.findall(r"\{[a-z]+\}", scene)
        if leftover:
            raise SystemExit(f"{v['id']}: unfilled scene colors {leftover}.")
        if len(scene) > SCENE_MAX_LENGTH:
            raise SystemExit(f"{v['id']}: scene is {len(scene)} characters; the app allows {SCENE_MAX_LENGTH}.")

    lines = [
        "// Generated by scripts/build-claude-mod.py. Do not edit by hand.",
        "",
        "export type Variant = {",
        "  id: string",
        "  name: string",
        "  glass: string",
        "  anchors: Record<'surface-0' | 'surface-1' | 'surface-2' | 'surface-3' | 'text-primary' | 'text-secondary' | 'text-muted', string>",
        "  roles: Record<'accent' | 'danger' | 'warning' | 'success' | 'pro', string>",
        "  tokens: Record<string, string>",
        "}",
        "",
        "/** The scene, with {token} placeholders for each variant's colors. */",
        f"export const SCENE = {json.dumps(template)}",
        "",
        f"export const VARIANTS: Variant[] = {json.dumps(variants, indent=2)}",
        "",
    ]
    OUTPUT.write_text("\n".join(lines), "utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(variants)} variants, scene template {len(template)} characters.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    manifest["userConfig"]["color"]["options"] = [v["id"] for v in variants]
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", "utf-8", newline="\n")
    print(f"Updated the color options in {MANIFEST.relative_to(ROOT)}.")

    check_with_node(variants)


if __name__ == "__main__":
    main()
