query_builder.py:
This file builds most of the SQL query.

Realistically, using a read-only user for pales should be safe enough, or implementing the connection to be read-only. Even then, the only variables that are used to build the queries have been defined, or restricted, by the program, not the user.

Regarding building dynamic queries with keyword variables, the following may be useful:
https://www.psycopg.org/docs/advanced.html#adapting-new-types
https://www.psycopg.org/docs/extensions.html#psycopg2.extensions.adapt

parser.py:
This file sends most of the variables to the query_builder to build the SQL query, but does (currently) construct the SQL WHERE statement as it is processing the tokens.
