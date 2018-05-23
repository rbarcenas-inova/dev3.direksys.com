####################################################################
########             prototypeS                 ########
####################################################################

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_prototypes_notes';
	}elsif($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_prototypes';
	}
}

sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab1 :  fileS
##############################################


	## PRM
	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_prototypes_files WHERE id_prototypes='$in{'id_prototypes'}' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_prototypes_files.ID_admin_users,sl_prototypes_files.Date,sl_prototypes_files.Time,file FROM sl_prototypes_files,admin_users WHERE id_prototypes='$in{'id_prototypes'}' AND sl_prototypes_files.ID_admin_users=admin_users.ID_admin_users $query ORDER BY id_prototypes_files DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_prototypes_files.ID_admin_users,sl_prototypes_files.Date,sl_prototypes_files.Time,file FROM sl_prototypes_files,admin_users WHERE id_prototypes='$in{'id_prototypes'}' AND sl_prototypes_files.ID_admin_users=admin_users.ID_admin_users $query ORDER BY id_prototypes_files DESC LIMIT $first,$usr{'pref_maxh'};");
		}
	
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'files'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'file'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/admin/download?cmd=mer_prototypes&id_prototypes=$in{'id_prototype'}&file=$rec->{'file'}' target='_blank'>Download</a></td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	## Tables Header/Titles
	$va{'keyname'} = 'files';
	&load_db_fields_values($in{'db'},'ID_prototypes',$in{'id_prototypes'},'*');
}

1;


