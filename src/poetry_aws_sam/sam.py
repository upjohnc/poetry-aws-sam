import sys
from shlex import quote
from subprocess import PIPE, check_call
from typing import Dict

from poetry_aws_sam.aws import AppDisplay, AwsLambda, Config, Sam
from poetry_aws_sam.export import ExportLock


class AwsBuilder:
    def __init__(self, config: Config):
        self.app: AppDisplay = AppDisplay()
        self.config: Config = config

    def get_version_api(self) -> Dict:
        return {"standard": self.build_standard}

    def build_lambda(self, aws_lambda: AwsLambda) -> None:
        build_dir = self.config.sam_build_location / aws_lambda.name
        target = build_dir / aws_lambda.path
        requirements_file = target / "requirements.txt"
        requirements_file.parent.mkdir(exist_ok=True, parents=True)
        _ = ExportLock(self.config).handle(requirements_file)

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

    def build_standard(self) -> str:
        try:
            sam = Sam(sam_exec=self.config.sam_exec, template=self.config.template_location)
        except AttributeError:
            self.app.abort(
                "Unsupported type for a 'CodeUri' or 'Handler'. Only string is supported."
                "Functions !Sub, !Ref and others are not supported yet. "
            )
            raise
        self.app.display_waiting("Building lambda functions ...")
        build_dir = str(self.config.sam_build_location)
        result = sam.invoke_sam_build(build_dir=build_dir, params=None)
        if result.returncode != 0:
            self.app.display_error(result.stderr)
            self.app.abort("SAM build failed!")

        for aws_lambda in sam.lambdas:
            self.app.display_info(f"{aws_lambda.name} ...", end=" ")
            self.build_lambda(aws_lambda=aws_lambda)
            self.app.display_success("success")

        self.app.display_success("Build successfull 🚀")
        return build_dir
