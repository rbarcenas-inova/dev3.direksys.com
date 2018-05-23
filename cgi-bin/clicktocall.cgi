#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################


# Load the form information and set the config file and userid.
local(%in) = &parse_form;
local(@db_cols,%db_select_fields,%db_valid_types,%db_not_null);
local($sid,%error,%va,%trs,%perm);
$in{'sid'} ? ($sid   = $in{'sid'}): ($sid   = '');

use Asterisk::Manager;
local ($server)   = '63.95.246.131';
local ($username) = 'direksys';
local ($password) = '32-221611';
	

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

	print "Content-type: text/html\n\n";
	&home_page;
	### Dial Extension
	if ($in{'sitdialnum'}){
		$tmp{'extension'} = 'SIP/401';
		#$tmp{'extension'} = 'Local/601@ext-queues';
		print "<pre>";
		#print qq|ACTION: Originate\nChannel: $tmp{'extension'}\nExten: 8$in{'sitdialnum'}\nPriority: 1\nContext: from-internal\nAsync: True\nCallerid: <$in{'sitdialnum'}>\n\n|;
		%command  = (ACTION => 'Originate',Channel => $tmp{'extension'},Exten => '8'.$in{'sitdialnum'},Priority => '1',Context => 'from-internal',	Async => 'True',	Callerid => "<$in{'sitdialnum'}>");
		@ary = &send_cmd_to_ast(0,%command );
		foreach ( @ary ) {
    		print "$_\n";
		}
		print "</pre>";
		
		#return "OK";
	}elsif($in{'list_channels'}){
		$server   = '63.95.246.130';
		%command  = (Action=>'Status');
		print "<pre>";
		@ary = &send_cmd_to_ast('StatusComplete',%command );
		foreach ( @ary ) {
			$line = $_;
			if ($line =~ '==='){
				#print "########\n account: $account\n context: $context\n callerid: $callerid\n channel: $channel \n########\n";
				## assign
				if ($channel =~ /SIP\/\d/ and $context){
					++$resp{$account};
					push(@cdr,"From : $callerid / DID: $account / Duration: $dur sec");
				}else{
					$account = '';
					$context = '';
					$callerid = '';
					$channel = '';
					$dur = '';
				}
				next;
			}
			if ($line =~ /Account: (.*)/){
				$account = $1;
			}
			if ($line =~ /Context: (.*)/){
				$context = $1;
			}
    		if ($line =~ /CallerID: (.*)/){
				$callerid = $1;
			}
			if ($line =~ /Channel: (.*)/){
				$channel = $1;
			}
			if ($line =~ /Seconds: (.*)/){
				$dur = $1;
			}
    		#print "$line\n";
		}
		if ($channel =~ /SIP\/\d/ and $context){
			++$resp{$account};
			push(@cdr,"From : $callerid / DID: $account / Duration: $dur sec");
		}
		
		print "\n\n\n\n\n##################\n";
		foreach $key (sort keys %resp) {
			print "$key : ".($resp{$key}/1)."\n";
		}
		print "\n\n##################\n";
		foreach( @cdr ){
			print "$_\n";
		}		
		print "</pre>";
	}else{
		print "...";
	}
}

sub home_page {
# --------------------------------------------------------
	print qq|
<head>
  <meta name="generator" content="HTML Tidy for Windows (vers 14 February 2006), see www.w3.org">

  <title>Direksys Administration : </title>

<script language="JavaScript1.2" type="text/javascript">

function loadDoc(docname) {
	if (xmlhttp) {
		var i = Math.round(10000*Math.random())
		docname = docname + '&rsid='+i;
		document.all.ajaxcontent.innerHTML="<img src='/sitimages/processing.gif' border='0'>";
		//popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'mouse-corner', -400, -1);
		//popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'mouse-corner',100 ,300);
		
		xmlhttp.open("GET", docname,true); 
		xmlhttp.onreadystatechange=function() {
			if (xmlhttp.readyState==4) {
				// document.forms[0].ajaxcontent.value=xmlhttp.responseText;
				document.all.ajaxcontent.innerHTML=xmlhttp.responseText;
			}
		}
		xmlhttp.send(null)	
	}
}
</script>

<body bgcolor="#EEEEEE" topmargin="0">

<p>Call (786) 200 4423 <a href='/cgi-bin/clicktocall.cgi?sitdialnum=7862004423'>Call</a></p>
<p><a href="/cgi-bin/clicktocall.cgi?list_channels=1">List SIP channls</p>
<p><a href='/cgi-bin/clicktocall.cgi'>Home</a></p>
|;
	
}


sub send_cmd_to_ast {
# --------------------------------------------------------
	my ($end,%command) = @_;
	my (@output);

	# Connect to Asterisk
	$asterisk = new Asterisk::Manager;
	$asterisk->user($username);
	$asterisk->secret($password);
	$asterisk->host($server);
	$asterisk->connect || die "Could not connect to Asterisk on $server: ", $asterisk->error, "\n";
	@output = $asterisk->sendcommand(%command);

#	print "ARY 1:\n";
#	foreach( @ary ){
#	  print "$_\n";
#	}
#	print "ARY 2:\n";
# 	@ary = $asterisk->read_response;
#	foreach( @ary ){
#	  print "$_\n";
#	}
	if ($end){
		while( 1 ){
			++$c;
			last  if ($c>500);
			my @ary = $asterisk->read_response;
		  	last  if $ary[0] =~ /$end/;
		  	push (@output, '=========');
		  	push (@output, @ary);
		}
	}
	
	
	return @output;
#	use Net::Telnet ();
#	$tn = new Net::Telnet (Port => 5038,
#		      Prompt => '/.*[\$%#>] $/',
#		      Output_record_separator => '',
#		      Errmode    => 'return'
#		     );
#	$server = '63.95.246.131';
#	$username = 'direksys';
#	$password = '32-221611';
#	$tn->open($server);
#	$tn->waitfor('/0\n$/');             
#	print "Action: Login\nUsername: $username\nSecret: $password\n\n";
#	$tn->print("Action: Login\nUsername: $username\nSecret: $password\n\n");
#	$tn->waitfor('/Authentication accept*/');
#	
#	## Test 2  OK
#	$tn->print("$command");
#	#$tn->waitfor('/Response: Success\n/');
#	($line) = $tn->waitfor('/.*\n\n/');
#
#	$tn->print("Action: Logoff\n\n");
#	return ("$line\n".$tn->lastline);
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

