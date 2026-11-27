kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-sound.git
  track: main
  ref: 8.0.3-27-gebdde53965188df88952c58ca3fc4d04baa4b7bb

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- gnome-build-meta.bst:sdk/libgee.bst
- desktop/settings/switchboard.bst
- freedesktop-sdk.bst:components/libpulse.bst
- gnome-build-meta.bst:core-deps/libcanberra.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libgexiv14.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
