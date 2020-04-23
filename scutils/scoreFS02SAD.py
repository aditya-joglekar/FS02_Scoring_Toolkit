#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 5 2020

@author: Aditya Joglekar

###############################################################################
# Revision history
# v1.0 (April 15, 2020)
#    - Aditya Joglekar
#    Developed using Python v3.6.7
#
###############################################################################
# This software was developed at the University of Texas at Dallas, Center for  
# Robust Speech Systems (UTD-CRSS). It serves as a wrapper around multiple  
# third-party open-source code listed below. This software is licensed under 
# a Creative Commons Attribution-ShareAlike 4.0 International License.
#
# UTD-CRSS assumes no responsibility whatsoever for its use by any party, and 
# makes no guarantees, expressed or implied, about its quality, reliability, 
# or any other characteristic. We would appreciate acknowledgement if the 
# software is used. This software can be redistributed and/or modified freely 
# provided that any derivative works bear some notice that they are derived 
# from it, and any modified versions bear some notice that they 
# have been modified.
#
# THIS SOFTWARE IS PROVIDED "AS IS."  With regard to this software, 
# UTD-CRSS MAKES NO EXPRESS OR IMPLIED WARRANTY AS TO ANY MATTER WHATSOEVER, 
# INCLUDING MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
#
# Open-Source Software Credits:
# KALDI         - ASR          -  WER   - (http://kaldi-asr.org/), 
#                                         (https://github.com/kaldi-asr/kaldi/
#                                         blob/master/src/bin/compute-wer.cc)
# DSCORE        - DIARIZATION  -  DER   - (https://github.com/nryant/dscore)
# NIST openSAT  - SAD          -  DCF   - (https://www.nist.gov/itl/iad/mig/
#                             nist-open-speech-activity-detection-evaluation)
###############################################################################
"""


import fs02utils as util
import argparse




def parse_arguments():
    
    sctk_path = util.get_fs02sctk_path()
    def_out_path = util.get_results_path()+'SAD_DCF_Result_'+util.getDateTimeStrStamp()+'.txt'
    coll_inps_str = 'Allowed Inputs: 0, 0.25, 0.5, 1, 2'
    
    
    desc='Wrapper File to generate DCF Scores for FS02 Challenge SAD Task.' +\
        'For more information regarding scoring input and hypothesis files, '+\
        'refer below arguments description.'+\
        'Open-Source Software Credits: This script uses scoreFile_SAD.pl '+\
        'developed by NIST. for more info, refer: (https://www.nist.gov/'+\
        'itl/iad/mig/nist-open-speech-activity-detection-evaluation)'
    
    ref_mp = 'egs/ref_gt/SAD/'
    hyp_mp = 'egs/sys_results/SAD/'
    
    ref_def = sctk_path+ref_mp
    hyp_def = sctk_path+hyp_mp
    
    
    ref_str = 'Reference (ground truth) Directory Path. '+\
        'This directory must include only SAD ground truth files. '+\
        'Please refer ./'+ref_mp+' directory for examples.'
    hyp_str = 'Hypothesis (system output) Directory Path. '+\
        'This directory must include only SAD system output files. '+\
        'Please refer ./'+hyp_mp+' directory for examples and file format.'
    out_str = 'Output (per file and overall system score) File Path. '+\
        'Default: Result file will stored in '+util.get_results_path()+' directory. '+\
        'Additional log files if generated will be stored in '+util.get_logs_path()
    clr_str = 'Desired forgiveness Collar for SAD evaluation. '+coll_inps_str+\
        ' Default collar length: 0.5 secs.'
    
    
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-ref', '--ref', type=str, default=ref_def, help=ref_str)
    parser.add_argument('-hyp', '--hyp', type=str, default=hyp_def, help=hyp_str)
    parser.add_argument('-out', '--out', type=str, default=def_out_path, help=out_str)
    parser.add_argument('-sadcollar', '--sadcollar', type=float, default=0.5, help=clr_str)
    
    args = parser.parse_args()
    ref_path = util.processInpPath(args.ref)
    hyp_path = util.processInpPath(args.hyp)
    out_path = util.processInpPath(args.out, inpType='file')
    sadcollar = proc_sad_collar(args.sadcollar)
    
    return ref_path, hyp_path, out_path, sadcollar



def proc_sad_collar(sadcollar):
    coll_inps = [0, 0.25, 0.5, 1, 2]
    if float(sadcollar) not in coll_inps:
        print('SAD Collar provided not allowed. Evaluating using default (0.5) collar.')
        print('Allowable Collars: ',str(coll_inps))
        sadcollar = 0.5
    return str(float(sadcollar))



def get_write_msg_list(params):
    
    ref_path, hyp_path, sadcollar = params
    
    strz = '\t\t'+'*'*40+'\n'
    write_msg = [strz+'\t\t--Stating SAD system Evaluation for FS02--\n'+strz]
    write_msg.append('\tGround Truth Directory Path : '+ref_path)
    write_msg.append('\tSystem Output Directory Path : '+hyp_path)
    write_msg.append('\tforgiveness collar for SAD evaluation : '+str(sadcollar))
    write_msg.append('\n\n')
    
    return write_msg
    


def score_file_SAD(gt_fp, hyp_fp, sadcollar):
        
    temp_out_fp = util.get_temp_path()+util.getfName(gt_fp)+'.out'
    util.remove_file(temp_out_fp)
    scprl_fath = util.get_fs02sctk_path()+'scutils/scoreFile_SAD.pl'
    term_cmd = ['perl', scprl_fath, '-r', gt_fp, '-h', hyp_fp, '-s', '2', '-e',
               '3', '-g', '4', '-t', '5', '-f', '6', '-u', '7', '-o', temp_out_fp]
    
    termOut = util.get_term_output(term_cmd)

    termOut = termOut.strip().replace('\n\n','\n').split('\n')
    termOut = [x.strip() for x in termOut][2:]
    util.remove_file(temp_out_fp)

    collarDict = {'0.0':3, '0.25':7, '0.5':11, '1.0':15, '2.0':19}
    dcf_desired = termOut[int(collarDict[sadcollar])].split()[2].strip()
    if not util.is_number(dcf_desired):
        dcf_desired = 'NaN'
    return dcf_desired



def score_folder_SAD(fileList, fileDict, sadcollar, write_msg):
    dcfDict = {}
    non_scored = []
    for fname in fileList:
        dcf = score_file_SAD(fileDict['ref'][fname], fileDict['hyp'][fname], sadcollar)
        if dcf == 'NaN':
            non_scored.append(fname)
        else:
            dcfDict[fname] = dcf
    
    if len(non_scored) > 0:
        wline = '\nThe following files cound not be scored:\n\t'
        +' '.join(non_scored)+'\nPlease check the System Output for errors.\n'
        write_msg.append(wline)
    
    wline = 'Files Succesfully Evaluated: '+str(len(dcfDict))+'\n'
    write_msg.append(wline)
    return dcfDict, write_msg



def get_SAD_results(dcfDict, write_msg):
    
    overall_dcf = 0.0
    numFiles = len(dcfDict)
    
    write_msg.append('\n\n\t---Individual DCF Scores---\n')
    write_msg.append('   File Name\t:\t  DCF')
    for fname in dcfDict:    
        curr_dcf = dcfDict[fname]
        write_msg.append(fname+'\t:\t'+curr_dcf)
        overall_dcf += float(curr_dcf)
    overall_dcf = str(round(overall_dcf/numFiles,5))
    dcf_pc = ' ('+str(float(overall_dcf)*100)+' %)'
    
    wline = '\n\n'; print(wline); write_msg.append(wline)
    wline = '\t'+'*'*60; print(wline); write_msg.append(wline)
    wline = '\tOVERALL DCF Result for FS02 SAD Task: '+overall_dcf+dcf_pc
    print(wline); write_msg.append(wline)
    wline = '\t'+'*'*60; print(wline); write_msg.append(wline)
    wline = '\n\n'; print(wline)
    
    return overall_dcf, write_msg



if __name__ == '__main__':

    # Input Arguments
    ref_path, hyp_path, out_path, sadcollar = parse_arguments()
    
    # Results and Log
    write_msg = get_write_msg_list((ref_path, hyp_path, sadcollar))
    
    # Get Files to Score
    fileList, fileDict, write_msg = util.get_files_to_score(ref_path, hyp_path, write_msg)
    del ref_path, hyp_path
    
    # Score Files
    dcfDict, write_msg = score_folder_SAD(fileList, fileDict, sadcollar, write_msg)
    del sadcollar, fileList, fileDict
    
    # Get SAD DCF results
    overall_dcf, write_msg = get_SAD_results(dcfDict, write_msg)
    
    # Write Results and Log
    util.writeList(write_msg, out_path, isOverWrite=True)
    del write_msg, out_path



