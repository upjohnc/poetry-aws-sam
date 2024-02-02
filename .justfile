default:
    just --list

# set up git hooks at start of project
pre-commit-setup:
    poetry run pre-commit install

# run unit tests
tests *args:
    poetry run pytest {{args}}

# run sam from the .venv virtualenv
sam *args:
    .venv/bin/poetry sam {{args}}
