kind: meson

sources:
- kind: git_repo
  url: github:elementary/greeter.git
  track: main
  ref: 8.1.2-64-g824e7553d29a7437df18888f64446b86725e7728

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/gobject-introspection.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/gsettings-desktop-schemas.bst
- freedesktop-sdk.bst:components/gtk3.bst
- freedesktop-sdk.bst:components/desktop-file-utils.bst
- gnome-build-meta.bst:core/gnome-desktop.bst
- freedesktop-sdk.bst:components/xorg-lib-x11.bst
- gnome-build-meta.bst:sdk/gdk-pixbuf.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- desktop/lightdm.bst
- freedesktop-sdk.bst:components/glib.bst
- deps/libadwaita.bst
- desktop/mutter.bst
- gnome-build-meta.bst:core-deps/libhandy.bst
- deps/granite-7.bst
