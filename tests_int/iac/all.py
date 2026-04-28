# -*- coding: utf-8 -*-

"""
Run all infrastructure integration tests.
"""

if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_unit_test

    run_unit_test(
        __file__,
        is_folder=True,
    )
