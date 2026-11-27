kind: meson

sources:
- kind: git_repo
  url: github:elementary/stylesheet.git
  track: main
  ref: 8.2.2-46-g5955a2ce3992dfaf79742ed9025bb17335e893da

build-depends:
- freedesktop-sdk.bst:public-stacks/buildsystem-meson.bst
- freedesktop-sdk-extra.bst:components/sassc.bst
