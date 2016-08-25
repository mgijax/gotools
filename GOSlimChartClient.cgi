#!/usr/bin/perl

#use strict;
#use warnings;
use diagnostics;
use CGI ':standard';

use lib "lib";
use GO::TermFinder;
use GO::AnnotationProvider::AnnotationParser;
use GO::OntologyProvider::OntologyParser;
use Spreadsheet::WriteExcel;
use Set::Scalar;

    print header;
    print start_html('GO_Slim Chart Results');
    print "<PRE>";

# Create a new workbook called results.xls and add a worksheet
    my $workbook  = Spreadsheet::WriteExcel->new("data/output/results.xls");
    my $worksheet = $workbook->add_worksheet();

# set ontology file and aspect
    my $ontology = param('ontology');
    $ontologyFile = "data/input/".$ontology.".ontology";
    my $aspect = substr $ontology,0,1;
    $_ = $aspect;
    s/c/C/;
    s/f/F/;
    s/p/P/;
    $aspect = $_;

#get version information for ontology file
    open(ONTO,$ontologyFile)||print "ONTO open error";
    my $line;
    	$line = <ONTO>;		##skip line 1
    	$line = <ONTO>;		##skip line 2
    	$line = <ONTO>;		##date info on line 3
	print "Ontology version\n";
# write ontology info for excel output
    $worksheet->write(0, 0, 'Ontology version');
	print $line;
    $worksheet->write(1, 0, $line);
    	$line = <ONTO>;		##version info on line 4
	print $line;
    $worksheet->write(2, 0, $line);
    close (ONTO)||print "ONTO close error";

#read in GO bins for chart selection
    my $binsFile = "data/input/".$ontology."_GO_Bins.txt";
    open (GO_BINS, "$binsFile")||print "GO_BINS open error";
    my @bins;
    while (<GO_BINS>) {
	chomp;
	push (@bins, $_);
	}
    close (GO_BINS)||print "GO_BINS close error";

#read in MGI summary
    my $mgiallFile = "data/input/allmgi_".$ontology.".txt";
    open (MGI_ALL, "$mgiallFile")||print "GO_BINS open error";
    my %mgiall;
    while (<MGI_ALL>) {
	chomp;
	/([\w \/\-,]*)\t(\d*)/;
	$bin_name=$1;
	$bin_count=$2;
	$mgiall{$bin_name} = $bin_count;
	#print "Mgi all counts: ", $bin_name, " ", $bin_count, " ", $mgiall{$bin_name}, "\n";
	}
	$mgiall{'all'} = $bin_count;
    close (MGI_ALL)||print "MGI_ALL close error";

# set annotations file
#default: include IEA evidence codes
    my $annotationFile = "data/input/gene_association.mgi";
    if (param('iea') eq "exclude") {
    $annotationFile = "data/input/gene_association_noIEA.mgi";
    }

#get version information for associations file
    open (ANNOT,$annotationFile) ||print "open error";
	print "Annotations version\n";
    $worksheet->write(3, 0, 'Annotations version');
    	$line = <ANNOT>;	##version info on line 1
	print $line;
    $worksheet->write(4, 0, $line);
    	$line = <ANNOT>;	##date info on line 2
	print $line;
    $worksheet->write(5, 0, $line);
    close (ANNOT) ||print "close error";

    print "\nAny warnings will be listed here:\n";
# set number of genes
    my $numGenes = 30000;

#genes in textarea or file?
    my @genes;
    my $count = 0;
    my $mac_line;

#textarea with genes
    if (param('loci')) { 

    foreach $line ( split(/\n/, param('loci')) ) {
	$count++;
	push (@genes, $line);
	}
    }

