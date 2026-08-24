# F344 – OpenAPI Profile POST and PATCH (F-CA15)

**Status:** Pending  
**Type:** Feature  
**Depends On:** `F343_pin_1_0_0_and_migrate_lists`  
**Description:** First F-CA15 task. Document Customer-control Profile writes on the existing GET blueprint: `POST /api/profile` and `PATCH /api/profile/{ProfileId}`. Do not re-bump `api-utils`. No Python — F343 already serves Profile GET via `create_profile_get_routes`. Event POST is already documented.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — Customer **controls** Profile; Admin also **creates** Profile
- `../mentorhub/DeveloperEdition/standards/api_standards.md` — OpenAPI is the SPA contract
- `tasks/_PLANNING.md` — fetch Profile from the configurator if Input/Update fields are missing from the F341 `Profile` component
- `README.md`
- `../mentorhub_api_utils/README.md` — shared `create_profile` is global POST; PATCH lives on the Customer subclass
- `../mentorhub_api_utils/api_utils/services/profile_service.py` — `create_profile` returns the document; system-managed `_id` / `created` / `saved`
- `docs/openapi.yaml` — F342 GET list + by-id; Profile tag may still say read-only

**Add these operations** (same path casing as existing Profile GET in this document):

| Method and path | Body in | Body out | Notes |
| --- | --- | --- | --- |
| `POST /api/profile` | `ProfileInput` | `Profile` | `201`; Bearer; `401`/`403`/`400`/`500` |
| `PATCH /api/profile/{ProfileId}` | `ProfileUpdate` | `Profile` | `200`; Bearer; `401`/`403`/`404`/`400`/`500` |

`ProfileInput` / `ProfileUpdate` are writable Profile fields from the live dictionary **minus** `_id`, `created`, and `saved`. If F341’s `Profile` component is missing a field, re-fetch:

```bash
curl -X GET "http://localhost:8383/api/configurations/json_schema/Profile.yaml/latest/" -H "accept: application/json"
```

If the configurator is unavailable, set **Status** to `Blocked` and stop.

Keep F342 list GET (`Profile[]`, `offset`/`size` headers, no cursor, no `X-Pagination-*`). Do not add Payment, Product, Stripe, or webhook paths. Do not change Event POST.

Update the Profile tag/description from read-only to create + patch (Customer control).

## Goals

- Profile POST and PATCH are documented with Input/Update schemas that omit system-managed fields.
- List GET remains a JSON array with `offset`/`size` request headers.
- No `after_id`, `has_more`, `next_cursor`, or `X-Pagination-*`.
- The document remains valid OpenAPI 3.0.x.
- No Python, Pipfile, or README changes.

## Testing Expectations

Run all commands from this API repository root.

- **Spec validation**
  - `python3 -c "import yaml; yaml.safe_load(open('docs/openapi.yaml'))"`
  - Confirm `POST /api/profile` (`201` `Profile`) and `PATCH /api/profile/{ProfileId}` (`200` `Profile`); list GET unchanged; Event POST unchanged.
- **Unit / lint / build** (docs-only; HTTP writes land in F345)
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `curl -s http://localhost:8387/docs/openapi.yaml` — served spec includes Profile POST/PATCH

## Outputs

- `docs/openapi.yaml` — Profile POST/PATCH operations and Input/Update schemas

The agent must not update files outside this list.

## Execution Notes
