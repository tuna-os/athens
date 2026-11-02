kind: stack
description: Host commands used by the shipped GTK installer and fisherman

depends:
- gnome-build-meta.bst:sdk/at-spi2-core.bst
- gnome-build-meta.bst:sdk/pygobject.bst
- freedesktop-sdk.bst:components/flatpak.bst
- freedesktop-sdk.bst:components/flatpak-xdg-utils.bst
- freedesktop-sdk.bst:components/polkit.bst
- freedesktop-sdk.bst:components/podman.bst
- freedesktop-sdk.bst:components/skopeo.bst
- freedesktop-sdk.bst:components/cryptsetup.bst
- freedesktop-sdk.bst:components/parted.bst
- freedesktop-sdk.bst:components/util-linux.bst
- freedesktop-sdk.bst:components/dosfstools.bst
- freedesktop-sdk.bst:components/e2fsprogs.bst
- freedesktop-sdk.bst:components/btrfs-progs.bst
- freedesktop-sdk.bst:components/xfsprogs.bst
- freedesktop-sdk.bst:components/openssh-systemd.bst
