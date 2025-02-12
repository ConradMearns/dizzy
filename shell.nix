with import <nixpkgs> { };

stdenv.mkDerivation {
  name = "drokpa";
  buildInputs = [
    python310
    poetry
    rqlite
  ];
  shellHook = ''
    # poetry shell
  '';
  LD_LIBRARY_PATH = lib.makeLibraryPath [ pkgs.stdenv.cc.cc ];
}
