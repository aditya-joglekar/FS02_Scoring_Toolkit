#!/usr/bin/perl

#############################################################################
# Revision history
# v1.0 (September 2, 2015)
#    - Greg Sanders
# v2.0 (October 1, 2015)   Fixed errors.
#    - Greg Sanders
# v2.1 (October 9, 2015)   Return 0 rather than NaN
#    - Greg Sanders          when a file is all speech or all non-speech
# v2.2 (October 15, 2015)  Eliminate incorrect output of collars at the
#    - Greg Sanders          very end of the file when last seg is non-speech
# v3.0 (October 29, 2015   Final scoring code: generating .csv output
#    - Greg Sanders
# v4.0 (December 01, 2015  Added handling of nonScorable ref segments
#    - Greg Sanders         (they result from last year's RATS adjudication)
# v5.0 (January 22, 2016  Added handling of Uncertain and Mixed ref segments
#    - Greg Sanders         (from this year's adjudication by Leidos)
#
#    Developed using Perl v5.16.3
#
#############################################################################
# This software was developed at the National Institute of Standards and Technology by
# employees and/or contractors of the Federal Government in the course of their official duties.
# Pursuant to Title 17 Section 105 of the United States Code this software is not subject to
# copyright protection within the United States and is in the public domain.
#
# NIST assumes no responsibility whatsoever for its use by any party, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other characteristic.
# We would appreciate acknowledgement if the software is used.  This software can be
# redistributed and/or modified freely provided that any derivative works bear some notice
# that they are derived from it, and any modified versions bear some notice that they
# have been modified.
#
# THIS SOFTWARE IS PROVIDED "AS IS."  With regard to this software, NIST MAKES NO EXPRESS
# OR IMPLIED WARRANTY AS TO ANY MATTER WHATSOEVER, INCLUDING MERCHANTABILITY,
# OR FITNESS FOR A PARTICULAR PURPOSE.
#############################################################################

use strict;

use Getopt::Std;

use vars qw($opt_a $opt_b $opt_e $opt_f $opt_g $opt_h $opt_n $opt_o $opt_p $opt_r $opt_s $opt_t $opt_u $opt_v);
getopts ('a:b:e:f:g:h:n:o:p:r:s:t:u:v');

# opt_r is the path to the ref file (the input annotation)
# opt_o is the path to the .csv output file of results

# opt_p is the participant team ID (from scoreDataset_SAD.pl)
my $participantID = $opt_p;

# opt_a is the testSetID (from the test definition .xml file)
my $testSetID = $opt_a;

# opt_b is the testID (from the test definition .xml file)
my $testID = $opt_b;

# opt_s is the zero-based column of start times for the ref 
# opt_e is the zero-based column of end times for the ref
                          
# opt_g is the zero-based column of interval-type for the ref (S, NS, NT, RI, RS, RX)   # could include "uncertain" if annotation supported that
                       ## Note: RX is a "button off" interval, so effectively NS
                       ##       RS was adjudicated as NS
                       ##       RI was adjudicated as unintelligible speech
                       ##       NT was automatically determined to be "no transmission"

# opt_h is the path to the hyp file (the system output)
# opt_n is the base hyp filename, without path, and goes in the output lines

# opt_t is the zero-based column of start times for the hyp
# opt_f is the zero-based column of end times for the hyp
# opt_u is the zero-based column of interval-type for the hyp (speech or non-speech)

# opt_v is a boolean flag -- it triggers voluminous/verbose output to STDERR

die "Hyp file not defined\n" if not defined($opt_h); 
die "Ref file not defined\n" if not defined($opt_r); 

die "Ref interval-type field not defined\n" if not defined($opt_g);
die "Hyp interval-type field not defined\n" if not defined($opt_u);

die "Ref interval-start field not defined\n" if not defined($opt_s);
die "Hyp interval-start field not defined\n" if not defined($opt_t);

die "Ref interval-end field not defined\n" if not defined($opt_e);
die "Hyp interval-end field not defined\n" if not defined($opt_f);

my $refFilePath = $opt_r;
open REF_FILE, "<$refFilePath" or die "Cannot open ref file $refFilePath\n";

my $hypFilePath = $opt_h;
open HYP_FILE, "<$hypFilePath" or die "Cannot open hyp file $hypFilePath\n";

my $outputFilePath = $opt_o;
open OUTPUT_FILE, ">>", "$outputFilePath" or die "Cannot open output .csv file $outputFilePath\n";

my @scorableSegs_noCollar = ();     # with no collars around the speech segs
my @scorableSegs_quarterSec = ();   # 1/4 second collars
my @scorableSegs_halfSec = ();      # 1/2 second collars
my @scorableSegs_oneSec = ();       # one second collars
my @scorableSegs_twoSecs = ();      # two seconds collars

my @hypSegs = ();    # always with no collars (collars pertain to the ref)

my $currRefTime = 0.0;  # where we are in the ref file (end prev seg, with no collar)
my $prevIntervalType = "";


