#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import MutableMapping, Any, Callable
from types import MethodType
from inspect import signature, _empty


class MultiMethod:
    """The descriptor"""

    def __init__(self, name):
        self._name = name
        self.methods: dict[tuple[type, ...], Callable] = {}

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return MethodType(self, instance)

    def register(self, func) -> None:
        sig = signature(func)
        _types: tuple[type, ...] = tuple()
        for name, parm in sig.parameters.items():
            if name == "self":
                continue
            if parm.annotation is _empty:
                raise TypeError(f"{name} all parameters must be annotated")
            _types = _types + (parm.annotation,)
            if parm.default is not _empty:
                self.methods[_types] = func
        self.methods[_types] = func

    def __call__(self, *args, **kwds) -> Any:
        _types: tuple[type, ...] = tuple(type(a) for a in args[1:])
        return self.methods[_types](*args)


class MultiDict(dict):
    def __setitem__(self, key, val):
        if key not in self:
            super().__setitem__(key, val)
            return
        oval = self[key]
        if isinstance(oval, MultiMethod):
            mm = oval
            mm.register(val)
        else:
            mm = MultiMethod(key)
            mm.register(oval)
            mm.register(val)
        super().__setitem__(key, mm)


class MultiMeta(type):
    @classmethod
    def __prepare__(
        mcls, clsname: str, bases: tuple[type, ...], /, **kwds: Any
    ) -> MutableMapping[str, object]:
        return MultiDict()


class Visit(metaclass=MultiMeta):
    def add(self, x: int, y: int) -> int:
        print(f"add-int-int({x}, {y})")
        return x + y

    def add(self, x: str, y: str) -> str:  # noqa: F81
        print(f"add-str-str({x}, {y})")
        return x + y

    def add(self, x: float, y: float = 2.3) -> float:  # noqa: F81
        print(f"add-float-float({x}, {y})")
        return x + y


if __name__ == "__main__":
    v = Visit()
    v.add(1, 2)
    v.add("a", "b")
    v.add(2.3)
