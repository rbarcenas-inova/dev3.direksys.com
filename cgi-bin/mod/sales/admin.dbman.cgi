##################################################################
##########     PRODUCTS PAGES       	######################
##################################################################

sub prod_now {
# --------------------------------------------------------
	$in{'action'}=1;
	&load_cfg('sl_products');
	&prod_search;
}

sub prod_today {
# --------------------------------------------------------
	$in{'action'}=1;
	&load_cfg('sl_products');
	&prod_search;
}

sub prod_info {
# --------------------------------------------------------
# Last Modified on: 03/17/09 17:15:01
# Last Modified by: MCC C. Gabriel Varela S: Parámetros sltv_itemshipping
# Last Modified by RB on 12/07/2010: Se agregan parametros para sltv_itemshipping
	
	if ($in{'id_products'}){
		&load_cfg('sl_products');
		my (%tmp) = &get_record('ID_products',$in{'id_products'},'sl_products');
		foreach $key (keys %tmp){
			$in{$key} = $tmp{$key};
		}
		$in{'sprice'} = &format_price($in{'sprice'});
		
		### Calculate Shipping
		($va{'shptotal1'},$va{'shptotal2'},$va{'shptotal3'},$va{'shptotal1pr'},$va{'shptotal2pr'},$va{'shptotal3pr'},$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($in{'edt'},$in{'sizew'},$in{'sizeh'},$in{'sizel'},$in{'weight'},$in{'id_packingopts'},$in{'shipping_table'},$in{'shipping_discount'},$in{'id_products'});
		## US Continental
		$va{'shptotal1'} = &format_price($va{'shptotal1'});
		$va{'shptotal2'} = &format_price($va{'shptotal2'});		
		## Puerto Rico
		$va{'shptotal1pr'} = &format_price($va{'shptotal1pr'});
		$va{'shptotal2pr'} = &format_price($va{'shptotal2pr'});				
		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus  WHERE id_products='$in{'id_products'}' and (choice1 != '' or choice2 != '' or choice3 != '' or choice4 != '')");
		if ($sth->fetchrow>0){ 
			&lista_choice();
			for (1..4){
				if($in{'choicename'.$_}){
					$va{'searchresults'} .= "<tr>\n";					
					$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$in{'choicename'.$_}</td>\n";
					$va{'searchresults'} .= "   <td class='smalltext' valign='top'>$va{'cho'.$_}</td>\n";
					$va{'searchresults'} .= "</tr>\n";					
				}
			}
		}else{
			$va{'searchresults'} .= qq|
				<tr>
					<td colspan='2' align='center'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}	
		$va{'listskus'}=$va{'searchresults'};
		
		print "Content-type: text/html\n\n";
		print &build_page('prod_showprod.html');
		return;
	}
	print "Content-type: text/html\n\n";
	print &build_page('prod_search.html');
}

sub prod_search {
# --------------------------------------------------------
	
	#@db_cols = ('ID_products','Model','Name','SPrice');
	@headerfields = ('ID_products','Model','Name','SPrice');
	#@db_cols;
	@db_cols = ('ID_products','Model','Name','ID_brands','ManufacterSKU','ProductType','SPrice');
	if ($in{'action'}){
		$header_fields = join(",",@db_cols);

		if ($in{'pricerange'}){
			($from,$to) = split(/-/,$in{'pricerange'});
			#$from =~ s/\$ //;
			#$to =~ s/\$ //;
			$in{'from_sprices'} = $from;
			$in{'to_sprices'} = $to;
		}
		
		my ($numhits, @hits) = &prodquery('sl_products');
		$db_valid_types{'sprice'} = "currency";
		if ($numhits > 0){
			&prod_search_result($numhits, @hits);
			return;
		}else{
			$va{'message'}=&trans_txt('search_nomatches');
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page('prod_search.html');
}

sub prod_search_result {
# --------------------------------------------------------	
	
	my ($numhits,@hits) = @_;
	$va{'matches'} = $numhits;
	my (%tmp, $qs, $add_title);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($rows) = ($#hits+1)/($#db_cols+1);
	for (0 .. $rows-1) {
		$d = 1 - $d;
		%tmp = &array_to_hash($_, @hits);
		$page .= qq|		    <tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onClick="trjump('/cgi-bin/mod/sales/admin?cmd=prod_info&id_products=$tmp{$db_cols[0]}')">\n|;
		for (0..$#headerfields){
			if ($headerfields[$_] =~ /([^:]+):([^\.]+)\.([^\.]+)/){
				## 1)DB  2)ID  3)Name
				$page .= "	<td valign='top'><a href='".&build_link($1,$2,$tmp{$2})."' class='error'>". &load_name($1,$2,$tmp{$2},$3) ."</a></td>\n";
			}elsif($headerfields[$_] eq 'ID_products'){
				$page .= qq|	<td nowrap valign='top'>|. &format_sltvid($tmp{$headerfields[$_]}) .qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} eq "date"){
				$page .= qq|	<td align="center" nowrap valign='top'>| . &sql_to_date($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif($db_valid_types{lc($headerfields[$_])} eq "currency"){
				$page .= qq|	<td align="right" nowrap valign='top'>| . &format_price($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}elsif ($db_valid_types{lc($headerfields[$_])} eq "numeric"){
				$page .= qq|	<td align="right" nowrap valign='top'>| . &format_number($tmp{$headerfields[$_]}) . qq|&nbsp;</td>\n|;
			}else{
				$tmp{$headerfields[$_]} =~ s/\n/<br>/g;
				$page .= qq|	<td valign='top'>$tmp{$headerfields[$_]}&nbsp;</td>\n|;
			}
		}
		$page .= "		</tr>";
	}
	$va{'searchresults'} = $page;
	($va{'pageslist'},$va{'qs'})  = &pages_list($in{'nh'},"$script_url",$numhits,$usr{'pref_maxh'});
	print "Content-type: text/html\n\n";
	print &build_page('prod_list.html');
}

##################################################################
############                HOME                 #################
##################################################################
sub dbman_home {
# --------------------------------------------------------
	
	if  ($in{'add'}) 			{ &html_add_select;
	}elsif ($in{'search'})		{ &html_search_select; 
	}elsif ($in{'edit'})		{ &html_edit_select; 
	}elsif ($in{'modify'})		{ &html_modify_form_record;
	}elsif ($in{'lookfor'})		{ &html_small_search;
	}elsif ($in{'view'})		{ &html_view_record;
	}else{
		foreach $key (keys %in) {
			if ($in{$key} eq &trans_txt('btn_edit')){
				$in{'modify'} = substr($key,5);
				$in{'edit'}   = "Select" ;
				&html_edit_select;
				return;
			}elsif ($in{$key} eq &trans_txt('btn_del')){
				$in{'delete'} = substr($key,5);
				&html_delete;
				return;
			}elsif ($in{$key} eq &trans_txt('btn_view')){
				$in{'view'} = substr($key,5);
				&html_view_record;
				return;
			}
		}
		&html_search_select;
	}
}

1;

