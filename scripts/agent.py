#!/usr/bin/env python
"""Portable infrastructure agent."""

import os
import sys
import subprocess

class Project(object):
    pass

def build_docker_image():

    # Remove old image

    # Build new image
    # docker build -t image_name path

    pass

def build_singularity_image():
    pass

def output_run_script():
    pass

def run_analysis_on_files(file_list):
    # NOTE - file_list is *container* relative

    data_root = '/data'

    for filename in file_list:
        fq_data_file = os.path.join(data_root, filename)

        run_command = ['python', '/scripts/analysis.py', fq_data_file, '/output']

        print(' '.join(run_command))
        #subprocess.call(run_command)


def main():
    #output_run_script()
    
    file_list = sys.argv[1:]

    run_analysis_on_files(file_list)

if __name__ == '__main__':
    main()
