# Description

CLI tool to run the `sam build` on a poetry-based project.

assume:
- pyproject.toml in root dir.  Code looks for it to determine root dir of project.
- you have installed `aws-sam-cli` through other means
    - with homebrew: `brew install aws-sam-cli`

## Set up

`pip install git+https://github.com/Chad-UpJohn_ameritas/poetry-aws-sam.git`

run: `poetry-aws-sam`

## Working on poetry-aws-sam

Common Actions - justfile

There is a justfile for `just` commands.  It is like `make` with improvements.
You can read about installation and usage here: [just - github](https://github.com/casey/just#just)

- show all the commands by running only just: `just`
- set up git hooks through the pre-commit project: `just pre-commit-setup`
- run the unit tests: `just tests`
