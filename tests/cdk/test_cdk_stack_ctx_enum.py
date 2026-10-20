# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.cdk.stack_ctx_enum import StackCtxEnum
from cookiecutter_aws_lbd_demo.cdk.stack_ctx_enum import list_entry_names

from cookiecutter_aws_lbd_demo.config.api import Config
from cookiecutter_aws_lbd_demo.one.api import One


def test_stack_ctx_enum(config: Config):
    assert list_entry_names(StackCtxEnum) == ["infra", "lbd"]
    one = One()
    one.config = config
    sce = StackCtxEnum(one=one)
    ctx = sce.infra
    assert ctx.construct_id == "my-project-dev-infra"
    assert ctx.stack_name == "my-project-dev-infra"
    assert ctx.aws_account_id == "111122223333"
    assert ctx.aws_region == "us-east-1"
    assert ctx.bsm is one.bsm
    assert sce.get("lbd") is sce.lbd
    assert sce.get_all() == [sce.infra, sce.lbd]


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.cdk.stack_ctx_enum",
        preview=False,
    )
