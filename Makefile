VERSION := $(shell cat version.txt)

all: check-version-file
	@echo "Version: $(VERSION)"

tag: check-version-file check-tag-exists
	git tag -a $(VERSION) -m "Release Version $(VERSION)"
	git push origin $(VERSION)

check-version-file:
	@if [ ! -f version.txt ]; then \
		echo "Error: version.txt is empty"; \
		exit 1; \
	fi

check-tag-exists:
	@if git rev-parse $(VERSION) >/dev/null 2>&1; then \
		echo "Error: Git tag $(VERSION) already exists"; \
		exit 1; \
	fi