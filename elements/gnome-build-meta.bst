kind: junction

sources:
- kind: git_repo
  url: gnome:gnome-build-meta.git
  track: gnome-51
  ref: 51.1-36-g8a89846df11e86cee57c728a86a247e61d604b84
- kind: patch_queue
  path: patches/gnome-build-meta

config:
  options:
    arch: '%{arch}'
    # No separate compiler executor is configured. Keep compiler-cache lookups,
    # but run misses in the existing sandbox instead of one REAPI sandbox/job.
    recc: cache-only
  overrides:
    # Keep the upstream SDK junction and its coherent GNOME library overrides.
    # The theme must be replaced before GNOME's initramfs is assembled too.
    gnomeos-deps/plymouth-gnome-theme.bst: branding/plymouth.bst
    oci/integration/os-release.bst: os-release.bst
    # Replacing SDK libraries with independent FD versions broke GLib/at-spi
    # minimum versions and dropped transitive sysprof development dependencies.
    freedesktop-sdk.bst:components/networkmanager.bst: gnome-build-meta.bst:core-deps/NetworkManager.bst
    freedesktop-sdk.bst:components/appstream.bst: deps/appstream.bst
    freedesktop-sdk.bst:components/udisks.bst: gnome-build-meta.bst:core-deps/udisks2.bst
    freedesktop-sdk.bst:components/libplist.bst: gnome-build-meta.bst:core-deps/libplist.bst
    freedesktop-sdk.bst:components/libimobiledevice.bst: gnome-build-meta.bst:core-deps/libimobiledevice.bst
    freedesktop-sdk.bst:components/fwupd.bst: gnome-build-meta.bst:core-deps/fwupd.bst
    freedesktop-sdk.bst:components/upower.bst: gnome-build-meta.bst:core-deps/upower.bst
    freedesktop-sdk.bst:components/colord.bst: gnome-build-meta.bst:core-deps/colord.bst
    core-deps/librest.bst: deps/librest.bst
    core-deps/libshumate.bst: deps/libshumate.bst
    sdk/gtk.bst: deps/gtk-4.bst
    sdk/libadwaita.bst: deps/libadwaita.bst
    core-deps/gnome-online-accounts.bst: deps/gnome-online-accounts.bst
