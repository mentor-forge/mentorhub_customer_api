# F343 – Pin api-utils 1.0.0 and migrate remaining lists

**Status:** Pending  
**Type:** Feature  
**Depends On:** `F342_openapi_1_0_0_list_gets`  
**Description:** F-CA14 owns this pin. Bump `api-utils` from `0.2.1` to `1.0.0` **in the same change** as the remaining list-contract migration — 1.0.0 does not export `execute_infinite_scroll_query`. Mount shared GET factories for Profile, Event, Note, and Journey; keep local `execute_list_query` only for Customer and Rating. Lands in the same PR as F340–F342. Do **not** add Profile POST/PATCH (F344–F345).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — Customer **controls** Customer, Payment, Profile; **creates** Event; **consumes** Journey, Rating, Note
- `../mentorhub/DeveloperEdition/standards/api_standards.md` — routes are HTTP-only; RBAC in services; MongoIO only
- `tasks/_PLANNING.md` — `pipenv run install` after Pipfile changes (CodeArtifact; run `mh` first). Do not call `mongo.get_collection(...)`. Encode ids at the MongoIO boundary.
- `README.md`
- `../mentorhub_api_utils/README.md` — subclass pattern; `create_*_get_routes(service_cls)` then add POST on the returned blueprint; list GET is a JSON array; `offset`/`size` headers only
- `../mentorhub_api_utils/api_utils/routes/shared_get_routes.py`
- `../mentorhub_api_utils/api_utils/flask_utils/list_request.py` — `parse_list_request`
- `../mentorhub_api_utils/api_utils/mongo_utils/list_query.py` — `build_match_filter`, `execute_list_query(collection_name, ...)`
- `Pipfile` / `Pipfile.lock` — currently `api-utils==0.2.1`
- `src/server.py` — keep existing `/api/*` prefixes (card/dashboard/subscription already gone)
- `docs/openapi.yaml` — F342 list contract
- Current services: `src/services/customer_service.py`, `profile_service.py`, `event_service.py`, `journey_service.py`, `note_service.py`, `rating_service.py`
- Current routes: `src/routes/customer_routes.py`, `profile_routes.py`, `event_routes.py`, `journey_routes.py`, `note_routes.py`, `rating_routes.py`
- Unit tests under `test/services/` and `test/routes/`; E2E under `test/e2e/`
- `test/test_server.py` — Journey list GET at `/api/journey` will 404 after the factory (by-id only)
- `test/e2e/e2e_auth.py` — admin persona is unrestricted on shared outbound GET; add `profile_id` / `customer_id` only if a non-admin assertion needs them

**External prerequisite:** `api-utils==1.0.0` must resolve from the CodeArtifact index. If `pipenv run install` cannot resolve 1.0.0, set **Status** to `Blocked` and stop.

**Pin:** this task owns `api-utils==1.0.0`. Install with `pipenv run install`. Do **not** use bare `pipenv install`. Use `scripts/pipenv-lock.sh` if lock hashes must be regenerated first.

**Why pin and Python land together:** this repo still calls `execute_infinite_scroll_query`. 1.0.0 removed that helper. Subclasses cannot inherit 1.0.0 parents while the process pins `0.2.1`. Card/Dashboard/Subscription were deleted in F340 so they are not in this migration.

### Shared GET factories (Event, Note, Journey, Profile)

```python
from api_utils.routes.shared_get_routes import create_profile_get_routes
from src.services.profile_service import ProfileService

def create_profile_routes():
    bp = create_profile_get_routes(ProfileService)
    # POST/PATCH added in F345
    return bp
```

Thin subclasses — convert `@staticmethod` to `@classmethod`. Routes import **local** subclasses only (never `from api_utils.services import ProfileService` in `src/routes/`).

| Local class | Parent | Inherit | Keep local | Factory |
| --- | --- | --- | --- | --- |
| `ProfileService` | `api_utils.services.ProfileService` | `get_profiles`, `get_profile`, `get_profile_by_token`, `create_profile` | none (no `update_profile` yet) | `create_profile_get_routes` — list + by-id |
| `EventService` | `api_utils.services.EventService` | `get_events`, `create_event` (returns the **document**) | `get_event` (shared has no by-id) | `create_event_get_routes` — list only; then `POST ""` and `GET /<event_id>` |
| `NoteService` | `api_utils.services.NoteService` | `get_notes_for_resource` | `get_note` (shared has no by-id) | `create_note_get_routes` — list requires `resource_id`; then `GET /<note_id>` |
| `JourneyService` | `api_utils.services.JourneyService` | `get_journey` | **delete** `get_journeys` | `create_journey_get_routes` — by-id only |

Do **not** 403 on GET in these subclasses; outbound filters live on the shared class. Re-export `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER` (and Event/Note equivalents) from the local module only if something still imports them; factories walk MRO.

Event POST: `created = EventService.create_event(...)` then `jsonify(created), 201`. Do not assume a bare id. Shared `create_event` overwrites client `context` from the token.

If a shared GET omits a live dictionary field that F341 documented, do not fork the parent. Record a harvest follow-up in **Execution Notes**. Prefer inheriting the shared method.

### Local `execute_list_query` (Customer, Rating)

No shared Customer or Rating service. Customer **controls** Customer; Mentee **controls** Rating (this API consumes). Do **not** call `mongo.get_collection(...)`.

