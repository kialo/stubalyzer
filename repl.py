"""
Runs analyze.py and gives the 'result' to play around with in a REPL.
"""

from IPython import start_ipython
from traitlets.config import Config

config = Config()
config.InteractiveShellApp.exec_lines = [
    f"%run analyze.py",
    "print('The result is in the variable `graph` - have fun')",
]

start_ipython(config=config)
