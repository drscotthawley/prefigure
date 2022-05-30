# prefigure

> Run-configuration management utils: combines configparser, argparse, and wandb.API

Capabilities for archiving run settings and pulling configurations from previous runs.  With just 3 lines of code 😎 : the import, the arg setup, & the wandb push.  

Combines argparse, configparser, and wandb.API

## Install:

```bash
pip install prefigure
```


## Instructions:

All your usual command line args (with the exception of `--name` and `--training-dir`) are now to be specified in a `defaults.ini` file -- see `examples/` for an example.  
A different `.ini` file can be specified via  `--config-file`.

The option `--wandb-config <url>` pulls previous runs' configs off wandb, where `<url> is the url of any one of your runs to override those defaults:
e.g. `--wandb-config='https://wandb.ai/drscotthawley/delete-me/runs/1m2gh3o1?workspace=user-drscotthawley'`
(i.e., whatever URL you grab from your browser window when looking at an individual run.)  

**NOTE: the `--wandb-config` thing can only pull from WandB runs that used prefigure, i.e. that have logged a "wandb config push".**

Any command line args you specify will override any settings from WandB and/or the `.ini` file.

The order of precedence is "command line args override WandB, which overrides the .ini file".


### 1st line to add
In your run/training code, add this near the top:

```Python
from prefigure.prefigure import get_all_args, wandb_log_config
```

### 2nd line to add
Near the top of your `main()`, add this:

```Python
args = get_all_args()
```

Further down in your code, comment-out (or delete) *all* your command-line arguments. If you want different command-line arguments, then add or change them in defaults.ini.  The 'help' string for these is provided via  comment in the line preceding your variable. (see defaults.ini for examples)


### 3rd line to add
and then right after you define the wandb logger, run

```Python
wandb_log_config(wandb_logger, args)
```


## Sample usage (code_):

```Python
from prefigure import get_all_args, wandb_log_config


def main():

    # Config setup. Order of preference will be:
    #   1. Default settings are in defaults.ini file or whatever you specify via --config-file
    #   2. if --wandb-config is given, pull config from wandb to override defaults
    #   3. Any new command-line arguments override whatever was set earlier
    args = get_all_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.manual_seed(args.seed)

    train_set = SampleDataset([args.training_dir], args)
    train_dl = data.DataLoader(train_set, args.batch_size, shuffle=True,
                               num_workers=args.num_workers, persistent_workers=True, pin_memory=True)
    wandb_logger = pl.loggers.WandbLogger(project=args.name)
    wandb_log_config(wandb_logger, args) # push config to wandb for archiving

    demo_dl = data.DataLoader(train_set, args.num_demos, shuffle=True)

```