#### - - - - - - - - - - - -
# We begin by inhaling the ref file, converting it to our data-structure with no collars.
while (<REF_FILE>) {
    chomp; chomp;
    my @fields = split /\t/;
  
    if (($fields[$opt_s] > $currRefTime) and ($currRefTime == 0.0)) { 
        # # The ref file does not begin at 0.0 so we exnihilate an initial non-speech segment
        # # In this case, there is not going to be a preceding NonSpeech segment to splice into
        # push @scorableSegs_noCollar, [0.0, $fields[$opt_s], "NonSpeech"];
        # $prevIntervalType = "NonSpeech";
        # $currRefTime = $fields[$opt_s];

        # The ref file does not begin at 0.0 so we exnihilate an initial collar segment
        # In this case, there is not going to be a preceding NonSpeech segment to splice into
        push @scorableSegs_noCollar, [0.0, $fields[$opt_s], "Collar"];
        $currRefTime = $fields[$opt_s];
    }
       
    if (($fields[$opt_s] > $currRefTime) and ($currRefTime > 0.0)) { 
        die "Error in ref file at un-annotated time interval from $currRefTime to $fields[$opt_s]\n";
    } elsif (($fields[$opt_g] eq "NS") or ($fields[$opt_g] eq "NT") or ($fields[$opt_g] eq "RX") or ($fields[$opt_g] eq "RS")) {
        if (($prevIntervalType eq "NonSpeech") and ($currRefTime > 0.0)) {    # There is a preceding NonSpeech segment to splice into
            my @prev = pop @scorableSegs_noCollar;
            $fields[$opt_s] = $prev[0][0];   # splice these NonSpeech segments
        }
        push @scorableSegs_noCollar, [$fields[$opt_s], $fields[$opt_e], "NonSpeech"];
        $prevIntervalType = "NonSpeech";
        $currRefTime = $fields[$opt_e];
    } elsif ((($fields[$opt_g] eq "S") or ($fields[$opt_g] eq "RI")) and ($fields[$opt_s] == $currRefTime)) {
        # I am treating RI as S, because I think such segments would be S in the Eval Dataset.
        # In theory, I think the RI segments should be non-scored time, but the Eval Dataset annotation doesn't support that distinction.
        if (($prevIntervalType eq "Speech") and ($currRefTime > 0.0)) {    # There is a preceding Speech segment to splice into
            my @prev = pop @scorableSegs_noCollar;
            $fields[$opt_s] = $prev[0][0];   # splice these speech segments
        }
        push @scorableSegs_noCollar, [$fields[$opt_s], $fields[$opt_e], "Speech"];
        $prevIntervalType = "Speech";
        $currRefTime = $fields[$opt_e];
    } elsif ((($fields[$opt_g] eq "nonScorable") or ($fields[$opt_g] eq "Mixed") or ($fields[$opt_g] eq "Uncertain")) and ($fields[$opt_s] == $currRefTime)) {
        # This is a segment that was adjudicated as nonScorable, a mix of speech and nonSpeech, or adjudicator was uncertain
        push @scorableSegs_noCollar, [$fields[$opt_s], $fields[$opt_e], "Collar"];   # Yeah, I know, the name "scorableSegs" does not match this
        $currRefTime = $fields[$opt_e];
    } else {  #overlapping ref segs or unexpected value at $fields[$opt_g]
        if (($fields[$opt_g] ne "S") and ($fields[$opt_g] ne "NS") and ($fields[$opt_g] ne "NT") and ($fields[$opt_g] ne "RX") and ($fields[$opt_g] ne "RS") and ($fields[$opt_g] ne "RI")) {
            die "Error: Unexpected segment type $fields[$opt_g]   (which is not S, NS, NT, RX, RS, or RI)\n";
        } else {
            die "Error: overlapping ref segs, with end prev seg at $currRefTime and begin new seg at $fields[$opt_s]\n";
        }
    }
    # If we knew the end time of the file and the file ends with a nonspeech segment,
    # we could here output that nonspeech segment.
}
## Now we have inhaled the ref file

