# aws-config

This is the only part of the **AWS deployment framework designed to be forked and modified.**  
**You control it, and your fork does not need to be public.**

This repo is designed to declare everything that can be deployed — but actual deployment is controlled separately.

It works together with:
- [`aws-deployment-guide`](https://github.com/tstrall/aws-deployment-guide) for orchestration and walkthroughs
- [`aws-iac`](https://github.com/tstrall/aws-iac) for shared Terraform-based infrastructure components
- [`aws-lambda`](https://github.com/tstrall/aws-lambda) for optional Lambda handlers and tools

## Repository Structure

```
.
├── account_environments/
│   ├── dev.json           # Defines the environment binding for the 'dev' OU
│   └── prod.json          # Defines the environment binding for the 'prod' OU
├── iac-config/
│   ├── dev/
│   │   └── serverless-site/
│   │       └── strall-com/
│   │           └── config.json
│   ├── prod/
│   │   └── ...
├── scripts/
│   ├── define_account_environment.py
│   ├── deploy_config.py
│   ├── validate_account_environment.py
│   └── validate_config.py
```

## Environment Setup

Each AWS account must define its environment binding before any configuration can be deployed. This is done by setting the `/iac-config/environment` parameter in Systems Manager Parameter Store.

Each file in `account_environments/` corresponds to an Organizational Unit (OU) and defines how accounts within that OU should be configured and constrained.

### Manual Setup

1. Open the appropriate file:
   - `account_environments/dev.json`
   - `account_environments/prod.json`

2. In the AWS Console for the target account:
   - Go to **Systems Manager → Parameter Store → Create parameter**
   - Name: `/iac-config/environment`
   - Type: `String`
   - Tier: `Advanced` (required for future protection)
   - Value: Paste the full JSON blob from the file

This must be completed before deployment or validation can occur.

### Scripted Setup

To define the environment parameter from the CLI:

```bash
AWS_PROFILE=dev-core python scripts/define_account_environment.py --env dev
AWS_PROFILE=prod-core python scripts/define_account_environment.py --env prod
```

- Loads from `account_environments/<env>.json`
- Writes to `/iac-config/environment` in the target AWS account

## How Configuration Becomes Active

This repository defines configuration that can be deployed — but it is not automatically active.  
Only values that are explicitly published to AWS Systems Manager Parameter Store (via approved scripts or manual steps) will be used at deploy time.

This two-step process ensures that:

- You can version and review changes in Git before applying them
- Only declared environments and components can be deployed
- Control over this repository — and how it is published to AWS — defines the allowed architecture for your environment

In other words: this repo sets the rules, but AWS Parameter Store enforces them.

Each AWS account is explicitly bound to one environment by setting a single JSON parameter in AWS Systems Manager: `/iac-config/environment`. All other configuration is defined declaratively under this repo and selected at runtime based on that binding.

## Deploying a Config Instance

Once an environment is defined, you may deploy a configuration instance by referencing its logical path under the environment tree.

```bash
AWS_PROFILE=dev-core python scripts/deploy_config.py --config serverless-site/strall-com
```

- Resolves the current environment and repo via `/iac-config/environment`
- Clones the configured Git repo and branch
- Loads and validates the referenced config JSON
- (Currently performs dry run; deploy logic can be extended)

## Roles and Separation of Responsibility

This system is designed to enforce strict separation between:

- **Defining an environment** — done once per account by administrators
- **Deploying a config** — done routinely by developers, CI/CD, or automation tools

Environment binding must be declared before any deployment is possible. Protection is enforced via IAM, ensuring that production environments cannot be overwritten accidentally.

## Validation Scripts

These help verify correct setup before attempting deployment.

### Validate the environment parameter

```bash
AWS_PROFILE=dev-core python scripts/validate_account_environment.py
```

- Loads the current value of `/iac-config/environment` from the AWS account
- Determines the environment name from the `name` field
- Compares it to `account_environments/<name>.json`

### Validate a config instance

```bash
python scripts/validate_config.py --config serverless-site/strall-com
```

Checks that the referenced config exists and is valid JSON.

## Security and Governance

- All deployments are gated by the `/iac-config/environment` parameter
- The parameter must be set manually or via script using proper AWS credentials
- IAM policies in the core account should restrict `ssm:PutParameter` to trusted roles only
- No configuration is applied unless committed to Git and declared under an approved environment

## Customization

- Fork this repository to define your own environments and constraints
- Update `account_environments/` to define new OUs and controls
- Create new deployable configs under `iac-config/dev/` or `iac-config/prod/`

## Developer Setup: AWS CLI Profiles

This project assumes you are using named AWS CLI profiles to authenticate into different AWS accounts.

To set up a profile for a core account (e.g. `dev-core` or `prod-core`), you can use either IAM access keys or SSO.

### Option 1: Configure a profile using access keys

```bash
aws configure --profile dev-core
```

Follow the prompts to enter your access key, secret, and region (usually `us-east-1`).

### Option 2: Configure a profile using SSO (AWS IAM Identity Center)

```bash
aws configure sso --profile dev-core
```

This requires you to know your SSO start URL and role name.

---

Once a profile is configured, you can run framework scripts with:

```bash
AWS_PROFILE=dev-core python scripts/define_account_environment.py --env dev
```

Each script supports `AWS_PROFILE` to target the appropriate account securely and explicitly.

## License

[Apache 2.0 License](LICENSE)
