# -*- coding: utf-8 -*-

from cookiecutter_aws_lbd_demo.cdk.mise_tasks import BEGIN_MARKER
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import END_MARKER
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import CDK_ACTIONS
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import validate_stacks
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import StackTarget
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import get_stack_targets
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import get_task_name
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import render_cdk_tasks
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import render_project_cdk_tasks
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import print_cdk_stack_urls
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import replace_cdk_tasks_block
from cookiecutter_aws_lbd_demo.cdk.mise_tasks import update_mise_toml

import pytest

import tomllib

from cookiecutter_aws_lbd_demo.paths import path_enum
from cookiecutter_aws_lbd_demo.cdk import mise_tasks


@pytest.mark.parametrize(
    "stacks",
    [
        ["all"],
        ["my_b", "my-b"],
    ],
)
def test_validate_stacks_error(stacks: list[str]):
    with pytest.raises(ValueError):
        validate_stacks(stacks)


def test_get_stack_targets():
    targets = get_stack_targets("prd")
    assert list(targets) == ["infra", "lbd"]
    target = targets["infra"]
    assert target.construct_id == "cookiecutter-aws-lbd-demo-prd-infra"
    assert "stackinfo?filteringText=cookiecutter-aws-lbd-demo-prd-infra&" in (
        target.console_url
    )


def test_get_task_name():
    assert get_task_name("up", "dev", "all") == "cdk-up-dev-all"
    assert get_task_name("up", "dev", "my-b") == "cdk-up-dev-my-b-stack"


def _target(construct_id: str) -> StackTarget:
    return StackTarget(construct_id=construct_id, console_url=f"https://{construct_id}")


def test_render_cdk_tasks():
    """
    The block is valid TOML: per environment, ``config-deploy-<env>``,
    ``config-delete-<env>``, ``lambda-layer-check-<env>`` and ``cdk-gc-<env>``, then four tasks for ``all`` and
    four per stack, each run in ``cdk/`` with ``ENV_NAME`` set; then
    ``config-deploy-all`` and ``config-delete-all``. A task prints the console URL of exactly the
    stacks it acts on, then the cdk command, then runs it.
    """
    block = render_cdk_tasks(
        {
            "dev": {"a": _target("p-dev-a"), "my_b": _target("p-dev-my-b")},
            "prd": {"a": _target("p-prd-a"), "my_b": _target("p-prd-my-b")},
        }
    )
    assert block.startswith(BEGIN_MARKER)
    assert block.endswith(END_MARKER)
    tasks = tomllib.loads(block)["tasks"]
    assert len(tasks) == 2 * (4 + 3 * len(CDK_ACTIONS)) + 2
    for name, task in tasks.items():
        if not name.startswith(("config-", "lambda-layer-check-")):
            assert task["dir"] == "cdk"

    # fmt: off
    task = tasks["config-deploy-prd"]
    assert task["env"] == {"ENV_NAME": "prd"}
    assert task["run"] == ".venv/bin/python .mise/tasks/config-deploy.py"

    task = tasks["config-delete-dev"]
    assert task["env"] == {"ENV_NAME": "dev"}
    assert task["run"] == ".venv/bin/python .mise/tasks/config-delete.py"

    assert tasks["config-deploy-all"]["depends"] == ["config-deploy-dev", "config-deploy-prd"]
    assert tasks["config-delete-all"]["depends"] == ["config-delete-dev", "config-delete-prd"]

    task = tasks["cdk-gc-dev"]
    assert task["depends"] == ["inst", "lambda-source-build"]
    assert task["run"].splitlines()[-1] == "cdk gc --unstable=gc --action=print --profile {{env.AWS_PROFILE_FOR_DEV}}"

    # every cdk task deploys the built source; up also deploys the config
    assert tasks["cdk-synth-dev-all"]["depends"] == ["inst", "lambda-source-build"]
    assert tasks["cdk-down-dev-a-stack"]["depends"] == ["inst", "lambda-source-build"]
    assert tasks["cdk-up-prd-my-b-stack"]["depends"] == ["inst", "lambda-source-build", "lambda-layer-check-prd", "config-deploy-prd"]
    task = tasks["lambda-layer-check-dev"]
    assert task["env"] == {"ENV_NAME": "dev"}
    assert task["run"] == ".venv/bin/python .mise/tasks/lambda-layer-check.py"
    # fmt: on

    # fmt: off
    task = tasks["cdk-synth-dev-all"]
    assert task["env"] == {"ENV_NAME": "dev"}
    assert task["run"].splitlines() == [
        "echo '--- CloudFormation console ---'",
        "echo 'p-dev-a: https://p-dev-a'",
        "echo 'p-dev-my-b: https://p-dev-my-b'",
        "echo '--- Run command ---'",
        "echo 'cdk synth'",
        "cdk synth",
    ]

    task = tasks["cdk-up-prd-all"]
    assert task["env"] == {"ENV_NAME": "prd"}
    assert task["run"].splitlines()[-1] == "cdk deploy --all --require-approval never --profile {{env.AWS_PROFILE_FOR_PRD}}"

    task = tasks["cdk-plan-dev-my-b-stack"]
    assert task["run"].splitlines() == [
        "echo '--- CloudFormation console ---'",
        "echo 'p-dev-my-b: https://p-dev-my-b'",
        "echo '--- Run command ---'",
        "echo 'cdk diff p-dev-my-b --exclusively --method auto --profile {{env.AWS_PROFILE_FOR_DEV}}'",
        "cdk diff p-dev-my-b --exclusively --method auto --profile {{env.AWS_PROFILE_FOR_DEV}}",
    ]

    task = tasks["cdk-down-prd-a-stack"]
    assert task["run"].splitlines()[-1] == "cdk destroy p-prd-a --exclusively --force --profile {{env.AWS_PROFILE_FOR_PRD}}"
    # fmt: on


