{
  inputs = {
    nixpkgs = {
      #url = "github:nixos/nixpkgs?rev=6f1890f3e6cd5c0945dbbf35ae35868e2767dc43";
      url = "github:nixos/nixpkgs?rev=7881fbfd2e3ed1dfa315fca889b2cfd94be39337";
    };
    home-manager = {
      #url = "github:nix-community/home-manager?rev=e1aec543f5caf643ca0d94b6a633101942fd065f";
      url = "github:nix-community/home-manager?rev=2a4fd1cfd8ed5648583dadef86966a8231024221";
    };
    alexandria = {
      #url = "gitlab:alexandria/alexandria?host=gitlab.common-lisp.net&rev=154eee9951d7bd8e0aeeb4928aece30a99bf2c6a";
      url = "gitlab:alexandria/alexandria?host=gitlab.common-lisp.net&rev=8514d8e68ed0c733abf7f96f9e91b24912686dc4";
      flake = false;
    };
    nur-expressions = {
      #url = "gitlab:rycee/nur-expressions?rev=7122959edcf173a13b728291176b1c9799fd1b55";
      url = "gitlab:rycee/nur-expressions?rev=96b37d54815787864c79010f1d07a50f98fdbd99";
      flake = false;
    };
  };

  outputs = { nixpkgs, ... }: {
    packages.x86_64-linux = {
      nixpkgs = nixpkgs.legacyPackages.x86_64-linux.hello;
    };
  };
}
