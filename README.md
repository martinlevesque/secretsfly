
# secretsfly

secretsfly is an easy to use, minimalist, with low number of dependencies, and fast secrets management tool with a focus on self-hosting and security.
It can also be used as a personal secrets management tool.
Don't let third party manage your secrets, keep them yourself and avoid the risk of data leaks.

## Secrets mechanism

- Secrets are encrypted by a master key per project. When storing secrets in the main database, the master key is temporarily stored in memory (encrypted) and needs to be kept secret by the end user.
- The master key is temporarily encrypted in memory and is deleted after a certain amount of time (see `ADMIN_MASTER_KEY_EXPIRATION`).
- The master key is generated by the user and is never stored on the application database. Therefore in a scenario where the secrets database is stolen, the secrets are still safe and cannot be decrypted.
- Secrets are encrypted using AES-256-GCM.

## Features

- Secrets are grouped per project and per environment.
- Secrets follow a project hierarchy - secrets coming from inherited projects are also available to the child projects.
- Cloud agnostic rather than multi-cloud support as opposed to Hashicorp Vault, and similar tools.
- Ability to rotate the master key, and re-encrypt all secrets with a new master key.

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
- `AVAILABLE_ENVIRONMENTS`: Default: prod. Comma separated list of environments available globally.
- `ADMIN_MASTER_KEY_EXPIRATION`: Default: 300 (in seconds). Master key timeout, after which the master key is deleted from memory.
- `ADMIN_UI_DECRYPTED_SECRETS_EXPIRATION`: Default: 5. Number of minutes before redirecting to the encrypted secrets page from the decrypted page.
- `ADMIN_BASIC_AUTH_USERNAME`: Username for the admin UI. Basic auth is enabled if this variable is set.
- `ADMIN_BASIC_AUTH_PASSWORD`: Password for the admin UI.

### SSL

It is recommended to enable SSL on the secretsfly server.
For a quick self-signed certificate, run the following command:

```
cd certs
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

For some notes related to security and potential vulnerabilities, see [SECURITY.md](SECURITY.md).

## Client Installation

TODO

## Backup



## Related Projects and motivation

### Vault

https://www.datocms-assets.com/2885/1597082390-vault-com-security-whitepaper-v2-digital.pdf

### Doppler

comparing doppler vs vault:
https://www.doppler.com/blog/doppler-vs-hashicorp-vault

- vault is key-value
- doppler is grouping secrets in projects
- to test - example with github, sync secrets?

## todo

### better display table projects

### better display table service tokens

### [DONE] way to have non base64 master key - could auto base64, 32 bytes (chars)