#!/bin/bash
# Created on Sun Apr 12 2020
# @author: Aditya Joglekar
set -e
source $(dirname $(realpath "$0"))/cfg_path.sh


#--------------------------------------------------------------------#
# Script to generate DCF Scores for FS02 Challenge ASR Task
# (different inputs type required for ASR_track1 and ASR_track2)
# (Check help for details)
# 
# USAGE:
#   bash scoreFS02_ASR.sh <ref_path> <hyp_path> <out_path> 
#  
#       ref_path: Reference (Ground Truth) Directory/File Path
#       hyp_path: Hypothesis (System Output) Directory/File Path
#       out_path: File Path to write Overall WER Score
#   
#   REQUIRED Before running script: 
#       set local Kaldi path in cfg_path.sh script.
#       set desired track number to be evaluated in cfg_path.sh script
# 
# EXAMPLES:
#   Get Description and Help Options: 
#       bash ./scripts/scoreFS02_ASR.sh
# 
#   Run on Default Examples:
#(track_num="1")     bash ./scripts/scoreFS02_ASR.sh ./egs/ref_gt/ASR/ASR_track1/ ./egs/sys_results/ASR/ASR_track1/
#(track_num="2")     bash ./scripts/scoreFS02_ASR.sh ./egs/ref_gt/ASR/ASR_track2/FS01_ASR_track2_transcriptions_Dev ./egs/sys_results/ASR/ASR_track2/FS01_ASR_track2_transcriptions_Dev
#--------------------------------------------------------------------#


# Input arguments
ref_path=$1
hyp_path=$2
out_path=$3


# Check Kaldi path
if [ ! -f ${kaldi_path}/src/bin/compute-wer ]; then
    echo -e "Kaldi path is either not a valid directory \
or does not contain compute-wer.\nCannot compute WER scores. \
Please insert a valid Kaldi path in the ./cfg_path.sh file. \
\nTerminating program...\n\n\n"
    exit 1;
fi


# Run Score File
if [ $# -eq 0 ]; then
    # Help options
    $python_path $asr_score_file -h
else
    if [ -z "$ref_path" ] || [ -z "$hyp_path" ]; then
        # generates score on default example provided with the toolkit
        echo -e "\nInput (ref or hyp) paths not provided."
        echo -e "Running scipt on default example.\n"
        $python_path $asr_score_file --kaldi $kaldi_path --track $track_num
    else
        if [ -z "$out_path" ]; then
            # generates score and saves it to the default path
            $python_path $asr_score_file --kaldi $kaldi_path \
            --track $track_num --ref $ref_path --hyp $hyp_path
        else
            # generates score and saves it to the path provided by user
            $python_path $asr_score_file --kaldi $kaldi_path \
            --track $track_num --ref $ref_path \
            --hyp $hyp_path --out $out_path
        fi    
    fi
fi


# remove temp folder
rm -rf $temp_path
# END