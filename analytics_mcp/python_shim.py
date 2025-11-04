"""Shim executable for environments lacking a ``python`` binary."""

import os
import shutil
import sys


def main() -> None:
    """Execute the user's command with the available ``python3`` interpreter.

    Some deployment targets (such as the Railway environment used for this
    project) only provide a ``python3`` executable.  Our release previously
    relied on a ``python`` binary being present, so invoking ``python`` during
    startup resulted in ``command not found`` errors.  We ship this shim so the
    package always exposes a ``python`` entry point that forwards arguments to
    the available ``python3`` interpreter.
    """

    python3 = shutil.which("python3")
    if python3 is None:
        raise SystemExit("python3 executable not found on PATH; unable to run 'python'.")

    os.execv(python3, [python3, *sys.argv[1:]])


if __name__ == "__main__":  # pragma: no cover - the module is used as a script.
    main()
