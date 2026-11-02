"""Unit tests for the Hello World application (pytest)."""

import pytest

from hello.__main__ import main
from hello.calc import add
from hello.core import greet


def test_BasicAddition():
    """BasicAddition: the test function `add` sums two numbers."""
    assert add(2, 3) == 5


@pytest.mark.parametrize(("a", "b", "expected"), [(0, 0, 0), (-1, 1, 0), (2.5, 0.5, 3.0)])
def test_AdditionCases(a, b, expected):
    assert add(a, b) == expected


def test_Greeting():
    assert greet() == "Hello, World!"


def test_MainPrintsGreeting(capsys):
    assert main() == 0
    assert capsys.readouterr().out == "Hello, World!\n"