## If the ref begins with a nonSpeech seg, deal with that.
if ($scorableSegs_noCollar[0][2] eq "Collar") {
    ## The ref starts with a Collar, which gets output unchanged for all collar sizes
    ## The actual situation is that the ref did not start at time 0.0
    my $end = $scorableSegs_noCollar[0][1];

    push @scorableSegs_twoSecs, [0.0, $end, "Collar"];
    push @scorableSegs_oneSec, [0.0, $end, "Collar"];
    push @scorableSegs_halfSec, [0.0, $end, "Collar"];
    push @scorableSegs_quarterSec, [0.0, $end, "Collar"];

} elsif ($scorableSegs_noCollar[0][2] eq "NonSpeech") {
    my $start = $scorableSegs_noCollar[0][0];
    my $end = $scorableSegs_noCollar[0][1];
    my $dur = $end - $start;

    if ($start != 0.0) {
        die "Unexpected ref start time > 0.0: (start $scorableSegs_noCollar[0][0] : end $scorableSegs_noCollar[0][1] : type $scorableSegs_noCollar[0][2])\n"; 
    }

    ## In the case of collars, start the collars at zero if the resulting preceding NonSpeech segment will not
    ## last for at least 0.1 seconds
    if ($dur >= 0.35) {
        if ($dur > 0.25) {
            push @scorableSegs_quarterSec, [$start, $end - 0.25, "NonSpeech"];
        }
        push @scorableSegs_quarterSec, [$end - 0.25, $end, "Collar"];    # collar preceding a speech region

        if ($dur >= 0.6) {
            if ($dur > 0.5) {
                push @scorableSegs_halfSec, [$start, $end - 0.5, "NonSpeech"];
            }
            push @scorableSegs_halfSec, [$end - 0.5, $end, "Collar"];    # collar preceding a speech region

            if ($dur >= 1.1) {
                if ($dur > 1.0) {
                    push @scorableSegs_oneSec, [$start, $end - 1.0, "NonSpeech"];
                }
                push @scorableSegs_oneSec, [$end - 1.0, $end, "Collar"];    # collar preceding a speech region

                if ($dur >= 2.1) {
                    if ($dur > 2.0) {
                        push @scorableSegs_twoSecs, [$start, $end - 2.0, "NonSpeech"];
                    }
                    push @scorableSegs_twoSecs, [$end - 2.0, $end, "Collar"];    # collar preceding a speech region
                } else {
                    push @scorableSegs_twoSecs, [$start, $end, "Collar"];        # collar preceding a speech region
                }
            } else {
                push @scorableSegs_oneSec, [$start, $end, "Collar"];        # collar preceding a speech region
                push @scorableSegs_twoSecs, [$start, $end, "Collar"];       # collar preceding a speech region
            }
        } else {
            push @scorableSegs_halfSec, [$start, $end, "Collar"];       # collar preceding a speech region
            push @scorableSegs_oneSec, [$start, $end, "Collar"];        # collar preceding a speech region
            push @scorableSegs_twoSecs, [$start, $end, "Collar"];       # collar preceding a speech region
        }
    } else {
        push @scorableSegs_quarterSec, [$start, $end, "Collar"];    # collar preceding a speech region
        push @scorableSegs_halfSec, [$start, $end, "Collar"];       # collar preceding a speech region
        push @scorableSegs_oneSec, [$start, $end, "Collar"];        # collar preceding a speech region
        push @scorableSegs_twoSecs, [$start, $end, "Collar"];       # collar preceding a speech region
    }
} else {
    ## the ref starts with a speech seg, which gets output unchanged for all collar sizes
    my $end = $scorableSegs_noCollar[0][1];

    push @scorableSegs_twoSecs, [0.0, $end, "Speech"];
    push @scorableSegs_oneSec, [0.0, $end, "Speech"];
    push @scorableSegs_halfSec, [0.0, $end, "Speech"];
    push @scorableSegs_quarterSec, [0.0, $end, "Speech"];
}

