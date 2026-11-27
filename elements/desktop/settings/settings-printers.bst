kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-printers.git
  track: main
  ref: 8.0.2-18-g39ab29977cb06af4871a81be308d87b3e9d354a9

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- freedesktop-sdk.bst:components/cups.bst
- desktop/settings/switchboard.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
