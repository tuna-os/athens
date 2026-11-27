kind: meson

sources:
- kind: git_repo
  url: github:elementary/portals.git
  track: main
  ref: 8.2.0-53-g9d6fd99e69ebb37279d0395e2cc83e6a11f80f26

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/glib.bst
- deps/gtk-4.bst
- gnome-build-meta.bst:core-deps/vte.bst
- freedesktop-sdk.bst:components/systemd.bst
- freedesktop-sdk-extra.bst:components/accountsservice.bst
- deps/libadwaita.bst
- deps/pantheon-wayland.bst
- deps/granite-7.bst
