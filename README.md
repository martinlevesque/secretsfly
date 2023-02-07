
# secretsfly

secretsfly is an easy to use, simple, with low number of dependencies, and fast secrets management tool with a focus on self-hosting and security.
Don't let third party manage your secrets, keep them yourself and avoid the risk of data leaks.

## Environment variables

- `AVAILABLE_ENVIRONMENTS`: Default: prod. Comma separated list of environments available globally.
- `ADMIN_MASTER_KEY_EXPIRATION`: Default: 300 (in seconds). Master key timeout, after which the master key is deleted from the session.
- `NB_MINUTES_DECRYPTED_BEFORE_REDIRECT`: Default: 5. Number of minutes before redirecting to the encrypted secrets page from the decrypted page.

## How it works

- Secrets are encrypted by a master key per project. When storing secrets in the main database, the master key is temporarily stored in the session and needs to be kept secret by the end user.
- The master key is stored in the session and is deleted after a certain amount of time (see `ADMIN_MASTER_KEY_EXPIRATION`).
- The master key is generated by the user and is never stored on the application database. Therefore in a scenario where the secrets database is stolen, the secrets are still safe and cannot be decrypted.
- Secrets follow a project hierarchy - secrets coming from inherited projects are also available to the child projects.

##

https://keystone.sh/docs/guides/use-secrets-in-your-project/

https://www.doppler.com/

import os
import subprocess

os.environ["TTEST"] = "testtt"

subprocess.call('env > out.txt', shell=True)

## todo

### [DONE] 0. test status API

### [DONE] UI ability to list projects

### [DONE] UI ability to create a project

### [DONE] UI ability to generate a master key for a root project

### [DONE] UI store master key in session

### [DONE] have default environments global created on startup

### [DONE] use a proper logger with log levels

### [DONE] UI set time to live of session to ~1 hour

### [DONE] UI ability to generate a service token for a project+environment: read/write

### [DONE] UI list service tokens for a project+environment

### [DONE] UI display project environments

### [DONE] UI list secrets without values

### [DONE] UI listing secret for a given environment (no value)

### [DONE] UI listing secret for a given environment (decrypted values)

### [DONE] UI create a new secret on a project, with *version*

### [DONE] UI on decrypted secrets page, redirect after few minutes

### [DONE] Test store large secret

### [DONE] UI delete a secret on a project

### replace master key storage in session

### API `list secrets using a service token+master key

### define project parent of a given project

### retrieve parent secrets if any, one master key per main project

### [DONE] validation of master key - it should not contain :


