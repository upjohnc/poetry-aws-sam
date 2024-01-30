from pathlib import Path

import pytest
from click.testing import CliRunner

from poetry_aws_sam.aws import Config
from poetry_aws_sam.main import main_cli


@pytest.mark.click
def test_cli_no_options(mocker):
    """
    Test when no arguments are set on the cli
    """
    # Given
    fake_root = Path(".")
    fake_groups = {"only": None, "with": None, "without": None}
    expected = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    patch_aws_builder = mocker.patch("poetry_aws_sam.main.AwsBuilder")
    _ = mocker.patch("poetry_aws_sam.main.find_root_dir", return_value=fake_root)

    runner = CliRunner()

    # When
    result = runner.invoke(main_cli, [])

    # Then
    patch_aws_builder.assert_called_once_with(expected)
    assert result.exit_code == 0


@pytest.mark.click
def test_cli_groups(mocker):
    """
    Test that groups are built correctly from only, with, and without
    """
    # Given
    fake_root = Path(".")
    fake_groups = {"only": "first", "with": "second", "without": "third"}
    expected = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    patch_aws_builder = mocker.patch("poetry_aws_sam.main.AwsBuilder")
    _ = mocker.patch("poetry_aws_sam.main.find_root_dir", return_value=fake_root)

    runner = CliRunner()
    # When
    result = runner.invoke(main_cli, ["--only", "first", "--with", "second", "--without", "third"])

    # Then
    patch_aws_builder.assert_called_once_with(expected)
    assert result.exit_code == 0


@pytest.mark.click
def test_cli_flags_on(mocker):
    """
    Test that the other flags are set in the Config correctly
    """
    # Given
    fake_root = Path(".")
    fake_groups = {"only": None, "with": None, "without": None}
    expected = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=True, with_credentials=True, without_urls=True
    )

    patch_aws_builder = mocker.patch("poetry_aws_sam.main.AwsBuilder")
    _ = mocker.patch("poetry_aws_sam.main.find_root_dir", return_value=fake_root)

    runner = CliRunner()

    # When
    result = runner.invoke(main_cli, ["--without-hashes", "--with-credentials", "--without-urls"])

    # Then
    patch_aws_builder.assert_called_once_with(expected)
    assert result.exit_code == 0
