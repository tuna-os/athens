kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-display.git
  track: main
  ref: 8.0.3-13-g6c1af54ff9c986077a6f3b944ea9e980f1361fc6

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
