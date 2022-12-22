
https://keystone.sh/docs/guides/use-secrets-in-your-project/

https://www.doppler.com/

import os
import subprocess

os.environ["TTEST"] = "testtt"

subprocess.call('env > out.txt', shell=True)
