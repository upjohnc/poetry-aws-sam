from poetry_aws_sam import main


def test_it():
    main.main_cli()
    assert 1 == 1
