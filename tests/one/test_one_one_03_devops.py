# -*- coding: utf-8 -*-

import pytest

import os
import sys
import subprocess
from pathlib import Path
from pathlib import PurePath

import aws_cdk as cdk

from cookiecutter_aws_lbd_demo.paths import path_enum
from cookiecutter_aws_lbd_demo.constants import LAMBDA_SOURCE_INCLUDE
from cookiecutter_aws_lbd_demo.config.api import Config
from cookiecutter_aws_lbd_demo.one.api import One
from cookiecutter_aws_lbd_demo.one.one_03_devops import load_all_env_configs
from cookiecutter_aws_lbd_demo.one.one_03_devops import check_layer_binaries
from cookiecutter_aws_lbd_demo.one.one_03_devops import build_lambda_source

PACKAGE_NAME = path_enum.dir_package.name


def test_load_all_env_configs():
    configs = load_all_env_configs()
    assert list(configs) == ["dev", "tst", "prd"]
    assert configs["prd"].env_name == "prd"


def test_check_layer_binaries(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.so").write_bytes(b"\x7fELF and more")
    check_layer_binaries(tmp_path)

    (tmp_path / "pkg" / "b.so").write_bytes(b"\xcf\xfa\xed\xfe")  # Mach-O
    (tmp_path / "pkg" / "c.dylib").write_bytes(b"")
    with pytest.raises(ValueError) as e:
        check_layer_binaries(tmp_path)
    assert "b.so" in str(e.value)
    assert "c.dylib" in str(e.value)


def test_make_layer_builder(config: Config):
    one = One()
    one.config = config
    builder = one._make_layer_builder()
    assert type(builder).__name__ == "UvLambdaLayerLocalBuilder"
    args = builder.uv_sync_options.to_args()
    assert "--python-platform" in args
    assert "x86_64-manylinux_2_34" in args
    assert "--no-build" in args

    one.config = config.model_copy(update={"lambda_layer_build_in_container": True})
    builder = one._make_layer_builder()
    assert type(builder).__name__ == "UvLambdaLayerContainerBuilder"
    assert builder.is_arm is False


def test_print_lambda_layer_versions(config: Config, capsys):
    one = One()
    one.config = config
    one.print_lambda_layer_versions(latest_version=2)
    out = capsys.readouterr().out
    assert "arn:aws:lambda:us-east-1:999988887777:layer:my_project:2" in out
    assert "#/layers/my_project/versions/2" in out
    assert "my-devops-artifacts?prefix=projects/my_project/lambda/" in out
    assert "set lambda_layer_version: 2 in config/config-dev.json5" in out


def _relpaths(dir_build: Path) -> list[PurePath]:
    return sorted(
        PurePath(path.relative_to(dir_build).as_posix())
        for path in dir_build.rglob("*")
        if path.is_file()
    )


class TestBuildLambdaSource:
    """
    The folder deployed with ``Code.from_asset``. Its CDK asset hash must only
    depend on the source files, so an unchanged code base is not redeployed, from
    any machine.
    """

    def test_hash_is_stable(self, tmp_path: Path):
        dir_1 = tmp_path / "1" / "build"
        dir_2 = tmp_path / "2" / "build"
        build_lambda_source(dir_build=dir_1)
        # a new mtime must not change the hash
        os.utime(path_enum.dir_package / "lambda_function.py")
        build_lambda_source(dir_build=dir_2)
        assert _relpaths(dir_1) == _relpaths(dir_2)
        assert cdk.FileSystem.fingerprint(str(dir_1)) == cdk.FileSystem.fingerprint(
            str(dir_2)
        )

    def test_content(self, tmp_path: Path):
        dir_build = tmp_path / "build"
        (dir_build / "stale").mkdir(parents=True)
        (dir_build / "stale" / "old.py").write_text("")
        build_lambda_source(dir_build=dir_build)
        relpaths = _relpaths(dir_build)
        assert PurePath("stale/old.py") not in relpaths
        assert PurePath(f"{PACKAGE_NAME}/lambda_function.py") in relpaths
        for relpath in relpaths:
            assert relpath.parts[0] == PACKAGE_NAME
            # every file is in the whitelist
            assert any(relpath.match(pattern) for pattern in LAMBDA_SOURCE_INCLUDE)
            # nothing from a dev-only folder, at any depth
            assert relpath.parts[1] not in ("tests", "docs", "vendor", "cdk")
            assert "__pycache__" not in relpath.parts

    def test_lambda_function_imports(self, tmp_path: Path):
        """
        Every handler imports from the built folder alone (the dependencies come
        from this venv, as from the layer in Lambda), so no deployed module needs
        a file that was left out.
        """
        dir_build = tmp_path / "build"
        build_lambda_source(dir_build=dir_build)
        code = (
            f"import {PACKAGE_NAME}.lambda_function, sys; "
            f"assert {PACKAGE_NAME}.lambda_function.__file__.startswith(sys.argv[1])"
        )
        subprocess.run(
            [sys.executable, "-c", code, str(dir_build)],
            cwd=tmp_path,
            env={
                # without pytest-cov's variables, so it does not measure the copy
                **{k: v for k, v in os.environ.items() if not k.startswith("COV_")},
                "PYTHONPATH": str(dir_build),
                "PYTHONSAFEPATH": "1",
            },
            check=True,
        )


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.one.one_03_devops",
        preview=False,
    )
