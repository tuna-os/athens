#!/usr/bin/env python3
"""Install a locally loaded Athens image to a fresh file, then boot under UEFI.

Only a throwaway derivative gains the serial-console assertion service. Neither
this image nor its disk is a release artifact. No registry credentials required.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


GUEST = r"""#!/bin/bash
set -euo pipefail
exec >/dev/ttyS0 2>&1
finish() {
    rc=$?
    trap - EXIT
    journalctl -b -u lightdm --no-pager
    if [ "$rc" -eq 0 ]; then
        echo ATHENS_BOOT_SMOKE_OK
    else
        echo ATHENS_BOOT_SMOKE_FAILED
    fi
    systemctl poweroff --no-block
    exit "$rc"
}
trap finish EXIT
. /usr/lib/os-release
test "$ID" = athens
test "$NAME" = 'TunaOS Athens'
test -s /usr/share/backgrounds/TunaOS/Athens/athens-wallpaper.png
test -s /usr/share/icons/hicolor/scalable/apps/athens-logo.svg
test -s /usr/share/wayland-sessions/pantheon-wayland.desktop
test "$(systemctl get-default)" = graphical.target
for attempt in {1..120}; do
    if systemctl is-active --quiet lightdm.service; then break; fi
    sleep 1
done
systemctl is-active lightdm.service
# A service which immediately crashes and restarts is not a passing desktop.
restarts=$(systemctl show lightdm.service -p NRestarts --value)
sleep 20
systemctl is-active lightdm.service
test "$(systemctl show lightdm.service -p NRestarts --value)" = "$restarts"
bootc status --json
"""
UNIT = """[Unit]
Description=Disposable Athens boot qualification assertions
After=lightdm.service systemd-user-sessions.service
Wants=lightdm.service
[Service]
Type=simple
ExecStart=/usr/libexec/athens-boot-smoke
[Install]
WantedBy=multi-user.target
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Image already in rootful Podman storage")
    parser.add_argument("--output", type=Path, default=Path("bootc-smoke"))
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--firmware", type=Path, default=Path("/usr/share/OVMF/OVMF_CODE_4M.fd"))
    parser.add_argument("--variables", type=Path, default=Path("/usr/share/OVMF/OVMF_VARS_4M.fd"))
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error("run with sudo: bootc's loopback installation requires root")
    if os.uname().machine != "x86_64":
        parser.error("this UEFI smoke currently supports x86_64 only")
    for command in ("podman", "qemu-system-x86_64", "qemu-img"):
        if not shutil.which(command):
            parser.error(f"required command not installed: {command}")
    for firmware in (args.firmware, args.variables):
        if not firmware.is_file():
            parser.error(f"UEFI firmware not found: {firmware}")
    subprocess.run(["podman", "image", "exists", args.image], check=True)
    output = args.output.resolve()
    output.mkdir()  # Refuse to overwrite any previous evidence or disk.
    context = output / "context"
    context.mkdir()
    (context / "assertions").write_text(GUEST)
    (context / "smoke.service").write_text(UNIT)
    (context / "Containerfile").write_text(
        f"FROM {args.image}\n"
        "COPY assertions /usr/libexec/athens-boot-smoke\n"
        "COPY smoke.service /usr/lib/systemd/system/athens-boot-smoke.service\n"
        "RUN chmod 0755 /usr/libexec/athens-boot-smoke && "
        "systemctl enable athens-boot-smoke.service\n"
    )
    image = f"localhost/athens-boot-smoke:{os.getpid()}"
    try:
        with (output / "install.log").open("w") as log:
            subprocess.run(["podman", "build", "--pull=never", "-t", image, str(context)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run(["qemu-img", "create", "-f", "raw", str(output / "disk.raw"), "20G"],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run([
                "podman", "run", "--rm", "--privileged", "--pid=host", "--pull=never",
                "--security-opt", "label=disable", "-v", "/dev:/dev",
                "-v", "/var/lib/containers:/var/lib/containers",
                "-v", f"{output}:/evidence", image,
                "bootc", "install", "to-disk", "--via-loopback", "--generic-image",
                "--skip-fetch-check", "--filesystem=ext4", "--karg=console=ttyS0,115200n8",
                "/evidence/disk.raw",
            ], stdout=log, stderr=subprocess.STDOUT, check=True)
        shutil.copyfile(args.variables, output / "OVMF_VARS.fd")
        acceleration = "kvm" if os.access("/dev/kvm", os.R_OK | os.W_OK) else "tcg"
        with (output / "serial.log").open("w") as log:
            subprocess.run([
                "qemu-system-x86_64", "-machine", f"q35,accel={acceleration}",
                "-m", "4096", "-smp", "2", "-display", "none", "-serial", "stdio",
                "-monitor", "none", "-no-reboot", "-nic", "user,model=virtio-net-pci",
                "-device", "virtio-vga", "-drive",
                f"if=pflash,format=raw,readonly=on,file={args.firmware.resolve()}",
                "-drive", f"if=pflash,format=raw,file={output / 'OVMF_VARS.fd'}",
                "-drive", f"if=virtio,format=raw,file={output / 'disk.raw'}",
            ], stdout=log, stderr=subprocess.STDOUT, check=True, timeout=args.timeout)
        serial = (output / "serial.log").read_text(errors="replace")
        if "ATHENS_BOOT_SMOKE_OK" not in serial or "ATHENS_BOOT_SMOKE_FAILED" in serial:
            raise RuntimeError(f"guest assertions failed; inspect {output / 'serial.log'}")
        print(f"Athens installation and UEFI boot assertions passed; evidence: {output}")
    finally:
        subprocess.run(["podman", "image", "rm", image], check=False)


if __name__ == "__main__":
    try:
        main()
    except (subprocess.SubprocessError, OSError, RuntimeError) as error:
        print(f"Athens boot smoke failed: {error}", file=sys.stderr)
        sys.exit(1)
