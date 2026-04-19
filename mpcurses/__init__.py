
# Copyright (c) 2021 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from importlib import metadata as _metadata
import importlib
from os import getenv

__all__ = [
    'MPcurses'
]

def __getattr__(name):
    if name == 'MPcurses':
        from .mpcurses import MPcurses
        return MPcurses

    # If the requested attribute isn't one of the known top-level symbols,
    # try to lazily import a submodule (e.g. `thread_order.scheduler`) so
    # attribute lookups such as those used by mocking/patching succeed.
    try:
        return importlib.import_module(f"{__name__}.{name}")
    except Exception:
        raise AttributeError(name)

try:
    __version__ = _metadata.version(__name__)
except _metadata.PackageNotFoundError:
    __version__ = '1.1.0'

if getenv('DEV'):
    __version__ = f'{__version__}+dev'
