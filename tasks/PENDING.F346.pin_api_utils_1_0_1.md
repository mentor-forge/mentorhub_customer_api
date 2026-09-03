# F346 – Pin api-utils 1.0.1

**Status:** Pending  
**Type:** Feature  
**Depends On:** none  
**Description:** F-CA16 owns this pin. Bump `api-utils` from `1.0.0` to exact **`1.0.1`**, refresh the lockfile from CodeArtifact, and sync E2E JWT claims with `Token` (`display_name` instead of `name`). Do **not** rewrite local services or routes in this task except as required for the pin to install and for tests to mint a valid 1.0.1 token.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `tasks/_PLANNING.md` — Shared Library / Version Bump Checklist; `pipenv run install` after Pipfile changes (CodeArtifact; run `mh` first). Do not call `mongo.get_collection(...)`.
- `README.md`
- `../mentorhub_api_utils/README.md` — pin examples and `Token` / `create_flask_token` claim shape
- `../mentorhub_api_utils/api_utils/flask_utils/token.py` — `Token.to_dict` / `create_flask_token` must expose **`display_name`**, not `name`
- `../mentorhub_api_utils/api_utils/config/config.py` — `to_dict(token)` GET `/api/config` token payload (expect `display_name`)
- `../mentorhub_api_utils/api_utils/mongo_utils/mongo_io.py` — confirm `MongoIO` signatures still match local services
- `../mentorhub_api_utils/api_utils/mongo_utils/list_query.py` — confirm `execute_list_query` / `build_match_filter` signatures
- `Pipfile` / `Pipfile.lock` — currently `api-utils==1.0.0`
- `test/e2e/e2e_auth.py` — mint claims that 1.0.1 `Token` accepts
- `src/server.py` — keep existing `/api/*` prefixes; config routes stay `create_config_routes()`

**Source issue:** F-CA16 ([mentorhub_customer_api#19](https://github.com/mentor-forge/mentorhub_customer_api/issues/19)) — bump to latest `api-utils` **1.0.1**. Token key migration in local code is **F347**.

**External prerequisite:** `api-utils==1.0.1` must resolve from the CodeArtifact index. Run `mh` once per shell, then `pipenv run install`. If 1.0.1 cannot be resolved, set **Status** to `Blocked`, rename this file to `BLOCKED.F346.pin_api_utils_1_0_1.md`, and stop — do not stay on `1.0.0` and do not point `Pipfile` at a git URL or local path.

This API **owns this repo’s 1.0.1 pin**. Sibling domain APIs pin independently; do not change other repos.

**Pin:** this task owns `api-utils==1.0.1`. Install with `pipenv run install`. Do **not** use bare `pipenv install` or `pipenv install --dev`. Use `scripts/pipenv-lock.sh` if lock hashes must be regenerated first.

### Expected 1.0.1 Token contract

After install, confirm against the installed package (not only sibling source if they diverge):

- `create_flask_token()` / `Token.to_dict()` keys include `user_id`, **`display_name`**, `roles`, `profile_id`, `customer_id`, `mentor_id`, `remote_ip`.
- There is **no** `name` key on the token dict.
- JWT claim for the display label is **`display_name`**. `profile_id` remains required.
- GET `/api/config` token object uses the same dict (via `Config.to_dict(token)`).

If 1.0.1 still required `name`, stop and record the mismatch in **Execution Notes**; do not invent a local mapper.

### What NOT to do

- Do not replace `token.get("name")` / `token["name"]` in `src/` or tests here (F347).
- Do not change Profile, Customer, Rating, or Journey **document** `name` fields, list filters, or OpenAPI collection schemas.
- Do not bump to `1.1.0` or leave a floating `*` pin.
- Do not edit `mentorhub_api_utils` from this repo.

## Goals

- `Pipfile` and `Pipfile.lock` pin `api-utils==1.0.1` (CodeArtifact `[[source]]` unchanged; keep the comment that public PyPI `api-utils` is unrelated).
- Dependencies are installed with `pipenv run install` (run `mh` first if CodeArtifact credentials are missing).
- `importlib.metadata.version("api-utils") == "1.0.1"`.
- `test/e2e/e2e_auth.py` mints a JWT whose claims match 1.0.1 `Token`: include **`display_name`**, do not rely on claim **`name`**. Keep `profile_id` (required). Add `customer_id` / `mentor_id` only if 1.0.1 `Token` requires them for the admin E2E persona (today they are optional empty defaults).
- `README.md` states the `api-utils==1.0.1` pin (replace the current `1.0.0` wording). Do not document the `display_name` service migration except as a one-line note that the token dict uses `display_name`.
- Helper signatures used by this API (`MongoIO`, `execute_list_query`, `encode_document`, shared GET factories, exceptions) still match 1.0.1. Record any mismatch in **Execution Notes**; do not patch around it locally.

### Craftsmanship Expectations

- Reuse `api_utils` `Token` / `create_flask_token`; do not add a local claim-mapping helper.
- Treat DRY as avoiding duplicated knowledge: the token claim schema is owned by `api_utils`. This repo only mints test JWTs and pins the package.
- Keep journey-specific services unchanged in this task.

## Testing Expectations

Run all commands from this API repository root.

- **Install**
  - `mh` once per shell if CodeArtifact credentials are not already available
  - `pipenv run install`
  - Confirm `importlib.metadata.version("api-utils") == "1.0.1"`
  - Confirm `create_flask_token` / `Token.to_dict` include `display_name` and omit `name`
- **Unit / lint / build**
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
- **Dev E2E**
  - `pipenv run db` if needed
  - `pipenv run dev` (separate terminal or background)
  - `pipenv run e2e` — tokens from `test/e2e/e2e_auth.py` must authenticate against 1.0.1 `Token`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `pipenv run e2e` against the containerized API
  - `curl` a authenticated `GET /api/config` (or inspect an E2E response) and confirm the token object uses `display_name`, not `name`

Testing should try to prove the pin wrong: a JWT that still only has claim `name` (no `display_name`) must not be treated as the supported 1.0.1 shape. Do not add a compatibility shim that copies `name` into `display_name`.

## Outputs

- `Pipfile` — pin `api-utils==1.0.1`
- `Pipfile.lock` — refresh via `pipenv run install` (use `scripts/pipenv-lock.sh` if hashes must be regenerated first)
- `README.md` — 1.0.1 pin
- `test/e2e/e2e_auth.py` — JWT claims aligned with 1.0.1 `Token` (`display_name`, required `profile_id`)

The agent must not update files outside this list.

## Execution Notes
