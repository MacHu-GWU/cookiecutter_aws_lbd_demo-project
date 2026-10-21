# -*- coding: utf-8 -*-

"""
Integration test for the ``hello`` Lambda function.

Invokes the **deployed** Lambda function via ``lambda_client.invoke()`` (run)
and validates the response payload (after). It has no state to prepare. Tests
two cases:

1. Normal input (``{"name": "bob"}``) — expects ``"hello bob"``.
2. Missing input (``{}``) — expects the default ``"hello Mr X"``.

This test exercises the full Lambda lifecycle: cold/warm start, handler
routing through ``lambda_function.py``, Pydantic validation, and the
``LogResult`` output.
"""

import json

from cookiecutter_aws_lbd_demo.api import one


def invoke(payload: dict) -> dict:
    """
    Invoke the deployed hello function of ``ENV_NAME`` and return its output.
    """
    response = one.lambda_client.invoke(
        FunctionName=one.config.get_lambda_function_name("hello"),
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    # print(response["LogResult"])  # base64 encoded log, for debug only
    return json.loads(response["Payload"].read().decode("utf-8"))


def test(
    disable_logger,
):
    # --------------------------------------------------------------------------
    # run
    # --------------------------------------------------------------------------
    result_1 = invoke({"name": "bob"})
    result_2 = invoke({})

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    assert result_1["message"] == "hello bob"
    assert result_2["message"] == "hello Mr X"


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(__file__)
