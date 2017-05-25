import os
import argparse
import subprocess

CONTAINERS_REL_PATH = "containers"

def write_run_control_file(project_root, container_name):
    run_control = { 'container' : container_name,
                    'version' : '0.1.0' }

    run_control_file = os.path.join(project_root, 'run_control.json')

    with open(run_control_file, 'w') as f:
        json.dump(run_control, f)

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('project_root', help='Project root')
    parser.add_argument('container_name', help='Name to use for container')

    args = parser.parse_args()

    if not os.path.isdir(args.project_root):
        args.error("Not a directory: {}".format(args.project_root))

    containers_path = os.path.join(args.project_root, CONTAINERS_REL_PATH)
    if not os.path.isdir(containers_path):
        os.mkdir(containers_path)


    remove_command = ['docker', 'rmi', 'packed-for-cluster']
    subprocess.call(remove_command)

    build_command = ['docker',
                     'build',
                     '-t',
                     'packed-for-cluster',
                     'docker/packed-for-cluster']
    return_code = subprocess.call(build_command)
    if return_code != 0:
        raise(RuntimeError("You need to build your image analysis docker image"))

    singularity_build_command = ['docker',
                                 'run',
                                 '-v',
                                 '/var/run/docker.sock:/var/run/docker.sock',
                                 '-v',
                                 containers_path + ':' + '/output',
                                 '--privileged',
                                 '-t',
                                 '--rm',
                                 'mcdocker2singularity',
                                 'packed-for-cluster',
                                 args.container_name]
    subprocess.call(singularity_build_command)


if __name__ == "__main__":
    main()
