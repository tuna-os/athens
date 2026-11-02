kind: script
description: |
  Athens OCI image — Pantheon desktop layered on the GNOME OS bootc base.

build-depends:
  - gnome-build-meta.bst:freedesktop-sdk.bst:components/fakecap.bst
  - gnome-build-meta.bst:freedesktop-sdk.bst:components/oci-builder.bst
  - freedesktop-sdk.bst:components/glib.bst
  - gnome-build-meta.bst:core-deps/dconf.bst
  - gnome-build-meta.bst:freedesktop-sdk.bst:vm/prepare-image.bst
  - oci/layers/athens-init-scripts.bst
  - filename: gnome-build-meta.bst:oci/gnomeos/image.bst
    config:
      location: /parent
  - filename: oci/layers/athens.bst
    config:
      location: /layer
  # Replace GNOME OS identity after composition, without overlapping elements.
  - filename: os-release.bst
    config:
      location: /identity

environment:
  LD_PRELOAD: /usr/libexec/fakecap/fakecap.so
  FAKECAP_DB: /fakecap

variables:
  sysroot-seed: 6e3d9bb4-d4d4-4f87-ae6c-10d44c7a7be2

config:
  commands:
    - mkdir /fakecap
    - |
      prepare-image.sh \
         --sysroot /layer \
         --initscripts /initial_scripts \
         --seed "%{sysroot-seed}" \
         --noroot --noboot >/dev/null

    - |
      systemd-sysusers --root /layer

    - |
      glib-compile-schemas /layer/usr/share/glib-2.0/schemas

    - |
      dconf update /layer/etc/dconf/db

    # bootc images must not have both /etc and /usr/etc.
    - |
      if [ -d /layer/usr/etc ]; then
        mkdir -p /layer/etc
        cp -a /layer/usr/etc/. /layer/etc/
        rm -rf /layer/usr/etc
      fi

    - |
      cp /identity/usr/lib/os-release /layer/usr/lib/os-release
      ln -sfn ../usr/lib/os-release /layer/etc/os-release
      systemctl --root=/layer set-default graphical.target
      systemctl --root=/layer enable --force lightdm.service

    - |
      cd "%{install-root}"
      build-oci <<EOF
      mode: oci
      gzip: disabled
      images:
      - os: linux
        architecture: "%{go-arch}"
        parent:
          image: /parent
        layer: /layer
        comment: "Import Athens Pantheon desktop layer"
        config:
          Labels:
            'com.github.containers.toolbox': 'true'
            'org.opencontainers.image.title': 'Athens'
            'org.opencontainers.image.description': 'Athens Pantheon desktop image based on GNOME OS'
            'org.opencontainers.image.vendor': 'TunaOS'
            'org.opencontainers.image.licenses': 'GPL-3.0'
            'org.opencontainers.image.url': 'https://github.com/tuna-os/athens'
            'org.opencontainers.image.source': 'https://github.com/tuna-os/athens'
            'containers.bootc': '1'
        index-annotations:
          'org.opencontainers.image.ref.name': 'ghcr.io/tuna-os/athens:latest'
      EOF
