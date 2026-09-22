.PHONY: help install validate validate-spelling clean check-uv

help:
	@echo "aap-skills"
	@echo ""
	@echo "Available targets:"
	@echo "  install           - Install Python dependencies (requires uv)"
	@echo "  validate          - Run all validation checks (skills + spelling)"
	@echo "  validate-spelling - Run codespell spell check"
	@echo "  clean             - Remove generated files"
	@echo ""
	@echo "Requirements:"
	@echo "  uv - Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"

check-uv:
	@command -v uv >/dev/null 2>&1 || { \
		echo "Error: uv is not installed"; \
		echo ""; \
		echo "Install uv with:"; \
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo ""; \
		echo "Or visit: https://github.com/astral-sh/uv"; \
		exit 1; \
	}

install: check-uv
	@echo "Installing Python dependencies with uv..."
	@uv sync --group dev
	@echo "Dependencies installed!"

validate: check-uv
	@EXIT=0; \
	echo ""; \
	echo "=== Validating AAP skills..."; \
	uv run python scripts/validate_skills.py || EXIT=1; \
	echo "=== Running spell check..."; \
	$(MAKE) validate-spelling || EXIT=1; \
	echo ""; \
	if [ $$EXIT -eq 0 ]; then \
		echo "✅ All validations passed!"; \
	else \
		echo "❌ Validation failed"; \
	fi; \
	exit $$EXIT

validate-spelling: check-uv
	@echo "Running spell check with codespell..."
	@uv run codespell
	@echo "✅ Spell check passed!"

clean:
	@echo "Cleaning generated files..."
	@rm -rf .validate/
	@echo "Cleaned!"
