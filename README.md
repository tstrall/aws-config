# aws-config

This is the only part of the **AWS deployment framework designed to be forked and modified.**  
**You control it, and your fork does not need to be public.**

This repo is designed to declare everything that can be deployed — but actual deployment is controlled separately.

## Repository Structure

```
.
├── account_environments/
│   ├── dev.json           # Defines the environment binding for the 'dev' OU
│   └── prod.json          # Defines the environment binding for the 'prod' OU
├── aws-config/
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

Each AWS account must define its environment binding before any configuration can be deployed. This is done by setting the `/aws-config/environment` parameter in Systems Manager Parameter Store.

Each file in `account_environments/` corresponds to an Organizational Unit (OU) and defines how accounts within that OU should be configured and constrained.

### Manual Setup

1. Open the appropriate file:
   - `account_environments/dev.json`
   - `account_environments/prod.json`

2. In the AWS Console for the target account:
   - Go to Systems Manager → Parameter Store → Create parameter
   - Name: `/aws-config/environment`
   - Type: `String`
   - Value: Paste the full JSON blob from the file

This must be completed before deployment or validation can occur.

### Scripted Setup

To define the environment parameter from the CLI and ensure it is properly protected:

```bash
python3 scripts/define_account_environment.py --env dev
```

- Loads from `account_environments/dev.json`
- Writes to `/aws-config/environment` in the target AWS account
- Automatically applies a restrictive IAM policy to prevent unauthorized changes

Only the designated administrative role (e.g. `OrgAdmin`) will be allowed to modify or delete the parameter. All other roles, including account root, will be denied.

## How Configuration Becomes Active

This repository defines configuration that can be deployed — but it is not automatically active.  
Only values that are explicitly published to AWS Systems Manager Parameter Store (via approved scripts or manual steps) will be used at deploy time.

This two-step process ensures that:

- You can version and review changes in Git before applying them
- Only declared environments and components can be deployed
- Control over this repository — and how it is published to AWS — defines the allowed architecture for your environment

In other words: this repo sets the rules, but AWS Parameter Store enforces them.


It works together with:
- [`aws-deployment-guide`](https://github.com/tstrall/aws-deployment-guide) for orchestration and walkthroughs
- [`aws-iac`](https://github.com/tstrall/aws-iac) for shared Terraform-based infrastructure components
- [`aws-lambda`](https://github.com/tstrall/aws-lambda) for optional Lambda handlers and tools

Each AWS account is explicitly bound to one environment by setting a single JSON parameter in AWS Systems Manager: `/aws-config/environment`. All other configuration is defined declaratively under this repo and selected at runtime based on that binding.

## Deploying a Config Instance

Once an environment is defined, you may deploy a configuration instance by referencing its logical path under the environment tree.

```bash
python3 scripts/deploy_config.py --config serverless-site/strall-com
```

- Resolves the current environment and repo via `/aws-config/environment`
- Clones the configured Git repo and branch
- Loads and validates the referenced config JSON
- (Currently performs dry run; deploy logic can be extended)

## Roles and Separation of Responsibility

This system is designed to enforce strict separation between:

- **Defining an environment** — done once per account by administrators
- **Deploying a config** — done routinely by developers, CI/CD, or automation tools

Environment binding must be declared before any deployment is possible, and cannot be overwritten accidentally. This protects production environments while enabling flexibility in development.

## Validation Scripts

These help verify correct setup before attempting deployment.

### Validate the environment parameter

```bash
python3 scripts/validate_account_environment.py
```

- Loads the current value of `/aws-config/environment` from the AWS account
- Determines the environment name from the `name` field
- Compares it to `account_environments/<name>.json`

### Validate a config instance

```bash
python3 scripts/validate_config.py --config serverless-site/strall-com
```

Checks that the referenced config exists and is valid JSON.

## Security and Governance

- All deployments are gated by the `/aws-config/environment` parameter
- This parameter is protected by a resource policy and can only be written by an admin role
- Environment validation and config deployment are separate, scriptable processes
- No configuration is applied unless committed to Git and declared under an approved environment

## Customization

- Fork this repository to define your own environments and constraints
- Update `account_environments/` to define new OUs and controls
- Create new deployable configs under `aws-config/dev/` or `aws-config/prod/`

## License

[Apache 2.0 License](LICENSE)
