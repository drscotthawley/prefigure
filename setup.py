from setuptools import setup

setup(
    name='configger',
    version='0.1.0',
    description='Run configuration management utils: combines configparser, argparse, and wandb.API',
    url='https://github.com/drscotthawley/configger',
    author='Scott H. Hawley',
    author_email='scott.hawley@belmont.edu',
    license='BSD 2-clause',
    packages=['pyexample'],
    install_requires=['argparse',
                      'configparser',
                      'wandb'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
