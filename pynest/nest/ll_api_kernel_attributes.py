# -*- coding: utf-8 -*-
#
# ll_api_kernel_attributes.py
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
Kernel status access for the attributes of the ``nest`` module.
"""

import inspect

from .ll_api import spp, sps, sr, stack_checker


@stack_checker
def get_kernel_status():
    """Read the complete kernel status dictionary."""

    sr("GetKernelStatus")
    return spp()


@stack_checker
def set_kernel_status(params):
    """Write the entries of the dictionary `params` to the kernel status."""

    sps(params)
    sr("SetKernelStatus")


class KernelAttribute:
    """
    Descriptor that maps an attribute of the ``nest`` module onto an entry of the
    kernel status dictionary.

    Reading the attribute reads the kernel status, assigning to it writes the kernel
    status. The docstring assembled from the arguments below is what ``help()`` and
    the :ref:`sec_kernel_attributes` documentation page show, so it is written in
    reStructuredText.

    Parameters
    ----------
    typehint : str
        Type of the value, rendered as the ``:type:`` field of the docstring.
    description : str
        What the attribute means, as one reStructuredText paragraph. Indentation is
        stripped, so a triple-quoted string indented to match the surrounding code
        renders correctly. A trailing period is optional; one is always rendered.
    readonly : bool, optional
        Whether assigning to the attribute raises an `AttributeError`.
    default : optional
        Value of the attribute in a freshly reset kernel. Documented only; the
        kernel, not this descriptor, applies it.
    localonly : bool, optional
        Whether the value describes the local MPI rank rather than the whole
        simulation.
    """

    def __init__(self, typehint, description, readonly=False, default=None, localonly=False):
        self.typehint = typehint
        self.readonly = readonly
        self.localonly = localonly
        self.default = default
        self.__doc__ = self._build_docstring(description)

    def _build_docstring(self, description):
        summary = inspect.cleandoc(description).rstrip()
        if summary.endswith("."):
            summary = summary[:-1]
        if self.default is not None:
            summary += f", defaults to ``{self.default}``"
        scope = ", ".join(
            label
            for label, applies in (("**read only**", self.readonly), ("**local only**", self.localonly))
            if applies
        )
        return "\n\n".join(block for block in (summary + ".", scope, f":type: {self.typehint}") if block)

    def __set_name__(self, cls, name):
        self._name = name

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        status = get_kernel_status()
        # `kernel_status` exposes the status dictionary itself, not an entry of it.
        return status if self._name == "kernel_status" else status[self._name]

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError(f"`{self._name}` is a read only kernel attribute.")
        set_kernel_status({self._name: value})
