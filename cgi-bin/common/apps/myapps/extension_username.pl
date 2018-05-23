#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
use DBI;
use DBIx::Connector;
use DBD::mysql;
use Cwd;
use File::Copy;
use Encode;

# Load the form information and set the config file and userid.
local(%in) = &parse_form;
local(%config, %cfg, %usr);

# Required Libraries
# --------------------------------------------------------
eval {
	require ("../../subs/auth.cgi");
	require ("../../subs/sub.base.html.cgi");
};

if ($@) { &cgierr ("Error loading required Libraries",300,$@); }

eval { &main; };
if ($@) { &cgierr("Fatal error, 301, $@"); }

exit;

sub main {	
	$|++;
	print "Content-type: text/html\n\n";

	# aplico la 2 porque este proceso fue diseñado para TMK
	$in{'e'} = 2 if (!$in{'e'});
	my @cols = ('extension','name');

	&load_settings;

	print "<h4>DIREKSYS($in{'e'}) - Relacion de Usuarios - Extension</h4>";
	
	my $file_path = $cfg{'path_layouts'}.'fide/';
	opendir (CMDIR, $file_path) || &cgierr('Unable to open directory ' . $file_path ,704,$!);
	@files = readdir(CMDIR);# Read in list of files in directory..
	closedir (CMDIR);

	&connect_db;
	##### Looping files extensions .csv
	FILE: foreach my $file_name (sort @files) {

		next if ($file_name =~ /^\./);		# Skip "." and ".." entries..
		next if ($file_name =~ /^index/);	# Skip index.htm type files..
		next if ($file_name !~ /.csv$/);	# Skip
		next if ($file_name =~ /processed.csv$/);# Skip

		print "Archivo encontrado: " . $file_name  . "\n<br>";
		print "Intentando abrir el archivo " . $file_name  . "\n<br>";

		##### Open File
		my $i=0;
		my $str_to_file = '';


		if (-e  $file_path . $file_name) {

			open(my $this_file, "<", $file_path . $file_name) or &cgierr('Unable to open file: '. $file_path . $file_name, 601,$!);

			LINE: while (<$this_file>) {
				$line = $_;
				$line =~ s/\r|\n|//g;
				print "$i - $line\n\n";

				my ($item_status);
				my @line_data = split(/\,/);
				my $this_str_data = '';
				for (0..$#line_data) {

					$line_data[$_] =~ s/\r|\n|\t|\"//g;
					$line_data[$_] =~ s/^\s+//;
					$line_data[$_] =~ s/\s+$//;

					if( $_ >= 1 ){
						$this_str_data .= ",".$line_data[$_];
					}
				}

				### Si el dato es numerico(para descartar la linea de titulo)
				my $username = '';
				if( $line_data[0] =~ /\d{4}/ ){
					my $this_ext = $line_data[0];

					my $sql_usr = "SELECT Username FROM admin_users WHERE Username_ref = '".$this_ext."' AND `Status` = 'Active';";
					my $sth_usr = &Do_SQL($sql_usr);
					$username = $sth_usr->fetchrow();
					print " ------>> SI: $username<br>";
				}else{
					print "<br>";
					$username = 'UserName';
				}

				$str_to_file .= $username.",".$line_data[0].$this_str_data."\n";

			}

		}

		### Se genera el archivo con los datos obtenidos de la CC
		my $only_file_name = substr($file_name, 0, length($file_name) - 4);
		if( open(my ($file),">", $file_path.$only_file_name."_processed.csv") ){
			print $file $str_to_file;
			close($file);
			print "\n<br>Se genero correctamente el archivo: ".$only_file_name."_processed.csv";
		}else{
			&cgierr("Unable to open $fname");
		}
	}

	&disconnect_db;
}

#########################################################
##			Query				##
##########################################################
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

##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Last Modified on: 11/10/08 11:58:21
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

sub load_settings {
	my ($fname);
	
	if ($in{'e'}) {
		$fname = "../../general.e".$in{'e'}.".cfg";
	}else {
		$fname = "../../general.ex.cfg";
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

sub check_ip {
# --------------------------------------------------------
	my ($ip, $ipfilter) = @_;
	
	my (@ip) = split(/\./,$ip,4);
	my (@allowip) = split(/\,/,$ipfilter,4);
	
	for my $i(0..$#allowip){
		$allowip[$i] =~ s/\n|\r//g;
		$ok = 1;
		my (@ipfilter) = split(/\./,$allowip[$i],4);
		for my $x(0..3){
			if ($ip[$x] ne $ipfilter[$x] and $ipfilter[$x] ne 'x'){
				$ok = 0;
			}
		}
	}
	return $ok;
}


1;