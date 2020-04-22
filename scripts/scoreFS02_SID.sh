#!/bin/bash
set -e
source $(dirname $(realpath "$0"))/cfg_path.sh


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