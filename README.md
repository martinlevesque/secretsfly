
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

### UI ability to generate a service token for a project: read/write

### UI create a new secret on a project

### UI delete a secret on a project

### API list secrets using a service token+master key


