#!/usr/bin/env python

import sys
import argparse
import subprocess
import shlex

# setup cmsDriver era commands
eraCommands = dict()
for year in [2016,2017,2018]:
    eraCommands[year] = dict()
# see https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD#Running_on_various_datasets_from
# don't put spaces in arguments or the 'split' later will fail
eraCommands[2016]['mc']  =""" --era Run2_2016,run2_miniAOD_80XLegacy """ # RunIISummer16MiniAODv2 MC
eraCommands[2016]['data']=""" --era Run2_2016,run2_nanoAOD_94X2016 """   # 94X data (17Jul2018) [and RunIISummer16MiniAODv3 MC]
eraCommands[2017]['mc']  =""" --era Run2_2017,run2_nanoAOD_94XMiniAODv2 """ # for 2017 94X MiniAODv2 samples (including 31Mar2018 data)
eraCommands[2017]['data']=eraCommands[2017]['mc']
eraCommands[2018]['mc']  =""" --era Run2_2018,run2_nanoAOD_102Xv1 """ # for all 2018 10XY samples
eraCommands[2018]['data']=eraCommands[2018]['mc']

# common data/MC cmsDriver parts
commonPart = dict()
prefix="""cmsDriver.py lqCustomNano_{0}_{1}_{2} -s NANO"""
commonPart['data']=prefix
commonPart['mc']=prefix
commonPart['data']+=""" --data --eventcontent NANOAOD --datatier NANOAOD """
commonPart['mc']+=""" --mc --eventcontent NANOAODSIM --datatier NANOAODSIM """
commonPartBoth=""" --conditions {2} -n 100 --no_exec --customise_commands="process.add_(cms.Service('InitRootHandlers',EnableIMT=cms.untracked.bool(False)))" """
commonPart['data']+=commonPartBoth
commonPart['mc']+=commonPartBoth

cmsDriverCommands = dict()
for year in [2016,2017,2018]:
    cmsDriverCommands[year] = dict()
    for category in ['mc','data']:
        cmsDriverCommands[year][category]=commonPart[category]+eraCommands[year][category]


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
    command = cmsDriverCommands[year][category].format(category,year,globalTag)
    splitCommand = shlex.split(command)
    print 'run for {0} {1}'.format(year,category),':',command
    subprocess.check_call(splitCommand)
else:
    print 'could not find cmsDriver command for {0} {1}'.format(year,category)+'; Quitting.'
    exit(-1)


