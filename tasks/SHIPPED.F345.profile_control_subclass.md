# F345 – Profile control subclass (create + PATCH + inbound RBAC)

**Status:** Shipped  
**Type:** Feature  
**Depends On:** `F344_openapi_profile_create_patch`  
**Description:** Remainder of F-CA15. Pin stays `api-utils==1.0.0` (refresh lockfile only if needed). Local `ProfileService` already subclasses shared GET/create from F343. Add inbound write checks, `update_profile`, and Profile POST/PATCH on the factory blueprint. Routes keep importing the local subclass. Do not 403 on GET.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — Customer **controls** Profile; **creates** Event
- `../mentorhub/DeveloperEdition/standards/api_standards.md` — RBAC at the service layer; MongoIO only
- `tasks/_PLANNING.md` — `pipenv run install` if the lockfile is refreshed; encode ids before MongoIO; do not use `mongo.get_collection(...)`
- `README.md`
- `../mentorhub_api_utils/README.md` — inbound writes on the subclass; outbound GET on the parent; routes import the local subclass
- `../mentorhub_api_utils/api_utils/services/profile_service.py` — inherit `get_profile`, `get_profiles`, `get_profile_by_token`, `create_profile`; `SYSTEM_MANAGED_FIELDS`; `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER`
- `../mentorhub_api_utils/api_utils/services/rbac.py` — `is_admin`
- `../mentorhub_api_utils/api_utils/routes/shared_get_routes.py` — `create_profile_get_routes` already mounted in F343
- `src/services/profile_service.py` — thin subclass from F343; no `update_profile` yet
- `src/routes/profile_routes.py` — factory GET only
- `src/services/event_service.py` / `src/routes/event_routes.py` — F343 should already inherit `create_event` and POST the document; confirm, do not re-pin
- `docs/openapi.yaml` — F344 POST/PATCH
- `test/services/test_profile_service.py`
- `test/routes/test_profile_routes.py`
- `test/e2e/test_profile.py`
- `test/e2e/e2e_auth.py`

**Pin:** already `api-utils==1.0.0`. `pipenv run install` only if `Pipfile.lock` needs a refresh. Do not re-bump the version. Do not use bare `pipenv install`.

```python
from api_utils.services import ProfileService as SharedProfileService

class ProfileService(SharedProfileService):
    @classmethod
    def update_profile(cls, profile_id, data, token, breadcrumb):
        # Customer control: restricted _id/created/saved; stamp saved; MongoIO.update_document
        ...
```

**Inbound RBAC (writes only):** override `_check_permission` so `create` and `update` require `Config.ROLE_CUSTOMER` or admin (`ROLE_ADMIN` / `is_admin(token)`). For `read`, call `super()._check_permission(...)` — do **not** 403 on GET (outbound list/get-by-id stays on the shared class: own profile, same `customer_id`, admin root, hide archived).

- `create_profile`: call inbound create check; when the caller is a customer (not admin), stamp `customer_id` from the token; then `super().create_profile(...)`.
- `update_profile`: inbound update check; load the target with `MongoIO.get_document` (or inherited `get_profile`); **403** if the caller is not admin and the target is neither the caller’s own profile nor in the caller’s `customer_id`; strip `_id` / `created` / `saved`; stamp `saved` from the breadcrumb; `encode_document`; `MongoIO.update_document`. Return the updated document (follow existing control-PATCH pattern: update then get-by-id if that is clearer).

Do not import `api_utils.services.ProfileService` in routes.

**Routes:** keep `bp = create_profile_get_routes(ProfileService)`. Add:

- `POST ""` → `ProfileService.create_profile` → `201` with the returned document
- `PATCH /<profile_id>` → `ProfileService.update_profile` → `200`

Handlers: `create_flask_token()`, `create_flask_breadcrumb(token)`, `request.get_json() or {}`, `@handle_route_exceptions`. Do not validate or alter payloads in the route.

List GET remains a JSON array with `offset`/`size` headers (factory). Event POST stays inherited `create_event` from F343 — if F343 still has a local id-returning `create_event`, switch it here to `super().create_event` / inherited method and return the document with `201`. Do not add Payment or Stripe.

## Goals

