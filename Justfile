export bst2_image := env("BST2_IMAGE", "registry.gitlab.com/freedesktop-sdk/infrastructure/freedesktop-sdk-docker-images/bst2:64eb0b4930d57a92710822898fb73af6cc1ae35d")
default:
    #!/usr/bin/env bash
    set -xeuo pipefail
    just --choose


build-image:
    #!/usr/bin/env bash
    set -euo pipefail
    MKOSI="$(command -v mkosi || echo "$HOME/.local/bin/mkosi")"
    sudo rm -rf mkosi.output/
    sudo "$MKOSI" build -ff
    sudo chown -R "$(id -u):$(id -g)" mkosi.output
    sudo chmod -R u+rwX mkosi.output



genkey:
    # Like `mkosi genkey`, but with a fixed-length serial so every build's verity signature is the same size.
    # A random serial is a byte shorter 1 in 256 times, and a shorter signature written over a longer one
    # by an installed system's sysupdate leaves the old tail behind and breaks boot.
    OPENSSL_CONF=/dev/null openssl req -new -x509 -newkey rsa:2048 -keyout mkosi.key -out mkosi.crt \
        -days 730 -subj "/CN=mkosi of root/" -nodes -set_serial "0x40$(openssl rand -hex 19)"

bst *ARGS:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p "${HOME}/.cache/buildstream"
    podman run --rm \
        --privileged \
        --device /dev/fuse \
        --network=host \
        -v "{{justfile_directory()}}:/src:rw" \
        -v "${HOME}/.cache/buildstream:/root/.cache/buildstream:rw" \
        -w /src \
        "{{bst2_image}}" \
        bash -c 'if [ -t 1 ]; then bst --colors "$@"; else bst --no-colors "$@"; fi' -- ${BST_FLAGS:-} {{ARGS}}

clean:
    #!/usr/bin/env bash
    set -euo pipefail
    MKOSI="$(command -v mkosi || echo "$HOME/.local/bin/mkosi")"
    sudo "$MKOSI" clean
