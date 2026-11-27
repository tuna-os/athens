kind: meson

sources:
- kind: git_repo
  url: github:elementary/panel-notifications
  track: main
  ref: 7.1.1-154-ga448f173dfed86478944d4a03002b6eff8c322e8

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
- deps/libadwaita.bst
- freedesktop-sdk.bst:components/gdk-pixbuf.bst
- desktop/panel/wingpanel.bst
- deps/granite-7.bst
- desktop/panel/wingpanel.bst
