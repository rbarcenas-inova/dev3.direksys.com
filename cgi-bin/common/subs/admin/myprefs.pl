####################################################################
#   MY PREFS   #
####################################################################
sub myprefs {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
# Last Modified RB: 04/08/09  17:41:35 -- Se agrego screenres como preferencia del usuario

	# 'pref_language','pref_style',
	$in{'extension'} = (!$in{'action'})? &load_name("admin_users","ID_admin_users",$usr{'id_admin_users'},"extension") : $in{'extension'} ;
	$in{'username_ref'} = (!$in{'action'})? &load_name("admin_users","ID_admin_users",$usr{'id_admin_users'},"username_ref") : $in{'username_ref'};

	my (@db_cols) = ('username_ref','pref_table_width','application','pref_maxh','pref_newmsg');
	if ($in{'msg'}){
		$va{'message'} = &trans_txt($in{'msg'});
		 for my $i(0..$#db_cols) {
	   	 	$in{$db_cols[$i]} = $usr{$db_cols[$i]};
		 }		
	}elsif($in{'action'}){

		$in{'pref_table_width'} = $in{'table_width'};
		$in{'pref_maxh'} = int($in{'pref_maxh'});
		$in{'application'} = $in{'multiapp'};
		($usr{'multiapp'} !~ /$in{'multiapp'}/) and (delete($in{'application'}));
		
		# !$in{'pref_language'} or !$in{'pref_style'} or 
		if (!$in{'pref_maxh'} or !$in{'pref_table_width'} or !$in{'application'} or !$in{'application'}){
			for my $i(0..$#db_cols-1) {
				if (!$in{$db_cols[$i]}){
					$error{$db_cols[$i]} = &trans_txt('required');
				}
			}
			$va{'message'} = &trans_txt("reqfields");
		}else{

			$query = '';
			for my $i(0..$#db_cols) {
			    $query .= "$db_cols[$i]='".$in{$db_cols[$i]}."',";
			}
			chop($query);

			$query .= ($in{'extension'} ne '')? ",extension='$in{'extension'}'":"";
			
			my ($sth) = &Do_SQL("UPDATE admin_users SET $query WHERE ID_admin_users=$usr{'id_admin_users'}");
			$va{'message'} = &trans_txt("prefsupdated");
			for my $i(0..$#db_cols) {
			    $usr{$db_cols[$i]}=$in{$db_cols[$i]};
			}
			$usr{'table_width'} = $in{'table_width'};
			&save_auth_data;
			$va{'message'} = &trans_txt("prefsupdated");
			&auth_logging("prefsupdated",'');
			$va{'reload'} = "parent.location.href ='/cgi-bin/mod/$usr{'application'}/admin?cmd=myprefs&msg=prefsupdated';";
		}
	}else{
		 for my $i(0..$#db_cols) {
	   	 	$in{$db_cols[$i]} = $usr{$db_cols[$i]};
		 }
	}

	print "Content-type: text/html\n\n";
	print &build_page('myprefs.html');
  
}

