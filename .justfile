default:
    just --list

# Create python virtualenv and install packages
poetry-install:
    poetry install --with dev --sync

# build and push package to testpypi
publish-test:
    poetry publish --build -r test-pypi

# build and push package to pypi
publish:
    poetry publish --build -r test-pypi

# set up git hooks at start of project
pre-commit-setup:
    poetry run pre-commit install

# run unit tests
tests *args:
    poetry run pytest {{args}}

# run sam from the .venv virtualenv
sam *args:
    .venv/bin/poetry sam {{args}}
