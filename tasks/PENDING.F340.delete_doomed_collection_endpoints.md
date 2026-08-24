# F340 – Delete doomed Card, Dashboard, and Subscription endpoints (E0)

**Status:** Pending  
**Type:** Feature  
**Depends On:** none  
**Description:** First task of F-CA14 / E0 in this repo. Remove `/api/card`, `/api/dashboard`, and `/api/subscription` (OpenAPI, routes, services, tests) **before** the 1.0.0 list migration so those collections are not rewritten to offset/size. Keep `/api/customer` and `/api/profile` GET as bases for later journey work. Confirm there are no Product routes (none today). No Stripe, no custom auth, no webhook routes. Stay on `api-utils==0.2.1`.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — Customer **controls** Customer, Payment, Profile; **creates** Event; **consumes** Journey, Rating, Note
- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml` — same control/create/consume map; Customer API port `8387`
- `tasks/_PLANNING.md` — MongoIO only; do not edit sibling repos
- `README.md`
- `src/server.py` — registers subscription, dashboard, and card blueprints
- `docs/openapi.yaml` — `/api/Card`, `/api/Dashboard`, `/api/Subscription` plus matching component schemas
- `test/test_server.py` — asserts those three prefixes are registered

**Doomed HTTP surface (delete entirely):**

| Prefix | Service | Routes | Unit tests | E2E |
| --- | --- | --- | --- | --- |
| `/api/card` | `src/services/card_service.py` | `src/routes/card_routes.py` | `test/services/test_card_service.py`, `test/routes/test_card_routes.py` | `test/e2e/test_card.py` |
| `/api/dashboard` | `src/services/dashboard_service.py` | `src/routes/dashboard_routes.py` | `test/services/test_dashboard_service.py`, `test/routes/test_dashboard_routes.py` | `test/e2e/test_dashboard.py` |
| `/api/subscription` | `src/services/subscription_service.py` | `src/routes/subscription_routes.py` | `test/services/test_subscription_service.py`, `test/routes/test_subscription_routes.py` | `test/e2e/test_subscription.py` |

**Keep unchanged** (still cursor lists until F343): `/api/customer`, `/api/profile`, `/api/event`, `/api/journey`, `/api/rating`, `/api/note`, `/api/config`, `/docs`, `/metrics`.

**Product:** grep `src/`, `test/`, and `docs/openapi.yaml` for Product paths. There are none today. If any admin-only Product route exists, delete it — Products belong on Admin API. Do **not** add Product, Stripe, Cognito login, or webhook endpoints.

**Why this is first:** F-CA14’s audit still lists Card, Dashboard, and Subscription as infinite-scroll migrations. Deleting them here avoids migrating three doomed lists to `execute_list_query` and then removing them.

Do **not** bump `Pipfile`. Do **not** migrate remaining lists. Do **not** drop Event.

## Goals

- `/api/card`, `/api/dashboard`, and `/api/subscription` are gone from OpenAPI, Flask registration, services, and tests.
- OpenAPI tags and `components.schemas` for Card, Dashboard, Subscription (and their Input/Update variants) are removed. Remaining paths still `$ref` `InfiniteScrollResponse` until F342.
- `src/server.py` no longer imports or logs those three blueprints.
- `test/test_server.py` asserts those prefixes are **absent** (404 / not in the URL map) and still asserts customer, profile, event, journey, rating, and note remain.
- No Product routes exist.
- Remaining cursor list code is untouched so `pipenv run test` stays green on `api-utils==0.2.1`.

## Testing Expectations

Run all commands from this API repository root.

- **Confirmation grep** (zero hits outside this task file)
  - `rg -n 'card_service|dashboard_service|subscription_service|create_card_routes|create_dashboard_routes|create_subscription_routes|/api/card|/api/dashboard|/api/subscription' src test docs/openapi.yaml README.md`
- **Unit / lint / build**
  - `pipenv run test`
  - `pipenv run lint`
  - `pipenv run build`
- **Packaging verification**
  - `pipenv run container`
  - `pipenv run api`
  - `curl -s http://localhost:8387/docs/openapi.yaml` — no Card/Dashboard/Subscription paths or schemas; customer and profile GET remain
  - `curl -s -o /dev/null -w '%{http_code}' http://localhost:8387/api/card` (and dashboard, subscription) — `404`

## Outputs

- `src/server.py` — unregister card, dashboard, subscription blueprints and log lines
- `docs/openapi.yaml` — remove Card, Dashboard, Subscription paths, tags, and component schemas
- `test/test_server.py` — drop registration assertions for the three prefixes; assert they are absent
- `README.md` — only if it names those endpoints
- **Delete:**
  - `src/services/card_service.py`
  - `src/services/dashboard_service.py`
  - `src/services/subscription_service.py`
  - `src/routes/card_routes.py`
  - `src/routes/dashboard_routes.py`
  - `src/routes/subscription_routes.py`
  - `test/services/test_card_service.py`
  - `test/services/test_dashboard_service.py`
  - `test/services/test_subscription_service.py`
  - `test/routes/test_card_routes.py`
  - `test/routes/test_dashboard_routes.py`
  - `test/routes/test_subscription_routes.py`
  - `test/e2e/test_card.py`
  - `test/e2e/test_dashboard.py`
  - `test/e2e/test_subscription.py`

The agent must not update files outside this list.

## Execution Notes
