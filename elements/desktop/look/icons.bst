kind: meson

sources:
- kind: git_repo
  url: github:elementary/icons.git
  track: main
  ref: 9.0.0-53-g15f39396167bc8eb188d9e256bc79058ff4615f9

runtime-depends:
 - freedesktop-sdk.bst:components/gdk-pixbuf.bst

depends:
  - freedesktop-sdk.bst:components/librsvg.bst

build-depends:
  - freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
  - freedesktop-sdk.bst:components/pkg-config.bst
  - deps/xcursorgen.bst
