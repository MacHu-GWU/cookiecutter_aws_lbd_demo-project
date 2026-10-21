# Project Guide for AI Assistants

## What this is

A multi-environment AWS Lambda project, deployed with AWS CDK from a developer machine. `README.rst` has the overview, the first-time setup, and the common tasks.

**Load the `pywf-aws-lbd-base` skill (`.claude/skills/pywf-aws-lbd-base/`) before changing anything.** It is the source of truth for the design: environments, config, the `one` singleton, Lambda handlers, the layer, the stacks, the deploy flow, and the recipes for common changes. Read `SKILL.md`, then only the reference that covers the task. If the code and the skill disagree, the code wins: fix the skill or tell the user.

## Tasks

Run everything through `mise run <task>`, never the underlying tool. `mise tasks ls` lists every task. The AWS CLI is not on `PATH`: use `mise exec -- aws ...`.

| Task | Use |
| :--- | :--- |
| `inst` | install the dependencies |
| `format`, `lint`, `cov` | run all three after every change; keep the coverage |
| `cdk-synth-<env>-all`, `cdk-plan-<env>-all` | check the stacks |
| `lambda-layer-build-only`, `lambda-layer-check-<env>` | check the layer |
| `cdk-gen-tasks` | after changing `cdk/mise_tasks.py`, the stacks, or the environments; it rewrites the `<cdk-stack-tasks>` block of `mise.toml` |
| `gen-quick-links` | after changing the config or a URL property; it rewrites `QUICK_LINKS.md` |

## Ask before writing to AWS

A task whose description says "writes to AWS" needs the user's yes first, and one yes covers one step in one environment: `lambda-layer-deploy`, `lambda-layer-cleanup-real-run`, `config-deploy-*`, `config-delete-*`, `cdk-up-*`, `cdk-down-*`, `int-test`. Read-only tasks and `aws ... list/get/describe` can run without asking.

## Working rules

- The user commits. Do not commit unless asked.
- Match the surrounding code: comment density, naming, idiom. Source docstrings say how; the skill says what and why.
- Tests: follow the `if __name__ == "__main__":` pattern of the existing test files. Never assert a value that changes with a deploy (a layer version, an account ID); read it from the config.
- Editing the skill: follow `references/00-authoring.md`, regenerate the index with `python3 .claude/skills/pywf-oss-base/scripts/update_skill_index.py --skill_dir .claude/skills/pywf-aws-lbd-base`, and check with `python3 .claude/skills/pywf-oss-base/scripts/check_skill_family.py --skills_dir .claude/skills --prefix pywf-aws-lbd`.
