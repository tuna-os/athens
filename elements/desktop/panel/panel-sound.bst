kind: meson

sources:
- kind: git_repo
  url: github:elementary/panel-sound
  track: main
  ref: 8.0.3-39-g649ec3ca43556b6805865452cc10abbee4ec1659

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/gsettings-desktop-schemas.bst
- freedesktop-sdk.bst:components/glib.bst
- deps/gtk-4.bst
- gnome-build-meta.bst:sdk/libnotify.bst
- freedesktop-sdk.bst:components/libpulse.bst
- deps/granite-7.bst
- desktop/panel/wingpanel.bst
