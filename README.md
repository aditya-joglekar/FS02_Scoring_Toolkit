# Fearless Steps Challenge Phase-02 Scoring Toolkit (FS02-Sctk)
Scoring Toolkit for the Fearless Steps Challenge Phase-02

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

* [Overview](#overview)
  * [Credits](#credits)
  * [FS02 Scoring Metrics](#metrics)
	* [Requirements](#requirements)
	* [Folder Structure](#folder-structure)
	* [Usage](#usage)
	* [Author](#author)
	* [References](#references)
  * [License](#license)
	* [Acknowledgements](#acknowledgements)

<!-- /code_chunk_output -->
## Overview
This software was developed at the University of Texas at Dallas, Center for Robust Speech Systems (UTD-CRSS). It serves as a wrapper around multiple third-party open-source code listed below. (See [Credits](#credits)).
This toolkit intends to provide a simple scoring mechanism streamlined for FS02 Challenge usage for all tasks mentioned in [FS02 Scoring Metrics](#metrics). For more details, please see the [FS02 Challenge Website](https://fearless-steps.github.io/ChallengePhase2/)

### FS02 Scoring Metrics

The scoring metrics for FS02 Challenge per Task are:
  1. Speech Activity Detection (SAD):                   Detection Cost Function (DCF)

  2. Speaker Identification (SID):                      Top-5 Accuracy (% Top-5 Acc.)

  3. Speaker Diarization (SD):                          Diarization Error Rate (% DER)
      a. Track 1: SD using system SAD     (SD_track1)
      b. Track 2: SD using reference SAD  (SD_track2)

  4. Automatic Speech Recognition (ASR):                Word Error Rate (% WER)
      a. Track 1: Continuous stream ASR       (ASR_track1) 
      b. Track 2: ASR using Diarized Segments (ASR_track2) 


## Requirements
* Linux (not tested on Windows)
* Python >= 3.6 (3.7 recommended: Tested with Python 3.6.X, and 3.7.X.)
* Kaldi [Kaldi Installation](http://kaldi-asr.org/doc/install.html) (*Required for ASR evaluation)
* intervaltree>=3.0.0     (see requirements.txt)
* numpy>=1.16.2           (see requirements.txt)
* scipy>=0.17.0           (see requirements.txt)
* tabulate>=0.5.0         (see requirements.txt)
* sortedcontainers==2.1.0 (see requirements.txt)

## Credits
This toolkit makes use of three open source software:

[KALDI](http://kaldi-asr.org): The ASR python script uses compute-wer tool from the Kaldi Speech Recognition Toolkit. 
for more info, refer: [Kaldi Tools](http://kaldi-asr.org/doc/tools.html).
If you have used the toolkits' ASR scripts, please consider citing the following reference:

 .. [1] Povey, Daniel, Arnab Ghoshal, Gilles Boulianne, Lukas Burget, Ondrej Glembek, Nagendra Goel, Mirko Hannemann et al. *"The Kaldi speech recognition toolkit."* In IEEE 2011 workshop on automatic speech recognition and understanding, no. CONF. IEEE Signal Processing Society, 2011. [`PDF <https://infoscience.epfl.ch/record/192584/files/Povey_ASRU2011_2011.pdf>`_]

[DSCORE](https://github.com/nryant/dscore): DIARIZATION  -  DER   - (https://github.com/nryant/dscore)
[NIST openSAT]  - SAD          -  DCF   - (https://www.nist.gov/itl/iad/mig/nist-open-speech-activity-detection-evaluation)



## Folder Structure
```
    ./FS02_Scoring_Toolkit
  ├── egs
  │   ├── ref_gt
  │   │   ├── ASR
  │   │   │   ├── ASR_track1
  │   │   │   └── ASR_track2
  │   │   │       └── FS01_ASR_track2_transcriptions_Dev
  │   │   ├── SAD
  │   │   ├── SD
  │   │   │   ├── RTTM
  │   │   │   └── UEM
  │   │   └── SID
  │   │       └── FS01_SID_uttID2spkID_Dev.txt
  │   └── sys_results
  │       ├── ASR
  │       │   ├── ASR_track1
  │       │   └── ASR_track2
  │       │       └── FS01_ASR_track2_transcriptions_Dev
  │       ├── SAD
  │       ├── SD
  │       └── SID
  │           └── FS01_SID_uttID2spkID_Dev.txt
  ├── LICENSE
  ├── README.md
  ├── requirements.txt
  ├── scripts
  │   ├── cfg_path.sh
  │   ├── scoreFS02_ASR.sh
  │   ├── scoreFS02_SAD.sh
  │   ├── scoreFS02_SD.sh
  │   └── scoreFS02_SID.sh
  ├── scutils
  │   ├── dscore
  │   │   ├── LICENSE
  │   │   ├── scorelib
  │   │   ├── score.py
  │   │   └── validate_rttm.py
  │   ├── fs02utils.py
  │   ├── scoreFile_SAD.pl
  │   ├── scoreFS02ASR.py
  │   ├── scoreFS02SAD.py
  │   ├── scoreFS02SD.py
  │   └── scoreFS02SID.py
  └── submission_packet
      ├── crss@utdallas.edu_ASR_track2_Submission_1
      │   ├── Dev
      │   │   └── Dev_Readme
      │   ├── Eval
      │   │   └── Eval_Readme
      │   └── FS02_System_Description_eg.pdf
      ├── crss@utdallas.edu_ASR_track2_Submission_1.tar.gz
      └── Evaluation_and_Submission_Rules.txt
```

## Usage
The 

## Author
  * Aditya Joglekar, CRSS, UT-Dallas
  
  please contact FearlessSteps@utdallas.edu, if you have any question regarding this repository.

## License
This toolkit is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. See  LICENSE for more details

## Acknowledgements
This project was supported in part by  AFRL  under  contractFA8750-15-1-0205, NSF-CISE Project 1219130, and partially by the University of Texas at Dallas from the Distinguished University Chair in Telecommunications Engineering held by J.H. L. Hansen. We would also like to thank Tatiana Korelsky and the National Science Foundation (NSF) for their support on this scientific and historical project.
