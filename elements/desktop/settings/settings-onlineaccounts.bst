kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-onlineaccounts.git
  track: main
  ref: 8.0.2-42-g2f370b8a0d916a34706fcf4b1887b4bddb52372e

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- deps/libevolution-minimal.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/gtk-4.bst
- deps/granite-7.bst
