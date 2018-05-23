#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################


# Load the form information and set the config file and userid.
local(%in) = &parse_form;
local(@db_cols,%db_select_fields,%db_valid_types,%db_not_null);
local($sid,%error,%va,%trs,%perm);
$in{'sid'} ? ($sid   = $in{'sid'}): ($sid   = '');

# Required Libraries
# --------------------------------------------------------

eval {
	&main;
};
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

sub main {
# --------------------------------------------------------
	$|++;
##### Loading File Location
# --------------------------------------------------------
($in{'e'}) and ($in{'e'} = int($in{'e'}));
my $home_dir = './common';
if ($in{'e'}>0){
	open (CFG, "<$home_dir/general.e$in{'e'}.cfg") or &cgierr ("Unable to open: general.cfg",301,$!);
}else{
	open (CFG, "< $home_dir/general.cfg") or &cgierr ("Unable to open: $home_dir/general.cfg",302,$!);
}
LINE: while (<CFG>) {
	(/^#/)      and next LINE;
	(/^\s*$/)   and next LINE;
	$line = $_;
	$line =~ s/\n|\r//g;
	my ($td,$name,$value) = split (/\||\=/, $line,3);
	if ($td eq "conf") {
		$cfg{$name} = $value;
		next LINE;
	}
}
close CFG;
	
print "Content-type: text/html\n\n";

	if( $in{'id'} and $in{'pict'} ) {
		if( -e "$cfg{'path_imgman'}/$in{'id'}a$in{'pict'}.jpg" ) {
			print "<img src='".$cfg{'path_imgman_url'}.$in{'id'}."a$in{'pict'}.jpg' border='0' alt='$in{'id'}'>";
		}else{
			print $cfg{'path_imgman_url'}.$in{'id'}."a$in{'pict'}.jpg";
		}
		print qq|
		<IFRAME SRC="showimages.cgi?id=$in{'id'}&nopop=1" name="rcmd" TITLE="Show Products" width="100%" height="115" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
			<H2>Unable to do the script</H2>
			<H3>Please update your Browser</H3>
			</IFRAME>|;
	}elsif($in{'id'}){
		if( -e "$cfg{'path_imgman'}/$in{'id'}b1.gif" ) {
			print qq|
				<script language="JavaScript1.2">
					function imgwin(link) {
						win = window.open("","extra","toolbar=no,width=530,height=480,directories=no,status=no,scrollbars=yes,resizable=no,menubar=no")
						win.location.href = link;
						win.focus();
					}
				</script>|;
			print "<table width='100%'><tr><td nowrap>";
			(!$in{'img'}) and ($in{'img'}=1);
			$img=$in{'img'}+1;
			$img=9 if !$img;
			for( $i = 1; $i < $img; $i++ ) {
				if( -e "$cfg{'path_imgman'}/$in{'id'}b$i.gif" ) {
					$pic = "<img src='$cfg{path_imgman_url}$in{id}b$i.gif' alt='$in{id}' border='1'>";
					if( -e "$cfg{'path_imgman'}/$in{'id'}a$i.jpg" ) {
						if ($in{'nopop'}){
							print "<a href=\"showimages.cgi?id=$in{'id'}&e=$in{'e'}&pict=$i\" target='_top'>$pic</a>&nbsp;";	
						}else{
							print "<a href=\"javascript:imgwin('showimages.cgi?id=$in{'id'}&e=$in{'e'}&pict=$i');\">$pic</a>&nbsp;";	
						}
					}else {
						print "$pic&nbsp;";
					}
				}				
			}
			print "</td></tr></table>";
		}
	}
}

##########################################################
##			Query				##
##########################################################
sub parse_form {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : Decoding Form Data. This is taken in %in hash as pairs.
# Parameters : 
	my (@pairs, %in);
	my ($buffer, $pair, $name, $value);
	if ($ENV{'REQUEST_METHOD'} eq 'GET') {
		@pairs = split(/&/, $ENV{'QUERY_STRING'});
	}elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
 		@pairs = split(/&/, $buffer);
 		$ENV{'QUERY_STRING'} =  $buffer;
 		$ENV{'REQUEST_METHOD'} = 'GET';
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
			
			$value =~ s/\r//g;
			#$value =~ s/<!--(.|\n)*-->//g;			# Remove SSI.
			if ($value eq "---") { next PAIR; }		# This is used as a default choice for select lists and is ignored.
			
			(exists $in{$name}) ?
				($in{$name} .= "|$value") :		# If we have multiple select, then we tack on
				($in{$name}  = $value);			# using the ~~ as a seperator.
	}
	
	return %in;
}

##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Last Modified on: 11/10/08 12:24:27
# Last Modified by: MCC C. Gabriel Varela S: Se corrige la forma en que se muestra la fecha
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
											<font face='Arial' size='2'><a href="mailto:$systememail">$systememail</a></font></td>
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

