kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-network.git
  track: main
  ref: 8.2.0-34-gdb01b23b98ee61a34861370e6c33f79f469d0bad

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

runtime-depends:
- desktop/network/nm-connection-editor.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- gnome-build-meta.bst:core-deps/libnma.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/gtk-4.bst
- deps/granite-7.bst
