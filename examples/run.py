#! /usr/bin/env python3
from prefigure.prefigure import get_all_args, push_wandb_config

import pytorch_lightning as pl
import wandb


# Usage: ./run.py --name test-prefigure

def main():
    # Config setup. Order of preference will be:
    #   1. Default settings are in defaults.ini file or whatever you specify via --config-file
    #   2. if --wandb-config is given, pull config from wandb to override defaults
    #   3. Any new command-line arguments override whatever was set earlier
    args = get_all_args()

    print("Args = \n",args)

    assert args.name is not None, "In this example, we make you you set 'name'"

    print(f"Pushing args to wandb run {args.name}")
    wandb_logger = pl.loggers.WandbLogger(project=args.name)
    push_wandb_config(wandb_logger, args, omit=['training_dir']) # push config to wandb for use later

if __name__ == '__main__':
    main()
