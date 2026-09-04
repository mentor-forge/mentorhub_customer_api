# F346 – Pin api-utils 1.0.1

**Status:** Shipped  
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

### Plan
1. Confirm helper signatures (`MongoIO`, `execute_list_query`, `build_match_filter`, `encode_document`, `create_flask_token`) against sibling `api_utils` 1.0.1 source — local services already use compatible call shapes; no `src/` changes in this task.
2. Pin `Pipfile` `api-utils==1.0.1` (keep CodeArtifact `[[source]]` and PyPI comment).
3. Regenerate `Pipfile.lock` with `scripts/pipenv-lock.sh` (run `mh` first), then `pipenv run install`. If 1.0.1 cannot resolve from CodeArtifact, set Status Blocked and stop (no path-install).
4. Confirm installed `importlib.metadata.version("api-utils") == "1.0.1"` and audit installed `Token.to_dict` / `create_flask_token` (`display_name` present, no `name` key).
5. Align `test/e2e/e2e_auth.py` JWT claims: add `display_name`, keep required `profile_id`, do not mint claim `name`.
6. Update `README.md` pin wording to 1.0.1 and a one-line note that the token dict uses `display_name`.
7. Run unit/lint/build, then dev E2E and container packaging E2E; curl `/api/config` to confirm token object shape.

### Summary
Pinned `api-utils==1.0.1` from CodeArtifact (`scripts/pipenv-lock.sh` then `pipenv run install`). Installed version is `1.0.1`. E2E JWT now mints `display_name` (no claim `name`) plus required `profile_id`. `customer_id` / `mentor_id` remain optional empty defaults on `Token`. No `src/` changes. README pin updated.

### Token contract (installed 1.0.1)
- `importlib.metadata.version("api-utils") == "1.0.1"`
- `Token.to_dict()` / `create_flask_token()` keys: `user_id`, `display_name`, `roles`, `profile_id`, `customer_id`, `mentor_id`, `remote_ip`
- No `name` key on the token dict
- JWT display label: installed `Token` maps `claims.name` **or** `claims.display_name` into `display_name`. This task mints `display_name` only (does not rely on claim `name`; no local mapper)
- `profile_id` required; `customer_id` / `mentor_id` optional empty defaults
- `Config.to_dict(token)` passes the same dict through GET `/api/config`
- Authenticated GET `/api/config` (dev and container): `display_name=Adam`, keys as above, `name` absent

### Helper signature audit
Installed 1.0.1 signatures match local usage; no local patches:
- `MongoIO.get_documents/get_document/create_document/update_document/upsert_document`
- `execute_list_query(collection_name, *, match, sort_by, offset, size, project)`
- `build_match_filter(base_match, parsed_filters, filter_spec)`
- `encode_document(document, id_properties, date_properties)`

### Test results
- `pipenv run test`: 77 passed, 24 deselected
- `pipenv run lint`: **fails** on pre-existing wrap in `src/services/profile_service.py` (logger.info). Not in Outputs; left unchanged. `test/e2e/e2e_auth.py` is black-clean.
- `pipenv run build`: success
- Dev E2E (`pipenv run dev` + `pipenv run e2e`): 23 passed, 1 failed
- `pipenv run container`: built `ghcr.io/mentor-forge/mentorhub_customer_api:latest` with `api-utils==1.0.1`
- Container E2E (`pipenv run api` + `pipenv run e2e`): 23 passed, 1 failed

`test/e2e/test_profile.py::test_create_and_patch_profile_endpoint` returns 500 because the POST body still sends Profile document field `name`, which Mongo `$jsonSchema` rejects (`additionalProperties: ['name']`). Shared `create_profile` pass-through; not a token-auth failure. Out of scope (F347 / document `name`); this task must not change that test or `src/`.

Auth-required E2E cases passed; 1.0.1 `Token` accepts the minted JWT.
