pupillae
A coven of tools to administer PnP RPGs.

daemons:
postgreSQL
discord bot

imps:
bones - a dice roller
fons - (i.e. god of wells and springs, Font of Knowledge) Create or enter data.
	- Enter miniature data into a database.
		^ fons_gui.py: DearPyGui.
	- Create randomised data for characters, settlements, and land, etc.


pales - (i.e. god of shepherds and flocks) Parse the data and package it for viewing in some manner.
	pupil: View database entries.
	- Discord bot scripts
	- Creating HTML formats for websites

TODO:
Current paths are dicey, especially for connecting to the postgres server via database.ini:
1) cd to pupillae.
2) source ./venv/bin/activate
3) python3 /pales/disc_bot.py

./conf/config.py contains a hardcoded relative path. --fix with os.path
check schema permissions on pgAdmin for fons

Fix up fons_gui.py:
- globals everywhere.
- Most functions.
- Use os.path properly
	- Fix hardcoded Linux file structures
- Convert png to jpg as part of scale_image()
	- move PIL commands to external script
	- Poss keep png format, check storing image as bytea in postgres and decode with discbot.
- Validate photo_path and other paths; create folders if needed.
- Make a class for the database structure instead of a dict(?), (and move it to fons_pg(?))

fons_pg has python str concat.
- Line 70: sql.Literal(table_str)
