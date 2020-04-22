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
# KALDI         - ASR           - WER - (http://kaldi-asr.org/), 
#       (https://github.com/kaldi-asr/kaldi/blob/master/src/bin/compute-wer.cc)
# DSCORE       - DIARIZATION   - DER - (https://github.com/nryant/dscore)
# NIST openSAT  - SAD           - DCF 
###############################################################################
"""

import fs02utils as util
import argparse



def parse_arguments():
    sctk_path = util.get_fs02sctk_path()
    def_out_path = util.get_results_path()+'ASR_WER_Result_'+util.getDateTimeStrStamp()+'.txt'
    def_ref_path = sctk_path+'egs/ref_gt/ASR/ASR_track'
    def_hyp_path = sctk_path+'egs/sys_results/ASR/ASR_track'
    
    parser = argparse.ArgumentParser(description='Wrapper File to generate ASR (track1 and track2) Scores for FS02 Challenge')
    
    parser.add_argument('-track', '--track', type=str, default='1', 
                        help='Evaluation of Task-track.\nInput Options: [1 , 2]'+
                        '\nDefault (no input) will run script on ASR-track1 example in ./egs/')
    parser.add_argument('-kaldi','--kaldi','-kaldipath', '--kaldipath', type=str, required=True,
                        help='base path to the locally installed kaldi directory.'+
                        '\ne.g. /home/crss/kaldi')
    parser.add_argument('-ref', '--ref', type=str, default=def_ref_path,
                        help='Reference (ground truth) Directory Path (for Track-1),'+
                        ' or File Path (for Track-2)')
    parser.add_argument('-hyp', '--hyp', type=str, default=def_hyp_path,
                        help='Hypothesis (system output) Directory Path (for Track-1),'+
                        ' or File Path (for Track-2)')
    parser.add_argument('-out', '--out', type=str, default=def_out_path,
                        help='Output (system score) File Path. \nDefault: Results stored in "results" dir')    
    args = parser.parse_args()
    
    track_num = proc_track_num(args.track)
    kaldi_path = util.processInpPath(args.kaldi)    
    if args.ref == def_ref_path or args.hyp == def_hyp_path:
        ad = str(track_num)+'/'
        def_2_name = 'FS02_ASR_track2_transcriptions_Dev'
        print('ref or hyp paths are either not provided, or match default paths.')
        print('Running Script on default example for Track-',str(track_num))
        if track_num == 2:
            args.ref = def_ref_path+ad+def_2_name
            args.hyp = def_hyp_path+ad+def_2_name
        else:
            args.ref = def_ref_path+ad
            args.hyp = def_hyp_path+ad
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