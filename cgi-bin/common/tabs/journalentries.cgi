#!/usr/bin/perl
#####################################################################
########                   APARTS	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_journalentries_notes';
	}elsif($in{'tab'} eq 5){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_journalentries';
	}
}

#############################################################################
#############################################################################
#	Function: load_tabs1
#
#	Created on: 5/9/2013 3:14:10 PM
#
#	Author: Carlos Haas
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs1 {
#############################################################################
#############################################################################
	# use Data::Dumper;
	# cgierr(Dumper getMovementInfo(11469576)->{'Description'});
	$va{'display_manual'} = 'none';
	$va{'display_auto'} = 'block';
	$va{'segments'} = &table_to_json('sl_accounts_segments', 'ID_accounts_segments Id, Name', "Status = 'Active'");
	$va{'urlservice'} = '/cgi-bin/common/apps/ajaxfinance';
	$va{'id_tabled'} = '0';
	$va{'tableused'} = 'Unknown';

	$in{$cadidorders} = '0';
	$cadtborders = 'Unknown';
	if($in{'id_journalentries'}){
		$filter = "AND sl_movements.ID_journalentries = '$in{'id_journalentries'}'";
	}
	$qry = "
	SELECT 
		sl_accounts.ID_accounting
		, sl_accounts.Name AccountName
		, sl_movements.ID_segments
		, sl_accounts_segments.Name SegmentName
		, sl_movements.Category
		, IF(sl_movements.Credebit = 'Debit', sl_movements.Amount, 0) Debit
		, IF(sl_movements.Credebit = 'Credit', sl_movements.Amount, 0) Credit
		, sl_movements.Amount
		, sl_movements.EffDate
		, sl_movements.Status 
		, sl_movements.ID_movements
		, sl_movements.ID_accounts
		, sl_movements.Reference
		, sl_movements.Credebit
		, sl_movements.ID_segments
		, sl_movements.ID_journalentries
		, sl_movements.tablerelated
		, sl_movements.ID_tablerelated
		, IF(sl_movements.EffDate between sl_accounting_periods.From_Date AND sl_accounting_periods.To_Date, 1, 0) edit
		, (SELECT group_concat(FieldValue) FROM sl_movements_auxiliary WHERE ID_movements = sl_movements.ID_movements group by ID_movements) Description
	FROM sl_movements 
	LEFT JOIN sl_accounts on sl_movements.ID_accounts = sl_accounts.ID_accounts
	LEFT JOIN sl_accounts_segments on sl_movements.ID_segments = sl_accounts_segments.ID_accounts_segments
	LEFT JOIN sl_journalentries on sl_journalentries.ID_journalentries = sl_movements.ID_journalentries
	INNER JOIN sl_accounting_periods on sl_accounting_periods.Status = 'Open'
	WHERE 1
		AND sl_movements.Id_tableused='$in{$cadidorders}'
		AND sl_movements.tableused='$cadtborders' 
		$filter
		AND sl_movements.Status = 'Active'
/*		AND sl_movements.EffDate between sl_accounting_periods.From_Date AND sl_accounting_periods.To_Date*/
	GROUP BY sl_movements.ID_movements
	ORDER BY sl_movements.ID_movements DESC;";

	$movements = &Do_SQL($qry);
	
	@results = ();
	while ($rec = $movements->fetchrow_hashref() ) {
		my %temp = (
			'ID_tableused' => $in{$cadidorders},
			'tableused' => $cadtborders,
			'ID_movements' => $rec->{'ID_movements'},
			'ID Account' =>&format_account($rec->{'ID_accounting'}),
			'Account Name' => $rec->{'AccountName'},
			'Segment' => $rec->{'ID_segments'},
			'Category' => $rec->{'Category'},
			'Debit' => $rec->{'Debit'},
			'Credit' => $rec->{'Credit'},
			'Eff Date' => $rec->{'EffDate'},
			'Journal Entry' => $rec->{'ID_journalentries'},
			'Table Related' => $rec->{'tablerelated'},
			'ID tablerelated' => $rec->{'ID_tablerelated'},
			'Description' => $rec->{'Description'},
			# 'edit' => $rec->{'edit'}
		);


		push @results, \%temp;
	}
	$va{'data'} = encode_json \@results;



	if($in{'categories'} =~ /Diario/i ){
		$va{'display_manual'} = 'block';
		$va{'display_auto'} = 'none';
	}
	my ($query);
	
	if ($in{'from_date'}){
		$query .= "AND EffDate >= '".$in{'from_date'}."'";
	}
	if ($in{'to_date'}){
		$query .= "AND EffDate <= '".$in{'to_date'}."'";
	}
	if ($in{'category'}){
		$in{'category'} =~ s/\|/','/g;  
		$query .= "AND Category IN ('".$in{'category'}."')"; 
	}
	$in{'type_id'} = int($in{'type_id'});
	if ($in{'type'} and $in{'type_id'}>0){
		$query .= "AND ID_tableused='$in{'type_id'}' AND tableused='$in{'type'}'" ;
	}

	my (@c) = split(/,/,$cfg{'srcolors'});

	###########
	########### 1) Summary Section
	###########
	my $sumdebits; my $sumcredits;
	my ($sth) = &Do_SQL("SELECT Category,Effdate,COUNT(*), SUM(IF(Credebit = 'Debit',Amount,0)), SUM(IF(Credebit = 'Credit',Amount,0))
						FROM sl_movements WHERE `Status`='Active' AND ID_journalentries = '$in{'id_journalentries'}' GROUP BY Category, EffDate;");
	while(my ($category, $effdate, $quantity, $debits, $credits) = $sth->fetchrow()){

		$d = 1 - $d;
		my $this_style = abs($debits - $credits) < 0.5 ? 'green' : 'red';
		my $link_drop = $in{'status'} eq 'New' ? 
						qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'view'}&dropcat=$category&dropdate=$effdate&tab=1"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>| :
						'';

		$va{'summaryresults'} .= qq|<tr bgcolor='$c[$d]'>\n
										<td class="smalltext">$link_drop</td>\n
										<td class="smalltext">|.$category.qq|</td>\n
										<td class="smalltext"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'view'}&tab=3&effdate=$effdate">|.$effdate.qq|</a></td>\n
										<td class="smalltext" align="center">|.$quantity.qq|</td>\n
										<td class="smalltext" align="right" style="color:$this_style">|.&format_price($debits).qq|</td>\n
										<td class="smalltext" align="right" style="color:$this_style">|.&format_price($credits).qq|</td>\n
									</tr>\n|;
		$sumdebits += $debits;
		$sumcredits += $credits;

	}

	if($sumdebits){

		my $f_style = abs($sumdebits - $sumcredits) == 0 ? 'green' : 'red';
		$va{'summaryresults'} .= qq|<tr bgcolor='$c[$d]'>\n
										<td class="smalltext" colspan="4">$link_drop</td>\n
										<td class="smalltext" align="right" style="color:$f_style;font-size:bold;">|.&format_price($sumdebits).qq|</td>\n
										<td class="smalltext" align="right" style="color:$f_style;;font-size:bold;">|.&format_price($sumcredits).qq|</td>\n
									</tr>\n|;

	}else{

		$va{'summaryresults'} .= qq|<tr bgcolor='$c[$d]'>\n
										<td class="smalltext" colspan="6" align="center">|.&trans_txt('search_nomatches').qq|</td>\n
									</tr>\n|;

	}


	###########
	########### 2) Search Section
	###########
	if($in{'search_entries'}){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE (ID_journalentries IS NULL OR ID_journalentries=0) $query");
		$va{'matches'} = $sth->fetchrow;

		if ($va{'matches'}>0){
			
			my ($sth) = &Do_SQL("SELECT Category, COUNT( * ) , SUM( Amount ) FROM `sl_movements` WHERE Status = 'Active' AND  (ID_journalentries IS NULL OR ID_journalentries=0) $query GROUP BY Category;");
			while (my (@ary) = $sth->fetchrow_array){
				$d = 1 - $d;
				$va{'total'} += $ary[2];
	
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='50'><input type='checkbox' name='category' checked value='$ary[0]' class='checkbox'></td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>".$ary[0]."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='100'>".$ary[1]."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' width='100' align='right'>".&format_price($ary[2])."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
			if ($va{'total'} > 0) {
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext' colspan='3' align='right'>Total</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
		}else{
			$va{'tabmessage'} = "<p class='stdtxterr'>".&trans_txt('search_nomatches')."</p>";
			#$va{'hide_results'} = "visibility: hidden;";	
		}
	}else{
		#$va{'hide_results'} = "visibility: hidden;";
		
	}

}

#############################################################################
#############################################################################
#	Function: load_tabs2
#
#	Created on: 5/9/2013 3:14:10 PM
#
#	Author: Carlos Haas
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs2 {
#############################################################################
#############################################################################
	
	my $modquery = $in{'effdate'} ? " AND EffDate = '$in{'effdate'}' " : '';
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*),SUM(IF(Credebit = 'Debit' AND Status = 'Active',Amount,0)) AS Debits,SUM(IF(Credebit = 'Credit' AND Status = 'Active',Amount,0)) AS Credits FROM sl_movements WHERE ID_journalentries = '$in{'id_journalentries'}' AND Status = 'Active' $modquery;");
	my ($count, $sumdebits, $sumcredits) = $sth->fetchrow();

	$va{'matches'} = $count;
	if ($va{'matches'}>0){
		my (%tbl_ref) = ('sl_orders'=>'opr_orders',
			'sl_purchaseorders'=>'mer_po',
			'sl_adjustments'=>'opr_adjustments',
			'sl_vendors'=>'mer_vendors',
			'sl_bills'=>'mer_bills',
			'sl_creditmemos'=>'opr_creditmemos');

		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("SELECT * FROM sl_movements LEFT JOIN sl_accounts USING(ID_accounts) WHERE ID_journalentries = '$in{'id_journalentries'}' AND sl_movements.Status = 'Active' $modquery LIMIT $first,$usr{'pref_maxh'} ;");
		$va{'tot_credit'} = 0;$va{'tot_debit'} = 0;
		while ($rec = $sth->fetchrow_hashref){

			$d = 1 - $d;

			($rec->{'tableused'} eq 'sl_vendors' and $rec->{'tablerelated'} eq 'sl_bills' and $rec->{'ID_tablerelated'} > 0 and $rec->{'Category'} eq 'Pagos') and ($rec->{'tableused'} = 'sl_bills' and $rec->{'ID_tableused'}  = $rec->{'ID_tablerelated'});

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_journalentries&view=".$in{'id_journalentries'}."&drop=".$rec->{'ID_movements'}."&tab=2'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_accounts&view=$rec->{'ID_accounts'}\">$rec->{'ID_accounting'} $rec->{'Name'} </a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Category'}."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'EffDate'}."</td>\n";
			
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$tbl_ref{$rec->{'tableused'}}&view=$rec->{'ID_tableused'}&tab=6#initab'>$sys{'db_'.$tbl_ref{$rec->{'tableused'}}.'_title'} : $rec->{'ID_tableused'}</a></td>\n";
			if ($rec->{'Credebit'} eq 'Debit'){
				$va{'tot_debit'} += $rec->{'Amount'};
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>&nbsp;</td>\n";
			}else{
				$va{'tot_credit'} += $rec->{'Amount'};
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>&nbsp;</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			}
			$va{'searchresults'} .= "</tr>\n";
		}
		$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' colspan='5' align='right'>Totals</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'tot_debit'})."</td>\n";
		$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($va{'tot_credit'})."</td>\n";
		$va{'searchresults'} .= "</tr>\n";

		### Total General
		$va{'searchresults'} .= "<tr bgcolor='white'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' colspan='7' align='center'><br><br>\n";
		$va{'searchresults'} .= "      <table border='0' cellspacing='0' cellpadding='2' width='40%' align='center' class='formtable'>\n";
		$va{'searchresults'} .= "         <tr>\n";
		$va{'searchresults'} .= "            <td class='menu_bar_title' colspan='3' align='center'>Totals</td>\n";
		$va{'searchresults'} .= "         </tr>\n";
		$va{'searchresults'} .= "         <tr>\n";
		$va{'searchresults'} .= "            <td width = '40%''>Total Debits:</td>\n";
		$va{'searchresults'} .= "         	 <td align='right' width = '30%'>".&format_price($sumdebits)."</td>\n";
		$va{'searchresults'} .= "            <td  width = '30%'>&nbsp;</td>\n";
		$va{'searchresults'} .= "         </tr>\n";
		$va{'searchresults'} .= "         <tr>\n";
		$va{'searchresults'} .= "            <td width = '40%''>Total Credits:</td>\n";
		$va{'searchresults'} .= "            <td  width = '30%'>&nbsp;</td>\n";
		$va{'searchresults'} .= "         	 <td align='right' width = '30%'>".&format_price($sumcredits)."</td>\n";
		$va{'searchresults'} .= "         </tr>\n";
		$va{'searchresults'} .= "      </table><br><br>\n";
		$va{'searchresults'} .= "  </td>\n";
		$va{'searchresults'} .= "</tr>\n";


	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
			
	}
}


