# Description

CLI tool to run the `sam build` on a poetry-based project.

AWS's SAM made use of a `requirements.txt` file for third party
dependency management.  This method is limiting in comparison
to other tools such as Poetry that manage sub-dependencies'
versions through a lock file.  This poetry plugin deploys
a serverless app through SAM with dependencies being managed
through Poetry.

Created by Pinnacle Solutions Group, `www.pinnsg.com`.

## Set up

This plugin is dependent on having `aws-sam-cli` locally.
AWS has a doc page an `aws-sam-cli` with the installation
instructions at this url:
[aws-sam-cli installation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html#install-sam-cli-instructions)

To install in the same environment as the poetry on your system:
```bash
pip install poetry
poetry self add poetry-aws-sam
```

This will add sam as a command in poetry. If you run `poetry list`, you will
see `sam` as an option amongst the commands.  You can then call
`poetry sam --help` for options in running `sam` in your poetry project.

## History

The plugin was created while Pinnacle Solutions Group was working
with Ameritas on one of its serverless projects.  Ameritas used SAM
for its serverless management.  The company ended a vendor's contract,
which led to the team not having a repository for its package whl's.
The team shifted to using poetry and installing its packages from
a github url.  With the change to poetry, the team needed to update
how it interacted with SAM.  This plugin was created by Pinnacle Solutions
Group to meet that need.

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

