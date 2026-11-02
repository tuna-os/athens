# Athens
![Athens wordmark](branding/athens/athens-wordmark.svg)

TunaOS created the [Athens application icon](branding/athens/athens-logo.svg)
and wallpaper, separate from Elementary OS artwork. The desktop components
and recipe basis retain their upstream names and attribution.

![Athens desktop wallpaper preview](branding/athens/athens-wallpaper.png)

Athens is TunaOS's Pantheon-based BuildStream recipe. TunaOS adapted the initial recipe and image-build setup from [JumpyVi's `elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta). This is not an original TunaOS implementation. Upstream Elementary/Pantheon components retain their own names, licenses, and attribution. See [LICENSE](LICENSE) and the pinned source definitions under `elements/`.

## Build locally

Requirements:

- Podman
- `just`
- Mkosi at or above the minimum in `mkosi.conf`
- `zstd`
- `systemd`

Generate a local development key, then build the Mkosi disk image:

```bash
just genkey
just build-image
```

Mkosi writes the image and partition artifacts to `mkosi.output/`.
This path produces images for disks, not OCI images or installer ISOs.
It retains incremental state in `mkosi.cache/` between builds.
Use `just clean` only to discard that state.
These images are experiments, not production releases or system extensions.

Build the Athens image for bootc with BuildStream, then export its OCI
layout to `buildstream-oci/`:

```bash
just build-oci
just export-oci
just load-oci
just lint-oci
```

`just export-oci` checks out the completed `oci/athens.bst` artifact.
The `buildstream-oci/` destination must not exist.
`just load-oci` imports that local layout into **rootful** Podman without a registry operation.
`just lint-oci` runs `bootc container lint` on the imported image.

The target adds Pantheon and codecs to the OCI base from GNOME OS.
It sets the TunaOS Athens identity, LightDM and wallpaper defaults, and the `containers.bootc` image label.
It does not push to a registry.

Pantheon includes upstream `elementary/session-settings`, which supplies the
Wayland session descriptors and user units.
The `pantheon-wayland` integration library alone does not provide a session that LightDM can launch.
Local checks fetched the pinned session provider and resolved its dependencies.
Those checks do not prove that it compiles.

Inspect or build elements inside the pinned container with
`just bst show oci/athens.bst` or `just bst build oci/athens.bst`.

## Validation and status

For pull requests, CI checks YAML, actions and BuildStream structure.
They also validate the graph for `x86_64` and `aarch64` without a build.
Graph checks alone do not qualify an image; source-text assertions are not boot tests.

For compilation and boot checks, dispatch **Test** with `build_image=true`,
or **Build and boot Athens candidate**.
The workflow builds `oci/athens.bst`, exports and lints the local image,
and installs a disposable derivative with test instrumentation through `bootc install to-disk`.
It then boots that disk under UEFI/QEMU.

Guest assertions check the Athens identity and artwork, Pantheon session files,
and LightDM service stability.
They do not prove that desktop login, updates, secure boot, or the installer work for a user.

The workflow uses the same candidate to produce and UEFI-boot live ISO media:

```bash
# Additional tools: squashfs-tools, dosfstools, mtools, xorriso,
# qemu-system-x86, qemu-utils and ovmf (Ubuntu package names).
just build-iso     # athens-live/athens-live.iso, normal live session
just smoke-iso     # athens-live-smoke/, powers off after guest assertions
just smoke-oci     # bootc-smoke/, disposable installed disk + serial evidence
```

The live producer uses the Tromsø systemd-boot/dmsquash-live architecture.
A pinned Debian builder creates only the initramfs against the Athens kernel.
The live desktop root is Athens, not Debian.
The live account is `liveuser`, with an empty password and automatic Pantheon login.
Use this only on disposable development media.
This path does not enable SSH.

The normal ISO does not shut down automatically.
Qualification media adds `athens.smoke=1`.
It checks overlay-root boot, Athens artwork, LightDM stability and a Gala process owned by the live user, then shuts down.
This media has **no GUI installer**.
Other checks verify installation through bootc, not a live installer.

After Gala starts, the live smoke captures `desktop.png` through QEMU's monitor.
Inspect that artifact before a claim about visual identity.

Both tools refuse existing output directories to preserve earlier evidence.
CI uploads OCI/ISO artifacts only after their corresponding checks complete.
It also uploads build and serial logs on failures.
`source.json` records the local image ID for the live media.
Only x86_64 has an executable boot smoke; aarch64 remains graph-only.
This workflow does not publish images to GHCR.

Local checks on 2026-11-02 loaded the complete OCI graph in the pinned bst2 container.
Python/Bash syntax checks and workflow lint passed.
A smoke with rootful Podman showed that OCI imports have no tag despite `ref.name`.
The load recipe now tags the imported image ID.

Local builds exported the identity and artwork elements.
Checks compared the exported `os-release`, wallpaper defaults and artwork hashes.
These limited smokes are not full OS compilation or boot evidence.
No Athens image/ISO has completed installation and live-boot qualification.
Executable installation and live-boot checks replace source-text assertions; old test counts are not qualification.

Caches retain dependencies across runs.
Candidate workflows serialize writes across branches to avoid races on mutable GHCR tags.
Source archives use separate snapshots for each run.
Jobs restore these by recipe and architecture.
Explicit saves run even after build failures, so later jobs can reuse the new sources.

The CI cache quota is 60G, as in the other desktop projects.
It limits stale artifacts, not active builds or image exports.

The first candidate run,
[41391122198](https://github.com/tuna-os/athens/actions/runs/41391122198),
passed graph checks for both architectures, workflow lint, the plan and its core build.
That build pulled 199 cached artifacts and built one.
Dependency chunks then failed on recipe errors and a live-cache archive race.
That run did not qualify an OCI image or ISO.

The graph now reuses GNOME's pinned SDK junctions, not incompatible independent GLib and accessibility libraries.
This restores GNOME's transitive Sysprof dependency without loss of profile tools or version checks.
Recipes declare the Python/GI, libsoup and Wayland-protocol dependencies that their pinned sources need.

The GNOME junction receives the explicit architecture option.
A local check for `aarch64` resolved the SDK's `binary-seed-aarch64.bst`, not host-default x86_64 dependencies.
This is graph evidence, not ARM boot evidence.

AppStream's bootstrap tools keep the SDK source pin.
The full composer uses that source with SVG support and Pantheon Vala bindings.
Vala consumers use the full provider, not the minimal library.
Flatpak-builder keeps its compose dependency.

CI builds stop on genuine errors before a timeout.
Before a CAS snapshot, shared CI stops residual builder containers.
It uploads full build logs separately and fails on archive mutation errors.

The next candidate run,
[41446531247](https://github.com/tuna-os/athens/actions/runs/41446531247),
reused 180 core artifacts, pulled 20 and built one.
It saved all chunk caches.
WebKit failed because RECC's local REAPI executor could not `fork()` (`EAGAIN`), not because of a reported C++ source error.

GNOME now uses its supported `cache-only` compiler mode.
Cache hits remain reusable; misses compile in the existing build sandbox.
Upstream excludes that execution-policy environment variable from artifact keys.
A check with pinned BuildStream confirmed the requested environment and the unchanged key prefix for WebKit (`c3db2faa`).
This does not prove that WebKit compiles or that the OS boots.

The GNOME OS junction uses its committed template to generate secure-boot keys in default `snakeoil` mode.
The repository contains no private key for production use.
These development keys do not establish production trust.

Athens has no release publication, update feed or production signature configuration.
The Mkosi image excludes the sources and key for systemd-sysupdate from Elementary.
Athens needs an approved update endpoint and trust contract first.
Do not distribute generated images as production releases.


## Acknowledgments

- [JumpyVi](https://github.com/jumpyvi) for the original BuildStream recipe and image-build basis in [`elementary-build-meta`](https://github.com/jumpyvi/elementary-build-meta).
- [Elementary OS](https://github.com/elementary) and Pantheon component maintainers for the desktop components and upstream recipes.
- [FreeDesktopSDK](https://gitlab.com/freedesktop-sdk/freedesktop-sdk) for build cache and upstream elements.
- [GnomeOS](https://gitlab.gnome.org/GNOME/gnome-build-meta) for remote element definitions.
- [Zirconium](https://github.com/zirconium-dev/zirconium-hawaii) for the repository template.
