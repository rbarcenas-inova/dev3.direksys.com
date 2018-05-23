#####################################################################
########                   NON INVENTORY	                   ########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq '6'){
		## Logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'admin_users';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
	$va{'addbtn'} = qq|<a href='javascript:trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_admin_users]&tab=[in_tab]&addperm=1")'><img src='[va_imgurl]/[ur_pref_style]/b_add.gif' title='Add User' alt='' border='0'></a>&nbsp;|;
	$va{'display_special_perm'} = 'display:none;';
	
	if ($in{'addperm'}){

		$va{'display_perm'} = '';
		if(!&check_permissions($in{'cmd'},'_addperm','')){ return &html_unauth_tab; };
		$va{'new_tbname'} = 'usrman_tab1_add';

	}if ($in{'addspecialperm'}){

		$va{'display_special_perm'} = '';
		$va{'display_perm'} = 'display:none;';
		
		## Special perms
		if(!&check_permissions($in{'cmd'},'_addperm','')){ return &html_unauth_tab; };
		$va{'new_tbname'} = 'usrman_tab1_add';

	}


	## Perms
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users_perms WHERE ID_admin_users='$in{'id_admin_users'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM admin_users_perms WHERE ID_admin_users='$in{'id_admin_users'}' ORDER BY command DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= qq|   <td class='smalltext'>
						<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=usrman&nh=$in{'nh'}&tab=1&view=$in{'id_admin_users'}&drop=$rec->{'ID_admin_users_perms'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>
						$rec->{'command'}</td>\n|;
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'application'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	

	## Tables Header/Titles
	&load_db_fields_values($in{'db'},'ID_admin_users',$in{'id_admin_users'},'*');
}

sub load_tabs2 {
# --------------------------------------------------------
	## Perms
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_users_groups WHERE ID_admin_users='$in{'id_admin_users'}'");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT admin_users_groups.id_admin_users_perms, admin_groups.ID_admin_groups, admin_groups.Name FROM admin_users_groups LEFT JOIN admin_groups ON admin_users_groups.ID_admin_groups=admin_groups.ID_admin_groups WHERE admin_users_groups.ID_admin_users='$in{'id_admin_users'}' ORDER BY Name DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			## FC > Agregar opcion para sacar de grupo a user
			my $deleteButton = '';
			if(&check_permissions('user_group_edit','','')){
				$deleteButton .= qq|
					<a href="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=userman_tab2&action=drop&id=$rec->{'id_admin_users_perms'}" data-type="ajax">
					<img border="0" alt=""  title="Drop" src="/sitimages//default/b_drop.png">
					</a>|
			}
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$deleteButton &nbsp; $rec->{'ID_admin_groups'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='2' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
			
									
	}	

	## Tables Header/Titles
	&load_db_fields_values($in{'db'},'ID_admin_users',$in{'id_admin_users'},'*');
}


sub load_tabs3 {
# --------------------------------------------------------
	## Logs
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE Type='Access' AND ID_admin_users='$in{'id_admin_users'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM admin_logs LEFT JOIN admin_users ON admin_logs.ID_admin_users=admin_users.ID_admin_users WHERE Type='Access' AND admin_logs.ID_admin_users='$in{'id_admin_users'}' ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
			
									
	}	
				

	## Tables Header/Titles
	#&load_db_fields_values($in{'db'},'ID_admin_users',$in{'id_admin_users'},'*');
}

sub load_tabs4 {
# --------------------------------------------------------
	## Logs
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE Type<>'Access' AND ID_admin_users='$in{'id_admin_users'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM admin_logs LEFT JOIN admin_users ON admin_logs.ID_admin_users=admin_users.ID_admin_users WHERE Type<>'Access' AND admin_logs.ID_admin_users='$in{'id_admin_users'}' ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
			
									
	}	
				

	## Tables Header/Titles
	#&load_db_fields_values($in{'db'},'ID_admin_users',$in{'id_admin_users'},'*');
}

sub load_tabs5 {
# --------------------------------------------------------	
	## POS
    $va{'new_tbname'} = 'usrman_tab5_add';

    my $sql1 = &Do_SQL("SELECT sl_vars.VValue, sl_vars.Subcode
			FROM sl_vars 
			WHERE vname LIKE 'pos_config_$in{'id_admin_users'}'");
	$vars = $sql1->fetchrow_hashref;
	$va{'update_customer'} = $vars->{'VValue'};
	$va{'update_warehouses'} = $vars->{'Subcode'};

    if ($in{'addpos'}){

    	$sql = &Do_SQL("SELECT COUNT(sl_vars.ID_vars) 
			FROM sl_vars 
			WHERE vname LIKE 'pos_config_$in{'id_admin_users'}'");

    	if ($sql->fetchrow == 0) {
    		&Do_SQL("INSERT INTO sl_vars 
    			(VName,VValue,Subcode) 
    			VALUES( 'pos_config_".$in{'id_admin_users'}."' ,".$in{'id_admin_users'}.", ".&filter_values($in{'update_warehouses'}).") ");            		
    	}else{
    		&Do_SQL("UPDATE sl_vars SET VName = 'pos_config_".$in{'id_admin_users'}."' , VValue = ".$in{'id_admin_users'}." , Subcode = ".&filter_values($in{'update_warehouses'})." WHERE VName = 'pos_config_".$in{'id_admin_users'}."' ");            	    		    	 			
    	}    	
    }
}



sub load_tabs7 {

	my $sql = "SELECT
				(SELECT name FROM sl_accounts WHERE ID_accounts = ID_accounts_debit) ID_accounts_debit,
				(SELECT name FROM sl_accounts WHERE ID_accounts = ID_accounts_credit) ID_accounts_credit,
				(SELECT name FROM sl_accounts WHERE ID_accounts = ID_accounts_debit_pettycash) ID_accounts_debit_pettycash
				FROM sl_expenses_users WHERE ID_admin_users = $in{'id_admin_users'} and Status='Active';";
	my ($sth) = &Do_SQL($sql);
	( $id_debit, $id_credit, $id_debit_pettycash ) = $sth->fetchrow;

	$id_debit 				= ($id_debit) ? $id_debit : '---';
	$id_credit 				= ($id_credit) ? $id_credit : '---';
	$id_debit_pettycash 	= ($id_debit_pettycash) ? $id_debit_pettycash : '---';

	$va{'searchresults'} = qq|<tr><td width="33%">$id_debit</td><td width="33%">$id_credit</td><td width="33%">$id_debit_pettycash</td></tr>|;

}

1;