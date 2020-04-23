#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 5 2020

@author: Aditya Joglekar

###############################################################################
# Revision history
# v1.0 (April 15, 2020)
#    - Aditya Joglekar
#    Developed using Python v3.7.7
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
# KALDI         - ASR          -  WER   - (http://kaldi-asr.org), 
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
    def_out_path = util.get_results_path()+'SD_DER_Result_'+util.getDateTimeStrStamp()+'.txt'
    coll_inps_str = 'Allowed Inputs: 0, 0.25, 0.5, 1, 2'
    
    
    desc='Wrapper File to generate DER Scores for FS02 Challenge SD (track1 and track2) Tasks.' +\
        'Scoring mechanism for both tracks will be the same. For more '+\
        'information regarding scoring input and hypothesis files, refer '+\
        'below arguments description. Open-Source Software Credits: '+\
        'This script uses dscore toolkit developed by Neville Ryant for '+\
        'generating DER scores. for more info, refer: (https://github.com/nryant/dscore)'
    
    ref_mp = 'egs/ref_gt/SD/'
    hyp_mp = 'egs/sys_results/SD/'
    
    ref_def = sctk_path+ref_mp
    hyp_def = sctk_path+hyp_mp
    
    
    ref_str = 'Reference (ground truth) Directory Path. '+\
        'This directory must include only SD ground truth RTTM '+\
        'and UEM folders. Please refer ./'+ref_mp+' directory for examples.'
    hyp_str = 'Hypothesis (system output) Directory Path. '+\
        'This directory must include only diarization system output RTTM files. '+\
        'Please refer ./'+hyp_mp+' directory for examples and file format.'
    out_str = 'Output (per file and overall system score) File Path. '+\
        'Default: Result file will stored in '+util.get_results_path()+' directory. '+\
        'Additional log files if generated will be stored in '+util.get_logs_path()
    clr_str = 'Desired forgiveness Collar for SD evaluation. '+coll_inps_str+\
        ' Default collar length: 0.25 secs.'
    
    
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-ref', '--ref', type=str, default=ref_def, help=ref_str)
    parser.add_argument('-hyp', '--hyp', type=str, default=hyp_def, help=hyp_str)
    parser.add_argument('-out', '--out', type=str, default=def_out_path, help=out_str)
    parser.add_argument('-diarcollar', '--diarcollar', type=float, default=0.25, help=clr_str)
    args = parser.parse_args()
    
    ref_path = proc_sd_ref_files(util.processInpPath(args.ref))
    hyp_path = util.processInpPath(args.hyp)
    out_path = util.processInpPath(args.out, inpType='file')
    diarcollar = proc_sd_collar(args.diarcollar)
    
    return ref_path, hyp_path, out_path, diarcollar


def proc_sd_ref_files(ref_path):
    rttm_path = ref_path+'RTTM/'
    uem_path = ref_path+'UEM/'
    if not util.check_isDir(rttm_path):
        print('Ground Truth RTTM Folder does not exist in ref path.')
        util.terminate_program()
    if not util.check_isDir(uem_path):
        print('Ground Truth UEM Folder does not exist in ref path.')
        util.terminate_program()
    
    rttm_list = util.get_from_dir(rttm_path)
    uem_list = util.get_from_dir(uem_path)
    
    if len(rttm_list) < 1:
        print('\nNo RTTM files found in ref path. Cannot provide score.')
        util.terminate_program()
    if len(uem_list) < 1:
        print('\nNo UEM files found in ref path. Cannot provide score.')
        util.terminate_program()
    
    rttm_dict = {util.getfName(x):x for x in rttm_list}
    uem_dict = {util.getfName(x):x for x in uem_list}
    missing_from_uem = list(set(rttm_dict.keys()) - set(uem_dict.keys()))
    missing_from_rttm = list(set(uem_dict.keys()) - set(rttm_dict.keys()))
    
    if len(missing_from_uem+missing_from_rttm) > 0:
        print('Uncommon Files found between Ground Truth RTTM and UEM folders.')
        print('Missing Files:')
        if len(missing_from_uem) > 0:
            for fn in missing_from_uem:
                print(fn+'.uem')
        if len(missing_from_rttm) > 0:
            for fn in missing_from_rttm:
                print(fn+'.rttm')
        util.terminate_program()
    return ref_path


def proc_sd_collar(diarcollar):
    coll_inps = [0, 0.25, 0.5, 1, 2]
    if float(diarcollar) not in coll_inps:
        print('SD Collar provided not allowed. Evaluating using default (0.25) collar.')
        print('Allowable Collars: ',str(coll_inps))
        diarcollar = 0.25
    return str(float(diarcollar))


