kind: meson

sources:
- kind: git_repo
  url: github:elementary/granite.git
  track: granite-7
  ref: 7.8.1-2-g6bd8892000d7a70f4a9717939d334f2ae066b1a6

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/gobject-introspection.bst
- freedesktop-sdk-extra.bst:components/sassc.bst
- deps/libshumate.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/glib.bst
- deps/gtk-4.bst
- gnome-build-meta.bst:sdk/libgee.bst
