# AGENTS

## Scope

These instructions apply to the whole repository.

## Project summary

- Python client for the Trakt.tv API
- Main package: `trakt/`
- Tests: `tests/`
- Packaging and tooling: `setup.py`, `requirements.txt`, `testing-requirements.txt`, `Makefile`

## Repo-local instruction files

- No additional repo-local instruction files are checked in here.
- If additional instruction files appear later, read them before editing code.

## Key entry points

- API surface most agents touch first: `trakt/users.py`
- HTTP/client layer: `trakt/api.py`, `trakt/core.py`, `trakt/decorators.py`
- Shared data helpers: `trakt/mixins.py`, `trakt/utils.py`
- Errors and exception mapping: `trakt/errors.py`

## Architecture notes

- Many public methods are generator-based wrappers: they yield a URI, optional
  payload, then receive processed JSON back from the decorator layer.
- `trakt.core` keeps global client and auth state; changes there affect the
  entire package.
- `DataClassMixin` and `IdsMixin` are the main composition helpers for model
  wrappers.
- `ListEntry`, `PublicList`, and `UserList` show the preferred pattern for
  converting nested API payloads into typed objects.

## Development commands

- Install runtime dependencies: `python3 -m pip install -r requirements.txt`
- Install test and lint dependencies: `python3 -m pip install -r testing-requirements.txt`
- Combined setup: `make init`
- Run lint: `make style`
- Run tests: `make test`
- Run coverage: `make coverage`
- Run pytest directly: `python3 -m pytest tests`
- Run a single test: `python3 -m pytest tests/test_users.py::test_user_list -q`
- Run one file: `python3 -m pytest tests/test_users.py -q`
- Run by name: `python3 -m pytest tests/test_users.py -k test_user_list -q`
- Build release artifacts: `python3 -m pip install --upgrade build && python3 -m build`
- Legacy packaging still works: `python3 setup.py sdist bdist_wheel`
- Docs build: `make docs`

## Change guidance

- Keep edits narrow and local to the modules needed for the task.
- Prefer existing helpers and patterns over new abstractions.
- When touching `trakt/users.py`, watch for nested model conversion and
  mixin-based attribute delegation.
- When touching `trakt/api.py`, keep request, decode, and error handling paths
  aligned with current behavior.
- When touching tests, prefer updating mock payloads over mocking deeper
  internals.
- Keep tests deterministic and offline; `tests/conftest.py` patches the Trakt
  client with local mock responses.
- Do not delete or rename public APIs without a strong reason.
- Do not reformat unrelated files.
- If a change affects packaging, authentication, or response decoding, update
  tests before considering the work done.

## Code style

- Match the surrounding file. This codebase is not uniformly modernized, so
  local consistency matters more than broad cleanup.
- Import order should be stdlib, third-party, then local `trakt.*` imports.
  Let `isort` handle ordering.
- Prefer absolute imports within the package, which is the dominant style here.
- Preserve existing module docstrings and UTF-8 source headers in legacy files.
- Avoid wholesale reflowing. Keep line wrapping close to the nearby code.
- Use single quotes where the file already does so.
- Use type hints sparingly and locally. New public APIs can be annotated, but
  do not force a repo-wide typing migration.
- Common typing patterns here are `dataclass`, `NamedTuple`, `Optional`,
  `Union`, and small container annotations on public surfaces.
- Naming is conventional Python: `snake_case` for functions and variables,
  `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants, and leading
  underscores for private helpers.
- Public exports are often tracked with `__all__`; update it when the import
  surface changes on purpose.
- Keep module and class docstrings short and factual.
- The request layer uses generator-based decorators in `trakt.decorators`;
  preserve that pattern for new endpoints that fit the existing model.
- `trakt.core` stores global client and auth state; be careful when editing
  code that mutates module-level configuration.

## Error handling

- Use the repository’s custom exceptions in `trakt.errors` for known Trakt
  failure modes.
- Raise `ValueError` for invalid user input and parameter validation.
- Reserve `RuntimeError` for internal impossible states, not ordinary bad
  input.
- Do not swallow exceptions unless the surrounding code already does that for
  compatibility.
- Preserve the current `BadResponseException` behavior when JSON decoding
  fails.
- Follow the existing `HttpClient` and `TokenAuth` patterns instead of adding
  a new request stack.

## Data and models

- Many response objects are thin wrappers over API payloads; preserve fields
  that are already exposed.
- Prefer explicit copying or filtering when normalizing JSON unless the
  current module intentionally mutates the input.
- Keep list and collection classes iterable when the public API exposes them
  that way.
- If you add new model properties, make sure they do not break existing
  `__getattr__` delegation in mixins and dataclasses.
- Keep public return types stable. The tests generally assert classes, counts,
  and a few important field values.

## Packaging notes

- `setup.py` reads `README.rst` and `requirements.txt`; keep those files in
  sync with packaging changes.
- `requirements.txt` is runtime-only; `testing-requirements.txt` adds pytest,
  pytest-cov, and flake8.
- The docs workflow depends on `make docs` and may rewrite
  `trakt/__version__.py` from git tags.
- If you touch packaging metadata, check the release workflow as well as the
  local build command.
- Avoid adding a second packaging path unless the repo already needs it.

## Validation

- Run `pytest` for behavior changes.
- For CLI or packaging changes, run the relevant Makefile target too.
- For a single test, use `python3 -m pytest tests/test_users.py::test_user_list -q`.
- For import-only changes, run `pre-commit run isort --files <touched files>`
  or the equivalent touched-files-only `isort` invocation.
- When a test fails because of data-shape drift, update the mock payloads and
  the assertions together.
- Before finishing, sanity-check the exact command an agent would run for the
  change.

## Commit guidelines

- Prefer atomic commits: one intent, one self-contained change.
- Keep commits small enough to review and revert independently.
- Separate refactors, behavior changes, tests, and docs when practical.
- Follow the principles from https://cbea.ms/git-commit/.
- Use a short imperative subject line.
- Include a blank line after the subject.
- Add a `Co-authored-by` trailer for LLM-assisted commits.
