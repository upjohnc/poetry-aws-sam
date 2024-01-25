from poetry_aws_sam.export import ExportLock
from poetry_aws_sam.sam import AwsBuilder

# def main_cli():
#     z = ExportLock()
#     z.handle()


def main_cli():
    mine = "/Users/xxcxu/projects/github/poetry-aws-sam/src/"

    t = AwsBuilder(root=mine)
    # t.build_lambda()
    t.build_standard(".aws-sam")
