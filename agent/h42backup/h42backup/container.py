import os
#import json
import docker

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
                    ignore = True
                    if 'Name' in vol:
                        ignore = vol['Name'] in vol_ignore
                    if vol['Type'] == 'bind' and include_bind:
                        mounts.append({'type': 'bind', 'dest': vol['Destination'], 'ignore': ignore})
                    if vol['Type'] == 'volume':
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
            
            if error:
                ctb['error'] = error

    return bck


def backup_run(bck, config):
    vols = bck.getDockerVolumes()
    return h42backup_agent_run(f'/h42backup/h42-backup-agent backup exec --name={bck.name}', config, vols)

def h42backup_agent_run(cmd, config, volumes=None):
    if volumes is None:
        volumes = {}
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    vols = {'h42backup_agent_config': {'bind': CONF_PATH, 'mode': 'ro'}, 'h42backup_agent_root': {'bind': '/root', 'mode': 'ro'}}
    vols.update(volumes)

    netconf = client.api.create_networking_config({
        config.worker['network']: client.api.create_endpoint_config(
            ipv6_address=config.worker['ipv6']
        )
    })

    ctr = client.containers.run(
        image='gilles67/h42-backup-agent',
        command=cmd,
        auto_remove=True,
        networking_config=netconf,
        volumes=vols
    )


    
    return ctr
