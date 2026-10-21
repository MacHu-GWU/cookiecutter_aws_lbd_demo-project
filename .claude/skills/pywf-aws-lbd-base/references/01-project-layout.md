---
description: "The general modules of the package and the root files they read, in dependency order: runtime, env, config, the boto session, and the one singleton, plus paths, .env, and the config folder. Read when looking for where a general concern lives, or deciding where a new one goes."
---

# Project Layout

---

## 1. The general modules, in dependency order

| Module | Holds |
| :--- | :--- |
| `<package_name>/runtime.py` | where the code runs |
| `<package_name>/env.py` | which environment it targets |
| `<package_name>/config/` | the settings of one environment: the model, the names, the loading |
| `<package_name>/one/one_02_boto_ses.py` | the boto session of the current environment |
| `<package_name>/one/` | `one`, the single entry point to all of the above |
| `<package_name>/paths.py` | `path_enum`, every path of the repo, such as `path_enum.dir_config` |

Each module may use the ones above it, never the ones below.

---

## 2. Root files they read

| Path | Holds | Committed |
| :--- | :--- | :--- |
| `config/config-shared.json5`, `config/config-<env>.json5` | config values | yes |
| `config/config-shared-secret.json5`, `config/config-<env>-secret.json5` | secret config values, such as the account ID | no, git-ignored |
| `config/example/` | the shape of every config file, `*.json5.example` | yes |
| `.env` | personal variables: `ENV_NAME`, `AWS_PROFILE_FOR_<ENV>` | no, git-ignored |
| `.env.example` | the variables `.env` needs, with placeholder values | yes |

mise loads `.env` for every task. Seed repo: [`.env.example`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/blob/0.2.1/.env.example), [`config/`](https://github.com/MacHu-GWU/cookiecutter_aws_lbd_demo-project/tree/0.2.1/config).

---

## 3. Tests

- `tests/` (`mise run cov`): unit tests, no AWS call. `tests/conftest.py` forces the local runtime and `ENV_NAME=dev`, points `path_enum.dir_config` at a copy of the committed config files plus fake `-secret` files, and gives a `config` fixture with fixed values.
- `tests_int/` (`mise run int-test`): integration tests against what is deployed in `ENV_NAME`. They read AWS, so ask the user's yes before relying on them.
