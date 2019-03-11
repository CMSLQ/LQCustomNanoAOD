#!/usr/bin/env python

import sys
import argparse
import subprocess

cmsDriverCommands = dict()
for year in [2016,2017,2018]:
    cmsDriverCommands[year] = dict()

# example: https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer16NanoAODv4-00034
# don't put spaces in arguments or the 'split' later will fail
cmsDriverCommands[2016]['mc']="""
cmsDriver.py lqCustomNano_mc_102Xv2 -s NANO --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions {0} -n 100 --era Run2_2016,run2_miniAOD_80XLegacy --no_exec --customise_commands="process.add_(cms.Service('InitRootHandlers',EnableIMT=cms.untracked.bool(False)))"
"""
cmsDriverCommands[2016]['data']="""
cmsDriver.py lqCustomNano_data_102X -s NANO --data --eventcontent NANOAOD --datatier NANOAOD --conditions {0} -n 100 --era Run2_2016,run2_nanoAOD_94X2016 --no_exec --customise_commands="process.add_(cms.Service('InitRootHandlers',EnableIMT=cms.untracked.bool(False)))"
"""

parser = argparse.ArgumentParser()
parser.add_argument("--datatype", help="MC or data", required=True,choices=['mc','data'])
parser.add_argument("--gt", help="global tag to use", required=True)
parser.add_argument("--year", help="year to use", required=True,type=int)
args = parser.parse_args()
print 'datatype:',args.datatype
print 'gt:',args.gt
print 'year:',args.year

globalTag = args.gt
year = args.year
category = args.datatype


if year in cmsDriverCommands.keys() and category in cmsDriverCommands[year].keys():
    command = cmsDriverCommands[year][category].format(globalTag)
    print 'run for {0} {1}'.format(year,category),':',command
    subprocess.check_call(command.split())
else:
    print 'could not find cmsDriver command for {0} {1}'.format(year,category)+'; Quitting.'
    exit(-1)


