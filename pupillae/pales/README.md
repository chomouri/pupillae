pales.py:
https://www.postgresql.org/docs/13/queries-limit.html
Hardcoded ext for jpg for saved_dir image upload.
Need to move conf.ini section because pales is very much not using fons_gui for this, ... although the images are intended to be exclusively saved by fons_gui. 

parser.py:
This file sends most of the variables to the query_builder to build the SQL query, but does (currently) construct the SQL WHERE statement as it is processing the tokens.


query_builder.py:
This file builds most of the SQL query.

Realistically, using a read-only user for pales should be safe enough, or implementing the connection to be read-only. Even then, the only variables that are used to build the queries have been defined, or restricted, by the program, not the user.

Regarding building dynamic queries with keyword variables, the following may be useful:
https://www.psycopg.org/docs/advanced.html#adapting-new-types
https://www.psycopg.org/docs/extensions.html#psycopg2.extensions.adapt
