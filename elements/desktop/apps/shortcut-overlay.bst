kind: meson

sources:
- kind: git_repo
  url: github:elementary/shortcut-overlay.git
  track: main
  ref: 8.1.0-79-g277a7812ef0944a811a61f6164c0e9e3e1b3448d

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- gnome-build-meta.bst:sdk/libgee.bst
- deps/pantheon-wayland.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/glib.bst
- freedesktop-sdk.bst:components/desktop-file-utils.bst
- deps/gtk-4.bst
- deps/libadwaita.bst
- freedesktop-sdk.bst:components/sqlite.bst
- deps/granite-9.bst
