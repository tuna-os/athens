kind: meson

sources:
- kind: git_repo
  url: github:elementary/settings-useraccounts.git
  track: main
  ref: 8.0.1-102-gabd23276d1bde1f7a7d30137dfb6258fe92a2d39

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk-extra.bst:components/accountsservice.bst
- gnome-build-meta.bst:core/gnome-desktop.bst
- freedesktop-sdk.bst:components/polkit-gobject.bst
- freedesktop-sdk.bst:components/glib.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:components/systemd.bst
- desktop/settings/switchboard.bst
- freedesktop-sdk.bst:components/pwquality.bst
- gnome-build-meta.bst:core/gnome-settings-daemon.bst
- deps/libadwaita.bst
- deps/gtk-4.bst
- deps/granite-7.bst
