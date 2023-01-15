
## Environment variables

- `AVAILABLE_ENVIRONMENTS`: Default: prod. Comma separated list of environments available globally.
- `ADMIN_MASTER_KEY_EXPIRATION`: Default: 300 (in seconds). Master key timeout, after which the master key is deleted from the session.

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

### UI create a new secret on a project, with *version*

### Test store large secret

### UI delete a secret on a project

### API `list secrets using a service tok`en+master key

### [DONE] validation of master key - it should not contain :


