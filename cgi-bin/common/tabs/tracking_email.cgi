#!/usr/bin/perl
####################################################################
########                  tracking_email                   ########
####################################################################


sub build_tabs {
# --------------------------------------------------------
	$in{'tab'} = int($in{'tab'});
	my ($tab_jump,$tbjump,$page_fname,@header_cols,$fname);
	if(!&check_permissions($in{'cmd'},'',$in{'tab'})){ return &html_unauth_tab; };
	
	if (!$in{'tab'}) {
		$in{'tab'}=1;
	}else{
		$tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabs';\n</script>";
	}
	
	# $script_url change
	($in{'xtabs'}) and ($script_url =~ s/admin$/dbman/) and ($va{'script_url'} =~ s/admin$/dbman/);
	$va{'activetab'} = $in{'tab'};
	
	# $typeaction - used by *_construct.html
	($in{'view'}) and ($va{'typeaction'}='view');
	($in{'modify'}) and ($va{'typeaction'}='modify');
	($in{'edit'}) and ($va{'typeaction'}='edit');
	
	# $tbnow - used to reinitialize $in{'nh'} variable
	($in{'tbnow'}) and ($in{'tbnow'} != $in{'tab'}) and ($in{'nh'} = 1);
	
	($in{'finaldec'} eq 'on' ) and ($va{'extracfg'} .= "&authby=$usr{'authby'}");
	
	if ($in{'tab'}>0 and $in{'tab'}<=3){
		if ($in{'print'}){
			$fname = $tpath."tabs/tracking_email_print_tab$in{'tab'}.html";
		}else{
			$fname = $tpath."tabs/tracking_email_tab$in{'tab'}.html";
		}

		if (-e $fname){
			$page_fname = 'tracking_email_tab'.$in{'tab'}.'.html';
		}else{
			@header_cols  = split(/,/,&trans_txt('tracking_email_header_tab'.$in{'tab'}));
			$va{'tbltitles'} = "<tr><td class='menu_bar_title' nowrap>" . join("</td><td class='menu_bar_title'>" ,@header_cols) . "</td></tr>";
			$page_fname = 'prepage';
			$va{'prepage'} = &load_prepage;
		}		

		## for Perm_all
		if (!check_permissions($in{'cmd'},'',$in{'tab'})) { 
			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='$#header_cols' align="center">|.&trans_txt('not_auth').qq|</td>
				</tr>\n|;
		}else{
			&{'load_tabs'.$in{'tab'}};
			($in{'tab'}) and ($tbjump = "<script language='JavaScript'>\n  self.document.location.href = '#tabsl';\n</script>");
		}

		if ($in{'print'}){
			return &build_page($page_fname);
		## Solo imprime el tab activo
		}elsif($in{'xtabs'}){
			print "Content-type: text/html\n\n";
			print &build_page($page_fname);
		## Imprime los tabs con YUI	
		}elsif(-e $tpath."tabs/$va{'tbname'}.cfg"){
			if (-e $fname and !$in{'print'}){
				$va{'tbbuild'}=&build_page($page_fname).$tbjump;
            }else{
                $va{'tbbuild'} = $va{'prepage'};
            }
			&build_ajaxtabs;
			return &build_page('constructor.html').$tbjump;
		## Imprime los tabs estaticos	
		}else{
			return &build_page($page_fname) .$tab_jump;		 
		}
	}
}


sub load_tabs1 {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	## Comments
	
	if ($in{'action'}){
		if ((!$in{'notes'} or !$in{'notestype'}) and !$in{'edit'}){
			$va{'tabmessages'} = &trans_txt('reqfields_short');
		}else{
			$va{'tabmessages'} = &trans_txt('opr_orders_noteadded');

			&add_order_notes_by_type($in{'id_orders'},&filter_values($in{'notes'}),$in{'notestype'});
			delete($in{'notes'});
			delete($in{'notestype'});
			&auth_logging('opr_orders_noteadded',$in{'id_orders'});
			$in{'tabs'} = 1;
		}
	}
	## VRM
	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
		$in{'tabs'} = 1;
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders='$in{'id_orders'}' $query");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT ID_orders,sl_orders_notes.ID_admin_users,sl_orders_notes.Date as mDate,sl_orders_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_orders_notes,admin_users WHERE ID_orders='$in{'id_orders'}' AND sl_orders_notes.ID_admin_users=admin_users.ID_admin_users $query ORDER BY sl_orders_notes.Date DESC,sl_orders_notes.Time DESC LIMIT $first,$usr{'pref_maxh'} ;");
		delete($va{'searchresults'});
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	&load_db_fields_values($in{'db'},'ID_orders',$in{'id_orders'},'*');
}


