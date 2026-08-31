# photonics-toolkit

Working Python tools for optics and signal processing — built from real R&D
workflows. Each folder is a self-contained project with its own README and
runnable example.

## Tools

| Tool | What it does |
|------|--------------|
| [**knife-edge-beam-profiler**](knife-edge-beam-profiler/) | Measure a focused beam's FWHM / 1-e² diameter from a knife-edge scan (edge response → derivative → Gaussian fit). Works for visible, IR, or THz beams. |
| [**Snells Law Basic**](Snells%20Law%20Basic/) | Interactive Matplotlib visualizer for refraction, critical angle, and total internal reflection at a flat interface. |
| [**Snells Law For Curved Surfaces**](Snells%20Law%20For%20Curved%20Surfaces/) | Tkinter GUI tracing ray refraction at concave/convex spherical surfaces about the local surface normal. |
| [**Lens Manufacturing**](Lens%20Manufacturing/) | Interactive lens-geometry simulator: draws the cross-section, computes focal length / FFL / BFL from the thick-lens equation, and flags manufacturability (sag, edge-thickness, hemisphere limits). |

## Quick start

```bash
git clone https://github.com/S-Sid/photonics-toolkit.git
cd photonics-toolkit
pip install -r requirements.txt
```

Then `cd` into any tool folder and follow its README.

## License

MIT — see [LICENSE](LICENSE).
