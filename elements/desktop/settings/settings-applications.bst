kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-applications.git
  track: main
  ref: 8.3.0-33-ga8db1fe5898321a81eddc18d1bbf92ed1f08ccf6

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- freedesktop-sdk.bst:components/flatpak.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
