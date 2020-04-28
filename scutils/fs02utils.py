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


import os, glob, sys, json, re
from datetime import datetime
from string import ascii_letters
from subprocess import Popen, PIPE, STDOUT


def moveup_dir(file_path):
    return os.path.normpath(file_path + os.sep + os.pardir)


def get_fs02sctk_path():
    sctk_path = moveup_dir(os.path.dirname(os.path.realpath(__file__)))
    if sctk_path[-1] != '/':
        sctk_path += '/' 
    return sctk_path


def get_temp_path():
    temp_path = get_fs02sctk_path()+'egs/.temp/'
    if not os.path.isdir(temp_path):
        os.mkdir(temp_path)
    return temp_path


def get_results_path():
    results_path = get_fs02sctk_path()+'results/'
    if not os.path.isdir(results_path):
        os.mkdir(results_path)
    return results_path


def get_logs_path():
    logs_path = get_fs02sctk_path()+'logs/'
    if not os.path.isdir(logs_path):
        os.mkdir(logs_path)
    return logs_path


def terminate_program():
    print('Terminating FS02 score-file without scoring execution\n')
    sys.exit()


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def check_isDir(inp_path):
    if os.path.isdir(inp_path):
        boolVal = True
    else:
        boolVal = False
    return boolVal


def get_from_dir(inp_path):
    filepath_list = glob.glob(inp_path+'*')
    return filepath_list
    

def getDateTimeStrStamp():
    now = datetime.now()
    dt_string = now.strftime("%d%b%Y_%H-%M-%S")
    return dt_string


# term_cmd should be a list
def get_term_output(term_cmd):
    p = Popen(term_cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    termOut = p.stdout.read().decode()
    return termOut


def is_number(num_str):
    try:
        float(num_str)
        return True
    except ValueError:
        return False


""" USAGE: fileName = util.getfName(filePath) """
def getfName(file_path):
    fp = os.path.basename(file_path)
    return str('.'.join(fp.split('.')[:-1]).strip())


def get_bname(file_path):
    return os.path.basename(file_path)


""" USAGE: util.writeList(writeList, writePath, isOverWrite) """   
def writeList(writelist, writePath, isOverWrite=False, verbose=True):
    if os.path.isfile(writePath) and not isOverWrite:
        print('Cannot OverWrite. File Exists at Path:\n',writePath)
    else:
        with open(writePath,'w') as file:
            file.write('\n'.join(writelist))
        if verbose:
            print('Content / Scores Written to Path:\n',writePath,'\n\n\n')


""" USAGE: readList = util.readList(readPath) """
def readList(readPath):
    with open(readPath,'r') as file:
        readList = file.read().strip().split('\n')
        readList = [x.strip() for x in readList]
    return readList




def get_json_txtstr(file_path):
    # to allow words like let's, we're, etc
    english_chars = set(ascii_letters + "'")
    content = []
    with open(file_path,'r') as file:  
        data = json.load(file)
        if not type(data)==list:
            data = [data]
        for utt in data:
            # scoring words like we're will be held off for the third phase of the challenge
            words = utt['words'].replace("'","")
            words = re.sub(r'[,.;:@#?!&$]+', ' ', words)
            words = words.replace('[unk]','').upper()
            words = ' '.join(e for e in words.split() if english_chars.issuperset(e))
            content.append(words)
    content = ' '.join(content)
    content = re.sub(' +', ' ',content)
    content = content.strip()
    return content


def json_dir_to_txt(dir_path, dirType):
    json_fp_list = get_from_dir(dir_path)
    write_path = get_temp_path()+'ASR_track1_'+dirType+'_'+getDateTimeStrStamp()
    writelist = []
    for fp in json_fp_list:
        fname = getfName(fp)
        str_transcript = get_json_txtstr(fp)
        writelist.append(fname+' '+str_transcript)
    writelist.sort()
    writeList(writelist, write_path, isOverWrite=True, verbose=False)
    return write_path


def processInpPath(inp_path, inpType='dir', checkExists=False):
    if inp_path is not None:
        inp_path = str(inp_path)
    else:
        print('No Input Path provided')
        terminate_program()
    if inp_path[-1] == '/':
        inp_path = inp_path[:-1]
    
    if inpType == 'file':
        dir_name = os.path.dirname(inp_path)
        if not os.path.isdir(dir_name):
            print(dir_name,' -> Directory Path of file does not Exist.')
            terminate_program()
        else:
            if checkExists:
                if not os.path.isfile(inp_path):
                    print(inp_path,' -> File Path does not Exist.')
                    terminate_program()
            return inp_path
    else:
        if not os.path.isdir(inp_path):
            print(inp_path,' -> Path is not a Directory or does not Exist')
            terminate_program()
        else:
            if inp_path[-1] != '/':
                inp_path += '/'
            return inp_path

def get_files_to_score(ref_path, hyp_path, write_msg, isFolder=True, task=''):
    fileDict = {'ref':{},'hyp':{}}
    
    if isFolder:
        ref_list = get_from_dir(ref_path)
        hyp_list = get_from_dir(hyp_path)
    else:
        ref_list = readList(ref_path)
        hyp_list = readList(hyp_path)
    
    if len(ref_list) < 1:
        print('\nNo Reference files found in ref path. Cannot provide score.')
        terminate_program()
    if len(hyp_list) < 1:
        print('\nNo System Output files found in hyp path. Cannot provide score.')
        terminate_program()

    if isFolder:
        ref_dict = {getfName(x):x for x in ref_list}
        hyp_dict = {getfName(x):x for x in hyp_list}
    else:
        if task == 'SID':
            ref_dict = {x.split()[0].strip():x.split()[-1].strip() for x in ref_list}
            hyp_dict = {x.split()[0].strip():[y.strip() for y in x.split()[1:]] for x in hyp_list}
        else:
            ref_dict = {x.split()[0].strip():' '.join(x.split()[1:]).strip() for x in ref_list}
            hyp_dict = {x.split()[0].strip():' '.join(x.split()[1:]).strip() for x in hyp_list}
    
    missing_from_hyp = list(set(ref_dict.keys()) - set(hyp_dict.keys()))
    missing_from_ref = list(set(hyp_dict.keys()) - set(ref_dict.keys()))
    total_missing = missing_from_hyp+missing_from_ref
    
    all_file_list = list(set(list(ref_dict.keys()) + list(hyp_dict.keys()) ))
    files_to_score = list(set(set(all_file_list) - set(total_missing)))
    
    if len(files_to_score) < 1:
        print('\nNo common files between Ref and Hyp that can be scored.')
        terminate_program()
    
    files_to_score.sort()
    for fn in files_to_score:
        fileDict['ref'][fn] = ref_dict[fn]
        fileDict['hyp'][fn] = hyp_dict[fn]
        
    # write Messages
    write_msg.append('\n\nTotal Files to be Evaluated : '+str(len(files_to_score)))
    if isFolder:
        write_msg.append('\nScoring File Names:\n'+' '.join(files_to_score))
    else:
        if len(total_missing) > 0:
            write_msg.append('Number of files missing from the evaluation list: '+str(len(total_missing)))
            write_msg.append('Missing File Names:\n'+' '.join(total_missing))
        else:
            write_msg.append('No files missing from evaluation list.')
    write_msg.append('\n\n')
    
    return files_to_score, fileDict, write_msg
# EOF
