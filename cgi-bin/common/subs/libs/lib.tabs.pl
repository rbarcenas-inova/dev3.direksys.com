sub build_tabs {
# --------------------------------------------------------
	my ($tab_jump,$tbjump,$page_fname,@header_cols,$fname);


	## Check Tab Perms
	if(!&check_permissions($in{'cmd'},'',$in{'tab'})){ return &html_unauth_tab; };
	@ary = split(/:|,/, $sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}}) if ($sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}});
	@ary = split(/:|,/, $sys{'db_'.$in{'cmd'}.'_htabs'}) if (!$sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}});

	$in{'tab'} = int($in{'tab'});
	$in{'tab'}=$ary[0] if (!$in{'tab'});
	$in{'tab'}=1 if (!$in{'tab'});
	
	# $script_url change
	$va{'activetab'} = $in{'tab'};
	$in{'tab_pos'} =$in{'tab'};
	
	# $typeaction - used by *_construct.html
	($in{'view'}) and ($va{'typeaction'}='view');
	($in{'modify'}) and ($va{'typeaction'}='modify');
	($in{'edit'}) and ($va{'typeaction'}='edit');
	
	# $tbnow - used to reinitialize $in{'nh'} variable
	($in{'tbnow'}) and ($in{'tbnow'} != $in{'tab'}) and ($in{'nh'} = 1);
	
	$fname = $tpath."tabs/$sys{'db_'.$in{'cmd'}.'_form'}_tab$in{'tab'}.html";
		
	if (-e $fname){
		$page_fname = $sys{'db_'.$in{'cmd'}.'_form'}.'_tab'.$in{'tab'}.'.html';
	}		
	

	## for Perm_all
	my ($func) = 'load_tabs'.$in{'tab'};
	if (defined &$func){
		&$func;	
	}else{
		my ($func) = 'load_tabsconf';
		if (defined &$func){
			&$func;
			if (!$va{'tab_title'} or !$va{'tab_type'}){
				$va{'message'} = &trans_txt('gen_error');
				return &html_message_tab; 
			}
		}else{
			$va{'message'} = &trans_txt('gen_error');
			return &html_message_tab; 
		}
	}
	##($in{'tab'}) and ($tab_jump = "<script language='JavaScript'>\n  self.document.location.href = '#tabsl';\n</script>");

	#&cgierr;
	## Tab overwrite
	if($va{'new_tbname'}){
		$nfname = $tpath."tabs/$va{'new_tbname'}.html";
		(-e $nfname) and ($fname = $nfname) and ($page_fname = $va{'new_tbname'} . '.html');
		delete($va{'new_tbname'});
	}


	if ($in{'print'}){
		return &build_page($page_fname);
		## Solo imprime el tab activo
	}elsif($in{'xtabs'}){
		print "Content-Type: text/html; charset=iso-8859-1\n\n";
		if ($page_fname and (!$va{'tab_title'} or !$va{'tab_type'})){
			print &build_page($page_fname);
		}elsif($va{'tab_title'} and $va{'tab_type'}){
			print &load_pretab;
		}else{
			if (!$va{'tab_headers'}){
         		$va{'tab_headers'} = "<tr><td class='menu_bar_title'>".&trans_txt($in{'cmd'}.'_htab'.$in{'tab'})."</td></tr>\n";
         		$va{'tab_headers'} =~ s/,/<\/td><td class='menu_bar_title'>/g;
        	}
			print &build_page('tab_lists.html');
		}
		## Imprime los tabs con YUI	
	}else{
         if ($va{'tab_title'} and $va{'tab_type'}){
         	$va{'tbbuild'} = &load_pretab;
         }elsif(-e $fname){
            $va{'tbbuild'} = &build_page($page_fname).$tbjump;
         }else{
         	if (!$va{'tab_headers'}){
         		$va{'tab_headers'} = "<tr><td class='menu_bar_title'>".&trans_txt($in{'cmd'}.'_htab'.$in{'tab'})."</td></tr>\n";
         		$va{'tab_headers'} =~ s/,/<\/td><td class='menu_bar_title'>/g;
        	}
         	$va{'tbbuild'} = &build_page('tab_lists.html');;
         }
         
		 &build_ajaxtabs;
		 return "<a name='initab' id='initab'></a> ".&build_page('constructor.html').$tbjump;	 
	}
}

