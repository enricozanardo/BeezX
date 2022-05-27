let
    name = "enrix";
    src= ./.;
    version = "0.1";
    pkgs = import <nixpkgs> {allowUnfree=true;};
in
with pkgs;
stdenv.mkDerivation{
    name = "${name}";
    inherit src;
    buildInputs = [
        git
        python3
        python39Packages.pip
        python39Packages.pip-tools
        python39Packages.pytest
        python39Packages.virtualenv
    ];
}
