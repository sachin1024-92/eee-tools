"""Command line: ``python -m eeetools <module> <function> key=value ...``"""

from __future__ import annotations

import inspect
import math
import sys

from . import drives, hv, power, signals

MODULES = {"hv": hv, "signals": signals, "power": power, "drives": drives}


def _functions(module) -> dict:
    return {
        name: fn
        for name, fn in inspect.getmembers(module, inspect.isfunction)
        if fn.__module__ == module.__name__ and not name.startswith("_")
    }


def _parse(key: str, value: str):
    """Arguments are numbers only. Nothing typed on the command line is ever evaluated."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        number = float(value)
    except ValueError:
        raise ValueError(f"{key} must be a number, got {value!r}") from None
    if not math.isfinite(number):
        raise ValueError(f"{key} must be a finite number, got {value!r}")
    return number


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help") or args[0] not in MODULES:
        print("usage: python -m eeetools <module> [function key=value ...]\n")
        for name, module in MODULES.items():
            print(f"{name}: {(module.__doc__ or '').strip().splitlines()[0]}")
        return 0 if args and args[0] in ("-h", "--help") else (1 if args else 0)
    functions = _functions(MODULES[args[0]])
    if len(args) == 1 or args[1] not in functions:
        for name, fn in functions.items():
            print(f"{name}{inspect.signature(fn)}")
        return 0 if len(args) == 1 else 1
    try:
        for item in args[2:]:
            if "=" not in item:
                raise ValueError(f"expected key=value, got {item!r}")
        kwargs = dict(item.split("=", 1) for item in args[2:])
        result = functions[args[1]](**{k: _parse(k, v) for k, v in kwargs.items()})
    except (TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"{key} = {value:.6g}")
    elif isinstance(result, tuple):
        print(", ".join(f"{v:.6g}" for v in result))
    else:
        print(f"{result:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
