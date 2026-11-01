kind: manual
description: >-
  Original Athens identity artwork by TunaOS: icon, wordmark, and wallpaper
  asset. It is separate from Elementary OS artwork.

sources:
- kind: local
  path: branding/athens

depends:
- gnome-build-meta.bst:freedesktop-sdk.bst:public-stacks/runtime-minimal.bst

config:
  install-commands:
  - install -Dm644 athens-logo.svg '%{install-root}%{datadir}/icons/hicolor/scalable/apps/athens-logo.svg'
  - install -Dm644 athens-wordmark.svg '%{install-root}%{datadir}/tunaos/branding/athens-wordmark.svg'
  - install -Dm644 athens-wallpaper.svg '%{install-root}%{datadir}/tunaos/branding/athens-wallpaper.svg'
  - install -Dm644 athens-wallpaper.png '%{install-root}%{datadir}/backgrounds/TunaOS/Athens/athens-wallpaper.png'
  - '%{install-extra}'

variables:
  strip-binaries: ''
