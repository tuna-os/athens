kind: manual
description: >-
  Original Athens identity artwork by TunaOS: icon, wordmark, and wallpaper
  asset. It is separate from Elementary OS artwork.

sources:
- kind: local
  path: branding/athens

build-depends:
- freedesktop-sdk.bst:public-stacks/runtime-gnu.bst

config:
  install-commands:
  - install -Dm644 athens-logo.svg '%{install-root}%{datadir}/icons/hicolor/scalable/apps/athens-logo.svg'
  - install -Dm644 athens-wordmark.svg '%{install-root}%{datadir}/tunaos/branding/athens-wordmark.svg'
  - install -Dm644 athens-wallpaper.svg '%{install-root}%{datadir}/tunaos/branding/athens-wallpaper.svg'
  - install -Dm644 athens-wallpaper.png '%{install-root}%{datadir}/backgrounds/TunaOS/Athens/athens-wallpaper.png'
  - |
    mkdir -p '%{install-root}%{datadir}/glib-2.0/schemas'
    cat >'%{install-root}%{datadir}/glib-2.0/schemas/99_athens.gschema.override' <<'EOF'
    [org.gnome.desktop.background]
    picture-uri='file:///usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png'
    picture-uri-dark='file:///usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png'
    picture-options='zoom'
    EOF
  - '%{install-extra}'

variables:
  strip-binaries: ''
