#!/usr/bin/env python2

from distutils.core import setup
from glob import glob

setup(
    name = 'BubbMan2',
    version = '1.1.2',
    description = 'A solo entry by pymike for PyWeek #8',
    long_description = open('Readme.txt').read(),
    author = 'pymike',
    maintainer = 'Tempel',
    maintainer_email = 'randy.heydon@clockworklab.net',
    url = 'http://www.pygame.org/project-BubbMan+2-1114-.html',
    packages = ['lib','retrogamelib'],
    package_data = {'retrogamelib': ['*.png']},
    data_files = [('data', glob('data/*'))],
    scripts = ['run_game.py'],
    license = 'LGPL',
)