##################################################################
#     MY PREFS : MY PASSWORD   	#
##################################################################
sub myprefs_mypass {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
#Last modified on 16 Dec 2010 11:00:56
#Last modified by: MCC C. Gabriel Varela S. :Se cambia de crypt a sha1
#Last modified on 17 Dec 2010 13:51:36
#Last modified by: MCC C. Gabriel Varela S. :Se actualiza también campo de tabla change_pass a No
	if ($in{'action'}){
		if ($in{'oldpass'}){
			undef($pass);
			use Digest::SHA1;
			my $sha1= Digest::SHA1->new;
			#$sha1->add($in{'oldpass'});
			#my $password = $sha1->hexdigest;
			my ($sth) = &Do_SQL("SELECT Password FROM admin_users WHERE ID_admin_users=$usr{'id_admin_users'} AND Password=sha1('$in{'oldpass'}');");
			my ($pass) = $sth->fetchrow();
			#if ((length($pass)==13 and $pass eq crypt($in{'oldpass'},substr(crypt($in{'oldpass'},'ns'),3,7)))or(length($pass)==40 and $pass=$password)){
			if( $pass and $pass ne '' ){
				if ($in{'newpass1'} eq $in{'newpass2'} and length($in{'newpass1'})>=8 and length($in{'newpass1'})<=16){
					$sha1->reset;
					$sha1->add($in{'newpass1'});
					my ($cpass) = $sha1->hexdigest;

					if( $pass ne $cpass ){

						### Inicializa la transaccion
						#&Do_SQL("START TRANSACTION;");

						my $days_exp = $cfg{'days_expiration_pwd'};
						$days_exp = 30 if(!$days_exp);
						
						
						$va{'message'} = &trans_txt("password_updated");
						# cgierr($cfg{'multiserver'});
						# cgierr($cfg{'multiserver'});
						if($cfg{'multiserver'}){
							use JSON;
							use LWP::UserAgent;
							use Data::Dumper;
							my %response;
							if($in{'newpass1'}){
								# &cgierr($in{'newpass1'});
								my $username = &Do_SQL("SELECT username FROM admin_users WHERE id_admin_users = $usr{'id_admin_users'}")->fetchrow();
								my $ua = LWP::UserAgent->new;
								my %parameters = (
									'new_password' => "$in{'newpass1'}"
								);


								my $req = HTTP::Request->new(POST => $cfg{'api_url'}."user/$username");
								$req->header('Content-Type' => 'application/json');
								$req->header('Authorization' => "Bearer $cfg{'api_getinvoice_token'}");
								 
								# add POST data to HTTP request bodys
								my $post_data = encode_json \%parameters;

								$req->content($post_data);
								 
								my $resp = $ua->request($req);
								if ($resp->is_success) {
									my $obj = eval { decode_json $resp->decoded_content } // {};
								}
							}


						}else{
							my ($sth) = &Do_SQL("UPDATE admin_users SET Password='".&filter_values($cpass)."',change_pass='No', expiration = DATE_ADD(CURDATE(), INTERVAL $days_exp DAY), tempPasswd=NULL WHERE ID_admin_users=$usr{'id_admin_users'}");
							$usr{'change_pass'}='No';
							&save_auth_data;
							&chg_multipass(&load_name("admin_users","ID_admin_users",$usr{'id_admin_users'},"userName"),$cpass,$days_exp);
						}			
						&auth_logging("password_updated",'');	
						print 'Location: /cgi-bin/mod/'.$usr{'application'}.'/admin?logoff=1';					


						### Finaliza la transaccion
						#&Do_SQL("COMMIT;");
					}else{
						$va{'message'} = &trans_txt("invalid_new_pass");
					}
				}else{
					$va{'message'} = &trans_txt("invalid_new_pass");
				}
			}else{
				$va{'message'} = &trans_txt("invalid_old_pass");
			}
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('myprefs_mypass.html');
}


##################################################################
#     MY PREFS : WEB PAGE   	#
##################################################################
sub myprefs_wpage {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	if ($in{'action'}){
		my ($sth) = &Do_SQL("UPDATE admin_users SET pref_wpage='$in{'pref_wpage'}' WHERE ID_admin_users=$usr{'id_admin_users'}");
		$va{'message'} = &trans_txt("prefsupdated");
		$usr{'pref_wpage'} = $in{'pref_wpage'};
		&save_auth_data;
		&auth_logging("pageprefs_wpage",'');
	}
	
	$in{'pref_wpage'} = $usr{'pref_wpage'};

  print "Content-type: text/html\n\n";
  print &build_page('myprefs_wpage.html');
}


##################################################################
#     MY PREFS : MY LOG   	#
##################################################################
sub myprefs_mlogs {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	&connect_db;
	$sth = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE ID_admin_users='$usr{'id_admin_users'}';");
	$va{'matches'} = $sth->fetchrow();

	if ($va{'matches'}>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		($va{'pageslist'},$in{'qs'}) = &pages_list($in{'nh'},"$cfg{'path_ns_cgi'}$cfg{'path_ns_cgi_sitadmin'}", $va{'matches'}, $usr{'pref_maxh'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE admin_logs.ID_admin_users='$usr{'id_admin_users'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'LogDate'}."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})." $rec->{'Action'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}

	}else{
		$va{'searchresults'} = "		<tr>\n		    <td align='center' colspan='6'><p>&nbsp;</p>" . trans_txt('search_nomatches') . "<p>&nbsp;</p></td>\n		 </tr>\n";
		$va{'pageslist'} = 0;
		$va{'matches'}     = 0;
	}
	print "Content-type: text/html\n\n";
	print &build_page('myprefs_mlogs.html');
}


1;
