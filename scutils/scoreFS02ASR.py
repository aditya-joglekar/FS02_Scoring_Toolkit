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
    def_out_path = util.get_results_path()+'ASR_WER_Result_'+util.getDateTimeStrStamp()+'.txt'
   
    
    
    desc='Wrapper File to generate WER Scores for FS02 Challenge ASR (track1 and track2) Task.' +\
        'Scoring mechanism for both tracks is the same, but the system output '+\
        'hypothesis file/folder expected from the user will be different. '+\
        '(folder with json files for track-1, and a plain text file for track-2)'+\
        'For more information regarding scoring input and hypothesis files, '+\
        'refer below arguments description. Open-Source Software Credits: '+\
        'This script uses compute-wer tool from the Kaldi Speech Recognition '+\
        'Toolkit. for more info, refer: (http://kaldi-asr.org/doc/tools.html)'
    
    ref_mp = 'egs/ref_gt/ASR/ASR_track'
    hyp_mp = 'egs/sys_results/ASR/ASR_track'
    
    ref_def = sctk_path+ref_mp
    hyp_def = sctk_path+hyp_mp
            
    ref_str = 'Reference (ground truth) Path. '+\
        '(Directory Path for Track-1, and File Path for Track-2) '+\
        'Directory Path for Track-1 must include only ASR ground truth files. '+\
        'For ASR_track1: directory containing json format ground truth files required. '+\
        'Please refer ./'+ref_mp+'1/ directory for examples. '+\
        'For ASR_track2: kaldi "text" file. Refer: { https://kaldi-asr.org/doc/data_prep.html#data_prep_data }. '+\
        '   file contents of File Path for Track-2 must include only FS02_ASR_track2 '+\
        'file-names followed by associated transcripts (like in Kaldi "text" format)'+\
        'Please refer ./'+ref_mp+'2/ directory for examples.'
    hyp_str = 'Hypothesis (system output) Directory/File Path. '+\
        '(Directory Path for Track-1, and File Path for Track-2) '+\
        'Directory Path for Track-1 must include only FS02-ASR system output files. '+\
        'For ASR_track1: directory containing json format system output files required. '+\
        'Please refer ./'+ref_mp+'1/ directory for examples and file format. '+\
        'For ASR_track2: kaldi "text" file. Refer: { https://kaldi-asr.org/doc/data_prep.html#data_prep_data }. '+\
        'file contents of File Path for Track-2 must include only FS02_ASR_track2 '+\
        'file-names followed by associated transcripts (like in Kaldi "text" format)'+\
        'Please refer ./'+ref_mp+'2/ directory for examples and file format.'
    out_str = 'Output (overall system score) File Path. '+\
        'Default: Result file will stored in '+util.get_results_path()+' directory. '+\
        'Additional log files if generated will be stored in '+util.get_logs_path()
    trk_str = 'Track number of the ASR Task to be evaluated. '+\
        'Input Options: (as string) "1" or "2"'
    kld_str = 'base path to the locally installed kaldi directory. '+\
        'e.g. /home/crss/kaldi. This argument is required for'
    
    
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-track', '--track', type=str, default='1', help=trk_str)
    parser.add_argument('-kaldi','--kaldi', type=str, required=True, help=kld_str)
    parser.add_argument('-ref', '--ref', type=str, default=ref_def, help=ref_str)
    parser.add_argument('-hyp', '--hyp', type=str, default=hyp_def, help=hyp_str)
    parser.add_argument('-out', '--out', type=str, default=def_out_path, help=out_str)
     
    args = parser.parse_args()
    
    track_num = proc_track_num(args.track)
    kaldi_path = util.processInpPath(args.kaldi)    
    if args.ref == ref_def or args.hyp == hyp_def:
        ad = str(track_num)+'/'
        t2_name = 'FS01_ASR_track2_transcriptions_Dev'
        print('ref or hyp paths are either not provided, or match default paths.')
        print('Running Script on default example for Track-',str(track_num))
        if track_num == 2:
            args.ref = ref_def+ad+t2_name
            args.hyp = hyp_def+ad+t2_name
        else:
            args.ref = ref_def+ad
            args.hyp = hyp_def+ad
    if track_num == 2:
        ref_path = util.processInpPath(args.ref, inpType='file', checkExists=True)
        hyp_path = util.processInpPath(args.hyp, inpType='file', checkExists=True)
    else:
        ref_path = util.processInpPath(args.ref)
        hyp_path = util.processInpPath(args.hyp)
    out_path = util.processInpPath(args.out, inpType='file')
    
    return ref_path, hyp_path, out_path, track_num, kaldi_path



