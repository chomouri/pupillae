pupillae - fons

TODO:
General "except psycopg2.Error as e:
	print(e)" is not great. Fix this so it works as part of a return message.

Fix up fons_gui.py:
- Convert png to jpg as part of scale_image()
	- Poss keep png format, check storing image as bytea in postgres and decode with discbot.
- Make a class for the database structure instead of a dict(?), (and move it to fons_pg(?))
- fons_pg has python str concat in get_col_details(). ? submit_p_sql()
	^ Line 70: sql.Literal(table_str)
- Create a function to ensure that the Parent Table is inserted before any Descendant Table. The fk_dict can be used for this but currently the tables are alphabetical and get sorted() anyway.
- fill out fons_gui section with window sizes
- pupillae DB tables can only have one PK and one FK. Composite keys are not supported.
- Currently submit_p_sql() uses "if all(isinstance(i, int) for i in response[0:2]):" and filters out the save_image function when m_id is None (i.e. when modif not submitted and (auto)FK in modif).
	^ Probably a checkbox in the modif window.

fons_img.py
- A Statement Context Manager for temporary files/directories would be good.
	ref: https://docs.python.org/3/reference/datamodel.html#context-managers
	https://docs.python.org/3/library/tempfile.html
- configparser is suddenly turning the tuple value (400, 400) into a string. Workaround: separate (int(x), int(y)).
- General Robustness is needed.
