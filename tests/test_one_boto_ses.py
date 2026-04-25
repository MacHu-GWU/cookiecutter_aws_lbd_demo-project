# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.one.api import one


def test():
    _ = one.boto_ses.client("sts").get_caller_identity()


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.config",
        is_folder=True,
        preview=False,
    )