# upload file with genes
    if (param('uploadfile')) {
    my $file = param('uploadfile');
    while (<$file>) {
    $count++;
# get rid of spaces, tabs
	s/[ \t]//g;
#change PC endlines (return, endline) to endline
	s/\r\n/\n/g;
    chomp;
    push (@genes, $_);
##include this in case file has mac endlines \r which cause entirefile to be read as one line
    $mac_line=$_;
    }

#check for mac endline (return) -- if found need to reparse file
    $_=$mac_line;
	if (/\r/) {
	@genes = "";
	foreach $line ( split(/\r/) ) {
	    $count++;
	    push (@genes, $line);
	    }
	$count = $count-1;
	}

    close $file;
    }

	my $full_gene_set = Set::Scalar->new;
	$full_gene_set = Set::Scalar->new(@genes);

    $ontology   = GO::OntologyProvider::OntologyParser->new(ontologyFile=>$ontologyFile);

    my $annotation = GO::AnnotationProvider::AnnotationParser->new(annotationFile=>$annotationFile);

    my $termFinder = GO::TermFinder->new(annotationProvider=> $annotation,
				     ontologyProvider  => $ontology,
				     totalNumGenes     => $numGenes,
				     aspect            => $aspect);

    my @pvalues    = $termFinder->findTerms(genes=>\@genes);

# look for nodes corresponding to bins

#    print "GO ID for bin\tGO term\t\t\tCount for bin\tAnnotated genes\n";
    my $ex_gene = "";
    my $hypothesis = 1;
   
    my %go_bins;
    $count = 0;
    foreach my $bin (@bins) {
	$go_bins{$bin} = Set::Scalar->new;
        foreach my $pvalue (@pvalues){
            $ex_gene = ""; 
            if ($bin eq $pvalue->{NODE}->goid) {
                #print $pvalue->{NODE}->goid, "\t";    
                #printf "%-25.25s",($pvalue->{NODE}->term);
                #print "\t"; 
                #printf "%5d", ($pvalue->{NUM_ANNOTATIONS});
                #print "\t\t";
                #print join(", ", values (%{$pvalue->{ANNOTATED_GENES}})), "\n";
	        $go_bins{$bin} = Set::Scalar->new(values (%{$pvalue->{ANNOTATED_GENES}}));
            }
        }
    }

    my $skip_lines = 8;
# write header row for excel output
    $worksheet->write($skip_lines, 1, 'Count');
    $worksheet->write($skip_lines, 2, 'Percentage');
    $worksheet->write($skip_lines, 3, 'All MGI');

#initialize bins
	my $one = Set::Scalar->new;
	my $two = Set::Scalar->new;
	my $three = Set::Scalar->new;
	my $four = Set::Scalar->new;
	my $five = Set::Scalar->new;
	my $six = Set::Scalar->new;
	my $seven = Set::Scalar->new;
	my $eight = Set::Scalar->new;
	my $nine = Set::Scalar->new;
	my $ten = Set::Scalar->new;
	my $eleven = Set::Scalar->new;
	my $twelve = Set::Scalar->new;
	my $thirteen = Set::Scalar->new;
	my $fourteen = Set::Scalar->new;
	my $fifteen = Set::Scalar->new;
	my $sixteen = Set::Scalar->new;

if ($aspect eq "P") {
#biological process bins
#set up bins
	$one = $go_bins{'GO:0007155'};
	$two = $go_bins{'GO:0007267'};
	$three = $go_bins{'GO:0007049'} + $go_bins{'GO:0008283'};
	$four = $go_bins{'GO:0016265'};
	$five = $go_bins{'GO:0016043'};
	$six = $go_bins{'GO:0019538'};
	$seven = $go_bins{'GO:0006259'};
	$eight = $go_bins{'GO:0016070'} + $go_bins{'GO:0006350'};
	$nine = $go_bins{'GO:0008152'} - ($seven + $go_bins{'GO:0016070'} + $six);
	$ten = $go_bins{'GO:0006950'};
	$eleven = $go_bins{'GO:0006810'};
	$twelve = $go_bins{'GO:0007275'};
	$thirteen = $go_bins{'GO:0007165'};
	$fourteen = $go_bins{'GO:0000004'};
	$sixteen = $full_gene_set;
	$fifteen = $sixteen - ($one + $two + $three + $four + $five + $six + $seven + $eight + $nine + $ten + $eleven + $twelve + $thirteen + $fourteen);

    print "\n<b>Results for Biological Process Bins: \n";
    print "Process\t\t\t\tCount\tPercentage\tAll MGI</b>\n";
    $worksheet->write($skip_lines-1, 0, 'Results for Biological Process Bins:');
    $worksheet->write($skip_lines, 0, 'Process');

#print bin results
$label="cell adhesion";
$set=$one;
$group=$sixteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+1);

