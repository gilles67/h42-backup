import os
#import json
import docker
import docker.types

VALID_PROFILE = ['volume', 'mariadb']
CONF_PATH = os.getenv("H42BACKUP_CONFPATH", "/h42backup/config")

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
                    print(vol)
                    ignore = True
                    if 'Name' in vol:
                        ignore = vol['Name'] in vol_ignore
                    if vol['Type'] == 'bind' and include_bind:
                        mounts.append({'type': 'bind', 'dst': vol['Destination'], 'src': vol['Source'], 'ignore': False, 'mode':'rw'})
                    if vol['Type'] == 'volume':
                        mounts.append({'type': 'volume', 'dst': vol['Destination'], 'name': vol['Name'], 'ignore': ignore, 'mode':'rw'})

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
                            mounts.append({'type': 'volume', 'dst': vol['Destination'], 'name': vol['Name'],'ignore': False , 'mode':'rw'})
                    if len(mounts) == 0:
                        error.append('Mariadb: backup volume ' +  backup_volume +  ' not found in docker mount list.')
            if error:
                ctb['error'] = error

    return bck


def backup_run(bck):
    vols = bck.getDockerVolumes()
    ctr = h42backup_agent_run(f'/h42backup/h42-backup-agent backup exec --name={bck.name}', vols)
    bck.lock(ctr.name)
    return ctr

def h42backup_agent_run(cmd, volumes=None):
    mnts = []
    if volumes is None:
        volumes = {}
    for vol in volumes:
        if vol['type'] == "volume":
            mnts.append(docker.types.Mount(vol['dst'], vol['name'], type=vol['type'], read_only=vol['mode']=="ro"))
        if vol['type'] == "bind":
            mnts.append(docker.types.Mount(vol['dst'], vol['src'], type=vol['type'], read_only=vol['mode']=="ro"))

    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    ctr = client.containers.run(
        image='gilles67/h42-backup-agent',
        command=cmd,
        mounts=mnts,
        remove=True,
        detach=True
    )
    return ctr
