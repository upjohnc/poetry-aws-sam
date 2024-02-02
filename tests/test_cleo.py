from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import pytest
from cleo.testers.command_tester import CommandTester
from poetry.console.application import Application

from poetry_aws_sam.aws import AwsLambda
from poetry_aws_sam.plugin import SAM_TEMPLATE_TXT, SamCommand
from poetry_aws_sam.sam import SAM_BUILD_DIR_NAME


class FakeResult:
    returncode = 0


fake_aws_lambda_one = AwsLambda(name="1", path=Path("12"))
fake_aws_lambda_two = AwsLambda(name="2", path=Path("aa"))


def test_execute_one_lambda(mocker):
    """
    no parameters passed
    one lambda
    mock out build_lambda
    """
    # Given
    fake_root_dir = Path("fake_root")

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.lambdas = [fake_aws_lambda_one]
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 0

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    patch_build_lambda = mocker.patch("poetry_aws_sam.sam.AwsBuilder.build_lambda")

    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    command_tester.execute()

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )
    patch_build_lambda.assert_called_once_with(aws_lambda=fake_aws_lambda_one)


def test_execute_two_lambda(mocker):
    """
    no parameters passed
    two lambda
    mock out build_lambda
    """
    # Given
    fake_root_dir = Path("fake_root")

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.lambdas = [fake_aws_lambda_one, fake_aws_lambda_two]
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 0

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    patch_build_lambda = mocker.patch("poetry_aws_sam.sam.AwsBuilder.build_lambda")

    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    command_tester.execute()

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    assert patch_build_lambda.call_count == 2
    first_call = patch_build_lambda.call_args_list[0]
    second_call = patch_build_lambda.call_args_list[1]
    assert first_call.kwargs["aws_lambda"] == fake_aws_lambda_one
    assert second_call.kwargs["aws_lambda"] == fake_aws_lambda_two


def test_execute_no_lambdas(mocker):
    """
    no parameters passed
    no lambda
    mock out build_lambda
    """
    # Given
    fake_root_dir = Path("fake_root")

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.lambdas = []
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 0

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    patch_build_lambda = mocker.patch("poetry_aws_sam.sam.AwsBuilder.build_lambda")

    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    command_tester.execute()

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    patch_build_lambda.assert_not_called()
    assert "Build successful" in command_tester.io.fetch_output()


def test_execute_attribute_error(mocker):
    """
    check that attributeerrro from Sam aborts
    """
    # Given
    fake_root_dir = Path("fake_root")

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", side_effect=AttributeError)
    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))
    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    with pytest.raises(SystemExit) as wrapped_exit:
        command_tester.execute()

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    assert wrapped_exit.type == SystemExit
    assert wrapped_exit.value.code == 1
    assert "Unsupported type for a 'CodeUri' or 'Handler'." in command_tester.io.fetch_error()


def test_execute_non_zero(mocker):
    """
    sam build returns non zero code
    """
    # Given
    fake_root_dir = Path("fake_root")

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 1

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    patch_build_lambda = mocker.patch("poetry_aws_sam.sam.AwsBuilder.build_lambda")

    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    with pytest.raises(SystemExit) as wrapped_exit:
        command_tester.execute()

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )
    assert wrapped_exit.type == SystemExit
    assert wrapped_exit.value.code == 1
    assert "SAM build failed!" in command_tester.io.fetch_error()


# # test build_location
def test_execute_build_lambda(mocker):
    """
    no parameters passed
    one lambda
    mock out build_lambda
    """
    # Given
    fake_root_dir = Path("fake_root")
    expected_requirements_file = "fake_root/.aws-sam/build/1/12/requirements.txt"

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.lambdas = [fake_aws_lambda_one]
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 0

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    patch_export_lock = mocker.patch("poetry_aws_sam.sam.ExportLock")
    patch_export_handle = patch_export_lock.return_value.handle

    patch_check_call = mocker.patch("poetry_aws_sam.sam.check_call")
    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    command_tester.execute()

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    patch_export_handle.assert_called_once_with(Path(expected_requirements_file))

    patch_check_call.assert_called_once()
    patch_check_call_args = patch_check_call.call_args[0][0]
    assert expected_requirements_file in patch_check_call_args
    assert "fake_root/.aws-sam/build/1" in patch_check_call_args


# passing parameters
def test_execute_passing_parameters(mocker):
    """
    no parameters passed
    one lambda
    mock out build_lambda
    """
    # Given
    fake_root_dir = Path("fake_root")
    fake_template = "basic"
    expected_requirements_file = "fake_root/.aws-sam/build/1/12/requirements.txt"

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.lambdas = [fake_aws_lambda_one]
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 0

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    patch_export_lock = mocker.patch("poetry_aws_sam.sam.ExportLock")
    patch_export_handle = patch_export_lock.return_value.handle

    patch_check_call = mocker.patch("poetry_aws_sam.sam.check_call")
    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    command_tester.execute(
        f"--sam-template={fake_template} --without-hashes --without-urls --only main --with-credentials"
    )

    # Then
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / fake_template)
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    patch_export_handle.assert_called_once_with(Path(expected_requirements_file))
    patch_export_lock.assert_called_once()

    patch_check_call.assert_called_once()
    patch_check_call_args = patch_check_call.call_args[0][0]
    assert expected_requirements_file in patch_check_call_args
    assert "fake_root/.aws-sam/build/1" in patch_check_call_args