sub build_ajaxtabs{
#-----------------------------------------
# Created on: 02/03/09  13:28:48 By  Roberto Barcenas
# Forms Involved: all tabs
# Description : Build the tabs array based on file nametab.cfg
# Parameters : 

#var now=[va_activetab];
#var jump = '[in_tab_pos]';
	my $id_admin_users = 0;
	if( $in{'view'} ){		
		$id_admin_users = &load_name('sl_orders','ID_orders',$in{'view'},'ID_admin_users');
	}
	
	my ($totchar);
	##cmd=[in_cmd]&xtabs=claims&tab=2&id_claims=[in_id_claims]&[va_typeaction]=[in_id_claims]&tbnow=[in_tab]&nh=[in_nh]&[va_extracfg]&db=[in_db]
	if ($sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}} or $sys{'db_'.$in{'cmd'}.'_htabs'}){			
		my (@ary);
		my $i=1; 
		$va{'tabs_perpage'}=0; 
		$va{'tbname'} = $sys{'db_'.$in{'cmd'}.'_form'};
		my $maxchar=250; 
		my $flag=0;
		$va{'data_array'} = '';
		@ary = split(/:|,/, $sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}}) if ($sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}});
		@ary = split(/:|,/, $sys{'db_'.$in{'cmd'}.'_htabs'}) if (!$sys{'db_'.$in{'cmd'}.'_htabs_'.$usr{'pref_language'}});		
		my $perm_view = ( $usr{'application'} eq 'sales' and $id_admin_users != $usr{'id_admin_users'} ) ? 0 : 1;
		my $tab_view = 1;
		for my $x(0..$#ary/2){			
			$tab_view = 1;
			if( ($x == 2 or $x == 4 or $x == 5 or $x == 8 or $x == 11) and !$perm_view ){
				$tab_view = 0;
			}
			if( $tab_view ){
				$va{'data_array'}  .= "{'label':'$ary[$x*2+1]','dataSrc':'/cgi-bin/mod/$usr{'application'}/admin?cmd=$in{'cmd'}&$db_cols[0]=$in{lc($db_cols[0])}&xtabs=$sys{'db_'.$in{'cmd'}.'_form'}&activetab=$ary[$x*2]&view=$in{lc($db_cols[0])}&tab=$ary[$x*2]&tab_pos=$ary[$x*2]'},";
				$totchar += length($ary[$x*2+1]);
				if ($in{'tab'} eq $ary[$x*2]){
					$va{'activetab'} = $i;
					$in{'tab_pos'} = $i;
				}
				#(!$in{'tab'})? ($va{'activetab'}=1):($va{'activetab'}=$in{'tab'});
				$va{'tabs_perpage'} = $i if ($totchar > $maxchar and $va{'tabs_perpage'} == 0);
				$i++;
			}
		}		
		chop($va{'data_array'});
		$va{'tabs_perpage'} = $i if $va{'tabs_perpage'} == 0;
		$va{'activetab'}    = 1  if !$va{'activetab'};
		$va{'tab_pos'}    = 1  if !$va{'tab_pos'};
	}else{
		$va{'data_array'} = '';
		my $i=1; $va{'tabs_perpage'}=0; $maxchar=70; $flag=0;
		my ($tpath) = $cfg{'path_templates'};
		$tpath =~ s/\[lang\]/$usr{'pref_language'}/gi;
		$tpath .= "tabs/$sys{'db_'.$in{'cmd'}.'_form'}.cfg";
		if (-e	$tpath){
			if(open(TABS, "<$tpath")){
				LINE: while (<TABS>) {
					$line = $_;
					$line =~ s/\r|\n//g;
					$line =~ /(.+):(.*)/;
					$posfict = $2;
					$va{'data_array'}  .= "{'label':'$1','dataSrc':'$2&tab_pos=$i'},";
					$totchar += length($1);
					$va{'tabs_perpage'} = $i if ($totchar > $maxchar and $va{'tabs_perpage'} == 0);
					if($posfict	=~	/tab=$va{'activetab'}/ and !$flag){
						$va{'activetab'}	=	$i;
						$flag=1
					}
					$i++;
				}
				chop($va{'data_array'});
			  close AUTH;
			  $va{'tabs_perpage'} = $i if $va{'tabs_perpage'} == 0;
			}
		}elsif($cfg{'cd'}){
			&cgierr("Unable to Open : $tpath",$!,452);
		}
	}
}
sub load_pretab{
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
					<td class="titletext">[in_id_customers] &nbsp;</td>
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
		</table>|;
	}else{
		if ($va{'tab_type'} eq 'notes'){
			$page = &load_tabs_notes;
		}elsif($va{'tab_type'} eq 'logs'){
			$page = &load_tabs_logs;
		}elsif($va{'tab_type'} eq 'movs'){
			$page = &load_tabs_movs;
		}else{
			$page = &load_tabs_list;
		}
	}
	return $page;
}


