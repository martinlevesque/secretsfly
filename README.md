
https://keystone.sh/docs/guides/use-secrets-in-your-project/

https://www.doppler.com/

import os
import subprocess

os.environ["TTEST"] = "testtt"

subprocess.call('env > out.txt', shell=True)

## todo

### [DONE] 0. test status API

### UI ability to list projects

### UI ability to create a project

### UI ability to generate a master key for a root project

### UI ability to generate a service token for a project: read/write

### UI create a new secret on a project

### UI delete a secret on a project

### API list secrets using a service token+master key


