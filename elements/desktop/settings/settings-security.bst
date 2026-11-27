kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-security-privacy
  track: main
  ref: 8.0.2-23-g15142e14f3d88c640a54f570acfe4c37bff46a3e

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/polkit-gobject.bst
- deps/libzeitgeist.bst

depends:
- desktop/settings/switchboard.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