sub load_tabs_notes {
# --------------------------------------------------------
##############################################
## tab : Notes
##############################################
	my (@ary) = &load_enum_toarray($va{'tab_table'},'Type');
	for my $i(0..$#ary){
		$va{'tab_filterby'} .= qq|&nbsp;<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[fc_template_idvalue]&tab=[in_tab]&filter=$ary[$i]#tabs">$ary[$i]</a> -\n|;
		$va{'notetypes'}    .= qq|<input type="radio" name="notestype" class="radio" value="$ary[$i]">$ary[$i] &nbsp;\n|;
	}
	$va{'tab_name'} = $sys{'db_'.$in{'cmd'}.'_form'};


	if ($in{'tabaction'}){
		if ((!$in{'notestxt'} or !$in{'notestype'})){
			$va{'tabmessages'} = &trans_txt('reqfields');
		}else{
			$va{'tabmessages'} = &trans_txt($in{'cmd'}.'_noteadded');
			
			my ($sth) = &Do_SQL("INSERT INTO $va{'tab_table'} SET $db_cols[0]='$in{lc($db_cols[0])}',Notes='".&filter_values($in{'notestxt'})."',Type='$in{'notestype'}',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			$va{'tabmessages'} = &trans_txt($in{'cmd'}.'_noteadded');
			delete($in{'notestxt'});
			delete($in{'notestype'});
			delete($in{'action'});
			&auth_logging($in{'cmd'}.'_noteadded',$in{lc($db_cols[0])});
			$in{'tabs'} = 1;
		}
	}
	my ($query);
	if ($in{'filter'}){
		$query = "AND Type='".&filter_values($in{'filter'})."' ";
		$va{'query'} = $in{'filter'};
	}
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $va{'tab_table'} WHERE $db_cols[0]='$in{lc($db_cols[0])}' $query ");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT ID_".substr($va{'tab_table'}, 3).", $va{'tab_table'}.ID_admin_users,$va{'tab_table'}.Date as mDate,$va{'tab_table'}.Time as mTime,FirstName,LastName,Type,Notes FROM $va{'tab_table'} LEFT JOIN admin_users USING(ID_admin_users) WHERE $db_cols[0]='$in{lc($db_cols[0])}' $query ORDER BY $db_cols[0]_notes DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Type'}</td>\n";

			#####
			##### Get file attached
			#####
			my $sth_att = &Do_SQL("SELECT ID_notes_attached FROM sl_notes_attached WHERE ID_table_notes=".$rec->{'ID_'.substr($va{'tab_table'}, 3)}." AND table_notes='".$va{'tab_table'}."';");
			my $rec_att = $sth_att->fetchrow();

			my $html_attached = "";
			if( $rec_att ){
				$html_attached = "<a href='/cgi-bin/common/apps/schid?cmd=view_notes_attached&id=".$rec_att."' class='fancy_modal_iframe' title='View file' target='_blank'> 
									<img src='[va_imgurl]/[ur_pref_style]/view_file2.png' alt='file_attached' style='width: 24px; height: 24px;' />
								</a>";
			}

			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Notes'}</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' style='text-align: right;'>$html_attached</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}	
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	return &build_page('tab_notes.html');
}

sub load_tabs_logs {
# --------------------------------------------------------
##############################################
## tab : Logs
##############################################
	my (@c) = split(/,/,$cfg{'srcolors'});
		
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM admin_logs WHERE tbl_name='$va{'tab_table'}' AND Action='$in{lc($db_cols[0])}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		my ($sth) = &Do_SQL("SELECT * FROM admin_logs,admin_users WHERE tbl_name='$va{'tab_table'}' AND Action='$in{lc($db_cols[0])}' AND admin_logs.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_admin_logs DESC LIMIT $first,$usr{'pref_maxh'};");
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
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return &build_page('tab_logs.html');
	
}


