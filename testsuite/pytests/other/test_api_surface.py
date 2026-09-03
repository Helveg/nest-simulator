# -*- coding: utf-8 -*-
#
# test_api_surface.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""
Tests for the namespace of the ``nest`` root module.

``nest`` resolves its namespace lazily: submodules and the public API of the
``lib.hl_api_*`` modules are imported on first access by ``NestModule.__getattr__``,
which discovers both from the package directory. Static analysers cannot follow that,
so ``nest/__init__.py`` spells the same namespace out in an ``if TYPE_CHECKING:``
block. Nothing reads that block at runtime, which is exactly why it needs a test.
"""

import ast
import importlib.util
import pathlib

import nest
import pytest


def _type_checking_imports():
    """Return the submodules and ``lib`` modules imported in the TYPE_CHECKING block."""

    tree = ast.parse(pathlib.Path(nest.__file__).read_text())
    guard = next(
        node for node in tree.body if isinstance(node, ast.If) and ast.unparse(node.test).endswith("TYPE_CHECKING")
    )

    submodules, api_modules = set(), set()
    for node in ast.walk(guard):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module is None:  # `from . import a, b, c`
            submodules |= {alias.name for alias in node.names}
        elif node.module.startswith("lib."):  # `from .lib.hl_api_x import *`
            api_modules.add(node.module.split(".", 1)[1])

    return submodules, api_modules


def test_type_checking_block_lists_every_submodule():
    """The TYPE_CHECKING block must cover the submodules the runtime exposes."""

    declared, _ = _type_checking_imports()
    assert declared == set(nest._submodules())


def test_type_checking_block_lists_every_api_module():
    """The TYPE_CHECKING block must cover the `hl_api` modules the runtime searches."""

    _, declared = _type_checking_imports()
    assert declared == {module.__name__.rsplit(".", 1)[1] for module in nest._api_modules()}


def test_api_module_exports_are_disjoint():
    """
    `NestModule.__getattr__` returns the first `hl_api` module that exports a name, so
    two modules exporting the same name would make the lookup order significant.
    """

    seen = {}
    for module in nest._api_modules():
        for name in module.__all__:
            assert name not in seen, f"'{name}' is exported by both {seen[name]} and {module.__name__}"
            seen[name] = module.__name__


def test_all_covers_the_lazily_resolved_namespace():
    """Every name in ``nest.__all__`` must actually resolve on the module."""

    for name in nest.__all__:
        if name in nest._kernel_attr_names:
            # Reading one of these queries the kernel; only check that the descriptor
            # made it onto the module type.
            assert hasattr(type(nest), name), f"'{name}' has no kernel attribute descriptor"
        elif name in nest._submodules():
            # Importing these can need optional third-party packages, so only check
            # that the submodule the name promises is there.
            assert importlib.util.find_spec(f"nest.{name}") is not None, f"'nest.{name}' does not exist"
        else:
            assert hasattr(nest, name), f"'{name}' is advertised in __all__ but does not resolve"


def test_unknown_attribute_raises():
    with pytest.raises(AttributeError):
        nest.thisAttributeDoesNotExist
