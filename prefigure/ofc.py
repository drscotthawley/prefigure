# -*- coding: utf-8 -*-
__author__ = 'S.H. Hawley'

"""
On-the-Fly (User) Control (& Calibration)

This allows for changes to 
"""

from prefigure import get_all_args, arg_eval
import configparser
import gradio as gr
import gradio.blocks as gb
import copy
import itertools
import os
import warnings 




class OFC(object):
    "On-the-Fly Control: Saves args to a new file, updates 'args' when changes occur to file"
    def __init__(self, args, ofc_file='ofc.ini', gui=False):
        "NOTE: ofc_file should be given a unique name if multiple similar runs are occuring"
        self.ofc_file = args.name+'-'+ofc_file
        args.gui = gui or args.gui
        self.args = args
        self.section_name = 'STEERABLES'
        self.debug = False
        self.public_link = ''
        self.save(args)
        if args.gui: self.create_gradio_interface()

    def save(self, args):
        "saves all steerable params (args) as new INI file"
        config = configparser.ConfigParser()
        config.add_section(self.section_name)
        for key, val in vars(args).items():
            config[self.section_name][key] = str(val)
        if self.debug: print("OFC.save: Saving to ",self.ofc_file)
        with open(self.ofc_file, 'w') as f:
            config.write(f)

    def update(self):
        "find out which variables have changed"
        save_args_dict = vars(self.args)
        config = configparser.ConfigParser()
        config.read(self.ofc_file)
        new_args_dict = dict(config.items(self.section_name))

        changed = {}
        for key, val in new_args_dict.items():
            if not (',' in val):  # changes to list variables are not supported yet
                val = arg_eval(val)
                if (val != save_args_dict[key]) and (key != 'wandb_config'):
                    print(f"\n  OFC: {key} has been changed to {val}")
                    changed[key] = val
                    vars(self.args)[key] = val    # NOTE: THIS will overwrite values in args. 
        return changed   # changed dict can be used for wandb logging of changes

    def create_gui_element(self,key,value):
        "creates a single gui element based on variable type"
        if isinstance(value, bool):
            input_element = gr.components.Radio([True, False], value=value, label=key)
        elif isinstance(value, int):
            maximum = value * 2 if value > 0 else 1
            input_element = gr.components.Slider(minimum=0, maximum=maximum, value=value, label=key, step=1)
        elif isinstance(value, float):
            maximum = value * 2 if value > 0.0 else 1.0
            input_element = gr.components.Slider(minimum=0.0, maximum=maximum, value=value, label=key)
        elif isinstance(value, str):
            input_element = gr.components.Textbox(value=value, label=key)
        else:
            input_element = gr.components.Textbox(value=str(value), label=key) # for lists, etc.
        return input_element

    def create_gradio_interface(self, columns=3):
        "for all variables in args, create gui elements"
        inputs = []
        args_dict = vars(self.args)
        column_length = len(args_dict)//columns
        with gr.Blocks(title="OFC", theme=gr.themes.Base()) as demo:
            gr.HTML(f'<center><h1>prefigure: On-the-Fly Control (OFC)</h1></center>')        
            with gr.Row():
                for c in range(columns):
                    with gr.Column():
                        for key, value in itertools.islice(args_dict.items(), c*column_length, (c+1)*column_length):
                            if key=='gui': continue  # don't add 'gui' var to gui
                            if self.debug: print("key = ",key," value = ",value,", type = ",type(value))
                            input_element = self.create_gui_element(key,value)
                            inputs.append(input_element)
            submit_button = gr.Button(value="Submit", variant='primary',)
            submit_button.click(fn=self.on_gui_submit, inputs=inputs)
        print()

        auth = ( os.getenv('OFC_USERNAME', ''), os.getenv('OFC_PASSWORD', '') )
        share = True
        if auth[0] == '' or auth[1] == '':
            warnings.warn("OFC: No username/password provided. Authentication & Public sharing disabled.")
            auth, share = None, False
        _, _, public_link = demo.launch(prevent_thread_lock=True, auth=auth, share=share)
        print(f"Demo launched. Public link is {public_link} Moving on.")
        self.public_link = public_link   # do a wandb.log(wandb.HTML(f'<a href="{ofc.public_link}">OFC</a>')

    def on_gui_submit(self, *args_gui):
        "writes to the ofc file, then updates the args"
        args_copy = copy.copy(self.args)
        args_dict = vars(args_copy)
        filtered_args = [attr_name for attr_name in args_dict.keys() if not attr_name.startswith("__")]
        for value, attr_name in zip(args_gui, filtered_args):
            setattr(args_copy, attr_name, value)
        self.save(args_copy) 
        self.update() 

if __name__ == '__main__':
    # testing
    import time
    args = get_all_args(defaults_file='../examples/defaults.ini')
    args.name = 'test'
    print("args = \n",args)
    ofc = OFC(args, gui=True)
    while True:
        #print("\nargs = ",args)
        changed = ofc.update()
        time.sleep(2)
