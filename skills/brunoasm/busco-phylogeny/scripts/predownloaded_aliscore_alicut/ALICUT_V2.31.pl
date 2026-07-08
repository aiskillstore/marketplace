#!/usr/bin/perl
use strict       ;
use File::Copy   ;
use Tie::File    ;
use Fcntl        ;
use Term::Cap ;
use Term::ANSIColor qw(:constants);
use Getopt::Std  ;

# updated on 13th february , 2009 by patrick kück
# updated on  2nd april    , 2009 by patrick kück
# updated on 15th june     , 2009 by patrick kück
# updated on 26th july     , 2009 by patrick kück
# updated on  7th september, 2011 by patrick kück (alicut v2.3)
# updated on 22.2.2017, by patrick kück (alicut v2.31) -> correction of initial warning due to line 547, changed some terminal prints, argv handling commands

my @answer_remain_stems = ( 'no', 'yes' ) ;
my @answer_codons       = ( 'no', 'yes' ) ;
my @answer_third_pos    = ( 'no', 'yes' ) ;

&argv_handling ( \@answer_remain_stems, \@answer_codons, \@answer_third_pos ) ;
&menu          ( \@answer_remain_stems, \@answer_codons, \@answer_third_pos ) ;



sub argv_handling{
	
	my $aref_remain_stems = $_[0] ;
	my $aref_codons       = $_[1] ;
	my $aref_third_pos    = $_[2] ;
	
	my ( $commandline )   = join "", @ARGV ;
		
	$commandline =~ s/ |\s+// ;
	my @commands = split "-", $commandline ;
	shift @commands ;
		
	for my $single_command ( sort @commands ){
			
			if		( $single_command =~ /^r$/i ) { @$aref_remain_stems = ( reverse @$aref_remain_stems) }
			elsif	( $single_command =~ /^c$/i ) { @$aref_codons       = ( reverse @$aref_codons      ) }
			elsif	( $single_command =~ /^3$/i ) { @$aref_third_pos    = ( reverse @$aref_third_pos   ) }
			elsif	( $single_command =~ /^h$/i ) { &help }
			elsif	( $single_command =~ /^p$/i ) { &preface }
			elsif	( $single_command =~ /^s$/i ) {  
													&header ;
													&commands( \$aref_remain_stems->[0], \$aref_codons->[0], \$aref_third_pos->[0]) ;
													&start (\$aref_remain_stems->[0], \$aref_codons->[0], \$aref_third_pos->[0])
			}
			else	{ print "\n\t!COMMAND-ERROR!: unknown command \"-", $single_command, "\"\n" }
	}
		
	&menu ( \@$aref_remain_stems, \@$aref_codons, \@$aref_third_pos)
}

sub header{
	
	printf "\n%68s\n", "------------------------------------------------------------"     ;
	printf "%49s\n"  , "Welcome to ALICUT V2.31 !"                                        ;
	printf "%60s\n"  , "a Perlscript to cut ALISCORE identified RSS"                      ;
	printf "%57s\n"  , "written by Patrick Kueck (ZFMK, Bonn)"                            ;
	printf "%68s\n\n", "------------------------------------------------------------"     ;
}

sub commands{
	
	my $sref_rem_stems = $_[0] ;
	my $sref_reo_codon = $_[1] ;
	my $sref_th_posit  = $_[2] ;
	
	print  "\n\t------------------------------------------------------------"             ;
	print  "\n\tRemain Stem Position   :\t", $$sref_rem_stems ;
	print  "\n\tRemove Codon           :\t", $$sref_reo_codon ;
	print  "\n\tRemove 3rd Position    :\t", $$sref_th_posit ;
	print  "\n\t------------------------------------------------------------\n"           ;
}

