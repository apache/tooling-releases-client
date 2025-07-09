.PHONY: sync

bump: install
	uv run atr dev stamp

check:
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
	rm -f uv.lock
	uv lock
	uv pip install -e .

sync:
	uv sync --group dev
