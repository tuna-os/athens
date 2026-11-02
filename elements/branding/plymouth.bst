kind: manual
description: Athens watermark and default spinner theme, including installed initramfs

sources:
- kind: local
  path: branding/athens

runtime-depends:
- gnome-build-meta.bst:core-deps/plymouth.bst

build-depends:
- freedesktop-sdk.bst:public-stacks/runtime-gnu.bst

variables:
  strip-binaries: ''

config:
  install-commands:
  - install -Dm644 athens-boot-logo.png '%{install-root}%{datadir}/plymouth/themes/spinner/watermark.png'
  - |
    mkdir -p '%{install-root}%{datadir}/plymouth'
    printf '[Daemon]\nTheme=spinner\nShowDelay=0\n' > '%{install-root}%{datadir}/plymouth/plymouthd.defaults'
  - '%{install-extra}'

public:
  bst:
    overlap-whitelist:
    - '%{datadir}/plymouth/plymouthd.defaults'
    - '%{datadir}/plymouth/themes/spinner/watermark.png'
