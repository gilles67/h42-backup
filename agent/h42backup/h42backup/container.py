import docker, json

VALID_PROFILE = ['volume', 'mariadb']

def backup_list():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    bck = {}
    for ct in client.containers.list(all=True):
        is_backup = False
        error = []
        if 'one.h42.backup.enable' in ct.labels:
            if ct.labels['one.h42.backup.enable'] == 'true':
                is_backup = True

        if is_backup:
            ctb = bck[ct.name] = {}
            ctb['profile'] = "volume"
            if 'one.h42.backup.profile' in ct.labels:
                if ct.labels['one.h42.backup.profile'] in VALID_PROFILE:
                    profile = ctb['profile'] = ct.labels['one.h42.backup.profile']
                else:
                    profile = ctb['profile'] = 'invalid'
                    error.append("H42backup: invalid profile detected! one.h42.backup.profile=" + ct.labels['one.h42.backup.profile'] + ".")

            if profile == 'volume':
                vol_ignore = []
                if 'one.h42.backup.volume.ignore' in ct.labels:
                    vol_ignore = ctb['volume_ignore'] = ct.labels['one.h42.backup.volume.ignore'].split(',')
                include_bind = False
                if 'one.h42.backup.volume.include_bind' in ct.labels:
                    if ct.labels['one.h42.backup.volume.include_bind'] == 'true': 
                        include_bind = ctb['volume_include_bind'] = True

                mounts = ctb['mounts'] = []
                for vol in ct.attrs['Mounts']:
                    if vol['Type'] == 'bind' and include_bind:
                        mounts.append({'type': 'bind', 'dest': vol['Destination']})
                    if vol['Type'] == 'volume':
                        ignore = vol['Name'] in vol_ignore
                        mounts.append({'type': 'volume', 'dest': vol['Destination'], 'name': vol['Name'], 'ignore': ignore })
            
            if profile == 'mariadb':
                backup_volume = None
                if 'one.h42.backup.mariadb.volume' in ct.labels:
                    backup_volume = ctb['mariadb_backup_volume'] = ct.labels['one.h42.backup.mariadb.volume']
                else:
                    error.append('Mariadb: backup volume not define, "one.h42.backup.mariadb.volume" docker label not exists or is empty.')

                if backup_volume:
                    mounts = ctb['mounts'] = []
                    for vol in ct.attrs['Mounts']:
                        if vol['Type'] == 'volume' and vol['Name'] == backup_volume:
                            mounts.append({'type': 'volume', 'dest': vol['Destination'], 'name': vol['Name'],'ignore': False  })

                    if len(mounts) == 0:
                        error.append('Mariadb: backup volume ' +  backup_volume +  ' not found in docker mount list.')
            
            if len(error):
                ctb['error'] = error

    return bck


def backup_run(bck):
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    vols = bck.getDockerVolumes()
    ctr = client.containers.run(
        image='h42-backup/agent',
        command='/h42backup/h42-backup-agent backup exec --name={}'.format(bck.name),
        auto_remove=True,
        network_mode='bridge',
        volumes=vols
    )
    return ctr

