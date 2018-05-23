##########################################################
##		MERCHANDISING : VENDORS
##########################################################
sub loaddefault_mer_vendors {
	$in{'adjustment'} = 'No';
}

sub view_mer_vendors {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 1/1/2007 9:43AM
# Last Modified on:
# Last Modified by:
# Author: 
# Description : 
# Parameters : 

	my $err;
	my (@cols) = ('FirstName','LastName1','LastName2','Title','Phone','Mobile','Fax','Email','im','Status');
	if ($in{'drop_contact'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_vendors_contacts WHERE ID_vendors_contacts='$in{'drop_contact'}';");
		$va{'message'} = &trans_txt('mer_vendors_contact_del');
		&auth_logging('mer_vendors_contact_del',$in{'id_vendors'});		
	}elsif($in{'drop_categ'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_vendors_categories WHERE ID_vendors_categories='$in{'drop_categ'}';");
		$va{'message'} = &trans_txt('mer_vendors_category_del');
		&auth_logging('mer_vendors_category_del',$in{'id_vendors'});	
	}elsif($in{'action'} eq 'add_contact'){
		if (!$in{'contact_firstname'} or !$in{'contact_lastname1'} or !$in{'contact_phone'}){
			$va{'message'} = &trans_txt('mer_vendors_contact_err').'<br>'.&trans_txt('reqfields');
		}else{
			my ($query);
			for (0..$#cols){
				$query .= $cols[$_] . "='".&filter_values($in{'contact_'.lc($cols[$_])}) ."',"
			}
			chop($query);
			my ($sth) = &Do_SQL("INSERT INTO sl_vendors_contacts SET ID_vendors='$in{'id_vendors'}',$query,Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
			$va{'message'} = &trans_txt('mer_vendors_contact_ok');
			&auth_logging('mer_vendors_contact_ok',$in{'id_vendors'});
		}
	}elsif($in{'action'} eq 'update_contact'){
		if ($in{'update'}){
			if (!$in{'contact_firstname'} or !$in{'contact_lastname1'} or !$in{'contact_phone'}){
				$va{'message'} = &trans_txt('mer_vendors_contact_err').'<br>'.&trans_txt('reqfields');
			}else{
				my ($query);
				for (0..$#cols){
					$query .= $cols[$_] . "='".&filter_values($in{'contact_'.lc($cols[$_])}) ."',"
				}
				chop($query);
				my ($sth) = &Do_SQL("UPDATE sl_vendors_contacts SET $query WHERE ID_vendors_contacts='$in{'id_vendors_contacts'}';");
				$va{'message'} = &trans_txt('mer_vendors_contact_updated');
				&auth_logging('mer_vendors_contact_updated',$in{'id_vendors'});
			}
		}
	}elsif($in{'action'} eq 'add_category'){
		if (!$in{'id_categories'}){
			$va{'message'} = &trans_txt('mer_vendors_category_err').'<br>'.&trans_txt('reqfields');
		}else{
			my ($sth) = &Do_SQL("INSERT INTO sl_vendors_categories SET ID_vendors='$in{'id_vendors'}',ID_categories='$in{'id_categories'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
			$va{'message'} = &trans_txt('vendors_category_ok');
			&auth_logging('mer_vendors_category_ok',$in{'id_vendors'});
		}
	}
		
	## load Contacts
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT sl_vendors_contacts.*, admin_users.Username 
						 FROM sl_vendors_contacts 
						 	LEFT JOIN admin_users ON sl_vendors_contacts.Email = admin_users.Email
						 		AND sl_vendors_contacts.`Status` = 'Active' 
						 		AND sl_vendors_contacts.Email != ''
						 	LEFT JOIN admin_users_vendors ON admin_users.ID_admin_users = admin_users_vendors.id_admin_users
						 		AND sl_vendors_contacts.ID_vendors = admin_users_vendors.id_vendors
						 WHERE sl_vendors_contacts.ID_vendors = '$in{'id_vendors'}';");
	while ($rec = $sth->fetchrow_hashref){
		my $drop_cont = qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$in{'id_vendors'}&drop_contact=$rec->{'ID_vendors_contacts'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a> | if (&check_permissions($in{'cmd'},'_edit',''));
		$d = 1 - $d;
		$va{'contacts'} .= qq|
		<tr bgcolor='$c[$d]'>
			<td class="smalltext">
			  <a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=mer_vendors_contact&id_vendors=$in{'id_vendors'}&id_vendors_contacts=$rec->{'ID_vendors_contacts'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='Edit' alt='' border='0'></a>			
				$drop_cont	
			</td>
			<td class="smalltext">$rec->{'ID_vendors_contacts'}</td>
			<td class="smalltext">$rec->{'FirstName'} $rec->{'LastName1'} $rec->{'LastName2'}</td>
			<td class="smalltext">$rec->{'Title'}</td>
			<td class="smalltext">$rec->{'Phone'}</td>
			<td class="smalltext">$rec->{'Mobile'}</td>
			<td class="smalltext">$rec->{'Fax'}</td>
			<td class="smalltext">$rec->{'Email'}</td>
			<td class="smalltext">$rec->{'Status'}</td>
			<td class="smalltext">$rec->{'Username'}</td>
		</tr>
		|;
	}
	
	(!$va{'contacts'}) and ($va{'contacts'} = "<tr><td align='center' colspan='7'>".&trans_txt('mer_vendors_nocontact')."</td></tr>\n");
	
	## Load categories
	my (@c) = split(/,/,$cfg{'srcolors'});
	#my ($sth) = &Do_SQL("SELECT sl_categories.ID_categories,sl_categories.Title FROM sl_vendors_categories,sl_categories WHERE ID_vendors='$in{'id_vendors'}' AND sl_categories.ID_categories=sl_vendors_categories.ID_categories;");
	my ($sth) = &Do_SQL("SELECT * FROM sl_vendors_categories,sl_categories WHERE ID_vendors='$in{'id_vendors'}' AND sl_categories.ID_categories=sl_vendors_categories.ID_categories;");
	while ($rec = $sth->fetchrow_hashref){
	#while (@rec = $sth->fetchrow_array()){
		$d = 1 - $d;
		my $drop_cat = qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_vendors&view=$in{'id_vendors'}&drop_categ=$rec->{'ID_vendors_categories'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a> | if (&check_permissions($in{'cmd'},'_edit',''));
		$va{'categories'} .= qq|
		<tr bgcolor='$c[$d]'>
			<td class="smalltext">	
					$drop_cat				
					($rec->{'ID_categories'}) $rec->{'Title'}</td>
		</tr>
		|;
	}
	if ($in{'id_accounts_debit'} and $in{'id_accounts_debit'} > 0 and $in{'id_accounts_credit'} and $in{'id_accounts_credit'} > 0) {
		my ($sth) = &Do_SQL("
				SELECT 
				sl_accounts.ID_accounts,
				IF(CHAR_LENGTH(sl_accounts.ID_accounting) = 8,
					CONCAT(LEFT(sl_accounts.ID_accounting,3),'-',SUBSTRING(sl_accounts.ID_accounting,4,2),'-',RIGHT(sl_accounts.ID_accounting,3)),
					sl_accounts.ID_accounting
				) AS ID_accounting, 
				sl_accounts.Name Account
				FROM sl_accounts 
				WHERE sl_accounts.ID_accounts = ".$in{'id_accounts_debit'}."

				UNION ALL

				SELECT 
				sl_accounts.ID_accounts,
				IF(CHAR_LENGTH(sl_accounts.ID_accounting) = 8,
					CONCAT(LEFT(sl_accounts.ID_accounting,3),'-',SUBSTRING(sl_accounts.ID_accounting,4,2),'-',RIGHT(sl_accounts.ID_accounting,3)),
					sl_accounts.ID_accounting
				) AS ID_accounting, 
				sl_accounts.Name Account
				FROM sl_accounts 
				WHERE sl_accounts.ID_accounts = ".$in{'id_accounts_credit'}.";"
				);
		while ($rec = $sth->fetchrow_hashref){
			if ($rec->{'ID_accounts'} == $in{'id_accounts_debit'}) {
				$va{'debit_accounting'} = $rec->{'ID_accounting'}.' '.$rec->{'Account'}.qq| (<a href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=fin_accounts&view=|.$in{'id_accounts_debit'}.qq|">|.$in{'id_accounts_debit'}.qq|</a>)|;
			} elsif ($rec->{'ID_accounts'} == $in{'id_accounts_credit'}){
				$va{'credit_accounting'} = $rec->{'ID_accounting'}.' '.$rec->{'Account'}.qq| (<a href="/cgi-bin/mod/|.$usr{'application'}.qq|/dbman?cmd=fin_accounts&view=|.$in{'id_accounts_credit'}.qq|">|.$in{'id_accounts_credit'}.qq|</a>)|;
			}
		}
	}

	(!$va{'categories'}) and ($va{'categories'} = "<tr><td align='center' colspan='7'>".&trans_txt('mer_vendors_nocat')."</td></tr>\n");

	return;
}

sub del_mer_vendors{
# --------------------------------------------------------
# Last Modification by JRG : 03/11/2009 : Se agrega log
	my ($sth) = &Do_SQL("DELETE FROM sl_vendors_categories WHERE ID_vendors='$in{'delete'}';");
	&auth_logging('mer_vendors_category_del',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_vendors_contacts WHERE ID_vendors='$in{'delete'}';");
	&auth_logging('mer_vendors_contact_del',$in{'delete'});
	my ($sth) = &Do_SQL("DELETE FROM sl_vendors_notes WHERE ID_vendors='$in{'delete'}';");
	&auth_logging('mer_vendors_notedel',$in{'delete'});
}

sub validate_mer_vendors {
# --------------------------------------------------------
	my $err;
	if (!$in{'status'}){
		$error{'status'} = &trans_txt('required');
		++$err;
	}

	if ($in{'edit'}) {
		my ($sth) = &Do_SQL("select count(*) from `sl_purchaseorders` inner join sl_vendors using (ID_vendors) where ID_vendors = '$in{'id_vendors'}';");
		my $numRes = $sth->fetchrow;
		if($numRes > 0) {
			my ($sth) = &Do_SQL("select Currency from `sl_vendors` where ID_vendors = '$in{'id_vendors'}';");
			my $currency = $sth->fetchrow;
			if ($currency ne $in{'currency'}) {
					$error{'currency'} = &trans_txt('currency_no_editable');
					++$err;	
			}
		}		
	}
	if ($in{'id_accounts_debit'} == 0 or $in{'id_accounts_debit'} eq '') {
		$error{'id_accounts_debit'} = &trans_txt('invalid');
		++$err;
	}
	if ($in{'id_accounts_credit'} == 0 or $in{'id_accounts_credit'} eq '') {
		$error{'id_accounts_credit'} = &trans_txt('invalid');
		++$err;
	}

	if( $va{'error_vendors'} ){
		++$err;
	}
	
	return $err;
}


1;