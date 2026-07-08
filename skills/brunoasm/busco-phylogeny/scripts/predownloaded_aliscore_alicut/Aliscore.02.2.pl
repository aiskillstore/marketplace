#!/usr/bin/perl

#written by Bernhard Misof, ZFMK, Bonn
#version of 20th February 2012

#updated by Bernhard Misof, 4th March 2008
#updated by Bernhard Misof, 7th March 2008
#updated by Bernhard Misof,11th March 2008
#updated by Bernhard Misof,26th March 2008
#updated by Bernhard Misof, 2nd April 2008
#updated by Bernhard Misof, 6th May   2008
#updated by Bernhard Misof, 6th May   2008   => -e for nt sequences! -e for nt sequences disables N replacement for fuzzy ends of sequences!
#updated by Bernhard Misof, 20th February 2012 => svg output added 
#updated by Bernhard Misof, 21th February 2012 => RY input files possible 


#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  


use strict          ;
use warnings        ;
use Aliscore_module ;
use Tie::File       ;
use Fcntl           ;


#converts different line feeds in open process
use open IN => ":raw", OUT => ":raw" ;



=pod

=head1 Introduction

Aliscore is designed to filter alignment ambiguous or randomly similar sites in multiple sequence alignments (MSA). It does not generate a generic alignment, this must be provided by the user. Aliscore reads exclusively alignments in FASTA format independently of suffices (.fas .txt .fts etc.). Aliscore reads the alignment and generates a hash of these sequences with taxon names as keys and simple sequence arrays as values. It works on these hash elements and uses these hasj elements as the basic data. Aliscore tolerates newlines in sequences but not in taxon names. Sequences must be of similar length! Aliscore can not read sequences in interleaved format, but this does not correspond to a plain fasta file anyway. Blanks in sequences are ignored, any other sign in sequences except for these covered by the universal DNA/RNA code will chock the program. Ambiguities are understood, as are indels. Kapital or small letters are equally good as input and can be used interchangeably, RNA and DNA sequences can be used in one alignment, RNA sequences are translated into DNA sequences.
Aliscore works on WindowsPCs, Macs and Linux mashines, but was written on Linux. If input files are coming from Windows make sure CRFL feeds are removed. Aliscore tries to remove them, but my not succeed in every instance.
Taxon names must only include alphanumeric signs, underscores (_) and blanks, everything else might chock the program. Aliscore will issue an error prompt and die if any non-alphanumeric sign is encountered in taxon names. If used with the outgroup option avoid blanks in names as this might lead to erroneous recognition of taxon names.
Aliscore will write results into its own folder. it will produce two files, one file with the consensus Profile, and one file with a list of characters with negative scores in this profile.

=over
=item

	example of an input file:

	>Podura aquatica 18S_1
	aaagtctgtgacgttgtacggact
	gcgtgtgcagctgtgacgggcgcc
	>Sminthurus_sp
	AUTGCTugccguuugaucgugugc
	UUGGACUGCGUCGATCGUUGCGCG

=back

=head1 Usage

Aliscores knows several options, it chocks if an unknown option is encountered. Make sure you write the input options correctly, for example -w 4 and not -w4 or -w_4, etc., likewise do not (!) use -in infile, or in infile or -i_infile; these are all wrong input formats and will cause the program to die. It will still trie to open an "n infile" or "_infile" which is hopefully not present, it will also tell you this.

=over

=item *

-N option: without invoking the -N option gaps are treated as 5th character. With the -N option invoked gaps are treated as ambiguous character. Leading and tailing gaps of sequences are always interpreted as ambigous characters with and without the -N option. Interpreting gaps as ambiguous characters results in a loss of long indel sections consistently found in the majority of taxa. This means that well aligned expansion segements in rDNA sequences, which are not present in other taxa will be lost, if not commonly found in the MSA. Interpreting gaps as 5th character interprets stretches of indels as well aligned sections.


=item *

-w # option: without invoking this -w # option, Aliscore will use the default window size of 4 for the sliding window. You may choose any other window size, smaller or larger, but it does not make sense to choose something smaller then 4. If you vote for a much larger window size then 4, Aliscore will become successively blind for small stretches of randomly similar sections. (See paper on Aliscore performance). If you vote for window size <4 Aliscore will start making substantial type I errors and call non-randomly similar sites randomly similar, depending on its neighbors.


=item *

-r # option: if -r is used without an argument 4*N random pairs are compared, checking for replications (which are avoided). If -r is used with an argument, this number of randomly selected pairs is analysed and used to infer the consensus profile, if -r used used with an argument which is beyond the maximal number of possible non-overlapping pairs, only the maximal number of pairs is compared. If the -r option and the -t option are not used, random pairs are compared as default, with 4*N selection of pairs.