#### - - - - - - - - - - - -
## Now we need to populate reference data-structures for the various collar size.
##
## We have already processed scorableSegs_noCollar[0].
## Sweep through the rest of scorableSegs_noCollar, and generate versions for various collar sizes
## Note that "normal" collars come out of nonSpeech segs, and we output the Speech segs unchanged.
## But note also:  time that is notScorable due to adjudication will be "Collar" in scorableSegs_noCollar.
for (my $xx = 1; $xx < scalar(@scorableSegs_noCollar); $xx += 1) {
    my $start = $scorableSegs_noCollar[$xx][0];
    my $end = $scorableSegs_noCollar[$xx][1];
    my $dur = $end - $start;
    my $segType = $scorableSegs_noCollar[$xx][2];

    if ($segType eq "Speech") {
        push @scorableSegs_twoSecs, [$start, $end, "Speech"];
        push @scorableSegs_oneSec, [$start, $end, "Speech"];
        push @scorableSegs_halfSec, [$start, $end, "Speech"];
        push @scorableSegs_quarterSec, [$start, $end, "Speech"];
    } elsif ($segType eq "Collar") {
        push @scorableSegs_twoSecs, [$start, $end, "Collar"];
        push @scorableSegs_oneSec, [$start, $end, "Collar"];
        push @scorableSegs_halfSec, [$start, $end, "Collar"];
        push @scorableSegs_quarterSec, [$start, $end, "Collar"];
    } else {   ## Note: $segType has to be "NonSpeech" and there must be an immediately preceding "Speech" segment
               ##       or beginning of file
        ## In the case of collars, merge the collars if the resulting intervening NonSpeech segment will not
        ## last for at least 0.1 seconds
        if (($dur >= 4.1) and ($xx < (scalar(@scorableSegs_noCollar)-1))) {
            push @scorableSegs_twoSecs, [$start, $start+2.0, "Collar"];      # collar following a speech region
            push @scorableSegs_twoSecs, [$start+2.0, $end-2.0, "NonSpeech"];
            push @scorableSegs_twoSecs, [$end-2.0, $end, "Collar"];          # collar preceding a speech region

            push @scorableSegs_oneSec, [$start, $start+1.0, "Collar"];       # collar following a speech region
            push @scorableSegs_oneSec, [$start+1.0, $end-1.0, "NonSpeech"];
            push @scorableSegs_oneSec, [$end-1.0, $end, "Collar"];           # collar preceding a speech region

            push @scorableSegs_halfSec, [$start, $start+0.5, "Collar"];      # collar following a speech region
            push @scorableSegs_halfSec, [$start+0.5, $end-0.5, "NonSpeech"];
            push @scorableSegs_halfSec, [$end-0.5, $end, "Collar"];          # collar preceding a speech region

            push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];      # collar following a speech region
            push @scorableSegs_quarterSec, [$start+0.25, $end-0.25, "NonSpeech"];
            push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];          # collar preceding a speech region
        } elsif (($dur >= 2.1) and ($xx == (scalar(@scorableSegs_noCollar)-1))) {
            push @scorableSegs_twoSecs, [$start, $start+2.0, "Collar"];      # collar following a speech region
            push @scorableSegs_twoSecs, [$start+2.0, $end, "NonSpeech"];
            #push @scorableSegs_twoSecs, [$end-2.0, $end, "Collar"];           # collar preceding a speech region

            push @scorableSegs_oneSec, [$start, $start+1.0, "Collar"];       # collar following a speech region
            push @scorableSegs_oneSec, [$start+1.0, $end, "NonSpeech"];
            #push @scorableSegs_oneSec, [$end-1.0, $end, "Collar"];           # collar preceding a speech region

            push @scorableSegs_halfSec, [$start, $start+0.5, "Collar"];      # collar following a speech region
            push @scorableSegs_halfSec, [$start+0.5, $end, "NonSpeech"];
            #push @scorableSegs_halfSec, [$end-0.5, $end, "Collar"];          # collar preceding a speech region

            push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];      # collar following a speech region
            push @scorableSegs_quarterSec, [$start+0.25, $end, "NonSpeech"];
            #push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];          # collar preceding a speech region
        } else {
            push @scorableSegs_twoSecs, [$start, $end, "Collar"];            # merged collar

            if (($dur >= 2.1) and ($xx < (scalar(@scorableSegs_noCollar)-1))) {
                push @scorableSegs_oneSec, [$start, $start+1.0, "Collar"];      # collar following a speech region
                push @scorableSegs_oneSec, [$start+1.0, $end-1.0, "NonSpeech"];
                push @scorableSegs_oneSec, [$end-1.0, $end, "Collar"];          # collar preceding a speech region

                push @scorableSegs_halfSec, [$start, $start+0.5, "Collar"];      # collar following a speech region
                push @scorableSegs_halfSec, [$start+0.5, $end-0.5, "NonSpeech"];
                push @scorableSegs_halfSec, [$end-0.5, $end, "Collar"];          # collar preceding a speech region

                push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];      # collar following a speech region
                push @scorableSegs_quarterSec, [$start+0.25, $end-0.25, "NonSpeech"];
                push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];          # collar preceding a speech region
            } elsif (($dur >= 1.1) and ($xx == (scalar(@scorableSegs_noCollar)-1))) {
                push @scorableSegs_oneSec, [$start, $start+1.0, "Collar"];      # collar following a speech region
                push @scorableSegs_oneSec, [$start+1.0, $end, "NonSpeech"];
               # push @scorableSegs_oneSec, [$end-1.0, $end, "Collar"];          # collar preceding a speech region

                push @scorableSegs_halfSec, [$start, $start+0.5, "Collar"];      # collar following a speech region
                push @scorableSegs_halfSec, [$start+0.5, $end, "NonSpeech"];
               # push @scorableSegs_halfSec, [$end-0.5, $end, "Collar"];          # collar preceding a speech region

                push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];      # collar following a speech region
                push @scorableSegs_quarterSec, [$start+0.25, $end, "NonSpeech"];
               # push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];          # collar preceding a speech region
            } else {
                push @scorableSegs_oneSec, [$start, $end, "Collar"];            # merged collar

                if (($dur >= 1.1) and ($xx < (scalar(@scorableSegs_noCollar)-1))) {
                    push @scorableSegs_halfSec, [$start, $start+0.5, "Collar"];      # collar following a speech region
                    push @scorableSegs_halfSec, [$start+0.5, $end-0.5, "NonSpeech"];
                    push @scorableSegs_halfSec, [$end-0.5, $end, "Collar"];          # collar preceding a speech region

                    push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];      # collar following a speech region
                    push @scorableSegs_quarterSec, [$start+0.25, $end-0.25, "NonSpeech"];
                    push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];          # collar preceding a speech region
                } elsif (($dur >= 0.6) and ($xx == (scalar(@scorableSegs_noCollar)-1))) {
                    push @scorableSegs_halfSec, [$start, $start+0.5, "Collar"];      # collar following a speech region
                    push @scorableSegs_halfSec, [$start+0.5, $end, "NonSpeech"];
                   # push @scorableSegs_halfSec, [$end-0.5, $end, "Collar"];          # collar preceding a speech region

                    push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];      # collar following a speech region
                    push @scorableSegs_quarterSec, [$start+0.25, $end, "NonSpeech"];
                   # push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];          # collar preceding a speech region
                } else {
                    push @scorableSegs_halfSec, [$start, $end, "Collar"];            # merged collar

                    if (($dur >= 0.6) and ($xx < (scalar(@scorableSegs_noCollar)-1))) {
                        push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];       # collar following a speech region
                        push @scorableSegs_quarterSec, [$start+0.25, $end-0.25, "NonSpeech"];
                        push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];           # collar preceding a speech region
                    } elsif (($dur >= 0.35) and ($xx == (scalar(@scorableSegs_noCollar)-1))) {
                        push @scorableSegs_quarterSec, [$start, $start+0.25, "Collar"];       # collar following a speech region
                        push @scorableSegs_quarterSec, [$start+0.25, $end, "NonSpeech"];
                       # push @scorableSegs_quarterSec, [$end-0.25, $end, "Collar"];           # collar preceding a speech region
                    } else {
                        push @scorableSegs_quarterSec, [$start, $end, "Collar"];              # merged collar
                    }
                }
            }
        }
    } #x
}

#### - - - - - - - - - - - -
# Here we have debugging dumps of the reference data-structures.

