####################################################################
########             RETURNS                  ########
####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 2){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_returns_notes';
	}elsif($in{'tab'} eq 3){
		## Logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_returns';
	}
}

sub load_tabs1 {

			#&cgierr("MSG: $perm{'returnswarehouse_tab2'}");
			# $perm{'returnswarehouse_tab3'}=1 if (!$perm{'returnswarehouse_tab3'});
			# if (!$perm{'returnswarehouse_tab3'}) { 
				# $va{'searchresults'} = qq|
					# <tr>
						# <td colspan='6' align="center">|.&trans_txt('not_auth').qq|</td>
					# </tr>\n|;
			# }else{
				$in{'drop'} = int($in{'drop'});
				if ($in{'drop'}>0)
				{
					my $upcdel=&load_name('sl_returns_upcs','ID_returns_upcs',$in{'drop'},'UPC');
					&Do_SQL("delete from sl_returns_upcs where ID_returns_upcs=$in{'drop'}");
					&auth_logging("returns_upcs_deleted",$in{'drop'});
					&Do_SQL("update sl_returns set itemsqty=itemsqty-1 where ID_returns=$in{'id_returns'}");
					&auth_logging("UPC $upcdel deleted from return",$in{'id_returns'});
				}
				elsif($in{'addupc'})
				{
					my ($sth) = &Do_SQL("Insert into sl_returns_upcs set ID_returns=$in{'id_returns'},UPC='$in{'addupc'}'");
					&auth_logging('returns_upcs_added',$sth->{'mysql_insertid'});
					&Do_SQL("update sl_returns set itemsqty=itemsqty+1 where ID_returns=$in{'id_returns'}");
					&auth_logging('returns_updated',$in{'id_returns'});
				}
				my (@c) = split(/,/,$cfg{'srcolors'});
				#GV Inicia modificación 24jun2008
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns='$in{'id_returns'}' and UPC!=''");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					(!$in{'nh'}) and ($in{'nh'}=1);
					$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
					($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
					my ($sth) = &Do_SQL("SELECT ID_returns_upcs,sl_returns_upcs.UPC, if(isnull(InOrder),'---',InOrder)as InOrder, if(isnull(sl_returns_upcs.Status),'---',sl_returns_upcs.Status)as Status, ID_sku_products,Model, Name FROM sl_returns_upcs left join sl_skus on(sl_returns_upcs.UPC=sl_skus.UPC) left join sl_products on(sl_skus.ID_products=sl_products.ID_products) WHERE ID_returns='$in{'id_returns'}'  and sl_returns_upcs.UPC!='' LIMIT $first,$usr{'pref_maxh'};");
					#GV Termina modificación 24jun2008
					my $cmd="";
					if($perm{'mer_products_view'} or $perm{'allperm'}=~/mer_products_view/)
					{
						$cmd="mer_products";
					}
					elsif($perm{'products_view'} or $perm{'allperm'}=~/products_view/)
					{
						$cmd="products";
					}
#					$num=keys (%perm);
#					$cad="";
#					foreach $key (sort(keys %perm)) {
#						$cad.="$key=$perm{$key};\n";
#    			}
#    			&cgierr("MES: $cad");
#					&cgierr("MES: $num,$perm{'products_view'}, $perm{'mer_products_view'}, $cad");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$rec->{'Notes'} =~ s/\n/<br>/g;
						#$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick=\"trjump('$script_url?cmd=$cmd&view=".substr($rec->{'ID_sku_products'},3,6)."')\">\n";
						$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
						$va{'searchresults'} .= "  <td class='smalltext'><a href=\"$script_url?cmd=$in{'cmd'}&modify=$in{'id_returns'}&tab=3&drop=$rec->{'ID_returns_upcs'}\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a>$rec->{'UPC'}</td>\n";
						if($rec->{'Name'}eq"" and $rec->{'Model'}eq"")
						{
							$rec->{'Name'}=&load_name('sl_parts','ID_parts',substr($rec->{'ID_sku_products'},3,6),'Name');
							$rec->{'Model'}=&load_name('sl_parts','ID_parts',substr($rec->{'ID_sku_products'},3,6),'Model');
						}
						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Model'}/$rec->{'Name'}</td>\n";
#						$va{'searchresults'} .= "  <td class='smalltext'>".&format_sltvid($rec->{'ID_sku_products'})."</td>\n";
#						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'InOrder'}</td>\n";
#						$va{'searchresults'} .= "  <td class='smalltext'>$rec->{'Status'}</td>\n";
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
		#return "<a name='tabs' id='tabs'>&nbsp;</a> $cadjavascript " . &build_page('returnswarehouse_tab'.$in{'tab'}.'.html') .$tab_jump;			
}

1;