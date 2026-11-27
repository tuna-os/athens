kind: meson

sources:
- kind: git_repo
  url: github:elementary/notifications.git
  track: main
  ref: 8.1.2-25-g55ca0cef82f3054fdc29eaa72aea331d9295561c

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst
- gnome-build-meta.bst:core-deps/libcanberra.bst
- deps/gtk-4.bst
- deps/libadwaita.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- deps/granite-7.bst
