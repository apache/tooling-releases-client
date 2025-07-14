.PHONY: build bump check commit install sync

build:
	uv build

bump: install
	@# We install above to ensure that dev stamp is up to date
	uv run atr dev stamp
	rm -f uv.lock
	uv lock

check: bump
	@# Always bump to ensure that we check the exact current version
	git add -A
	uv run pre-commit run --all-files
	@# TODO: Move this to .pre-commit-config.yaml?
	@# It always runs on all files, so it's not a good traditional lint
	uv run pytest -q

commit:
	git add -A
	git commit
	git pull
	git push

install:
	uv pip install -e .

sync:
	uv sync --group dev