sub help{
	
	print
 <<info;
    
	-------------------------------------------------------------------
	-------------------------------------------------------------------
	
	General Information and Usage:
	-------------------------------
	ALICUT V2.31 removes ALISCORE identified RSS positions 
	in given FASTA file(s) which are listed in the FASTA file cor-
	responding ALISCORE "List" outfile(s). If structure sequences
	are implemented, ALICUT V2.3 automatically replaces brackets 
	of non rss positions by dots when they are paired with rss 
	identified positions.
	
	
	
	Start ALICUT under default
	-------------------------------------------------------------------
	To remove all ALISCORE identified RSS positions:
	
	Type <s> return (via Menu) or
	Type <perl ALICUT_V2.3.pl -s> <enter> (via command line)
	
	
	
	R-Option (Remain Stems)
	-------------------------------------------------------------------
	To remain all stem positions of identified rss within FASTA file(s): 
	
	Type <r> <return> <s> <enter> (via Menu)
	Type <perl ALICUT_V2.3.pl -r -s> <enter> (via command line)
	
	
	
	C-Option (Remove Codon)
	-------------------------------------------------------------------
	To translate ALISCORE identified RSS positions of amino-acid data
	into nucleotide triplet positions before exclusion of randomised
	sequence sections:
	
	Type <c> return <s> return (via Menu) or
	Type <perl ALICUT_V2.3.pl -c -s> <enter> (via command line)
	
	Note: 
	This option is only useful if you have analysed amino-acid 
	data, but wish to exclude nucleotide positions from the amino-acid 
	data corresponding nucleotide data.
	Be aware, that the name of the nucleotide data file has to be named 
	equal to the ALISCORE analysed amino-acid data file. The C-option
	can not be applied on amino-acid sequences. Otherwise, ALICUT
	excludes the original ALISCORE identified sequence sections.
	
	
	
	3-Option (Remove 3rd position)
	-------------------------------------------------------------------
	To remove ALISCORE identified RSS only if its sequence position is 
	up to amultiple of 3:
	
	Type <3> <return> <s> <return> (via Menu)
	Type <perl ALICUT_V2.3.pl -3 -s> <enter> (via command line)
	
	Note: 
	The 3-Option can be combined with the C-option. In this case,
	positions of the ALISCORE "List" outfile(s) are translated into
	codon positions from which only the 3rd positions are excluded.
	The 3-Option can only be applied on nucleotide data. Otherwise, 
	ALICUT excludes the original ALISCORE identified sequence sections.
	
	
	
	ALICUT IN and OUT files
	-------------------------------------------------------------------
	ALICUT V2.3 needs the original ALISCORE FASTA infile(s) and "List"
	outfile(s) in the same folder as ALICUT V2.3.
	
	The "List" outfile(s) must contain the identified RSS positions
	in one single line, separated by whitespace.
	
	e.g. 1 3 5 6 8 9 10 11 123 127 10000 10001
	
	ALICUT V2.0 can handle unlimited FASTA files in one single run.
	The sole condition is that the Prefix of the ALISCORE "List" 
	outfile(s) are identic with the associated FASTA infile(s). 
	ALICUT V2.3 first searches for the ALISCORE "List" outfile(s), 
	removes the Suffix "_List_random.txt" and searches for the 
	"List" associated FASTA file(s).
	
	e.g. COI.fas_List_random.txt (ALISCORE "List" outfile)
	     COI.fas                 (Associated FASTA infile)
	
	If both files are detected, ALICUT V2.3 excludes the RSS identified 
	positions of the "List" file(s) in the associated
	FASTA file(s) and saves the changes in a new FASTA outfile,
	named "ALICUT_FASTAinputname.fas".
	
	Under the C- and 3-Option, removed sequence positions differ from
	the original "List" position numbers. Under both options, ALICUT 
	prints the actually removed positions in separate "ALICUT_LIST" 
	outfile(s).
	
	ALICUT V2.3 generates also an info file "ALICUT_info". This file 
	informs about the number and percentage of removed positions, number 
	of single sequences, single parameter settings, and sequence states 
	of each restricted FASTA file. 
	If structure sequences are identified by ALICUT, ALICUT generates
	structure info file(s) which lists remaining stem pairs and loop 
	positions, as well as percentages of both structure elements.
	
	-------------------------------------------------------------------
	-------------------------------------------------------------------
	
	
info
;

	print  "\tBACK to ALICUT MAIN-Menu:\t\t type <return>\n"                    ;
	print  "\n\t------------------------------------------------------------\n\t"  ;

	chomp ( my $answer_xy = <STDIN> );

	&menu ;
	
}

