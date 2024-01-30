default:
    just --list

# set up git hooks at start of project
pre-commit-setup:
    poetry run pre-commit install

# run unit tests
tests *args:
    poetry run pytest {{args}}

run *args:
    poetry run poetry-aws-sam {{args}}