$label="cell-cell signaling";
$set=$two;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+2);

$label="cell cycle and proliferation";
$set=$three;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+3);

$label="death";
$set=$four;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+4);

$label="cell organization and biogenesis";
$set=$five;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+5);

$label="protein metabolism";
$set=$six;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+6);

$label="DNA metabolism";
$set=$seven;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+7);

$label="RNA metabolism";
$set=$eight;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+8);

$label="other metabolic processes";
$set=$nine;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+9);

$label="stress response";
$set=$ten;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+10);

$label="transport";
$set=$eleven;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+11);

$label="developmental processes";
$set=$twelve;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+12);

$label="signal transduction";
$set=$thirteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+13);

$label="unknown biological processes";
$set=$fourteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+14);

$label="other biological processes";
$set=$fifteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+15);

$label="all biological processes";
$set=$sixteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+16);
}
#end of biological process section

if ($aspect eq "C") {
#cellular component bins
#set up bins

	$two = $go_bins{'GO:0005576'};
	$one = $go_bins{'GO:0005578'} - $two;
	$three = $go_bins{'GO:0005886'};
	$four = $go_bins{'GO:0016020'} + $go_bins{'GO:0005624'} - $three;
	$five = $go_bins{'GO:0005829'} + ($go_bins{'GO:0016528'} -  ($go_bins{'GO:0016529'} + $go_bins{'GO:0030314'}));
	$six = $go_bins{'GO:0005856'} + $go_bins{'GO:0005815'} + $go_bins{'GO:0005819'} + $go_bins{'GO:0030484'} + $go_bins{'GO:0009434'};
	$seven = $go_bins{'GO:0005739'};
	$eight = $go_bins{'GO:0005783'} + $go_bins{'GO:0005793'} + $go_bins{'GO:0005794'} + $go_bins{'GO:0030133'} + $go_bins{'GO:0005798'};
	$nine = $go_bins{'GO:0016282'} + $go_bins{'GO:0016283'} + $go_bins{'GO:0005851'} + $go_bins{'GO:0016281'} + $go_bins{'GO:0005854'} + $go_bins{'GO:0005855'} + $go_bins{'GO:0005840'};
	$ten = $go_bins{'GO:0005634'};
	$eleven = $go_bins{'GO:0020022'} + $go_bins{'GO:0000177'} + $go_bins{'GO:0005768'} + $go_bins{'GO:0009514'} + $go_bins{'GO:0005764'} + $go_bins{'GO:0005777'} + $go_bins{'GO:0005773'};
	$twelve = $go_bins{'GO:0008372'};
	$fourteen = $full_gene_set;
	$thirteen = $fourteen - ($one + $two + $three + $four + $five + $six + $seven + $eight + $nine + $ten + $eleven + $twelve);

    print "\n<b>Results for Cellular Component Bins: \n";
    print "Component\t\t\t\tCount\tPercentage\tAll MGI</b>\n";
    $worksheet->write($skip_lines-1, 0, 'Results for Cellular Component Bins:');
    $worksheet->write($skip_lines, 0, 'Component');

$label="non-structural extracellular";
$set=$one;
$group=$fourteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+1);

$label="extracellular matrix";
$set=$two;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+2);

$label="plasma membrane";
$set=$three;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+3);

$label="other membranes";
$set=$four;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+4);

$label="cytosol";
$set=$five;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+5);

$label="cytoskeleton";
$set=$six;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+6);

$label="mitochondrion";
$set=$seven;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+7);

$label="ER/Golgi";
$set=$eight;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+8);

$label="translational apparatus";
$set=$nine;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+9);

$label="nucleus";
$set=$ten;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+10);

