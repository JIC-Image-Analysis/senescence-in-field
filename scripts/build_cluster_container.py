import argparse
import subprocess

def write_run_control_file(project_root, container_name):
    run_control = { 'container' : container_name,
                    'version' : '0.1.0' }

    run_control_file = os.path.join(project_root, 'run_control.json')

    with open(run_control_file, 'w') as f:
        json.dump(run_control, f)


def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('container_name', help='Name to use for container')
    
    args = parser.parse_args()

    container_name = args.container_name

    container_path = '/usr/users/cbu/hartleym/mnt/cluster_home/sketchings/senescence-in-field/containers'

    remove_command = ['docker', 'rmi', 'packed-for-cluster']
    subprocess.call(remove_command)

    build_command = ['docker', 
                     'build', 
                     '-t', 
                     'packed-for-cluster', 
                     'docker/packed-for-cluster']
    subprocess.call(build_command)

    singularity_build_command = ['docker',
                                 'run',
                                 '-v',
                                 '/var/run/docker.sock:/var/run/docker.sock',
                                 '-v',
                                 container_path + ':' + '/output',
                                 '--privileged',
                                 '-t',
                                 '--rm',
                                 'mcdocker2singularity',
                                 'packed-for-cluster',
                                 container_name]
    subprocess.call(singularity_build_command)


if __name__ == "__main__":
    main()
