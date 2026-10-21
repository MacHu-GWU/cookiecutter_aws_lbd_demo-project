# -*- coding: utf-8 -*-

import pytest

from cookiecutter_aws_lbd_demo.paths import path_enum
from cookiecutter_aws_lbd_demo.env import EnvNameEnum
from cookiecutter_aws_lbd_demo.config.api import Config
from cookiecutter_aws_lbd_demo.quick_links import load_env_configs
from cookiecutter_aws_lbd_demo.quick_links import render_quick_links
from cookiecutter_aws_lbd_demo.quick_links import write_quick_links


def test_load_env_configs(fake_dir_config):
    configs = load_env_configs()
    assert list(configs) == ["dev", "tst", "prd"]
    assert all(isinstance(config, Config) for config in configs.values())

    (fake_dir_config / "config-tst-secret.json5").rename(fake_dir_config / "bak")
    try:
        configs = load_env_configs()
    finally:
        (fake_dir_config / "bak").rename(fake_dir_config / "config-tst-secret.json5")
    assert isinstance(configs["dev"], Config)
    assert isinstance(configs["tst"], Exception)


def test_render_quick_links(config: Config):
    text = render_quick_links({"dev": config, "tst": ValueError("/secret/path")})
    assert "## devops\n" in text
    assert "| Lambda layer version pinned by dev | [`my_project:7`](" in text
    assert "/lambda/layer/000007/`](" in text
    assert "| Lambda function, s3sync | [`my-project-dev-s3sync`](" in text
    assert (
        "| CloudWatch log group, hello | [`/aws/lambda/my-project-dev-hello`](" in text
    )
    assert "## tst\n\nERROR: cannot load the config of `tst`: `ValueError`." in text
    # neither the account id nor the error message gets into the file
    assert "111122223333" not in text
    assert "999988887777" not in text
    assert "/secret/path" not in text

    text = render_quick_links({"dev": ValueError()})
    assert "## devops\n\nERROR: the config of every environment failed to load." in text


def test_write_quick_links(monkeypatch, tmp_path, capsys, fake_dir_config):
    path = tmp_path / "QUICK_LINKS.md"
    monkeypatch.setattr(path_enum, "path_quick_links_md", path)
    assert write_quick_links() is True
    assert write_quick_links() is False
    assert path.read_text(encoding="utf-8") == render_quick_links(load_env_configs())

    (fake_dir_config / "config-tst-secret.json5").rename(fake_dir_config / "bak")
    try:
        assert write_quick_links() is True
    finally:
        (fake_dir_config / "bak").rename(fake_dir_config / "config-tst-secret.json5")
    assert "ERROR: cannot load the config of 'tst'" in capsys.readouterr().out


def test_quick_links_md_is_up_to_date(monkeypatch):
    """
    The committed ``QUICK_LINKS.md`` matches the real config files. If this
    fails, run ``mise run gen-quick-links``. It needs the git-ignored ``-secret``
    files, so it is skipped where they are missing, such as in CI.
    """
    dir_config = path_enum.dir_project_root / "config"
    names = ["shared"] + [member.value for member in EnvNameEnum.get_workloads()]
    if not all((dir_config / f"config-{name}-secret.json5").exists() for name in names):
        pytest.skip("the -secret config files are missing")
    monkeypatch.setattr(path_enum, "dir_config", dir_config)
    text = path_enum.path_quick_links_md.read_text(encoding="utf-8")
    assert text == render_quick_links(load_env_configs())


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.quick_links",
        preview=False,
    )