sub load_tabs_list {
# --------------------------------------------------------
	$va{'tab_name'} = $sys{'db_'.$in{'cmd'}.'_form'};
	my (@ary) = split(/,/,$va{'tab_headers_names'});
	$va{'tab_headers'} = "<tr>\n";
	for my $i(0..$#ary){
		$va{'tab_headers'} .= "<td class='menu_bar_title'>".&trans_txt($ary[$i])."</td>\n";
	}
	$va{'tab_headers'} .= "</tr>\n";


	my (@c)   = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $va{'tab_table'} WHERE $db_cols[0]='$in{lc($db_cols[0])}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT $va{'tab_headers_fields'} FROM $va{'tab_table'} WHERE $db_cols[0]='$in{lc($db_cols[0])}'");				
		while (my @rec = $sth->fetchrow_array){
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			for my $i(0..$#rec){
				$va{'searchresults'} .= "   <td class='smalltext' >$rec[$i] </td>\n";
			}
			$va{'searchresults'} .= "</tr>\n";				
		}
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='$#ary' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return &build_page('tab_lists.html');
}


sub load_tabs_movs{


	my (@c) = split(/,/,$cfg{'srcolors'});
	my $tot_cred,$tot_debs;

		$sth=&Do_SQL("SELECT SUM(t) FROM
					(
						SELECT COUNT(*)AS t FROM sl_movements WHERE ID_tableused = '$va{'tab_idvalue'}' AND tableused = '$va{'tab_table'}' AND Status = 'Active'
						UNION
						SELECT COUNT(*)AS t FROM sl_movements WHERE ID_tablerelated = '$va{'tab_idvalue'}' AND tablerelated = '$va{'tab_table'}' AND Status = 'Active'
					)t1;");

	$va{'matchescredits'} = $sth->fetchrow;
	if ($va{'matchescredits'}>0){
		$sth=&Do_SQL("SELECT * FROM sl_movements WHERE ID_tableused = '$va{'tab_idvalue'}' AND tableused = '$va{'tab_table'}' AND Status = 'Active'
						UNION
						SELECT * FROM sl_movements WHERE ID_tablerelated = '$va{'tab_idvalue'}' AND tablerelated = '$va{'tab_table'}' AND Status = 'Active'
						ORDER BY EffDate, Category DESC, ID_movements , Credebit, Amount , CONCAT(Date, ' ',Time) ASC ;");


		my $this_date = '0'; my $this_category = ''; my $these_debits; my $these_credits;
		$tot_debs = 0;
		while($rec=$sth->fetchrow_hashref){
			
			if($this_date ne $rec->{'EffDate'} or $this_category ne $rec->{'Category'}) {

				if($this_date ne '0' or $this_category ne ''){

					#########
					######### Sumarize Dates
					#########

					my $eq = $these_debits ne $these_credits ? "style='color:red;'" : "style='color:green;'";
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= "  <td class='smalltext' colspan='3'>&nbsp;</td>";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' nowrap $eq>".&format_price($these_debits)."</td>";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' nowrap $eq>".&format_price($these_credits)."</td>";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' nowrap colspan='3'>&nbsp;</td>";
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right' colspan='8'>&nbsp;</td>";

					$these_debits = 0;
					$these_credits = 0;

				}

				$d = 1 - $d;
				$this_date = $rec->{'EffDate'};
				$this_category = $rec->{'Category'};

			}


			my $this_debit = &format_price($rec->{'Amount'});
			$these_debits += $rec->{'Amount'};
			$tot_debs += $rec->{'Amount'};
			my $this_credit = '';

			if($rec->{'Credebit'} eq 'Credit') {

				$this_credit = &format_price($rec->{'Amount'});
				$these_credits += $rec->{'Amount'};
				$this_debit = '';
				$tot_debs -= $rec->{'Amount'};
				$these_debits -= $rec->{'Amount'};
				$tot_cred += $rec->{'Amount'};
				
			}
			my $this_category;
			my @ary = split(/\s/, $rec->{'Category'});
			if(scalar @ary > 1){
				for(0..$#ary){
					$this_category .= uc(substr($ary[$_],0,1));
				}
			}else{
				$this_category = uc(substr($ary[0],0,));
			}



			my $accountnumber = &load_name('sl_accounts','ID_accounts',$rec->{'ID_accounts'},'ID_accounting');
			my $accountname = &load_name('sl_accounts','ID_accounts',$rec->{'ID_accounts'},'Name');
			my $journal_status = !$rec->{'ID_journalentries'} ? '' : substr(&load_name('sl_journalentries','ID_journalentries',$rec->{'ID_journalentries'},'Status'),0,1);

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'ID_movements'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext'>".&format_account($accountnumber)."</td>";
			$va{'searchresults'} .= "  <td class='smalltext'>$accountname</td>";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' nowrap>".$this_debit."</td>";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' nowrap>".$this_credit."</td>";
			$va{'searchresults'} .= "  <td class='smalltext' align='center' nowrap>$rec->{'EffDate'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' align='left' nowrap>$this_category</td>";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' nowrap>$rec->{'ID_journalentries'}$journal_status</td>";
			$va{'searchresults'} .= "</tr>\n";

			#my $segmentname = $rec->{'ID_segments'} > 0 ? &load_name('sl_accounts_segments','ID_accounts_segments',$rec->{'ID_segments'},'Name') : 'N/A';
			#$rec->{'ID_journalentries'} = 'N/A' if !$rec->{'ID_journalentries'};

			#$va{'searchresults'} .= "  <td class='smalltext'>$segmentname $txtp</td>";
			#$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Category'}</td>";
			#$va{'searchresults'} .= "  <td class='smalltext' align='right' nowrap>$rec->{'ID_journalentries'}</td>";

		}

		#########
		######### Sumarize Dates
		#########

		my $eq = $these_debits ne $these_credits ? "style='color:red;'" : "style='color:green;'";
		$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' colspan='3'>&nbsp;</td>";
		$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' nowrap $eq>".&format_price($these_debits)."</td>";
		$va{'searchresults'} .= "  <td class='smalltext' align='right' valign='top' nowrap $eq>".&format_price($these_credits)."</td>";
		$va{'searchresults'} .= "  <td class='smalltext' align='right' colspan='3'>&nbsp;</td>";
		$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' align='right' colspan='8'>&nbsp;</td>";


		$va{'tot_debs'}=&format_price($tot_debs);
		$va{'tot_cred'}=&format_price($tot_cred);
		$va{'link_movements_auxiliary'} = '/cgi-bin/common/apps/movements_auxiliary?cmd=detail_movements_auxiliary&id_orders='.$in{'id_orders'};

	}else{

		$va{'tot_debs'} = &format_price(0);
		$va{'tot_cred'} = &format_price(0);
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;

	}

	if ($in{'toprint'}){
		&get_company_info();
		return &build_page('tab_movs_print.html');
	}else{
		return &build_page('tab_movs_v2.html');
	}


}


sub build_tab_cust_pterms{
# --------------------------------------------------------
	my ($selected);
	$selected='selected' if ($in{'pterms'} eq 'all' or !$in{'pterms'});
	
	my ($output) = qq|
					<li class="$selected" id="tab1" title="" onclick="trjump(&quot;/cgi-bin/mod/admin/admin?cmd=opr_customers_home&pterms=all&quot;)">
						<a href="javascript:return false;">
							<em>All</em>
						</a>
					</li>\n|;	
	
	my ($i) = 2;
	my ($sth) = &Do_SQL("SELECT Name FROM sl_terms WHERE Status='Active';");
	while (my ($pterm) = $sth->fetchrow() ) {
		($in{'pterms'} eq $pterm)?
			($selected='selected'):($selected='');
		$output .= qq|	
					<li class="$selected" id="tab$i" title="" onclick="trjump(&quot;/cgi-bin/mod/admin/admin?cmd=opr_customers_home&pterms=$pterm&quot;)">
						<a href="javascript:return false;">
							<em>$pterm</em>
						</a>
					</li>\n|;
		++$i;
	}
	return $output;
}


sub edition_type{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12/22/08 17:02:17
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :

	#&cgierr(2);
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers);
	$cadtborders="sl_$in{'edit_type'}orders";
	$cadtbproducts="sl_$in{'edit_type'}orders_products";
	$cadtbproductstmp="sl_$in{'edit_type'}orders_productstmp";
	$cadtbpayments="sl_$in{'edit_type'}orders_payments";
	$cadtbpaymentstmp="sl_$in{'edit_type'}orders_paymentstmp";
	$cadtbcustomers="sl_$in{'edit_type'}customers";
	$cadidorders="id_$in{'edit_type'}orders";
	$cadidorderproducts="id_$in{'edit_type'}orders_products";
	$cadidorderpayments="id_$in{'edit_type'}orders_payments";
	$cadidcustomers="id_$in{'edit_type'}customers";

	if ($in{'edit_type'} =~ /purchaseorders|adjustments|bills|vendors|banks_movements|creditmemos|customers_advances/){
		$cadtborders="sl_$in{'edit_type'}";
		$cadidorders="id_$in{'edit_type'}";
	}
		
	return ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers);
}

1;