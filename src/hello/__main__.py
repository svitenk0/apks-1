"""Entry point: `python -m hello` and the PyInstaller executable `hello`."""

import sys

from hello.core import greet


def main() -> int:
    """Print the greeting and return the process exit code."""
    print(greet())
    return 0


if __name__ == "__main__":
    sys.exit(main())