if ( defined($opt_v) ) {
    print STDERR "\nBEGIN dumping reference data-structures\n\n";
    
    print "NO COLLAR\n";
    for (my $xx = 0; $xx < scalar(@scorableSegs_noCollar); $xx += 1) {
        print STDERR "\tnoCollar $xx: start $scorableSegs_noCollar[$xx][0] : end $scorableSegs_noCollar[$xx][1] : type $scorableSegs_noCollar[$xx][2]\n";
    }

    print "\nQUARTER COLLAR\n";
    for (my $xx = 0; $xx < scalar(@scorableSegs_quarterSec); $xx += 1) {
        print STDERR "\tquarterCollar $xx: start $scorableSegs_quarterSec[$xx][0] : end $scorableSegs_quarterSec[$xx][1] : type $scorableSegs_quarterSec[$xx][2]\n";
    }

    print "\nHALF COLLAR\n";
    for (my $xx = 0; $xx < scalar(@scorableSegs_halfSec); $xx += 1) {
        print STDERR "\thalfCollar $xx: start $scorableSegs_halfSec[$xx][0] : end $scorableSegs_halfSec[$xx][1] : type $scorableSegs_halfSec[$xx][2]\n";
    }

    print "\nONE COLLAR\n";
    for (my $xx = 0; $xx < scalar(@scorableSegs_oneSec); $xx += 1) {
        print STDERR "\toneCollar $xx: start $scorableSegs_oneSec[$xx][0] : end $scorableSegs_oneSec[$xx][1] : type $scorableSegs_oneSec[$xx][2]\n";
    }

    print "\nTWO COLLAR\n";
    for (my $xx = 0; $xx < scalar(@scorableSegs_twoSecs); $xx += 1) {
        print STDERR "\ttwoCollar $xx: start $scorableSegs_twoSecs[$xx][0] : end $scorableSegs_twoSecs[$xx][1] : type $scorableSegs_twoSecs[$xx][2]\n";
    }

    print STDERR "\nDONE dumping reference data-structures\n\n";
}


#### - - - - - - - - - - - -
# Much like we inhaled the reference file, inhale the system output (i.e., the hyp).
#
# Since we assume the reference actually covers the entire audio input, 
# there has to be some decision about system output (hyp) that starts earlier
# than the reference, or that ends later.  What we actually do here is
# to trim/truncate the system output in those cases.  Similarly, if
# the system output starts later than the ref or ends earlier, we pad out
# the system output with a NonSpeech segment.  Therefore, the system output
# ends up starting at the same time as the ref, and ending at the same time.
#
# I believe this is the correct way to score these.   -- Greg Sanders 

my $currHypTime = 0.0;
$prevIntervalType = "";
while (<HYP_FILE>) {
    chomp; chomp;
    my @fields = split /\t/;
  
    if (($fields[$opt_t] > $currHypTime) or ($fields[$opt_t] < $currHypTime)) {
        die "Error in hyp file at un-annotated time interval from $currHypTime to $fields[$opt_t]\n";
    } elsif (($fields[$opt_u] eq "non-speech") or ($fields[$opt_u] eq "nonspeech")) {   # Actually, sys output should have a hyphen 
        if (($prevIntervalType eq "NonSpeech") and ($currHypTime > 0.0)) {    # There is a preceding NonSpeech segment to splice into
            my @prev = pop @hypSegs;
            $fields[$opt_t] = $prev[0][0];   # splice these NonSpeech segments
        }
        push @hypSegs, [$fields[$opt_t], $fields[$opt_f], "NonSpeech"];
        $currHypTime = $fields[$opt_f];
        $prevIntervalType = "NonSpeech";
    } elsif ($fields[$opt_u] eq "speech") {
        if (($prevIntervalType eq "Speech") and ($currHypTime > 0.0)) {    # There is a preceding Speech segment to splice into
            my @prev = pop @hypSegs;
            $fields[$opt_t] = $prev[0][0];   # splice these Speech segments
        }
        push @hypSegs, [$fields[$opt_t], $fields[$opt_f], "Speech"];
        $currHypTime = $fields[$opt_f];
        $prevIntervalType = "Speech";
    } else {  #overlapping hyp segs
       die "Error: overlapping hyp segs, with end prev seg at $currHypTime and begin new seg at $fields[$opt_t] with type $fields[$opt_u]\n";
    }
    # If we knew the end time of the file and the file ends with a nonspeech segment,
    # we could here output that nonspeech segment.
}

## If the hyp begins with a nonSpeech seg, deal with that.
if ($hypSegs[0][2] eq "NonSpeech") {
    my $start = $hypSegs[0][0];
    my $end = $hypSegs[0][1];
    my $dur = $end - $start;

    if ($start != 0.0) {
        die "Unexpected start time > s $hypSegs[0][0] : e $hypSegs[0][1] : t $hypSegs[0][2]<\n"; 
    }
}

my $refStartTime = $scorableSegs_noCollar[0][0];                           # the hyp will be made to start at this time
my $refEndTime = $scorableSegs_noCollar[scalar(@scorableSegs_noCollar) - 1][1];  # hyp will be made to end at this time

if ($hypSegs[0][0] < $refStartTime) {
    while ($hypSegs[0][1] <= $refStartTime) {
        shift @hypSegs;
    }
}
# Now, the initial hyp seg should either start at refStartTime or else enclose refStartTime

