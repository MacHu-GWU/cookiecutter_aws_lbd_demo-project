---
description: "What may run inside Lambda: the [project] dependencies are exactly the layer, dev-only libraries stay in extras and are imported lazily, importing <package_name> must work with the layer alone, no package metadata at runtime, and the version comes from PACKAGE_VERSION. Read before adding a dependency, importing a library, or reading the package version."
---

# Lambda Dependencies and Imports

Seed repo: [`pyproject.toml`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/pyproject.toml), [`lazy_imports.py`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/cookiecutter_aws_lbd_demo/lazy_imports.py).

---

## 1. Two kinds of dependencies

| Where in `pyproject.toml` | What | In Lambda |
| :--- | :--- | :--- |
| `[project] dependencies` | what the functions need at runtime | yes: the layer is built from exactly this list |
| `dev`, `test`, `doc`, `mise` extras | build, deploy, and test tools: CDK, `cdk-mate`, `json5`, the layer builder, SSM helpers, `moto` | no |

Every package in `[project] dependencies` makes the layer bigger and every cold start slower. Put a package there only if code inside a function imports it.

---

## 2. Importing `<package_name>` inside Lambda

The function's code is the whole package (minus dev-only folders), and only the layer is installed next to it. So:

- A module a function imports must import only `[project] dependencies` at module level.
- A dev-only library is imported inside the function body that needs it, or through `lazy_imports.py`, which falls back to a `MissingDependency` that raises only when used.
- `one` is imported in every function, so every `one` mixin must follow this; the CDK and deploy mixins import their libraries lazily (`08-one-singleton.md`).
- A test imports every handler with only the built source folder on the path, so a violation fails in `mise run cov`, not in AWS.

---

## 3. No package metadata

The deployed code is the source files, not an installed package: there is no `dist-info`, so `importlib.metadata` raises inside Lambda. Code that runs in a function never reads metadata. The version of the deployed code is the `PACKAGE_VERSION` environment variable, which the Lambda stack sets from `[project].version` of `pyproject.toml` at synth time; `pyproject.toml` is the only place the version is written.
