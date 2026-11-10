.PHONY: build bump check commit pre-commit sync sync-all update-hooks

build:
	uv build

bump:
	@# This assumes that we have the latest version of "dev stamp"
	@# If not, run "uv pip install -e ." first
	@# The dev stamp command adds --exclude-newer to the uv.lock file
	uv run --locked atr dev stamp
	uv lock --upgrade
	uv sync --locked --all-groups

check: pre-commit bump
	@# We run lint modifications first, then update the version
	@# We do not consider the following a lint as it runs all test cases always
	uv run --locked pytest -q

commit:
	git add -A
	git commit
	git pull
	git push

pre-commit:
	git add -A
	uv run --locked prek run --all-files

sync:
	uv sync --locked --no-dev

sync-all:
	uv sync --locked --all-groups

update-hooks:
	uv run --locked prek update
