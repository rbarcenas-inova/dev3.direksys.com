#!/usr/bin/perl

##################################################################
############                HELP                 #################
##################################################################
sub help {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('help:'.$in{'page'}.'.html');
}


##################################################################
############                ORDERS                 #################
##################################################################
sub opr_orders {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('opr_orders_home.html');
}

sub rep_orders {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('orders.html');
}


##################################################################
############                HELP                 #################
##################################################################

sub invoices {
	print "Content-type: text/html\n\n";
	my $orders_data = &Do_SQL("SELECT cu_invoices.* from cu_invoices inner join cu_invoices_lines using(ID_invoices) where id_orders = $in{'id_orders'} limit 1")->fetchrow_hashref();
	my %hash = %{$orders_data};
	%in = (%hash, %in);
	$in{'id_invoices'} = $in{'ID_invoices'};
	get_invoice_data();
	print &build_page('invoices.html');
}

sub rd{
	print "Content-type: text/html\n\n";
	print &build_page('reference_deposit.html');
}

sub msglist {
# --------------------------------------------------------
	if ($in{'action'}){
		$va{'message'} = &trans_txt('msgd_nomsgs');
	}
	print "Content-type: text/html\n\n";
	(!$in{'page'}) and ($in{'page'} = 'home');
	print &build_page('msgs_search.html');
}



##################################################################
############          GENERAL COMMANDS           #################
##################################################################
sub mypass {
# --------------------------------------------------------
#Last modified on 16 Dec 2010 11:16:39
#Last modified by: MCC C. Gabriel Varela S. :Se cambia crypt por sha1
#Last modified on 17 Dec 2010 14:02:02
#Last modified by: MCC C. Gabriel Varela S. :Se actualiza también campo de tabla change_pass a 'No'
	if ($in{'action'}){
        ### Check Permissions
        #GV Modificación: Se incluye segundo parámetro a la función _ccinb
		if ($in{'oldpass'}){
			use Digest::SHA1;
			my $sha1= Digest::SHA1->new;
			$sha1->add($in{'oldpass'});
			my $password = $sha1->hexdigest;
			my ($sth) = &Do_SQL("SELECT Password FROM admin_users WHERE ID_admin_users=$usr{'id_admin_users'}");
			my ($pass) = $sth->fetchrow();
			if ((length($pass)==13 and $pass eq crypt($in{'oldpass'},substr(crypt($in{'oldpass'},'ns'),3,7)))or(length($pass)==40 and $pass=$password)){
				if ($in{'newpass1'} eq $in{'newpass2'} and length($in{'newpass1'})>=5 and length($in{'newpass1'})<=10){
					$sha1->reset;
					$sha1->add($in{'newpass1'});
					my ($cpass) = $sha1->hexdigest;
					my ($sth) = &Do_SQL("UPDATE admin_users SET Password='".&filter_values($cpass)."',change_pass='No' WHERE ID_admin_users=$usr{'id_admin_users'}");
					$usr{'change_pass'}='No';
					&save_auth_data;
					$va{'message'} = &trans_txt("password_updated");
					&auth_logging("password_updated",'');
					&chg_multipass(&load_name("admin_users","ID_admin_users",$usr{'id_admin_users'},"userName"),$cpass);
				}else{
					$va{'message'} = &trans_txt("invalid_new_pass");
				}
			}else{
				$va{'message'} = &trans_txt("invalid_old_pass");
			}
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page("mypass.html");
}

sub mylogs {
# --------------------------------------------------------
    ### Check Permissions


	&connect_db;
	$sth = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE ID_admin_users='$usr{'id_admin_users'}';");
	$va{'matches'} = $sth->fetchrow();

	if ($va{'matches'}>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		($va{'pageslist'},$in{'qs'}) = &pages_list($in{'nh'},"$cfg{'path_ns_cgi'}$cfg{'path_ns_cgi_admin'}", $va{'matches'}, $usr{'pref_maxh'});
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
	print &build_page("mylogs.html");
}


##################################################################
############                HELP                 #################
##################################################################
sub help {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	print &build_page("help.html");
}


	
1;

