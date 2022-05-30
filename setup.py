from setuptools import setup

setup(
    name='prefigure',
    version='0.0.1',
    description='Run configuration management utils: combines configparser, argparse, and wandb.API',
    url='https://github.com/drscotthawley/prefigure',
    author='Scott H. Hawley',
    author_email='scott.hawley@belmont.edu',
    license='MIT',
    packages=['prefigure'],
    install_requires=['argparse',
                      'configparser',
                      'wandb',
                      'pytorch_lightning'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
