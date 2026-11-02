## Build outputs

### Tow-Boot features

The experimental build combines the pinned R8Q hardware-support fork with
Tow-Boot's menu implementation from `tb-2023.07-007` and the Tow-Boot logo.
It retains the fork's EFI boot manager, bootstd, UFS support, Samsung device
trees, USB serial console, USB mass storage, and fastboot. It does not use the
legacy `distro_bootcmd` or the eMMC/RGB-LED phone UX intended for other phones.

Hold **Volume Down** during startup to enter the Tow-Boot menu. Use the volume
buttons to navigate and Power to select. After failed automatic EFI boot,
acknowledge the pause prompt to open the menu. It offers EFI boot, a boot-device
scan, USB modes, the firmware console, reboot, and shutdown. A keyboard console
can enter the menu with Escape during the boot countdown.

The previously built plain U-Boot image has been reported to boot on hardware;
that does not establish that this Tow-Boot port works on hardware. Its display,
menu navigation, and OS handoff still need device testing.

### GitHub Actions

After this change is pushed to the repository's default branch, open **Actions >
Build R8Q boot image > Run workflow** and select the branch to build. Download
the `r8q-boot-image` artifact from the completed run and extract
`u-boot-r8q-boot.img`. It also includes the matching U-Boot binary, device trees,
configuration, build information, and `SHA256SUMS`.
The filename remains `u-boot-r8q-boot.img` for packaging compatibility; the
workflow checks the configuration and payload for Tow-Boot features before
packaging, rather than relying on its filename or banner.

The workflow builds with Nix, then runs the pinned fork's packaging tests and
boot image validation. The image uses the Samsung header and stock DTB section
committed in that fork. These are not automatically matched to your installed
firmware. A successful build does not verify booting on your phone. Confirm
compatibility with your exact model and firmware, back up your working boot
image, and ensure you can restore it before testing. No flashing is automated.

### Local Nix build

```
nix-build -A samsung-galaxyS20FER8q -o result-r8q
archive=$(nix-build -A samsung-galaxyS20FER8q.config.Tow-Boot.src --no-out-link)
mkdir r8q-source
tar -xf "$archive" -C r8q-source --strip-components=1
bash r8q-source/.github/scripts/test-r8q-package.sh
python3 .github/scripts/check-r8q-tow-boot.py \
  result-r8q/config/noenv.config result-r8q/r8q-build/u-boot.bin
bash r8q-source/.github/scripts/r8q-package.sh \
  "$PWD/result-r8q/r8q-build" "$PWD/artifacts/r8q"
```

In addition to Nix, packaging requires Bash, Python 3, and `fdtget`/`dtc`
(the `device-tree-compiler` package on Debian/Ubuntu). The committed `magiskboot`
tool requires an x86-64 Linux host.

The build produces Tow-Boot with its control device tree appended, the control
device tree separately, and the Linux device tree for the R8Q. These unmodified
build outputs are under `r8q-build/`. The Nix firmware output alone does not
produce a Tow-Boot installer image or an Android `boot.img`; the packaging
command above creates `artifacts/r8q/u-boot-r8q-boot.img`.

Do not flash the raw U-Boot binary directly. The Galaxy S20 FE boot image needs
the stock Samsung DTB section and header, and the correct packaging procedure
depends on the exact device firmware. Use the packaging instructions and
scripts in the [R8Q U-Boot source repository](https://github.com/ben443/u-boot-r8q)
with the matching stock boot image. Verify the resulting image and recovery
procedure for your exact model before flashing.