- Local `ProfileService` still subclasses shared; adds `update_profile` and inbound create/update RBAC; stamps `customer_id` on customer creates.
- Profile POST and PATCH are mounted on the factory blueprint; GET list/by-id unchanged.
- Routes import `src.services.profile_service.ProfileService` only.
- Customer (or admin) can create and patch Profile; non-customer non-admin is 403 on writes; GET does not 403 for “not a customer”.
- Unit, route, and E2E tests cover POST `201`, PATCH `200`, write 403, restricted fields, and list array + `offset`/`size`.
- `pipenv run test`, `pipenv run lint`, `pipenv run build` pass.

## Testing Expectations

Run all commands from this API repository root.

- **Install** (only if lockfile changed)
  - `mh` once per shell if CodeArtifact credentials are not already available
  - `pipenv run install`
- **Confirmation greps**
  - `rg "from api_utils.services import .+Service" src/routes` — zero hits
  - `rg 'execute_infinite_scroll_query|after_id|has_more|next_cursor' --glob '*.py' --glob 'docs/openapi.yaml'` — zero hits
- **Unit / lint / build**
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
  - `test/services/test_profile_service.py` — create allowed for customer and admin; customer create stamps `customer_id`; update allowed for own profile / same `customer_id` / admin; `HTTPForbidden` otherwise; `_id`/`created`/`saved` rejected or stripped on update; `saved` stamped; inherited GETs still present; no 403-on-GET for missing customer role
  - `test/routes/test_profile_routes.py` — POST `201` and PATCH `200` patch `src.routes.profile_routes.ProfileService.*`; GET list still returns an array
  - `test/e2e/test_profile.py` — list is a JSON array; add create + patch coverage with a token that includes `roles` and `customer_id` / `profile_id` as needed
- **Dev E2E**
  - `pipenv run db` if needed
  - `pipenv run dev` (separate terminal or background)
  - `pipenv run e2e`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `pipenv run e2e` against the containerized API
  - `curl -s http://localhost:8387/docs/openapi.yaml` — includes F344 Profile POST/PATCH

## Outputs

- `src/services/profile_service.py`
- `src/routes/profile_routes.py`
- `src/services/event_service.py` — only if Event POST does not yet inherit `create_event`
- `src/routes/event_routes.py` — only if Event POST still assumes a bare id
- `test/services/test_profile_service.py`
- `test/routes/test_profile_routes.py`
- `test/e2e/test_profile.py`
- `test/e2e/e2e_auth.py` — only if customer-role tokens are required
- `test/services/test_event_service.py` / `test/routes/test_event_routes.py` / `test/e2e/test_event.py` — only if Event POST return shape changes in this task
- `README.md` — only if Profile write contract should be mentioned
- `Pipfile.lock` — only if `pipenv run install` refreshes hashes (do not change the `api-utils==1.0.0` pin)

The agent must not update files outside this list.

## Execution Notes

- Plan:
  1. Implement Profile control subclass in `src/services/profile_service.py`:
     - Inbound write RBAC (`_check_permission`) requiring `ROLE_CUSTOMER` or `ROLE_ADMIN` for `create` and `update`; delegating `read` to `super()`.
     - `create_profile`: stamps `customer_id` from token when caller is customer (not admin), calls `super().create_profile(...)`.
     - `update_profile`: checks permissions (admin, own profile, or same `customer_id`), strips `_id`/`created`/`saved`, stamps `saved`, encodes doc, and updates via `MongoIO.update_document`.
  2. Mount `POST ""` and `PATCH /<profile_id>` in `src/routes/profile_routes.py` using `ProfileService`.
  3. Update unit tests in `test/services/test_profile_service.py` and `test/routes/test_profile_routes.py`.
  4. Update `test/e2e/test_profile.py` with create and patch coverage.
  5. Run tests, format, lint, build, and container packaging verification.

- Test Results:
  - `pipenv run test`: 77 passed, 24 deselected in 0.19s.
  - `pipenv run lint`: Black check passed (0 errors across 38 files).
  - `pipenv run build`: Python compileall succeeded.
  - `pipenv run container`: Docker container build succeeded (`ghcr.io/mentor-forge/mentorhub_customer_api:latest`).
  - Grep confirmations: 0 hits for `from api_utils.services import .+Service` in `src/routes`; 0 hits for obsolete pagination terms in code/docs.
