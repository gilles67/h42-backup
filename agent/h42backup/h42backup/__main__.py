#!/usr/bin/python3
import argparse,json
from container import backup_list, backup_run
from backup import backupConf, borgConf

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='')

parser_backup = subparsers.add_parser('backup', help='backup command')
parser_backup.add_argument('backup', choices=['list', 'run', 'full', 'profile'])
parser_backup.add_argument('--profile', nargs='?')

parser_borg = subparsers.add_parser('borg', help='borg command')
parser_borg.add_argument('borg', choices=['init-config'])

args = parser.parse_args()
if 'backup' in args:
    if args.backup == 'list':
        list = backup_list()
        for name in list.keys():
            bck = backupConf(name)
            bck.load_container(list[name])
            bck.save()
            print(bck.list())
    elif args.backup == 'full':
        pass
    elif args.backup == 'run' and args.profile:
        bck = backupConf(args.profile)
        if not bck.exists():
            sys.exit("Backup configuration file not exists !")
        backup_run(bck)
    elif args.backup == 'profile' and args.profile:
        brc = borgConf()
        if not brc.exists():
            sys.exit("Borg configuration file not exists !")
        bck = backupConf(args.profile)
        if not bck.exists():
            sys.exit("Backup configuration file not exists !")
        brc.create(bck)
        
    else:
        print("🚧 Nothing todo !")
        print(args)

if 'borg' in args:
    if args.borg == 'init-config':
        brc = borgConf() 
        print(json.dumps(brc.config, indent=4))
