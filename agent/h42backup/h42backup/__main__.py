#!/usr/bin/python3
import sys
import argparse
from container import backup_list, backup_run
from backup import backupConfig, borgConfig

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='')

parser_backup = subparsers.add_parser('backup', help='backup command')
parser_backup.add_argument('backup', choices=['list', 'run', 'full', 'exec'])
parser_backup.add_argument('--name', nargs='?')

parser_borg = subparsers.add_parser('borg', help='borg command')
parser_borg.add_argument('borg', choices=['init-config', 'public-key', 'init-repo'])

args = parser.parse_args()
if 'backup' in args:
    if args.backup == 'list':
        bck_list = backup_list()
        for name in bck_list:
            bck = backupConfig(name)
            bck.load_container(bck_list[name])
            bck.save()
            print(bck.list())
    elif args.backup == 'full':
        pass
    elif args.backup == 'run' and args.name:
        bck = backupConfig(args.name)
        if not bck.exists:
            sys.exit("Backup configuration file not exists !")
        if bck.is_lock:
            sys.exit(f"Backup {args.name} is locked !")
        print(backup_run(bck))
    elif args.backup == 'exec' and args.name:
        brc = borgConfig()
        if not brc.exists:
            sys.exit("Borg configuration file not exists !")
        bck = backupConfig(args.name)
        if not bck.exists:
            sys.exit("Backup configuration file not exists !")
        brc.create(bck)
    else:
        print("🚧 Nothing todo !")
        print(args)

if 'borg' in args:
    brc = borgConfig()
    if args.borg == 'init-config':
        print("Configuration init !")
    if args.borg == 'public-key':
        print(brc.publicKey)
    if args.borg == 'init-repo':
        brc.initRepo()
