# Samsung Galaxy S20 FE (R8Q)

## Device-specific notes

This experimental target combines the pinned R8Q hardware-support fork with
Tow-Boot's menu implementation and logo. It retains the fork's EFI boot path,
bootstd, UFS support, and USB modes. It is excluded from Tow-Boot release
artifacts while hardware validation is outstanding.

Hold **Volume Down** during startup to enter the Tow-Boot menu, then use the
volume buttons to navigate and Power to select. This is not the eMMC/RGB-LED
phone UX used on other Tow-Boot phones. Display, button navigation, and OS
handoff still need device testing.

The manual **Build R8Q Tow-Boot image** workflow packages the result into
`tow-boot-r8q-boot.img`, using the pinned fork's Samsung inputs. Download the
`tow-boot-r8q-<commit SHA>` artifact for the intended revision, not an older
`r8q-boot-image` artifact, which may contain plain U-Boot. The workflow verifies
Tow-Boot features and checks that the final image contains that exact binary.
See [INSTALLING.md](INSTALLING.md) for build instructions and firmware
compatibility precautions.
