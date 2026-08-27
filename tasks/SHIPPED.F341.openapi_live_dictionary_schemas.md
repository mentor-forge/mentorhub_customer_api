# F341 – OpenAPI component schemas from the live configurator

**Status:** Shipped  
**Type:** Feature  
**Depends On:** `F340_delete_doomed_collection_endpoints`  
**Description:** Second F-CA14 task. Replace template `components.schemas` for the collections this API still serves with the latest JSON schemas from the running MongoDB configurator. Do this **after** E0 deletion so Card/Dashboard/Subscription are not refreshed and then thrown away. Docs only — no Python, no pin. List-GET pagination stays cursor-shaped until F342.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md` — OpenAPI is the SPA contract; configurator is the schema source of truth
- `tasks/_PLANNING.md` — fetch schemas with `curl` against the running configurator; do **not** read dictionary YAML from `mentorhub_mongodb_api`
- `README.md`
- `docs/openapi.yaml` — after F340, remaining domain schemas are `Event`, `EventInput`, `Profile`, `Customer`, `Journey`, `Rating`, `Note`

**Relevant collections** (fetch each; these are the dictionaries this API still exposes):

| Dictionary | OpenAPI component(s) to replace |
| --- | --- |
| `Customer` | `Customer` |
| `Profile` | `Profile` |
| `Event` | `Event`, `EventInput` (input = writable client fields; no `_id` / `created` / `context`) |
| `Journey` | `Journey` |
| `Rating` | `Rating` |
| `Note` | `Note` |

Start the backing database if needed (`pipenv run db`), then:

```bash
curl -X GET "http://localhost:8383/api/configurations/json_schema/Customer.yaml/latest/" -H "accept: application/json"
curl -X GET "http://localhost:8383/api/configurations/json_schema/Profile.yaml/latest/" -H "accept: application/json"
curl -X GET "http://localhost:8383/api/configurations/json_schema/Event.yaml/latest/" -H "accept: application/json"
curl -X GET "http://localhost:8383/api/configurations/json_schema/Journey.yaml/latest/" -H "accept: application/json"
curl -X GET "http://localhost:8383/api/configurations/json_schema/Rating.yaml/latest/" -H "accept: application/json"
curl -X GET "http://localhost:8383/api/configurations/json_schema/Note.yaml/latest/" -H "accept: application/json"
```

If the configurator is unavailable or a listed dictionary has no latest schema, set **Status** to `Blocked` and stop. Do not fall back to YAML files in other repos. Do not fetch Card, Dashboard, Subscription, or Product.

Map BSON/configurator types to OpenAPI 3.0 (`objectId` → 24-hex string, dates → `date-time` strings). Keep existing `Breadcrumb` if the live schema still uses it. Drop template-only properties the dictionary no longer has (for example Event `name` / `description` if the live Event is `type` + `context`).

**Do not** change path operations, `after_id`, `InfiniteScrollResponse`, or Python. F342 rewrites list GET contracts against these updated `$ref`s.

**Modified services / harvest:** this task is OpenAPI-only. Full-document GET/PATCH in later tasks pass Mongo documents through, so schema fields do not require projections here. If a live field **cannot** be represented honestly without changing a **shared** `api_utils` service:

- Do not edit `mentorhub_api_utils` from this repo.
- Do not fork a local copy of a shared service.
- Record the gap in **Execution Notes** (collection, field, why shared GET would omit it) and set **Status** to `Blocked` so a harvest-to-utils issue can land first.

Customer and Rating stay local in F343; they do not need a harvest for schema-only OpenAPI updates.

## Goals

- `Customer`, `Profile`, `Event` / `EventInput`, `Journey`, `Rating`, and `Note` component schemas match the live configurator dictionaries.
- No Card, Dashboard, Subscription, or Product schemas are re-introduced.
- Path operations and the cursor envelope are unchanged.
- The document remains valid OpenAPI 3.0.x.
- No Python, Pipfile, or README changes.

## Testing Expectations

Run all commands from this API repository root.

- **Spec validation**
  - `python3 -c "import yaml; yaml.safe_load(open('docs/openapi.yaml'))"`
  - Confirm the six remaining domain schemas include live fields from the curl responses; doomed schemas stay gone; list operations still document `after_id` / `has_more` / `next_cursor` (F342).
- **Unit / lint / build** (docs-only; suite must still pass on `api-utils==0.2.1`)
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `curl -s http://localhost:8387/docs/openapi.yaml` — served file includes updated component schemas

## Outputs

- `docs/openapi.yaml` — replace remaining domain component schemas from configurator JSON

The agent must not update files outside this list.

## Execution Notes

- Plan:
  1. Query live configurator at `http://localhost:8383/api/configurations/json_schema/<Dictionary>.yaml/latest/` for Customer, Profile, Event, Journey, Rating, and Note.
  2. Map configurator JSON schemas to OpenAPI 3.0 component schemas:
     - Use `$ref: '#/components/schemas/Breadcrumb'` for `created` and `saved` breadcrumb objects.
     - Represent `objectId` as string with pattern `'^[0-9a-fA-F]{24}$'`.
     - Construct `EventInput` without system-managed fields (`_id`, `created`, `context`).
  3. Replace schemas in `docs/openapi.yaml`.
  4. Validate OpenAPI spec with python yaml.safe_load, run unit tests, lint, and build.

- Test Results:
  - Fetched live configurator JSON schemas for Customer, Profile, Event, Journey, Rating, and Note from `http://localhost:8383`.
  - Component schemas in `docs/openapi.yaml` accurately mapped to OpenAPI 3.0.3 components.
  - Spec validation: `python3 -c "import yaml; yaml.safe_load(open('docs/openapi.yaml'))"` passed with 0 errors.
  - `pipenv run test`: 127 passed, 24 deselected.
  - `pipenv run lint`: Black check passed with 0 errors.
  - `pipenv run build`: Passed.

