#!/usr/local/bin/perl

#use strict;
#use warnings;
use diagnostics;
use CGI ':standard';

use lib "GO_TermFinder/lib";
use GO::TermFinder;
use GO::AnnotationProvider::AnnotationParser;
use GO::OntologyProvider::OntologyParser;
use Spreadsheet::WriteExcel;

    print header;
    print start_html('GO Term Finder Results');
    print "<PRE>";

# Create a new workbook called results.xls and add a worksheet
    my $workbook  = Spreadsheet::WriteExcel->new("data/output/results.xls");
    my $worksheet = $workbook->add_worksheet();
    $worksheet->set_column(0, 0, 12);
    $worksheet->set_column(1, 1, 25);
    $worksheet->set_column(4, 5, 15);
    my $format01 = $workbook->add_format();
    $format01->set_num_format('0.00000');
    my $format02 = $workbook->add_format();
    $format02->set_num_format('0.0000E+00');

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
    open(ONTO,$ontologyFile)||print "open error";
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
    close (ONTO)||print "close error";

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
    my $numGenes = 34011;

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
    if (/[ \t]/) {
	s/[ \t]//g;
	}	
#change PC endlines (return, endline) to endline
    if (/\r\n/) {
	s/\r\n/\n/g;
	}
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

    my $ontology   = GO::OntologyProvider::OntologyParser->new(ontologyFile=>$ontologyFile);

    my $annotation = GO::AnnotationProvider::AnnotationParser->new(annotationFile=>$annotationFile);

    my $termFinder = GO::TermFinder->new(annotationProvider=> $annotation,
				     ontologyProvider  => $ontology,
				     totalNumGenes     => $numGenes,
				     aspect            => $aspect);

    my @pvalues    = $termFinder->findTerms(genes=>\@genes);

# now just print the info back to the client

    print "<b>GOID\t\tGO_term\t\t\t\tFrequency\t\t\tGenome frequency\t\t\t\tP-value\tCorrected P-value\tGene(s)\tDirectly Annotated GOID list</b>\n";
    my $print_line = 0;
    my $skip_lines = 7;

# write header row for excel output
    $worksheet->write($skip_lines, 0, 'GOID');
    $worksheet->write($skip_lines, 1, 'GO_term');
    $worksheet->write($skip_lines, 2, 'Frequency');
    $worksheet->write($skip_lines, 3, 'Genome frequency');
    $worksheet->write($skip_lines, 4, 'P-value');
    $worksheet->write($skip_lines, 5, 'Corrected P-value');
    $worksheet->write($skip_lines, 6, 'Gene(s)');

    my $ex_gene = "";
    my $hypothesis = 1;

# get count of genes with no errors -- use count to top node Gene_ontology GO:0003673
    foreach my $pvalue (@pvalues){
	if ($pvalue->{NODE}->goid eq "GO:0003673") {
	$count = $pvalue->{NUM_ANNOTATIONS};
	}
    }

    foreach my $pvalue (@pvalues){
    $ex_gene = "";   
# For web version report all nodes
#    next if ($pvalue->{CORRECTED_PVALUE} > 0.001); 
    $print_line = 1;

print $pvalue->{NODE}->goid, "\t";
printf "%-25.25s",($pvalue->{NODE}->term);
print "\t";
printf "%1.5f", (($pvalue->{NUM_ANNOTATIONS})/$count);
print " (";
printf "%5d", ($pvalue->{NUM_ANNOTATIONS});
print " of ";
printf "%5d", $count;
print " genes )\t ";
printf "%1.5f", (($pvalue->{TOTAL_NUM_ANNOTATIONS})/$numGenes);
print " (";
printf "%5d", ($pvalue->{TOTAL_NUM_ANNOTATIONS});
print " of ";
printf "%5d", $numGenes;
print " annotated genes )\t "; 
printf "%1.3e", ($pvalue->{PVALUE});
print "\t";
printf "%1.3e", ($pvalue->{CORRECTED_PVALUE});
print "\t";

foreach my $gene (values (%{$pvalue->{ANNOTATED_GENES}})) {
    $ex_gene = $ex_gene . $gene . ",";
    if (substr($gene,0,4) eq "MGI:") {
    print "<a href=\"http://www.informatics.jax.org/searches/accession_report.cgi?id=", $gene, "\">", $gene, "</a>, ";
    }
else
{
    print "<a href=\"http://www.informatics.jax.org/javawi/servlet/SearchTool?query=", $gene, "&selectedQuery=Genes+and+Markers\">", $gene, "</a>, ";
}
}

print br;

my $excel_line = $skip_lines + $hypothesis;
$worksheet->write($excel_line, 0, $pvalue->{NODE}->goid);
$worksheet->write($excel_line, 1, $pvalue->{NODE}->term);
$worksheet->write($excel_line, 2, ($pvalue->{NUM_ANNOTATIONS})/$count, $format01);
$worksheet->write($excel_line, 3, ($pvalue->{TOTAL_NUM_ANNOTATIONS})/$numGenes, $format01);
$worksheet->write($excel_line, 4, $pvalue->{PVALUE}, $format02);
$worksheet->write($excel_line, 5, $pvalue->{CORRECTED_PVALUE}, $format02);
$worksheet->write($excel_line, 6, $ex_gene);

    $hypothesis++;
    
}

##if no nodes meet significance criterion print that
    if ($print_line == 0) {
    print "No significant nodes found.",br;
    }
print br;


# Write some hyperlinks
#$worksheet->write('A30', 'http://www.perl.com/', 'Perl home'   );

#print "<a href=\"http://devwww/~mdolan/GoTools/cgi-bin/results.xls\">To download as an Excel file, right click and \"Save Link As...\"</a>";
print "<a href=\"./data/output/results.xls\">To download as an Excel file, right click and \"Save Link As...\"</a>";
print "</PRE>",br;

end_html;
