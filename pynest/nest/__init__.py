# -*- coding: utf-8 -*-
#
# __init__.py
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

r"""PyNEST - Python interface for the NEST Simulator

* ``nest.helpdesk()`` opens the NEST documentation in your browser.

* ``nest.__version__`` displays the NEST version.

* ``nest.node_models`` shows all available neuron and device models.

* ``nest.synapse_models`` shows all available synapse models.

* To get details on the model equations and parameters,
  please check out our model documentation at https://nest-simulator.readthedocs.io/en/stable/models/index.html.

* To get help on functions in the ``nest`` package, use Python's
  ``help()`` function or IPython's ``?``, e.g.
     - ``help(nest.Create)``
     - ``nest.Connect?``

For more information visit https://www.nest-simulator.org.
"""

# `nest` is more than a namespace: kernel attributes such as `nest.resolution` read
# from and write to the running kernel. That requires descriptors, and descriptors
# only fire when they are found on an object's *type*, so at the bottom of this file
# the module object is given the `NestModule` type defined below (PEP 562). Retyping
# the module object the interpreter already created -- rather than replacing it --
# keeps `import nest` pointing at one and the same object everywhere, including in
# the compiled `pynestkernel` extension and in the `hl_api` modules imported below,
# which run while this file is still executing.
#
# The type is also where the submodules live, as `_LazySubmodule` descriptors, so that
# `import nest` only costs the kernel plus the `hl_api` API surface.
#
# pylint: disable=wildcard-import, unused-wildcard-import, no-name-in-module, invalid-name

import sys
import types

from . import ll_api as _ll_api  # noqa: F401  (importing `ll_api` starts the kernel)
from .lib.hl_api_connections import *  # noqa: F401,F403
from .lib.hl_api_exceptions import *  # noqa: F401,F403
from .lib.hl_api_info import *  # noqa: F401,F403
from .lib.hl_api_models import *  # noqa: F401,F403
from .lib.hl_api_nodes import *  # noqa: F401,F403
from .lib.hl_api_parallel_computing import *  # noqa: F401,F403
from .lib.hl_api_simulation import *  # noqa: F401,F403
from .lib.hl_api_sonata import *  # noqa: F401,F403
from .lib.hl_api_spatial import *  # noqa: F401,F403
from .lib.hl_api_types import *  # noqa: F401,F403
from .ll_api import set_communicator  # noqa: F401
from .ll_api_kernel_attributes import KernelAttribute

try:
    # Bound under a private name so that it stays out of the `nest` API.
    import versionchecker as _versionchecker  # noqa: F401
except ImportError:
    pass


class _LazySubmodule:
    """
    Descriptor that imports a submodule on first attribute access and then replaces
    itself on the class with the imported module. Keeps ``import nest`` from paying
    for submodules the script never touches, and keeps submodules with optional
    third-party dependencies importable only by the users who have those installed.

    The submodule is named after the attribute unless `module_name` says otherwise.
    """

    def __init__(self, module_name=None):
        self._module_name = module_name

    def __set_name__(self, cls, name):
        self._name = name
        if self._module_name is None:
            self._module_name = name

    def __get__(self, instance, cls):
        # Imported here to keep `importlib` out of the `nest` namespace.
        import importlib

        module = importlib.import_module("." + self._module_name, __name__)
        setattr(cls, self._name, module)
        return module


