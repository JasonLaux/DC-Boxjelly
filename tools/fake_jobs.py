#!/usr/bin/python

"""
Generate fake jobs
"""

import os
import shutil
from os.path import join

JOB_COUNT = 3000
JOB_PREFIX = 'GEN'

_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
JOBS = os.path.abspath(join(_DIR_PATH, '..', 'data', 'jobs'))

TEMPLATE_JOB = join(JOBS, 'CAL00001')

def main():
    max_digit_len = len(str(JOB_COUNT))
    for i in range(1, JOB_COUNT + 1):
        target = join(JOBS, JOB_PREFIX + str(i).zfill(max_digit_len))
        shutil.copytree(TEMPLATE_JOB, target)

if __name__ == '__main__':
    main()
