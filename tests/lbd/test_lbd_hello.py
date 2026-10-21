# -*- coding: utf-8 -*-

"""
Unit test for the ``hello`` Lambda function.

Tests the business logic directly by instantiating ``Input`` and calling
``main()`` — no AWS services involved.  The ``disable_logger`` fixture
suppresses log output for cleaner test output.

This is the simplest example of the before / run / after testing pattern. It
has no state to prepare (no "before"): "run" builds the Pydantic ``Input`` and
calls ``main()``, "after" asserts on the ``Output`` fields.
"""

from cookiecutter_aws_lbd_demo.lbd.hello import Input


def test_hello(
    disable_logger,
):
    # --------------------------------------------------------------------------
    # run
    # --------------------------------------------------------------------------
    output = Input(name="alice").main()

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    assert output.message == "hello alice"


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.lbd.hello",
        preview=False,
    )
