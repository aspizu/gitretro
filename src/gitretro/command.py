import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .json_object import JSONObject

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class Command:
    _program: str
    _args: tuple[str, ...]

    def args(self, *args: str, if_: bool = True) -> Command:
        if not if_:
            return self
        return Command(self._program, self._args + args)

    def cmd(self, cmd: str) -> Command:
        return self.args(*shlex.split(cmd))

    def optv(self, name: str, value: str | None = None) -> Command:
        if value is None:
            return self
        return self.args(name, value)

    def opt(self, name: str, value: bool = True) -> Command:
        if value:
            return self.args(name)
        return self

    def __iter__(self) -> Iterator[str]:
        yield self._program
        yield from self._args

    @classmethod
    def from_which(cls, program: str) -> Command:
        program_ = shutil.which(program)
        if program_ is None:
            msg = f"Program '{program}' not found"
            raise RuntimeError(msg)
        return cls(program_, ())

    def output(self) -> str:
        return subprocess.check_output([*self], text=True).rstrip("\n")  # noqa: S603

    def json[T](self) -> JSONObject[T]:
        return JSONObject.parse(self.output())

    def run(self) -> int:
        p = subprocess.run([*self], check=True)  # noqa: S603
        return p.returncode
