.PHONY: lint build serve dev clean

lint:
	ruff check scripts/ && ruff format --check scripts/ && mypy scripts/ --ignore-missing-imports --scripts-are-modules
	yamllint -c .yamllint.yml .
	eslint assets/js/

build: lint
	rm -rf _site
	bundle exec jekyll build

serve: build
	bundle exec jekyll serve

dev:
	pip install -q requests pyyaml Pillow python-dateutil
	python scripts/gen_fixtures.py
	bundle exec jekyll serve

clean:
	rm -rf _site _posts archive/