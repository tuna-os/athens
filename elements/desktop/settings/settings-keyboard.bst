kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-keyboard.git
  track: main
  ref: 8.1.1-26-g77688e3161fcf859a55ea7eec7b8e13a525e307a

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/vala.bst
- deps/libxklavier.bst
- freedesktop-sdk.bst:components/libxml2.bst
- freedesktop-sdk.bst:components/dbus.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- freedesktop-sdk.bst:components/glib.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
