from configparser import ConfigParser
from datetime import datetime
import os
from typing import Any, Dict

def config(filename: str = './pupillae/conf/conf.ini', section: str = 'general'
    ) -> Dict[str, str]:
    """Use conf.ini section to build dictionary of parameters.

    Parameters
    ----------
    filename : str, optional (default: './pupillae/conf/conf.ini')
        Path
    section : str, optional (default: 'general')
        The section of `filename` to use for parameter dictionary.

    Raises
    ------
    Exception
        `filename` not found.
        `section` not found.

    Returns
    -------
    dict
        [`filename` `section`]{**kwargs}
    """

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

def initialise_dirs(params: Dict[str, str]) -> None:
    """Validate or create directories

    Parameters
    ----------
    params : dict
        Relevant Keys: "*_dir"

    """
    for key in params.keys():
        if str(key).endswith("_dir"):
            try:
                if not os.path.isdir(params[key]):
                    os.makedirs(params[key])
                print(f"{key} = {params[key]}")
            except (Exception, PermissionError) as e:
                print(e)

def initialise_logs(dir: str, types: Dict[str, str]) -> Dict[str, str]:
    """Create logs files

    Parameters
    ----------
    dir : str
        Path
    types: Dict[str, str]
        Format: {type: template}

    Return
    ------
    dict
        Format: {type: path}

    """
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
