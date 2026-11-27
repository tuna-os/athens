kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-notifications.git
  track: main
  ref: 8.0.1-16-g1eb5b306f519b5e76e60c84b693989a83688471f

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/gtk-4.bst
- deps/granite-7.bst
