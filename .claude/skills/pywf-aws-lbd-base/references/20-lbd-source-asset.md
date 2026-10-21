---
description: "How the function code ships: mise run lambda-source-build copies a whitelist of the package's files into build/lambda/source/build/, the Lambda stack deploys it with Code.from_asset, and an unchanged folder hashes the same on any machine, so nothing is redeployed; the include / exclude constants and their pattern rules, the tests that keep the hash stable, and cdk-gc for old assets. Read before changing which files are deployed, how the source is built, or when a deploy updates a function that did not change."
---

# Lambda Source Asset

Seed repo: [`one/one_03_devops.py`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/cookiecutter_aws_lbd_demo/one/one_03_devops.py) (`build_lambda_source`), [`constants.py`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/cookiecutter_aws_lbd_demo/constants.py), [the tests](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/tests/one/test_one_one_03_devops.py).

---

## 1. Built by copying, deployed as a CDK asset

- `mise run lambda-source-build` wipes `build/lambda/source/build/`, then copies the files of `<package_name>/` that match `LAMBDA_SOURCE_INCLUDE` and not `LAMBDA_SOURCE_EXCLUDE` into `build/lambda/source/build/<package_name>/` (`copy_source_for_lambda_deployment` of `aws_lbd_art_builder_core`).
- Every function of the Lambda stack uses `Code.from_asset` of that folder (`14-cdk-layout.md`). CDK zips it and uploads it to the bootstrap bucket of the workload account, keyed by its hash; environments with the same code share one object.
- Every `cdk-*` task depends on `lambda-source-build` (`17-cdk-mise-tasks.md`), so the folder is always fresh before synth. There is no separate upload step and no S3 key to pass around.
- No CDK bundling: it would run the build inside synth, need a hand-written `ILocalBundling` in Python, and tie build to deploy.

---

## 2. Unchanged code, unchanged template

CDK's asset hash covers each file's relative path and content, not its time stamp or permissions. Copying keeps that true across machines; installing the package would not (`pip install --target` writes absolute paths into `dist-info/direct_url.json`). So an unchanged code base produces an unchanged template, and `cdk deploy` reports no changes instead of updating every function.

---

## 3. What is copied

- `LAMBDA_SOURCE_INCLUDE` is a whitelist, `["*.py"]` by default. Add a pattern such as `"*.json"` when a function reads data files next to its code.
- `LAMBDA_SOURCE_EXCLUDE` drops dev-only folders: `tests/`, `docs/`, `vendor/`, and the CDK code, which needs `aws_cdk` (`10-lbd-dependencies.md`).
- Patterns go through `PurePath.match`, anchored at the end of the path relative to the package, and `*` matches one path part. So `"tests/*"` drops `tests/a.py` but not `tests/sub/a.py`: keep those folders flat, or add one pattern per depth (`"cdk/*"`, `"cdk/*/*"`).

---

## 4. Tests

- Two builds into different folders, with a file's time stamp changed in between, have the same `aws_cdk.FileSystem.fingerprint`.
- Every built file matches `LAMBDA_SOURCE_INCLUDE`, none is under an excluded folder at any depth, and a stale file from an earlier build is gone.
- `<package_name>.lambda_function` imports in a subprocess whose path has the built folder and the venv's packages only, so no deployed module needs a file that was left out.

---

## 5. Old assets

Each code change leaves its old zip in the bootstrap bucket. `mise run cdk-gc-<env>` lists the ones no deployed stack uses (`--action=print`). It scans every stack of the account and region, so environments sharing an account are safe. Deleting them is a separate run with `--action=full`, after the user's yes.
