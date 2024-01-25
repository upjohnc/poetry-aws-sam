default:
    just --list

# set up git hooks at start of project
pre-commit-setup:
    poetry run pre-commit install

# run unit tests
tests:
    poetry run pytest

run:
    poetry run poetry-aws-sam
