from __future__ import annotations

import os
import typing
from pathlib import Path

from ..resources import resources
from ._pathutil import (
    is_valid_module,
    path_to_module,
    scantree,
)

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["editable_redirect", "libdir_to_installed", "mapping_to_modules"]


def __dir__() -> list[str]:
    return __all__


def fstring_repr(d: dict[str, str]) -> str:
    items = []
    for k, v in d.items():
        items.append(f"{k!r}: f{v!r}")
    return "{" + ", ".join(items) + "}"


def editable_redirect(
    *,
    modules: dict[str, str],
    installed: dict[str, str],
    reload_dir: Path | None,
    rebuild: bool,
    verbose: bool,
    build_options: Sequence[str],
    install_options: Sequence[str],
    install_dir: str,
) -> str:
    """
    Prepare the contents of the _editable_redirect.py file.
    """

    editable_py = resources / "_editable_redirect.py"
    editable_txt: str = editable_py.read_text(encoding="utf-8")

    arguments = (
        os.fspath(reload_dir) if reload_dir else None,
        rebuild,
        verbose,
        build_options,
        install_options,
        install_dir,
    )
    arguments_str = fstring_repr(modules) + ", " + fstring_repr(installed) + ", " + ", ".join(repr(x) for x in arguments)
    editable_txt += f"\n\nroot_dir=os.getenv('CUDF_PYTHON_ROOT', '/home/coder/cudf/python/cudf')\ninstall({arguments_str})\n"
    return editable_txt


def mapping_to_modules(mapping: dict[str, str], libdir: Path) -> dict[str, str]:
    """
    Convert a mapping of files to modules to a mapping of modules to installed files.
    """
    return {
        path_to_module(Path(v).relative_to(libdir)): "{root_dir}/" + str(Path(k))
        for k, v in mapping.items()
        if is_valid_module(Path(v).relative_to(libdir))
    }


def libdir_to_installed(libdir: Path) -> dict[str, str]:
    """
    Convert a mapping of files to modules to a mapping of modules to installed files.
    """
    return {
        path_to_module(pth): str(pth)
        for v in scantree(libdir)
        if is_valid_module(pth := v.relative_to(libdir))
    }
