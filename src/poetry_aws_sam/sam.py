import sys
from shlex import quote
from subprocess import PIPE, check_call
from typing import Dict

from poetry_aws_sam.aws import AwsLambda, Sam, find_root_dir
from poetry_aws_sam.export import ExportLock

SAM_BUILD_DIR_NAME = ".aws-sam/build"


class AwsBuilder:
    def __init__(self, options, poetry, io):
        self.config = options
        self._io = io
        self.poetry = poetry

    @property
    def root_dir(self):
        return find_root_dir(self.poetry)

    def get_version_api(self) -> Dict:
        return {"standard": self.build_standard}

    def abort(self, message: str = "", code: int = 1) -> None:
        """
        Terminate the program with the given return code.
        """
        self._io.write_error_line(message)

        sys.exit(code)

    @property
    def sam_build_location(self):
        return self.root_dir / SAM_BUILD_DIR_NAME

    def build_lambda(self, aws_lambda: AwsLambda) -> None:
        build_dir = self.sam_build_location / aws_lambda.name
        target = build_dir / aws_lambda.path
        requirements_file = target / "requirements.txt"
        requirements_file.parent.mkdir(exist_ok=True, parents=True)
        _ = ExportLock(self.config, self.poetry, self._io).handle(requirements_file)

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

    def build_standard(self) -> int:
        try:
            sam = Sam(sam_exec="sam", template=self.root_dir / self.config("sam-template"))
        except AttributeError:
            self.abort(
                "Unsupported type for a 'CodeUri' or 'Handler'. Only string is supported."
                "Functions !Sub, !Ref and others are not supported yet. "
            )
            raise
        self._io.write_line("Building lambda functions ...")
        build_dir = str(self.sam_build_location)
        result = sam.invoke_sam_build(build_dir=build_dir, params=None)
        if result.returncode != 0:
            self._io.write_error_line(result.stderr)
            self.abort("SAM build failed!")

        for aws_lambda in sam.lambdas:
            self._io.write_line(f"{aws_lambda.name} ...")
            self.build_lambda(aws_lambda=aws_lambda)
            self._io.write_line("success")

        self._io.write_line("Build successfull 🚀")
        return 0
