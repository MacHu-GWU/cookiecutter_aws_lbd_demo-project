# -*- coding: utf-8 -*-

"""
Rewrite QUICK_LINKS.md, the console URL of every AWS resource, from the config.
"""

from cookiecutter_aws_lbd_demo.paths import path_enum
from cookiecutter_aws_lbd_demo.quick_links import write_quick_links


def main():
    if write_quick_links():
        print(f"Updated {path_enum.path_quick_links_md}")
    else:
        print(f"{path_enum.path_quick_links_md} is already up to date")


if __name__ == "__main__":
    main()