def test_print_cdk_stack_urls(monkeypatch, capsys):
    """
    A failing environment prints an error line instead of raising, and the
    other environments are still printed.
    """
    get_stack_targets_ = mise_tasks.get_stack_targets

    def get_stack_targets(env_name: str):
        if env_name == "tst":
            raise FileNotFoundError("config-tst.json5")
        return get_stack_targets_(env_name)

    monkeypatch.setattr(mise_tasks, "get_stack_targets", get_stack_targets)
    print_cdk_stack_urls()
    out = capsys.readouterr().out
    assert (
        "--- tst ---\nERROR: cannot work out the stacks of 'tst': FileNotFoundError"
        in out
    )
    assert "cookiecutter-aws-lbd-demo-dev-infra: https://" in out
    assert "cookiecutter-aws-lbd-demo-prd-lbd: https://" in out


@pytest.mark.parametrize(
    "text",
    [
        "no markers",
        f"{END_MARKER}\n{BEGIN_MARKER}\n",
    ],
)
def test_replace_cdk_tasks_block_error(text: str):
    with pytest.raises(ValueError):
        replace_cdk_tasks_block(text, "")


def test_update_mise_toml(tmp_path):
    path = tmp_path / "mise.toml"
    path.write_text(f"[env]\n\n{BEGIN_MARKER}\nold\n{END_MARKER}\n# tail\n")
    block = render_cdk_tasks({"dev": {"a": _target("p-dev-a")}})
    assert update_mise_toml(path, block) is True
    text = path.read_text()
    assert text.startswith("[env]\n\n")
    assert text.endswith(f"{END_MARKER}\n# tail\n")
    assert "old" not in text
    assert update_mise_toml(path, block) is False


def test_mise_toml_is_up_to_date():
    """
    ``mise.toml`` holds the tasks of exactly the stacks of StackCtxEnum in every
    environment. If this fails, run ``mise run cdk-gen-tasks``.
    """
    text = path_enum.path_mise_toml.read_text(encoding="utf-8")
    assert render_project_cdk_tasks() in text


if __name__ == "__main__":
    from cookiecutter_aws_lbd_demo.tests import run_cov_test

    run_cov_test(
        __file__,
        "cookiecutter_aws_lbd_demo.cdk.mise_tasks",
        preview=False,
    )