=item *

-t treefile option: -t must be used with a tree file in Newick format, rooted or unrooted. The tree file should be in the same folder as the sequence file (not mandatory). If there are more than one tree in the tree file, only the first one will be read, all other trees will be ignored. Aliscore will read the tree and store as a hash with node levels as keys and taxa as values for each node. Aliscores uses this tree to work through the MSA from tips to bottom of tree. First, sister groups of terminal taxa are identified (node lists, level 1 as key) and compared, these taxa are then replaced by consensus sequences using the ambiguity code. Consensus sequences represent now the new set of terminal taxa with which Aliscore proceeds. This process is repeated until every possible pair of sequences within the tree is evaluated. Make shure that your tree does not contain CRFL from Windows if working on Linux!


=item *

-l # option: -l can be used to restrict iterating through the tree to a specific node level, specified with the argument at the -l option. If -l 1 is used only primary sister group relationships are used to infer the consensus profile. If there are less node levels then arguments, Aliscore iterates through the tree and stops.


=item *

-s option: -s option can be used to generate a strict profile from all single comparisons. This profile will be very conservative because it scores every site as negative which exhibits a negative score in one single profile already. This option does not make to much sense, do not use it on purpose!


=item *

-o taxon,taxon,.. option: the -o option is used with a list of taxa separated by commatas. These taxa will be compared with all other taxa not in this list, but not with each other. It can be used to assess the range of randomness between outgroup taxa and ingroup taxa, or between every two groups of interest, if the alignment is restricted to ingroup taxa only before analysis.

=back

=cut


=pod

=head1 Interna

Details and comments are given in order of its appearance in code.


=head2 Input

Input Arguments are collected into a 1-dimensional array and grep is used to retrieve options plus arguments;
white spaces are cleaned off, and array is created by splitting input string at -;
If you use taxon names with white spaces in -o option you might run into problems.

	for example:
	our ($file)=grep /^i.+/,@INPUT;$file=~s/(^i)//;

=cut


#print $USAGE if infile or switches are missing

#declare and initialize variables

	our $transcript      = '-'         ;
	our $sequence_length = '-'         ;
	our @variability     = ()          ;
	our $invariant       = 0           ;
	our @invar_sections  = ()          ;
	our @temp            = ()          ;
	our $n_sections      = 0           ;
	our @section         = ()          ;

	our @PAIRS_org       = ()          ;
	our @PAIRS           = ()          ;
	our @PAIRScores      = ()          ;
	our $range           = '-'         ;
	our @Temp            = ()          ;
	our @Profile         = ()          ;
	our $position        = ()          ;
	our @Character_List  = ()          ;
	our $nchar           = '-'         ;
	our @taboo           = ()          ;
	our $ref_scoring     = ()          ;
	our $threshhold      = ()          ;

# process switches

#both subs assume the presence of global input variables listed above, they are therefore dependent on these and serve here just for improving readability
#Aliscore_module::help is used to provide short describtions of options and their use

#reads input given by @ARGV and changes default parameter if defined

our (  $file      ,
       $random    ,
       $window    ,
       $option    ,
       $tree      ,
       $level     ,
       $strict    ,
       $outgroup  ,
       $pairs     ,
       $indels    ,
       $group     ,
       $strict_in ,
       $ingo      ,
       $matrix
     )  		=  Aliscore_module::get_options () ;


=pod

=head2 Reading FASTA file

Fasta file is read and stored as a hash with taxon names as keys and references to sequence arrays as values. Sequences are stored as flat list, each position constituting an element. Only references to these hash elements are returned from the subroutine. The reference to the hash is used as a global variable indicated by our, only the file name is used as argument for the subroutine to open and read the file; will die if file has not bee found. Aliscore understands DNA ambiguity code, there is no need to replaces these. Aliscore does not accept any sign except letters and indels in sequences. It will die if anything else is encountered in seqquences.

	command:
	our ($ref_FASTA)=Alignment_alpha::readFASTA_simple($file);

number of taxa and taxon names are collected into an array for later comparison
Aliscore attempts to estimate the data type, either nucleotide or amino acid data. Aliscore considers sequences whith an ACTG content of > 0.8 (without counting indels and N) as nucleotide sequences, if less then 0.8 as amino acid data. It estimates data property from every sequence, if two sequences are considered of different data type, Aliscore stops. Aliscore might stop if a single nucleotide sequence contains more then 0.2 ambiguities. In almost every case, Aliscore will correctly estimate data type, if it does not, it will stop and report on the problem. If the data contains sequences of more then 0.2 ambiguities, it might be advisable to recode ambiguities as N's or remove the particular sequence.
RNA sequences will be recoded to DNA sequences. Nucleotide data can be a mix of RNA/DNA data.

