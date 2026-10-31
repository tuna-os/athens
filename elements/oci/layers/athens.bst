kind: compose
description: Athens runtime layer for the OCI bootc image

build-depends:
  - freedesktop-sdk.bst:components/gcc.bst
  - oci/layers/athens-stack.bst

config:
  exclude:
    - debug
    - extra
    - static-blocklist
