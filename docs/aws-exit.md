# Customer API AWS exit audit

## Package delivery

Before this migration the Pipfile and lock pinned API Utils 1.0.4 from CodeArtifact. The README's 1.0.3 reference is stale. The earlier pin task, F346, shipped for 1.0.1 and is superseded by the current pin. There are no unfinished pin tasks.

The migration uses the public [API Utils 1.0.5 wheel](https://github.com/mentor-forge/mentorhub_api_utils/releases/download/v1.0.5/api_utils-1.0.5-py3-none-any.whl). An unauthenticated download matched the published SHA-256 `79de3829e2baa294497e08925908645bcea53cdf497d02b6bed71322a503d952`. The Pipfile and lock now pin the exact wheel URL and digest and resolve third-party dependencies from public PyPI. The public PyPI package named `api-utils` is unrelated. Run `pipenv run install` to sync the development environment from the lock, and `pipenv lock` when intentionally updating it. For future rollbacks, restore the verified GitHub-hosted wheel pin and its matching lockfile together. The rollback floor is 1.0.5.

| Surface | Current dependency | Migration |
| --- | --- | --- |
| `Pipfile`, `Pipfile.lock`, `scripts/pipenv-install.sh`, `scripts/pipenv-lock.sh` | AWS CLI token and endpoint lookup; install wrapper exports a temporary requirements file | F349 uses Pipenv's native sync and lock with a public index and an exact hashed wheel. Preserve the existing install command used by local package automation. |
| `Dockerfile`, `scripts/docker-build.sh` | Authenticated index passed to Docker through a build argument | F350 builds from the lock without registry credentials and retains the image and runtime entry point. |
| `.github/workflows/docker-push.yml` | AWS OIDC role, CodeArtifact index, and build argument | F351 removes AWS auth, adds read-only PR checks, and retains GHCR publishing on main. |
| `README.md`, `tasks/_PLANNING.md` | Developer setup still points to CodeArtifact | F352 documents the new setup and records independent Customer API acceptance. |

## Runtime contracts

Customer API starts with shared Config and MongoIO. Route handlers obtain normalized bearer claims through `create_flask_token()`. API Utils 1.0.5 retains the token dictionary's `user_id`, `display_name`, `roles`, `profile_id`, and `customer_id` contract. The Customer persona fixture already uses `display_name`. Preserve scoped profile and customer lookup, JWT and role enforcement, and MongoIO-backed service calls. Verify those contracts with the actual pinned wheel in subsequent tasks.

The tracked runtime source and tests contain no Cognito or direct AWS SDK references. Developer Edition Compose historically supplied Cognito variables to Customer API, but this repo has no consumers of those settings. Provider-specific integration belongs in its infrastructure repository. This migration needs no identity adapter, data rewrite, or OpenAPI changes.

Customer API acceptance covers a clean locked install, its tests, and its packaged runtime against local backing services. Production infrastructure and Customer SPA adoption can be tracked independently.