if ($hypSegs[0][0] > $refStartTime) {
    if ($hypSegs[0][2] eq "NonSpeech") {
        $hypSegs[0][0] = $refStartTime;    # adjust hyp start time to match ref
    } else {   # $hypSegs[0][2] is "Speech" 
        my $existingHypStartTime = $hypSegs[0][0];
        unshift @hypSegs, [$refStartTime, $existingHypStartTime, "NonSpeech"];  # prepend appropriate NonSpeech seg
    }
}
# Now, the initial hyp seg should begin at refStartTime

if ($hypSegs[scalar(@hypSegs) - 1][1] > $refEndTime) {
    while ($hypSegs[scalar(@hypSegs) - 1][0] >= $refEndTime) {
        pop @hypSegs;   # discarding all hyp seg(s) that begin beyond refEndTime
    }
}
# Now, the final hyp seg should either end at refEndTime or else enclose it

# print "endHyp is: type $hypSegs[scalar(@hypSegs) - 1][2] : start $hypSegs[scalar(@hypSegs) - 1][0] : end $hypSegs[scalar(@hypSegs) - 1][1]\n";
if ($hypSegs[scalar(@hypSegs) - 1][1] > $refEndTime) {
    # Final hyp seg encloses refEndTime
    $hypSegs[scalar(@hypSegs) - 1][1] = $refEndTime;    # adjust hyp end time to match ref   (last idx changed from [0] to [1])
  #  if ($hypSegs[scalar(@hypSegs) - 1][2] eq "NonSpeech") {
  #       $hypSegs[scalar(@hypSegs) - 1][1] = $refEndTime;    # adjust hyp end time to match ref   (last idx changed from [0] to [1])
  #   } else {   # $hypSegs[scalar(@hypSegs) - 1][2] is "Speech"
  #       my $existingHypEndTime = $hypSegs[scalar(@hypSegs) - 1][1];
  #       push @hypSegs, [$existingHypEndTime, $refEndTime, "NonSpeech"];   # append appropriate NonSpeech seg
  #   }
}
# Now, the final hyp seg should end at refEndTime if hyp previously ended later

# However, it's still possible that the hyp (incorrectly) ends before the ref ends.
# If so, fix that by adding a non-speech hyp seg through the end of the ref.
if ($hypSegs[scalar(@hypSegs) - 1][1] < $refEndTime) {
    push @hypSegs, [$hypSegs[scalar(@hypSegs)-1][1], $refEndTime, "NonSpeech"];   # append appropriate NonSpeech seg
}

## Dump the hyp
if ( defined($opt_v) ) {
    print "\nHYP SEGS:\n";
    for (my $xx = 0; $xx < scalar(@hypSegs); $xx += 1) {
        print STDERR "\tstart $hypSegs[$xx][0] : end $hypSegs[$xx][1] : type $hypSegs[$xx][2]\n";
    }
    print STDERR "end of HYP SEGS\n\n";
}


### Print identifying info as header for the output
print "\nHyp file:  $opt_h\nRef file:  $opt_r\n";


#### - - - - - - - - - - - -
# For each collar size, call subroutine to compute scores
computeAndPrintScores(\@scorableSegs_noCollar, \@hypSegs, 0.0, "No Collar");
computeAndPrintScores(\@scorableSegs_quarterSec, \@hypSegs, 0.25, "QuarterSecond Collar");
computeAndPrintScores(\@scorableSegs_halfSec, \@hypSegs, 0.5, "HalfSecond Collar");
computeAndPrintScores(\@scorableSegs_oneSec, \@hypSegs, 1.0, "OneSecond Collar");
computeAndPrintScores(\@scorableSegs_twoSecs, \@hypSegs, 2.0, "TwoSecond Collar");
print "\n";


