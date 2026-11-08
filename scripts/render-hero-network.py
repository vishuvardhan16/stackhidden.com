#!/usr/bin/env python3
"""Render the hero background: the lineage network loop (Nov 8, 2026).

Writes eight files to assets/ (or --out):

  hero-network-dark.mp4         1920x1080, the desktop loop
  hero-network-light.mp4
  hero-network-dark-narrow.mp4  720x1080, for 920px and under
  hero-network-light-narrow.mp4
  hero-network-*.webp           each video's first frame, as its still

The picture: about 58 nodes scattered over a frame a little wider than the
screen, each joined to its nearest neighbours ahead of it, drifting on small
circles. Seven records travel routes through the network, left to right,
with fading tails: violet and cyan, and one amber record, the one that gets
flagged. A node lights up as a record passes it. The colours are the site's
own tokens (style.css), so the loop belongs to each theme.

Every frame is a function of its phase p in [0, 1), and every motion turns a
whole number of times per loop, so frame 300 would equal frame 0: the
browser's loop has no seam. 10 seconds at 30 fps.

The narrow file is the middle 720 pixels of the same scene, drawn with every
stroke and glow 1.6 times as heavy (stroke=1.6). On a phone that strip is
seen zoomed in, and at the desktop weight its 1px lines nearly vanished
under the text tint.

Encoding: H.264, yuv420p, CRF 24, preset veryfast, no audio, with the index
at the front of the file (+faststart) so playback can start before the file
has fully arrived. Compared at 24, 27, and 30: at 30 the thin lines broke up
in light mode, at 27 they thinned, and 24 kept them whole. The stills are taken from
the encoded files, not the renders, so the hand-over from still to video is
exact. WebP quality 88.

Needs Python 3 with numpy, opencv-python, and Pillow, and ffmpeg on PATH.
A full render takes a few minutes. Run from the repository root:

  python3 scripts/render-hero-network.py
  python3 scripts/render-hero-network.py --out /tmp/net --themes dark
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

TAU = 2 * math.pi
W, H = 1920, 1080
FPS, FRAMES = 30, 300
NARROW = (600, 1320)  # the middle 720 columns
NARROW_STROKE = 1.6
CRF = 24
WEBP_QUALITY = 88

# The site's colour tokens (style.css), as RGB. cyan and amber are the
# record colours; light mode uses deeper versions so they read as ink.
PALETTE = {
    "dark": {"base": (13, 16, 23), "base2": (19, 25, 42), "blue": (110, 168, 254), "violet": (139, 124, 246),
             "cyan": (125, 211, 252), "amber": (251, 191, 36)},
    "light": {"base": (244, 246, 250), "base2": (228, 235, 247), "blue": (31, 95, 208), "violet": (106, 83, 214),
              "cyan": (2, 132, 199), "amber": (180, 110, 10)},
}
LAYERS = ("blue", "violet", "cyan", "amber")


def base_gradient(theme: str) -> np.ndarray:
    """A quiet gradient, a little lighter (or deeper) toward the upper right."""
    pal = PALETTE[theme]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 0.78 * W) / W) ** 2 + ((yy - 0.18 * H) / H) ** 2)
    k = np.clip(1.15 - d * 1.3, 0, 1)[..., None] ** 1.6
    return np.array(pal["base"], np.float32) / 255 * (1 - k) + np.array(pal["base2"], np.float32) / 255 * k


# A fixed dither, the same in every frame: it breaks up banding in the
# gradient without giving the encoder motion to spend bits on. Drawn dark
# first, then light, from one generator: the order the shipped files used.
_rng = np.random.default_rng(7)
DITHER = {theme: (_rng.random((H, W, 1), np.float32) - 0.5) / 255 * 1.6 for theme in ("dark", "light")}
BASE = {theme: base_gradient(theme) for theme in ("dark", "light")}


def composite(theme: str, masks: dict) -> np.ndarray:
    """Light the layers: added as light in dark mode, laid on as ink in light."""
    pal = PALETTE[theme]
    out = BASE[theme].copy()
    for name in LAYERS:
        col = np.array(pal[name], np.float32) / 255
        m = masks[name]
        if theme == "dark":
            out += m[..., None] * col
        else:
            a = np.clip(m * 0.9, 0, 0.95)[..., None]
            out = out * (1 - a) + col * a
    rgb = (np.clip(out + DITHER[theme], 0, 1) * 255 + 0.5).astype(np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def glow(m: np.ndarray, near: float, far: float, core: float, near_k: float, far_k: float) -> np.ndarray:
    """Core plus a near and a far bloom; the far bloom is blurred at quarter size."""
    g1 = cv2.GaussianBlur(m, (0, 0), near)
    small = cv2.resize(m, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), far / 4), (W, H), interpolation=cv2.INTER_LINEAR)
    return m * core + g1 * near_k + g2 * far_k


def network_setup():
    """Nodes, edges, and record routes. Seeded, so every run draws the same network."""
    rng = np.random.default_rng(5)
    # Scattered, not gridded: dart throwing with a minimum spacing, over an
    # area a little wider than the frame so links run off its edges.
    nodes, tries, gap = [], 0, 0.105 * W
    while len(nodes) < 58 and tries < 20000:
        tries += 1
        x, y = rng.uniform(-0.08, 1.08) * W, rng.uniform(0.04, 0.96) * H
        if all((x - n["p"][0]) ** 2 + (y - n["p"][1]) ** 2 > gap * gap for n in nodes):
            nodes.append({"p": (x, y), "dr": rng.uniform(6, 15), "ph": rng.uniform(0, TAU)})
    # Each node links to its two nearest neighbours ahead of it (to the
    # right), no further than a fifth of the frame: no long spikes.
    edges, longest = [], 0.2 * W
    for i, a in enumerate(nodes):
        ahead = [j for j, b in enumerate(nodes) if b["p"][0] > a["p"][0] + 0.03 * W]
        ahead = [j for j in ahead if math.dist(a["p"], nodes[j]["p"]) < longest]
        ahead.sort(key=lambda j: math.dist(a["p"], nodes[j]["p"]))
        edges.extend((i, j) for j in ahead[:2])
    out_edges: dict = {}
    for i, j in edges:
        out_edges.setdefault(i, []).append(j)
    # Seven records start from the leftmost nodes and follow edges to the
    # far side. Record 4 is the amber one.
    routes = []
    starts = sorted(range(len(nodes)), key=lambda i: nodes[i]["p"][0])[:9]
    for s in range(7):
        node = starts[(s * 3) % len(starts)]
        route = [node]
        while node in out_edges:
            node = out_edges[node][int(rng.integers(0, len(out_edges[node])))]
            route.append(node)
        routes.append({"nodes": route, "laps": int(rng.choice([1, 1, 2])), "off": rng.uniform(0, 1),
                       "layer": "amber" if s == 4 else ("violet" if s % 2 else "cyan")})
    return nodes, edges, routes


SETUP = network_setup()


def frame(theme: str, p: float, stroke: float = 1.0) -> np.ndarray:
    """One frame at phase p, as BGR uint8. stroke scales every stroke and glow."""
    nodes, edges, routes = SETUP
    th = lambda v: max(1, int(round(v * stroke)))  # noqa: E731
    # Each node drifts once round its own small circle per loop.
    pos = np.array([(n["p"][0] + n["dr"] * math.cos(TAU * p + n["ph"]), n["p"][1] + n["dr"] * math.sin(TAU * p + n["ph"]))
                    for n in nodes], np.float32)
    m = {name: np.zeros((H, W), np.float32) for name in LAYERS}
    lines = {name: np.zeros((H, W), np.float32) for name in LAYERS}
    for i, j in edges:
        cv2.line(lines["blue"], tuple(int(v) for v in pos[i]), tuple(int(v) for v in pos[j]), 0.22, th(1), cv2.LINE_AA)
    lit = np.zeros(len(nodes), np.float32)
    for rt in routes:
        pts = pos[rt["nodes"]]
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        total = float(seg.sum())
        # The record's head runs from 200px before the route to 200px past
        # it, laps times per loop, so it enters and leaves off its ends.
        u = ((p * rt["laps"] + rt["off"]) % 1.0) * (total + 400) - 200
        samples = np.linspace(u - 170.0, u, 32)  # a 170px tail
        cum = np.concatenate([[0], np.cumsum(seg)])
        prev = None
        for k, s in enumerate(samples):
            if s < 0 or s > total:
                prev = None
                continue
            idx = min(int(np.searchsorted(cum, s, side="right")) - 1, len(seg) - 1)
            t = (s - cum[idx]) / max(seg[idx], 1e-6)
            q = pts[idx] * (1 - t) + pts[idx + 1] * t
            if prev is not None:
                cv2.line(m[rt["layer"]], prev, (int(q[0]), int(q[1])), 0.95 * (k / (len(samples) - 1)) ** 2, th(3), cv2.LINE_AA)
            prev = (int(q[0]), int(q[1]))
        for n_i, c in zip(rt["nodes"], cum):
            lit[n_i] = max(lit[n_i], math.exp(-((u - c) / (70.0 * stroke)) ** 2))
    for i, q in enumerate(pos):
        centre = (int(q[0]), int(q[1]))
        cv2.circle(lines["blue"], centre, th(4), 0.5 + 0.5 * float(lit[i]), -1, cv2.LINE_AA)
        cv2.circle(lines["blue"], centre, th(9), 0.18 + 0.6 * float(lit[i]), th(1), cv2.LINE_AA)
        if lit[i] > 0.05:
            cv2.circle(m["cyan"], centre, th(6), 0.8 * float(lit[i]), -1, cv2.LINE_AA)
    for name in LAYERS:
        m[name] = (glow(m[name], 5 * stroke, 40 * stroke, 1.0, 1.0, 0.8)
                   + glow(lines[name], 2.5 * stroke, 26 * stroke, 1.0, 0.6, 0.35))
    return composite(theme, m)


def encode(path: Path, size: str, frames) -> None:
    """Pipe raw frames to ffmpeg; write to a temporary name and rename on success."""
    tmp = path.with_name(path.stem + ".part.mp4")
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", size, "-framerate", str(FPS),
         "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(CRF), "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(tmp)],
        stdin=subprocess.PIPE,
    )
    for f in frames:
        enc.stdin.write(f.tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"ffmpeg failed on {path.name}")
    os.replace(tmp, path)


def still(video: Path) -> None:
    """The encoded file's own first frame, as a WebP next to it."""
    png = video.with_name(video.stem + ".first.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-frames:v", "1", str(png)], check=True)
    Image.open(png).convert("RGB").save(video.with_suffix(".webp"), "WEBP", quality=WEBP_QUALITY, method=6)
    png.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=Path("assets"))
    ap.add_argument("--themes", nargs="+", default=["dark", "light"], choices=["dark", "light"])
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    a, b = NARROW
    for theme in args.themes:
        wide = args.out / f"hero-network-{theme}.mp4"
        encode(wide, f"{W}x{H}", (frame(theme, i / FRAMES) for i in range(FRAMES)))
        still(wide)
        narrow = args.out / f"hero-network-{theme}-narrow.mp4"
        encode(narrow, f"{b - a}x{H}", (frame(theme, i / FRAMES, NARROW_STROKE)[:, a:b].copy() for i in range(FRAMES)))
        still(narrow)
        print(theme, wide.stat().st_size, narrow.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
