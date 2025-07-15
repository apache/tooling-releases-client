.PHONY: build bump check commit pre-commit update-deps

build:
	uv build

bump:
	@# This assumes that we have the latest version of "dev stamp"
	@# If not, run "uv pip install -e ." first
	uv run atr dev stamp
	@# Suppress the warning about ignoring the existing lockfile
	rm -f uv.lock
	@# This writes the new stamp into the uv.lock file and upgrades the package
	@# We do not have to use --upgrade as that is only for dependencies
	uv sync

check: pre-commit bump
	@# We run lint modifications first, then update the version
	@# We do not consider the following a lint as it runs all test cases always
	uv run pytest -q

commit:
	git add -A
	git commit
	git pull
	git push

pre-commit:
	git add -A
	uv run pre-commit run --all-files

update-deps:
	uv lock --upgrade
	uv sync