#### - - - - - - - - - - - -
# Next, compute the sums that are the inputs to the Miss Rate and the False Alarm Rate for this collarSize,
#       and then compute and print the Miss Rate and False Alarm Rate (also DCF as in eval plan).
sub computeAndPrintScores {
    my ($currSetOfRefSegs, $currSetOfHypSegs, $collarLen, $collarSize) = @_;   # The passed arguments
             # collarLen is numeric,  collarSize is descriptive string

    my $speechTimeSum = 0.0;     # total Speech time
    
    my $truePositiveSum = 0.0;
    my $falseNegativeSum = 0.0;

    my $nonSpeechTimeSum = 0.0;    # total scored NonSpeech time
    
    my $trueNegativeSum = 0.0;
    
    my $falsePositiveSum = 0.0;
    
    ## Note: The ref segs are all contiguous (i.e., they cover the ref time)
    ##       and likewise the hyp segs are all contiguous.
    
    ## Advancing the currScoringTime marks out the time interval
     # . . . that is currently being scored,
     # . . . extending from prevScoringTime through currScoringTime,
     # . . . (which will be scored as defined by currRefState and currHypState)
    my $prevScoringTime = 0.0;
    my $currScoringTime = 0.0;
    my $currRefState = "undefined";
    my $currHypState = "undefined";  
    
    ## We will score up through the last endTime that occurs in ref
    my $endScoredTime = $$currSetOfRefSegs[scalar(@$currSetOfRefSegs)-1][1];

    my $hypIdx = 0;
    my $maxHypIdx = scalar(@$currSetOfHypSegs) - 1;
    
    my $refIdx = 0;
    my $maxRefIdx = scalar(@$currSetOfRefSegs) - 1;
    
    while($currScoringTime < $endScoredTime) {
       # Each time through this loop, there are four seg boundaries to consider:
       # (1) start of ref seg
       # (2) end of ref seg 
       # (3) start of hyp seg
       # (4) end of hyp seg
       # Number 2 is always greater than 1, and likewise 4 greater than 3,
       # . . . but we don't know anything about the existing ordering of 1 vs 3 or 4,
       # . . . nor anything about the existing order of 2 vs 3 or 4.
       # We have already scored all time up through currScoringTime.
       # Because the segs are contiguous, the hyp seg and/or ref seg already begins at currScoringTime.
       # Similarly, the end of the interval to be scored is whichever of the four seg boundaries
       # . . . exceeds currScoringTime by the least.
    
        $prevScoringTime = $currScoringTime;
       # The following if/elsif/else will always advance currScoringTime.
       # It should also set currHypState and currRefState correctly.
        if ($$currSetOfHypSegs[$hypIdx][0] < $$currSetOfRefSegs[$refIdx][0]) {
            # start time of hyp seg is not later than start time of ref seg or end time of ref seg
            $currScoringTime == $$currSetOfRefSegs[$refIdx][0];
            $currRefState = $$currSetOfRefSegs[$refIdx][2];
    
            # The end of the interval to be scored is the end of hyp seg or of ref seg, whichever is less
            if ($$currSetOfHypSegs[$hypIdx][1] <= $$currSetOfRefSegs[$refIdx][1]) {
                $currScoringTime = $$currSetOfHypSegs[$hypIdx][1];
                $hypIdx += 1 if $hypIdx < $maxHypIdx;
            } else {
                $currScoringTime = $$currSetOfRefSegs[$refIdx][1];
                $refIdx += 1 if $refIdx < $maxRefIdx;
            }
        } elsif ($$currSetOfHypSegs[$hypIdx][0] > $$currSetOfRefSegs[$refIdx][0]) {
            # start of ref seg is not later than start of hyp seg or end of hyp seg
            $currScoringTime == $$currSetOfHypSegs[$hypIdx][0];
            $currHypState = $$currSetOfHypSegs[$hypIdx][2];
    
            # The end of the interval to be scored is the end of hyp seg or of ref seg, whichever is less
            if ($$currSetOfHypSegs[$hypIdx][1] <= $$currSetOfRefSegs[$refIdx][1]) {
                $currScoringTime = $$currSetOfHypSegs[$hypIdx][1];
                $hypIdx += 1 if $hypIdx < $maxHypIdx;
            } else {
                $currScoringTime = $$currSetOfRefSegs[$refIdx][1];
                $refIdx += 1 if $refIdx < $maxRefIdx;
            }
        } else {   # $$currSetOfHypSegs[$hypIdx][0] == $$currSetOfRefSegs[$refIdx][0], and both == currScoringTime
            $currRefState = $$currSetOfRefSegs[$refIdx][2];
            $currHypState = $$currSetOfHypSegs[$hypIdx][2];
            # The end of the interval to be scored is the end of hyp seg or of ref seg, whichever is less
            if ($$currSetOfHypSegs[$hypIdx][1] <= $$currSetOfRefSegs[$refIdx][1]) {
                $currScoringTime = $$currSetOfHypSegs[$hypIdx][1];
                $hypIdx += 1 if $hypIdx < $maxHypIdx;
            } else {
                $currScoringTime = $$currSetOfRefSegs[$refIdx][1];
                $refIdx += 1 if $refIdx < $maxRefIdx;
            }
        }

        # We are done with this time through the while loop if the ref segment is a collar.
        next if $currRefState eq "Collar";
    
        # If we get here, the ref seg must be Speech or NonSpeech
        my $segDur = $currScoringTime - $prevScoringTime;
        if ($currRefState eq "Speech") {
            $speechTimeSum += $segDur;
            if ($currHypState eq "Speech") {
                $truePositiveSum += $segDur;
if (defined($opt_v)) { printf "truePos    %6.3f to %6.3f (%6.3f)\n", $prevScoringTime, $currScoringTime, $segDur; }
            } elsif ($currHypState eq "NonSpeech") {
                $falseNegativeSum += $segDur;
if (defined($opt_v)) { printf "miss       %6.3f to %6.3f (%6.3f)\n", $prevScoringTime, $currScoringTime, $segDur; }
            } else {
                print "***** $currScoringTime $prevScoringTime Error1: currRefState $currRefState and currHypState $currHypState ******* \n";
            } 
        } elsif ($currRefState eq "NonSpeech") {
            $nonSpeechTimeSum += $segDur;
            if ($currHypState eq "NonSpeech") {
                $trueNegativeSum += $segDur;
if (defined($opt_v)) { printf "trueNeg    %6.3f to %6.3f (%6.3f)\n", $prevScoringTime, $currScoringTime, $segDur; }
            } elsif ($currHypState eq "Speech") {
                $falsePositiveSum += $segDur;
if (defined($opt_v)) { printf "falseAlarm %6.3f to %6.3f (%6.3f)\n", $prevScoringTime, $currScoringTime, $segDur; }
            } else {
                print "***** Error2: currRefState $currRefState and currHypState $currHypState ******* \n";
            } 
        } else {
            print "***** Error3: currRefState \"$currRefState\" and currHypState \"$currHypState\" (currScoringTime $currScoringTime : prevScoringTime $prevScoringTime : endScoredTime $endScoredTime : refIdx $refIdx : maxRefIdx $maxRefIdx : hypIdx $hypIdx : maxHypIdx $maxHypIdx : collarSize $collarSize) ******* \n";
        }
    }
    
    
    #### - - - - - - - - - - - -
    # Compute and print the official scores for this combination of hyp and ref, for this collarSize

    my $saved_speechTimeSum = $speechTimeSum;
    my $saved_nonSpeechTimeSum = $nonSpeechTimeSum;
    print "\n    Scores with $collarSize\n";
    
    if ($speechTimeSum < 0.00001) {   # That is, actually 0.0
        $speechTimeSum = 1;   # Note that $falseNegativeSum must be zero in this case

        if ($falseNegativeSum != 0) {
            printf "\n***** Error4: speechTimeSum == 0 but falseNegativeSum != 0 *****\n\n";
        }
    }
    printf "\t      Prob_Miss == %7.5f   (%7.3f / %7.3f)\n",
                             $falseNegativeSum / $speechTimeSum,  $falseNegativeSum,  $speechTimeSum;

    if ($nonSpeechTimeSum < 0.00001) {   # That is, actually 0.0
        $nonSpeechTimeSum = 1;   # Note that $falsePositiveSum must be zero in this case

        if ($falsePositiveSum != 0) {
            printf "\n***** Error5: nonSpeechTimeSum == 0 but falsePositiveSum != 0 *****\n\n";
        }
    }
    printf "\tProb_FalseAlarm == %7.5f   (%7.3f / %7.3f)\n\n",
                             $falsePositiveSum / $nonSpeechTimeSum,  $falsePositiveSum,  $nonSpeechTimeSum;

   my $team;
   my $submission;
   my $clusterNum;
   ($team, $submission, $clusterNum) = split(/_/, $participantID);

   ## Calculate and print DCF 
   ##    Note: OUTPUT_FILE row is "collarLen,DCF,Prob_Miss,Prob_FA,falseNegativeSum,falsePositiveSum,trueNegativeSum,truePositiveSum,speechTimeSum,nonSpeechTimeSum,participantID,team,submission,clusterNum,testSetID,testID,fileID\n"

    $speechTimeSum = $saved_speechTimeSum;
    $nonSpeechTimeSum = $saved_nonSpeechTimeSum;
    if (($speechTimeSum < 0.00001) and ($nonSpeechTimeSum < 0.00001)) {   # Both are actually 0.0
        printf "\t            DCF == 0.00000\n";
        printf OUTPUT_FILE "%4.2f,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,$participantID,$team,$submission,%d,$testSetID,$testID,$opt_n\n", $collarLen, $clusterNum;
    } elsif ($speechTimeSum < 0.00001) {   # That is, actually 0.0
        my $DCF =  (0.25*($falsePositiveSum/$nonSpeechTimeSum));

        printf "\t            DCF == %7.5f   ((0.75 * 0.000) + (0.25 * %7.5f))\n",
                                      $DCF,                            $falsePositiveSum/$nonSpeechTimeSum;

        printf OUTPUT_FILE "%4.2f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,$participantID,$team,$submission,%d,$testSetID,$testID,$opt_n\n", $collarLen, $DCF, 0.0, $falsePositiveSum/$nonSpeechTimeSum, 0.0, $falsePositiveSum, $trueNegativeSum, 0.0, 0.0, $nonSpeechTimeSum, $clusterNum;

        printf "\t            DCF == %7.5f   ((0.75 * 0.000) + (0.25 * %7.5f))\n",
                                     (0.25*($falsePositiveSum/$nonSpeechTimeSum)),
                                                                      $falsePositiveSum/$nonSpeechTimeSum;
    } elsif ($nonSpeechTimeSum < 0.00001) {   # That is, actually 0.0
        my $DCF = (0.75*($falseNegativeSum/$speechTimeSum));

        printf "\t            DCF == %7.5f   ((0.75 * %7.5f) + (0.25 * 0.000))\n", 
                                     $DCF,            $falseNegativeSum/$speechTimeSum;

        printf OUTPUT_FILE "%4.2f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,$participantID,$team,$submission,%d,$testSetID,$testID,$opt_n\n", $collarLen, $DCF, $falseNegativeSum/$speechTimeSum, 0.0, $falseNegativeSum, 0.0, 0.0, $truePositiveSum,$speechTimeSum, 0.0, $clusterNum;
    } else {
        my $DCF = (0.75*($falseNegativeSum/$speechTimeSum)) + (0.25*($falsePositiveSum/$nonSpeechTimeSum));

        printf "\t            DCF == %7.5f   ((0.75 * %7.5f) + (0.25 * %7.5f))\n",
                                     $DCF,            $falseNegativeSum/$speechTimeSum,
                                                                       $falsePositiveSum/$nonSpeechTimeSum;

        printf OUTPUT_FILE "%4.2f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,%7.5f,$participantID,$team,$submission,%d,$testSetID,$testID,$opt_n\n", $collarLen, $DCF, $falseNegativeSum/$speechTimeSum, $falsePositiveSum/$nonSpeechTimeSum, $falseNegativeSum, $falsePositiveSum, $trueNegativeSum, $truePositiveSum, $speechTimeSum, $nonSpeechTimeSum, $clusterNum;
    }
}

