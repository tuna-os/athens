kind: meson

sources:
- kind: git_repo
  url: github:elementary/session-settings.git
  track: main
  ref: 10e8d30652dc522b68585561980f9b5afe8a6a1d

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/pkg-config.bst

depends:
- gnome-build-meta.bst:core/gnome-settings-daemon.bst

runtime-depends:
- gnome-build-meta.bst:core/gnome-session.bst
- desktop/gala.bst

