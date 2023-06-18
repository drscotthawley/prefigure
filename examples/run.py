#! /usr/bin/env python3
from prefigure import get_all_args, push_wandb_config, OFC

import pytorch_lightning as pl
import wandb
import gin
import time

# Usage: ./run.py --name test-prefigure
#  ^ the "test-prefigure" is the name of the wandb run

@gin.configurable 
def test_print(msg='Standard run'):
    print(f"test_print: msg = {msg}")

@gin.configurable 
def get_name(name=None):
    return name

def main():
    # Config setup. Order of preference will be:
    #   1. Default settings are in defaults.ini file or whatever you specify via --config-file
    #   2. if --wandb-config is given, pull config from wandb to override defaults
    #   3. Any new command-line arguments override whatever was set earlier
    args = get_all_args()


    test_print()

    print("Args = \n",args)
    if args.name is None: args.name = get_name()

    assert args.name is not None, "In this example, we make you you set 'name'"

    print(f"Pushing args to wandb run {args.name}")
    wandb_logger = pl.loggers.WandbLogger(project=args.name)
    push_wandb_config(wandb_logger, args, omit=['training_dir']) # push config to wandb for use later

    ofc = OFC(args, gui=True) 
    print(f"OFC: Public link is {ofc.public_link}")
    wandb.log({"gradio_link": wandb.Html(f'OFC Gradio URL is <a href="{ofc.public_link}" target="_blank">{ofc.public_link}</a>')})

    while True:
        changed = ofc.update()
        time.sleep(2)

if __name__ == '__main__':
    main()
