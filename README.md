# Athens

Athens is TunaOS's Pantheon-based BuildStream recipe. Its initial recipe and image-build setup are adapted from [JumpyVi's `elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta); this is not an original TunaOS implementation. Upstream Elementary/Pantheon components retain their own names, licenses, and attribution. See [LICENSE](LICENSE) and the pinned source definitions under `elements/`.

## Build locally

Requirements:

- Podman
- `just`
- Mkosi meeting the minimum in `mkosi.conf`
- `zstd`
- `systemd`

Generate a local development signing key, then build the disk image:

```bash
just genkey
just build-image
```

The image and partition artifacts are written to `mkosi.output/`. This recipe does not produce a qualified installer ISO or production release. Build a single BuildStream element in the pinned container with `just bst show desktop/gala.bst` or `just bst build stacks/athens.bst`.

## Validation and status

Pull requests run YAML/action lint, structural BuildStream lint, product-contract tests, and BuildStream graph validation for `x86_64` and `aarch64`. CI validates the graph; it does not compile the full image or prove boot/install behavior.

Release publication, Athens update feeds, and production signing are not configured. The inherited Elementary systemd-sysupdate sources and signing key are intentionally excluded from the active image until Athens has an approved update endpoint and trust contract. Do not distribute generated images as production releases.

## Acknowledgments

- [JumpyVi](https://github.com/jumpyvi) for the original BuildStream recipe and image-build basis in [`elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta).
- [Elementary OS](https://github.com/elementary) and Pantheon component maintainers for the desktop components and upstream recipes.
- [FreeDesktopSDK](https://gitlab.com/freedesktop-sdk/freedesktop-sdk) for build cache and upstream elements.
- [GnomeOS](https://gitlab.gnome.org/GNOME/gnome-build-meta) for remote element definitions.
- [Zirconium](https://github.com/zirconium-dev/zirconium-hawaii) for the repository template.
