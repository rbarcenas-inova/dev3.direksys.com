#!/usr/bin/perl
#######################################################################
#######################################################################
#######################################################################
use DBI;
use DBIx::Connector;
use DBD::mysql;

local ($home_dir) = '/home/www/domains/direksys.com/cgi-bin/common/apps/';
local	($uname)	=	 `uname -n`;

if($uname =~ /sltv/){
	$home_dir=~s/direksys/dev\.shoplatinotv/g;

}elsif($uname !~ /s11/){
	$home_dir=~s/domains\//inn_domains\/dev\./g;
}
	
# Load the form information and set the config file and userid.
chdir ("$home_dir");

# Required Libraries
# --------------------------------------------------------
eval {
	require ("../subs/auth.cgi");
	require ("../subs/sub.base.html.cgi");
};


eval { &main; };
if ($@) { &cgierr("Fatal error,301,$@"); }

exit;

sub main {
# --------------------------------------------------------
# Last Modified on: 07/13/09 14:23:19
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a &payments_of_postdated;
	
	$|++;
	&connect_db;
	&assign_destination;
	&disconnect_db;
}


#####################
##################### Sub Funciones (utilizadas por las funciones principales de este archivo


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

sub assign_destination{
# --------------------------------------------------------

	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});

	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Mixcoac';",1);
	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Vixicom' WHERE CURDATE() = '2011-08-30' AND  `didmx` IN(1757,1699,1659,1660,1780,1666,1759,1102,1120,1040,1668,1798,1678,1096,1147,1083);",1);
	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Vixicom' WHERE CURDATE() = '2011-08-31' AND  `didmx` IN(1742,1664,1082,1169,1124,1648,1759,1727);",1);
	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Vixicom' WHERE CURDATE() = '2011-09-01' AND  `didmx` IN(11541757,1666,1699,1124,1708,1755,1682,1096,1798,1659,1120,1605,1147,1083,1087,1131);",1);
	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Vixicom' WHERE CURDATE() = '2011-09-02' AND  `didmx` IN(1652,1660,1102,1679,1665,1822,1667,1754);",1);
	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Vixicom' WHERE CURDATE() = '2011-09-03' AND  `didmx` IN(17571770,1702,1685,1039,1657,1036,1679,1169,1039,1678,1708,1822,1665,1683,1157,1798,1699,1806);",1);
	my $sth = &Do_SQL("UPDATE `sl_numbers` SET destination='Vixicom' WHERE CURDATE() = '2011-09-04' AND  `didmx` IN(1664,1780,1036,1039,1702,1081,1679,1154,1036,1686,1648,1678,1096,1798,1120,1120,1699,1658,1120,1699,1087);",1);
	
	return;
	
}

