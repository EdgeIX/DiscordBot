#!/usr/bin/env python3
import inspect
import os

import rich

__all__ = ("print_error")

def print_error(error: str) -> None:
    """Prints a error with formatting
    Parameters
    ----------
    error : str
        The error message to display
    """
    # We get the 2nd item in the call stack to find where this function is called from
    frame = inspect.stack()[1]
    # We get the module of the caller
    module = inspect.getmodule(frame[0])
    if module is None:
        filename = "Unknown"
    else:
        # We get the file of the module
        filepath = module.__file__
        # We get the relative file path of the module
        filename = os.path.relpath(filepath)
    # We print the info with some color
    rich.print(f"[bold underline red]ERROR:[/] [blue]({filename})[/] : {error}")