def get_write_msg_list(params):
    
    ref_path, hyp_path, diarcollar = params
    
    strz = '\t\t'+'*'*60+'\n'
    write_msg = [strz+'\t\t--Stating SD (track1 and track2) system Evaluation for FS02--\n'+strz]
    write_msg.append('\tGround Truth Directory Path : '+ref_path)
    write_msg.append('\tSystem Output Directory Path : '+hyp_path)
    write_msg.append('\tforgiveness collar for SD evaluation : '+str(diarcollar))
    write_msg.append('\n\n')
    
    return write_msg
    

def score_file_SAD(py_val_path, py_score_path, fname, ref_rttm, hyp_rttm, ref_uem, diarcollar):
    
    val_term_cmd = ['python', py_val_path, ref_rttm, hyp_rttm]
    val_termOut = util.get_term_output(val_term_cmd)
    
    sc_term_cmd = ['python', py_score_path, '--ignore_overlaps', '--collar', 
                    diarcollar, '-u', ref_uem, '-r', ref_rttm, '-s', hyp_rttm]
    sc_termOut = util.get_term_output(sc_term_cmd)

    if len(sc_termOut.split('*** OVERALL ***')) == 2:
        der = sc_termOut.split('*** OVERALL ***')[-1].strip().split()[0]
    else:
        print('Error in scoring', fname,'. Please Check the log file.\n')
        der = 'NaN'    
    strz = '\n\n\t\t'+'*'*60+'\n\n\n'
    log_desc = '\n---Scoring Log for file:'+fname+'---'
    log_list = [log_desc,'\n\n',val_termOut,'\n\n', sc_termOut,strz]
    
    return der, log_list



def score_folder_SD(fileList, fileDict, diarcollar, write_msg, out_path):
    sctk_path = util.get_fs02sctk_path()
    py_val_path = sctk_path+'scutils/dscore/validate_rttm.py'
    py_score_path = sctk_path+'scutils/dscore/score.py'
    log_write_path = util.get_logs_path()+util.get_bname(out_path)+'.log'
    derDict = {}
    log_list = []
    unsuc_files = []
    for fn in fileList:
        ref_rttm = fileDict['ref'][fn]
        hyp_rttm = fileDict['hyp'][fn]
        ref_uem = ref_rttm.replace('/RTTM/','/UEM/').replace('.rttm','.uem')
        der, curr_log = score_file_SAD(py_val_path, py_score_path, 
                               fn, ref_rttm, hyp_rttm, ref_uem, diarcollar)
        if der != 'NaN':
            derDict[fn] = der
        else:
            unsuc_files.append(fn)
        log_list += curr_log
    with open(log_write_path,'w') as file:
            file.write('\n'.join(log_list))
            print('\n\nLog File for SD Task - DER evaluation',
                  'written to path:\n\t',log_write_path,'\n\n')
    
    write_msg.append('\n\n')
    write_msg.append('Number of Files to be Evaluated:'+str(len(fileList))+'\n\n')
    write_msg.append('Number of Files Successfully Evaluated:'+str(len(derDict))+'\n\n')
    if len(unsuc_files) > 0:
        write_msg.append('Files that could not be evaluated:\n\t'+' '.join(unsuc_files))
    return derDict, write_msg

def get_SD_results(derDict, write_msg):
    
    overall_der = 0.0
    numFiles = len(derDict)
    
    write_msg.append('\n\n\t---Individual DER Scores---\n')
    write_msg.append('   File Name\t:\t  DER')
    for fn in derDict:
        der = derDict[fn]
        overall_der += float(der)
        write_msg.append(fn+'\t:\t'+der)
    overall_der = str(round(overall_der/numFiles,5))
    wline = '\n\n'; print(wline); write_msg.append(wline)
    wline = '\t'+'*'*50; print(wline); write_msg.append(wline)
    wline = '\tOVERALL DER Result for FS02 SD Task: '+overall_der+' %'
    print(wline); write_msg.append(wline)
    wline = '\t'+'*'*50; print(wline); write_msg.append(wline)
    wline = '\n\n'; print(wline)
        
    
    return overall_der, write_msg


if __name__ == '__main__':

    # Input Arguments
    ref_path, hyp_path, out_path, diarcollar = parse_arguments()
    
    
    # Results and Log
    write_msg = get_write_msg_list((ref_path, hyp_path, diarcollar))
    
    # Get Files to Score
    fileList, fileDict, write_msg = util.get_files_to_score(ref_path+'RTTM/', hyp_path, write_msg)
    del ref_path, hyp_path
    
    # Score Files
    derDict, write_msg = score_folder_SD(fileList, fileDict, diarcollar, write_msg, out_path)
    del diarcollar, fileList, fileDict
    
    # Get SD DER results
    overall_der, write_msg = get_SD_results(derDict, write_msg)
    
    # Write Results and Log
    util.writeList(write_msg, out_path, isOverWrite=True)
    del write_msg, out_path
# EOF