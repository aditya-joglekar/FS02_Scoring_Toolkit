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
    def_out_path = util.get_results_path()+'SID_TopN_Result_'+util.getDateTimeStrStamp()+'.txt'
    
    parser = argparse.ArgumentParser(description='Scoring File to generate Top-N Accuracy Scores for FS02 SID Challenge Task')
    
    parser.add_argument('-ref', '--ref', type=str, 
                        default=sctk_path+'egs/ref_gt/SID/FS01_SID_uttID2spkID_Dev.txt',
                        help='Reference (ground truth) File Path')
    parser.add_argument('-hyp', '--hyp', type=str, 
                        default=sctk_path+'egs/sys_results/SID/FS01_SID_uttID2spkID_Dev.txt',
                        help='Hypothesis (system output) File Path')
    parser.add_argument('-out', '--out', type=str, default=def_out_path,
                        help='Output (system score) File Path. \nDefault: Results stored in "results" dir')
    parser.add_argument('-topN', '--topN', type=int, default=5,
                        help='Desired Top-N Accuracy for SID evaluation')
    
    args = parser.parse_args()
    ref_path = util.processInpPath(args.ref, inpType='file', checkExists=True)
    hyp_path = util.processInpPath(args.hyp, inpType='file', checkExists=True)
    out_path = util.processInpPath(args.out, inpType='file')
    max_TopN = validate_hyp_file(hyp_path)
    topN_num = proc_topN_inp(args.topN, max_TopN)
    
    return ref_path, hyp_path, out_path, topN_num


def proc_topN_inp(topN_num, max_TopN):
    if topN_num < 1:
        print('Top-N parameter has to be greater than 0.')
        print('Evaluating using default (5) value.')
        topN_num = 5
    if topN_num > max_TopN:
        print('Top-N parameter cannot be greater than no. of system predictions.')
        print('Setting Top-N value to :',str(max_TopN))
        topN_num = max_TopN
    return topN_num


def validate_hyp_file(hyp_path):
    hyp_list = util.readList(hyp_path)
    n_diff_res = len(list(set([len(x.split()) for x in hyp_list])))
    if n_diff_res != 1:
        print('System Output File not consistent.')
        print('All sample results should contain the same no. of speaker predictions.')
        util.terminate_program()
    else:
        max_TopN = len(hyp_list[1].split()) - 1
    
    return max_TopN


def get_write_msg_list(params):
    
    ref_path, hyp_path, topN_num = params
    
    strz = '\t\t'+'*'*40+'\n'
    write_msg = [strz+'\t\t--Stating SID system Evaluation for FS02--\n'+strz]
    write_msg.append('\tGround Truth File Path : '+ref_path)
    write_msg.append('\tSystem Output File Path : '+hyp_path)
    write_msg.append('\tN value for Top-N Accuracy Scoring : '+str(topN_num))
    write_msg.append('\n')
    
    return write_msg



def score_SID(fileList, fileDict, topN_num, write_msg, out_path):
    clsfd_Dict = {n:{'corr':[],'incorr':[]} for n in range(1,topN_num+1)}
    
    for fn in fileList:
        ref_str = fileDict['ref'][fn]
        hyp_str_list = fileDict['hyp'][fn]
        
        for topn in clsfd_Dict:
            hyp_topn = hyp_str_list[:topn]
            if ref_str in hyp_topn:
                clsfd_Dict[topn]['corr'].append(fn)
            else:
                clsfd_Dict[topn]['incorr'].append(fn)
    
    topNDict = {n:round((100.0*len(clsfd_Dict[n]['corr']))/len(fileList),3) for n in clsfd_Dict}
    
    write_msg.append('Individual Results (per file) written to following paths:\n')
    strz = '\t'+'*'*40+'\n'
    for n in clsfd_Dict:
        write_path = util.get_logs_path()+util.get_bname(out_path)+'.Top-'+str(n)
        write_msg.append(write_path)
        write_list = [strz+'\tPer File SID Top-'+str(n)+' Accuracy Results\n'+strz]
        write_list.append('\n\nCorrect Predictions:\n'+' '.join(clsfd_Dict[n]['corr']))
        write_list.append('\n\nIncorrect Predictions:\n'+' '.join(clsfd_Dict[n]['incorr']))
        write_list.append('\n')
        util.writeList(write_list, write_path, isOverWrite=True)
    write_msg.append('\n\n\n')
    write_msg.append(strz+'\tTop-N Acurracy System Evaluation Results:\n'+strz)
    for n in topNDict:
        write_msg.append('\tTop-'+str(n)+' Accuracy : '+str(topNDict[n])+' %')
    write_msg.append(strz+'\n')
    return topNDict, write_msg

def get_Top5_results(topNDict, write_msg):
    top5res = str(topNDict[5])
    strz = '\t'+'*'*50+'\n'
    wline = '\n'+strz+'\tTop-5 Accuracy Result for FS02 SID Task : '+top5res+' %\n'+strz+'\n\n'
    write_msg.append(wline); print(wline)
    return write_msg
    


if __name__ == '__main__':

    # Input Arguments
    ref_path, hyp_path, out_path, topN_num = parse_arguments()
    
    
    # Results and Log
    write_msg = get_write_msg_list((ref_path, hyp_path, topN_num))
    
    # Get Files to Score
    fileList, fileDict, write_msg = util.get_files_to_score(ref_path, hyp_path, 
                                        write_msg, isFolder=False, task='SID')
    del ref_path, hyp_path
    
    # Score Files
    topNDict, write_msg = score_SID(fileList, fileDict, topN_num, write_msg, out_path)
    del topN_num, fileList, fileDict
    
    # Get SID Top-5 Accuracy results
    get_Top5_results(topNDict, write_msg)
    
    # Write Results and Log
    util.writeList(write_msg, out_path, isOverWrite=True)
    del write_msg, out_path