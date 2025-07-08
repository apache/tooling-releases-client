.PHONY: sync

check:
	git add -A
	uv run pre-commit run --all-files

commit:
	git add -A
	git commit
	git pull
	git push

install:
	uv pip install -e .

sync:
	uv sync --group dev