sub preface{

print
<<preface
	
	--------------------FASconCAT PREFACE---------------------
	
	Version     : 2.31
	Language    : PERL
	Last Update : 22nd February, 2017
	Author      : Patrick Kueck, ZFMK Bonn GERMANY
	e-mail      : patrick_kueck\@web.de
	Homepage    : http://www.zfmk.de
	
	This program is free software; you can whitedistribute it 
	and/or modify it under the terms of the GNU General Public 
	License as published by the Free Software Foundation ; 
	either version 2 of the License, or (at your option) any 
	later version.

	This program is distributed in the hope that it will be 
	useful, but WITHOUT ANY WARRANTY; without even the 
	implied warranty of MERCHANTABILITY or FITNESS FOR A 
	PARTICULAR PURPOSE. See the GNU General Public License for 
	more details. 

	You should have received a copy of the GNU General Public 
	License along with this program; if not, write to the Free 
	Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, 
	USA.
	
	For further free downloadable programs visit:
	www.zfmk.de/web/Forschung/Abteilungen/AG_Wgele/index.en.html
	
	------------------------------------------------------------

preface
; 

	print  "\tBACK to ALICUT MAIN-Menu:\t\t type <return>\n"                       ;
	print  "\n\t------------------------------------------------------------\n\t"  ;

	chomp ( my $answer_xy = <STDIN> );

	&menu;
}

sub menu{
	
	my $aref_remain_stems = $_[0] ;
	my $aref_remove_codon = $_[1] ;
	my $aref_third_posit  = $_[2] ;
	
	&header ;
	
	print "\n\tSTART ALICUT:\t\ttype <s> <return>"                                        ;
	print "\n\tQUIT  ALICUT:\t\ttype <q> <return>"                                        ;
	print "\n\tREMAIN STEMS:\t\ttype <r> <return>"                                        ;
	print "\n\tREMOVE CODON:\t\ttype <c> <return>"                                        ;
	print "\n\tREMOVE   3rd:\t\ttype <3> <return>"                                        ;
	print "\n\tHELP:\t\t\ttype <h> <return>"                                              ;
	print "\n\tPREFACE:\t\ttype <p> <return>"                                             ;
	
	&commands ( \$aref_remain_stems->[0], \$aref_remove_codon->[0], \$aref_third_posit->[0] );
	
	my       $answer_opening =  &commandline ;
	
	until  ( $answer_opening =~ /^s$|^r$|^c$|^p$|^h$|^1$|^2$|^q$|^3$/i ){ 
		
		print "\n\t!COMMAND-ERROR!: unknown command \"$answer_opening\"!\n" ;

		$answer_opening =  &commandline ;
	}

	$answer_opening =~ /^s$/i      and do { &start ( \$aref_remain_stems->[0], \$aref_remove_codon->[0], \$aref_third_posit->[0] ) } ;
	$answer_opening =~ /^r$/i      and do { @$aref_remain_stems = (reverse @$aref_remain_stems ); &menu                            } ;
	$answer_opening =~ /^c$/i      and do { @$aref_remove_codon = (reverse @$aref_remove_codon ); &menu                            } ;
	$answer_opening =~ /^3$/i      and do { @$aref_third_posit  = (reverse @$aref_third_posit  ); &menu                            } ;
	$answer_opening =~ /^q$/i      and do {                                                        exit                            } ;
	$answer_opening =~ /^h$/i      and do {                                                       &help                            } ;
	$answer_opening =~ /^1$/       and do {                                                       &error1                          } ;
	$answer_opening =~ /^2$/       and do {                                                       &error2                          } ;
	$answer_opening =~ /^p$/i      and do {                                                       &preface                         }
}

