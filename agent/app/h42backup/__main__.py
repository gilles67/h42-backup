#!/usr/bin/python3
import argparse
from container import * 

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='')

parser_backup = subparsers.add_parser('backup', help='backup command')
parser_backup.add_argument('backup', choices=['list', 'full'])

args = parser.parse_args()
if 'backup' in args:
    if args.backup == 'list':
        backup_list()
