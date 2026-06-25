"""Dizzy core library."""

try:
    # Written at build time by hatch-vcs from the git tag.
    from ._version import __version__
except ImportError:  # pragma: no cover - source checkout without a build
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _version

    try:
        __version__ = _version("dizzy")
    except PackageNotFoundError:
        __version__ = "0.0.0+unknown"
