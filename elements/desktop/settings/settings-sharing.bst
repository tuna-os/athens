kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-sharing.git
  track: main
  ref: 8.0.3-15-gca94f8748f54a538a0e5a48b42c5bf4a9e10a608

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
