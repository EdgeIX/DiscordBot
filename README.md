# EdgeIX Discord Bot
![EdgeIX](https://www.edgeix.net/img/logo.png)

## About EdgeIX Bot
EdgeIX Bot is a Discord Bot that uses IXP Managers API to allow users to display peer status and various other functions from within the EdgeIX Discord.


## About EdgeIX

EdgeIX operates multi-lateral layer 2 internet exchanges for anyone with an autonomous system number (ASN).
We believe that having more internet exchange points (IXPs) contributes to a healthier internet ecosystem for Australia, and are focusing on under-served regional markets such as Darwin (DRW), Hobart (HBA) and Adelaide (ADL).

 

With over 20 years industry experience in the telecommunication space and operation of internet exchanges, our team is dedicated to provide best-in-class product and service.


## How can I become a Peer?
[Become a peer!](https://www.edgeix.net/contact/)

## Contributing
Pull requests are welcome.

## Development and deployment

Runtime starts from `src/main.py`. Legacy root scripts `bot.py` and `bgp.py`
remain for reference and are unsupported. Use Python 3.14.7 and Docker for
repeatable builds and checks. Copy `.env.sample` to `.env`, fill in the
development values, and keep the populated file private.

`PYTHON_ENV=dev` enables development hot reload by default. Set
`ENABLE_HOT_RELOAD=false` when it is not wanted. Set `PYTHON_ENV=prod` for a
production process; hot reload is disabled for non-development environments.
`TOKEN` and `GUILD_ID` are canonical names. `DISCORD_TOKEN` and
`DISCORD_GUILD` remain accepted aliases for existing development files.

Build and test entirely through Docker:

```sh
docker build --target runtime -t edgeixbot:runtime .
docker build --target test -t edgeixbot:test .
docker run --rm --network none edgeixbot:test pytest -q
docker run --rm --network none edgeixbot:test ruff check src tests
docker run --rm edgeixbot:test pip-audit --requirement requirements.txt
```

Regenerate dependency locks inside Docker after changing `requirements.in` or
`requirements-dev.in`. `--upgrade` refreshes transitive pins while leaving the
existing lock files in place if resolution fails:

```sh
docker run --rm -v "$PWD:/work" -w /work \
  python:3.14.7-slim-bookworm sh -c \
  'python -m pip install --upgrade pip pip-tools && \
   pip-compile --upgrade --allow-unsafe --generate-hashes --output-file requirements.txt requirements.in && \
   pip-compile --upgrade --allow-unsafe --generate-hashes --output-file requirements-dev.txt \
     --constraint requirements.txt requirements-dev.in'
```

Deploy an immutable image tag built by CI, for example
`samfty/edgeixbot:<git-commit-sha>`, and pass the populated environment file to
the runtime. Keep the previous commit tag available for rollback:

```sh
docker pull samfty/edgeixbot:<previous-git-commit-sha>
docker stop edgeixbot || true
docker rm edgeixbot || true
docker run --name edgeixbot --env-file .env \
  samfty/edgeixbot:<previous-git-commit-sha>
```

Rollback changes the image reference only; it does not replace development
credentials or environment values. CI publishes commit-SHA tags plus `latest`
for `main` and version tags for `v*` releases.

CI runs unit tests and lint without network access inside the test container,
then audits locked runtime dependencies. A live Discord smoke test has not
been performed; before production rollout, verify startup/reconnect, command
sync, role approval/removal, API failure handling, and clean shutdown in an
isolated Discord guild.

## Development with an invalid IXPM certificate

Set `IXPM_VERIFY_SSL=false` in your environment (or Compose `.env` file) to
disable TLS certificate verification for IXPM peer refresh requests. Verification
is enabled by default; only the value `false` disables it. Other HTTP requests
are unaffected.

For Compose, pass the setting through the service's `environment` list:

```yaml
- IXPM_VERIFY_SSL=${IXPM_VERIFY_SSL:-true}
```

Rebuild or pull an image containing this change, then recreate the container:

```sh
IXPM_VERIFY_SSL=false docker compose up -d --force-recreate
```

Use this only for development: disabling verification allows server impersonation
and exposure of the IXPM API key. Leave verification enabled in production.

## License
[GNU General Public License v3.0
](https://www.gnu.org/licenses/gpl-3.0.en.html)
