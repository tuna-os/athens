kind: meson

sources:
- kind: git_repo
  url: github:elementary/granite.git
  track: main
  ref: 7.8.1-172-g95fe4658b9e8349b231b640b329b75a04486a394

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/gobject-introspection.bst
- freedesktop-sdk-extra.bst:components/sassc.bst
- gnome-build-meta.bst:core-deps/libshumate.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/glib.bst
- deps/gtk-4.bst
- gnome-build-meta.bst:sdk/libgee.bst
