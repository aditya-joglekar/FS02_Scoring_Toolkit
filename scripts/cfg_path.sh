#!/bin/bash

# This script contains paths and config variables for all Tasks

# Arguments to be set by user before execution 
export python_path="python" # Set desired python path               (*required)
# python_path required if not running from a virtual environment
export kaldi_path="/home/crss/kaldi" # Set kaldi path               (*required)
export track_num="1" # Set ASR Task Track number to evaluate system outputs on.

# Default settings
export sad_collar="0.5" # Default for FS02 SAD Task
export sd_collar="0.25" # Default for FS02 SD Tasks (Track-1 and Track-2)
export topN_eval="5"    # Default: 5 for FS02 SID Task

sctk_dir=$(dirname $(dirname $(realpath "$0")))

export sad_score_file=${sctk_dir}/scutils/scoreFS02SAD.py
export sd_score_file=${sctk_dir}/scutils/scoreFS02SD.py
export sid_score_file=${sctk_dir}/scutils/scoreFS02SID.py
export asr_score_file=${sctk_dir}/scutils/scoreFS02ASR.py
export temp_path=${sctk_dir}/egs/.temp
