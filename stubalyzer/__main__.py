from .analyze import main

"""
This file allows stubalyzer to be executed as a module like this:
python -m stubalyzer --config mypy.ini /path/to/stubs
"""

if __name__ == "__main__":
    main()
