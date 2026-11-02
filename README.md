# Athens
![Athens wordmark](branding/athens/athens-wordmark.svg)

The [Athens application icon](branding/athens/athens-logo.svg) and wallpaper
are original TunaOS artwork, separate from Elementary OS branding. The desktop
components and recipe basis retain their upstream names and attribution.

![Athens desktop wallpaper preview](branding/athens/athens-wallpaper.png)

Athens is TunaOS's Pantheon-based BuildStream recipe. Its initial recipe and image-build setup are adapted from [JumpyVi's `elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta); this is not an original TunaOS implementation. Upstream Elementary/Pantheon components retain their own names, licenses, and attribution. See [LICENSE](LICENSE) and the pinned source definitions under `elements/`.

## Build locally

Requirements:

- Podman
- `just`
- Mkosi meeting the minimum in `mkosi.conf`
- `zstd`
- `systemd`

Generate a local development signing key, then build the Mkosi disk image:

```bash
just genkey
just build-image
```

The Mkosi image and partition artifacts are written to `mkosi.output/`. This
path remains the existing disk-image build; it does not produce an OCI image
or installer ISO. Incremental state in `mkosi.cache/` is retained between builds;
use `just clean` only when deliberately discarding it. These are experimental
development disk images, not production releases or system extensions.

Build the separate Athens bootc OCI image with BuildStream, then export its OCI
layout to `buildstream-oci/`:

```bash
just build-oci
just export-oci
just load-oci
just lint-oci
```

`just export-oci` checks out the already-built `oci/athens.bst` artifact and
requires the `buildstream-oci/` destination not to exist. `just load-oci`
imports that local OCI layout into **rootful** Podman without a registry operation;
`just lint-oci` runs `bootc container lint` on that imported image.
The target layers Athens's Pantheon/codecs content over the GNOME OS OCI
base runtime, replaces the runtime identity with TunaOS Athens, selects LightDM
and Athens wallpaper defaults, and sets the `containers.bootc` image label.
It does not push to a registry.

BuildStream elements can also be inspected or built directly inside the pinned
container with `just bst show oci/athens.bst` or
`just bst build oci/athens.bst`.

## Validation and status

Pull requests run YAML/action lint, structural BuildStream lint, and read-only
BuildStream graph validation for `x86_64` and `aarch64`. Graph checks alone do
not qualify an image; source-text contract assertions are not boot tests.

For actual compilation and boot verification, dispatch the **Test** workflow
with `build_image=true`, or **Build and boot Athens candidate**. This builds
`oci/athens.bst`, exports and lints the real local image, installs a disposable
test-instrumented derivative with `bootc install to-disk`, and boots it under
UEFI/QEMU. Guest assertions check Athens identity/artwork, Pantheon session files,
and a stable running LightDM service. This is not proof of an interactive
desktop login, update flow, secure boot, or installer usability.

The same candidate is then used to produce and UEFI-boot live ISO media:

```bash
# Additional tools: squashfs-tools, dosfstools, mtools, xorriso,
# qemu-system-x86, qemu-utils and ovmf (Ubuntu package names).
just build-iso     # athens-live/athens-live.iso, normal live session
just smoke-iso     # athens-live-smoke/, powers off after guest assertions
just smoke-oci     # bootc-smoke/, disposable installed disk + serial evidence
```

The live producer uses the Tromsø systemd-boot/dmsquash-live architecture:
a pinned Debian builder creates only the initramfs against the Athens kernel;
the live desktop root is Athens, not Debian. The live account is `liveuser`
with an empty password and automatic Pantheon login; use this only on disposable
development media. SSH is not enabled by this path. The normal ISO stays running;
qualification media explicitly adds `athens.smoke=1` and powers off after
checking overlay-root live boot, Athens artwork, LightDM stability and a Gala
process owned by the live user. This media has **no GUI installer**; bootc
installation is tested separately, not disguised as live-installer coverage.

Both tools refuse existing output directories to preserve earlier evidence.
CI uploads actual OCI/ISO artifacts only after their corresponding checks
complete, plus build/serial logs on failures. `source.json` records the exact
local OCI image ID used for live media. Only x86_64 has an executable boot smoke;
aarch64 remains graph-only. No image is published to GHCR by this workflow.

Local verification on 2026-11-02 loaded the complete OCI graph successfully in
the pinned bst2 container and passed Python/Bash syntax checks and workflow lint.
An actual rootful Podman OCI-transport smoke also confirmed imports are untagged
despite `ref.name`; the load recipe now explicitly tags the imported image ID.
This is not compilation or boot evidence. No Athens image/ISO has yet completed
the new installation and live-boot qualification; treat all outputs as unqualified
until a complete candidate run and its serial evidence are available.
Source-text/config-contract tests have been removed in favor of the executable
installation/live-boot checks above; their old passing counts are not qualification.
Shared dependency caches persist across runs; candidate workflows serialize
cache writers across branches rather than racing rolling GHCR cache tags.

The GNOME OS junction's secure-boot key sources use its checked-in key-generation
template in the default `snakeoil` mode. No signing key is committed or used for
production signing; this does not establish a distributable secure-boot trust
contract.

Release publication, Athens update feeds, and production signing are not
configured. The inherited Elementary systemd-sysupdate sources and signing key
are intentionally excluded from the active Mkosi image until Athens has an
approved update endpoint and trust contract. Do not distribute generated
images as production releases.


## Acknowledgments

- [JumpyVi](https://github.com/jumpyvi) for the original BuildStream recipe and image-build basis in [`elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta).
- [Elementary OS](https://github.com/elementary) and Pantheon component maintainers for the desktop components and upstream recipes.
- [FreeDesktopSDK](https://gitlab.com/freedesktop-sdk/freedesktop-sdk) for build cache and upstream elements.
- [GnomeOS](https://gitlab.gnome.org/GNOME/gnome-build-meta) for remote element definitions.
- [Zirconium](https://github.com/zirconium-dev/zirconium-hawaii) for the repository template.
