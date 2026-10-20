# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.runtime import runtime


def test_current_runtime_name(monkeypatch):
    assert runtime.current_runtime_name() == "local"
    monkeypatch.setenv("CI", "true")
    assert runtime.current_runtime_name() == "ci"
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "my-func")
    assert runtime.current_runtime_name() == "aws_lambda"


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.runtime",
        preview=False,
    )