=cut


print
<<FASTA;

	reading taxa from FASTA ...


FASTA

#reads file returns reference to FASTA Hash of file, taxon names are keys, sequence arrays are values, given in references
#if structures coded in dot/bracket format are present, these will separately be stored in hash

our ( $ref_FASTA, $ref_structures, $type ) = Aliscore_module::readFASTA_simple( $file , $ingo );


$type eq 'nt' and print
<<TYPE;


	data type             : nucleotide sequences
TYPE

$type eq 'RY' and print
<<TYPE;


	data type             : RY nucleotide sequences
TYPE

$type eq 'aa' and print
<<TYPE;


	data type             : amino acid sequences
TYPE
;

$type eq 'nt' and print
<<REPORT;

	input ...

	infile		: $file
	random pairs	: $pairs
	window size	: $window
	indels		: $indels
	tree file	: $tree
	node level	: $level
	strict profile	: $strict_in
	outgroup	: $group

REPORT

$type eq 'RY' and print
<<REPORT;

	input ...

	infile		: $file
	random pairs	: $pairs
	window size	: $window
	indels		: $indels
	tree file	: $tree
	node level	: $level
	strict profile	: $strict_in
	outgroup	: $group

REPORT

$type eq 'aa' and do {

		if ( $random =~ /r/ || $random =~ /^0$/ || $random =~ /-/ ) {

			$random = qw(r)    ;
			$pairs  = '4*NTAXA';
			$tree   = '-'      ;
print
<<TYPE;


	tree search with amino acid sequences
	currently not implemented

TYPE
;
		}
	};
	
$type eq 'RY' and do {

		if ( $random =~ /r/ || $random =~ /^0$/ || $random =~ /-/ ) {

			$random = qw(r)    ;
			$pairs  = '4*NTAXA';
			$tree   = '-'      ;
print
<<TYPE;


	tree search with amino acid sequences
	currently not implemented

TYPE
;
		}
	};

$type eq 'aa' and print
<<REPORT;

	input ...

	infile		: $file
	random pairs	: $pairs
	window size	: $window
	indels		: ambiguous
	tree file	: -
	node level	: -
	strict profile	: $strict_in
	outgroup	: $group
	matrix          : $matrix

REPORT


($type eq 'aa') and ($tree ne '-') and do {

print
<<TYPE;


	tree search with amino acid or RY sequences
	currently not implemented

TYPE
;
exit
};

($type eq 'RY') and ($tree ne '-') and do {

print
<<TYPE;


	tree search with amino acid or RY sequences
	currently not implemented

TYPE
;
exit
};

our @TAXA  = keys %$ref_FASTA;
our $NTaxa = keys %$ref_FASTA;

#executes random and tree switch
#resets number of pairs, if structures were present in data

$pairs     = 4*$NTaxa if $random =~ /^r$/                                         ;
$random    = 4*$NTaxa if $random =~ /^r$/ && ( $tree   =~ /-/ || $level =~ /all/ );

print
<<TAXA;
	number of taxa        : $NTaxa
	random number of pairs: $pairs

TAXA
;

our @STRUCTURES  = keys %$ref_structures;
our $NSTRUCTURES = keys %$ref_structures;

#checking and executing indel switch


$type eq 'nt' and do {

	if ($option eq "N"){map {grep s/\-/N/,@$_} values %$ref_FASTA}

	#substitutes T for U and reads sequence lengths

	$transcript  = map { grep  s/U/T/,@$_ } values %$ref_FASTA ;

	CHECK: {

		$sequence_length = @$_ and last CHECK for values %$ref_FASTA ;

		}

	#reports on recoding of RNA sequences

	print "\t","transcribed from RNA -> DNA","\n\n" if $transcript > 0 ;

	};

$type eq 'RY' and do {

	if ($option eq "N"){map {grep s/\-/N/,@$_} values %$ref_FASTA}

	CHECK: {

		$sequence_length = @$_ and last CHECK for values %$ref_FASTA ;

		}
	};


#replaces indels for X in amino acid sequences

$type eq 'aa' and do {

	#map {grep s/\-/X/,@$_} values %$ref_FASTA;

	#reads sequence lengths

	CHECK: {

		$sequence_length = @$_ and last CHECK for values %$ref_FASTA;

	       }

	};

=pod

=head2 Reading data type and scoring matrix

