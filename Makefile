run:
	./.venv/bin/python3 ./main.py

install:
	./.venv/bin/pip install -r requirements.txt

resetdb:
	rm Solaire.db
	sqlite3 Solaire.db ""

setup:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Creating database..."
	sqlite3 Solaire.db
	@echo "Setup complete"
	@echo "Please create .env file with structure"
	@echo "DISCORD_TOKEN=<bot token>"
	@echo "CID=<channel id>"
	@echo "GID=<server id>"
	@echo "ADMIN=<user id>"