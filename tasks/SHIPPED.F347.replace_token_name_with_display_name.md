# F347 – Replace token.name with token.display_name

**Status:** Shipped  
**Type:** Feature  
**Depends On:** `F346_pin_api_utils_1_0_1`  
**Description:** Remainder of F-CA16. With `api-utils==1.0.1` pinned, replace every **token dict** use of `name` with `display_name` in this API’s source and tests. Do not change collection/document `name` fields, list filters, or OpenAPI schemas for Profile, Customer, Rating, or Journey.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — Customer **controls** Customer, Payment, Profile; **creates** Event
- `../mentorhub/DeveloperEdition/standards/api_standards.md` — RBAC in services; MongoIO only
- `tasks/_PLANNING.md` — token claim schema is owned by `api_utils.flask_utils.token.Token`; do not call `mongo.get_collection(...)`
- `README.md`
- `../mentorhub_api_utils/README.md`
- `../mentorhub_api_utils/api_utils/flask_utils/token.py` — token dict key **`display_name`** (not `name`)
- `../mentorhub_api_utils/api_utils/services/event_service.py` — `create_event` copies `dict(token)` into `context`; that copy must not reintroduce `name`
- `src/services/customer_service.py`
- `src/services/profile_service.py`
- `src/services/event_service.py`
- `src/services/note_service.py`
- `src/services/journey_service.py`
- `src/services/rating_service.py`
- `src/routes/` — routes pass `create_flask_token()` through; do not map keys locally
- `test/services/` and `test/routes/` — `self.mock_token` / persona dicts
- `test/e2e/e2e_auth.py` — already aligned in F346; only touch if a remaining `name` claim slipped through
- `test/e2e/test_*.py` — document `name` query params are **not** token claims