Reads data type and generates accordingly scoring matrix. In case of nucleotide data, the scoring matrix is a simple match mismatch scoring matrix, in case of ambiguous characters the mismatch is optimistically interpreted. If indels are considered 5th charaters, they are scored in a mismatch/match pattern. A BLOSUM62 is used for the amino acid scoring with indels and X scoring 0. For aminoacid scoring, a Monte Carlo approach is used to generate a threshhold value, given the actual window size and aminoacid composition of the data.

=cut

#gets scoring matrix depending on sequence type

$ref_scoring = Aliscore_module::get_scoring ( $type, $matrix );

#for ( keys %$ref_scoring ) { print $_,"\t",$ref_scoring->{$_},"\n"};#exit;

#creates cutoff value for aminoacid scoring using a delete half bootstrap plus MC resampling of scoring values, depending on window size

$type eq 'aa' and do {

print <<THRESHHOLD;
	generates threshhold value for amino acid data
	using $matrix

THRESHHOLD


	$threshhold = Aliscore_module::get_threshhold ( $ref_scoring, $window, $ref_FASTA );

=pod

$ingo refers to special aminoacid scoring. if $ingo is set to e, matching indels are penalized but not aminoacid and indel matches. This favors sections of the alignment, in which aminoacids are indeed present, but not dominating the signal. A biological interpretation is not straightforward, but given data from EST projects or phylogenomic data, in which often parts of genes are missing, ALISCORE is less restrictive and favors information from aminoacid data.


=cut


	$ingo =~ /1/ and do {

		for ( keys %$ref_scoring ) {

		$$ref_scoring{$_} = ( $threshhold*2 ) / $window   if /([A-Z])\-/i || /\-([A-Z])/i ;

		if ( $matrix eq 'MATCH' ) { $$ref_scoring{$_} = 1 if /([A-Z])\-/i || /\-([A-Z])/i }

		}

	};

	$ingo =~ /-/ and do {

		for ( keys %$ref_scoring ) {

		$$ref_scoring{$_} =  sprintf ("%.3f", $threshhold / $window ) - 0.01    if /\-\-/ ;

		if ( $matrix eq 'MATCH' ) { $$ref_scoring{$_} = -1 if /\-\-/ }

		}

	};

};


$type eq 'nt' and do {

	$ingo =~ /1/ and do {

		for ( keys %$ref_scoring ) {

		$$ref_scoring{$_} = 1   if /([A-Z])\-/i || /\-([A-Z])/i ;

		}
	};
};

$type eq 'RY' and do {

	$ingo =~ /1/ and do {

		for ( keys %$ref_scoring ) {

		$$ref_scoring{$_} = 1   if /([A-Z])\-/i || /\-([A-Z])/i ;

		}
	};
};

=pod

=head2 Checks for mutiple identical sequences

Aliscore checks for potential identical sequences. It considers sequences which can be a subset of another longer sequence, ignoring N, potentially identical. Only the longer sequence, not considering N's, will be retained for the analyses. If there are mutiple potentially identical sequences, only the one with the most inclusive sequence will be retained. Aliscore does not concatenate sequences, even if potentially profitable. Results are reported to the terminal.

=cut

#checks for multiple identical sequences

print <<SINGLETONS;
	checks for (potential) identical taxa

SINGLETONS


@taboo = Aliscore_module::draw_singletons ( $type, $ref_FASTA );


@taboo > 0 and do {

print <<SINGLETONS;

	taxa excluded:

SINGLETONS

printf "\t%-30.30s\n",$_ for ( @taboo )

};


#reports on invariant sections >$window, scores site patterns,records invariant sections and variant sections to score

print <<START;

	scores site patterns ...

START



=pod

=head2 Checking variability

Checks for invariant sections across the alignment with an extension of >w+2 (w window size). Reports these sections and places information as an argument into subroutine later. This step improves speed, because only variable sections are actually scored for random similarity. A simple iteration through all sequence arrays is used to check variability of sites. A @temp array is used to create the list of variable sections, results are reported to terminal

=cut

