# -*- coding: utf-8 -*-

"""
Copy the package source files to build/lambda/source/build/ for Code.from_asset.
"""

from cookiecutter_aws_lbd_demo.one.api import one

if __name__ == "__main__":
    one.build_lambda_source()
