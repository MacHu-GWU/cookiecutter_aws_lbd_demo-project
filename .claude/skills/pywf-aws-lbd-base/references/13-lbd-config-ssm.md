---
description: "How a Lambda function gets its config: config-deploy-<env> writes the whole local Config of a workload environment as JSON to one SSM SecureString parameter, only when it changed; the function knows only the parameter name, CONFIG_SSM_PARAM_NAME, and reads it through the Powertools parameter cache with the aws_lambda runtime; one.config re-reads it so a new config needs no redeploy. Read before adding a config field a function reads, changing how a function loads its config, or running a config task."
---

# Lambda Config in SSM

Seed repo: [`config/config_00_main.py`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/cookiecutter_aws_lbd_demo/config/config_00_main.py), [`one/one_01_config.py`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/cookiecutter_aws_lbd_demo/one/one_01_config.py), [`one/one_03_devops.py`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/cookiecutter_aws_lbd_demo/one/one_03_devops.py).

---

## 1. The local files stay the source of truth

The config is edited only in `config/*.json5` (`07-config-load.md`). Each workload environment has one SSM parameter, `config.ssm_param_name_config` (`/<project>-<env>/config`), that holds a copy: the whole merged `Config` as JSON, `-secret` values included. So a function sees exactly the `Config` the developer sees, nested fields included, and no setting needs its own environment variable.

---

## 2. Deploying the copy

`mise run config-deploy-<env>` (`config-deploy-all` for every workload), `one.deploy_config()`:

- **Only when it changed:** `put_parameter_if_changed` of `simple_aws_ssm_parameter_store` writes only when the parameter is missing or its value differs. An unchanged config writes nothing and does not use up one of the 100 versions SSM keeps, so every `cdk-up` can deploy it safely.
- **`SecureString`,** because the `-secret` values are in it; tier `Intelligent-Tiering`, which turns advanced (8 KB) only when the value outgrows 4 KB. A unit test keeps each environment's JSON under 3000 bytes as an early warning.
- **boto3, not the infrastructure code,** so no value ends up in a template.
- It prints `created`, `updated` (with the version change), or `unchanged`, and the console URL of the parameter.
- `mise run config-delete-<env>` / `config-delete-all` delete it, and print `deleted` or `not found`. Destroying the stacks does not delete it.

---

## 3. Reading it in a function

- The runtime `aws_lambda` (`02-runtime.md`) is detected by `AWS_LAMBDA_FUNCTION_NAME`, which Lambda always sets.
- Every function gets the environment variable `CONFIG_SSM_PARAM_NAME`, the parameter name, plus `ENV_NAME`. No other config goes into environment variables.
- `Config.load` on `aws_lambda` calls `Config.load_from_ssm(name)`: Powertools `parameters.get_parameter(name, decrypt=True, max_age=CONFIG_MAX_AGE)`. While the JSON is unchanged it returns the same `Config` object, so its cached names are not rebuilt.
- `one.config` is a plain property on `aws_lambda` (`08-one-singleton.md`): every access goes through the cache, so a config deployed with `config-deploy-<env>` reaches running functions within `CONFIG_MAX_AGE` seconds, with no redeploy. Locally it loads the files once.
- The execution role needs `ssm:GetParameter` on that one parameter. The parameter is encrypted with the AWS managed key `aws/ssm`, whose key policy already lets every principal of the account decrypt through SSM, so no KMS permission is needed.

> **Open question:** how long `CONFIG_MAX_AGE` should be, and whether a function should force a fresh read at the start of an invocation, are still being decided. Today it is 300 seconds, read lazily on first access to `one.config`.

---

## 4. Testing

The config tests write the parameter to moto, set `CONFIG_SSM_PARAM_NAME`, load with `runtime_name="aws_lambda"`, and check the result equals the local `Config`; `parameters.clear_caches()` stands in for the cache expiring. The deploy test runs created, unchanged, updated, deleted, and not found against moto.