**Source issue:** F-CA16 ([mentorhub_customer_api#19](https://github.com/mentor-forge/mentorhub_customer_api/issues/19)) — replace any use of `token.name` with `token.display_name`.

**Pin:** already `api-utils==1.0.1` from F346. Do not re-bump. `pipenv run install` only if the lockfile needs a refresh. Do not use bare `pipenv install`.

### Token vs document `name`

| Kind | Keep `name`? | Action |
| --- | --- | --- |
| Token dict from `create_flask_token()` / `Token.to_dict()` | No | Use `display_name` (`token.get("display_name")`, `token["display_name"]`) |
| JWT payload in `e2e_auth.py` | No | Claim `display_name` (F346); remove leftover `name` |
| Profile / Customer / Rating / Journey **documents**, list `contains` filters, OpenAPI collection properties | Yes | Unchanged |
| `app.name`, blueprint `.name`, OpenAPI `tags.name` / parameter `name:` | Yes | Unchanged |

As of F346, local services mostly use `token.get("user_id")`, `roles`, `profile_id`, `customer_id`. Confirm with grep; if there are **zero** token `name` reads, still update **mock token dicts** so they match 1.0.1 (include `display_name`, omit token `name`) wherever tests construct a token.

Shared `EventService.create_event` sets `data["context"] = dict(token)`. Event unit tests that inspect `context` must expect `display_name`, not `name`.

Do not add a local fallback (`token.get("display_name") or token.get("name")`).

### What NOT to do

- Do not change `Pipfile` / `Pipfile.lock` version (F346).
- Do not edit `mentorhub_api_utils`.
- Do not rename Profile `name`, Customer `name`, or list query `?name=`.
- Do not expand OpenAPI `/api/config` token from `type: object` unless a test or explorer already documents token keys; if you do document keys, use `display_name` only.

## Goals

- Zero token-dict reads or writes of key `name` in `src/` and `test/` (JWT/token mocks and `create_flask_token` results).
- Mock tokens used as the first argument to services include `display_name` when they previously included a person label, or when Event `context` is asserted.
- `test/e2e/e2e_auth.py` has claim `display_name` and no claim `name`.
- Confirmation greps below are clean (false positives from document `name` / OpenAPI parameter `name:` are documented in **Execution Notes**, not “fixed” by renaming documents).
- MongoDB I/O in any touched service stays on `MongoIO` (`get_document`, `get_documents`, `create_document`, `update_document`, `upsert_document`).

### Craftsmanship Expectations

- Token claim shape is owned by `api_utils`; do not create a local `normalize_token` helper.
- Prefer deleting obsolete `name` on token mocks rather than keeping both keys.
- Do not work around 1.0.1 by copying `name` into `display_name`.

## Testing Expectations

Run all commands from this API repository root.

- **Confirmation greps**
  - `rg 'token\[.name.\]|token\.get\(.name.\)|token\.name' src test` — zero hits
  - `rg '"name":' test/e2e/e2e_auth.py` — zero hits
  - `rg 'display_name' test/e2e/e2e_auth.py` — at least one hit
  - Review remaining `"name"` in `test/services` and `test/routes`: only document fixtures and list filters, never token dicts
- **Unit / lint / build**
  - `pipenv run test` — service and route tests pass with 1.0.1 token dicts; Event create `context` does not contain `name`
  - `pipenv run lint`
  - `pipenv run build`
- **Dev E2E**
  - `pipenv run db` if needed
  - `pipenv run dev`
  - `pipenv run e2e`
  - Prove the boundary: E2E still uses least-privileged vs admin where existing tests do; do not mint tokens that only have `name`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `pipenv run e2e` against the containerized API
  - Authenticated `GET /api/config` token object has `display_name` and does not have `name`

## Outputs

- `src/services/customer_service.py` — only if a token `name` read exists
- `src/services/profile_service.py` — only if a token `name` read exists
- `src/services/event_service.py` — only if a token `name` read exists
- `src/services/note_service.py` — only if a token `name` read exists
- `src/services/journey_service.py` — only if a token `name` read exists
- `src/services/rating_service.py` — only if a token `name` read exists
- `src/routes/*.py` — only if a token `name` read exists
- `test/services/test_customer_service.py`
- `test/services/test_profile_service.py`
- `test/services/test_event_service.py`
- `test/services/test_note_service.py`
- `test/services/test_journey_service.py`
- `test/services/test_rating_service.py`
- `test/routes/test_customer_routes.py`
- `test/routes/test_profile_routes.py`
- `test/routes/test_event_routes.py`
- `test/routes/test_note_routes.py`
- `test/routes/test_journey_routes.py`
- `test/routes/test_rating_routes.py`
- `test/e2e/e2e_auth.py` — only if F346 left a `name` claim
- `README.md` — only if token dict documentation still says `name`

Skip files with no token-dict `name` usage; do not churn them. The agent must not update files outside this list.

## Execution Notes

### Plan
1. Confirm `src/` has zero `token.get("name")` / `token["name"]` / `token.name` reads (F346 leftover). Skip all `src/services/*` and `src/routes/*` — no token-dict `name` usage.
2. Confirm `test/e2e/e2e_auth.py` already mints `display_name` and has no claim `name` (F346). Skip unless a leftover `name` claim appears.
3. Confirm `README.md` already documents the token dict `display_name` key. Skip.
4. Update mock token dicts in listed `test/services/` and `test/routes/` files: add `display_name`, omit token `name`. Leave Profile/Customer/Rating/Journey **document** `name` fixtures and list filters unchanged.
5. In `test/services/test_event_service.py`, assert `create_event` copies token into `context` with `display_name` and without `name`.
6. Run confirmation greps, unit/lint/build, then dev E2E and packaging E2E + authenticated `GET /api/config`. Do not change Pipfile. Do not edit `mentorhub_api_utils`.
7. Known leftovers from F346 (out of scope unless token dict uses `name`): pre-existing black wrap in `src/services/profile_service.py`; E2E `test_create_and_patch_profile_endpoint` POST body still sends Profile document field `name`.

### Summary
`src/` had zero token-dict `name` reads; services/routes and README / `e2e_auth.py` were skipped. Mock tokens in listed service and route tests now include `display_name` and omit token `name`. Event create asserts `context.display_name` and `name` absent. Document/list `name` fixtures left unchanged. Pipfile not touched.

### Confirmation greps
- `rg 'token\[.name.\]|token\.get\(.name.\)|token\.name' src test` — zero hits
- `rg '"name":' test/e2e/e2e_auth.py` — zero hits
- `rg 'display_name' test/e2e/e2e_auth.py` — one hit (`display_name`: Adam)

Remaining `"name"` in `test/services` and `test/routes` (false positives, not token dicts):
- Customer / Rating / Profile document fixtures and `result["name"]` assertions
- List filters `filters={"name": "test"}` and `sort_by=[("name", 1), ...]`
- Profile POST/PATCH JSON bodies (`{"name": "new_profile"}`, create payloads)
- `test_event_service.py` `assertNotIn("name", result["context"])` — token-context guard, not a token write

### Test results
- `pipenv run test`: 77 passed, 24 deselected
- `pipenv run lint`: **fails** on pre-existing wrap in `src/services/profile_service.py` (`logger.info`). No token `name` read; not edited (Outputs: only if token `name` read exists). Test files are black-clean.
- `pipenv run build`: success
- Dev E2E (`pipenv run dev` + `pipenv run e2e`): 23 passed, 1 failed
- `pipenv run container`: built `ghcr.io/mentor-forge/mentorhub_customer_api:latest` with `api-utils==1.0.1`
- Container E2E (`pipenv run api` + `pipenv run e2e`): 23 passed, 1 failed

`test/e2e/test_profile.py::test_create_and_patch_profile_endpoint` returns 500 because the POST body still sends Profile document field `name`, which Mongo `$jsonSchema` rejects. Document-field issue; out of scope.

Auth-required E2E cases (`*_require_auth`) passed with the admin persona JWT (`display_name`, no claim `name`). Existing tests do not mint least-privileged personas; no token was minted with only `name`.

### GET /api/config token object
Dev and container authenticated GET `/api/config`:
- keys: `user_id`, `display_name`, `roles`, `profile_id`, `customer_id`, `mentor_id`, `remote_ip`
- `display_name=Adam`
- `name` absent

### Leftovers (out of scope)
- `pipenv run lint` black wrap in `src/services/profile_service.py`
- E2E profile create POST document field `name`
