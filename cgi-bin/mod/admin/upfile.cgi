#!/usr/bin/perl

#######################################################################
#######################################################################
#######################################################################
use CGI qw/:standard :html3/;
use DBI;
use DBIx::Connector;
use DBD::mysql;


# Load the form information and set the config file and userid.
local(%in) = &parse_form;
local($sid,%error,%va,%trs,%perm);
local ($upload_dir) = "uploads/";
local ($temp_file) = "tempexp.csv";
local ($err_file) = "temperr.csv";

$in{'sid'} ? ($sid   = $in{'sid'}): ($sid   = '');

# Required Libraries
# --------------------------------------------------------
eval {
	require ("../common/subs/auth.cgi");
	require ("../common/subs/sub.base.html.cgi");
	require ("upfile.cfg");
};
if ($@) { &cgierr ("Error loading required libraries,100,$@"); }

eval { &main; };
if ($@) { &cgierr("Fatal error,501,$@ $!"); }

exit;

sub main {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	$|++;
	&connect_db;
	&auth_cleanup;
	my ($status) = &auth_check_password;
	$in{'sit_app'} = 'upfile_';
	if ($in{'cmd'}eq'mer_prototypes'){
		&prototypes_upload;
	}elsif($in{'app'} and "application"){
		&html_upload;		
	}elsif($in{'app'} and "imgman"){
		&html_imgman;
	}else{
		&html_message;
	}
}

################################################################
##################  PHONE LIST #################################
################################################################

sub html_phonelist {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){
		if (!$in{'ftype'}){
			&html_phonelist_home(&trans_txt('filetype_required'));
		}else{
			&html_phonelist_start;
		}
	}elsif($in{'fieldsorder'} !~ /Phone/){
		&html_message(&trans_txt('invalid_fields'));
	}else{
		##### Upload Data ######
		my $file = param('file');
		if (open (SAVE,">$cfg{'auth_dir_filetemp'}$sid.txt")){
			while ($size = read($file,$data,1024)) {
				print SAVE $data;
				$total_size += $size;
			}
			close SAVE;
			&html_phonelist_home(&trans_txt('upfile_ok'));
		}else{
			&html_message(&trans_txt('upfile_err'));
		}		
	}
}

