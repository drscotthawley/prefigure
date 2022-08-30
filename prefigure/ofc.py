# -*- coding: utf-8 -*-
__author__ = 'S.H. Hawley'

"""
On-the-Fly (User) Control (& Calibration)

This allows for changes to 
"""

from prefigure import get_all_args, arg_eval
import configparser

class OFC(object):
    "On-the-Fly Control: Saves args to a new file, updates 'args' when changes occur to file"
    def __init__(self, args, ofc_file='ofc.ini'):
        "NOTE: ofc_file should be given a unique name if multiple similar runs are occuring"
        self.ofc_file = ofc_file
        self.args = args
        self.section_name = 'STEERABLES'
        self.save()

    def save(self):
        "saves steerable params (args) as new INI file"
        config = configparser.ConfigParser()
        config.add_section(self.section_name)
        for key, val in vars(self.args).items():
            config[self.section_name][key] = str(val)
        with open(self.ofc_file, 'w') as f:
            config.write(f)
                   
    def update(self):
        "find out which variables have changed"
        print("Checking ofc file....")
        save_args_dict = vars(self.args)
        config = configparser.ConfigParser()
        config.read(self.ofc_file)
        new_args_dict = dict(config.items(self.section_name))

        changed = {}
        for key, val in new_args_dict.items():
            val = arg_eval(val)
            if val != save_args_dict[key]:
                print(f"{key} has been changed to {val}")
                changed[key] = val
                vars(args)[key] = val    # NOTE: THIS will overwrite values in args. 
        return changed   # changed dict can be used for wandb logging of changes


if __name__ == '__main__':
    # testing
    import time
    args = get_all_args(defaults_file='../examples/defaults.ini')
    ofc = OFC(args)
    while True:
        print("\nargs = ",args)
        changed = ofc.update()
        time.sleep(2)


