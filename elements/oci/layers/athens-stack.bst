kind: stack
description: Athens Pantheon desktop layered on the GNOME OS runtime

depends:
  # Pantheon desktop and shared desktop applications, without the disk image's
  # generic base-system stack (GNOME OS provides the base runtime).
  - stacks/pantheon.bst
  # Athens multimedia additions.
  - stacks/codecs.bst
  - branding/athens.bst
  # GNOME OS provides the bootc-compatible base runtime.
  - gnome-build-meta.bst:oci/gnomeos/stack.bst
