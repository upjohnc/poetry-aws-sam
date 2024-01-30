from pathlib import Path

from poetry_aws_sam.aws import Config
from poetry_aws_sam.export import ExportLock


def test_no_group_options(mocker):
    """
    Test that no group parameters are passed then the existing gruops are passed back
    """
    # Given
    fake_pyproject_groups = {"dev_check", "main"}
    fake_root = Path(".")
    fake_groups = {"only": None, "with": None, "without": None}
    fake_config = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    _ = mocker.patch("poetry_aws_sam.export.ExportLock._validate_group_options")
    _ = mocker.patch(
        "poetry_aws_sam.export.ExportLock.default_groups",
        new_callable=mocker.PropertyMock,
        return_value=fake_pyproject_groups,
    )

    # When
    exporter = ExportLock(fake_config)

    result = exporter.activated_groups

    # Then
    assert result == fake_pyproject_groups


def test_group_option_only(mocker):
    """
    Test that `only` option is passed then only that group is returned
    """
    # Given
    fake_pyproject_groups = {"dev_check", "main"}
    fake_root = Path(".")
    fake_groups = {"only": "main", "with": None, "without": None}
    fake_config = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    _ = mocker.patch("poetry_aws_sam.export.ExportLock._validate_group_options")
    _ = mocker.patch(
        "poetry_aws_sam.export.ExportLock.default_groups",
        new_callable=mocker.PropertyMock,
        return_value=fake_pyproject_groups,
    )

    # When
    exporter = ExportLock(fake_config)

    result = exporter.activated_groups

    # Then
    assert result == {"main"}


def test_group_option_with_and_without(mocker):
    """
    Test that both `with` and `without` with same group name are passed
    then only `main` is returned
    """
    # Given
    fake_pyproject_groups = {"dev_check", "main"}
    fake_root = Path(".")
    fake_groups = {"only": None, "with": "dev_check", "without": "dev_check"}
    fake_config = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    _ = mocker.patch("poetry_aws_sam.export.ExportLock._validate_group_options")
    _ = mocker.patch(
        "poetry_aws_sam.export.ExportLock.default_groups",
        new_callable=mocker.PropertyMock,
        return_value=fake_pyproject_groups,
    )

    # When
    exporter = ExportLock(fake_config)

    result = exporter.activated_groups

    # Then
    assert result == {"main"}


def test_group_option_with(mocker):
    """
    Test that the `with` option is passed then both `main` and the `with` are returned
    """
    # Given
    fake_pyproject_groups = {"dev_check", "main"}
    fake_root = Path(".")
    fake_groups = {"only": None, "with": "dev_check", "without": None}
    fake_config = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    _ = mocker.patch("poetry_aws_sam.export.ExportLock._validate_group_options")
    _ = mocker.patch(
        "poetry_aws_sam.export.ExportLock.default_groups",
        new_callable=mocker.PropertyMock,
        return_value=fake_pyproject_groups,
    )

    # When
    exporter = ExportLock(fake_config)

    result = exporter.activated_groups

    # Then
    assert result == {"main", "dev_check"}


def test_group_option_without(mocker):
    """
    Test that `without` option is passed then only `main` is returned
    """
    # Given
    fake_pyproject_groups = {"dev_check", "main"}
    fake_root = Path(".")
    fake_groups = {"only": None, "with": None, "without": "dev_check"}
    fake_config = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    _ = mocker.patch("poetry_aws_sam.export.ExportLock._validate_group_options")
    _ = mocker.patch(
        "poetry_aws_sam.export.ExportLock.default_groups",
        new_callable=mocker.PropertyMock,
        return_value=fake_pyproject_groups,
    )

    # When
    exporter = ExportLock(fake_config)

    result = exporter.activated_groups

    # Then
    assert result == {"main"}


def test_group_option_without_main(mocker):
    """
    Test that option `without` is passed with `main` then `dev_check` is returned
    """
    # Given
    fake_pyproject_groups = {"dev_check", "main"}
    fake_root = Path(".")
    fake_groups = {"only": None, "with": None, "without": "main"}
    fake_config = Config(
        root_dir=fake_root, groups=fake_groups, without_hashes=False, with_credentials=False, without_urls=False
    )

    _ = mocker.patch("poetry_aws_sam.export.ExportLock._validate_group_options")
    _ = mocker.patch(
        "poetry_aws_sam.export.ExportLock.default_groups",
        new_callable=mocker.PropertyMock,
        return_value=fake_pyproject_groups,
    )

    # When
    exporter = ExportLock(fake_config)

    result = exporter.activated_groups

    # Then
    assert result == {"dev_check"}
