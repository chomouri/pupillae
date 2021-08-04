#!/usr/bin/python
import os
from datetime import datetime
from configparser import ConfigParser


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

def initialise_dirs(params):
    for key in params.keys():
        if str(key).endswith("_dir"):
            try:
                if not os.path.isdir(params[key]):
                    os.makedirs(params[key])
                print(f"{key} = {params[key]}")
            except (Exception, PermissionError) as e:
                print(e)

def initialise_logs(dir, types):
    logs = {}
    for type, template in types.items():
        try:
            now = datetime.now()
            time_string = now.strftime("%Y-%m-%d_%H:%M_")
            file_name = time_string + type + ".log"
            log_file = os.path.join(dir, file_name)
            with open(log_file, 'x') as f:
                f.write(f"#{template}\n")
            print(f"{type} = {log_file}")
            logs[type] = log_file
        except (Exception, FileExistsError, PermissionError) as e:
            print(e)
    return logs
