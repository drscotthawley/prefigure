# -*- coding: utf-8 -*-
__author__ = 'S.H. Hawley'

"""
Routines for easily keeping track of & archiving run configurations.
Supports config (.ini) files, pulling previous configs from WandB, 
and overrides with command-line options.
"""

from pathlib import Path
from ast import literal_eval 
import argparse
import configparser
import wandb
import sys
import copy
import distutils
import json

DEFAULTS_FILE = 'defaults.ini'  # override via --config-file

def arg_eval(value):
    "this just packages some type checking for parsing args"
    try: 
        val = literal_eval(str(value))
    except (SyntaxError, ValueError, AssertionError):
        val = value
    return val

def setup_gin(gin_file):
    "called by read_defaults"
    import gin
    gin.parse_config_file(gin_file)
    return {}, '' # read_defaults is expected to return two things



def read_config(config_file):
    "read a config file, setup config dict"
    suffix = Path(config_file).suffix
    if '.gin' == suffix:  # "full gin compatibility" = ignore all other prefigure code ;-)
        print(f"prefigure: Switching to gin mode for config file {config_file}")
        config, config_text = setup_gin(config_file)
    elif '.json' == suffix:  # if the config file itself is a json file
        with open(config_file) as f:
            config = json.load(f)
        config_text = ''
    elif '.ini' == suffix: 
        configp = configparser.ConfigParser()
        configp.optionxform = str                 # don't change uppercase to lowercase
        configp.read(config_file)
        config, config_text = dict(configp.items('DEFAULTS')), ''
        with open(config_file) as f:
            config_text = f.readlines()
    else:
        print (f"ERROR: Unknown config file extension: {suffix}.")
        raise ValueError()
    
    return config, config_text


class BareParser(argparse.ArgumentParser):
    "lil thing just to get out the help message"
    def error(self, e, message):
        sys.stderr.write(f'ERROR: {message} {e}\n\n')
        self.print_help()
        sys.exit(2)

def read_defaults(defaults_file=DEFAULTS_FILE):
    "read the defaults (config) file, setup defaults dict"
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--config-file', required=False, default=defaults_file,
        help='name of local configuration (.ini) file')
    config_file = p.parse_known_args()[0].config_file
    try:
        defaults, defaults_text = read_config(config_file)
    except Exception as e:
        p = BareParser()
        p.add_argument('--config-file', required=False, default=defaults_file,
            help='name of local configuration (.ini) file')
        args=p.parse_args()
        p.error(e,f"Trouble reading {config_file}")
        sys.exit(1)
    return defaults, defaults_text


def parse_imports(args, debug=False):
    "If the user has supplied args which are themselves config files, parse them"
    if not hasattr(args, 'imports'): return args
    orig_args = copy.deepcopy(args)  # not good to edit args while looping over args
    for key, value in vars(orig_args).items():
        if debug: print(f"parse_imports: key = {key}, value = {value}")
        if (key in ['wandb_config','config_file']): continue  # don'e read in the basics a second time
        if key in args.imports and isinstance(value, str) and Path(value).suffix in ['.ini','.json','.gin']:
            # if the arg is a string and the string is a path to a config file
            # then parse it and add the args to the namespace
            if debug: print(f"parse_imports: Parsing config file {value}")
            new_value, value_text = read_config(value)
            # for any of those, delete the namespace attribute before adding it below
            #delattr(args, key)

            if debug: print(f"parse_imports: Replacing the following in the namespace: {key}:{new_value}",)
            #args = argparse.Namespace(**vars(args), **defaults)
            setattr(args, key, new_value)
    return args




def setup_args(defaults, defaults_text='',):
    """combine defaults from .ini file and add parseargs arguments, 
        with help pull from .ini"""
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)  
    # --help and the next few args are always there regardless of what user supplies
    p.add_argument('--config-file', required=False, default=DEFAULTS_FILE, #added so it appears on -h list
        help='name of local configuration (.ini) file')
    #removing name as required arg. no more hand-holding:  p.add_argument('--name', required=False, default=None, help='name of the run')
    p.add_argument('--wandb-config', required=False,  help='wandb url to pull config from')


    # add other CLI args using defaults .ini file, i.e. it determines what args are 'allowed'
    for key, value in defaults.items():
        if (key in ['wandb_config','config_file']): break
        help = ""
        for i in range(len(defaults_text)):  # get the help string from defaults_text
            if key in defaults_text[i]:
                help = defaults_text[i-1].replace('# ','')
        argname = '--'+key.replace('_','-')
        #if '--name' == argname: continue
        val = Path(value) if ((type(value) == str) and ('_dir' in value)) else arg_eval(value)
        val_type = type(val)
        #print(f"argname: {argname}, val: {val}, val_type: {val_type}")
        if val is None: # None is weird in Python
            p.add_argument(argname, type=str, nargs='?', const=None, default=None, help=help)
        elif (val_type != type(True)):   # gotta handle boolean values specially when dealing with argparse
            p.add_argument(argname, default=val, type=val_type, help=help)
        else: # normal string/int/etc
            #val_type = bool(distutils.util.strtobool(val))
            p.add_argument(argname, type=val_type, nargs='?', const=True, default=False, help=help)

    args = p.parse_args() 
        
    return args
    

def pull_wandb_config(wandb_config, defaults):
    """overwrites parts of defaults using wandb config info 
       wandb_config is the url of one of your runs"""
    api = wandb.Api()  # might get prompted for api key login the first time
    splits = wandb_config.split('/')
    entity, project, run_id = splits[3], splits[4], splits[-1].split('?')[0]
    run = api.run(f"{entity}/{project}/{run_id}")
    for key, value in run.config.items():
        if 'OMITTED' != value: defaults[key] = arg_eval(value)
    return defaults



def push_wandb_config(wandb_logger, args, omit=[]): 
    """
    save config to wandb (for possible retrieval later)
    Omit: list of args you don't want pushed to wandb; will push an empty string for these
    """
    if hasattr(wandb_logger.experiment.config, 'update'): #On multi-GPU runs, only process rank 0 has this attribute!
        copy_args = copy.deepcopy(args)
        for var_str in omit:  # don't push certain reserved settings to wandb
            if hasattr(copy_args, var_str):
                setattr(copy_args, var_str, 'OMITTED')
        wandb_logger.experiment.config.update(copy_args)


def get_all_args(defaults_file=DEFAULTS_FILE):
    " Config setup."
    args = {}
    #   1. Default settings are in defaults ini (or some other config) file
    defaults, defaults_text = read_defaults(defaults_file=defaults_file)
    args = setup_args(defaults, defaults_text=defaults_text)  

    #   2. if --wandb-config is given, pull config from wandb to override defaults
    if args.wandb_config is not None:
        defaults = pull_wandb_config(args.wandb_config, defaults) # 2.

    #   3. Any new command-line arguments override whatever was set earlier
    args = setup_args(defaults, defaults_text=defaults_text) # 3. this time cmd-line overrides what's there


    #  4. If any of the args are themselves config files, parse them
    args = parse_imports(args)

    return args


if __name__ == '__main__':
    # quick test
    args = get_all_args(defaults_file='defaults.ini')#../examples/defaults.ini')
    print("args = ",args)
