from os import path

# Always prefer setuptools over distutils
from setuptools import setup

VERSION = "0.5.0"
# This is the name of the GitHub repo and the package name on pypi
PACKAGE_NAME = "stubalyzer"


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    name=PACKAGE_NAME,
    version=VERSION,
    description=(
        "Analysis tool comparing hand written stubs to stubgen-generated ones, "
        "reporting inconsistencies"
    ),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url=f"https://github.com/kialo/{PACKAGE_NAME}",
    author="Kialo GmbH",
    author_email="open-source@kialo.com",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Typing :: Typed",
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords="mypy analysis stubgen stubs",
    packages=["stubalyzer"],
    python_requires=">=3.6",
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=["mypy", "schema"],
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={
        "dev": [
            "black",
            "bump2version",
            "flake8-rst-docstrings",
            "flake8",
            "ipython",
            "isort",
            "lxml",
            "pip-tools",
            "pytest",
        ]
    },
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    entry_points={
        "console_scripts": ["stubalyzer=stubalyzer.analyze:main"]
    },  # Optional
    # List additional URLs that are relevant to your project as a dict.
    project_urls={
        "Bug Reports": f"https://github.com/kialo/{PACKAGE_NAME}/issues",
        "Source": f"https://github.com/kialo/{PACKAGE_NAME}",
    },
    # For mypy to find types
    zip_safe=False,
    package_data={"stubalyzer": ["py.typed"]},
)
