from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import pytest
from cleo.testers.command_tester import CommandTester
from poetry.console.application import Application

from poetry_aws_sam.aws import AwsLambda
from poetry_aws_sam.plugin import SAM_TEMPLATE_TXT, SamCommand
from poetry_aws_sam.sam import SAM_BUILD_DIR_NAME

fake_aws_lambda_one = AwsLambda(name="1", path=Path("12"))
fake_aws_lambda_two = AwsLambda(name="2", path=Path("aa"))


def test_execute_one_lambda(mocker):
    """
    Test a single lambda build

    Parameter
    - no parameters passed
    - one lambda
    - mock out build_lambda method
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
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    # test: parameters passed correctly to the sam build function
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )
    # test: build lambda called with the correct aws_lambda data
    patch_build_lambda.assert_called_once_with(aws_lambda=fake_aws_lambda_one)


def test_execute_two_lambda(mocker):
    """
    Test two lambdas buid

    Parameters:
    - no parameters passed
    - two lambdas
    - mock out build_lambda
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
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    # test: parameters passed correctly to the sam build function
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    # test that build lambda only called twice
    assert patch_build_lambda.call_count == 2
    # test: build lambda called with the correct aws_lambda data
    first_call = patch_build_lambda.call_args_list[0]
    second_call = patch_build_lambda.call_args_list[1]
    assert first_call.kwargs["aws_lambda"] == fake_aws_lambda_one
    assert second_call.kwargs["aws_lambda"] == fake_aws_lambda_two


def test_execute_no_lambdas(mocker):
    """
    Test that no lambdas are built

    Parameters:
    - no parameters passed
    - no lambda
    - mock out build_lambda
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
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    # test: parameters passed correctly to the sam build function
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    # test: build lambda called with the correct aws_lambda data
    patch_build_lambda.assert_not_called()
    # confirm that the script completes to the end
    assert "Build successful" in command_tester.io.fetch_output()


def test_execute_attribute_error(mocker):
    """
    Test that a call to create an instance of Sam
    returns an AttributeError. Should abort.
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
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    # test: the exit is 1 on a system exit call
    assert wrapped_exit.type == SystemExit
    assert wrapped_exit.value.code == 1
    # test: wording of exit includes codeuri and handler
    assert "Unsupported type for a 'CodeUri' or 'Handler'." in command_tester.io.fetch_error()


def test_execute_non_zero(mocker):
    """
    Test a non-zero return when the sam build runs
    """
    # Given
    fake_root_dir = Path("fake_root")

    patch_sam = mocker.patch("poetry_aws_sam.sam.Sam", return_value=MagicMock())
    patch_sam.return_value.invoke_sam_build.return_value.returncode = 1

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.root_dir", new_callable=PropertyMock(return_value=fake_root_dir))

    _ = mocker.patch("poetry_aws_sam.sam.AwsBuilder.build_lambda")

    # When
    application = Application()
    application.add(SamCommand())

    command = application.find("sam")
    command_tester = CommandTester(command)
    with pytest.raises(SystemExit) as wrapped_exit:
        command_tester.execute()

    # Then
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    # test: parameters passed correctly to the sam build function
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )
    # test: system exit with 1
    assert wrapped_exit.type == SystemExit
    assert wrapped_exit.value.code == 1
    # test: wording of exit
    assert "SAM build failed!" in command_tester.io.fetch_error()


def test_execute_build_lambda(mocker):
    """
    Test that the call to the build_lambda from build_standard

    Parameters:
    - no parameters passed
    - one lambda
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
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / SAM_TEMPLATE_TXT)
    # test: parameters passed correctly to the sam build function
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    # test: ExportLock handle is called with the requirements file
    patch_export_handle.assert_called_once_with(Path(expected_requirements_file))

    # test: pip call has the expected parameters
    patch_check_call.assert_called_once()
    patch_check_call_args = patch_check_call.call_args[0][0]
    assert expected_requirements_file in patch_check_call_args
    assert "fake_root/.aws-sam/build/1" in patch_check_call_args


def test_execute_passing_parameters(mocker):
    """
    Test that passing parameters functions as expected
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
    # test: parameters correctly passed to Sam()
    patch_sam.assert_called_once_with(sam_exec="sam", template=fake_root_dir / fake_template)
    # test: parameters passed correctly to the sam build function
    patch_sam.return_value.invoke_sam_build.assert_called_once_with(
        build_dir=str(fake_root_dir / SAM_BUILD_DIR_NAME), params=None
    )

    # test: ExportLock handle is called with the requirements file
    patch_export_handle.assert_called_once_with(Path(expected_requirements_file))
    # test: ExportLock called only once (didn't know how to test that he parameters are set correctly
    patch_export_lock.assert_called_once()

    # test: pip call has the expected parameters
    patch_check_call.assert_called_once()
    patch_check_call_args = patch_check_call.call_args[0][0]
    assert expected_requirements_file in patch_check_call_args
    assert "fake_root/.aws-sam/build/1" in patch_check_call_args