sub print_tabs{
# --------------------------------------------------------
	$in{'print'} = 1;
	return &build_tabs;
}


sub load_prepage{
# --------------------------------------------------------
	my ($page);

	if ($in{'print'}){
		$page = qq|
		&nbsp;
		[ip_forms:sltv_header]
	
		<fieldset><legend>Customer Info</legend>
			<table border="0" cellspacing="0" cellpadding="2" width="100%">
				<tr>
					<td width="30%" class="titletext">Customer ID  : </td>
					<td class="titletext">[in_id_tracking_email] &nbsp;</td>
				</tr>
				<tr>
					<td width="30%" class="smalltext">Date / Time /user  : </td>
					<td class="smalltext">[in_date] [in_time] &nbsp; Created by : ([in_id_admin_users]) [in_admin_users.firstname] [in_admin_users.lastname]</td>
				</tr>		
			</table>
		</fieldset>
		&nbsp;
 		<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
		 [va_tbltitles]
		 [va_searchresults]
		</table>
	|;
	}else{
		$page = qq|
	&nbsp;
	[fc_build_statictabs]
	<table width="100%" border="0" cellspacing="0" cellpadding="0" class="gborder" align="center">
		<tr>
			<td class="tbltextttl">
				<a href='javascript:trjump("[va_script_url]?cmd=[in_cmd]&view=[in_id_tracking_email]&tab=[va_activetab]#tabs")'><img src='[va_imgurl]/[ur_pref_style]/b_reload.gif' title='Refresh' alt='' border='0'></a>&nbsp;
				<a href="javascript:prnwin('[va_script_url]?cmd=[in_cmd]&search=Print&tab=[in_tab]&tabcmd=[in_cmd]&toprint=[in_id_tracking_email]')"><img src='[va_imgurl]/[ur_pref_style]/b_print.png' title='Print' alt='' border='0'></a>
				[va_keyname] : [va_matches]</td>
			<td align="right" class="tbltextttl">Pages: [va_pageslist]</td>
	 	</tr>
		<tr>
			<td colspan="3">
		 		<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
				 [va_tbltitles]
				 [va_searchresults]
				</table>
			</td>
		</tr>
		<tr><td>&nbsp;</td></tr>
	</table>
	|;
	&load_db_fields_values($in{'db'},'ID_orders',$in{'id_orders'},'*');
	}
	return $page;
}

sub load_tabs2 {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/13/08 13:24:02
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	## Comments
	
	## VRM
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_tracking_email_out WHERE ID_tracking_email='$in{'id_tracking_email'}' ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_tracking_email_out WHERE ID_tracking_email='$in{'id_tracking_email'}'");
		delete($va{'searchresults'});
		while ($rec = $sth->fetchrow_hashref){
			$rec->{'Body'} =~ s/\n/<br>/g;
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$username=&load_db_names('admin_users','ID_admin_users',$rec->{'ID_admin_users'},'[FirstName] [LastName]');
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'} $rec->{'Time'}<br />($rec->{'ID_admin_users'})$username</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Subject'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Body'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

sub load_tabs3 {
# --------------------------------------------------------
##############################################
## tab3 : LOGS
##############################################

	### Logs
	my (@c) = split(/,/,$cfg{'srcolors'});
	$sth = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_tracking_email' AND Action='$in{$va{'typeaction'}}'") if !$in{'print'};
	$sth = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='sl_tracking_email' AND Action='$in{'id_tracking_email'}'") if $in{'print'};
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_tracking_email' AND Action='$in{'id_tracking_email'}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$va{'pageslist'} =~	s/xtabs=products&//g;
			$sth = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='sl_tracking_email' AND Action='$in{$va{'typeaction'}}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ID_admin_users'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	## Tables Header/Titles
	$va{'keyname'} = 'Logs';
}


1;