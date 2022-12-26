
https://keystone.sh/docs/guides/use-secrets-in-your-project/

https://www.doppler.com/

import os
import subprocess

os.environ["TTEST"] = "testtt"

subprocess.call('env > out.txt', shell=True)

## todo

### 0. test status API

### 1. UI ability to create a project

### 2. UI ability to list projects

### 3. UI ability to generate a master key for a root project

### 4. UI ability to generate a service token for a project: read/write

### 5. UI create a new secret on a project

### 6. UI delete a secret on a project

### 7. API list secrets using a service token+master key


