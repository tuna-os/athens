kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-mouse-touchpad.git
  track: main
  ref: 8.1.0-71-g370da929b37d151fb0ca9661173df9bcf0e7e154

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- desktop/settings/switchboard.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
