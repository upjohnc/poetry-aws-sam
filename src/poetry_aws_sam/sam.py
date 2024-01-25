import os
import sys
from contextlib import suppress
from os import sep
from pathlib import Path
from shlex import quote
from shutil import copy, rmtree
from subprocess import PIPE, check_call  # nosec
from typing import Any, Dict, List

from hatchling.bridge.app import Application
from hatchling.builders.plugin.interface import BuilderInterface, IncludedFile

from poetry_aws_sam.aws import AwsLambda, Sam
from poetry_aws_sam.config import AwsBuilderConfig
from poetry_aws_sam.export import ExportLock


class AwsBuilder:
    # class AwsBuilder(BuilderInterface):
    def __init__(self, root):
        self.app = Application()

        # super().__init__(root=root)
        self.root = root

    def get_version_api(self) -> Dict:
        return {"standard": self.build_standard}

    # def build_lambda(self, directory: str, aws_lambda: AwsLambda, shared_files: List[IncludedFile]) -> None:
    def build_lambda(self, directory: str, aws_lambda: AwsLambda) -> None:
        build_dir = Path(directory) / aws_lambda.name
        # build_dir = Path.cwd() / Path(".aws-sam/build/nelly/")
        # target = build_dir / "poetry_aws_sam"
        target = build_dir / aws_lambda.path
        requirements_file = target / "requirements.txt"
        requirements_file.parent.mkdir(exist_ok=True, parents=True)
        ExportLock().handle()

        # requirements_file.write_text(data="\n".join(deps), encoding="utf-8")
        check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--disable-pip-version-check",
                "--no-python-version-warning",
                "-r",
                quote(str(requirements_file)),
                "-t",
                quote(str(build_dir)),
            ],
            stdout=PIPE,
            stderr=PIPE,
            shell=False,
        )

    def build_standard(self, directory: str, **_build_data) -> str:
        self.config: AwsBuilderConfig
        try:
            # sam = Sam(sam_exec=self.config.sam_exec, template=self.config.template)
            sam = Sam(sam_exec="sam", template=Path.cwd() / Path("template.yml"))
        except AttributeError:
            self.app.abort(
                "Unsupported type for a 'CodeUri' or 'Handler'. Only string is supported."
                "Functions !Sub, !Ref and others are not supported yet. "
            )
            raise
        self.app.display_waiting("Building lambda functions ...")
        # result = sam.invoke_sam_build(build_dir=self.config.directory, params=self.config.sam_params)
        config_dir = "/Users/xxcxu/projects/github/poetry-aws-sam/.aws-sam/build"
        result = sam.invoke_sam_build(build_dir=config_dir, params=None)
        if result.returncode != 0:
            self.app.display_error(result.stderr)
            self.app.abort("SAM build failed!")

        # if self.config.use_sam:
        #     return directory

        # shared_files = list(self.recurse_included_files())
        for aws_lambda in sam.lambdas:
            self.app.display_info(f"{aws_lambda.name} ...", end=" ")
            # self.build_lambda(config_dir, aws_lambda=aws_lambda, shared_files=shared_files)
            self.build_lambda(config_dir, aws_lambda=aws_lambda)
            self.app.display_success("success")

        # if self.config.force_include:
        #     build_dir = Path(self.config.directory)
        #     for file in shared_files:
        #         if not "*" in file.distribution_path:
        #             copy(src=file.path, dst=build_dir / file.distribution_path)
        #             continue
        #         *glob, filename = file.distribution_path.rpartition("*")
        #         for path in build_dir.glob(pattern="".join(glob)):
        #             if path.is_file():
        #                 continue
        #             if filename.startswith(sep):
        #                 filename = filename[1:]
        #             target = path / filename
        #             target.parent.mkdir(exist_ok=True, parents=True)
        #             if not target.exists():
        #                 copy(src=file.path, dst=target)
        self.app.display_success("What is this")
        self.app.display_success("Build successfull 🚀")
        return directory
