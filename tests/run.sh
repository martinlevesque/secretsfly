
cp ./db/self-secrets-manager-current.db ./db/self-secrets-manager-test.db
export ENV=test

python -m pytest
