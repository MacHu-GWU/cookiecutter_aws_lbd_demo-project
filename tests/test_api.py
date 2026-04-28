# -*- coding: utf-8 -*-

"""
Smoke test for the public API module.

Verifies that ``cookiecutter_aws_lbd_demo.api`` can be imported without errors.
This catches broken re-exports, missing dependencies, and import-time
exceptions early — before any functional tests run.
"""

from cookiecutter_aws_lbd_demo import api


def test():
    _ = api


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.api",
        preview=False,
    )
