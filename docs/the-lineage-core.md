# The Lineage Core

The artwork at the top of the At a glance panel. A dotted sphere with rings around it, and small nodes traveling the rings.

## What it means

The sphere is governed data, drawn as a halftone core. The rings are lineage paths, the routes data takes between systems. The moving nodes are datasets traveling those routes. It is the subject of the site's research section drawn as a picture: data with a center of gravity, and everything accountable to it.

The idea of a living centerpiece came from looking at the best portfolio sites, where the main artwork moves. The subject and the drawing are this site's own. Nothing here is copied from another site.

## How it is drawn

Plain Canvas 2D in `app.js`, no libraries and no GPU shader. A shader would be heavier than one panel needs.

- The dot field is computed once at load: a grid clipped to a circle, each dot sized and faded by a simple light calculation, so the sphere reads as round.
- Three elliptical orbits are drawn as paths, tilted at different angles. Five nodes ride them, two rings one way and one ring the other, each node with a short fading trail.
- The core brightens and dims very slowly, a shimmer rather than a pulse. A full orbit takes the better part of a minute. The aim is calm, closer to a slow instrument than a screensaver.

## How it behaves

- Colors come from the theme variables, so it matches dark and light mode and recolors the moment the theme flips.
- It pauses when the panel scrolls off screen, using an IntersectionObserver, and when the browser tab is hidden.
- Under reduced motion it draws a single frame and stops.
- The still PNG versions that came before it are still in `assets/`, unreferenced, kept as the originals.
