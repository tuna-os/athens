#!/usr/bin/env python3
"""Build an x86_64 Athens live ISO from a local rootful Podman image.

Uses the same systemd-boot + Debian-built dmsquash-live initramfs architecture
as TunaOS Tromsø. No registry publication or installer is implied.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading


def run(*command: str, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--output", type=Path, default=Path("athens-live"))
    parser.add_argument("--smoke", action="store_true", help="Boot ISO in QEMU and assert live Pantheon readiness; ISO shuts down after assertions")
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().machine != "x86_64":
        parser.error("run as root on x86_64")
    tools = ["podman", "mksquashfs", "mkfs.fat", "mmd", "mcopy", "xorriso"]
    if args.smoke:
        tools.append("qemu-system-x86_64")
    for tool in tools:
        if not shutil.which(tool):
            parser.error(f"required tool not found: {tool}")
    firmware = Path("/usr/share/OVMF/OVMF_CODE_4M.fd")
    variables = Path("/usr/share/OVMF/OVMF_VARS_4M.fd")
    if args.smoke and not (firmware.is_file() and variables.is_file()):
        parser.error("install the ovmf package for UEFI smoke")
    metadata = json.loads(run("podman", "image", "inspect", args.image, capture_output=True, text=True).stdout)[0]
    if metadata["Architecture"] != "amd64":
        parser.error("only x86_64 ISO assembly is qualified by this tool")
    # Pin the actual local image ID, so a mutable tag cannot drift during build.
    source = metadata["Id"]
    output = args.output.resolve()
    output.mkdir()  # Never overwrite an earlier ISO or its evidence.
    live = f"localhost/athens-live:{os.getpid()}"
    root = Path(__file__).resolve().parents[1]
    mounted = False
    try:
        with (output / "build.log").open("w") as log:
            run("podman", "build", "--layers", "--build-arg", f"BASE_IMAGE={source}",
                "--security-opt", "label=disable", "--cap-add", "SYS_ADMIN", "-t", live,
                str(root / "files/live"), stdout=log, stderr=subprocess.STDOUT)
            mount = Path(run("podman", "image", "mount", live, capture_output=True, text=True).stdout.strip())
            mounted = True
            kernels = [path for path in (mount / "usr/lib/modules").iterdir() if path.is_dir()]
            if len(kernels) != 1:
                raise RuntimeError(f"expected exactly one kernel, found {kernels}")
            kernel = kernels[0]
            with tempfile.TemporaryDirectory(prefix="assembly-", dir=output) as temporary:
                work = Path(temporary)
                iso_root = work / "iso"
                (iso_root / "EFI/BOOT").mkdir(parents=True)
                (iso_root / "LiveOS").mkdir()
                run("mksquashfs", str(mount), str(iso_root / "LiveOS/squashfs.img"),
                    "-noappend", "-comp", "zstd", "-Xcompression-level", "3", "-processors", "2",
                    "-wildcards", "-e", "proc/*", "sys/*", "dev/*", "run/*", "tmp/*", stdout=log, stderr=subprocess.STDOUT)
                boot = mount / "usr/lib/systemd/boot/efi/systemd-bootx64.efi"
                files = {"EFI/BOOT/BOOTX64.EFI": boot,
                         "images/pxeboot/vmlinuz": kernel / "vmlinuz",
                         "images/pxeboot/initrd.img": kernel / "initramfs-live.img"}
                for destination, source_file in files.items():
                    path = work / "esp" / destination
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source_file, path)
                loader = work / "esp/loader"
                (loader / "entries").mkdir(parents=True)
                (loader / "loader.conf").write_text("timeout 1\ndefault athens-live.conf\n")
                options = "root=live:CDLABEL=ATHENS_LIVE rd.live.image rd.live.overlay.overlayfs=1 console=tty0 console=ttyS0,115200n8"
                if args.smoke:
                    options += " athens.smoke=1"
                (loader / "entries/athens-live.conf").write_text(
                    "title TunaOS Athens Live (Experimental)\nlinux /images/pxeboot/vmlinuz\n"
                    f"initrd /images/pxeboot/initrd.img\noptions {options}\n")
                esp = iso_root / "EFI/efi.img"
                size = sum(path.stat().st_size for path in (work / "esp").rglob("*") if path.is_file())
                with esp.open("wb") as stream:
                    stream.truncate(max(64 * 1024**2, size + 40 * 1024**2))
                run("mkfs.fat", "-F", "32", str(esp), stdout=log, stderr=subprocess.STDOUT)
                run("mcopy", "-s", "-i", str(esp), str(work / "esp/EFI"), str(work / "esp/images"), str(loader), "::/", stdout=log, stderr=subprocess.STDOUT)
                shutil.copyfile(boot, iso_root / "EFI/BOOT/BOOTX64.EFI")
                iso = output / "athens-live.iso"
                iso.touch()
                run("xorriso", "-dev", f"stdio:{iso}", "-volid", "ATHENS_LIVE",
                    "-rockridge", "on", "-joliet", "on", "-map", str(iso_root), "/",
                    "-boot_image", "any", "platform_id=0xef", "-boot_image", "any", "efi_path=EFI/efi.img", "-commit",
                    stdout=log, stderr=subprocess.STDOUT)
        (output / "source.json").write_text(json.dumps({"source_image": args.image, "source_image_id": metadata["Id"],
            "architecture": "x86_64", "qualification_smoke_iso": args.smoke,
            "installer": False}, indent=2) + "\n")
        if args.smoke:
            shutil.copyfile(variables, output / "OVMF_VARS.fd")
            acceleration = "kvm" if os.access("/dev/kvm", os.R_OK | os.W_OK) else "tcg"
            ready = threading.Event()
            with (output / "serial.log").open("w") as log:
                process = subprocess.Popen([
                    "qemu-system-x86_64", "-machine", f"q35,accel={acceleration}", "-m", "4096", "-smp", "2",
                    "-display", "none", "-serial", "stdio", "-monitor", "none", "-no-reboot", "-device", "virtio-vga",
                    "-qmp", f"unix:{output / 'qmp.sock'},server=on,wait=off",
                    "-nic", "user,model=virtio-net-pci", "-drive", f"if=pflash,format=raw,readonly=on,file={firmware}",
                    "-drive", f"if=pflash,format=raw,file={output / 'OVMF_VARS.fd'}",
                    "-drive", f"if=none,id=live,format=raw,media=cdrom,readonly=on,file={iso}",
                    "-device", "virtio-scsi-pci,id=scsi", "-device", "scsi-cd,drive=live",
                ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                def collect_serial():
                    for line in process.stdout:
                        log.write(line)
                        log.flush()
                        if "ATHENS_LIVE_SCREENSHOT_READY" in line:
                            ready.set()
                    ready.set()  # Early QEMU exit must fail promptly, not wait 15m.

                reader = threading.Thread(target=collect_serial)
                reader.start()
                try:
                    if not ready.wait(900):
                        raise RuntimeError("live boot did not reach screenshot readiness within 900s")
                    if "ATHENS_LIVE_SCREENSHOT_READY" not in (output / "serial.log").read_text(errors="replace"):
                        raise RuntimeError("QEMU exited before the live desktop was ready")
                    with socket.socket(socket.AF_UNIX) as monitor:
                        monitor.settimeout(20)
                        monitor.connect(str(output / "qmp.sock"))
                        stream = monitor.makefile("rwb")
                        json.loads(stream.readline())  # QMP greeting.
                        for command in ({"execute": "qmp_capabilities"},
                                        {"execute": "screendump", "arguments": {
                                            "filename": str(output / "desktop.png"), "format": "png"}}):
                            stream.write(json.dumps(command).encode() + b"\n")
                            stream.flush()
                            while True:
                                response = json.loads(stream.readline())
                                if "error" in response:
                                    raise RuntimeError(f"QEMU screenshot failed: {response}")
                                if "return" in response:
                                    break
                    process.wait(timeout=60)
                    if process.returncode:
                        raise subprocess.CalledProcessError(process.returncode, process.args)
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                    reader.join()
            serial = (output / "serial.log").read_text(errors="replace")
            if "ATHENS_LIVE_SMOKE_OK" not in serial or "ATHENS_LIVE_SMOKE_FAILED" in serial:
                raise RuntimeError(f"live guest assertions failed; inspect {output / 'serial.log'}")
        print(f"Athens live ISO: {iso}; source identity and evidence: {output}")
    finally:
        if mounted:
            run("podman", "image", "umount", live)
        subprocess.run(["podman", "image", "rm", live], check=False)


if __name__ == "__main__":
    main()
