{ config, lib, pkgs, ... }:

let
  sourceRevision = "0c3c827df9272308930f798ca0c9d85b7fa3f8b7";
  featureTag = "tb-2023.07-007";
  towBootFeatures = pkgs.fetchFromGitHub {
    owner = "Tow-Boot";
    repo = "U-Boot";
    rev = featureTag;
    hash = config.Tow-Boot.knownHashes.Tow-Boot.${featureTag};
  };
in
{
  device = {
    manufacturer = "Samsung";
    name = "Galaxy S20 FE (R8Q)";
    identifier = "samsung-galaxyS20FER8q";
    supportLevel = "experimental";
    inRelease = false;
  };

  hardware.soc = "generic-aarch64";

  Tow-Boot = {
    uBootVersion = "2026.10";
    src = pkgs.fetchurl {
      name = "u-boot-r8q-${sourceRevision}.tar.gz";
      url = "https://codeload.github.com/ben443/u-boot-r8q/tar.gz/${sourceRevision}";
      hash = "sha256-mLQDRxrL1zlQwaSjnS02Nn62MvbEDo9vMXCkgLNAY6o=";
    };
    defconfig = "qcom_defconfig";
    patches = lib.mkForce [ ./tow-boot-integration.patch ];
    # Keep bootstd and the working EFI boot path instead of distro_bootcmd.
    config = [
      (helpers: with helpers; {
        DEFAULT_DEVICE_TREE = freeform ''"qcom/sm8250-samsung-r8q"'';
        OF_SEPARATE = yes;
        ENV_IS_NOWHERE = yes;
        BOOTSTD = lib.mkForce yes;
        BOOTSTD_DEFAULTS = lib.mkForce yes;
        # The fork supplies bootcmd through its text environment, not Kconfig.
        BOOTCOMMAND = lib.mkForce unset;
        AUTOBOOT_PROMPT = lib.mkForce unset;
        CMD_BOOTFLOW = yes;
        PDCURSES_PREFER_VIDCONSOLE = yes;
      })
    ];
    builder = {
      environmentFile = "board/qualcomm/qcom-phone.env";
      postPatch = ''
        cp -r ${towBootFeatures}/cmd/tow-boot cmd/tow-boot
        cp -r ${towBootFeatures}/lib/PDCursesMod lib/PDCursesMod
        chmod -R u+w cmd/tow-boot lib/PDCursesMod
        patch -p1 < ${./tow-boot-menu-compat.patch}
      '';
      nativeBuildInputs = [ pkgs.buildPackages.xxd ];
      configFragments = [
        "board/qualcomm/qcom-phone.config"
        "configs/samsung-sm8250.config"
        "configs/samsung-r8q.config"
      ];
      installPhase = ''
        make $makeFlags "''${makeFlagsArray[@]}" dtbs
        mkdir -p "$out/r8q-build/dts/upstream/src/arm64/qcom"
        cp -v u-boot.bin "$out/binaries/Tow-Boot.$variant.bin"
        cp -v u-boot.dtb "$out/binaries/Tow-Boot.$variant.control.dtb"
        cp -v u-boot.bin "$out/r8q-build/u-boot.bin"
        cp -v u-boot-nodtb.bin "$out/r8q-build/u-boot-nodtb.bin"
        cp -v u-boot.dtb "$out/r8q-build/u-boot.dtb"
        cp -v dts/upstream/src/arm64/qcom/sm8250-samsung-r8q.dtb \
          "$out/r8q-build/dts/upstream/src/arm64/qcom/sm8250-samsung-r8q.dtb"
      '';
    };
  };

  build.default = lib.mkForce config.Tow-Boot.outputs.firmware;

  documentation.sections.installationInstructions =
    builtins.readFile ./INSTALLING.md;
}
