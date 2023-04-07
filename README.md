
# secretsfly

secretsfly is an easy to use, minimalist, with low number of dependencies, and fast secrets management tool with a focus on self-hosting and security.
It can also be used as a personal secrets management tool.
Don't let third party manage your secrets, keep them yourself and avoid the risk of data leaks.

## Related Projects and motivation

There are various tools to provide secrets management, such as Hashicorp Vault, Doppler, and others.
secretsfly is by no means a replacement for these tools, but rather a lightweight alternative focusing on self-hosting with
minimal dependencies and ease of maintenance.
Doppler provides significant value in terms of user experience, but it is not open source and master keys are stored in their database,
meaning you have no real control on your encryption keys.
Vault is open source and allows you to store your master keys, but it is a significantly more complex to setup and maintain.

## Demo

Note that a demo is available at https://secretsfly.fly.dev/ - it is periodically reset.

## Secrets mechanism

- Secrets are encrypted by one master key per project. When storing secrets in the main database (Sqlite), the master key is temporarily stored in memory (encrypted) and needs to be kept secret by the end user.
- The master key is temporarily encrypted in memory and is deleted after a certain amount of time (see `ADMIN_MASTER_KEY_EXPIRATION`).
- Further, te master key is generated by the user and is never stored on the application database. Therefore in a scenario where the secrets database is stolen, the secrets are still safe and cannot be decrypted.
- Secrets are encrypted using AES-256-GCM.
- You can generate service tokens per project and environment, which can then be used to retrieve project secrets.

## Features

- Secrets are grouped per project and per environment.
- Secrets follow a project hierarchy - secrets coming from inherited projects are also available to the child projects.
- Cloud agnostic rather than multi-cloud support as opposed to Hashicorp Vault, and similar tools.
- Ability to rotate the master key, and re-encrypt all secrets with a new master key.
- Service tokens allow to decrypt secrets and are passed in memory in the child process (typically a server requiring environment variables).
- Secrets in a given environment can be copied to other environments whenever missing.

## Server Installation

Booting secretsfly only requires to setup few environment variables (minimally `ENV`) and run the python flask server.
Note that on the first boot, the database is initialized by copying `db/secretsfly-current.db` to `db/secretsfly-[ENV].db`.

### Docker compose

A docker-compose file is provided in the repository.
To make it work, environments variables can be set in a `.env` file (see the supported variables in the next section).
If you want to enable HTTPS (recommended), see the SSL section below.

Then run:

```
docker-compose up -d --build
```

### Environment variables

- `ENV`: The secretsfly environment. Note that on the first boot, the database is initialized by copying `db/secretsfly-current.db` to `db/secretsfly-[ENV].db`.
- `DB_FOLDER`: Default: ./db. Folder where the database is stored.
- `AVAILABLE_ENVIRONMENTS`: Default: prod. Comma separated list of environments available globally.
- `ADMIN_MASTER_KEY_EXPIRATION`: Default: 300 (in seconds). Master key timeout, after which the master key is deleted from memory.
- `ADMIN_UI_DECRYPTED_SECRETS_EXPIRATION`: Default: 5. Number of minutes before redirecting to the encrypted secrets page from the decrypted page.
- `ADMIN_BASIC_AUTH_USERNAME`: Username for the admin UI. Basic auth is enabled if this variable is set.
- `ADMIN_BASIC_AUTH_PASSWORD`: Password for the admin UI.
- `VERSIONED_SECRET_VALUES`: Default: false. If set to true, secrets values are versioned. This means that when updating a secret, the old value is kept in the database.

### SSL

It is recommended to enable SSL on the secretsfly server.
For a quick self-signed certificate, run the following command:

```
cd certs
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

For some notes related to security and potential vulnerabilities, see [SECURITY.md](SECURITY.md).

## Client Usage

### CLI

A python CLI is provided in the `cli` directory, and can be used to decrypt secrets, including for example
in containers, custom scripts, etc. See the [cli/README.md](cli/README.md) for more details.
Example usage:

```
python cli/cli.py -- your server command (example: node server.js)
```

### User Interface

The server provides a simple admin user interface allowing to manage secrets in the browser.

## Backup

Backuping secretsfly is as simple as copying the sqlite database file located in `db/secretsfly-[ENV].db` to any storage
solution.
Note that the db content is safe to backup online, as the master key is never stored in the database.
A sample script copying into a git repository is as follows:

```
#!/bin/bash
cp /secretsfly/db/secretsfly-production.db /secretsfly-dump/backup.db
cd /secretsfly-dump/
git commit -am 'update'
git push
```

## Benchmark

A [benchmark](benchmark) was done, giving an idea about secretsfly performance to retrieve secrets by API.

## TODO

### possible get padding invalid if wrong master key while decrypting