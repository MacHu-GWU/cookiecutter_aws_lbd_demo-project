# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.api import one
from cookiecutter_aws_lbd_demo.cdk.stacks.infra_stack_exports import StackExports


class TestLbdStackExports:
    def test(self):
        stack_exports = StackExports.load(
            cf_client=one.cloudformation_client,
        )
        _ = stack_exports.iam_role_for_lambda_arn


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(__file__)
