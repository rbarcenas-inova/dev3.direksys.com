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

local(%in) = &parse_form;
local ($dir) = getcwd;
local ($in{'e'}) = 2;
# local ($usr{'id_admin_users'}) = 1;
# local ($cfg{'id_warehouses'}) = 1001;
# local ($cfg{'reset'}) = 1;


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

sub main {
# ID admin_events 97
# ID admin_event_logs 3133630
#################################################################
#################################################################    
    use Try::Tiny;
    use MIME::Base64;
    my $curdate = &Do_SQL("SELECT DATE_FORMAT(NOW(),'%Y%m%d') now;")->fetchrow();
    my $where="AND CapDate >= DATE_FORMAT(date_add(NOW(), INTERVAL -".$cfg{'ftp_diestel_days_interval'}." DAY),'%Y%m%d') AND Date <= DATE_FORMAT(date_add(NOW(), INTERVAL -".$cfg{'ftp_diestel_days_interval'}." DAY),'%Y%m%d')";
        
    $query = "SELECT date_add(NOW(), INTERVAL -".$cfg{'ftp_diestel_days_interval'}." DAY),
                        id_orders_payments,
                        id_orders,
                            Pmtfield11,
                            Pmtfield6,
                        DATE_FORMAT(CapDate, '%d/%m/%Y') date,
                        time,
                        AuthCode,
                        amount
                    FROM 
                        sl_orders_payments 
                    WHERE 1
                        $where
                        AND PmtField9 = 'Mastercard - Puntos'
                        AND Captured = 'Yes'
                    ORDER BY
                        id_orders_payments DESC";
    
	
    my $rs = &Do_SQL($query);   	
    my $path=$cfg{'ftp_local_diestel_directory'};
    my $f = $path.'/'."IU$curdate";
    my $filename=$f.'.txt';
	my $singlefilename="IU$curdate".".txt";
    my $content='';
    my $atach='';

	
    try{
        open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
                
        print $fh "HDR|$curdate\n";
        $atach.="HDR|$curdate\n";
        my $aux = 1;
		
        while(my $row = $rs->fetchrow_hashref() ){     				
                $referencia = $row->{'id_orders_payments'};
                if($row->{'amount'} == 1){
                    $referencia = $row->{'Pmtfield11'};
                }
                $encryp_card_number = &Do_SQL("SELECT sl_orders_cardsdata.card_number from sl_orders_cardsdata where id_orders='$row->{'id_orders'}' limit 1")->fetchrow();
                $card_number = &LeoDecrypt($encryp_card_number);
				print $fh "REG|$aux|$row->{'date'}|$row->{'time'}|".$cfg{'ftp_diestel_service'}."|$row->{'AuthCode'}|$card_number|".format_number($row->{'amount'},2,1)."|$row->{'Pmtfield6'}|$cfg{'ftp_diestel_reference_number'}|$referencia\n";
                $atach.="REG|$aux|$row->{'date'}|$row->{'time'}|".$cfg{'ftp_diestel_service'}."|$row->{'AuthCode'}|$card_number|".format_number($row->{'amount'},2,1)."|$row->{'Pmtfield6'}|$cfg{'ftp_diestel_reference_number'}|$referencia\n";
                $aux++;
        }
        my ($totalRow, $totalMount) = &Do_SQL("SELECT count(*), sum(Amount)
                                                FROM 
                                                    sl_orders_payments 
                                                WHERE 1
                                                    $where
                                                    AND PmtField9 = 'Mastercard - Puntos'
                                                    AND Captured = 'Yes'
                                                ORDER BY
                                                    id_orders_payments DESC")->fetchrow();        
		print $fh "TRL|$totalRow|".format_number($totalMount,2,1);
        $atach.="TRL|$totalRow|".format_number($totalMount,2,1);
        close $fh;    
		
		use Data::Dumper;
		use Net::FTPSSL;
		my $ftps = Net::FTPSSL->new($cfg{'ftp_diestel_host'}, 
								   Encryption => EXP_CRYPT,
								   Debug => 1, 
								   DebugLogFile => "test.log",
								   Croak => 1);
		$ftps->trapWarn ();     # Only call if opening a CPAN bug report.
		$ftps->login($cfg{'ftp_diestel_user'}, $cfg{'ftp_diestel_pass'});		
		$ftps->cwd("/In");		
		$ftps->put($filename,$cfg{'ftp_diestel_directory'}.$singlefilename);									
		$ftps->quit();		
		  
       # Enviamos correo a desarrollo con el archivo de puntos
        my $mensaje = "Puntos Diestel";
        my $email=$cfg{'team_direksys_email'};		
        my $fromMail=$cfg{'from_email'};		        
        my $subject = $cfg{'ftp_diestel_subject_email'};
        my %attachments = (
            $singlefilename=>encode_base64($atach)
        );        
		
		my $prev_day = timelocal(0, 0, 0, $mday-1, $mon, $year);		
        &send_mandrillapp_email_attachment($fromMail, $email, $subject,$mensaje,'Puntos diestel '.$prev_day,\%attachments);


    }catch{
        # Enviamos correo a desarrollo con el archivo de puntos
        my $mensaje = "Ha ocurrido un error en la copia del archivo de puntos diestel ".$singlefilename;
        my $email=$cfg{'team_direksys_email'};
        my $fromMail=$cfg{'from_email'};        
        my $subject = $cfg{'ftp_diestel_subject_email'};        
        &send_mandrillapp_email_attachment($fromMail, $email, "Error ".$subject,$mensaje,'Error Puntos diestel');
    }
}




##################################################################
#     CGIERR   	#
##################################################################
sub cgierr {
# --------------------------------------------------------
# Last Modified on: 11/10/08 12:00:31
# Last Modified by: MCC C. Gabriel Varela S: Se corrige que se muestre la fecha de forma correcta
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