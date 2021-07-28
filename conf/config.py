#!/usr/bin/python
from configparser import ConfigParser
import os


def config(filename='./conf/conf.ini', section='general'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    if not os.path.isfile(filename):
        path = os.getcwd()
        raise Exception('{0} not found in {1}'.format(filename, path))

    # get section, default to general
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
