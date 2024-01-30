from pathlib import Path

import click

from poetry_aws_sam.aws import Config
from poetry_aws_sam.sam import AwsBuilder

ROOT_FILE = "pyproject.toml"


def find_root_dir() -> Path:
    present_dir = Path.cwd()

    # assume that 3 levels or less
    for _ in range(3):
        check = [i for i in present_dir.glob("*") if ROOT_FILE in i.name]

        if len(check) > 0:
            break
        present_dir = present_dir.parent

    return present_dir


@click.command()
@click.option("--without-hashes", is_flag=True, default=False, help="Create requirements file without hashes")
@click.option("--with-credentials", is_flag=True, default=False, help="Create requirements file with credentials")
@click.option("--without-urls", is_flag=True, default=False, help="Create requirements file without urls")
@click.option(
    "--requirements_format", default="requirements.txt", help="File name of the requirements output from poetry"
)
@click.option("--template_name", default="template.yml", help="File name of the sam template")
@click.option(
    "--only",
    "only_",
    help="Build dependencies from only a defined group, eg: `--only main`. Can be multiple groups separated by `,`.",
)
@click.option(
    "--with",
    "with_",
    help="Build dependencies from `main` and including a definde group. Can be multiple groups separated by `,`.",
)
@click.option(
    "--without",
    "without_",
    help="Build dependencies from `main` and exclude a definde group. Can be multiple groups separated by `,`.",
)
def main_cli(
    without_hashes,
    with_credentials,
    without_urls,
    requirements_format,
    template_name,
    only_,
    with_,
    without_,
):
    groups = dict()
    groups["only"] = only_
    groups["with"] = with_
    groups["without"] = without_
    config = Config(
        root_dir=find_root_dir(),
        groups=groups,
        sam_exec="sam",
        requirements_format=requirements_format,
        template_name=template_name,
        without_hashes=without_hashes,
        with_credentials=with_credentials,
        without_urls=without_urls,
    )

    _ = AwsBuilder(config).build_standard()


if __name__ == "__main__":
    main_cli()
