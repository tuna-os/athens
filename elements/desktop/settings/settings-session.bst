kind: meson

sources:
- kind: git_repo
  url: github:elementary/session-settings.git
  track: main
  ref: 8.1.0-15-g467f5c56e3c74d3974a038635cde2b7a6bb16872

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst