
cp ./db/secretsfly-current.db ./db/secretsfly-test.db
export ENV=test

python -m pytest
