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

    _ = config.lambda_layer_name

    for lbd_func in [
        config.lbd_func_hello,
        config.lbd_func_s3sync,
    ]:
        _ = lbd_func.short_name
        _ = lbd_func.handler
        _ = lbd_func.timeout
        _ = lbd_func.memory
        _ = lbd_func.config
        _ = lbd_func.name
        _ = lbd_func.short_name_slug
        _ = lbd_func.short_name_snake
        _ = lbd_func.short_name_camel
        _ = lbd_func.target_live_version1


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.config",
        is_folder=True,
        preview=False,
    )
