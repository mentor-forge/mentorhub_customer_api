# Mentor Hub — Customer API

## Prerequisites
- Mentor Hub [Developers Edition](https://github.com/mentor-forge/mentorhub/blob/main/CONTRIBUTING.md)
- Developer [API Standard Prerequisites](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md)

## Developer Commands

```bash
## Install dependencies (run `mh` first for CodeArtifact auth)
pipenv run install

# start backing db container 
# Container Related commands use `de down` before starting the requested containers
pipenv run db

## run unit tests 
pipenv run test

## run api server in dev mode - captures command line, serves API at localhost:8387
pipenv run dev

## run E2E tests (assumes running API at localhost:8387)
pipenv run e2e

## run tests with coverage report
pipenv run coverage

## build application (pre-compiles Python code)
pipenv run build

## build container 
pipenv run container

## Run the backing database and api containers
pipenv run api

## Run the full microservice (db+api+spa)
pipenv run service

## format code
pipenv run format

## lint code
pipenv run lint
```

## Project Structure

- `src/` - Main package containing:
  - `server.py` - API entrypoint
  - `routes/` - HTTP request/response handlers
  - `services/` - Business logic and RBAC

- `test/` - Test suite with matching directory structure:
  - `routes/` - Route unit tests
  - `services/` - Service unit tests
  - `e2e/` - End-to-end tests flagged with `@pytest.mark.e2e`

## API Endpoints

See the [Open API Specifications](./docs/openapi.yaml) for details on the API.

The Customer API is built with `api-utils==1.0.2` and implements the 1.0.0 list GET contract (`offset`/`size` request headers, JSON array responses). The token dict from `create_flask_token()` uses `display_name`.

- **Shared GET Factories** (`api_utils.routes.shared_get_routes` + local service subclasses):
  - `/api/profile`: List & Get by ID (`ProfileService`)
  - `/api/event`: List (`EventService` shared) + local POST & Get by ID
  - `/api/note`: List by `resource_id` (`NoteService` shared) + local Get by ID
  - `/api/journey`: Get by ID (`JourneyService` shared)
- **Local List Handlers** (`api_utils.mongo_utils.execute_list_query`):
  - `/api/customer`: List & Get by ID (`CustomerService`)
  - `/api/rating`: List & Get by ID (`RatingService`)

For E2E, mint a Bearer token via `test/e2e/e2e_auth.py` (`get_auth_token()`) with `pipenv run dev` (matching `JWT_SECRET`).

### Simple Curl Commands:
```bash
# Bearer token for local dev (same JWT settings as pipenv run dev / e2e):
export TOKEN="$(PYTHONPATH=. pipenv run python -c 'from test.e2e.e2e_auth import get_auth_token; print(get_auth_token())')"

# Get the API Configuration
curl http://localhost:8387/api/config \
  -H "Authorization: Bearer $TOKEN"

```