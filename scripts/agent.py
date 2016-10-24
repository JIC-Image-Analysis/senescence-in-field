#!/usr/bin/env python
"""Portable infrastructure agent."""

import os
import sys
import subprocess

def build_docker_image():

    # Remove old image

    # Build new image
    # docker build -t image_name path

    pass

def build_singularity_image():
    pass

def output_run_script():
    pass

def magic():

    data_root = '/data'
    data_file_template = 'DJI_0{}.JPG'

    start = int(sys.argv[1])
    end = start + 5

    for file_id in range(start, end):
        data_file = data_file_template.format(file_id)
        fq_data_file = os.path.join(data_root, data_file)

        run_command = ['python', '/scripts/analysis.py', fq_data_file, '/output']

        print(' '.join(run_command))
        subprocess.call(run_command)


def main():
    output_run_script()

if __name__ == '__main__':
    main()