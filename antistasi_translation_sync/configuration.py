"""
WiP.

Soon.
"""

# region [Imports]

import os

import sys

import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import (TYPE_CHECKING, TypeVar, TypeGuard, TypeAlias, Final, TypedDict, Generic, Union, Optional, ForwardRef, final, Callable,
                    no_type_check, no_type_check_decorator, overload, get_type_hints, cast, Protocol, runtime_checkable, NoReturn, NewType, Literal, AnyStr, IO, BinaryIO, TextIO, Any)
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from collections.abc import (AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, ByteString, Callable, Collection, Container, Coroutine, Generator,
                             Hashable, ItemsView, Iterable, Iterator, KeysView, Mapping, MappingView, MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized, ValuesView)
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, cache
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, wait, as_completed, ALL_COMPLETED, FIRST_EXCEPTION, FIRST_COMPLETED

from .errors import NoTokenFoundError

from configparser import ConfigParser

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    ...

# endregion [Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion [Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion [Constants]


class EmptyBehaviour(Enum):
    KEEP = auto()
    REMOVE = auto()
    ERROR = auto()
    WARN = auto()

    @classmethod
    def _missing_(cls, value: object) -> Any:
        try:
            normalized_value = value.strip().replace(" ", "_").replace("-", "_").upper()
            return cls.__members__[normalized_value]
        except (AttributeError, KeyError):
            pass
        return super()._missing_(value)


class _SubConfig(ABC):

    __slots__ = tuple()

    @property
    def section_name(self) -> str:
        raw_name = self.__class__.__name__.removesuffix("Config")
        name = ''.join(f"_{c}" if c.isupper() else c for c in raw_name).strip("_").casefold()
        return name

    def update_from_config(self, config: ConfigParser) -> None:
        ...


class ReportConfig(_SubConfig):

    def __init__(self) -> None:
        pass


class WebhookConfig(_SubConfig):

    def __init__(self) -> None:
        pass


class TolgeeConfig(_SubConfig):
    __slots__ = ("base_url",
                 "api_project_token_suffix")

    def __init__(self) -> None:
        self.base_url: str = None
        self.api_project_token_suffix: str = "TOLGEE_API_TOKEN"

    def get_tolgee_api_project_token(self, project_name: str) -> str:
        env_name = f"{project_name}_{self.api_project_token_suffix}".upper()
        try:
            return os.environ[env_name]
        except KeyError:
            raise NoTokenFoundError(f"No token found for project name {project_name!r} and token-sufffix {self.api_project_token_suffix!r}.")


class StringtableConfig(_SubConfig):
    __slots__ = ("empty_container_behaviour",
                 "empty_key_behaviour",
                 "indentation")

    def __init__(self) -> None:
        self.empty_container_behaviour: EmptyBehaviour = EmptyBehaviour.KEEP
        self.empty_key_behaviour: EmptyBehaviour = EmptyBehaviour.KEEP
        self.indentation: int = 2


class Config:

    def __init__(self) -> None:
        self.tolgee_config = TolgeeConfig()
        self.stringtable_config = StringtableConfig()
        self._old_working_dir: Path = None

        self.working_dir: Path = Path.cwd().resolve()
        self.targets: Union[list[Path], Callable] = []

    @property
    def sub_configs(self) -> tuple[_SubConfig]:
        return tuple(sub_config for _, sub_config in inspect.getmembers_static(self, predicate=lambda x: isinstance(x, _SubConfig)))

    def update_from_config(self, config: ConfigParser) -> None:
        ...

        for sub_config in self.sub_configs:
            sub_config._update_from_config(config=config)

    def resolve_targets(self) -> Self:
        self._old_working_dir = Path.cwd().resolve()
        os.chdir(self.working_dir)
        new_targets = []
        for target in self.targets:
            if isinstance(target, Path):
                new_targets.append(target.resolve())

            elif isinstance(target, str):
                if target == "AUTO_ALL":
                    new_targets.extend(self._auto_find_targets())

                else:
                    new_targets.append(Path(target).resolve())

        self.targets = new_targets
        return self

    def _auto_find_targets(self):
        for dirname, folderlist, filelist in os.walk(self.working_dir):
            for filename in filelist:

                if filename.casefold() == "stringtable.xml":
                    yield Path(dirname, filename).resolve()

    def __setattr__(self, __name: str, __value: Any) -> None:

        if "." in __name:
            name_parts = __name.split(".")

            obj = self
            for name_part in name_parts[:-1]:
                obj = getattr(obj, name_part)

            setattr(obj, name_parts[-1], __value)

        else:

            super().__setattr__(__name, __value)


DEFAULT_CONFIG: Config = Config()

# region [Main_Exec]

if __name__ == '__main__':
    # x = Config()
    # print([i.section_name for i in x.sub_configs])
    x = EmptyBehaviour("raise ErRoR")
    print(x)
# endregion [Main_Exec]
