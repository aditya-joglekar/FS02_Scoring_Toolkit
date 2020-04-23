#!/bin/bash
set -e
source $(dirname $(realpath "$0"))/cfg_path.sh


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