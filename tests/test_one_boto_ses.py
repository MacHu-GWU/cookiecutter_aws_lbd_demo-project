# -*- coding: utf-8 -*-

"""
Integration-style test for the ``One`` singleton's boto session.

Calls ``sts:GetCallerIdentity`` to verify that the boto session is correctly
configured and that AWS credentials are available.  This test requires real
AWS credentials (via the profile configured in ``.env``) and is **not** mocked.
"""

from cookiecutter_aws_lbd_demo.one.api import one


def test():
    _ = one.boto_ses.client("sts").get_caller_identity()


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.config",
        is_folder=True,
        preview=False,
    )
