# Gamspreprocessor

`gamspreprocessor` (or short: `preprocess`) provides a set of tools useful in preparation
of GAMS object folders (which are required for packaging).

## Installation

gamspreprocessor is available on pypi.org and can be installed via pip:

```
pip install gamspreprocessor
```

A propably better way to install this tool is to use the `uv tool` command, which requires,
that you install `uv` first (see https://docs.astral.sh/uv/getting-started/installation/).

Use this command to install `gamspreprocessor` on your computer:

```bash
uv tool install gamspreprocessor
```

Afterwards, the `gamspreprocessor` command should be availabe on your machine.

If you do not want to install it permanently, you can use the `uvx` command provided by
`uv`:

```
uvx gamspreprocessor --help
```

## Usage

The package provides a single command `gamsproprocessor` (or short: `preprocess`) with a set of subcommands:

  - `csv`             Helpers for managing GAMS object CSV files.
  - `gams3export`     Export one or more objects from a GAMS 3 repository to...
  - `multitransform`  Helpers for transforming multiple files at once.
  - `project`         Helpers for managing GAMS projects.
  - `splitproject`    Helpers for creating object directories.
  - `transform`       Helpers for transforming GAMS files.
  - `validate`        Validate object folder(s).


## Documentation

Use `preprocess --help` for more information or consult the documentation:
https://dhgraz.github.io/gamspreprocessor/


## Contributing

The Github repository is ment to be a read only mirror of the work repository
hosted on our institutional private GitLab server. You can use the bug tracker
on Github, but everything else should happen in the Zimlab Github repo.


## License

[MIT](https://choosealicense.com/licenses/mit/)

