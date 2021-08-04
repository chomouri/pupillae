pupillae
A coven of tools to administer PnP RPGs.

Status: Pre-alpha.
	Testing out downloading and installation. Adding necessary functions and features as discovered.

System Requirements:
	Linux, postgreSQL.

daemons:
postgreSQL
discord bot

imps:
- fons - (i.e. Roman god of wells and springs)
Purpose: Create or enter data.
	- Enter miniature data into a database.
		^ fons_gui.py: DearPyGui.
	- Create randomised data for characters, settlements, and land, etc.
		^ Currently this is just a dice roller.

- pales - (i.e. Roman god of shepherds and flocks)
Purpose: Parse the data and package it for viewing in some manner.
	- Discord bot scripts

Current paths are dicey, especially for connecting to the postgres server via conf.ini.
The import of config.py may be  
