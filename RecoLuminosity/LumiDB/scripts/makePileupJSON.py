#!/usr/bin/env python
from __future__ import print_function
import argparse
import RecoLuminosity.LumiDB.LumiConstants as LumiConstants
import re
from math import sqrt
import six

##############################
## ######################## ##
## ## ################## ## ##
## ## ## Main Program ## ## ##
## ## ################## ## ##
## ######################## ##
##############################

# modified from the estimatePileup.py script in RecoLuminosity/LumiDB
# originally 5 Jan, 2012  Mike Hildreth
# The Run 2 version only accepts a csv file from brilcalc as input.

if __name__ == '__main__':
    parameters = LumiConstants.ParametersObject()

    parser = argparse.ArgumentParser(description="Script to estimate average and RMS pileup using the per-bunch luminosity information provided by brilcalc. The output is a JSON file containing a dictionary by runs with one entry per lumi section.")
    parser.add_argument('inputFile', help='CSV input file as produced from brilcalc')
    parser.add_argument('outputFile', help='Name of JSON output file')
    parser.add_argument('-b', '--selBX', help='Comma-separated list of BXs to use (will use all by default)')
    args = parser.parse_args()

    output = args.outputFile

    sel_bx = set()
    if args.selBX:
        for ibx in args.selBX.split(","):
            try:
                bx=int(ibx)
                sel_bx.add(bx)
            except:
                print(ibx,"is not an int")
        print("Processing",args.inputFile,"with selected BXs:", sorted(sel_bx))
    else:
        print("Processing",args.inputFile,"with all BX")

    # The "CSV" file actually is a little complicated, since we also want to split on the colons separating
    # run/fill as well as the spaces separating the per-BX information.
    sepRE = re.compile(r'[\]\[\s,;:]+')
    csv_input = open(args.inputFile, 'r')
    last_run = -1

    last_valid_lumi = []

    output_line = '{'
    for line in csv_input:
        if line[0] == '#':
            continue # skip comment lines

        pieces = sepRE.split(line.strip())

        if len(pieces) < 15:
            # The most likely cause of this is that we're using a csv file without the bunch data, so might as well
            # just give up now.
            raise RuntimeError("Not enough fields in input line; maybe you forgot to include --xing in your brilcalc command?\n"+line)
        try:
            run = int(pieces[0])
            lumi_section = int(pieces[2])
            #tot_del_lumi = float(pieces[11])
            #tot_rec_lumi = float(pieces[12])
            luminometer = pieces[14]
            xing_lumi_array = [( int(bxid), float(bunch_del_lumi), float(bunch_rec_lumi) ) \
                               for bxid, bunch_del_lumi, bunch_rec_lumi in zip( pieces[15::3],
                                                                                pieces[16::3],
                                                                                pieces[17::3]) ]
        except:
            print("Failed to parse line: check if the input format has changed")
            print(pieces[0],pieces[1],pieces[2],pieces[3],pieces[4],pieces[5],pieces[6],pieces[7],pieces[8],pieces[9])
            continue

        if run != last_run:
            if last_run>0:
                # add one empty lumi section at the end of each run, to mesh with JSON files
                output_line += "[%d,0.0,0.0,0.0]," % (last_valid_lumi[0]+1)
                output_line = output_line[:-1] + '], '
            last_run = run
            output_line += ('"%d":' % run )
            output_line += ' ['

            if lumi_section == 2:  # there is a missing LS=1 for this run
                output_line += '[1,0.0,0.0,0.0],'

        # Now do the actual parsing.
        if luminometer == "HFOC":
            threshold = 8.
        else:
            threshold = 1.2

        total_lumi = 0 
        total_int = 0
        total_int2 = 0
        total_weight = 0
        total_weight2 = 0
        filled_xings = 0

        # first loop to get sum for (weighted) mean
        for bxid, bunch_del_lumi, bunch_rec_lumi in xing_lumi_array:
            if sel_bx and bxid not in sel_bx:
                continue
            if bunch_del_lumi > threshold:
                total_lumi += bunch_rec_lumi
                # this will eventually be_pileup*bunch_rec_lumi but it's quicker to apply the factor once outside the loop
                total_int += bunch_del_lumi*bunch_rec_lumi
                filled_xings += 1

        # convert sum to pileup and get the mean
        total_int *= parameters.orbitLength / parameters.lumiSectionLength
        if total_lumi > 0:
            mean_int = total_int/total_lumi
        else:
            mean_int = 0

        # second loop to get (weighted) RMS
        for bxid, bunch_del_lumi, bunch_rec_lumi in xing_lumi_array:
            if sel_bx and bxid not in sel_bx:
                continue
            if bunch_del_lumi > threshold:
                mean_pileup = bunch_del_lumi * parameters.orbitLength / parameters.lumiSectionLength
                if mean_pileup > 100:
                    print("mean number of pileup events > 100 for run %d, lum %d : m %f l %f" % \
                          (runNumber, lumi_section, mean_pileup, bunch_del_lumi))
                    #print "mean number of pileup events for lum %d: m %f idx %d l %f" % (lumi_section, mean_pileup, bxid, bunch_rec_lumi)

                total_int2 += bunch_rec_lumi*(mean_pileup-mean_int)*(mean_pileup-mean_int)
                total_weight += bunch_rec_lumi
                total_weight2 += bunch_rec_lumi*bunch_rec_lumi

        # compute final RMS and write it out
        #print " LS, Total lumi, filled xings %d, %f, %d" %(lumi_section,total_lumi,filled_xings)
        bunch_rms_lumi = 0
        denom = total_weight*total_weight-total_weight2
        if total_lumi > 0 and denom > 0:
            bunch_rms_lumi = sqrt(total_weight*total_int2/denom)

        output_line += "[%d,%2.4e,%2.4e,%2.4e]," % (lumi_section, total_lumi, bunch_rms_lumi, mean_int)
        last_valid_lumi = [lumi_section, total_lumi, bunch_rms_lumi, mean_int]

    output_line = output_line[:-1] + ']}'
    csv_input.close()

    outputfile = open(output,'w')
    if not outputfile:
        raise RuntimeError("Could not open '%s' as an output JSON file" % output)

    outputfile.write(output_line)
    outputfile.close()
    print("Output written to", output)