sub html_phonelist_home {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	$va{'message'} = @_[0];
	$va{'invars'} .= qq|<input type="hidden" name="action" value="1">\n|;
	foreach $key (keys %in){
		$va{'invars'} .= qq|<input type="hidden" name="$key" value="$in{$key}">\n|;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('upfile:phonelist_message.html');
}

sub html_phonelist_start {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	#print header();
	print "Content-type: text/html\nKeep-Alive: 100\n\n";
	print qq|<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">
		<html>
			<head>
			<title>Status</title>
        <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
 	    	<link REL="STYLESHEET" HREF="$va{'imgurl'}/$usr{'pref_style'}/main.css" TYPE="text/css">
      </head>
			<body topmargin='2' leftmargin='4' bgcolor='#f4f4f1'>\n|;
	if (open (UPFILE,"<$cfg{'auth_dir_filetemp'}$sid.txt")){
		my (%ccar) = ('comma' => ',', 'tab' => "\t" , 'pipe' => '|' , 'space' => ' ', 'semicolon' => ';');
		my ($line,@ary,$phone,$query);
		my (@cols) = split(/\|/,$in{'fieldsorder'});
		my ($colslen) = $#cols;
		for(0..$#cols){
			if ($cols[$_] eq 'Phone'){
				$phone = $_;
			}
		}
		LINE: while (<UPFILE>) {
			(/^#/)    and next LINE;
			(/^\s*$/) and next LINE;
			$line = $_;
			$line =~ s/\n|\r//g;
			@ary = split(/$ccar{$in{'ftype'}}/,$line);
			if ($colslen ne $#ary){
				print "<span class='smalltext'>$ary[$phone] : ".&trans_txt('uploaded_invalid')."</span><br>";
			}else{
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM ccd_callers WHERE Phone='$ary[$phone]';");
				if ($sth->fetchrow()>0){
					print "<span class='smalltext'>$ary[$phone] : ".&trans_txt('uploaded_repeted')."</span><br>";
				}else{
					print "<span class='smalltext'>$ary[$phone] : ".&trans_txt('uploaded_added')."</span><br>";
					$query = "Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}',ID_campaigns='$in{'id_campaigns'}'";
					for (0..$colslen){
						$query .= ",$cols[$_]='".&filter_values($ary[$_])."'";
					}
					my ($sth) = &Do_SQL("INSERT INTO ccd_callers SET $query;");
				}
			}
		}
	}
	print "<span class='stdtxterr'>".&trans_txt('uploaded_completed')."</span>";
}

sub html_imgman {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	$in{'file'} =~ /\.(\w{3})$/;
	my ($exten) = ".".$1;

	&connect_db;
	my ($sth) = &Do_SQL("INSERT_ INTO igd_images SET ID_categories='$in{'ID_categories'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
	my ($fname) = "img".$sth->{'mysql_insertid'};
	##### Upload Data ######
	my $file = param('file');
	if (open (SAVE,">$cfg{'path_imgman'}$fname$exten")){
		binmode(SAVE);
		while ($size = read($file,$data,1024)) {
			print SAVE $data;
			$total_size += $size;
		}
		close SAVE;
		if ($total_size >0){
			&html_message(&trans_txt('upfile_ok'));
		}else{
			&html_message(&trans_txt('upfile_err'));
		}
	}else{
		&html_message(&trans_txt('upfile_err'));
	}
}

sub prototypes_upload{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 28 Apr 2010 11:28:09
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	#Primero hace el insert
	$in{'name'}=&load_name('sl_prototype','id_prototype',$in{'id_prototype'},'name');
	$in{'description'}=&load_name('sl_prototype','id_prototype',$in{'id_prototype'},'description');
	$in{'status'}=&load_name('sl_prototype','id_prototype',$in{'id_prototype'},'status');
	$in{'id_admin_users'}=&load_name('sl_prototype','id_prototype',$in{'id_prototype'},'id_admin_users');
	$in{'date'}=&load_name('sl_prototype','id_prototype',$in{'id_prototype'},'date');
	$in{'time'}=&load_name('sl_prototype','id_prototype',$in{'id_prototype'},'time');
	$va{'tabmessages'} = &trans_txt('mer_prototypes_fileadded');
	my ($sth) = &Do_SQL("INSERT INTO sl_prototype_files SET id_prototype='$in{'id_prototype'}',file='$val".&filter_values($in{'file'})."',file_name='".&filter_values($in{'id_prototype'}.$in{'file'})."',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	$lastid=$sth->{'mysql_insertid'};
	if($lastid>0){
		$in{'tabs'} = 2;
		my ($file) = $cfg{'path_shpfiles'}.$in{'id_prototype'}.$in{'file'};
		if (&load_convfile($file,1) == 1){
			&auth_logging('File updated: '.$in{'file'},$in{'id_prototype'});
			delete($in{'files'});
			delete($in{'filestype'});
			$va{'message'} = &trans_txt('upfile_ok');
			print "Content-type: text/html\n\n";
			print &build_page('mer_prototypes_view.html');
		}elsif (&load_convfile($file,1) == 2){
			&Do_SQL("Delete from sl_prototype_files where ID_prototype_files=$lastid");
			$va{'message'} = &trans_txt('upfile_exists');
			print "Content-type: text/html\n\n";
			print &build_page('mer_prototypes_view.html');			
		}else{
			&Do_SQL("Delete from sl_prototype_files where ID_prototype_files=$lastid");
			&html_uploaderr;
		}		
	}else{
		$va{'message'} = &trans_txt('upfile_exists');
		print "Content-type: text/html\n\n";
		print &build_page('mer_prototypes_view.html');			
	}
}

sub html_upload {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($file) = "$cfg{'path_cybersource'}imports/$in{'file'}";
	if (&load_convfile($file) == 1){
		$va{'message'} = &trans_txt('upfile_ok');
		print "Content-type: text/html\n\n";
		print &build_page('opr_outbound_updtrk.html');				
	}elsif (&load_convfile($file) == 2){
		$va{'message'} = &trans_txt('upfile_exists');
		print "Content-type: text/html\n\n";
		print &build_page('opr_outbound_updtrk.html');			
	}else{
		&html_uploaderr;
	}		
}

sub load_ups_2tbl {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($count)  = 0;
	my ($errors) = 0;
	my ($valid)  = 0;
		
	open (FILE, "$upload_dir$temp_file");
	while ($record = <FILE>){
		if ($count >0){		# The first record are the headers
			my (@ary) = split(',', $record);
			&indexOf($record,',');
			#&cgierr( substr($record,1,20));
  	}
  	$count++;
 	}
	close(FILE);
}

sub load_ups_data {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($count)  = 0;
	my ($errors) = 0;
	my ($valid)  = 0;
		
	open (FILE, "$upload_dir$temp_file");
	while ($record = <FILE>){
		if ($count >0){
			my (@ary) = split(',', $record);
			if ($ary[1] < 1000){
				## add record to errors file 
				&add_record("$upload_dir$err_file",$record);
				$errors++;
			}else{
				## if id_orders cannot be found in the record, add entire record to the errors list
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products2 WHERE ID_orders='$ary[1]'");
				$va{'matches'} = $sth->fetchrow;		
				if ($va{'matches'} eq 1){
					## update table sl_orders_products
					$shpDate = &format_date($ary[9]);		## common/sub.base_sltv.html
					my ($sth) = &Do_SQL("UPDATE sl_orders_products2 SET shpDate='$shpDate',Tracking='$ary[0]',shpProvider='UPS' WHERE ID_orders='$ary[1]'");
					## update status in orders table if it doesn't say 'Shipped'
					$sth = &Do_SQL("SELECT Status FROM sl_orders2 WHERE ID_orders='$ary[1]';");
					$rec = $sth->fetchrow_hashref;
					if ($rec->{'Status'} ne "Shipped"){
						$sth = &Do_SQL("UPDATE sl_orders2 SET Status='Shipped' WHERE ID_orders='$ary[1]';");
					}
					$valid++;
				}else{
					add_record("$upload_dir$err_file",$record);
					$errors++;							
				}
			}
  	}
  	$count++;
 	}
	close(FILE);
	
	$count -= 1;
	$va{'searchresults'} = qq |
		<tr onmouseover='m_over(this)' onmouseout='m_out(this)'>
			<td>$in{'file'}</td>
			<td align='center'>$valid</td>
			<td align='center' onClick=\"trjump('/cgi-bin/mod/admin/admin?cmd=load_ups_invdata')\">$errors</td>
			<td align='center'>$count</td>
		</tr>	|;
}

sub file_type {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	if (open (FILE, "$upload_dir$temp_file")){
		while ($record = <FILE>){		
			## found out the number of fields (commas) to determine file type
			my (@ary) = split(',', $record);
			
			return $#ary;
		}
		close (FILE);			
	}
	return 0;
}





sub html_uploaderr {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	$va{'message'} = &trans_txt('upfile_err');
	print "Content-type: text/html\n\n";
	print &build_page('opr_outbound_updtrk.html');
}

sub html_report {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	$va{'message'} = @_[0];
	print "Content-type: text/html\n\n";
	print &build_page('outbound_report.html');
}

sub html_uploaded {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	$va{'message'} = @_[0];
	print "Content-type: text/html\n\n";
	print &build_page('outbound_uploaded.html');
}

sub html_message {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	$va{'message'} = @_[0];
	print "Content-type: text/html\n\n";
	print &build_page('upfile:message.html');
}

################################################################
################################################################
################################################################
################################################################

sub parse_form {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	my (%in, $value);
	if ($ENV{'REQUEST_METHOD'} ne 'GET' and $ENV{'REQUEST_METHOD'} ne 'POST') {
		&cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
	}
	PAIR: foreach $key (param){
		$value = param($key);
		$value =~ s/<!--(.|\n)*-->//g;			# Remove SSI.
		$value =~ s/\r//g;
		if ($value eq "---") { next PAIR; }		# This is used as a default choice for select lists and is ignored.
		if ($value =~ /^\s*$/) { next PAIR; }		# This is used as a default choice for select lists and is ignored.
		(exists $in{$key}) ?
			($in{$key} .= "~~$value") :		# If we have multiple select, then we tack on
			($in{$key}  = $value);
		$in{$key} = $value;
	}
	return %in;
}

##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
# Last Modified on: 11/10/08 12:12:47
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la forma de mostrar la fecha
	my (@sys_err) = @_;
	print "Content-type: text/html\n\n";

	my ($key,$env,$out_in,$out_env);
	if (!$cfg{'cd'}){
		print qq|
			<head>
				<title>CGI - ERROR</title>
			</head>					
			<body BGCOLOR="#FFFFFF" LINK="#FF0000" VLINK="#FF0000" ALINK="#FF0000">			
				<table BORDER="0" WIDTH="500" CELLPADDING="10" CELLSPACING="10">
					<tr>
						<td BGCOLOR="#FF0000" colspan="2"><font size="5" color="#FFFFFF" face="Arial"><b>CGI-Error</b></font></td>
					</tr>
				</table>
				<table BORDER="0" WIDTH="550" CELLPADDING="2" CELLSPACING="0">|;
					$sys_err[0]	and print "\n<tr>\n  <td valign='top' width='200'><font face='Arial' size='3'>Error Message</font></td>\n  <td><font face='Arial' size='3' color='#FF0000'><b>$sys_err[0]</b></font></td>\n</tr>\n";
					$sys_err[1]	and print "<tr>\n  <td width='200'><font face='Arial' size='2'>Error Code</font></td>\n  <td><font face='Arial' size='2'>$sys_err[1]</font></td>\n";
					$sys_err[2]	and print "<tr>\n  <td valign='top' width='200'><font face='Arial' size='2'>System Message</font></td>\n  <td><font face='Arial' size='2'>$sys_err[2]</font></td>\n";
					print qq|
					<tr>
						<td colspan="2"><p>&nbsp</p><font face='Arial' size='2'>If the problem percist, please contact us with the above Information.</font><br>
							<font face='Arial' size='2'><a href="mailto:$systememail">$systememail</a></font>
						</td>
					</tr>
				</table>
			</body>
		</html>|;
		######################################
		### Save CGI ERR			
		##############################
		my ($ip);
		my (@outmsg) = @sys_err;
		my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
		$year+=1900;
		$mon++;
		my ($time,$date) = ("$hour:$min:$sec","$mon-$day-$year");
		
		foreach $key (sort keys %in) {
			$outmsg[3] .= "$key=$in{$key},";
		}
		
		foreach $env (sort keys %ENV) {
			$outmsg[4] .= "$env=$ENV{$env},";
		}
		
		for (0..4){
			$outmsg[$_] =~ s/\n|\r/ /g;
			$outmsg[$_] =~ s/\|/ /g;
		}
		
		if ($ENV{'REMOTE_ADDR'}){
			$ip = $ENV{'REMOTE_ADDR'};
		}elsif ($ENV{'REMOTE_HOST'}){
			$ip = $ENV{'REMOTE_HOST'};
		}elsif ($ENV{'HTTP_CLIENT_IP'}){
			$ip = $ENV{'HTTP_CLIENT_IP'};
		}else{
			$ip = "Unknow";
		}
		(!$cfg{'cgierr_log_file'}) and ($cfg{'cgierr_log_file'} = './logs/cgierr.log');
		if (open (LOG, ">>$cfg{'cgierr_log_file'}")){;
			print LOG "$usr{'username'}|$outmsg[0]|$outmsg[1]|$outmsg[2]|$outmsg[3]|$outmsg[4]|$time|$date|$ip\n";
			close AUTH;
		}
	}else{
		print "<PRE>\n\nCGI ERROR\n==========================================\n";
					$sys_err[0]	and print "Error Message       : $sys_err[0]\n";
					$sys_err[1]	and print "Error Code          : $sys_err[1]\n";
					$sys_err[2]	and print "System Message      : $sys_err[2]\n";
					$0			and print "Script Location     : $0\n";
					$]			and print "Perl Version        : $]\n";
					$sid		and print "Session ID          : $sid\n";


		print "\nForm Variables IN\n-------------------------------------------\n";
		
		foreach $key (sort keys %in) {
			my $space = " " x (20 - length($key));
			$out_in .= "$key=$in{$key},";
			print "$key$space: $in{$key}\n";
		}
		
		print "\nForm Variables ERROR\n-------------------------------------------\n";
		foreach $key (sort keys %error) {
			my $space = " " x (20 - length($key));
			print "$key$space: $error{$key}\n";
		}
		
		print "\nEnvironment Variables\n-------------------------------------------\n";
		foreach $env (sort keys %ENV) {
			my $space = " " x (20 - length($env));
			$out_env .= "$env=$ENV{$env},";
			print "$env$space: $ENV{$env}\n";
		}
		
		print "\n</PRE>";

	}

	exit -1;
}