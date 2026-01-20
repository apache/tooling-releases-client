.PHONY: build bump check commit pre-commit sync sync-all

build:
	uv build --frozen

bump:
	@# This assumes that we have the latest version of "dev stamp"
	@# If not, run "uv pip install -e ." first
	@# The dev stamp command adds --exclude-newer to the uv.lock file
	uv run --frozen atr dev stamp
	uv lock --upgrade
	uv sync --frozen --all-groups

check: pre-commit bump
	@# We run lint modifications first, then update the version
	@# We do not consider the following a lint as it runs all test cases always
	uv run --frozen pytest -q

commit:
	git add -A
	git commit
	git pull
	git push

pre-commit:
	git add -A
	uv run --frozen pre-commit run --all-files

sync:
	uv sync --frozen --no-dev

sync-all:
	uv sync --frozen --all-groups