#############################################################################
#############################################################################
#	Function: load_tabs3
#
#	Created on: 5/9/2013 3:14:10 PM
#
#	Author: Carlos Haas
#
#	Modifications: 
#
#	Parameters:
#
#	Returns:
#
#	See Also:
#
#
#
sub load_tabs3 {
#############################################################################
#############################################################################
	my ($total_style);

	my $modquery = $in{'effdate'} ? " AND EffDate = '$in{'effdate'}' " : '';
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT SUM(IF(Credebit = 'Debit' AND Status = 'Active',Amount,0)) AS Debits,SUM(IF(Credebit = 'Credit' AND Status = 'Active',Amount,0)) AS Credits FROM sl_movements WHERE ID_journalentries = '$in{'id_journalentries'}' AND Status = 'Active' $modquery;");
	my ($sumdebits, $sumcredits) = $sth->fetchrow();

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_journalentries = '$in{'id_journalentries'}' AND Status = 'Active' $modquery GROUP BY `tablerelated`,`ID_tablerelated`,`tableused`,`ID_tableused`;");
	$va{'matches'} = $sth->rows();

	if ($va{'matches'}>0){
		my (%tbl_ref) = ('sl_orders'=>'opr_orders',
			'sl_purchaseorders'=>'mer_po',
			'sl_adjustments'=>'opr_adjustments',
			'sl_vendors'=>'mer_vendors',
			'sl_bills'=>'mer_bills',
			'sl_creditmemos'=>'opr_creditmemos');
		
		(!$in{'nh'}) and ($in{'nh'}=1);
		$usr{'pref_maxh'} = $usr{'pref_maxh'}/4;
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					
		my ($sth) = &Do_SQL("SELECT tableused, ID_tableused, tablerelated, ID_tablerelated, Category  
							FROM sl_movements WHERE ID_journalentries = '$in{'id_journalentries'}' 
							AND Status = 'Active' $modquery
							GROUP BY `tablerelated`,`ID_tablerelated`,`tableused`,`ID_tableused`
							LIMIT $first,$usr{'pref_maxh'} ;");
		while (my (@ary) = $sth->fetchrow_array){
			$d = 1 - $d;

			my $modquery = " AND ID_tableused = '$ary[1]' AND tableused = '$ary[0]' ";
			($ary[0] eq 'sl_vendors' and $ary[2] eq 'sl_bills' and $ary[3] > 0 and $ary[4] eq 'Pagos') and ($ary[0] = $ary[2]) and ($ary[1]  = $ary[3]) and ($modquery = " AND ID_tablerelated = '$ary[3]' AND tablerelated = '$ary[2]' ");

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_journalentries&view=".$in{'id_journalentries'}."&gdrop=$ary[1],$ary[0]&tab=3'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='5'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$tbl_ref{$ary[0]}&view=$ary[1]&tab=6#initab'>$sys{'db_'.$tbl_ref{$ary[0]}.'_title'} : $ary[1]</a></td>\n";
			$va{'searchresults'} .= "</tr>\n";
			
			$va{'tot_credit'} = 0;$va{'tot_debit'} = 0;
			my ($sth) = &Do_SQL("SELECT * FROM sl_movements LEFT JOIN sl_accounts USING(ID_accounts) WHERE ID_journalentries = '$in{'id_journalentries'}' $modquery AND sl_movements.Status = 'Active' AND sl_movements.ID_journalentries >= 0;");
			while ($rec = $sth->fetchrow_hashref){
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_journalentries&view=".$in{'id_journalentries'}."&drop=".$rec->{'ID_movements'}."&tab=2'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_accounts&view=$rec->{'ID_accounts'}\">$rec->{'ID_accounting'} $rec->{'Name'} </a></td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'Category'}."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>".$rec->{'EffDate'}."</td>\n";
				
				if ($rec->{'Credebit'} eq 'Debit'){
					$va{'tot_debit'} += $rec->{'Amount'};
					$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right'>&nbsp;</td>\n";
				}else{
					$va{'tot_credit'} += $rec->{'Amount'};
					$va{'searchresults'} .= "  <td class='smalltext' align='right'>&nbsp;</td>\n";
					$va{'searchresults'} .= "  <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
				}
				$va{'searchresults'} .= "</tr>\n";
			}
			if ($va{'tot_credit'} eq $va{'tot_debit'}){
				$total_style = "Color:Green";
			}else{
				$total_style = "Color:Red";
			}
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "  <td class='smalltext' colspan='4' align='right'>Totals</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='$total_style'>".&format_price($va{'tot_debit'})."</td>\n";
			$va{'searchresults'} .= "  <td class='smalltext' align='right' style='$total_style'>".&format_price($va{'tot_credit'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";

		}

		### Total General
		$va{'searchresults'} .= "<tr bgcolor='white'>\n";
		$va{'searchresults'} .= "  <td class='smalltext' colspan='7' align='center'><br><br>\n";
		$va{'searchresults'} .= "      <table border='0' cellspacing='0' cellpadding='2' width='40%' align='center' class='formtable'>\n";
		$va{'searchresults'} .= "         <tr>\n";
		$va{'searchresults'} .= "            <td class='menu_bar_title' colspan='3' align='center'>Totals</td>\n";
		$va{'searchresults'} .= "         </tr>\n";
		$va{'searchresults'} .= "         <tr>\n";
		$va{'searchresults'} .= "            <td width = '40%''>Total Debits:</td>\n";
		$va{'searchresults'} .= "         	 <td align='right' width = '30%'>".&format_price($sumdebits)."</td>\n";
		$va{'searchresults'} .= "            <td  width = '30%'>&nbsp;</td>\n";
		$va{'searchresults'} .= "         </tr>\n";
		$va{'searchresults'} .= "         <tr>\n";
		$va{'searchresults'} .= "            <td width = '40%''>Total Credits:</td>\n";
		$va{'searchresults'} .= "            <td  width = '30%'>&nbsp;</td>\n";
		$va{'searchresults'} .= "         	 <td align='right' width = '30%'>".&format_price($sumcredits)."</td>\n";
		$va{'searchresults'} .= "         </tr>\n";
		$va{'searchresults'} .= "      </table><br><br>\n";
		$va{'searchresults'} .= "  </td>\n";
		$va{'searchresults'} .= "</tr>\n";

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

1;