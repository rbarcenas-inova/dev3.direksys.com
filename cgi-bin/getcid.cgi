#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################

#use socket;
use DBI;
use DBIx::Connector;
use DBD::mysql;

# Load the form information and set the config file and userid.
local(%in) = &parse_form;

eval { 
	require ("./common/subs/auth.cgi");
	require ("./common/subs/sub.base.html.cgi");
	require ("./mod/admin/sub.base.html.cgi");
	require ("./mod/admin/sub.func.html.cgi");
	#require "../../cgi-bin/mod/admin/admin.cfg";
	#require "../../cgi-bin/common/subs/auth.cgi";
	require ("./mod/admin/admin.html.cgi");
	require ("./mod/admin/admin.prefs.cgi");
	require ("./common/subs/sub.func.html.cgi");
	&main; };
if ($@) { &cgierr("Fatal error",101,$@); }

exit;

sub main {
# --------------------------------------------------------
# Last Modified on: 05/06/09 17:10:46
# Last Modified by: MCC C. Gabriel Varela S: Se inserta en CDR.
        $|++;
        print "Content-type: text/html\n\n";
        $in{'cid'} = int($in{'cid'});
        $in{'did'} = int($in{'did'});
        #$in{'exten'} = int($in{'exten'});
        $in{'user'} =~ s/\/|`|'|"|\n|\r|\t//g;  #'

		if ($in{'cid'} and $in{'did'} and $in{'exten'}){
			$DBH  = "dbi:mysql:database=cdronly;host=$cfg{'dbi_host'};mysql_read_default_file=/etc/mysql/my.cnf";
			$DBH  = DBI->connect($DBH,$cfg{'dbi_user'},$cfg{'dbi_pw'});
			
			&Do_SQL("INSERT INTO cdr (calldate ,clid ,src ,dst ,dcontext ,channel ,dstchannel ,lastapp ,lastdata ,duration ,billsec ,disposition ,amaflags ,accountcode ,uniqueid ,userfield )
							VALUES (now(), '$in{'cid'}', '$in{'did'}', '$in{'exten'}', '', '', '', '', '', '0', '0', '', '0', 'From external PBX', '', '');");
							
			$DBH->disconnect;
			$resp = 'ok';
			
			if (open (LOG, ">/home/www/domains/direksys.com/cgi-bin/newcall/$in{'exten'}.txt")){
				print LOG "$in{'cid'}|$in{'did'}|$in{'exten'}|$in{'user'}|".&get_date."|".&get_time."\n";
				close LOG;
			}else{
				#$resp = $! ."./newcall/$in{'exten'}.txt";
			}
			if (open (LOG, ">/home/www/domains/dev.shoplatinotv.com/cgi-bin/newcall/$in{'exten'}.txt")){
				print LOG "$in{'cid'}|$in{'did'}|$in{'exten'}|$in{'user'}|".&get_date."|".&get_time."\n";
				close LOG;
			}else{
				#$resp = $! ."./newcall/$in{'exten'}.txt";
			}			
			if (open (LOG, ">/home/www/domains/sltvadmin.com/cgi-bin/newcall/$in{'exten'}.txt")){
				print LOG "$in{'cid'}|$in{'did'}|$in{'exten'}|$in{'user'}|".&get_date."|".&get_time."\n";
				close LOG;
			}else{
				#$resp = $! ."./newcall/$in{'exten'}.txt";
			}
			if (open (LOG, ">>./logs.txt")){
				print LOG "$in{'cid'}|$in{'did'}|$in{'exten'}|$in{'user'}|".&get_date."|".&get_time."\n";
				close LOG;
			}
		}else{
			$resp = 'error';
		}
    
    
        
        print $resp;
}

####################################################################
########                 UTILITIES                          ########
####################################################################
sub get_time {
# --------------------------------------------------------
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	($sec < 10)  and ($sec = "0$sec");
	($min < 10)  and ($min = "0$min");
	($hour < 10) and ($hour = "0$hour");

	return "$hour:$min";
}

sub get_date {
# --------------------------------------------------------
	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
	my (@months, $output,$year_num,$mon_num);
	if ($usr{'pref_language'}){
		@months = qw!Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec!;
	}else{
		@months = qw!Ene Feb Mar Apr May Jun Jul Ago Sep Oct Nov Dic!;
	}

	($day < 10) and ($day = "0$day");

	$year_num = $year - 100;
	($year_num < 10) and ($year_num = "0$year_num");

	$mon_num = $mon + 1;
	($mon_num < 10) and ($mon_num = "0$mon_num");
	$output = "$day-$months[$mon]-" . ($year + 1900);

    return $output;
}
sub parse_form {
# --------------------------------------------------------

        my (@pairs, %in);
        my ($buffer, $pair, $name, $value);

        if ($ENV{'REQUEST_METHOD'} eq 'GET') {
                @pairs = split(/&/, $ENV{'QUERY_STRING'});
        }
        elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
                read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
                @pairs = split(/&/, $buffer);
        }
        else {
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
                if ($value eq "---") { next PAIR; }             # This is used as a default choice for select lists and is ignored.
                (exists $in{$name}) ?
                        ($in{$name} .= "|$value") :             # If we have multiple select, then we tack on
                        ($in{$name}  = $value);                 # using the ~~ as a seperator.
        }
        return %in;
}

sub cgierr {
# --------------------------------------------------------
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
        $sys_err[0]     and print "\n<tr>\n  <td valign='top' width='200'><font face='Arial' size='3'>Error Message</font></td>\n  <td><font face='Arial' size='3' color='#FF0000'><b>$sys_err[0]</b></font></td>\n</tr>\n";
        $sys_err[1]     and print "<tr>\n  <td width='200'><font face='Arial' size='2'>Error Code</font></td>\n  <td><font face='Arial' size='2'>$sys_err[1]</font></td>\n";
        $sys_err[2]     and print "<tr>\n  <td valign='top' width='200'><font face='Arial' size='2'>System Message</font></td>\n  <td><font face='Arial' size='2'>$sys_err[2]</font></td>\n";
        print qq|
<tr>
  <td colspan="2"><p>&nbsp</p><font face='Arial' size='2'>If the problem percist, please contact us with the above Information.</font><br>
                <font face='Arial' size='2'><a href="mailto:$systememail">$systememail</a></font></td>
</tr>
  </table>
</body>
</html>|;

        }else{
                print "<PRE>\n\nCGI ERROR\n==========================================\n";
                $sys_err[0]     and print "Error Message       : $sys_err[0]\n";
                $sys_err[1]     and print "Error Code          : $sys_err[1]\n";
                $sys_err[2]     and print "System Message      : $sys_err[2]\n";
                $0                      and print "Script Location     : $0\n";
                $]                      and print "Perl Version        : $]\n";
                $sid            and print "Session ID          : $sid\n";


                print "\nForm Variables IN\n-------------------------------------------\n";
                foreach $key (sort keys %in) {
                        my $space = " " x (20 - length($key));
                        $out_in .= "$key=$in{$key},";
                        print "$key$space: $in{$key}\n";
                }
                print "\nForm Variables ERROR\n-------------------------------------------\n";
                foreach $key (sort keys %error) {
                        my $space = " " x (20 - length($key));
                        $out_in .= "$key=$error{$key},";
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

}
