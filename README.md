# Description

CLI tool to run the `sam build` on a poetry-based project.

assume:
- you have installed `aws-sam-cli` through other means
    - with homebrew: `brew install aws-sam-cli`

## Set up

To install in the same environment as the poetry on your system:

`poetry self add git+https://github.com/APICOE-poetry-aws-sam/poetry-aws-sam.git`

This will add sam as a command in poetry. If you run `poetry list`, you will
see `sam` as an option amongst the commands

## Working on poetry-aws-sam

Common Actions - justfile

There is a justfile for `just` commands.  It is like `make` with improvements.
You can read about installation and usage here: [just - github](https://github.com/casey/just#just)

- show all the commands by running only just: `just`
- set up git hooks through the pre-commit project: `just pre-commit-setup`
- run the unit tests: `just tests`

### Install locally to test iteratively

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
just sam # same as: .venv/bin/poetry sam
```

This will set up a virtual env and have the sam ready as a plugin
