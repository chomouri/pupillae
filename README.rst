pupillae
A coven of tools to assist PnP RPGs.

Status: Pre-alpha.
	Testing out downloading and installation. Adding necessary functions and features as discovered/required.

Other-than-Python dependencies (ref: pyproject.toml):
	Linux, postgreSQL.

To Install:
	1. Clone this github repo.
	2. Open your poetry shell in the directory.
	3. Execute `poetry install`
	4. Configure conf.ini with appropriate details using the template as a guide.

daemons:
	- discord bot

imps:
- fons - (i.e. Roman god of wells and springs)
Purpose: Create or enter data.
	- Enter miniature data into a database.
		^ fons_gui.py
	- Create randomised data for characters, settlements, and land, etc.
		^ Currently this is just a dice roller.

- pales - (i.e. Roman god of shepherds and flocks)
Purpose: Parse the data and package it for viewing in some manner.
	- Discord bot scripts

Current paths are dicey, especially for connecting to the postgres server via conf.ini.
Various tweaks may be required to adapt the tools to your use, but I hope they provide some use.
