# This expression is intended to be evaluated with `--json` for CI purposes.
{ releaseOnly ? false }:
let
  pkgs = import ../nixpkgs.nix {};
  release-tools = import ../support/nix/release-tools.nix { inherit pkgs; };
  devices =
    if releaseOnly then
      builtins.filter
        (device: (release-tools.evalFor device {}).config.device.inRelease)
        release-tools.allDevices
    else
      release-tools.allDevices;
in
  devices
