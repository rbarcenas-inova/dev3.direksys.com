
##################################################################
#         ADMINISTRATION : USERS    	    #
##################################################################
sub usrman_admin {
# --------------------------------------------------------
# Forms Involved: man_users_userinfo.html & man_users_admin.html
# Created on: 9/07/2007 2:51PM
# Last Modified on:
# Last Modified by:
# Author: Rafael Sobrino
# Description : Searches for a user and allows the administrator to change the password. 
#               It writes the encrypted password to the admin_users table. 
# Last Modification by JRG : 03/09/2009 : Se agrega log
#Last modified on 16 Dec 2010 10:54:58
#Last modified by: MCC C. Gabriel Varela S. :Se incorpora nueva forma de encrypción
#Last modified on 17 Dec 2010 13:58:38
#Last modified by: MCC C. Gabriel Varela S. :Se actualiza también campo change_pass a Yes

	print "Content-type: text/html\n\n";

	if ($in{'search'} and !$in{'id_admin_users'}){
		$va{'message'} = trans_txt("empty_user_id");
		print &build_page('man_users_admin.html');
		return;
	}	

	if ($in{'id_admin_users'}){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users WHERE ID_admin_users='$in{'id_admin_users'}'");
		$va{'matches'} = $sth->fetchrow;		
		
		if ($va{'matches'}>0){

			my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE ID_admin_users='$in{'id_admin_users'}'");
			$rec = $sth->fetchrow_hashref;	
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('/cgi-bin/mod/[ur_application]/dbman?cmd=usrman&view=$rec->{'ID_admin_users'}')\">\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_admin_users'}</td>\n";			
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Username'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'FirstName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'email'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'MultiApp'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";

			if ($in{'chgpasswd'} and $in{'passwd'} eq ""){
				$va{'message'} = &trans_txt("no_passwd");
			}elsif($in{'chgpasswd'} and $in{'passwd'} ne ""){

				####
				#### Cambio de Password
				####

				my ($password);
				
				use Digest::SHA1;
				my $sha1= Digest::SHA1->new;
				$sha1->add($in{'passwd'});
				$password = $sha1->hexdigest;

				my $days_exp = 3;
				if($cfg{'multiserver'}){
					use JSON;
					use LWP::UserAgent;
					use Data::Dumper;
					my %response;
					if($in{'passwd'}){
						# my $ua = LWP::UserAgent->new;
						# my %parameters = {
						# 	'new_password' => "$in{'passwd'}"
						# };
						# my $response = $ua->post(
						# 	$cfg{'api_url'},
						# 	'Content-Type' 	=> 'application/json',
						# 	'Authorization' => "Bearer $cfg{'api_getinvoice_token'}",
				  #   		'Content' 		=> encode_json \%parameters
						# );
						# my $obj = eval { decode_json $response->content } // {};
						# &cgierr(Dumper $obj);
						my $username = &Do_SQL("SELECT username FROM admin_users WHERE id_admin_users = $usr{'id_admin_users'}")->fetchrow();
						my $ua = LWP::UserAgent->new;
						my %parameters = (
							'new_password' => "$in{'passwd'}"
						);


						my $req = HTTP::Request->new(POST => $cfg{'api_url'}."user/$username");
						$req->header('Content-Type' => 'application/json');
						$req->header('Authorization' => "Bearer $cfg{'api_getinvoice_token'}");
						 
						# add POST data to HTTP request body
						my $post_data = encode_json \%parameters;

						$req->content($post_data);
						 
						my $resp = $ua->request($req);
						if ($resp->is_success) {
							my $obj = eval { decode_json $resp->decoded_content } // {};
						}
					}

				}else{
					my ($sth) = &Do_SQL("UPDATE admin_users SET password='$password',tempPasswd='".&filter_values($in{'passwd'})."',change_pass='Yes', expiration = DATE_ADD(CURDATE(), INTERVAL $days_exp DAY) WHERE ID_admin_users='$in{'id_admin_users'}'");
					&chg_multipass(&load_name("admin_users","ID_admin_users",$in{'id_admin_users'},"userName"), $password, $days_exp, 2, $in{'passwd'});
				}				
				&auth_logging('passwd_updated',"");
				$va{'message'} = &trans_txt("passwd_updated");
				$in{'passwd'} = "";

			}
			print &build_page('man_users_userinfo.html');
			return;
		}else{
			$va{'message'} = trans_txt("user_not_found").": $in{'id_admin_users'}";
			$in{'id_admin_users'}="";
		}	
	}else{
		$va{'message'} = "";		
	}

	print &build_page('man_users_admin.html');
}

1;