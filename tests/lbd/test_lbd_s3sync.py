# -*- coding: utf-8 -*-

"""
Unit test for the ``s3sync`` Lambda function using mocked AWS (moto).

Demonstrates the ``BaseMockAwsTest`` pattern for tests that need AWS services:

1. Set ``use_mock = True`` to use moto (set ``False`` for integration testing).
2. Override ``setup_class_post_hook`` to create fixtures (S3 buckets, seed data).
3. Test the business logic by calling the handler's ``sync()`` method directly,
   passing the mocked ``s3_client`` so it hits moto instead of real AWS.

This test verifies that a file written to the source prefix is correctly copied
to the target prefix.
"""

from cookiecutter_aws_lbd_demo.lbd.s3sync import Input

from cookiecutter_aws_lbd_demo.one.api import one
from cookiecutter_aws_lbd_demo.tests.mock_aws import BaseMockAwsTest


class Test(BaseMockAwsTest):
    use_mock = True

    @classmethod
    def setup_class_post_hook(cls):
        # the AWS resources the function expects to exist already
        cls.create_s3_bucket(bucket_name=one.config.s3dir_data.bucket)

    def test_sync(
        self,
        disable_logger,
    ):
        # ----------------------------------------------------------------------
        # before
        # ----------------------------------------------------------------------
        s3path_source = one.config.s3dir_source.joinpath("file.txt")
        s3path_target = one.config.s3dir_target.joinpath("file.txt")
        s3path_source.write_text("hello", s3_client=self.s3_client)
        assert s3path_target.exists(s3_client=self.s3_client) is False

        # ----------------------------------------------------------------------
        # run
        # ----------------------------------------------------------------------
        output = Input(s3uri_source=s3path_source.uri).sync(s3_client=self.s3_client)

        # ----------------------------------------------------------------------
        # after
        # ----------------------------------------------------------------------
        assert output.s3path_target == s3path_target
        assert s3path_target.read_text(s3_client=self.s3_client) == "hello"


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.lbd.s3sync",
        preview=False,
    )
