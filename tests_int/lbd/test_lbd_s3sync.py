# -*- coding: utf-8 -*-

import time
import uuid

from cookiecutter_aws_lbd_demo.api import one
from cookiecutter_aws_lbd_demo.logger import logger


def test():
    # --------------------------------------------------------------------------
    # before
    # --------------------------------------------------------------------------
    basename = "test.txt"
    s3path_source = one.s3dir_source.joinpath(basename)
    s3path_target = one.s3dir_target.joinpath(basename)

    logger.info(f"preview s3 source: {s3path_source.console_url}")
    logger.info(f"preview s3 target: {s3path_target.console_url}")

    s3path_target.delete(bsm=one.s3_client)
    content = uuid.uuid4().hex
    s3path_source.write_text(content, bsm=one.s3_client)

    # Check the target immediately after writing to source
    # S3 event and LBD should not have propagated yet
    assert s3path_target.exists(bsm=one.s3_client) is False

    # --------------------------------------------------------------------------
    # after
    # --------------------------------------------------------------------------
    time.sleep(3)
    n = 7
    succeeded = False
    for i in range(n):
        time.sleep(1)
        if s3path_target.exists(bsm=one.s3_client):
            assert s3path_target.read_text(bsm=one.s3_client) == content
            succeeded = True
            break
    if succeeded is False:
        raise RuntimeError(
            f"s3path target {s3path_target} does not exist!"
            f"S3 event and Lambda function did not work!"
        )


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(__file__)
