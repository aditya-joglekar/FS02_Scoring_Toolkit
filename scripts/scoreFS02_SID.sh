#!/bin/bash
# Created on Sun Apr 12 2020
# @author: Aditya Joglekar
set -e
source $(dirname $(realpath "$0"))/cfg_path.sh


#----------------------------------------------------------#
# Script to generate DCF Scores for FS02 Challenge SID Task
# 
# USAGE:
#   bash scoreFS02_SID.sh <ref_path> <hyp_path> <out_path> 
#  
#       ref_path: Reference (Ground Truth) File Path
#       hyp_path: Hypothesis (System Output) File Path
#       out_path: File Path to write Top-5 Accuracy Score
# 
# EXAMPLES:
#   Get Description and Help Options: 
#       bash ./scripts/scoreFS02_SID.sh
# 
#   Run on Default Example:
#       bash ./scripts/scoreFS02_SID.sh ./egs/ref_gt/SID/FS01_SID_uttID2spkID_Dev.txt ./egs/sys_results/SID/FS01_SID_uttID2spkID_Dev.txt
#        
#----------------------------------------------------------#


# Input arguments
ref_path=$1
hyp_path=$2
out_path=$3


# Run Score File
if [ $# -eq 0 ]; then
    # Help options
    $python_path $sid_score_file -h
else
    if [ -z "$ref_path" ] || [ -z "$hyp_path" ]; then
        # generates score on default example provided with the toolkit
        echo -e "\nInput (ref or hyp) paths not provided."
        echo -e "Running scipt on default example.\n"
        $python_path $sid_score_file
    else
        if [ -z "$out_path" ]; then
            # generates score and saves it to the default path
            $python_path $sid_score_file --ref $ref_path --hyp $hyp_path \
            --topN $topN_eval
        else
            # generates score and saves it to the path provided by user
            $python_path $sid_score_file --ref $ref_path --hyp $hyp_path \
            --out $out_path --topN $topN_eval
        fi    
    fi
fi


# remove temp folder
rm -rf $temp_path
# END