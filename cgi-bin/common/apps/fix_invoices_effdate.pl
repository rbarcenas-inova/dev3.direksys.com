#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Find;
use XML::Simple;
use Data::Dumper;

local ($dir) = getcwd;
local ($in{'e'}) = 3;
local ($in{'d'}) = 0;
local ($in{'f'}) = 0;
local ($usr{'id_admin_users'}) = 1;

chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
};
if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

#################################################################
#################################################################
#	Function: main
#
#   		Main function: Calls execution scripts. Script called from cron task
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By:
#
#
#   	Parameters:
#
#
#   	Returns:
#
#
#
#   	See Also:
#
sub main {
#################################################################
#################################################################

	$|++;
	&connect_db;

	#######
	####### Leemos la ruta actual y reconstruimos la ruta al directorio base
	#######
	my ($a,$b) = split(/cgi-bin/, $dir);
	my $this_dir = $a . 'files/e' . $in{'e'} . '/cfdi/xml';

	#######
	####### Leeamos recursivamente todo el contenido y lo procesamos
	####### 
	print "Leyendo Datos dentro de $this_dir\n";
	# Traverse desired filesystems
	find(\&process_invoices, $this_dir);


	&disconnect_db;
	exit;

}


#############################################################################
#############################################################################
#   Function: process_invoices
#
#       Es: Lee archivo xml y extrae informacion para actualizar la base de datos con informacion faltante
#       En: 
#
#    Created on: 04/12/2013  16:21:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters: 
#
#		$file : Contiene el archivo xml a procesar
#
#
#  Returns:
#
#
#   See Also:
#
#
sub process_invoices {
#############################################################################
#############################################################################
	
 	my $file = $_;
 	return if $file eq '.';
 	return if $file eq '..';

    if (-d $file){

    	####
    	#### Directorio  (No se procesan)
    	####
    	++$in{'d'};
    	print "$in{'d'} . Entrando en carpeta $file\n";

    }elsif(-f $file and -s $file){

    	return if $file !~ /xml$|XML$/;

    	###
    	### Archivo (A procesar xml)
    	###

    	++$in{'f'};
    	print "    $in{'f'} . Factura $file\n";

    	#####
		##### doc_serial , doc_num
		my @ary_name = split(/_/, $file);
		my $doc_serial = $ary_name[0];
		my $doc_num = int($ary_name[1]);

    	# create object
		my $xml = new XML::Simple;

		# read XML file
		my $data = $xml->XMLin($file);
		
		# print output
		my $adate = Dumper($data->{'cfdi:Complemento'}->{'tfd:TimbreFiscalDigital'}->{'FechaTimbrado'});
		my $auid = Dumper($data->{'cfdi:Complemento'}->{'tfd:TimbreFiscalDigital'}->{'UUID'});
		my $edate = Dumper($data->{'fecha'});

		my $fis_date = $adate ne '' ? substr($adate,9,10) : '';
		my $emi_date = $edate ne '' ? substr($edate,9,10) : 'N/A';
		my $uuid =  $auid ne '' ? substr($auid,9,-3) : '';

		my $updated = 'ERROR1';
		my $query = "UPDATE cu_invoices SET xml_uuid = '$uuid', xml_fecha_emision = '$emi_date', xml_fecha_certificacion = '$fis_date' WHERE doc_serial = '$doc_serial' AND doc_num = '$doc_num' /*AND xml_fecha_emision IS NULL AND xml_fecha_certificacion IS NULL*/;";
		my $query2 = "SELECT doc_serial, doc_num xml_uuid, xml_fecha_emision, xml_fecha_certificacion FROM cu_invoices WHERE doc_num = '$doc_num';";

		if($fis_date ne '' and $uuid ne ''){

			my ($sth) = &Do_SQL($query);
			my ($res) = $sth->rows();

			if(!$res){

				######
				###### 1) Comprobamos si ya tiene datos
				######

				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM cu_invoices WHERE doc_serial = '$doc_serial' AND doc_num = '$doc_num' AND xml_fecha_emision IS NOT NULL;");
				$res = $sth2->fetchrow();
			}

			$updated = $res > 0 ? 'OK1' : 'ERROR2' ;

		}

		print "               FechaTimbrado: $fis_date\n";
		print "               FechaEmision: $emi_date\n";
		print "               Sello: $uuid\n";
		print "               Serie: $doc_serial\n";
		print "               Num: $doc_num\n";
		print "               Query: $query\n";
		print "               Updated: $updated\n";
		print "               Select: $query2\n" if $updated ne 'OK1';

    }


    return;
}



##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
	my (@sys_err) = @_;

	print "\nCGI ERROR\n==========================================\n";
	$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
	$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
	$sys_err[2]	and print "System Message      : $sys_err[2]\n";
	$0			and print "Script Location     : $0\n";
	$]			and print "Perl Version        : $]\n";
	$sid		and print "Session ID          : $sid\n";
	
	exit -1;
}
