
# secretsfly

secretsfly is an easy to use, simple, with low number of dependencies, and fast secrets management tool with a focus on self-hosting and security.
Don't let third party manage your secrets, keep them yourself and avoid the risk of data leaks.

## Environment variables

- `AVAILABLE_ENVIRONMENTS`: Default: prod. Comma separated list of environments available globally.
- `ADMIN_MASTER_KEY_EXPIRATION`: Default: 300 (in seconds). Master key timeout, after which the master key is deleted from the session.
- `NB_MINUTES_DECRYPTED_BEFORE_REDIRECT`: Default: 5. Number of minutes before redirecting to the encrypted secrets page from the decrypted page.
- `ADMIN_BASIC_AUTH_USERNAME`: Username for the admin UI. Basic auth is enabled if this variable is set.
- `ADMIN_BASIC_AUTH_PASSWORD`: Password for the admin UI.

## Secrets mechanism

- Secrets are encrypted by a master key per project. When storing secrets in the main database, the master key is temporarily stored in the session and needs to be kept secret by the end user.
- The master key is temporarily stored in memory and is deleted after a certain amount of time (see `ADMIN_MASTER_KEY_EXPIRATION`).
- The master key is generated by the user and is never stored on the application database. Therefore in a scenario where the secrets database is stolen, the secrets are still safe and cannot be decrypted.
- Secrets are encrypted using AES-256-GCM.

## Features

- Secrets are grouped per project and per environment.
- Secrets follow a project hierarchy - secrets coming from inherited projects are also available to the child projects.
- Cloud agnostic rather than multi-cloud support as opposed to Hashicorp Vault, and similar tools.

##

https://keystone.sh/docs/guides/use-secrets-in-your-project/

https://www.doppler.com/

import os
import subprocess

os.environ["TTEST"] = "testtt"

subprocess.call('env > out.txt', shell=True)

## Related Projects

### Vault

https://www.datocms-assets.com/2885/1597082390-vault-com-security-whitepaper-v2-digital.pdf

### Doppler

comparing doppler vs vault:
https://www.doppler.com/blog/doppler-vs-hashicorp-vault

- vault is key-value
- doppler is grouping secrets in projects
- to test - example with github, sync secrets?

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

### [DONE] API `list secrets using a service token+master key

### [DONE] validation of master key - it should not contain :

### [DONE] replace master key storage in session

### [DONE] thread to auto seal master key

### [DONE] define project parent of a given project

### [DONE] admin UI, retrieve parent secrets if any, one master key per main project

### [DONE] API secrets, retrieve parent secrets if any, one master key per main project

### [DONE] display flash if any

### [DONE] show if master key unsealed

### [DONE] bug - list selectable projects in new is not correct

### [DONE] button to seal unsealed master key

### [DONE] detect missing secret comparing other environments

### [DONE] parameter to protect the admin UI

### [DONE] improve base UI

### [DONE] have home

### (rotate) reencrypt feature (previous master key + new master key)
   should do a get
   generate a new master key and provide existing one
   reencrypt all secrets with new master key in TX
   list service tokens to regenerate

### performance analysis (benchmark folder)
#### on local
#### on fly

### possible read master key?

https://stackoverflow.com/questions/12977179/reading-living-process-memory-without-interrupting-it
https://techryptic.github.io/2018/04/07/Using-PTRACE-to-Inspect-&-Alter-Memory/