$label="other cytoplasmic organelle";
$set=$eleven;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+11);

$label="unknown cell component";
$set=$twelve;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+12);

$label="other cell component";
$set=$thirteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+13);

$label="all cell component";
$set=$fourteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+14);

}
#end of cellular component section

if ($aspect eq "F") {
#molecular function bins
#set up bins

	$one = $go_bins{'GO:0004871'} + $go_bins{'GO:0005102'};
	$two = $go_bins{'GO:0005215'};
	$three = $go_bins{'GO:0030234'};
	$four = $go_bins{'GO:0005201'};
	$five = $go_bins{'GO:0008147'} + $go_bins{'GO:0030345'} + $go_bins{'GO:0030280'};
	$six = $go_bins{'GO:0005200'} + $go_bins{'GO:0008092'} + $go_bins{'GO:0003774'};
	$seven = $go_bins{'GO:0030528'};
	$eight = $go_bins{'GO:0043023'} + $go_bins{'GO:0043024'} + $go_bins{'GO:0043022'} + $go_bins{'GO:0030533'};
	$nine = $go_bins{'GO:0003754'} + $go_bins{'GO:0030188'};
	$ten = $go_bins{'GO:0003676'};
	$eleven = $go_bins{'GO:0016301'};
	$twelve = $go_bins{'GO:0005554'};
	$fourteen = $full_gene_set;
	$thirteen = $fourteen - ($one + $two + $three + $four + $five + $six + $seven + $eight + $nine + $ten + $eleven + $twelve);

    print "\n<b>Results for Molecular Function Bins: \n";
    print "Function\t\t\t\tCount\tPercentage\tAll MGI</b>\n";
    $worksheet->write($skip_lines-1, 0, 'Results for Molecular Function Bins:');
    $worksheet->write($skip_lines, 0, 'Function');

$label="signal transduction activity";
$set=$one;
$group=$fourteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+1);

$label="transporter activity";
$set=$two;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+2);

$label="enzyme regulator activity";
$set=$three;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+3);

$label="extracellular structural activity";
$set=$four;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+4);

$label="bone, tooth or skin structural activity";
$set=$five;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+5);

$label="cytoskeletal activity";
$set=$six;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+6);

$label="transcription regulatory activity";
$set=$seven;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+7);

$label="translation activity";
$set=$eight;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+8);

$label="chaperone-related activity";
$set=$nine;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+9);

$label="nucleic acid binding activity";
$set=$ten;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+10);

$label="kinase activity";
$set=$eleven;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+11);

$label="unknown molecular function";
$set=$twelve;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+12);

$label="other molecular function";
$set=$thirteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+13);

$label="all molecular function";
$set=$fourteen;
$skip_lines++;
&print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines+14);

}
#end of molecular function section

print br;
# Write some hyperlinks
#$worksheet->write('A30', 'http://www.perl.com/', 'Perl home'   );

#print "<a href=\"http://devwww/~mdolan/GoTools/cgi-bin/results.xls\">To download as an Excel file, right click and \"Save Link As...\"</a>";
print "<a href=\"./data/output/results.xls\">To download as an Excel file, right click and \"Save Link As...\"</a>";
print "</PRE>",br;

end_html;

sub print_line($label, $set, $group, %mgiall, $worksheet, $skip_lines)
{
printf "%-25.25s",$label;
print "\t";
printf "%5d", $set->size;
print "\t";
printf "%1.5f", ($set->size/$group->size);
print "\t\t";
printf "%5d", $mgiall{$label};
print "\t";
printf "%1.5f", ($mgiall{$label}/$mgiall{'all'});
print "\n";
    $worksheet->write($skip_lines, 0, $label);
    $worksheet->write($skip_lines, 1, $set->size);
    $worksheet->write($skip_lines, 2, ($set->size/$group->size));
    $worksheet->write($skip_lines, 3, $mgiall{$label});
    $worksheet->write($skip_lines, 4, ($mgiall{$label}/$mgiall{'all'}));
#print GO_BINS_OUT "\t", $set, "\n";
}