```python
from api_utils.flask_utils.list_request import parse_list_request
from api_utils.mongo_utils import (
    build_match_filter,
    execute_list_query,
)

offset, size, filters, sort_by = parse_list_request(
    request, CUSTOMER_LIST_FILTERS, CUSTOMER_LIST_ORDER
)
match = build_match_filter({}, filters or {}, CUSTOMER_LIST_FILTERS)
return execute_list_query(
    config.CUSTOMER_COLLECTION_NAME,
    match=match,
    sort_by=sort_by,
    offset=offset,
    size=size,
)
```

Declare `CUSTOMER_LIST_FILTERS` / `CUSTOMER_LIST_ORDER` next to `CustomerService` and `RATING_LIST_FILTERS` / `RATING_LIST_ORDER` next to `RatingService`. Name `contains` is the existing filter; keep current allowed sort fields (`name`, `description`). List methods return a **plain list**, not `{items, has_more, next_cursor}`. By-id `get_customer` / `get_rating` stay on `MongoIO.get_document`.

Customer and Rating routes stay local (no factory): `GET ""` uses `parse_list_request` + the service list method + `jsonify(array), 200`; `GET /<id>` unchanged. `@handle_route_exceptions` stays.

### What NOT to do

- Do not keep a local copy of `execute_infinite_scroll_query`.
- Do not pass raw collections from `MongoIO.get_collection` into list helpers.
- Do not add Profile PATCH or Profile POST HTTP (F344–F345). Inheriting `create_profile` on the class is required; do not mount it yet.
- Do not re-add Card, Dashboard, Subscription, Product, Stripe, or webhook routes.
- Do not implement a local Journey list.

## Goals

- `Pipfile` and `Pipfile.lock` pin `api-utils==1.0.0` (CodeArtifact `[[source]]` unchanged; keep the comment that public PyPI `api-utils` is unrelated).
- Zero `execute_infinite_scroll_query`, `after_id`, `has_more`, or `next_cursor` in `src/`, `test/`, or `docs/openapi.yaml`.
- List endpoints use `offset`/`size` headers and return a JSON array.
- Shared GET factories used where specified; Customer and Rating lists use `execute_list_query` with a collection **name**.
- Routes import services from `src.services.*` only.
- `README.md` states the `api-utils==1.0.0` pin, local subclasses, and the list GET contract.
- Unit and E2E tests match F342 (array bodies; Note list 400 without `resource_id`; Journey list 404; Event POST returns the document).

## Testing Expectations

Run all commands from this API repository root.

- **Install**
  - `mh` once per shell if CodeArtifact credentials are not already available
  - `pipenv run install`
  - Confirm `importlib.metadata.version("api-utils") == "1.0.0"`
- **Confirmation greps** (zero hits)
  - `rg 'execute_infinite_scroll_query|after_id|has_more|next_cursor' --glob '*.py' --glob 'docs/openapi.yaml'`
  - `rg "from api_utils.services import .+Service" src/routes`
  - `rg "get_collection" src/services`
- **Unit / lint / build**
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
  - Service tests: list methods return a `list`; no cursor keys; Customer/Rating mock `execute_list_query` (not a raw collection); subclasses expose inherited GET/create methods; no `update_profile` yet
  - Route tests: patch `src.routes.<module>.<Service>.*`; send `offset`/`size` **headers**; assert JSON array; Note list without `resource_id` is 400; Journey collection GET is 404
- **Dev E2E**
  - `pipenv run db` if needed
  - `pipenv run dev` (separate terminal or background)
  - `pipenv run e2e`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `pipenv run e2e` against the containerized API
  - `curl -s http://localhost:8387/docs/openapi.yaml` — F342 list contract; no cursor envelope

## Outputs

- `Pipfile` — pin `api-utils==1.0.0`
- `Pipfile.lock` — refresh via `pipenv run install` (use `scripts/pipenv-lock.sh` if hashes must be regenerated first)
- `README.md` — 1.0.0 pin, local subclasses, list GET contract
- `src/services/customer_service.py`
- `src/services/rating_service.py`
- `src/services/profile_service.py`
- `src/services/event_service.py`
- `src/services/note_service.py`
- `src/services/journey_service.py`
- `src/routes/customer_routes.py`
- `src/routes/rating_routes.py`
- `src/routes/profile_routes.py`
- `src/routes/event_routes.py`
- `src/routes/note_routes.py`
- `src/routes/journey_routes.py`
- `src/routes/__init__.py` — only if exports are needed
- `src/server.py` — only if blueprint constructors or log lines must change
- `test/services/test_customer_service.py`
- `test/services/test_rating_service.py`
- `test/services/test_profile_service.py`
- `test/services/test_event_service.py`
- `test/services/test_note_service.py`
- `test/services/test_journey_service.py`
- `test/routes/test_customer_routes.py`
- `test/routes/test_rating_routes.py`
- `test/routes/test_profile_routes.py`
- `test/routes/test_event_routes.py`
- `test/routes/test_note_routes.py`
- `test/routes/test_journey_routes.py`
- `test/test_server.py` — Journey list GET is 404; remaining prefixes still registered
- `test/e2e/test_customer.py`
- `test/e2e/test_rating.py`
- `test/e2e/test_profile.py`
- `test/e2e/test_event.py`
- `test/e2e/test_note.py` — required `resource_id`; expect a JSON array
- `test/e2e/test_journey.py` — by-id only; drop list envelope assertions
- `test/e2e/e2e_auth.py` — only if identity claims are required for E2E

The agent must not update files outside this list.

## Execution Notes
