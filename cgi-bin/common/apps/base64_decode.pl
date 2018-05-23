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
use Date::Calc qw();

# Default la 11 porque este proceso fue diseñado para Importaciones
local(%in) = &parse_form;

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
#	Created by: Ing. Gilberto Quirino
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
	&execute_fix_left_qty_total;
}


#################################################################
#################################################################
#	Function: execute_fix_left_qty_total
#
#
#	Created by: Gilberto Quirino
#
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
sub execute_fix_left_qty_total{
	print "Content-type: text/html\n\n";

	#my $print = 'Test '.$cfg{'debug_cgierr'}.' -> '.$cfg{'team_direksys_email'};
	#$rslt = &send_text_mail($cfg{'from_email_info'},'gquirino@inovaus.com',"CGIERR->$in{'e'}:$cfg{'app_title'}->$usr{'application'}->$in{'cmd'}","$print");
	# print '<pre>';
	# print $rslt;
	# print '</pre>';
	#&cgierr('Esto es otro simulacro en develop!!');

	#return;

	my $print = "PFBSRT4KCkNHSSBFUlJPUgo9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09
PT0KRXJyb3IgTWVzc2FnZSAgICAgICA6IElOU0VSVCBJTlRPIGBzbF9kZWJ1Z2AgKGBjbWRgLCBg
aWRgLCBgbG9nYCwgYERhdGVgLCBgVGltZWAsIGBJRF9hZG1pbl91c2Vyc2ApIApWQUxVRVMgKCdy
ZXBfYmlfYWxsb3JkZXJzJywgJzk5OTk5JywgJ1NFTEVDVCAKICAgSURBZ2VudCwKICAgQWdlbnRO
YW1lLAogICBJRih1c2VyX3R5cGUgSVMgTk9UIE5VTEwgQU5EIHVzZXJfdHlwZSAhPSAnJyx1c2Vy
X3R5cGUsJ04vQScpIEFTIHVzZXJfdHlwZSwKICAgSUYoT3JkZXJzIElTIE5PVCBOVUxMLE9yZGVy
cywwKUFTIE9yZGVycywKICAgSURfdXNlciwKICAgVXNlcm5hbWVEaXJla3N5cwpGUk9NCigKICAg
U0VMRUNUIAogICAgICBJRF9hZG1pbl91c2VycyBBUyBJREFnZW50LAogICAgICAoQ09OQ0FUKFVQ
UEVSKGFkbWluX3VzZXJzLkZpcnN0TmFtZSksJyAnLFVQUEVSKGFkbWluX3VzZXJzLk1pZGRsZU5h
bWUpLCcgJyxVUFBFUihhZG1pbl91c2Vycy5MYXN0TmFtZSkpKSBBUyBBZ2VudE5hbWUsCiAgICAg
IHVzZXJfdHlwZSwgYWRtaW5fdXNlcnMuSURfYWRtaW5fdXNlcnMgYXMgSURfdXNlciwgYWRtaW5f
dXNlcnMuVXNlcm5hbWUgYXMgVXNlcm5hbWVEaXJla3N5cwogICBGUk9NIGFkbWluX3VzZXJzIAop
QVMgdG1wX2FnZW50CgpMRUZUIEpPSU4KKAogICBTRUxFQ1QKICAgICAgSURfYWRtaW5fdXNlcnMg
QVMgSURBLAogICAgICBDT1VOVChJRF9PcmRlcnMpIEFTIE9yZGVycwogICBGUk9NIHNsX29yZGVy
cwogICAgICBXSEVSRSAxCiAgICAgICBBTkQgc2xfb3JkZXJzLkRhdGUgQkVUV0VFTiAnMjAxNy0w
Ni0wMScgQU5EICcyMDE3LTA2LTAxJyAKICAgICAgIAoKICAgICAgIAoKICAgICAgCgogICAgICBB
TkQgU3RhdHVzICE9ICdTeXN0ZW0gRXJyb3InIAogICAgICBHUk9VUCBCWSBJRF9hZG1pbl91c2Vy
cwopQVMgdG1wX29yZGVyCk9OIHRtcF9vcmRlci5JREEgPSB0bXBfYWdlbnQuSURBZ2VudApIQVZJ
TkcgT3JkZXJzID4gMApPUkRFUiBCWSBBZ2VudE5hbWUgCgogPT09PT09PT09PT09PT09PT09PT09
PT09PT09PT09PT09PSAKCicsIGN1cmRhdGUoKSwgY3VydGltZSgpLCAnMTEnKTsKRXJyb3IgQ29k
ZSAgICAgICAgICA6IDEwNjQKU3lzdGVtIE1lc3NhZ2UgICAgICA6IFlvdSBoYXZlIGFuIGVycm9y
IGluIHlvdXIgU1FMIHN5bnRheDsgY2hlY2sgdGhlIG1hbnVhbCB0aGF0IGNvcnJlc3BvbmRzIHRv
IHlvdXIgTXlTUUwgc2VydmVyIHZlcnNpb24gZm9yIHRoZSByaWdodCBzeW50YXggdG8gdXNlIG5l
YXIgJ04vQScpIEFTIHVzZXJfdHlwZSwKICAgSUYoT3JkZXJzIElTIE5PVCBOVUxMLE9yZGVycyww
KUFTIE9yZGVycywKICAgSURfdXNlciwKICAgJyBhdCBsaW5lIDIKU2NyaXB0IExvY2F0aW9uICAg
ICA6IC9ob21lL3d3dy9kb21haW5zL2RpcmVrc3lzLmNvbS9jZ2ktYmluL21vZC9hZG1pbi9hZG1p
bgpQZXJsIFZlcnNpb24gICAgICAgIDogNS4wMTgwMDIKU2Vzc2lvbiBJRCAgICAgICAgICA6IDEx
LTU5ODE4MTQ5NzYyNDg0NDY0NDM2OTM2MAoKRm9ybSBWYXJpYWJsZXMgSU4KLS0tLS0tLS0tLS0t
LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQphY3Rpb24gICAgICAgICAgICAgIDogMQpj
bWQgICAgICAgICAgICAgICAgIDogcmVwX2JpX2FsbG9yZGVycwplICAgICAgICAgICAgICAgICAg
IDogMgpmcm9tX2RhdGUgICAgICAgICAgIDogMjAxNy0wNi0wMQpmcm9tX3NhbGVzX2RhdGUgICAg
IDogCmlkX2FkbWluX3VzZXJzICAgICAgOiAKaWRfcHJvZHVjdHMgICAgICAgICA6IAp0b19kYXRl
ICAgICAgICAgICAgIDogMjAxNy0wNi0wMQp0b19zYWxlc19kYXRlICAgICAgIDogCnR5cGUgICAg
ICAgICAgICAgICAgOiBvcmRlcgoKRm9ybSBWYXJpYWJsZXMgRVJST1IKLS0tLS0tLS0tLS0tLS0t
LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQoKRW52aXJvbm1lbnQgVmFyaWFibGVzCi0tLS0t
LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KQ09OVEVOVF9MRU5HVEggICAg
ICA6IDE2NwpDT05URU5UX1RZUEUgICAgICAgIDogYXBwbGljYXRpb24veC13d3ctZm9ybS11cmxl
bmNvZGVkCkNPTlRFWFRfRE9DVU1FTlRfUk9PVDogL2hvbWUvd3d3L2RvbWFpbnMvZGlyZWtzeXMu
Y29tL2NnaS1iaW4vCkNPTlRFWFRfUFJFRklYICAgICAgOiAvY2dpLWJpbi8KRE9DVU1FTlRfUk9P
VCAgICAgICA6IC9ob21lL3d3dy9kb21haW5zL2RpcmVrc3lzLmNvbS9odHRwZG9jcwpHQVRFV0FZ
X0lOVEVSRkFDRSAgIDogQ0dJLzEuMQpIVFRQX0FDQ0VQVCAgICAgICAgIDogdGV4dC9odG1sLGFw
cGxpY2F0aW9uL3hodG1sK3htbCxhcHBsaWNhdGlvbi94bWw7cT0wLjksaW1hZ2Uvd2VicCwqLyo7
cT0wLjgKSFRUUF9BQ0NFUFRfRU5DT0RJTkc6IGd6aXAsIGRlZmxhdGUKSFRUUF9BQ0NFUFRfTEFO
R1VBR0U6IGVzLUVTLGVzO3E9MC44CkhUVFBfQ0FDSEVfQ09OVFJPTCAgOiBtYXgtYWdlPTAKSFRU
UF9DT05ORUNUSU9OICAgICA6IGtlZXAtYWxpdmUKSFRUUF9DT09LSUUgICAgICAgICA6IEluc2lk
ZT1BY3Rpdm87IGNrX3dhcmVob3VzZXMxMT0xMDAxOyBhY29wZW5kaXZpZHM9cGhvbmUsc3VibWVu
dVg7IGFjZ3JvdXBzd2l0aHBlcnNpc3Q9cGhvbmU7IGtwMz0wOyBzZXNzaW9uaWQ9MDsgUEhQU0VT
U0lEPTJpNDc2MDdqdXBuazdnZjZhaXVxN3M4ZGs0OyBzbF9yZXR1cm5zMj0wLDY3MzY3OyBzbF9v
cmRlcnMyPTAsMTAyNzI2NDQsOTAxNzgyMywxMDE3OTgyNSwxMDQwNTM5MCwxMDM4MTMzMywxMDM5
ODM5NywxMDQwNjQxMywxMDM2MzEwMiwxMDQxMzgzNjsgc2xfcmV0dXJuczQ9MCwxMDE1OCwxMDQ1
Mjsgc2xzaWQ9MTEtNTk4MTgxNDk3NjI0ODQ0NjQ0MzY5MzYwOyB2b3hoZWxwPU9uOyBhcHBfZTI9
YWN0aXZlOyBhcHBfZTM9YWN0aXZlOyBhcHBfZTQ9YWN0aXZlOyBhcHBfZTU9YWN0aXZlOyBhcHBf
ZTc9YWN0aXZlOyBhcHBfZTEwPWFjdGl2ZTsgYXBwX2UxMT1hY3RpdmU7IGFwcF9lMTI9YWN0aXZl
OyBhcHBfZTEzPWFjdGl2ZTsgYXBwX2UxNz1hY3RpdmU7IHNsX29yZGVyczQ9MCw2MTcwMTQxLDYx
ODAyODIsNjE5OTc0MDsgZT0yCkhUVFBfSE9TVCAgICAgICAgICAgOiBteC5kaXJla3N5cy5jb20K
SFRUUF9PUklHSU4gICAgICAgICA6IGh0dHA6Ly9teC5kaXJla3N5cy5jb20KSFRUUF9SRUZFUkVS
ICAgICAgICA6IGh0dHA6Ly9teC5kaXJla3N5cy5jb20vY2dpLWJpbi9tb2QvYWRtaW4vYWRtaW4/
Y21kPXJlcF9iaV9hbGxvcmRlcnMKSFRUUF9VUEdSQURFX0lOU0VDVVJFX1JFUVVFU1RTOiAxCkhU
VFBfVVNFUl9BR0VOVCAgICAgOiBNb3ppbGxhLzUuMCAoV2luZG93cyBOVCA2LjE7IFdpbjY0OyB4
NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS81OC4wLjMw
MjkuMTEwIFNhZmFyaS81MzcuMzYKUEFUSCAgICAgICAgICAgICAgICA6IC91c3IvbG9jYWwvc2Jp
bjovdXNyL2xvY2FsL2JpbjovdXNyL3NiaW46L3Vzci9iaW46L3NiaW46L2JpbgpRVUVSWV9TVFJJ
TkcgICAgICAgIDogY21kPXJlcF9iaV9hbGxvcmRlcnMmYWN0aW9uPTEmZnJvbV9kYXRlPTIwMTct
MDYtMDEmdG9fZGF0ZT0yMDE3LTA2LTAxJmZyb21fdGltZT0tLS0mdG9fdGltZT0tLS0mZnJvbV9z
YWxlc19kYXRlPSZ0b19zYWxlc19kYXRlPSZpZF9hZG1pbl91c2Vycz0maWRfcHJvZHVjdHM9JnR5
cGU9b3JkZXIKUkVNT1RFX0FERFIgICAgICAgICA6IDE3Mi4yMC4xOC41MApSRU1PVEVfUE9SVCAg
ICAgICAgIDogNTExNjgKUkVRVUVTVF9NRVRIT0QgICAgICA6IEdFVApSRVFVRVNUX1NDSEVNRSAg
ICAgIDogaHR0cApSRVFVRVNUX1VSSSAgICAgICAgIDogL2NnaS1iaW4vbW9kL2FkbWluL2FkbWlu
ClNDUklQVF9GSUxFTkFNRSAgICAgOiAvaG9tZS93d3cvZG9tYWlucy9kaXJla3N5cy5jb20vY2dp
LWJpbi9tb2QvYWRtaW4vYWRtaW4KU0NSSVBUX05BTUUgICAgICAgICA6IC9jZ2ktYmluL21vZC9h
ZG1pbi9hZG1pbgpTRVJWRVJfQUREUiAgICAgICAgIDogMTcyLjE2LjEuMzgKU0VSVkVSX0FETUlO
ICAgICAgICA6IHBvc3RtYXN0ZXJAaW5vdmF1cy5jb20KU0VSVkVSX05BTUUgICAgICAgICA6IG14
LmRpcmVrc3lzLmNvbQpTRVJWRVJfUE9SVCAgICAgICAgIDogODAKU0VSVkVSX1BST1RPQ09MICAg
ICA6IEhUVFAvMS4xClNFUlZFUl9TSUdOQVRVUkUgICAgOiA8YWRkcmVzcz5BcGFjaGUvMi40Ljcg
KFVidW50dSkgU2VydmVyIGF0IG14LmRpcmVrc3lzLmNvbSBQb3J0IDgwPC9hZGRyZXNzPgoKU0VS
VkVSX1NPRlRXQVJFICAgICA6IEFwYWNoZS8yLjQuNyAoVWJ1bnR1KQoKPC9QUkU+";
	print "<PRE>".decode_base64($print)."</PRE>";
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