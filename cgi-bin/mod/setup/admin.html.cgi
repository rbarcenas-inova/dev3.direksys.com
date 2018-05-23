sub usrgroup_all{
# --------------------------------------------------------
	$va{'searchresults'} = '';
	$in{'drop'} = int($in{'drop'});

	if ($in{'drop'}>0){
		if(!&check_permissions($in{'cmd'}.'_drop','','')){ &html_unauth; return; };
		my ($sth) = &Do_SQL("DELETE FROM admin_groups_perms WHERE ID_admin_groups='0' AND ID_admin_groups_perms=$in{'drop'}");
		&auth_logging('usrgroup_all',0);
	}elsif($in{'action'}){
		$sth = &Do_SQL("SELECT COUNT(*) FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='".&filter_values($in{'type'})."' AND command='".&filter_values($in{$in{'type'}.'_cmd'})."'");
		if ($sth->fetchrow eq 1){
			## OK
			if ($in{'type'} eq 'admin'){
				$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='0', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'admin_cmd'})."' ");
			}else{
				$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='0', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_add'). "'") if ($in{'dbman_add'} eq 'on');
				$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='0', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_view'). "'") if ($in{'dbman_view'} eq 'on');
				$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='0', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_del'). "'") if ($in{'dbman_del'} eq 'on');
				$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='0', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.'_edit'). "'") if ($in{'dbman_edit'} eq 'on');
				$sth = &Do_SQL("SELECT tabs FROM admin_perms WHERE application='".&filter_values($in{'application'})."' AND type='dbman' AND command='".&filter_values($in{'dbman_cmd'})."'");		
				my ($tot_tabs) = $sth->fetchrow;
				if ($tot_tabs>0){
					for my $i(1..$tot_tabs){
						$sth = &Do_SQL("INSERT INTO admin_groups_perms SET ID_admin_groups='0', application='".&filter_values($in{'application'})."',  command='".&filter_values($in{'dbman_cmd'}.$i)."' ") if ($in{'dbman_tab'.$i} eq 'on');
					}
				}
			}
			$va{'message'} = &trans_txt('record_added');
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	}
	## ITEMS LIST
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($d);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_groups_perms WHERE ID_admin_groups='0'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM admin_groups_perms WHERE ID_admin_groups='0' ORDER BY command DESC ");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM admin_groups_perms WHERE ID_admin_groups='0' ORDER BY command DESC LIMIT $first,$usr{'pref_maxh'};");			
		}
	
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|<td class='smalltext' valign='top' nowrap>
								<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=usrgroup_all&nh=$in{'nh'}&drop=$rec->{'ID_admin_groups_perms'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
								 $rec->{'application'}</td>\n|;
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'command'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('usrgroup_all.html');
}


sub test_mandrill{

	my $from_mail = 'info@inova.com.mx';
	my $to_mail = 'rbarcenas@denacom.com,roberto.barcenas@gmail.com,ltorres@inova.com.mx,adiaz@inovaus.com, rbarcenas@inovaus.com';
	my $subject_mail = 'Testing Email RB';
	my $body_mail = '<h3>Testing Mandrill SMTP</h3>';
	my $text_mail = 'Testing Text';
	my $res = send_mandrillapp_email($from_mail,$to_mail,$subject_mail,$body_mail,$text_mail,'none');

	print "Content-type: text/html\n\n";
	print $res->{'status'};


}

1;

