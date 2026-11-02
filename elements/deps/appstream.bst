# SPDX-FileCopyrightText: Freedesktop-SDK Developers
# SPDX-License-Identifier: MIT
#
# Full SDK AppStream with the Vala bindings required by Pantheon.

kind: meson

# Share the canonical source pin with the SDK's bootstrap AppStream provider.
(@):
- freedesktop-sdk.bst:elements/include/appstream-source.yml

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk.bst:bootstrap/sed.bst
- freedesktop-sdk.bst:components/docbook5-xsl.bst
- freedesktop-sdk.bst:components/gperf.bst
- freedesktop-sdk.bst:components/itstool.bst
- freedesktop-sdk.bst:components/libxslt.bst
- freedesktop-sdk.bst:components/python3-gi-docgen.bst
- freedesktop-sdk.bst:components/vala.bst
- freedesktop-sdk.bst:components/wayland.bst

depends:
- freedesktop-sdk.bst:components/bash-completion.bst
- freedesktop-sdk.bst:components/cairo.bst
- freedesktop-sdk.bst:components/curl.bst
- freedesktop-sdk.bst:components/fontconfig.bst
- freedesktop-sdk.bst:components/freetype.bst
- freedesktop-sdk.bst:components/gdk-pixbuf.bst
- freedesktop-sdk.bst:components/glib-networking.bst
- freedesktop-sdk.bst:components/glib.bst
- freedesktop-sdk.bst:components/gobject-introspection.bst
- freedesktop-sdk.bst:components/libfyaml.bst
- freedesktop-sdk.bst:components/librsvg.bst
- freedesktop-sdk.bst:components/libxml2.bst
- freedesktop-sdk.bst:components/libxmlb.bst
- freedesktop-sdk.bst:components/pango.bst
- freedesktop-sdk.bst:components/systemd-libs.bst
- freedesktop-sdk.bst:components/zstd.bst

variables:
  meson-local: >-
    -Dstemming=false
    -Dcompose=true
    -Dtools=true
    -Dsvg-support=true
    -Dgir=true
    -Dsystemd=true
    -Ddocs=false
    -Dapidocs=true
    -Dman=true
    -Dblake3-support=false
    -Dvapi=true

public:
  bst:
    split-rules:
      devel:
        (>):
        - '%{libdir}/libappstream-compose.so'
        - '%{libdir}/libappstream.so'
        - '%{bindir}'
        - '%{bindir}/**'
