# `define_account_environment.py` – Define Environment Parameter

This script publishes a JSON environment binding to AWS Systems Manager Parameter Store.  
It must be run once per AWS account to define which environment it belongs to.

This is a required step before any configuration or infrastructure can be deployed using the **Adage** deployment framework.

---

## 📌 What It Does

- Loads a file like `account_environments/dev.json`
- Publishes it as a single string to SSM Parameter Store
- Default parameter path: `/iac/environment`
- You can override the prefix with `IAC_PREFIX`, or override the full name with `--param-name`

---

## ✅ Usage

```bash
AWS_PROFILE=dev-iac python scripts/define_account_environment.py --env dev
```

This publishes `account_environments/dev.json` to:

```
/iac/environment
```

---

## 🔀 Optional Overrides

### Use a different file path:

```bash
--path ./my/custom/env/defs
```

### Override the default prefix (`/iac`) using an environment variable:

```bash
IAC_PREFIX=/karma AWS_PROFILE=prod-iac python scripts/define_account_environment.py --env prod
```

This will publish to:

```
/karma/environment
```

*(Note: `IAC_PREFIX` is evaluated at script startup time)*

### Manually override the full parameter path:

```bash
--param-name /alt/structure/environment
```

This skips prefix logic and writes directly to the given name.

---

## 🧾 Example JSON (Environment Definition)

```json
{
  "name": "dev",
  "config_repo": "usekarma/aws-config",
  "config_branch": "main",
  "nicknames": ["dev", "sandbox"],
  "tags": {
    "owner": "platform-team"
  }
}
```

This will be stored as a **single string parameter** in Parameter Store.

---

## 🛡️ Best Practices

- Lock down the environment parameter (`/iac/environment`) via IAM in production
- Use Git history to manage and review changes to `account_environments/*.json`
- Avoid editing the parameter manually in the AWS Console

---

## Related Scripts

- [`validate_account_environment.py`](validate_account_environment.py) – checks if the parameter is set and valid
- [`deploy_config.py`](deploy_config.py) – uses this parameter to determine what config to deploy
