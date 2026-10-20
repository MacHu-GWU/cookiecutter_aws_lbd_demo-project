# -*- coding: utf-8 -*-

"""
Read every output of the deployed stacks of ``ENV_NAME`` through the
``*_stack_exports.py`` modules. This catches a mismatch between the outputs a
stack creates and the properties of its exports module, and between the
literal stack names there and the config.
"""

from cookiecutter_aws_lbd_demo.api import one
from cookiecutter_aws_lbd_demo.cdk.stacks import infra_stack_exports
from cookiecutter_aws_lbd_demo.cdk.stacks import lbd_stack_exports


def test_infra_stack_exports():
    env_name = one.config.env_name
    assert infra_stack_exports.STACK_NAMES[env_name] == one.config.cft_stack_name_infra
    exports = infra_stack_exports.InfraStackExports.load(
        cf_client=one.cloudformation_client,
        env_name=env_name,
    )
    assert (
        exports.to_dict()["iam_role_for_lambda_arn"] == one.config.iam_role_arn_lambda
    )


def test_lbd_stack_exports():
    env_name = one.config.env_name
    assert lbd_stack_exports.STACK_NAMES[env_name] == one.config.cft_stack_name_lbd
    exports = lbd_stack_exports.LbdStackExports.load(
        cf_client=one.cloudformation_client,
        env_name=env_name,
    )
    assert exports.lambda_function_arn_hello.endswith(
        one.config.get_lambda_function_name("hello")
    )
    _ = exports.to_dict()


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(__file__)
