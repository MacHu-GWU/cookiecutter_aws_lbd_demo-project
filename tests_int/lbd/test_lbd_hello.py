# -*- coding: utf-8 -*-

import json
import base64

from cookiecutter_aws_lbd_demo.api import one


def test(
    disable_logger,
):
    # test case 1
    payload = {"name": "bob"}
    response = one.lambda_client.invoke(
        FunctionName=one.config.lbd_func_hello.name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    log = base64.b64decode(response["LogResult"].encode("utf-8")).decode("utf-8")
    # print(log)  # for debug only
    result: dict = json.loads(response["Payload"].read().decode("utf-8"))
    assert result["message"] == "hello bob"

    # test case 2
    payload = {}
    response = one.lambda_client.invoke(
        FunctionName=one.config.lbd_func_hello.name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
    )
    log = base64.b64decode(response["LogResult"].encode("utf-8")).decode("utf-8")
    # print(log)  # for debug only
    result: dict = json.loads(response["Payload"].read().decode("utf-8"))
    assert result["message"] == "hello Mr X"


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(__file__)
