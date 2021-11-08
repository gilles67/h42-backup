import docker

def backup_list(): 
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    for ct in client.container:
        print(ct.name)
