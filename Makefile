.PHONY: sync

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
	uv pip install -e .

sync:
	uv sync --group dev
