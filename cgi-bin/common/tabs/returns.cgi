####################################################################
########             RETURNS                  ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 3){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_returns_notes';
	}elsif($in{'tab'} eq 4){
		## Logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_returns';
	}
}

sub load_tabs1 {
# --------------------------------------------------------
		$in{'drop'} = int($in{'drop'});
		if ($in{'drop'}>0 and $in{'status'} eq 'New'){
			my $upcdel=&load_name('sl_returns_upcs','ID_returns_upcs',$in{'drop'},'UPC');
			&Do_SQL("delete from sl_returns_upcs where ID_returns_upcs=$in{'drop'}");
			&auth_logging("returns_upcs_deleted",$in{'drop'});
			&Do_SQL("update sl_returns set itemsqty=itemsqty-1 where ID_returns=$in{'id_returns'}");
			&auth_logging("UPC $upcdel deleted from return",$in{'id_returns'});
		}elsif($in{'addupc'})				{
			my ($sth) = &Do_SQL("Insert into sl_returns_upcs set ID_returns=$in{'id_returns'},UPC='$in{'addupc'}'");
			&auth_logging('returns_upcs_added',$sth->{'mysql_insertid'});
			&Do_SQL("update sl_returns set itemsqty=itemsqty+1 where ID_returns=$in{'id_returns'}");
			&auth_logging('returns_updated',$in{'id_returns'});
		}
		my (@c) = split(/,/,$cfg{'srcolors'});

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' ");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT ID_returns_upcs
									, sl_skus.UPC
									, IF(ISNULL(InOrder)	,'---',InOrder) AS InOrder
									, IF(ISNULL(sl_returns_upcs.Status),'---',sl_returns_upcs.Status)AS Status
									, ID_sku_products
								FROM sl_returns_upcs 
									LEFT JOIN sl_skus ON IF(sl_returns_upcs.ID_parts < 400000000, (sl_returns_upcs.ID_parts+400000000), sl_returns_upcs.ID_parts)=sl_skus.ID_sku_products
								WHERE ID_returns='$in{'id_returns'}' 
								LIMIT $first,$usr{'pref_maxh'};");

			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$rec->{'Notes'} =~ s/\n/<br>/g;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
				if ($in{'Status'} eq 'New'){
					$va{'searchresults'} .= "  <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'id_returns'}&tab=1&drop=$rec->{'ID_returns_upcs'}\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>$rec->{'UPC'}</td>\n";
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'UPC'}</td>\n";
				}
				if($rec->{'Name'}eq "" and $rec->{'Model'}eq""){
					$rec->{'Name'}=&load_name('sl_parts','ID_parts',substr($rec->{'ID_sku_products'},3,6),'Name') if $rec->{'ID_sku_products'};
					$rec->{'Model'}=&load_name('sl_parts','ID_parts',substr($rec->{'ID_sku_products'},3,6),'Model') if $rec->{'ID_sku_products'};
				}
				$va{'searchresults'} .= "  <td class='smalltext'>".&format_sltvid($rec->{'ID_sku_products'})."</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Model'}/$rec->{'Name'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}	
		}else{
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		
	#}
		
	my $cadjavascript;
	$cadjavascript="<script language='JavaScript' type='text/javascript'>
			[va_autorun_js]
			
			function add_upc(){
				popup_show('popup_addupc', 'item_drag', 'popup_exiti', 'element-right', -1, -1,'tabs');
			}
		</script>
		
		<div id='popup_addupc' style='visibility: hidden; display: none; background-color: #ffffff;'>
			<div class='menu_bar_title' id='item_drag'>
			<img id='popup_exiti' src='[va_imgurl]/[ur_pref_style]/popupclose.gif' />
			&nbsp;&nbsp;&nbsp;Add Regular Item
			</div>
			<div class='formtable'>
			<IFRAME SRC='/cgi-bin/common/apps/schid?cmd=returns_addupcs&id_returns=[in_id_returns]&path=[va_script_url]&cmdo=[in_cmd]' name='rcmd' TITLE='Recieve Commands' width='546' height='250' FRAMEBORDER='0' MARGINWIDTH='0' MARGINHEIGHT='0' SCROLLING='auto'>
			<H2>Unable to do the script</H2>
			<H3>Please update your Browser</H3>
			</IFRAME>	
			</div></div>
		";
	$in{'tab'} = 1 if(!$in{'tab'});	
}

sub load_tabs2 {
# --------------------------------------------------------
		my (@c) = split(/,/,$cfg{'srcolors'});
		$in{'id_customers'} = &load_name('sl_returns','ID_returns',$in{'id_returns'},'ID_customers');
		my ($sth) = &Do_SQL("SELECT COUNT(*) 
							 FROM sl_returns 
							 WHERE ID_customers='$in{'id_customers'}'
							 	AND ID_returns<>$in{'id_returns'};");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT * 
								 FROM sl_returns 
								 WHERE ID_customers='$in{'id_customers'}' 
								 	AND ID_returns<>$in{'id_returns'}
								 LIMIT $first,$usr{'pref_maxh'};");

			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
				$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_returns&view=$rec->{'ID_returns'}'>$rec->{'ID_returns'}</a></td>\n";
				if ($rec->{'ID_orders'}>0){
					$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}'>$rec->{'ID_orders'}</a></td>\n";
				}else{
					$va{'searchresults'} .= "  <td class='smalltext'>---</td>\n";
				}
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Date'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'merAction'}</td>\n";
				$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}	
		}else{
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		
	#}
		
	
}


1;