kind: meson

sources:
- kind: git_repo
  url: github:elementary/pantheon-agent-polkit.git
  track: main
  ref: 8.1.0-17-g8a3785a4ccaf7f063fc8e5967fd9923725f8592e

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- deps/granite-7.bst
- deps/gtk-4.bst
- deps/libadwaita.bst
- deps/pantheon-wayland.bst
- freedesktop-sdk.bst:components/systemd.bst
- freedesktop-sdk.bst:components/polkit.bst
- freedesktop-sdk.bst:components/polkit-gobject.bst
- gnome-build-meta.bst:sdk/gcr.bst