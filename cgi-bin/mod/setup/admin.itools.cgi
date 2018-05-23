##################################################################
#     TOOLS   	#
##################################################################
sub itools{
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){

		my ($err);
		$in{'ping_count'} = int($in{'ping_count'});
		if ($in{'chkinet'}){
			$in{'ping_count'} = 5;
			$in{'address'} = "denabox.com";
		}elsif(!$in{'address'} or !$in{'ping_count'}){
			++$err;
		}
		
		if ($err>0){
			$va{'message'} = &trans_txt('itools_invalidip');
			$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
		}else{
			my ($cmd) = "ping -c $in{'ping_count'} '$in{'address'}'";
			if (open(UTIL, "$cmd 2>&1|")){
				while(<UTIL>){
					$va{'cmd_result'} .= $_
				}
			}
			$va{'cmd_result'} =~ s/\n/<br>/g;
		}
		
		if ($in{'chkinet'}){
			delete($in{'ping_count'});
			delete($in{'address'});
		}
		
	}else{
		$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('itools.html');
	
}

##################################################################
#     TOOLS  : MY IP  	#
##################################################################
sub itools_myip{
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){

		## Get SIT PBX version
		use LWP::UserAgent;
		my ($results,$new_ver);
		my ($ua) = new LWP::UserAgent;
		$ua->timeout(10);
		$ua->agent("Mozilla/8.0"); # pretend we are very capable browser
		my ($req) = new HTTP::Request 'GET' => "http://admin.denabox.com/cgi-bin/check/admin?myip=1";
		$req->header('Accept' => 'text/html');

		# send request
		$res = $ua->request($req);

		# check the outcome
		if ($res->is_success) {
			$va{'getip'} = $res->content;
		}else{
			$va{'getip'} = &trans_txt("itools_getip_error");
		}
	}else{
		$va{'getip'} = "<input type='submit' name='action' value='".&trans_txt('itools_getip')."' class='button'>";
	}
	  print "Content-type: text/html\n\n";
	  print &build_page('itools_myip.html');
}

sub itools_trace{
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){
		my ($err);
		if (!$in{'address'}){
			++$err;
		}elsif ($in{'address'} !~ /^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$/ and $in{'address'} =~ /[^\w\.]/){
			++$err;
		}
		if ($err>0){
			$va{'message'} = &trans_txt('itools_invalid');
			$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
		}else{
			my ($cmd) = "traceroute '$in{'address'}'";
			if (open(UTIL, "$cmd 2>&1|")){
				while(<UTIL>){
					$va{'cmd_result'} .= $_
				}
			}
			$va{'cmd_result'} =~ s/\n/<br>/g;
		}
	}else{
		$va{'trace_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
	}
	  print "Content-type: text/html\n\n";
	  print &build_page('itools_trace.html');
  
}

##################################################################
#     TOOLS : WHO IS  	#
##################################################################
sub itools_whois{
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){

		my ($err);
		if (!$in{'address'}){
			++$err;
		}elsif ($in{'address'} !~ /^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$/ and $in{'address'} =~ /[^\w\.]/){
			++$err;
		}
		
		if ($err>0){
			$va{'message'} = &trans_txt('itools_invalid');
			$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
		}else{
			my ($cmd) = "whois '$in{'address'}'";
			if (open(UTIL, "$cmd 2>&1|")){
				while(<UTIL>){
					$va{'cmd_result'} .= $_
				}
			}
			$va{'cmd_result'} =~ s/\n/<br>/g;
		}
		
	}else{
		$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
	}
	
	  print "Content-type: text/html\n\n";
	  print &build_page('itools_whois.html');
}

##################################################################
#     TOOLS : DNS  	#
##################################################################
sub itools_dns{
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){

		my ($err);
		if (!$in{'address'}){
			++$err;
		}elsif ($in{'address'} !~ /^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$/ and $in{'address'} =~ /[^\w\.]/){
			++$err;
		}
		
		if ($err>0){
			$va{'message'} = &trans_txt('itools_invalid');
			$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
		}else{
			%type = ('NS'=>'-t NS','MX'=>'-t MX','PTR'=>'-x');
			my ($cmd) = "dig $type{$in{'type'}} '$in{'address'}'";
			if (open(UTIL, "$cmd 2>&1|")){
				while(<UTIL>){
					$va{'cmd_result'} .= $_
				}
			}
			$va{'cmd_result'} =~ s/\n/<br>/g;
		}
		
	}else{
		$va{'cmd_result'} = "<p>&nbsp;</p><p align='center'>".&trans_txt('itools_noresult')."</p><p>&nbsp;</p>";
	}
	  print "Content-type: text/html\n\n";
	  print &build_page('itools_dns.html');
}

1;
