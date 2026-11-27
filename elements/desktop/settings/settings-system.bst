kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-system
  track: main
  ref: 8.2.3-18-g9e53d664a624b975425843df0e0dcfe40b98e41f

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/gobject-introspection.bst
- deps/appstream-minimal.bst

depends:
- freedesktop-sdk.bst:components/fwupd.bst
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- deps/gtk-4.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/udisks.bst
- freedesktop-sdk.bst:components/polkit-gobject.bst
- gnome-build-meta.bst:core-deps/libgtop.bst
- deps/libadwaita.bst
- gnome-build-meta.bst:sdk/libsoup.bst
- desktop/settings/switchboard.bst
- deps/packagekit-glib2.bst
- deps/granite-7.bst