$type eq 'nt' and do {

VARIABILITY: for my $i (0..$sequence_length-1){

		 my %Patterns;

			for (values %$ref_FASTA){ $Patterns{$_->[$i]}++ };

				my $variability = keys %Patterns;

				if (1 == $variability && 0 == grep /N|\-/,keys %Patterns){

					push @section, $i;
				}

				else {

					if (($window*2-2) <= @section){

						push @invar_sections, (join",",@section);

						splice @section,$#section-($window-2);#print "@section\n";exit;

						push @temp, @section;

						$n_sections++
					}

					@section = ();
				}

			$invariant++ if 1 == $variability && 0 == grep /N|\-/,keys %Patterns;
	        }
#print "@temp\n";exit;
#report on variability

print <<INVAR;

	invariant positions: $invariant
INVAR



{
my $extend  = $window*2-2;
#
$n_sections > 0 and do {

print <<SECTIONS;
	number of continuous invariant sections with size > $extend: $n_sections

SECTIONS
	};
#
$n_sections == 0 and do {

print <<SECTIONS;
	no continuous section of size > $extend

SECTIONS
	};
}


#creates array of variable sections

	for my $position ( 0..$sequence_length-1 ){ push @variability, $position if 0 == grep/^$position$/,@temp };

#removes positions > $sequence_length-($window-1)

	pop @variability until ( $variability[$#variability] <= $sequence_length-($window) );

};


$type eq 'RY' and do {

VARIABILITY: for my $i (0..$sequence_length-1){

		 my %Patterns;

			for (values %$ref_FASTA){ $Patterns{$_->[$i]}++ };

				my $variability = keys %Patterns;

				if (1 == $variability && 0 == grep /N|\-/,keys %Patterns){

					push @section, $i;
				}

				else {

					if (($window*2-2) <= @section){

						push @invar_sections, (join",",@section);

						splice @section,$#section-($window-2);#print "@section\n";exit;

						push @temp, @section;

						$n_sections++
					}

					@section = ();
				}

			$invariant++ if 1 == $variability && 0 == grep /N|\-/,keys %Patterns;
	        }
#print "@temp\n";exit;
#report on variability

print <<INVAR;

	invariant positions: $invariant
INVAR



{
my $extend  = $window*2-2;
#
$n_sections > 0 and do {

print <<SECTIONS;
	number of continuous invariant sections with size > $extend: $n_sections

SECTIONS
	};
#
$n_sections == 0 and do {

print <<SECTIONS;
	no continuous section of size > $extend

SECTIONS
	};
}


#creates array of variable sections

	for my $position ( 0..$sequence_length-1 ){ push @variability, $position if 0 == grep/^$position$/,@temp };

#removes positions > $sequence_length-($window-1);

	pop @variability until ( $variability[$#variability] <= $sequence_length-($window) );

};

#exit;

#execute MC process

$type eq 'nt' and do {

print <<MC

	starting MC process with sliding window and 100 resamplings each ...


MC
};

$type eq 'RY' and do {

print <<MC

	starting MC process with sliding window and 100 resamplings each ...


MC
};

=pod

=head2 Scoring of randomly selected sequence pairs

The code reads the $random parameter and if defined with a number, which should have happend in any case except for the situation where the -t option and the -l option was envoked starts the random selection process. It first generates al possible pairs from the list of taxon names. It then checks whether the -o option was provided with an argument, if this is the case it fills a pairs list with all comparisons between outgroup taxa and ingroup taxa, if the -o option was not provided with an argument, it checks the argument of the -r option and selects as many random unique pairs from the list of all possible pairs. If the argument of -r was too large it stops when all possible pairs are included.

=cut


#random selection of taxa pairs option, also outgroup option

if ($random =~ /\d+/){

	RANDOM: {

		my $max_PAIRS = ($NTaxa-@taboo)*($NTaxa-@taboo-1)/2;#print $max_PAIRS,"\n";exit;

#remove potentially identical taxa

			for my $taboo (@taboo){grep s/^$taboo$//,@TAXA};

			my $TAXA = join",",@TAXA;

			for ($TAXA){

				s/^\,+//x   ;
				s/\,+/\,/xg ;
				s/\,+$//x   ;
			}

			@TAXA = split",",$TAXA;

			die "\n\tnot enough taxa left!\n\n" if 1 >= @TAXA ;

#outgroup option
			if ($outgroup!~/-/){

				for my $taxon (split"\,",$outgroup){grep s/^$taxon$//,@TAXA}

				for my $taxon (split"\,",$outgroup){for (@TAXA){push @PAIRS, ($taxon.",".$_) unless 0 == length($_)}}
			}

#generates set of all possible pairs

			else {
				until (1 == @TAXA){

					my $first = shift@TAXA;

					push @PAIRS_org, ($first.",".$TAXA[$_]) for(0..$#TAXA);
				}

			my $number = @PAIRS_org;

#draws randomly from this set of all possible pairs

#report on number of pairs and random switch

$random < $max_PAIRS and do {

print <<MAX;

	max number of different pairs is $max_PAIRS
	$random random pairs are scored!

MAX

};

$random >= $max_PAIRS and do {

print <<MAX;

	max number of different pairs is $max_PAIRS
	max random pairs are scored!

MAX

};

#if variable random exceeds max number of pairs, all pairs are evaluated

				if ($random >= $max_PAIRS) {

					@PAIRS=@PAIRS_org
				}

#if variable random is less then max number of pairs, array of pairs is filled randomly, and without replicates from all possible pairs

				else {
					until ($random == @PAIRS){

						my @pair_new = splice@PAIRS_org,int(rand($#PAIRS_org)),1;

						push @PAIRS, $pair_new[0];
					}
				}
			}


#starts scoring of sequence pairs, uses parsimony scoring subroutine


=pod

=head3 Scoring

For each entry in the pairs list, it uses the two taxon names to look in the data hash for both sequences and uses the subroutine C>> nuc/aa_score_two >> with the scoring type, flat list of variable characters and both sequence references as arguments. All arguments are provided as references. The scoring profile is returned as a reference. Description of the scoring process see Alignment_alpha.pm. The list of arguments must be in order, reference to the scoring type must be first.

=cut


	my $counter = 1;


		for (@PAIRS){

			my ($taxon1,$taxon2) = split"\,";

			printf "\tpair: %-6.6s \-\>\ttaxon1: %-10.10s\ttaxon2: %-10.10s\n" , $counter, $taxon1, $taxon2 ;

			my $score;

#subroutine nuc/aa_score_two delivers a reference to the scoring array for the two sequences, it expects as input four arguments, first an option, window size, and two sequences as 1-dimensional arrays

			$score = Aliscore_module::nuc_score_two ($ref_scoring,\@variability,$window,$$ref_FASTA{$taxon1},$$ref_FASTA{$taxon2}) if $type eq 'nt';#print "@$score\n";exit;
			$score = Aliscore_module::nuc_score_two ($ref_scoring,\@variability,$window,$$ref_FASTA{$taxon1},$$ref_FASTA{$taxon2}) if $type eq 'RY';#print "@$score\n";exit;
			$score = Aliscore_module::aa_score_two  ($ref_scoring,$threshhold,$window,$$ref_FASTA{$taxon1},$$ref_FASTA{$taxon2})   if $type eq 'aa';#print "@$score\n";exit;

#counts the frequency of minus scores in score array and reports

			my $count = grep /\-\d/,@$score;

			print "\t            \tpositions below base line: ",$count,"\n";

#transfers the score as a string into score collector array

			push @PAIRScores, (join"\,",@$score);

			$counter++
		}#end of foreach pairs

	}#end of RANDOM
}
#end of random sampling of pairs, RANDOM
#_______________________________________________________________________________________________________________________________________


=pod

=head2 Scoring using tree based selection of pairwise comparisons

A user provided tree, rooted or unrooted, but fully dichotomous must be provided by the user. This tree is used for selection of sequence pairs. First, terminal sister taxa are compared, then these sequence pairs are replace by one consensus sequence. Consequently, the next set of terminal sequence pairs might contain consensus sequences and primary sequences. Consensus sequences make uses of the full ambiguity code to represent every difference in primary parent sequences. The scoring stops when the last sequence pair has been analysed.

=cut


else {

#reads tree and delivers a list of nodes for the progressive aliscore evaluation
#reads tree file if option on


	TREE: {

		my ( $NJ_Tree, @nodes );

		if ( $tree =~ /^NJ$/ ) {

			my $hamming_distance              = Aliscore_module::hamming_distance ( $ref_FASTA , @taboo ) ;

			( $NJ_Tree , @nodes )             = Aliscore_module::NJ_tree   ( $hamming_distance ) ;

			grep { s/\(//g , s/\)//g , s/(\:(?i:[\w\-\.])+)//g } @nodes ;                                     #print "@nodes\n";exit;


			PRINTTREE: {

					open  TREE ,">","${file}.tre";
					print TREE "$NJ_Tree\;"      ;
					close TREE                   ;                                                    #print $NJ_Tree,"\n";exit;

				    }

		}

		else {

=pod

=head3 Reading Tree

Tree must be in Newick format. Be careful, PAUP saves trees with basal polytomy as default. If these trees are used, an error message will stop the process (hopefully !). Save trees without basal polytomies in PAUP and everything will be fine. Check set options in PAUP! You can use rooted trees, either rooted in PAUP or any other software package, and everything should be fine. Take care to check taxon names in trees, because only if these names correspond exactly (!) to names in sequence files, scoring will be performed. Aliscore will have its own tree reconstruction routine soon, to avoid problems of incongruent taxon names and polytomies.

=cut



		my($ref_tree_taxa,$ref_nodes,$ref_tree) = Aliscore_module::readTOPOLOGY ($tree) ;

		@nodes                                  = keys %$ref_nodes;                                               #print $_,"\n" for @nodes;exit;

		}


		#gets ambiguitiy table as reference

		my $table                               = Aliscore_module::ambiguity_table ();


		#remove doubled taxa, noch besser machen!!!!!!!


=pod

=head3 Removing potentially identical taxa

Similarly to random pair selection, Aliscore removes potentially identical sequences in tree base selection of sequence pairs.

=cut


		for my $taboo (@taboo){grep s/\Q$taboo\E//,@nodes};

		for (@nodes){

			s/^\,+//  ;
			s/\,+/\,/g;
			s/\,+$//  ;
			s/.+// if !/\,/

		}

		my $nodes = join";",@nodes;

		for ($nodes){

			s/^\;+//  ;
			s/\;+/\;/g;
			s/\;+$//  ;

		}

		@nodes = split "\;",$nodes;									#print $_,"\n" for @nodes;exit;

		#removes leading and trailing blanks of taxon names

		grep s/^ *//,@nodes;
		grep s/ *$//,@nodes;

		my $nodelevel=1;

		until ( ! grep { /^((?i:[\w\-\.\* ])+\,(?i:[\w\-\.\* ])+)$/ } @nodes ){


			@PAIRS  = grep /^((?i:[\w\-\.\* ])+\,(?i:[\w\-\.\* ])+)$/,@nodes;                                 #print $_,"\n" for @PAIRS;#exit;


print<<NODELEVEL;

	working on node level: $nodelevel ...

NODELEVEL

			for (@PAIRS){

				my ($taxon1,$taxon2) = split"\,";

				if ( $taxon1 && $taxon2 !~/\*/ && $level!~/\+/ ) {

				printf "\ttaxon1: %-10.10s\ttaxon2: %-10.10s\n" , $taxon1, $taxon2

			        }

				die "taxon names of tree and sequence files do not match!\nprocess terminated!\n" if (!(grep /^\Q$taxon1\E$/,(keys %$ref_FASTA)) || !(grep /^\Q$taxon2\E$/,(keys %$ref_FASTA)));

				my $score = Aliscore_module::nuc_score_two ($ref_scoring,\@variability,$window,$$ref_FASTA{$taxon1},$$ref_FASTA{$taxon2});

			#print "@{$$ref_FASTA{$taxon1}}\n";exit;

				($level =~ /all/ || $level !~ /\+/) and do {

							my $count = grep /\-\d/,@$score;

							print "\tpositions below baseline: $count\n";

							push @PAIRScores, (join"\,",@$score);

							};

				($level =~ /(\d+)\+/) 		    and do {

							if ($1<=$nodelevel){

							my $count=grep /\-\d/,@$score;

							print "\tpositions below baseline: ",$count,"\n";

							push @PAIRScores, (join"\,",@$score);

							}
							};


			#creates consensus array of two sequences, array of references to arrays, 2-dimensional array

				$$ref_FASTA{$taxon1."*".$taxon2} = [ Aliscore_module::consensus_sequence($table,$$ref_FASTA{$taxon1},$$ref_FASTA{$taxon2}) ];

				delete $$ref_FASTA{$taxon1} ; delete $$ref_FASTA{$taxon2};

				#for my $keys ( keys %$ref_FASTA ) { print $keys,"\t"} print "\n";

				grep s/\Q$taxon1\E\,\Q$taxon2\E/$taxon1\*$taxon2/g,@nodes;                                #print "@nodes\n";#exit;

			}#end of foreach pairs

		$nodelevel++;

		if ($level !~ /all/ && $level !~ /\+/){last TREE if $level < $nodelevel}

		}#end of until

	}#end of TREE
}

#undef @PAIRS;
#end of sampling of pairs from trees, TREE

OUTFILE:{

open OUT, ">", "${file}_Profile_l${level}.txt" and last OUTFILE if $level   =~  /\d+/;
open OUT, ">", "${file}_Profile_l_all.txt"     and last OUTFILE if $level   !~  /\d+/ && $tree=~/\w/;
open OUT, ">", "${file}_Profile_random.txt"     and last OUTFILE if $random  =~  /\d+/;

	}


=pod

=head2 Generation of Consensus Profiles

From the collection of single profiles a consensus profile is generated. The consensus profile consists of medians for each site derived from site scores of all single profiles. It is thus a consensus representation of the situation in single profiles. Aliscore generates a List of all characters of the consensus profile below the 0 - base line. This list is written into a list file. Additionally, Aliscore writes a profile file in which three collumns are written. First column, an enummeration of positions, second column sites with positive consensus values and third column sites with negative consensus values.
Alternative consensus techniques would be conceivable, but the median certainly reflects the dominating mode among single profiles.
Single profiles are collected into a temporary array, before a consensus profile will be generated. If the number of taxa > 200 and/or length of sequences > 8000 the process might crash because of RAM limits. This must be corrected in the near future, to avoid problems with very large data.

=cut


#generates quality profile from collected scores

print <<GENERATE;

	generates quality profile from collected scores ...

GENERATE

$range = @PAIRScores;#print "@PAIRScores\n";exit;

my @Medianprofile = () ;

#creates temp container with score arrays

	for (@PAIRScores){push @Temp, [ split"," ]}

#adds scores from invariant sections to total pairswise scores

	for (@invar_sections){

		my @section=split",";

		for my $score (@Temp){

			for (0..$window-1){

				map {$_+=1} @$score[$section[$_]..$section[$#section-$_]];

			}
		}
	}

#adds headers to profiles

	push @Profile, "position\tpositive\tnegative\n";


#records individual scores, scales them and adds scores from all profiles over every site to generate a median score

	$strict =~ /1/ and do {

		for my $j (0..($sequence_length-1)){

			my @site_pr;

			push @Profile, ($j+1,"\t");

			my $n = 0;

			STRICT: for (0..$range-1){

					if ($Temp[$_][$j]<0){

						push @Profile, "0\t-1\n";
						push @Medianprofile, "-1";

						$n++;

						last STRICT;

					}
				}

			push @Profile, "1\t0\n" if $n==0;
			push @Medianprofile, "1";
		}
	};

	$strict =~ /-/ and do {

		for my $j (0..($sequence_length-1)){

			my @site_pr;

			push @Profile, ($j+1,"\t");

			push @site_pr, $Temp[$_][$j] for (0..($range-1));

			@site_pr = sort {$a<=>$b} @site_pr;

			my $site_median = ($range/2)=~/\./ ? $site_pr[(($range+1)/2)-1] : ($site_pr[($range/2)-1]+$site_pr[$range/2])/2;

			$site_median /= $window;

			push @Profile, "$site_median\t0\n" if $site_median >= 0;
			push @Profile, "0\t$site_median\n" if $site_median <  0;
			push @Medianprofile, "$site_median";
		}
	};

#prints out into profile file

	print OUT (join"",@Profile);
#	undef @Temp;
	close OUT;

#print OUT $Profile;

for my $element (@Temp){
	map {$_ /= $window} @{$element}
}

unshift @Temp, \@Medianprofile ;

#print "@{$Temp[0]}\n";exit;


print <<SCORING;

	scoring done ...

SCORING


	SVGPROFILES: {

	#generates vector plot from collected scores

print <<GENERATEPROFILES;

	generates vector plot from collected scores ...


GENERATEPROFILES

	Aliscore_module::profiles_svg ( $file, \@Temp) ;

	}


	my @Median_Profile = grep/\d\n/,@Profile;

	for (@Median_Profile){

		$nchar++;

		push @Character_List, "$nchar " if /\-/;
	}

	my $Character_List =  join"",@Character_List;
	$Character_List    =~ s/ $//g;

LIST: 		 {

	open LIST, ">", "${file}_List_l${level}.txt" 		      and last LIST 		if $level  =~ /\d+/;
	open LIST, ">", "${file}_List_l_all.txt"     		      and last LIST 		if $level  !~ /\d+/&& $tree=~/\w/;
	open LIST, ">", "${file}_List_random.txt"     		      and last LIST 		if $random =~ /\d+/;

		 }

	print LIST $Character_List."\n";
	close LIST;

PRINTINGPROFILE: {

	print "\tProfile written to ${file}_Profile_l${level}.txt\n" and last PRINTINGPROFILE if $level  =~ /\d+/;
	print "\tProfile written to ${file}_Profile_l_all.txt\n"     and last PRINTINGPROFILE if $level  !~ /\d+/&& $tree=~/\w/;
	print "\tProfile written to ${file}_Profile_random.txt\n"     and last PRINTINGPROFILE if $random =~ /\d+/;

		 }
PRINTINGLIST:    {

	print "\tList 	written to ${file}_List_l${level}.txt\n"    and last PRINTINGLIST    if $level  =~ /\d+/;
	print "\tList   written to ${file}_List_l_all.txt\n"        and last PRINTINGLIST    if $level  !~ /\d+/&& $tree=~/\w/;
	print "\tList   written to ${file}_List_random.txt\n"        and last PRINTINGLIST    if $random =~ /\d+/;

		 }

undef (%$ref_FASTA);
undef @PAIRScores;

my ($user,$system,$cuser,$csystem) = times;

print <<TIME;

	time used: $user sec

TIME

exit;

#finish

=pod

=head1 Copyright

das glaub ich ja gar nicht das das je so sein koennte!

Bernhard Misof, Feburary 2008

=cut

