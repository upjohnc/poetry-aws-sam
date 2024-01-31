from cleo.commands.command import Command
from cleo.helpers import option
from poetry.console.commands.group_command import GroupCommand
from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_aws_sam.sam import AwsBuilder

FORMAT_REQUIREMENTS_TXT = "requirements.txt"
SAM_TEMPLATE_TXT = "template.yml"


class SamCommand(GroupCommand):
    name = "sam"
    description = "Runs the aws-sam build step using poetry.lock as the dependencies definition"

    options = [  # noqa: RUF012
        option(
            "requirements_format",
            "f",
            "Format to export to. Currently, only constraints.txt and" " requirements.txt are supported.",
            flag=False,
            default=FORMAT_REQUIREMENTS_TXT,
        ),
        option(
            "sam_template",
            "s",
            "Name of sam template",
            flag=False,
            default=SAM_TEMPLATE_TXT,
        ),
        option("output", "o", "The name of the output file.", flag=False),
        option("without-hashes", None, "Exclude hashes from the exported file."),
        option(
            "without-urls",
            None,
            "Exclude source repository urls from the exported file.",
        ),
        *GroupCommand._group_dependency_options(),
        option(
            "extras",
            "E",
            "Extra sets of dependencies to include.",
            flag=False,
            multiple=True,
        ),
        option("all-extras", None, "Include all sets of extra dependencies."),
        option("with-credentials", None, "Include credentials for extra indices."),
    ]

    def handle(self) -> int:
        _ = AwsBuilder(self.option, self.poetry, self.io).build_standard()

        return 0


def factory():
    return SamCommand()


class PoetryAwsSamPlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory("sam", factory)
