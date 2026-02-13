.PHONY: serve ui sync

serve: sync
	@uv run idun agent serve --source=file --path=app/agent/config.yaml 

ui:
	@uv run streamlit run streamlit/app.py

sync:
	@uv sync