sub start{
	
	my $sref_stems_remain = $_[0] ;
	my $sref_codon_remove = $_[1] ;
	my $sref_third_remove = $_[2] ;
	
	my $j = 0  ;
	
	open  OUTinfo, ">>ALICUT_info.xls" ;
	print OUTinfo  "\nUsed List File\tUsed Fasta file\tremove triplets\tremove 3rd position\tnumber taxa\tbp before\tbp after\tremaining bp [%]\tsequence type\n"  ;
	
	
	
	# Read IN of all List_random.txt files within the same folder as ALICUT and handle it
	READING:
	foreach my $file ( <*List_*.txt> ) {
		
		# Set counter +1
		$j++;
	    
		
		
		# Read in of the ALISCORE-list outfile
		&tie_linefeeds ( \$file ) ;
		( open IN, "<$file" ) or die "n\t!FILE-ERROR!: Can not open listfile $file!\n" ;
		my $line = <IN> ; chomp $line ;
		
		# check for correct aliscore list format
		unless ( $line =~ /^(\d+ )+\d+$|^\d+$/ ) { warn "\t!FILE-WARN!: $file has no ALISCORE list format!\n" ; next READING }
		
		# Total number of randomized identified positions
		my @cut_positions = split " ", $line  ; close IN ;
		
		
		
		# "filename.fas_List_random.txt" to "filename.fas"
		( my $file_fasta = $file ) =~ s/_List_.+//  ;
		
		# Read in of the original ALISCORE fasta infile which belongs to the listfile
		&tie_linefeeds ( \$file_fasta ) ;
		( open INfas, "<$file_fasta" ) or warn "\t!FILE-WARN!: Can not find $file_fasta!\n" and next READING ;
		
		chomp ( my @inputfile = <INfas> ) ; close INfas ;
		warn  "\t!FILE-WARN!: File $file_fasta is empty!\n" if 0 == @inputfile and next READING ;
		
		# Handle the FASTA file in the way that sequencename and sequence alternate in each line
		@inputfile                   = fas_bearbeiten ( @inputfile ) ;
		
		# Generate a hash: key=>taxon, value => sequenz
		my %sequence                 = @inputfile ;
		my @values                   = values %sequence ;
		
		# Determine basepositions before und after cut. Output of cuttings as total number and in percent
		my $number_sequences         = keys %sequence ;
	    my $number_characters_before = length $values[0] ;
		
		
		
		
		
		
		# Check for correct FASTA format and handling of structure sequence
		my $sequence_state = 'nt' ;
		SEQUENCE_CHECK:
		for my $raw_taxon ( keys %sequence ){
				
				# if whitespace are between ">" and the next sign within a sequence name, delete these whitespaces
				$raw_taxon =~ s/^\>\s*/\>/g ;
			
				# if whitespaces between last sign and newline in sequence name, delete these whitespaces
				$raw_taxon =~ s/\s*$//g ;
			
				die    "\n\t!FILE-ERROR!: $raw_taxon in $file_fasta is not in FASTA format!\n"                     if           $raw_taxon                  !~ /^\>/                             ;
				die    "\n\t!FILE-ERROR!: Sequence name missing in $file_fasta!\n"                                 if           $raw_taxon                  =~ /^\>$/                            ;
				die    "\n\t!FILE-ERROR!: Sequence name $raw_taxon in $file_fasta involves forbidden signs!\n"     if           $raw_taxon                  !~ /\w/                              ;
				die    "\n\t!FILE-ERROR!: Sequences of $file_fasta have no equal length!\n"                        if length    $sequence{$raw_taxon}       != $number_characters_before         ;
				die    "\n\t!FILE-ERROR!: Sequence missing in $file_fasta!\n"                                      if           $sequence{$raw_taxon}       =~ /^\n$|^$/                         ;
				die    "\n\t!FILE-ERROR!: Sequence length in $file_fasta is too short to cut all positions!\n"     if           $number_characters_before   <  $cut_positions[ $#cut_positions ] ;
				
				
				
				# Structure handling
				if ( $sequence{$raw_taxon} =~ /.*\(.*\).*/ ){
					
					$sequence{$raw_taxon}  =~ s/-/./g  ;
					my @strc_elements      =  split "" , $sequence{$raw_taxon} ;
					
					for my $str_sign ( @strc_elements ){ 
						
						unless ( $str_sign =~ /\(|\)|\./ ){ die "\n\t!FILE-ERROR!: Structure string of $file_fasta involves forbidden signs in $raw_taxon!\n" }
					}
					
					my $structurestring       =  $sequence{$raw_taxon} ; 
					   $structurestring       =~ s/-/./g ;
					   $sequence{$raw_taxon}  =  &structure_handling ( \$structurestring, \$$sref_stems_remain, \@cut_positions, \$file_fasta ); next SEQUENCE_CHECK ;
				}
		
				
				
				# Check for correct sequence states
				$sequence{$raw_taxon}   =~ s/(\w+)/\U$1/ig ;
				my @seq_elements           = split "" , $sequence{$raw_taxon} ;
				
				for my $seq_sign ( @seq_elements ){ 
					
					unless ( $seq_sign =~ /A|C|G|T|U|-|N|Y|X|R|W|S|K|M|D|V|H|B|Q|E|I|L|F|P|\?/ ){ die "\n\t!FILE-ERROR!: Sequence of $file_fasta involves forbidden signs in $raw_taxon!\n" }
				}
				
				if ( $sequence{$raw_taxon}  =~ /I|E|L|Q|F|P/ ) { $sequence_state = 'aa' }
		}
		
		
		
		
		
		
		
		
		# Translate cut positions
		my @fasta_cut;
		&translate_cut_positions( \$$sref_codon_remove, \$$sref_third_remove, \@cut_positions, \$number_characters_before, \@fasta_cut, \$sequence_state, \$file_fasta );
		
		
		# Calculate percent of remaining positions
		my $number_cut_positions     = @cut_positions ;
		my $number_characters_after  = $number_characters_before-$number_cut_positions ;
		
		my $percent_left =  sprintf "%.1f", ( $number_characters_after / $number_characters_before ) * 100 ;
		   $percent_left =~ s/\./,/g ;
		   
		
		# Assume uncut positions to $final and print out to ALICUT_$file_fasta
		if    ( $$sref_codon_remove =~ /yes/ && $$sref_third_remove =~ /yes/ ){ open OUT, ">ALICUT_codon_3rd_$file_fasta" }
		elsif ( $$sref_codon_remove =~ /yes/ && $$sref_third_remove =~ /no/  ){ open OUT, ">ALICUT_codon_$file_fasta"     }
		elsif ( $$sref_codon_remove =~ /no/  && $$sref_third_remove =~ /yes/ ){ open OUT, ">ALICUT_3rd_$file_fasta"       }
		else                                                                  { open OUT, ">ALICUT_$file_fasta"           }
		
		for ( keys %sequence ){
			
			my @bases = split "", $sequence{$_}          ;
			my @final = map { $bases[$_] } @fasta_cut    ;
			my $final = $_."\n".( join "", @final )."\n" ;
			
			print OUT "$final" ;
		}
		close OUT;
		
		
		
		# Print Out of extra infos to ALICUT_info
		print OUTinfo  "$file\t$file_fasta\t$$sref_codon_remove\t$$sref_third_remove\t$number_sequences\t$number_characters_before\t$number_characters_after\t$percent_left\t$sequence_state\n" ;
		print          "\tDone  : $file cut to ALICUT_$file_fasta\n" 
	}
	
	close OUTinfo  ;
	
	
	# Print OUT number of right handled FASTA files in relation to total number of files
	printf "\n%68s\n",   "------------------------------------------------------------" ;
	printf "%42s\n",     "$j FASTA file(s) correctly handled!"                          ;
	printf "%57s\n",     "Further infos are printed out in Alicut_info.txt!"            ;
	printf "\n%63s\n",   "ALICUT V2.0 Finished! Thank you and good bye!"                ;
	printf "%68s\n",     "------------------------------------------------------------" ;
	
	
	&set_timer ;
	exit ;
	
	sub tie_linefeeds{
		
		my $sref_filename = $_[0] ;
		
		( open IN , "<$$sref_filename" ) or warn "\tError: can not open $$sref_filename!\n" and next READING ;
		
		(tie ( my @data, 'Tie::File', $$sref_filename )) ;
		
		warn "\t!FILE-WARN!: $$sref_filename is empty!\n" and next READING if 0 == @data ;
		
		map { s/\r\n/\n/g } @data ;
		map { s/\r/\n/g   } @data ;
		
		untie @data ; close IN ;
		
	}
	
	sub set_timer{
		
			my ( $user, $system, $cuser, $csystem ) = times ;
	
print <<TIME;

			***  time used: $user sec  ***

TIME

		
	}
	
	sub translate_cut_positions {
		
		my $sref_command_codon_remove = $_[0] ;
		my $sref_command_third_remove = $_[1] ;
		my $aref_cut_positions        = $_[2] ;
		my $sref_number_characters    = $_[3] ;
		my $aref_remaining_positions  = $_[4] ;
		my $sref_sequence_state       = $_[5] ;
		my $sref_filename             = $_[6] ;
		
		
		# Translate identified RSS aminoacid positions to nucleotide triplet positions
		if ( $$sref_command_codon_remove =~ /yes/ && $$sref_command_third_remove =~ /no/){
			
			unless ( $$sref_sequence_state =~ /aa/ ){
				
				my @fasta_old = @$aref_cut_positions ; @$aref_cut_positions = ();
				for my $number( @fasta_old ){
					
					my $newno1 = ($number*3)-2;
					my $newno2 = $newno1+1;
					my $newno3 = $newno2+1;
					
					push @$aref_cut_positions, ( $newno1, $newno2, $newno3 )
				}
				
				my $string_cutnumbers = join " ",  @$aref_cut_positions ;
				open  OUTnewcut, ">ALICUT_cut_positions_codon.txt" or die "\n\t!FILE-ERROR!: Can not open File ALICUT_cut_positions_codon.txt" ;
				print OUTnewcut  $string_cutnumbers ; close OUTnewcut ;
			}
			
			else { warn "\n\t!FILE-WARN!: $$sref_filename include aa sequences!\n\tCodon positions not translated!" }
		}
		
		# Translate identified RSS aminoacid positions to nucleotide triplet positions, but remove only third position
		elsif ( $$sref_command_codon_remove =~ /yes/ && $$sref_command_third_remove =~ /yes/){
			
			unless ( $$sref_sequence_state =~ /aa/ ){
			
				my @fasta_old = @$aref_cut_positions ; @$aref_cut_positions = ();
				for my $number( @fasta_old ){ 
					
					push @$aref_cut_positions, ($number*3) 
				}
				
				my $string_cutnumbers = join " ",  @$aref_cut_positions ;
				open  OUTnewcut, ">ALICUT_cut_positions_codon_3rd.txt" or die "\n\t!FILE-ERROR!: Can not open File ALICUT_cut_positions_codon_3rd.txt" ;
				print OUTnewcut  $string_cutnumbers ; close OUTnewcut ;
			}
			
			else { warn "\n\t!FILE-WARN!: $$sref_filename include aa sequences!\n\tCodon positions not translated!\n\t3rd codon position not removed!" }
		}
		
		# Remove only identified RSS if third position of original sequence 
		elsif ( $$sref_command_codon_remove =~ /no/ && $$sref_command_third_remove =~ /yes/){
			
			unless ( $$sref_sequence_state =~ /aa/ ){
				
				my @fasta_old = @$aref_cut_positions ; @$aref_cut_positions = ();
				for my $number( @fasta_old ){
					
					if ( $number % 3 == 0 ){ push @$aref_cut_positions, $number }
				}
				
				my $string_cutnumbers = join " ",  @$aref_cut_positions ;
				open  OUTnewcut, ">ALICUT_cut_positions_3rd.txt" or die "\n\t!FILE-ERROR!: Can not open File ALICUT_cut_positions_3rd.txt" ;
				print OUTnewcut  $string_cutnumbers ; close OUTnewcut
			}
			
			else { warn "\n\t!FILE-WARN!: $$sref_filename include aa sequences!\n\tNot only 3rd codon position removed!" }
		}
		
		
		# Examine remaining positions
		my  ( %seen, @zahlenreihe ) ;
		for ( 1 .. $$sref_number_characters ) { push @zahlenreihe, $_-1 }
		
		for my $value ( @$aref_cut_positions ){ $seen{$value-1}++ }
		for           ( @zahlenreihe         ){ unless ( $seen{$_} ){ push @$aref_remaining_positions, $_ } }
	}
}

sub fas_bearbeiten{
	
	my @infile = @_                   ;
	
	grep  s/(\>.*)/$1\t/,     @infile ;
	grep  s/ //g,             @infile ;
	grep  s/\n//g,            @infile ;
	grep  s/\t/\n/g,          @infile ;
	grep  s/\>/\n\>/g,        @infile ;
	my $string = join "",     @infile ;
	@infile    = split "\n",  $string ;
	shift                     @infile ;
	return                    @infile ;
}

sub structure_handling{
	
	my $sref_string        = $_[0] ;
	my $sref_answer_remain = $_[1] ;
	my $aref_cut_positions = $_[2] ;
	my $sref_filename      = $_[3] ;
	
	my ( 
		
		@pair_infos            ,
		@forward               ,
		@structurestring       ,
		@loops                 ,
		@pairs                 ,
		%structure_of_position ,
		%seen_struc
		
	);
	
	
	# Stem assignment
	my @structures = split "", $$sref_string ;
	my  $i = 0                                                                                                         	                  ;
	CHECKING:
	for ( @structures ){ $i++                                                                                                             ;
		
		SWITCH:
		$structure_of_position{$i} = $_                                                                                                   ;
		
		if ( $_  =~ /\(/ ){ push @forward, $i                                                                          and next CHECKING  }
		if ( $_  =~ /\)/ ){ my $pair_1 = pop @forward; push @pairs, ( $pair_1, $i ); push @pair_infos, ( $pair_1.":".$i ); next CHECKING  }
		if ( $_  =~ /\./ ){ push @loops,   $i                                                                          and next CHECKING  }
	}
	
	@pair_infos  =  reverse @pair_infos                                                                                                   ;
	
	
	
	
	# Generate listfiles for structure_info file
	my $pairlist =  join "\n\t\t\t\t\t", @pair_infos   ;
	my $looplist =  join "\n\t\t\t\t\t", @loops        ;
	
	
	# Number and proportion of stem and loop positions for structure info file
	my $N_total  =  @structures                        ;
	my $N_stems  =  @pair_infos                        ;
	my $N_loops  =  $N_total - ( $N_stems * 2 )        ;
	my $P_loops  =  ( $N_loops / $N_total ) * 100      ;
	my $P_stems  =  100 - $P_loops                     ;

	
	# Open structure info outfile
	open OUTstruc, ">ALICUT_Struc_info_${$sref_filename}.txt"                                  ;
	
	# Print out
	print OUTstruc "\nOriginal structure information identified in $$sref_filename:\n\n"  ;
	print OUTstruc "- Number of characters:\t\t\t$N_total\n"                              ;
	print OUTstruc "- Number of single loop characters:\t$N_loops [$P_stems %]\n"         ;
	print OUTstruc "- Number of paired stem characters:\t$N_stems [$P_loops %]\n"         ;
	print OUTstruc "\n- Paired stem positions:\t\t$pairlist\n\n"                          ;
	print OUTstruc "\n- Loop positions:\t\t\t$looplist\n"                                 ;

	close OUTstruc;
	
	if  ( $$sref_answer_remain =~ /yes/i ){
		
		my @cut_positions2 = ();
		
		# Remain rss identified stem positions within the MSA
		for ( @pairs ){ $seen_struc{$_} = 1                                                   }
		for ( @$aref_cut_positions ){ unless ( $seen_struc{$_} ){ push @cut_positions2, $_  } }
		@$aref_cut_positions = @cut_positions2                                                ;
	}
	
	else{
		
		my %pair = @pairs;
		
		# Replace paired structure positions of rss identified positions by dots
		for my $bp_for ( keys %pair ){
			
			for my $rss ( @$aref_cut_positions ){
				
				if ( $bp_for        == $rss ){ $structure_of_position{$pair{$bp_for}}  = "." ; last }
				if ( $pair{$bp_for} == $rss ){ $structure_of_position{$bp_for}         = "." ; last }
			}
		}
	}
	
	for    ( my $k=1; $k<=@structures-1; $k++ ){ push @structurestring, $structure_of_position{$k}   }
	my     $structure_string_neu = join "", @structurestring                                       ;
	return $structure_string_neu                                                                   ;
	
}

sub commandline{

	print  "\n\tCOMMAND:\t "                                                          ;
	
	chomp ( my $sub_answer_opening = <STDIN> );

	print  "\n\t------------------------------------------------------------\n"        ;
	
	return $sub_answer_opening;
}	



















































