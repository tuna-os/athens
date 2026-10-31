<div align="center">
  <h1>Athens</h1>
  <p><strong>Athens is TunaOS's Pantheon-based BuildStream recipe.</strong></p>
</div>

Athens adapts the recipe and image build setup from [JumpyVi's `elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta). JumpyVi's project is the basis of this recipe; Athens is not an original implementation by TunaOS. The desktop and applications are built from upstream Elementary/Pantheon and Freedesktop components, whose names and licenses remain those of their respective projects. See [LICENSE](LICENSE) and the source references in `elements/`.

## Build locally

Runtime dependencies:

- podman
- just
- zstd
- systemd

Generate local signing keys and build:

```bash
just genkey
just do-release
```

The full image build may take more than two hours and use around 90 GB of disk space. Build a single BuildStream element with `just bst build desktop/gala.bst`.

## Project status

The Athens recipe and image identity are being adapted for TunaOS. Release publishing, update feeds, signing credentials, and product qualification are not configured; do not enable release workflows or distribute images as production releases until those paths are reviewed.

## Acknowledgments

- [JumpyVi](https://github.com/jumpyvi) for the original BuildStream recipe and image-build basis in [`elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta).
- [Elementary OS](https://github.com/elementary) and Pantheon component maintainers for the desktop components and upstream recipes.
- [FreeDesktopSDK](https://gitlab.com/freedesktop-sdk/freedesktop-sdk) for build cache and upstream elements.
- [GnomeOS](https://gitlab.gnome.org/GNOME/gnome-build-meta) for remote element definitions.
- [Zirconium](https://github.com/zirconium-dev/zirconium-hawaii) for the repository template.
