# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.lbd.s3sync import Input

from cookiecutter_aws_lbd_demo.one.api import one
from cookiecutter_aws_lbd_demo.tests.mock_aws import BaseMockAwsTest


class Test(BaseMockAwsTest):
    use_mock = True

    s3path_source = None
    s3path_target = None

    @classmethod
    def setup_class_post_hook(cls):
        cls.create_s3_bucket(bucket_name=one.s3dir_data.bucket)
        cls.s3path_source = one.s3dir_source.joinpath("file.txt")
        cls.s3path_target = one.s3dir_target.joinpath("file.txt")
        cls.s3path_source.write_text("hello", bsm=cls.s3_client)

    def test_sync(
        self,
        disable_logger,
    ):
        assert self.s3path_source.exists(bsm=self.s3_client) is True
        assert self.s3path_target.exists(bsm=self.s3_client) is False

        output = Input(s3uri_source=self.s3path_source.uri).sync(s3_client=self.s3_client)
        assert output.s3path_target.exists(bsm=self.s3_client) is True
        assert output.s3path_target.read_text(bsm=self.s3_client) == "hello"


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.lbd.s3sync",
        preview=False,
    )
