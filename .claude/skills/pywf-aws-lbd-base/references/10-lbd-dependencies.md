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
| `dev`, `test`, `doc`, `mise` extras | build, deploy, and test tools: CDK, `cdk-mate`, `json5`, the layer builder, the layer-version helpers (`simple-aws-lambda`), `moto` | no |

Every package in `[project] dependencies` makes the layer bigger and every cold start slower. Put a package there only if code inside a function imports it.

---

## 2. Importing `<package_name>` inside Lambda

The function's code is the whole package (minus dev-only folders), and only the layer is installed next to it. So:

- A module a function imports must import only `[project] dependencies` at module level.
- A dev-only library is imported inside the function body that needs it, or through `lazy_imports.py`, which falls back to a `MissingDependency` that raises only when used.
- `one` is imported in every function, so every `one` mixin must follow this (`08-one-singleton.md`): the CDK mixin imports `aws_cdk` inside its properties; the deploy mixin imports its tools through `lazy_imports.py`, which tries them at load time and leaves a `MissingDependency` in Lambda, where they are not installed.
- A test imports every handler from the built source folder, so a module left out of the copy fails in `mise run cov`, not in AWS. It runs with the venv's packages, so it does not catch a dev-only import at module level: keep to the two rules above.

---

## 3. No package metadata

The deployed code is the source files, not an installed package: there is no `dist-info`, so `importlib.metadata` raises inside Lambda. Code that runs in a function never reads metadata. The version of the deployed code is the `PACKAGE_VERSION` environment variable, which the Lambda stack sets from `[project].version` of `pyproject.toml` at synth time; `pyproject.toml` is the only place the version is written.
