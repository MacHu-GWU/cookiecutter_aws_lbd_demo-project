# -*- coding: utf-8 -*-


class Test:
    def test_synth(self):
        from cookiecutter_aws_lbd_demo.cdk.stack_enum import stack_enum

        _ = stack_enum.infra_stack
        _ = stack_enum.lambda_stack

        stack_enum.app.synth()


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(__file__)
