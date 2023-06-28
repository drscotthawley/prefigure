#! /usr/bin/env python3
from prefigure import get_all_args, push_wandb_config, OFC

import pytorch_lightning as pl
import wandb
import time

def main():
    # Config setup. Order of preference will be:
    #   1. Default settings are in defaults.ini file or whatever you specify via --config-file
    #   2. if --wandb-config is given, pull config from wandb to override defaults
    #   3. Any new command-line arguments override whatever was set earlier
    args = get_all_args()

    print("Args = \n",args)
    use_wandb = True

    print(f"Pushing args to wandb run {args.name}")
    if use_wandb: 
        wandb_logger = pl.loggers.WandbLogger(project=args.name)
        push_wandb_config(wandb_logger, args, omit=['training_dir']) # push config to wandb for use later

    ofc = OFC(args, use_gui=True, steerables=['learning_rate','demo_every','demo_steps', 'num_demos','checkpoint_every', 'ema_decay'], 
              use_wandb=use_wandb) 
    print(f"ofc.gradio_url = {ofc.gradio_url}")

    while True:
        changed = ofc.update()
        time.sleep(2)

if __name__ == '__main__':
    main()
