#!/usr/bin/python3
import argparse
from container import backup_list
from backup import backupConf 

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='')

parser_backup = subparsers.add_parser('backup', help='backup command')
parser_backup.add_argument('backup', choices=['list', 'full', 'profile'])
parser_backup.add_argument('--profile', nargs='?')


args = parser.parse_args()
if 'backup' in args:
    if args.backup == 'list':
        list = backup_list()
        for name in keys(list):
            bck = backupConf(name)
            bck.load_container(list[name])
            bck.write()
            print(bck.list())
    elif args.backup == 'full':
        pass
    elif args.backup == 'profile':
        pass
    