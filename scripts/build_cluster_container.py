import subprocess

def main():

    container_name = 'version2.img'
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
