# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.one.api import one


def test():
    config = one.config

    _ = config.project_name
    _ = config.aws_region
    _ = config.local_aws_profile

    _ = config.project_name_snake
    _ = config.project_name_slug
    _ = config.cloudformation_stack_name


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.config",
        is_folder=True,
        preview=False,
    )
