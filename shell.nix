with import <nixpkgs> { };

stdenv.mkDerivation {
  name = "drokpa";
  buildInputs = [
    python310
    python310Packages.python-magic
    poetry
    file # foir libmagic
  ];
  shellHook = ''
    poetry shell
  '';
  LD_LIBRARY_PATH = lib.makeLibraryPath [ pkgs.stdenv.cc.cc pkgs.file ];
  # env = {
  #   PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
  #     # Need for python-magic
  #     pkgs.file
  #   ];
  #   PYTHONHOME = "${pkgs.python310Full}";
  #   PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
  #   LANG = "en_US.UTF-8";
  #   STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
  #   PRYBAR_PYTHON_BIN = "${pkgs.replitPackages.prybar-python310}/bin/prybar-python310";
  # };
}
