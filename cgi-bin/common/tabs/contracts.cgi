#!/usr/bin/perl
####################################################################
########                  Purchase Orders                   ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 6){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_mediacontracts_notes';
	}elsif($in{'tab'} eq 7){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_mediacontracts';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
##############################################
## tab1 : Stats
##############################################
# Last Modified RB: 05/15/09  16:35:25 -- Si el producsto es un Set, se cargan sus partes


	$sth = &Do_SQL("SELECT 
		SUM(IF(TIMESTAMPDIFF(MINUTE, '$in{'estday'} $in{'esttime'}', CONCAT(Date, ' ', Time) ) BETWEEN -30 AND 90,1,0))AS P1, 
		SUM(IF(TIMESTAMPDIFF(MINUTE, '$in{'estday'} $in{'esttime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,1,0))AS P2, 
		SUM(IF(TIMESTAMPDIFF(MINUTE, '$in{'estday'} $in{'esttime'}', CONCAT(Date, ' ', Time) ) > 360,1,0))AS P3
		FROM sl_leads_calls WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' AND IO='In'");
		($va{'p1calls'},$va{'p2calls'},$va{'p3calls'})=$sth->fetchrow();
		$va{'tcalls'} = $va{'p1calls'}+$va{'p2calls'}+$va{'p3calls'};


	my ($sth)=&Do_SQL("SELECT * FROM sl_mediacontracts WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';");
	my ($rec) = $sth->fetchrow_hashref();

	### Cost Per call
	if ($va{'p1calls'}){
		$va{'p1cc'} = &format_price($rec->{'Cost'}/$va{'p1calls'});
	}else{
		$va{'p1cc'} = 'N/A';
	}
	if ($va{'p2calls'}){
		$va{'p2cc'} = &format_price($rec->{'Cost'}/$va{'p2calls'});
	}else{
		$va{'p2cc'} = 'N/A';
	}
	if ($va{'p3calls'}){
		$va{'p3cc'} = &format_price($rec->{'Cost'}/$va{'p3calls'});
	}else{
		$va{'p3cc'} = 'N/A';
	}
	if ($va{'tcalls'}){
		$va{'tcc'} = &format_price($rec->{'Cost'}/$va{'tcalls'});
	}else{
		$va{'tcc'} = 'N/A';
	}



	my ($tmp_value) = &load_contract_totals($rec->{'ID_mediacontracts'},$rec->{'ESTTime'},$rec->{'ESTDay'},$rec->{'DestinationDID'});
	### Totals to Vars
	foreach $key (keys %{$tmp_value}){
		if ($key =~ /tot/){
			$va{lc($key)} = &format_price($tmp_value->{$key});
		}else{
			$va{lc($key)} = $tmp_value->{$key};
		}
	}
	
	## Calculate Totals
	$va{'p1tot'} = &format_price($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'});
	$va{'p2tot'} = &format_price($tmp_value->{'P2totTDC'}+$tmp_value->{'P2totCOD'});
	$va{'p3tot'} = &format_price($tmp_value->{'P3totTDC'}+$tmp_value->{'P3totCOD'});
	$va{'ttot'}  = &format_price($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'}+$tmp_value->{'P2totTDC'}+$tmp_value->{'P2totCOD'}+$tmp_value->{'P3totTDC'}+$tmp_value->{'P3totCOD'});
	$va{'ttottdc'} = &format_price($tmp_value->{'P1totTDC'}+$tmp_value->{'P2totTDC'}+$tmp_value->{'P3totTDC'});
	$va{'tqtytdc'} = $tmp_value->{'P1qtyTDC'}+$tmp_value->{'P2qtyTDC'}+$tmp_value->{'P3qtyTDC'};
	$va{'ttotcod'} = &format_price($tmp_value->{'P1totCOD'}+$tmp_value->{'P2totCOD'}+$tmp_value->{'P3totCOD'});
	$va{'tqtycod'} = $tmp_value->{'P1qtyCOD'}+$tmp_value->{'P2qtyCOD'}+$tmp_value->{'P3qtyCOD'};
	$va{'p1qty'} = $tmp_value->{'P1qtyTDC'}+$tmp_value->{'P1qtyCOD'};
	$va{'p2qty'} = $tmp_value->{'P2qtyTDC'}+$tmp_value->{'P2qtyCOD'};
	$va{'p3qty'} = $tmp_value->{'P3qtyTDC'}+$tmp_value->{'P3qtyCOD'};
	$va{'tqty'}  = $tmp_value->{'P1qtyTDC'}+$tmp_value->{'P1qtyCOD'} + $tmp_value->{'P2qtyTDC'}+$tmp_value->{'P2qtyCOD'} + $tmp_value->{'P3qtyTDC'}+$tmp_value->{'P3qtyCOD'};
	
	## Ratios
	if ($rec->{'Cost'}>0){
		$va{'p1ratio'} = &round(($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'})/$rec->{'Cost'},2);
		$va{'p2ratio'} = &round(($tmp_value->{'P2totTDC'}+$tmp_value->{'P3totCOD'})/$rec->{'Cost'},2);
		$va{'p3ratio'} = &round(($tmp_value->{'P2totTDC'}+$tmp_value->{'P3totCOD'})/$rec->{'Cost'},2);
		$va{'tratio'} = &round(($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'}+$tmp_value->{'P2totTDC'}+$tmp_value->{'P2totCOD'}+$tmp_value->{'P3totTDC'}+$tmp_value->{'P3totCOD'})/$rec->{'Cost'},2);
	}else{
		$va{'p3cc'} = 'N/A';
	} 
	&load_db_fields_values($in{'db'},'ID_mediacontracts',$in{'id_mediacontracts'},'*');
}

sub load_tabs2 {
# --------------------------------------------------------
##############################################
## tab5 : Spots
##############################################


	if($in{'action'}){

		if($in{'drop_spot'}){
		
		####################################################################
		####################################################################	
		## Spot Drop
		####################################################################
		####################################################################


			my $id_mediacontracts_rep = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$in{'drop_spot'},'ID_mediacontracts_rep',);
			my $rep_id_mediacontracts_rep = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$id_mediacontracts_rep,'rep_ID_mediacontracts_rep');


			if($id_mediacontracts_rep){

				my $repDist = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$id_mediacontracts_rep,'repDist');
				my $repCost = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$id_mediacontracts_rep,'repCost');
				my $new_minicontract = 0;

				## Minicontract
				if(!$rep_id_mediacontracts_rep){

					my $repestdate = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$id_mediacontracts_rep,'repESTDate');
					my $repesttime = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$id_mediacontracts_rep,'repESTTime');

					my $sth = Do_SQL("SELECT ID_mediacontracts_rep FROM sl_mediacontracts_rep WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' AND rep_ID_mediacontracts_rep = 0 AND CONCAT(repESTDate,' ',repESTTime) < '$repestdate $repesttime' ORDER BY CONCAT(repESTDate,' ',repESTTime) DESC LIMIT 1;");
					$new_minicontract = $sth->fetchrow();

					if(!$new_minicontract){
						## No hay minicontrato anterior. Replicas asignadas?
						my $sth = Do_SQL("SELECT ID_mediacontracts_rep FROM sl_mediacontracts_rep WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' AND rep_ID_mediacontracts_rep = '$id_mediacontracts_rep' AND CONCAT(repESTDate,' ',repESTTime) > '$repestdate $repesttime' ORDER BY CONCAT(repESTDate,' ',repESTTime) LIMIT 1;");
						$new_minicontract = $sth->fetchrow();
					}

				## Replica
				}else{
					my $sth = &Do_SQL("UPDATE sl_mediacontracts_rep SET repDist = IF(repDist + $repDist > 100, 100,repDist + $repDist) WHERE ID_mediacontracts_rep = '$rep_id_mediacontracts_rep';");
				}

				## Drop Spot
				my $sth = &Do_SQL("DELETE FROM sl_mediacontracts_rep WHERE ID_mediacontracts_rep = '$id_mediacontracts_rep';");

				## Minicontract. Tenia replicas?
				if($new_minicontract){
					my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_mediacontracts_rep WHERE rep_ID_mediacontracts_rep = '$id_mediacontracts_rep';");
					if($sth->fetchrow() == 0){
						$new_minicontract=0;
					}
				}


				## Re Asssign spots?
				if($new_minicontract){

					my $sth = &Do_SQL("UPDATE sl_mediacontracts_rep SET repDist = IF(repDist + $repDist > 100, 100,repDist + $repDist)  WHERE ID_mediacontracts_rep = '$new_minicontract';");
					my $sth = &Do_SQL("UPDATE sl_mediacontracts_rep SET rep_ID_mediacontracts_rep = '$new_minicontract' WHERE rep_ID_mediacontracts_rep = '$id_mediacontracts_rep';");

					my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Mini Contract Re Assigned\nOld:$id_mediacontracts_rep\nNew:$new_minicontract',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('mm_contracts_minireassigned',$in{'id_mediacontracts'});

				}

				my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Deleted: $id_mediacontracts_rep',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				&auth_logging('mm_contracts_spotdeleted',$in{'id_mediacontracts'});
				$va{'message'} = 'Spot Deleted';
			}else{
				$va{'message'} = &trans_txt('notfound');
			}
			delete($in{'action'});
			delete($in{'drop_spot'});

		}else{

		####################################################################
		####################################################################	
		## Spot Add/Update
		####################################################################
		####################################################################

			if(!$in{'repestdate'} or !$in{'repesttime'} or !$in{'repdist'}){
				$va{'message'} = &trans_txt('reqfields');
			}else{

				$in{'repdist'} = int($in{'repdist'});
				

				if($in{'upd_spot'} == 0){
					#######################################################
					#######################################################
					## New Spot
					#######################################################
					#######################################################

					## Minicontract
					my $q1 = "INSERT INTO sl_mediacontracts_rep SET ID_mediacontracts = '$in{'id_mediacontracts'}', 
								rep_ID_mediacontracts_rep = 0, repESTTime = '$in{'repesttime'}', 
								repESTDate = '$in{'repestdate'}', repCost = '$in{'repcost'}', repDist = 100, 
								repStatus = '$in{'repstatus'}', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;";
					my $sth = &Do_SQL($q1);
					my $sth = &Do_SQL("SELECT LAST_INSERT_ID()");
					my ($new_minicontract) = $sth->fetchrow();

					my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Main Spot Added: $new_minicontract',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('mm_contracts_mainspotadded',$in{'id_mediacontracts'});
					$va{'message'} = 'Main Spot Added';

				}elsif($in{'linked_to'}){

					#######################################################
					#######################################################
					## New Replica
					#######################################################
					#######################################################

					my $id_mediacontracts_rep = $in{'upd_spot'};

					my $sth = Do_SQL("SELECT SUM(repDist) AS repDist FROM sl_mediacontracts_rep WHERE rep_ID_mediacontracts_rep = '$id_mediacontracts_rep' GROUP BY rep_ID_mediacontracts_rep;");
					my($sumdist) = $sth->fetchrow();
					$sumdist += $in{'repdist'};

					## Minicontract / Replica
					my $q1 = "INSERT INTO sl_mediacontracts_rep SET ID_mediacontracts = '$in{'id_mediacontracts'}', 
								rep_ID_mediacontracts_rep = '$id_mediacontracts_rep', repESTTime = '$in{'repesttime'}', 
								repESTDate = '$in{'repestdate'}', repCost = 0, repDist = $in{'repdist'}, 
								repStatus = '$in{'repstatus'}', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' ;";
					my $sth = &Do_SQL($q1);
					my $sth = &Do_SQL("SELECT LAST_INSERT_ID()");
					my ($new_minicontract) = $sth->fetchrow();
					my ($sth) = &Do_SQL("UPDATE sl_mediacontracts_rep SET repDist = IF(100 - $sumdist > 0, 100 - $sumdist, 0) WHERE ID_mediacontracts_rep = '$id_mediacontracts_rep';");

					my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Added: $new_minicontract',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('mm_contracts_spotadded',$in{'id_mediacontracts'});
					$va{'message'} = 'Replica Added';

				}else{
					

					#######################################################
					#######################################################
					## Spot Update
					#######################################################
					#######################################################


					my $id_mediacontracts_rep = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$in{'upd_spot'},'ID_mediacontracts_rep');

					if($id_mediacontracts_rep){

						my $rep_id_mediacontracts_rep = load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$id_mediacontracts_rep,'rep_ID_mediacontracts_rep');

						## Update
						my $q1 = "UPDATE sl_mediacontracts_rep SET  
								repESTTime = '$in{'repesttime'}', repESTDate = '$in{'repestdate'}', repCost = '$in{'repcost'}', 
								repDist = $in{'repdist'}, ID_admin_users = '$usr{'id_admin_users'}', repStatus = '$in{'repstatus'}'
								WHERE ID_mediacontracts_rep = '$id_mediacontracts_rep' ;";
						my $sth = &Do_SQL($q1);

						my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='Edited: $rep_id_mediacontracts_rep',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
						&auth_logging('mm_contracts_spotedited',$in{'id_mediacontracts'});
						$va{'message'} = 'Spot Edited';

					}else{
						$va{'message'} = &trans_txt('notfound');
					}
				}
			
			}
			delete($in{'action'});
			delete($in{'upd_spot'});			
		}

	}


	my ($sth)=&Do_SQL("SELECT * FROM sl_mediacontracts WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';");
	my ($rec) = $sth->fetchrow_hashref();


	my ($sthm)=&Do_SQL("SELECT ID_mediacontracts_rep FROM sl_mediacontracts_rep WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' AND rep_ID_mediacontracts_rep = 0 ORDER BY CONCAT(repESTDate,' ',repESTTime);");
	$va{'matches'} = $sthm->rows();

	if($va{'matches'}){

		while(my($id_mediacontracts_rep) = $sthm->fetchrow()){

			my ($sth2)=&Do_SQL("SELECT * FROM sl_mediacontracts_rep WHERE ID_mediacontracts_rep = '$id_mediacontracts_rep' OR rep_ID_mediacontracts_rep = '$id_mediacontracts_rep' ORDER BY CONCAT(repESTDate,' ',repESTTime);");

			while($replica = $sth2->fetchrow_hashref()){

				my $this_type;
				my $link_new_spot;
				$va{'repcost'} = 0;
				$va{'linked_to'} = 0;
				if(!$replica->{'rep_ID_mediacontracts_rep'}){
					$this_type = 'Main Spot';
					$this_style='bgcolor="#f2f2f2"';
					$va{'repcost'} = $replica->{'repCost'};
					$link_new_spot = "<a href='#' title='Add New Replica' rel='#overlay_new_spot_$replica->{'ID_mediacontracts_rep'}'><img src='[va_imgurl]default/b_add.gif'></a>";
				}else{
					$this_type = 'Replica';
					$this_style='';
					$replica->{'repCost'} = &load_name('sl_mediacontracts_rep','ID_mediacontracts_rep',$replica->{'rep_ID_mediacontracts_rep'},'repCost');
				}
				$replica->{'repCost'} = round($replica->{'repCost'} * ($replica->{'repDist'}/100),2);

				## Va's for edition purpposes
				$va{'id_mediacontracts_rep'} = $replica->{'ID_mediacontracts_rep'};
				$va{'this_type'} = $this_type;
				$va{'repestdate'} = $replica->{'repESTDate'};
				$va{'repesttime'} = $replica->{'repESTTime'};
				$va{'repcost_disabled'} = $replica->{'rep_ID_mediacontracts_rep'} ? 'disabled="disabled" ' : '';
				$va{'repdist'} = $replica->{'repDist'};
				$va{'repstatus'} = $replica->{'repStatus'};

				## Next Spot.
				my $sth_qs = &Do_SQL("SELECT CONCAT(repESTDate,' ',repESTTime)AS nexspot FROM sl_mediacontracts_rep WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' AND CONCAT(repESTDate,' ',repESTTime) > '$replica->{'repESTDate'} $replica->{'repESTTime'}' ORDER BY CONCAT(repESTDate,' ',repESTTime) LIMIT 1;");
				my ($next_date) = $sth_qs->fetchrow();

				my $mod = $next_date ? " AND CONCAT(Date, ' ', Time) < '$next_date' " : ""; 

				$sth = &Do_SQL("SELECT 
					SUM(IF(TIMESTAMPDIFF(MINUTE, '$replica->{'repESTDate'} $replica->{'repESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN -1 AND 90,1,0))AS P1, 
					SUM(IF(TIMESTAMPDIFF(MINUTE, '$replica->{'repESTDate'} $replica->{'repESTTime'}', CONCAT(Date, ' ', Time) ) BETWEEN 91 AND 360,1,0))AS P2, 
					SUM(IF(TIMESTAMPDIFF(MINUTE, '$replica->{'repESTDate'} $replica->{'repESTTime'}', CONCAT(Date, ' ', Time) ) > 360,1,0))AS P3
					FROM sl_leads_calls WHERE ID_mediacontracts = '$in{'id_mediacontracts'}' AND IO='In' $mod ");
					($va{'p1calls'},$va{'p2calls'},$va{'p3calls'})=$sth->fetchrow();
					$va{'tcalls'} = $va{'p1calls'}+$va{'p2calls'}+$va{'p3calls'};

				### Cost Per call
				if ($va{'p1calls'}){
					$va{'p1cc'} = &format_price($replica->{'repCost'}/$va{'p1calls'});
				}else{
					$va{'p1cc'} = 'N/A';
				}
				if ($va{'p2calls'}){
					$va{'p2cc'} = &format_price($replica->{'repCost'}/$va{'p2calls'});
				}else{
					$va{'p2cc'} = 'N/A';
				}
				if ($va{'p3calls'}){
					$va{'p3cc'} = &format_price($replica->{'repCost'}/$va{'p3calls'});
				}else{
					$va{'p3cc'} = 'N/A';
				}
				if ($va{'tcalls'}){
					$va{'tcc'} = &format_price($replica->{'repCost'}/$va{'tcalls'});
				}else{
					$va{'tcc'} = 'N/A';
				}

				my ($tmp_value) = &load_contract_totals($rec->{'ID_mediacontracts'},$replica->{'repESTTime'},$replica->{'repESTDate'},$rec->{'DestinationDID'});

				($rec->{'P1Calls'},
						$tmp_value->{'P1totTDC'},$tmp_value->{'P1totCOD'},$tmp_value->{'P1qtyTDC'},$tmp_value->{'P1qtyCOD'},
						$tmp_value->{'StotTDC'},$tmp_value->{'StotCOD'},$tmp_value->{'SqtyTDC'},$tmp_value->{'SqtyCOD'},
						$tmp_value->{'COGS'}) = &load_count_rep($rec->{'ID_mediacontracts'},$replica->{'repESTDate'},$replica->{'repESTTime'});

				#va_P1totTDC

				### Totals to Vars
				foreach $key (keys %{$tmp_value}){
					if ($key =~ /tot/){
						$va{lc($key)} = &format_price($tmp_value->{$key});
					}else{
						$va{lc($key)} = $tmp_value->{$key};
					}
				}

				
				## Calculate Totals
				$va{'p1tot'} = &format_price($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'});
				$va{'p2tot'} = &format_price($tmp_value->{'P2totTDC'}+$tmp_value->{'P2totCOD'});
				$va{'p3tot'} = &format_price($tmp_value->{'P3totTDC'}+$tmp_value->{'P3totCOD'});
				$va{'ttot'}  = &format_price($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'}+$tmp_value->{'P2totTDC'}+$tmp_value->{'P2totCOD'}+$tmp_value->{'P3totTDC'}+$tmp_value->{'P3totCOD'});
				$va{'ttottdc'} = &format_price($tmp_value->{'P1totTDC'}+$tmp_value->{'P2totTDC'}+$tmp_value->{'P3totTDC'});
				$va{'tqtytdc'} = $tmp_value->{'P1qtyTDC'}+$tmp_value->{'P2qtyTDC'}+$tmp_value->{'P3qtyTDC'};
				$va{'ttotcod'} = &format_price($tmp_value->{'P1totCOD'}+$tmp_value->{'P2totCOD'}+$tmp_value->{'P3totCOD'});
				$va{'tqtycod'} = $tmp_value->{'P1qtyCOD'}+$tmp_value->{'P2qtyCOD'}+$tmp_value->{'P3qtyCOD'};
				$va{'p1qty'} = $tmp_value->{'P1qtyTDC'}+$tmp_value->{'P1qtyCOD'};
				$va{'p2qty'} = $tmp_value->{'P2qtyTDC'}+$tmp_value->{'P2qtyCOD'};
				$va{'p3qty'} = $tmp_value->{'P3qtyTDC'}+$tmp_value->{'P3qtyCOD'};
				$va{'tqty'}  = $tmp_value->{'P1qtyTDC'}+$tmp_value->{'P1qtyCOD'} + $tmp_value->{'P2qtyTDC'}+$tmp_value->{'P2qtyCOD'} + $tmp_value->{'P3qtyTDC'}+$tmp_value->{'P3qtyCOD'};
				
				## Ratios
				if ($rec->{'Cost'}>0){
					$va{'p1ratio'} = &round(($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'})/$rec->{'Cost'},2);
					$va{'p2ratio'} = &round(($tmp_value->{'P2totTDC'}+$tmp_value->{'P3totCOD'})/$rec->{'Cost'},2);
					$va{'p3ratio'} = &round(($tmp_value->{'P2totTDC'}+$tmp_value->{'P3totCOD'})/$rec->{'Cost'},2);
					$va{'tratio'} = &round(($tmp_value->{'P1totTDC'}+$tmp_value->{'P1totCOD'}+$tmp_value->{'P2totTDC'}+$tmp_value->{'P2totCOD'}+$tmp_value->{'P3totTDC'}+$tmp_value->{'P3totCOD'})/$rec->{'Cost'},2);
				}else{
					$va{'p3cc'} = 'N/A';
				}

				$va{'searchresults'} .= "<tr $this_style>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>
												<a href=\"$script_url?cmd=$in{'cmd'}&view=$in{'id_mediacontracts'}&tab=5&action=1&drop_spot=$replica->{'ID_mediacontracts_rep'}\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' alt='Delete' title='Delete' border='0'></a>&nbsp;&nbsp;
												<a href='#' title='Edit' rel='#overlay_edit_spot_".$replica->{'ID_mediacontracts_rep'}."'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' alt='Edit' title='Edit' border='0'></a>&nbsp;&nbsp;
												<a href='#' title='View' rel='#overlay_view_spot_".$replica->{'ID_mediacontracts_rep'}."'><img src='$va{'imgurl'}/app_bar/small_phpbrain.gif'></a>
												$link_new_spot
											</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$this_type</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$replica->{'repESTDate'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$replica->{'repESTTime'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($replica->{'repCost'})." ($replica->{'repDist'} %)</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>$va{'tcalls'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>$va{'tcc'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>$replica->{'repStatus'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";

				## New Replicas Overlay
				if(!$replica->{'rep_ID_mediacontracts_rep'}){
					my $tmp = $va{'repcost'};
					$va{'this_type'}='New Replica';
					$va{'repcost_disabled'} = 'disabled="disabled"';
					$va{'repcost'} = 0;
					$va{'linked_to'}=1;
					$va{'overlay_spots'} .='<div class="apple_overlay" id="overlay_new_spot_'.$replica->{'ID_mediacontracts_rep'}.'">'."\n".'
												<div class="contentWrap">
													'.&build_page('func:overlay_mm_contracts_spots_edit.html').'
												</div>'."\n".'
											</div>'."\n";
					$va{'this_type'}='Main Spot';
					$va{'repcost_disabled'} = '';
					$va{'repcost'} = $tmp;
					$va{'linked_to'}=0;
				}


				$va{'overlay_spots'} .='<div class="apple_overlay" id="overlay_edit_spot_'.$replica->{'ID_mediacontracts_rep'}.'">'."\n".'
											<div class="contentWrap">'.&build_page('func:overlay_mm_contracts_spots_edit.html').'</div>'."\n".'
										</div>'."\n";			

				$va{'overlay_spots'} .='<div class="apple_overlay" id="overlay_view_spot_'.$replica->{'ID_mediacontracts_rep'}.'">'."\n".'
										<div class="contentWrap">
											<br><br><center><h3>'.$this_type.' ('.$replica->{'repESTDate'}.' '.$replica->{'repESTTime'}.')</h3></center><br><br>
											'.&build_page('func:overlay_mm_contracts_spots_view.html').'
										</div>'."\n".'
									</div>'."\n";
				delete($va{'linked_to'});
			}
		
		}

	}else{
		$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
		$va{'searchresults'} .= "   <td class='smalltext' colspan='8'>".&trans_txt('search_nomatches')."</td>\n";
		$va{'searchresults'} .= "</tr>\n";
		$va{'spots_modal'} = '';
	}

	## New Spot
	$va{'this_type'} = 'New Spot';
	$va{'id_mediacontracts_rep'} = 0;
	$va{'repestdate'} = $rec->{'ESTDay'};
	$va{'repesttime'} = '';
	$va{'repcost'} = 0;
	$va{'repdist'} = 0;
	$va{'repcost_disabled'} = '';
	$va{'overlay_spots'} .='<div class="apple_overlay" id="overlay_new_spot">'."\n".'
									<div class="contentWrap">'.&build_page('func:overlay_mm_contracts_spots_edit.html').'</div>'."\n".'
								</div>';
    &load_db_fields_values($in{'db'},'ID_mediacontracts',$in{'id_mediacontracts'},'*');
}

sub load_tabs3{
# --------------------------------------------------------
##############################################
## tab4 : ORDERS
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_mediacontracts='$in{'id_mediacontracts'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT DISTINCT ID_orders,sl_customers.ID_customers, CONCAT(FirstName,' ',LastName1) AS Name,
						PostedDate, sl_orders.Date, sl_orders.Status
						FROM sl_orders INNER JOIN sl_customers USING(ID_customers)
						WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'
						ORDER BY sl_orders.ID_orders DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

			$sth = &Do_SQL("SELECT DISTINCT ID_orders,sl_customers.ID_customers, CONCAT(FirstName,' ',LastName1) AS Name,
						PostedDate, sl_orders.Date, sl_orders.Status
						FROM sl_orders INNER JOIN sl_customers USING(ID_customers)
						WHERE ID_mediacontracts = '$in{'id_mediacontracts'}'
						ORDER BY sl_orders.ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		}

		while ($rec = $sth->fetchrow_hashref){
			($rec->{'PostedDate'} eq '0000-00-00') and ($rec->{'PostedDate'} = '');
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"$script_url?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"$script_url?cmd=opr_customers&view=$rec->{'ID_customers'}\">$rec->{'Name'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PostedDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
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
	$va{'keyname'} = 'Notes';
	&load_db_fields_values($in{'db'},'ID_mediacontracts',$in{'id_mediacontracts'},'*');
}

sub load_tabs4{
# --------------------------------------------------------
##############################################
## tab6 : Calls per DMA
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM `sl_leads_calls` WHERE ID_mediacontracts='$in{'id_mediacontracts'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		$sth = &Do_SQL("SELECT RANK, DMA_DESC,  COUNT(*) AS qty 
							FROM (
							SELECT RANK,DMA_DESC
							FROM `sl_leads_calls` LEFT JOIN sl_zipdma  ON AreCode=LEFT(ID_leads,3) WHERE ID_mediacontracts='$in{'id_mediacontracts'}' GROUP BY `ID_leads`
							) AS tmp
							GROUP BY DMA_DESC ORDER BY qty DESC;
							");

		while ($rec = $sth->fetchrow_hashref){
			if(!$rec->{'DMA_DESC'}){
				$rec->{'DMA_DESC'} = "N/A";
			}
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'RANK'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'DMA_DESC'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'qty'}</td>\n";
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
	$va{'keyname'} = 'Notes';
	&load_db_fields_values($in{'db'},'ID_mediacontracts',$in{'id_mediacontracts'},'*');
}


sub load_tabs5{
# --------------------------------------------------------
##############################################
## tab7 : ORDERS per DMA
##############################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM `sl_orders` WHERE ID_mediacontracts='$in{'id_mediacontracts'}';");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		$sth = &Do_SQL("SELECT RANK, DMA_DESC,SUM(OrderNet) AS tot, SUM(TDC) AS ptdc, COUNT(*) AS qty 
								FROM (
								SELECT RANK,DMA_DESC,OrderNet,if (Ptype='Credit-Card', OrderNet,0) AS TDC
								FROM `sl_orders` LEFT JOIN sl_zipdma  ON ZipCode=Zip WHERE ID_mediacontracts='$in{'id_mediacontracts'}' 
								) AS tmp
								GROUP BY DMA_DESC ORDER BY qty DESC;
								");

		while ($rec = $sth->fetchrow_hashref){
			if(!$rec->{'DMA_DESC'}){
				$rec->{'DMA_DESC'} = "N/A";
			}
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'RANK'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'DMA_DESC'}</td>\n";
			if ($rec->{'tot'}>0){
				$va{'searchresults'} .= "   <td class='smalltext'>".&round($rec->{'ptdc'}/$rec->{'tot'}*100,2)."%</td>\n";
			}else{
				$va{'searchresults'} .= "   <td class='smalltext'>--</td>\n";
			}
			$va{'searchresults'} .= "   <td class='smalltext'>".&format_price($rec->{'tot'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'qty'}</td>\n";
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
	$va{'keyname'} = 'Notes';
	&load_db_fields_values($in{'db'},'ID_mediacontracts',$in{'id_mediacontracts'},'*');
}

1;