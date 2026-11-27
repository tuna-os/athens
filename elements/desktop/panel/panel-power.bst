kind: meson

sources:
- kind: git_repo
  url: github:elementary/panel-power
  track: main
  ref: 8.0.2-60-g2c74fe9faa79297db70667fc77b3ad5adf00075e

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
- gnome-build-meta.bst:core-deps/libgtop.bst
- deps/granite-7.bst
- desktop/panel/wingpanel.bst
