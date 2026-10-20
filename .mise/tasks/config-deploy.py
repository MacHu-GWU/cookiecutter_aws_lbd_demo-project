# -*- coding: utf-8 -*-

"""
Write the config of the current environment (ENV_NAME) to SSM Parameter Store.
"""

from cookiecutter_aws_lbd_demo.one.api import one

if __name__ == "__main__":
    one.deploy_config()
