#!/usr/bin/env python3
"""
Injects a blinking "GAME OVER" overlay into a pacman-contribution-graph SVG.
The overlay is shown only during the final GAME_OVER_MS of each animation
loop (synced to the SVG's own <durationMs> metadata) and is hidden again
right as the loop wraps back to frame 0, so the restart is seamless.
Usage: python3 add_game_over.py <input.svg> [output.svg]
If output is omitted, the input file is overwritten in place.
"""
import re
import sys

GAME_OVER_MS = 3000     # how long GAME OVER stays visible before loop restarts
BLINK_PERIOD_MS = 400   # blink speed during that window


def build_overlay(width, height, duration_ms):
    start_ms = duration_ms - GAME_OVER_MS
    if start_ms < 0:
        start_ms = 0

    # Build keyTimes/values: hidden until start_ms, then blink, then hidden
    # again right before the loop wraps (keyTime 1.0) so restart is seamless.
    key_times = [0.0, start_ms / duration_ms]
    values = ["hidden", "hidden"]

    t = start_ms
    visible = True
    while t < duration_ms - BLINK_PERIOD_MS:
        t += BLINK_PERIOD_MS
        key_times.append(round(t / duration_ms, 4))
        values.append("visible" if visible else "hidden")
        visible = not visible

    key_times.append(1.0)
    values.append("hidden")

    kt = ";".join(f"{k:.4f}" for k in key_times)
    vals = ";".join(values)

    cx = width / 2
    cy = height / 2
    font_size = max(14, min(28, height * 0.22))

    # NOTE: visibility is animated directly on each element (rect and text)
    # rather than on a wrapping <g>. Some SVG renderers (including how
    # GitHub displays raw SVGs) don't reliably propagate an animated
    # attribute value through inheritance to children -- they only look at
    # the static attribute. The upstream library itself avoids wrapping
    # groups for this exact reason (every ghost <use> animates its own
    # visibility individually), so we follow the same pattern here.
    return f'''<rect x="0" y="0" width="{width}" height="{height}" fill="#000000" opacity="0.55" visibility="hidden">
\t<animate attributeName="visibility" dur="{duration_ms}ms" repeatCount="indefinite"
\t\tkeyTimes="{kt}" values="{vals}" />
</rect>
<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle"
\tfont-family="'Press Start 2P', 'Courier New', monospace" font-weight="bold"
\tfont-size="{font_size}" fill="#ffff00" stroke="#000000" stroke-width="0.5" visibility="hidden">GAME OVER
\t<animate attributeName="visibility" dur="{duration_ms}ms" repeatCount="indefinite"
\t\tkeyTimes="{kt}" values="{vals}" />
</text>'''


def main():
    if len(sys.argv) < 2:
        print("Usage: add_game_over.py <input.svg> [output.svg]", file=sys.stderr)
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else in_path

    with open(in_path, "r", encoding="utf-8") as f:
        svg = f.read()

    w_match = re.search(r'<svg[^>]*\swidth="(\d+)"', svg)
    h_match = re.search(r'<svg[^>]*\sheight="(\d+)"', svg)
    d_match = re.search(r"<durationMs>(\d+)</durationMs>", svg)

    if not (w_match and h_match and d_match):
        print(f"WARNING: could not find width/height/durationMs in {in_path}, skipping overlay", file=sys.stderr)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        return

    width = int(w_match.group(1))
    height = int(h_match.group(1))
    duration_ms = int(d_match.group(1))

    overlay = build_overlay(width, height, duration_ms)

    if "</svg>" not in svg:
        print(f"WARNING: no closing </svg> tag found in {in_path}, skipping overlay", file=sys.stderr)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        return

    svg = svg.replace("</svg>", overlay + "</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Injected GAME OVER overlay into {out_path}")


if __name__ == "__main__":
    main()
