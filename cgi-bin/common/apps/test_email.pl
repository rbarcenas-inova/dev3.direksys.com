#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

#use strict;
#use Perl::Critic;
use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
# use File::Copy;

# local ($dir) = getcwd;
# Default la 2 porque este proceso fue diseñado para TMK
local(%in) = &parse_form;
# local ($in{'e'}) = 2 if (!$in{'e'});
# chdir($dir);

# Required Libraries
# --------------------------------------------------------
eval {
	require ('../subs/auth.cgi');
	require ('../subs/sub.base.html.cgi');
	require ('../subs/sub.func.html.cgi');
	require ('../subs/libs/lib.orders.pl');
	require ('cybersubs.cgi');
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
#	Modified By: Alejandro Diaz
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
	&execute_outsourcing_batch;
	&disconnect_db;

}


#################################################################
#################################################################
#	Function: execute_outsourcing_batch
#
#   		This functions reads from several outsourcing callcenters /home/ccname/orders paths. The file inside contains orders created by Listen Up Callcenter to be processed in Direksys. The script validate and create every order and send them to authorize if necessary
#
#	Created by: _Roberto Barcenas_
#
#
#	Modified By:Alejandro Diaz
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
sub execute_outsourcing_batch{
#################################################################
#################################################################
	my $process = ($in{'process'} ne 'commit')? qq|<span style="color:#000;background-color:gray;padding:5px;">ANALYZING</span>|:qq|<span style="color:#FFF;background-color:red;padding:5px;">EXECUTING</span>|;
	my $log_email;

	&load_settings;
	print "Content-type: text/html\n\n";
	print qq|<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n\n|;
	print "<h4>DIREKSYS $cfg{'app_title'} (e$in{'e'}) - TEST EMAIL SEND $process</h5>";
	
	if (!$in{'e'}){
		print qq|<span style="color:red;">ID de empresa es requerido</span>|;
		return;
	}
	
	$id_orders = ($in{'id_orders'})?$in{'id_orders'}:'9000479';
	$id_customers = (&load_name('sl_orders','ID_orders',$id_orders,'id_customers'));

	$va{'id_orders'} = $id_orders;
	$va{'name'} = lc(&load_name('sl_customers','ID_customers',$id_customers,'FirstName'));
	$va{'shp_name'} = lc(&load_name('sl_orders','ID_orders',$id_orders,'shp_name'));
	$va{'shp_address'} = lc(&load_name('sl_orders','ID_orders',$id_orders,"CONCAT(shp_Address1,',  ',shp_Address2,' y ',shp_Address3)"));
	$va{'shp_urbanization'} =  lc(&load_name('sl_orders','ID_orders',$id_orders,'shp_urbanization'));
	$va{'shp_city'} =  lc(&load_name('sl_orders','ID_orders',$id_orders,'shp_city'));
	$va{'shp_state'} = lc(&load_name('sl_orders','ID_orders',$id_orders,'shp_state')); 
	$va{'shp_zip'} = &load_name('sl_orders','ID_orders',$id_orders,'shp_zip');
	$va{'shpdate'} = $shpdate; 
	$va{'tracking'} = $tracking;
	$va{'shpprovider'} = '('.$provider.')';
	$va{'cservice_phone'} = $cfg{'cservice_phone'};
	$ptype = lc(&load_name('sl_orders','ID_orders',$id_orders,'Ptype'));
	$va{'total'} =  &format_price(&total_orders_products($id_orders));

	if ($ptype eq 'cod'){
		$va{'htmlcod'} = qq|
		<div style="border:2px solid #378de8; background-color:#e4f1ff; padding:15px;-moz-border-radius: 5px; border-radius: 5px;text-align:center;"><font   face="century gothic, verdana" size=4>
			<font color=#378de8><b>COD (Cash On Delivery)</b></font><br>
			Favor de tener listo el pago de:<br>
			<b>$va{'total'} </b>
		</font> 
		</div>
		<br><br>|;
	}

	if ($va{'tracking'} == 'DRIVER'){
		$va{'shpprovider'} = '';
		$va{'tracking'}  = '';
	}

	my ($from_email) = $cfg{'from_email'};
	my ($to_email) = ($cfg{'mandrillapp_test_to'})?$cfg{'mandrillapp_test_to'}:'adiaz@inovaus.com';
	my $subject = "Tu pedido esta en camino $id_orders";
	$body = &build_page('mod/wms/emails/default.html');
	print qq|ptype=$ptype<br>|;
	print qq|total=$total<br>|;
	print qq|from_email=$from_email<br>|;
	print qq|to_email=$to_email<br>|;
	print qq|subject=$subject<br>|;
	print qq|body=$body<br>|;


	if ($in{'process'} eq 'commit'){

		my $res = &send_mandrillapp_email($from_email,$to_email,$subject,$body,$body,'none');

		print "Enviando correo: $res->{'status'}<br>";
	}

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

sub load_settings {
	my ($fname);
	
	if ($in{'e'}) {
		$fname = "../general.e".$in{'e'}.".cfg";
	}else {
		$fname = "../general.ex.cfg";
	}

	## general
	open (CFG, "<$fname") or &cgierr ("Unable to open: $fname,160,$!");
	LINE: while (<CFG>) {
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		$line = $_;
		$line =~ s/\n|\r//g;
		my ($td,$name,$value) = split (/\||\=/, $line,3);
		if ($td eq "conf") {
			$cfg{$name} = $value;
			next LINE;
		}elsif ($td eq "sys"){
			$sys{$name} = $value;
			next LINE;
		}
	}
	close CFG;

}

sub validate_state_zipcode{
	my ($orig_zipcode,$orig_state) = @_;
	&Do_SQL("SET NAMES utf8");
	$sql = "SELECT ZipCode, StateFullName FROM sl_zipcodes WHERE Status='Active' AND zipcode='$orig_zipcode' AND StateFullName='$orig_state' GROUP BY ZipCode, StateFullName";
	my $sth = &Do_SQL($sql);
	my ($zipcode,$state) = $sth->fetchrow_array();

	if ( lc($state) eq lc($orig_state) ){
		return 0;
	}else{
		return "BD=$state != LO=$orig_state";
	}
}

sub parse_form {
# --------------------------------------------------------
	my (@pairs, %in);
	my ($buffer, $pair, $name, $value);

	if ($ENV{'REQUEST_METHOD'} eq 'GET') {
		@pairs = split(/&/, $ENV{'QUERY_STRING'});
	}elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
 		@pairs = split(/&/, $buffer);
	}else {
		&cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
	}
	PAIR: foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);

		$name =~ tr/+/ /;
		$name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$name = lc($name);

		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		$value =~ s/^\s+//g;
		$value =~ s/\s+$//g;

		#$value =~ s/\r//g;
		$value =~ s/<!--(.|\n)*-->//g;			# Remove SSI.
		if ($value eq "---") { next PAIR; }		# This is used as a default choice for select lists and is ignored.
		(exists $in{$name}) ?
			($in{$name} .= "|$value") :		# If we have multiple select, then we tack on
			($in{$name}  = $value);			# using the ~~ as a seperator.
	}
	return %in;
}

sub print_query{
	my ($sql) = @_;
	print qq|<div style="border:solid 1px #666;padding:3px;"><span style="font-size:10px;color:#0099FF;">$sql</span></div>|;
}