class NestModule(types.ModuleType):
    """
    Type of the ``nest`` root module.

    The kernel attributes below are descriptors: reading ``nest.<attribute>`` reads the
    status of the running NEST kernel and assigning to it writes that status.
    Descriptors are only honoured when they live on a type, which is why the ``nest``
    module object is given this type rather than plain ``ModuleType``.
    """

    # Every submodule reachable as `nest.<name>` is resolved on attribute access.
    kernel = _LazySubmodule("pynestkernel")
    ll_api = _LazySubmodule()
    logic = _LazySubmodule()
    math = _LazySubmodule()
    random = _LazySubmodule()
    raster_plot = _LazySubmodule()
    server = _LazySubmodule()
    spatial = _LazySubmodule()
    spatial_distributions = _LazySubmodule()
    visualization = _LazySubmodule()
    voltage_trace = _LazySubmodule()

    def set(self, **kwargs):
        "Forward kernel attribute setting to `SetKernelStatus()`."
        return self.SetKernelStatus(kwargs)

    def get(self, *args):
        "Forward kernel attribute getting to `GetKernelStatus()`."
        if not args:
            return self.GetKernelStatus()
        if len(args) == 1:
            return self.GetKernelStatus(args[0])
        return self.GetKernelStatus(args)

    def __dir__(self):
        return list(set(vars(self).keys()) | set(self.__all__))

    def __setattr__(self, attr, value):
        """
        Route assignment to the descriptor of the same name on `NestModule`, so that
        `nest.resolution = 0.1` reaches the kernel instead of shadowing the descriptor
        with an entry in the module dictionary. Names without such a descriptor cannot
        be assigned; the module namespace is a curated API, not a scratch pad. Use
        `nest.userdict` to attach data of your own.
        """
        # Imported here to keep `types` out of the `nest` namespace.
        import types

        if isinstance(value, types.ModuleType):
            # The import machinery attaches submodules to their parent package.
            self.__dict__[attr] = value
            return

        descriptor = getattr(type(self), attr, None)
        if descriptor is None or not hasattr(descriptor, "__set__"):
            raise AttributeError(f"Cannot set attribute '{attr}' on module 'nest'")
        descriptor.__set__(self, value)

    # Define the kernel attributes.
    #
    # FORMATTING NOTES:
    # * The description is dedented and a `.` is appended, so write it as a normal
    #   sentence and indent continuation lines to match the surrounding code.
    # * Strings containing a colon render incorrectly.

    kernel_status = KernelAttribute("dict", "Get the complete kernel status", readonly=True)
    resolution = KernelAttribute("float", "The resolution of the simulation (in ms)", default=0.1)
    biological_time = KernelAttribute("float", "The current simulation time (in ms)")
    to_do = KernelAttribute("int", "The number of steps yet to be simulated", readonly=True)
    max_delay = KernelAttribute("float", "The maximum delay in the network", default=0.1)
    min_delay = KernelAttribute("float", "The minimum delay in the network", default=0.1)
    ms_per_tic = KernelAttribute(
        "float",
        "The number of milliseconds per tic. Calculated by ms_per_tic = 1 / tics_per_ms",
        readonly=True,
    )
    tics_per_ms = KernelAttribute(
        "float",
        """
        The number of tics per millisecond. Change of tics_per_ms requires simultaneous
        specification of resolution
        """,
        default=1000.0,
    )
    tics_per_step = KernelAttribute(
        "int",
        "The number of tics per simulation time step. Calculated as tics_per_step = resolution * tics_per_ms",
        readonly=True,
    )
    T_max = KernelAttribute("float", "The largest representable time value", readonly=True)
    T_min = KernelAttribute("float", "The smallest representable time value", readonly=True)
    rng_types = KernelAttribute(
        "list[str]",
        "List of available random number generator types",
        readonly=True,
    )
    rng_type = KernelAttribute(
        "str",
        "Name of random number generator type used by NEST",
        default="mt19937_64",
    )
    rng_seed = KernelAttribute(
        "int",
        r"Seed value used as base for seeding NEST random number generators (:math:`1 \leq s\leq 2^{32}-1`)",
        default=143202461,
    )
    total_num_virtual_procs = KernelAttribute("int", "The total number of virtual processes", default=1)
    local_num_threads = KernelAttribute("int", "The local number of threads", default=1)
    num_processes = KernelAttribute("int", "The number of MPI processes", readonly=True)
    off_grid_spiking = KernelAttribute(
        "bool",
        "Whether to transmit precise spike times in MPI communication",
        readonly=True,
    )
    adaptive_target_buffers = KernelAttribute(
        "bool",
        "Whether MPI buffers for communication of connections resize on the fly",
        default=True,
    )
    send_buffer_size_secondary_events = KernelAttribute(
        "int",
        """
        Size of MPI send buffers for communicating secondary events (in bytes, per MPI
        rank, for developers)
        """,
        readonly=True,
    )
    recv_buffer_size_secondary_events = KernelAttribute(
        "int",
        """
        Size of MPI recv buffers for communicating secondary events (in bytes, per MPI
        rank, for developers)
        """,
        readonly=True,
    )
    buffer_size_spike_data = KernelAttribute(
        "int",
        "Total size of MPI buffer for communication of spikes",
        default=2,
    )
    buffer_size_target_data = KernelAttribute(
        "int",
        "Total size of MPI buffer for communication of connections",
        default=2,
    )
    growth_factor_buffer_target_data = KernelAttribute(
        "float",
        """
        If MPI buffers for communication of connections resize on the fly, grow them by
        this factor each round
        """,
        default=1.5,
    )
    max_buffer_size_target_data = KernelAttribute(
        "int",
        "Maximal size of MPI buffers for communication of connections",
        default=16777216,
    )
    spike_buffer_grow_extra = KernelAttribute(
        "float",
        """
        When spike exchange buffer is expanded, resize it to
        `(1 + spike_buffer_grow_extra) * required_buffer_size`
        """,
        default=0.5,
    )
    spike_buffer_shrink_limit = KernelAttribute(
        "float",
        """
        If the largest number of spikes sent from any rank to any rank is less than
        `spike_buffer_shrink_limit * buffer_size`, then reduce buffer size.
        `spike_buffer_shrink_limit == 0` means that buffers never shrink.
        See ``spike_buffer_shrink_spare`` for how the new buffer size is determined
        """,
        default=0.2,
    )
    spike_buffer_shrink_spare = KernelAttribute(
        "float",
        """
        When the buffer shrinks, set the new size to
        `(1 + spike_buffer_shrink_spare) * required_buffer_size`.
        See `spike_buffer_shrink_limit` for when buffers shrink
        """,
        default=0.1,
    )
    spike_buffer_resize_log = KernelAttribute(
        "dict",
        """
        Log of spike buffer resizing as a dictionary. It contains the `times` of the
        resizings (simulation clock in steps, always multiple of ``min_delay``),
        ``global_max_spikes_sent``, that is, the observed spike number that triggered
        the resize, and the ``new_buffer_size``. Sizes for the buffer section sent from
        one rank to another rank
        """,
        readonly=True,
    )

    use_wfr = KernelAttribute("bool", "Whether to use waveform relaxation method", default=True)
    wfr_comm_interval = KernelAttribute(
        "float",
        "Desired waveform relaxation communication interval",
        default=1.0,
    )
    wfr_tol = KernelAttribute(
        "float",
        "Convergence tolerance of waveform relaxation method",
        default=0.0001,
    )
    wfr_max_iterations = KernelAttribute(
        "int",
        "Maximal number of iterations used for waveform relaxation",
        default=15,
    )
    wfr_interpolation_order = KernelAttribute(
        "int", "Interpolation order of polynomial used in wfr iterations", default=3
    )
    max_num_syn_models = KernelAttribute("int", "Maximal number of synapse models supported", readonly=True)
    structural_plasticity_synapses = KernelAttribute(
        "dict",
        """
        Defines all synapses which are plastic for the structural plasticity algorithm.
        Each entry in the dictionary is composed of a synapse model, the presynaptic
        element and the postsynaptic element
        """,
    )
    structural_plasticity_update_interval = KernelAttribute(
        "int",
        """
        Defines the time interval in ms at which the structural plasticity manager will
        make changes in the structure of the network ( creation and deletion of plastic
        synapses)
        """,
        default=10000,
    )
    growth_curves = KernelAttribute(
        "list[str]",
        "The list of the available structural plasticity growth curves",
        readonly=True,
    )
    use_compressed_spikes = KernelAttribute(
        "bool",
        """
        Whether to use spike compression; if a neuron has targets on multiple threads of
        a process, this switch makes sure that only a single packet is sent to the
        process instead of one packet per target thread; it implies that connections are
        sorted by source.
        """,
        default=True,
    )
    data_path = KernelAttribute(
        "str",
        "A path, where all data is written to, defaults to current directory",
    )
    data_prefix = KernelAttribute("str", "A common prefix for all data files")
    overwrite_files = KernelAttribute("bool", "Whether to overwrite existing data files", default=False)
    print_time = KernelAttribute(
        "bool",
        "Whether to print progress information during the simulation",
        default=False,
    )
    network_size = KernelAttribute("int", "The number of nodes in the network", readonly=True)
    num_connections = KernelAttribute(
        "int",
        "The number of connections in the network",
        readonly=True,
        localonly=True,
    )
    connection_rules = KernelAttribute(
        "list[str]",
        "The list of available connection rules",
        readonly=True,
    )
    node_models = KernelAttribute(
        "list[str]",
        "The list of the available node (i.e., neuron or device) models",
        readonly=True,
    )
    synapse_models = KernelAttribute(
        "list[str]",
        "The list of the available synapse models",
        readonly=True,
    )
    local_spike_counter = KernelAttribute(
        "int",
        """
        Number of spikes fired by neurons on a given MPI rank during the most recent
        call to :py:func:`.Simulate`. Only spikes from "normal" neurons are counted, not
        spikes generated by devices such as ``poisson_generator``. Resets on each call
        to ``Simulate`` or ``Run``.
        """,
        readonly=True,
    )
    recording_backends = KernelAttribute(
        "list[str]",
        "List of available backends for recording devices",
        readonly=True,
    )
    stimulation_backends = KernelAttribute(
        "list[str]",
        "List of available backends for stimulation devices",
        readonly=True,
    )
    dict_miss_is_error = KernelAttribute(
        "bool",
        "Whether missed dictionary entries are treated as errors",
        default=True,
    )
    keep_source_table = KernelAttribute(
        "bool",
        "Whether to keep source table after connection setup is complete",
        default=True,
    )
    min_update_time = KernelAttribute(
        "float",
        "Shortest wall-clock time measured so far for a full update step [seconds]",
        readonly=True,
    )
    max_update_time = KernelAttribute(
        "float",
        "Longest wall-clock time measured so far for a full update step [seconds]",
        readonly=True,
    )
    update_time_limit = KernelAttribute(
        "float",
        """
        Maximum wall-clock time for one full update step [seconds]. This can be used to
        terminate simulations that slow down significantly. Simulations may still get
        stuck if the slowdown occurs within a single update step
        """,
        default=float("+inf"),
    )
    eprop_update_interval = KernelAttribute(
        "float",
        "Task-specific update interval of the e-prop plasticity mechanism [ms].",
        default=1000.0,
    )
    eprop_learning_window = KernelAttribute(
        "float",
        "Task-specific learning window of the e-prop plasticity mechanism [ms].",
        default=1000.0,
    )
    eprop_reset_neurons_on_update = KernelAttribute(
        "bool",
        "If True, reset dynamic variables of e-prop neurons upon e-prop update.",
        default=True,
    )
    # Kernel attribute indices, used for fast lookup in `lib/hl_api_simulation.py`
    _kernel_attr_names = frozenset(k for k, v in vars().items() if isinstance(v, KernelAttribute))
    _readonly_kernel_attrs = frozenset(k for k, v in vars().items() if isinstance(v, KernelAttribute) and v.readonly)

    userdict = {}
    """
    The variable userdict allows users to store custom data with the NEST kernel.

    Example: nest.userdict["nodes"] = [1,2,3,4]
    """


__version__ = _ll_api.sli_func("statusdict /version get")

# Retype the module object, putting the kernel attribute descriptors in force.
sys.modules[__name__].__class__ = NestModule

# What is left in this file's namespace is the `nest` namespace, so drop the scaffolding
# of this file, along with the packages that the import machinery attached to `nest` as
# a side effect of the imports above but that are not part of the API.
del sys, types, KernelAttribute, _LazySubmodule, _ll_api
del lib, ll_api_kernel_attributes, pynestkernel  # noqa: F821

# The API is what this file exports, plus what `NestModule` adds: the kernel attributes,
# `get`/`set` and the lazily imported submodules. `NestModule` itself is an
# implementation detail that is only exposed for the documentation build.
__all__ = sorted(
    (
        {name for name in globals() if not name.startswith("_")}
        | {name for name in dir(NestModule) if not name.startswith("_")}
    )
    - {"NestModule"}
)
