#! /usr/bin/env python3
from configger.configger import get_all_args, wandb_log_config

import pytorch_lightning as pl
import wandb

# Usage: ./run.py --name test-configger

def main():
    # Config setup. Order of preference will be:
    #   1. Default settings are in defaults.ini file or whatever you specify via --config-file
    #   2. if --wandb-config is given, pull config from wandb to override defaults
    #   3. Any new command-line arguments override whatever was set earlier
    args = get_all_args()

    wandb_logger = pl.loggers.WandbLogger(project=args.name)

    wandb_log_config(wandb_logger, args) # push config to wandb for use later

    wandb.finish()

if __name__ == '__main__':
    main()
