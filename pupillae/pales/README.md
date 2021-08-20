pupillae -- pales
The general idea of pales is to help the user read the data collected.


pales.py:
pales reads the data from the source and turns it (or by delegation) into a format that is readable, or according to the format specified by the user, for the platform that the user is viewing the information on.


parser.py:
This file sends most of the variables to the query_builder to build the SQL query, but does (currently) construct the SQL WHERE statement while it is processing the tokens. As such, this file needs to be watched.


query_builder.py:
This file builds most of the SQL query.
query_builder uses strings to build the query and as such, this file needs to be watched.

Realistically, using a read-only postgres account for pales should be safe enough, or implementing the connection to be read-only in addition. Even then, the only variables that are used as strings to build the queries have been defined, or restricted, by the program, not the user.
