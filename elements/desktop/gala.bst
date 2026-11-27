kind: meson

sources:
- kind: git_repo
  url: github:elementary/gala.git
  track: main
  ref: 8.6.2-80-g6c6e05ef753914146d8c5fd35ff58a53dd63ee43

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:components/pkg-config.bst
- freedesktop-sdk.bst:components/gettext.bst
- freedesktop-sdk.bst:components/vala.bst
- gnome-build-meta.bst:core/sysprof-app.bst
- freedesktop-sdk.bst:components/gobject-introspection.bst

runtime-depends:
- gnome-build-meta.bst:core/gnome-session.bst
- desktop/portals.bst
- freedesktop-sdk.bst:components/xdg-desktop-portal.bst
- deps/xdg-desktop-portal-gtk.bst

depends:
- freedesktop-sdk.bst:public-stacks/runtime-minimal.bst
- freedesktop-sdk.bst:components/systemd.bst
- freedesktop-sdk.bst:components/gsettings-desktop-schemas.bst
- freedesktop-sdk.bst:components/glib.bst
- freedesktop-sdk.bst:components/sqlite.bst
- deps/gtk-4.bst
- freedesktop-sdk.bst:components/gtk3.bst
- freedesktop-sdk.bst:components/desktop-file-utils.bst
- gnome-build-meta.bst:sdk/libgee.bst
- gnome-build-meta.bst:core/gnome-desktop.bst
- desktop/mutter.bst
- gnome-build-meta.bst:core-deps/libhandy.bst
- deps/granite-6.bst
- deps/granite-7.bst

config:
  install-commands:
    (>):
    - |
      install -Dm644 -t "%{install-root}/usr/share/factory/etc/xdg" \
        "%{install-root}/etc/xdg/io.elementary.desktop.wm.shell"
      rm -f "%{install-root}/etc/xdg/io.elementary.desktop.wm.shell"
      rmdir -p --ignore-fail-on-non-empty "%{install-root}/etc/xdg"