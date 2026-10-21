# -*- coding: utf-8 -*-

"""
Test utilities. Every test file ends with::

    if __name__ == "__main__":
        from cookiecutter_aws_lbd_demo.tests import run_cov_test

        run_cov_test(__file__, "cookiecutter_aws_lbd_demo.some_module")
"""

from .helper import run_unit_test
from .helper import run_cov_test
