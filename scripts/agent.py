#!/usr/bin/env python
"""Portable infrastructure agent."""

import os
import sys
import json
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

def run_analysis_on_data(data_to_process):
    # NOTE - file_list is *container* relative

    data_root = '/data'

    for datum in data_to_process:

        filename = datum['relative_raw_path']
        fq_data_file = os.path.join(data_root, filename)

        output_basename = datum['identifier']

        run_command = [ 'python', 
                        '/scripts/analysis.py', 
                        fq_data_file, 
                        '/output',
                        output_basename]

        print(' '.join(run_command))
        subprocess.call(run_command)

def read_manifest_and_run_files():

    manifest_path = '/project/manifest.json'

    with open(manifest_path) as f:
        manifest_data = json.load(f)

    manifest_data_by_id = { datum['identifier'] : datum 
                                for datum in manifest_data }

    data_ids_to_process = sys.argv[1:]

    data_to_process = [manifest_data_by_id[id] for id in data_ids_to_process]

    run_analysis_on_data(data_to_process)

def main():
    read_manifest_and_run_files()

if __name__ == '__main__':
    main()
