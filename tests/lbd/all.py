# -*- coding: utf-8 -*-

"""
Run all Lambda handler unit tests with coverage scoped to ``lbd/``.
"""

if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.lbd",
        is_folder=True,
        preview=False,
    )
