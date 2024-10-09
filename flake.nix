{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    { nixpkgs, flake-parts, ... }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = nixpkgs.lib.systems.flakeExposed;
      perSystem =
        { pkgs, ... }:
        {
          devShells.default = pkgs.mkShellNoCC {
            packages = [
              pkgs.nixVersions.latest
              (pkgs.python3.withPackages (p: with p; [jinja2]))
              (pkgs.ruby.withPackages (p: with p; [ solargraph ]))
            ];
          };
        };
    };
}
