# F342 – OpenAPI for 1.0.0 list GETs (offset/size, JSON array)

**Status:** Pending  
**Type:** Feature  
**Depends On:** `F341_openapi_live_dictionary_schemas`  
**Description:** Third F-CA14 task. Document the 1.0.0 Get List contract that F343 will implement: JSON-array bodies, `offset`/`size` request headers only, no cursor envelope. Drop the local Journey **list** (shared Journey has no list; factory is by-id only). Keep Customer/Profile/Event/Rating/Note lists and all remaining by-id GETs. No Profile POST/PATCH (F-CA15 / F344). No Python, no pin.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — Customer **controls** Customer and Profile; **creates** Event; **consumes** Journey, Rating, Note
- `../mentorhub/DeveloperEdition/standards/api_standards.md` — OpenAPI is the SPA contract
- `tasks/_PLANNING.md`
- `README.md`
- `../mentorhub_api_utils/README.md` — list GET is a JSON **array**; pagination is request headers `offset` (default `0`) and `size` (default `20`, max `100`); query `contains` / `in_list` plus `sort_by` / `order`; no cursor envelope; no `X-Pagination-*` response headers
- `../mentorhub_api_utils/api_utils/routes/shared_get_routes.py` — factory shapes: profile list + by-id; event list only (optional `profile_id`); note list requires `resource_id`; journey **by-id only**
- `../mentorhub_api_utils/api_utils/services/profile_service.py` — `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER`
- `../mentorhub_api_utils/api_utils/services/event_service.py` — `EVENT_LIST_FILTERS` / `EVENT_LIST_ORDER`
- `../mentorhub_api_utils/api_utils/services/note_service.py` — `NOTE_LIST_FILTERS` / `NOTE_LIST_ORDER`; list is `get_notes_for_resource`
- `docs/openapi.yaml` — F341 live schemas; remaining lists still use `after_id` / `InfiniteScrollResponse`

**Do not change these existing operations** (HTTP contract stays except list pagination/envelope where listed below):

| Method and path | Keep |
| --- | --- |
| `GET /api/customer/{CustomerId}` | Customer by-id |
| `GET /api/profile/{ProfileId}` | Profile by-id (plain Profile) |
| `POST /api/event` | Event create (`EventInput` from F341) |
| `GET /api/event/{EventId}` | local by-id (factory is list-only) |
| `GET /api/journey/{JourneyId}` | Journey by-id (factory) |
| `GET /api/rating/{RatingId}` | Rating by-id |
| `GET /api/note/{NoteId}` | Note by-id (factory is list-only) |
| `GET /api/config`, `/metrics`, `/docs` | platform |

**Do not add** Profile POST/PATCH, Payment, Product, Stripe, or webhook paths. Customer **controls** Profile writes in F344–F345.

**Update these list GETs** — `offset`/`size` **request** headers (defaults `0` / `20`, max `100`); `200` body is a JSON **array** of the F341 component; query `sort_by` / `order`; **delete** `after_id`, `limit`, and the `{items, has_more, next_cursor}` envelope. No `X-Pagination-*` response headers.

| Method and path | Body out | Filters / notes |
| --- | --- | --- |
| `GET /api/customer` | `Customer[]` | `name` `contains`; order from current allowed sort fields (`name`, `description`) |
| `GET /api/profile` | `Profile[]` | shared `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER` |
| `GET /api/event` | `Event[]` | shared `EVENT_LIST_FILTERS` / `EVENT_LIST_ORDER`; optional query `profile_id` |
| `GET /api/rating` | `Rating[]` | `name` `contains`; order from current allowed sort fields (`name`, `description`) |
| `GET /api/note` | `Note[]` | **required** query `resource_id`; shared `NOTE_LIST_FILTERS` / `NOTE_LIST_ORDER` (not a free-text `name` list) |

**Drop this operation** (do not replace with a local cursor or offset list):

| Method and path | Why |
| --- | --- |
| `GET /api/journey` (list) | Shared `JourneyService` has **no** list method; `create_journey_get_routes` is by-id only. E0 keeps Customer and Profile GET as later journey bases — not this template list. Implementing a local `execute_list_query` list here would be rework. Keep `GET /api/journey/{JourneyId}`. |

Remove `components.schemas.InfiniteScrollResponse` if nothing else `$ref`s it. After this task there must be **no** `after_id`, `has_more`, or `next_cursor` in `docs/openapi.yaml`.

Component schemas were updated in F341; do not Block on the configurator unless a list operation needs a new `$ref` that is missing.

## Goals

- Remaining list GETs declare `offset`/`size` request headers, `contains` / `in_list` filters from the table, `sort_by` / `order`, and a JSON-array `200` body.
- Journey list GET is removed; Journey by-id remains.
- Note list requires `resource_id`.
- No `after_id`, `has_more`, `next_cursor`, cursor envelope, or `X-Pagination-*` anywhere in this document.
- Profile remains GET-only (list + by-id). Event POST and Event/Note by-id stay.
- The document remains valid OpenAPI 3.0.x.
- No Python, Pipfile, or README changes.

## Testing Expectations

Run all commands from this API repository root.

- **Spec validation**
  - `python3 -c "import yaml; yaml.safe_load(open('docs/openapi.yaml'))"`
  - Confirm list `200` bodies are arrays; `offset`/`size` request headers present; Journey list gone; Journey by-id present; Note list requires `resource_id`; Profile has no POST/PATCH; zero `after_id` / `has_more` / `next_cursor` in the file.
- **Unit / lint / build** (docs-only; Python still serves cursor lists on `api-utils==0.2.1`)
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `curl -s http://localhost:8387/docs/openapi.yaml` — served spec matches the list contract above

## Outputs

- `docs/openapi.yaml` — 1.0.0 list GET contract; drop Journey list and `InfiniteScrollResponse`

The agent must not update files outside this list.

## Execution Notes
