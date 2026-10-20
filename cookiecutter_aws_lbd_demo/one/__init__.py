# -*- coding: utf-8 -*-

"""
The ``one`` singleton. Import from :mod:`cookiecutter_aws_lbd_demo.one.api`::

    from cookiecutter_aws_lbd_demo.one.api import one

    one.config          # the Config of the current environment
    one.bsm             # the boto session of the current environment
    one.bsm_devops      # the boto session of the DEVOPS account (local only)
"""