def proc_track_num(track_num):
    msg = 'Invalid Track number input. Valid Inputs: 1 or 2'
    msg = msg + '\nRunning script on default example for Track-1'
    if util.is_number(track_num):
        track_num = int(abs(float(track_num)))
        if track_num not in [1,2]:
            print(msg)
            track_num = 1
    else:
        print(msg)
        track_num = 1
    return track_num


def get_write_msg_list(params):
    ref_path, hyp_path, track_num = params
    ft = 'File' if track_num == 2 else 'Directory'
    strz = '\t\t'+'*'*40+'\n'
    write_msg = [strz+'\t\t--Stating ASR system Evaluation for FS02--\n'+strz]
    write_msg.append('\tWord Error Rate evaluation for : Track-'+str(track_num))
    write_msg.append('\tGround Truth '+ft+' Path : '+ref_path)
    write_msg.append('\tSystem Output '+ft+' Path : '+hyp_path)
    write_msg.append('\n\n') 
    return write_msg


def score_all_ASR(ref_path, hyp_path, write_msg, kaldi_path, track_num):
    if track_num ==1:
        gt_fp = 'ark:'+util.json_dir_to_txt(ref_path, dirType='ref')
        hyp_fp = 'ark:'+util.json_dir_to_txt(hyp_path, dirType='hyp')
    else:
        gt_fp = 'ark:'+ref_path
        hyp_fp = 'ark:'+hyp_path
    
    kld_cmd_path = kaldi_path+'src/bin/compute-wer'
    cmode = '--mode=all'
    file_term_cmd = [kld_cmd_path, '--text', cmode, gt_fp, hyp_fp]
    asr_file_termOut = util.get_term_output(file_term_cmd)
    write_msg.append('\n\n\n'+asr_file_termOut+'\n\n\n')
    wer_mrkr = '%WER'
    if wer_mrkr not in asr_file_termOut:
        print('Error in computing WER. Please check the output file for logs')
        overall_wer = 'NaN'
    else:
        overall_wer = asr_file_termOut.split(wer_mrkr)[-1].strip().split()[0].strip()
        wline = '\n\n'; print(wline); write_msg.append(wline)
        wline = '\t'+'*'*60; print(wline); write_msg.append(wline)
        wline = '\tOVERALL WER Result for FS02 ASR Track-'+str(track_num)+' Task: '+overall_wer+' %'
        print(wline); write_msg.append(wline)
        wline = '\t'+'*'*60; print(wline); write_msg.append(wline)
        wline = '\n\n'; print(wline)
    return overall_wer, write_msg



if __name__ == '__main__':

    # Input Arguments
    ref_path, hyp_path, out_path, track_num, kaldi_path = parse_arguments()
    
    # Results and Log
    write_msg = get_write_msg_list((ref_path, hyp_path, track_num))
    
    # Score Files  
    overall_wer, write_msg = score_all_ASR(ref_path, hyp_path, write_msg, kaldi_path, track_num)
    del ref_path, hyp_path, kaldi_path, track_num
    
    # Write Results and Log
    util.writeList(write_msg, out_path, isOverWrite=True)
    del write_msg, out_path
# EOF