

sub choices {
# --------------------------------------------------------
# Last Modified on: 09/12/08 13:54:09
# Last Modified by: MCC C. Gabriel Varela S: Se agrega par?metro id_products_exchange
	print "Content-type: text/html\n\n";
	if ($in{'id_products'}){
		my ($url);
		foreach $key (sort keys %in) {
			if ($key !~ /^ajax|url/){
				$url .= "$key=$in{$key}&";
			}
		}
		print qq|
				<table border="0" cellspacing="0" cellpadding="4" width="400" class="formtable">
			 		<tr>
			 			<td class="menu_bar_title" colspan="6" align="center">Vendor / Choices / Manufacter SKUs</td>
			 		</tr>\n|;
		my ($family);
		if (length($in{'id_products'})>6){
			$family = substr($in{'id_products'},3,6);
		}else{
			$family = $in{'id_products'};
		}
		#################################
		##### build Vendor SKUs
		#################################
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products='$family' AND Status='Active' ORDER BY ID_sku_products;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			(!$rec->{'choice2'}) and ($rec->{'choice2'}='---');
			(!$rec->{'choice3'}) and ($rec->{'choice3'}='---');
			(!$rec->{'choice4'}) and ($rec->{'choice4'}='---');
			print qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'onClick="trjump('$in{'url'}?$url&ajaxresp=$rec->{'ID_sku_products'}&id_products_exchange=$rec->{'ID_sku_products'}')">
				<td align="center" class="smalltext" $style>|.format_sltvid($rec->{'ID_sku_products'}).qq|</a></td>
				<td align="center" class="smalltext" $style>$rec->{'choice1'}</td>
				<td align="center" class="smalltext" $style>$rec->{'choice2'}</td>
				<td align="center" class="smalltext" $style>$rec->{'choice3'}</td>
				<td align="center" class="smalltext" $style>$rec->{'choice4'}</td>
				<td align="center" class="smalltext" $style>$rec->{'VendorSKU'}</td>
			</tr>\n|;
		}
		print qq|
					<tr>
						<td class="smalltext" colspan="6"></td>
					</tr>
				</table>\n|;
	}
}

sub inventory {
# --------------------------------------------------------
# Last Modified on: 05/18/09 17:23:46
# Last Modified by: MCC C. Gabriel Varela S: Se adapta para recibir ids de 9 d?gitos
# Last Time Modified By RB on 2/19/10 1:43 PM : Se agrupa por ID_parts

	my ($count,$d);
	print "Content-type: text/html\n\n";

	if ($in{'id_products'}){

		my (@cols) = split(/,/,$in{'cols'});
		print qq|
			<table border="0" cellspacing="0" cellpadding="4" width="400" class="formtable">
	 		<tr>
	 			<td class="menu_bar_title" align="center">$cols[0]</td>
	 			<td class="menu_bar_title" align="center">$cols[1]</td>
	 			<td class="menu_bar_title" align="center">$cols[2]</td>
	 			<td class="menu_bar_title" align="center">$cols[3]</td>
	 		</tr>\n|;

	 	my ($str_name);
	 	my (@c) = split(/,/,$cfg{'srcolors'});		
		
		### Check if it is SET
		my ($sth) = &Do_SQL("SELECT IsSet FROM sl_skus WHERE ID_products='$in{'id_products'}' or ID_sku_products=$in{'id_products'}");
		if ($sth->fetchrow eq 'Y'){
			my ($sth) = &Do_SQL("SELECT * FROM sl_parts,sl_skus_parts WHERE ID_sku_products like '%$in{'id_products'}' AND sl_parts.ID_parts=sl_skus_parts.ID_parts GROUP BY sl_parts.ID_parts;");
			while ($rec = $sth->fetchrow_hashref){
				print qq|
			 		<tr>
			 			<td align="center" colspan='5' class="smalltext">$rec->{'Model'}/$rec->{'Name'}</td>
			 		</tr>\n|;
			 	&inventory_details(400000000+$rec->{'ID_parts'},$in{'extradata'});	
			}
			
		}else{	
			&inventory_details($in{'id_products'},$in{'extradata'});
		}

		print qq|
				<tr>
					<td class="smalltext" colspan="5"></td>
				</tr>
			</table>\n|;
	}
}

sub inventory_details {
# --------------------------------------------------------
# Last Modified on: 02/24/09 12:25:43
# Last Modified by: MCC C. Gabriel Varela S: Se cambian consultas para mostrar agrupado por warehouses e Id de producto
# Last Modified on: 26/01/2015 02:26 pm
# Last Modified by: ISC Alejandro Diaz: Se corrije problema que evitaba mostrar el inventario

	my ($id_products,$extradata) = @_;
	my ($count,$sth,$modquery);

	my ($id_warehouses,$nopack,$include_all) = split(/:/, $extradata);
	$modquery .= " AND ID_warehouses = $id_warehouses" if ($id_warehouses > 0);
	$modquery .= " AND Location<>'PACK'" if ($nopack);
	$modquery .= " AND sl_warehouses.Type = 'Physical'" if (!$include_all);

	$sth = &Do_SQL("SELECT 
		sl_skus.ID_sku_products,
		sl_warehouses.ID_warehouses,
		SUM(sl_warehouses_location.Quantity) AS Quantity
	FROM sl_skus 
	INNER JOIN sl_warehouses_location ON (sl_skus.ID_sku_products=sl_warehouses_location.ID_products)
	INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_warehouses_location.ID_warehouses
	INNER JOIN sl_locations ON sl_locations.Code=sl_warehouses_location.Location AND sl_locations.ID_warehouses=sl_warehouses_location.ID_warehouses
	WHERE sl_skus.ID_sku_products = '$id_products'
	$modquery 
	AND sl_warehouses_location.Quantity > 0 
	AND sl_skus.Status='Active'
	AND sl_warehouses.Status='Active'
	AND sl_locations.Status='Active'
	GROUP BY sl_warehouses.ID_warehouses, sl_skus.ID_sku_products
	ORDER BY sl_warehouses.ID_warehouses;");

	my ($qty_inbatch) = &skus_quantity_inbatch($id_products);

	while ($rec = $sth->fetchrow_hashref){

		$d = 1 - $d;

		my $this_style = $rec->{'Quantity'} < $qty_inbatch ? qq|style="color:red"| : '';
		
		print qq|
		<tr bgcolor='$c[$d]'>
			<td class="smalltext">|.format_sltvid($rec->{'ID_sku_products'}).qq|</a></td>
			<td class="smalltext">($rec->{'ID_warehouses'}) |.&load_db_names('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'[Name]'). qq|</td>
			<td class="smalltext" align="right"><span $this_style>$qty_inbatch</span></td>
			<td class="smalltext" align="right"><span $this_style>$rec->{'Quantity'}</span></td>
		</tr>\n|;
		++$count;
	}

	if (!$count){
		print qq|
		<tr>
				<td class="smalltext" colspan="3" align="center">|.&trans_txt('search_nomatches') .qq|</td>
			</tr>\n|;
	}
	return;
}


sub prodlist1 {
# --------------------------------------------------------

	##/cgi-bin/common/apps/ajaxbuild?ajaxbuild=prodlist1&id_categories=[in_id_categories]&id_shows=[in_id_shows]&url=[va_script_url]
	my ($url);
	foreach $key (sort keys %in) {
		if ($key !~ /^ajax/){
			$url .= "$key=$in{$key}&";
		}
	}
	print "Content-type: text/html\n\n";
	print qq|
					<IFRAME SRC="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=prodlist2&$url" name="rcmd" TITLE="Recieve Commands" width="540" height="250" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
					<H2>Unable to do the script</H2>
					<H3>Please update your Browser</H3>
					</IFRAME>\n|;
}



sub serlist1 {
# --------------------------------------------------------

	##/cgi-bin/common/apps/ajaxbuild?ajaxbuild=prodlist1&id_categories=[in_id_categories]&id_shows=[in_id_shows]&url=[va_script_url]
	my ($url);
	foreach $key (sort keys %in) {
		if ($key !~ /^ajax/){
			$url .= "$key=$in{$key}&";
		}
	}
	print "Content-type: text/html\n\n";
	print qq|
					<IFRAME SRC="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=serlist2&$url" name="rcmd" TITLE="Recieve Commands" width="540" height="50" FRAMEBORDER="0" MARGINWIDTH="0" MARGINHEIGHT="0" SCROLLING="auto">
					<H2>Unable to do the script</H2>
					<H3>Please update your Browser</H3>
					</IFRAME>\n|;
}

sub serlist2 {
# --------------------------------------------------------

	&html_print_headers('SOSL');
	my ($query);
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my (@cols) = split(/,/,$in{'cols'});
	print qq|
				  <form action="/cgi-bin/mod/$usr{'application'}/dbman" method="post" name="sitform" target="_top">
					<input type="hidden" name="cmd" value="opr_orders">
					<input type="hidden" name="view" value="$in{'id_orders'}">
					<input type="hidden" name="tab" value="1">
					<input type="hidden" name="action" value="1">
					<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
						<tr>
				 			<td class="menu_bar_title" align="center">$cols[0]</td>
				 			<td class="menu_bar_title" align="center">$cols[1]</td>
				 			<td class="menu_bar_title" align="center">$cols[2]</td>
				 			<td class="menu_bar_title" align="center">$cols[3]</td>
				 			<td class="menu_bar_title" align="center">$cols[4]</td>
				 			<td class="menu_bar_title" align="center">$cols[5]</td>
				 		</tr>\n|;
	my ($sth) = &Do_SQL("SELECT * FROM sl_services WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		print qq|
						<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class="smalltext" valign="top"><input type="checkbox" name="add_itemser$rec->{'ID_services'}" value="add_itemser" class="checkbox"></td>
							<td class="smalltext" valign="top" nowrap>|.$rec->{'ID_services'}.qq|</a></td>
							<td class="smalltext">$rec->{'Name'}<br>$rec->{'Description'}</td>
							<td class="smalltext" align="right" valign="top" nowrap>|.&format_price($rec->{'SPrice'}).qq|</td>
							<td class="smalltext" align="right" valign="top" nowrap>|.$rec->{'SalesPrice'}.qq|</td>
							<td class="smalltext" align="right" valign="top" nowrap>|.$rec->{'Tax'}.qq|</td>
						</tr>\n|;		
	}
	print qq|
							<tr>
								<td class="smalltext" colspan="6"></td>
							</tr>
						</table>
					<p align="center"><input type="submit" value="Add ItemSer" class="button">
					</form>\n|;
}






sub data_stats {
# --------------------------------------------------------
# Author: Unknown
# Created on: Unknown
# Last Modified on: 07/23/2008
# Last Modified by: Jose Ramirez Garcia
# Description : the user 1327 was excluded in querys
# Forms Involved: 
# Parameters : 

	my ($rec);
	
	$rec{'callstotal'} = '---';
	$rec{'profittotal'} = '---';
	
	## Today Sales
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE Date=Curdate() AND Status NOT IN ('System Error','Void') AND sl_orders.ID_admin_users!='1327';");
	$rec{'orderstotal'} =  &format_number($sth->fetchrow);	

	my ($sth) = &Do_SQL("SELECT SUM(OrderNet) FROM sl_orders WHERE Date=Curdate() AND Status NOT IN ('System Error','Void') AND sl_orders.ID_admin_users!='1327';");
	$rec{'salestotal'} =  &format_price($sth->fetchrow);		

	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.Date=Curdate() AND sl_orders.ID_orders=sl_orders_payments.ID_orders AND sl_orders.Status NOT IN ('System Error','Void') AND sl_orders.ID_admin_users!='1327';");
	my ($totsales) = $sth->fetchrow;

	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders,sl_orders_payments WHERE sl_orders.Date=Curdate() AND sl_orders.ID_orders=sl_orders_payments.ID_orders AND Type='Credit-Card' AND sl_orders.Status NOT IN ('System Error','Void') AND sl_orders.ID_admin_users!='1327';");
	$aux =  $sth->fetchrow;	
	if ($totsales and $aux){
		$rec{'ccsalestotal'} = &format_number($aux/$totsales*100) .'%';
	}else{
		$rec{'ccsalestotal'} = '0 %';
	}

	$rec{'productslist'} = qq|
													 <table border="0" cellspacing="0" cellpadding="2" width="100%">
														 <tr>
													     <td class="menu_bar_title"></td>
													     <td class="menu_bar_title">ID</td>
													     <td class="menu_bar_title">Model/Name</td>
													     <td class="menu_bar_title">Prices</td>
													     <td class="menu_bar_title">Qty</td>
													     <td class="menu_bar_title">Tot. Sales</td>
														 </tr>\n|;
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders,sl_orders_products WHERE sl_orders.Date=Curdate() AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Status NOT IN ('System Error','Void') AND sl_orders.ID_admin_users!='1327';");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT *,SUM(Quantity) as TotQty,SUM(SalePrice) as TotSale FROM sl_orders,sl_orders_products WHERE sl_orders.Date=Curdate() AND sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.Status NOT IN ('System Error','Void') AND ID_products>100000000 AND sl_orders_products.Status='Active' AND sl_orders.ID_admin_users!='1327' GROUP BY RIGHT(ID_products,6);");
		while ($tmp = $sth->fetchrow_hashref){
			$d = 1 - $d;
			if ($tmp->{'ID_products'}=~ /^1/){
				$prod_name = &load_db_names('sl_products','ID_products',substr($tmp->{'ID_products'},3,6),"[Model]<br>[Name]");
			}elsif ($tmp->{'ID_products'}=~ /^6/){
				$prod_name = &load_db_names('sl_services','ID_services',substr($tmp->{'ID_products'},3,6),"[Name]");
			}
			$rec{'productslist'} .= qq|
										<tr>
									    <td></td>
									    <td valign="top">|.&format_sltvid(substr($tmp->{'ID_products'},3,6)).qq|</td>
									    <td valign="top">$prod_name</td>
									    <td valign="top">|.&format_price($tmp->{'SalePrice'}).qq|</td>
									    <td valign="top">$tmp->{'TotQty'}</td>
									    <td valign="top" nowrap align="right">|.&format_price($tmp->{'TotSale'}).qq|</td>
									 </tr>\n|;
		}
	}else{
		$rec{'productslist'} =  qq|
															<tr>
																<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
															</tr>\n|;
	}
	$rec{'productslist'} .= "</table>";

	print "Content-type: text/html\n\n";
	foreach $key (keys %rec){
		$rec{$key} =~ s/\|//g;
		print "$key|".$rec{$key}."|";
	}
}

sub check_address {
# --------------------------------------------------------
	my ($sth,$rec);
	print "Content-type: text/html\n\n";

	if ($in{'address1'}){
		$in{'zip'} = "0$in{'zip'}" if length($in{'zip'}) == 4;
		$rec->{'Address1'} = $in{'address1'};
		$rec->{'Address2'} = $in{'address2'};
		$rec->{'Address3'} = $in{'address3'};
		$rec->{'City'} = $in{'city'};
		$rec->{'Urbanization'} = $in{'urbanization'};
		$rec->{'Zip'} = $in{'zip'};
		$rec->{'shp_Address1'} = $in{'address1'};
		$rec->{'shp_Address2'} = $in{'address2'};
		$rec->{'shp_Address3'} = $in{'address3'};
		$rec->{'shp_City'} = $in{'city'};
		$rec->{'shp_Urbanization'} = $in{'urbanization'};
		$rec->{'shp_Zip'} = $in{'zip'};		
	}else{
		$sth = &Do_SQL("SELECT * FROM sl_orders WHERE ID_orders='$in{'id_orders'}';");
		$rec = $sth->fetchrow_hashref;
		$rec->{'Zip'} = "0$rec->{'Zip'}" if length($rec->{'Zip'}) == 4;
		$rec->{'shp_Zip'} = "0$rec->{'shp_Zip'}" if length($rec->{'shp_Zip'}) == 4;
	}

	##################################
	# Create a request (BILLING INFO)
	##################################
	use LWP::UserAgent;
	use HTTP::Request::Common;
	$ua=new LWP::UserAgent;		
	#my $req = HTTP::Request->new(GET => "http://zip4.usps.com/zip4/zcl_0_results.jsp?visited=1&pagenumber=0&firmname=0&address2=$rec->{'Address1'}&address1=$rec->{'Address2'}&city=$rec->{'City'}&urbanization=$rec->{'Urbanization'}&zip5=$rec->{'Zip'}&city=>$rec->{'City'}&state=");
	my $req = HTTP::Request->new(GET => "https://tools.usps.com/go/ZipLookupResultsAction!input.action?resultMode=0&companyName=&address1=$rec->{'Address1'}&address2=$rec->{'Address2'}&city=$rec->{'City'}&state=&urbanCode=&postalCode=&zip=$rec->{'Zip'}");
	# Pass request to the user agent and get a response back
	$resp = $ua->request($req);
	if ($resp->is_success){
		my (@lines,$error,$prt);
		@lines = split(/\n/,$resp->content);
		for (0..$#lines){
			($prt) and ($output .= $lines[$_]);
			#if ($lines[$_] =~ /headers="non"/){
			if($lines[$_] =~ /div id="error-box"/){
				$error = 1;
				$prt = 1;
			}elsif ($prt and $lines[$_] =~ /<span class="city range">/){
				$prt = 0;
			#}elsif ($lines[$_] =~ /headers="full"/){
			}elsif ($lines[$_] =~ /<div class="data">/){
				$ok = 1;
				$prt = 1;
			}	
		}


		if ($ok){
			print qq|<table border="0" cellspacing="0" cellpadding="2" width="380" bgcolor="#DEFFCA">
			<tr>
				<td><b>The Correct Billing Address is:</b></td>
			</tr>
			<tr>
				<td>$output</td>
			</tr>
			</table>\n|;
		}else{
			print qq|<table border="0" cellspacing="0" cellpadding="2" width="380" bgcolor="#FFCFCE">
			<tr>
				<td><b>ERROR: Unable to find the Billing Address</b></td>
			</tr>
			<tr>
				<td>$rec->{'Address1'} $rec->{'Address2'} $rec->{'Address3'} $rec->{'Urbanization'}<br>$rec->{'City'}, $rec->{'Zip'}</td>
			</tr>
			</table>\n|;
		}
		#return ($resp->content);
	}else{
		print "Error: " . $resp->status_line . "\n<BR>";
	}
	
	##################################
	# Create a request (BILLING INFO)
	##################################
	$output = '';
	$ok = '';
	my $req = HTTP::Request->new(GET => "http://zip4.usps.com/zip4/zcl_0_results.jsp?visited=1&pagenumber=0&firmname=0&address2=$rec->{'shp_Address1'}&address1=$rec->{'shp_Address2'}&city=$rec->{'shp_City'}&urbanization=$rec->{'shp_Urbanization'}&zip5=$rec->{'shp_Zip'}&city=>$rec->{'shp_City'}&state=");
	my $req = HTTP::Request->new(GET => "https://tools.usps.com/go/ZipLookupResultsAction!input.action?resultMode=0&companyName=&address1=$rec->{'shp_Address1'}&address2=$rec->{'shp_Address2'}&city=$rec->{'shp_City'}&state=&urbanCode=&postalCode=&zip=$rec->{'shp_Zip'}");
	
	# Pass request to the user agent and get a response back
	$resp = $ua->request($req);
	print "&nbsp;";
	if ($resp->is_success){
		my (@lines,$error,$prt);
		@lines = split(/\n/,$resp->content);
		for (0..$#lines){
			($prt) and ($output .= $lines[$_]);
			#if ($lines[$_] =~ /headers="non"/){
			if($lines[$_] =~ /div id="error-box"/){
				$error = 1;
				$prt = 1;
			}elsif ($prt and $lines[$_] =~ /<span class="city range">/){
				$prt = 0;
			#}elsif ($lines[$_] =~ /headers="full"/){
			}elsif ($lines[$_] =~ /<div class="data">/){
				$ok = 1;
				$prt = 1;
			}
		}
		if ($ok){
			print qq|<table border="0" cellspacing="0" cellpadding="2" width="380" bgcolor="#DEFFCA">
							<tr>
								<td><b>The Correct Shipping Address is:</b></td>
							</tr>
							<tr>
								<td>$output</td>
							</tr>
							</table>\n|;
		}else{
				print qq|<table border="0" cellspacing="0" cellpadding="2" width="380" bgcolor="#FFCFCE">
				<tr>
					<td><b>ERROR: Unable to find the Billing Address</b></td>
				</tr>
				<tr>
					<td>$rec->{'shp_Address1'} $rec->{'shp_Address2'} $rec->{'shp_Address3'} $rec->{'shp_Urbanization'}<br>$rec->{'shp_City'}, $rec->{'shp_Zip'}</td>
				</tr>
				</table>\n|;
		}
		
		print qq|<table border="0" cellspacing="0" cellpadding="2" width="380" bgcolor="#FFCFCE">
				<tr>
					<td><b>NOTE / NOTA</b></td>
				</tr>
				<tr>
					<td align="center" nowrap>If the Billing/Shipping Address is different you HAVE TO Change it</td>
				</tr>
				<tr>
					<td align="center" nowrap>Si la direccion de Envio/Cobro es diferente DEBE cambiarla</td>
				</tr>
				</table>\n|;
		#return ($resp->content);
	}else{
		print "Error: " . $resp->status_line . "\n<BR>";
	}
}

sub check_shipping_status {
# --------------------------------------------------------
# Last Modified on: 07/09/09 12:59:23
# Last Modified by: MCC C. Gabriel Varela S: Se integra paqueter?a IW
	my ($rec,$PortalProvider,$startSaving,$stopSaving);
	print "Content-type: text/html\n\n";

	if ($in{'provider'}){
		$rec->{'Provider'} = $in{'provider'};
		$rec->{'Tracking'} = $in{'tracking'};
	}
	
	if($rec->{'Provider'} eq 'UPS'){
		$PortalProvider = "http://m.ups.com/mobile/track?trackingNumber=$rec->{'Tracking'}&t=t";
		$ifframe = '1';
		#$PortalProvider = "http://www.ups.com/search/quick?loc=en_us&results=25&view=both&query=$rec->{'Tracking'}&sub=Search";
		#$startLooking = 'Scheduled Delivery Date logic';
		#$stopLooking  = 'End Module';
	}elsif($rec->{'Provider'} eq 'Fedex'){
		$PortalProvider = "http://www.fedex.com/Tracking/Detail?ftc_start_url=&totalPieceNum=&backTo=&template_type=print&cntry_code=us_espanol&language=espanol&trackNum=$rec->{'Tracking'}&pieceNum=&selectedTimeZone=localScanTime";
		$ifframe = '1';
		#$startLooking = '<HTML>';
		#$stopLooking  = '</HTML>';
		#$PortalProvider = "http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcom&cntry_code=us&language=english&tracknumbers=$rec->{'Tracking'}";
		#$startLooking = '<DIV id="content" CLASS="detailcolumn">';
		#$stopLooking  = '<div class="footerWrapper">';
	}elsif ($rec->{'Provider'} eq 'USPS'){						
		$PortalProvider = "https://tools.usps.com/go/TrackConfirmAction.action?tLabels=$rec->{'Tracking'}&FindTrackLabelorReceiptNumber=Find";								
		$ifframe = '1';
		#$startLooking = 'Label/Receipt Number:';
		#$stopLooking  = 'table summary';
	}elsif ($rec->{'Provider'} eq 'DHL Ground'){						
		$PortalProvider = "http://wap.dhl.com/cgi-bin/tracking.pl?TID=CP_ENG&FIRST_DB=AP&AWB=$rec->{'Tracking'}";								
	}elsif ($rec->{'Provider'} eq 'IW'){						
		$PortalProvider = "http://www.islandwide.com/TrackResult.asp?num=$rec->{'Tracking'}";								
		$startLooking = '<td width="878" valign="top"><table width="100%" border="0" cellpadding="0" cellspacing="0">';
		$stopLooking  = '<form method=';
	}

	##################################
	# Create a request (SHIPPING STATUS)
	##################################
	if ($ifframe){
		print qq|
		<iframe src ="$PortalProvider" width="500" height="300">
		  <p>Your browser does not support iframes.</p>
		</iframe>\n|;
	}else{
		use LWP::UserAgent;
		use HTTP::Request::Common;
		$ua=new LWP::UserAgent;		
		my $req = HTTP::Request->new(GET => "$PortalProvider");
	
		# Pass request to the user agent and get a response back
		$resp = $ua->request($req);
		if ($resp->is_success){
			my (@lines,$flag,$ok,$output);
			$ok=0;
			@lines = split(/\n/,$resp->content);
			for (0..$#lines){
				########## Getting Tracking Information ############################	
				if($lines[$_] =~ /$startLooking/ or $flag > 0){
					$output .= $lines[$_];
					$flag=1;
					$ok++;
				}
				########## Stop Data Saving ################################
				if($lines[$_] =~ /$stopLooking/ and $ok > 1){
					$flag=0;
					break;
				}
			}
			
			$output =~ s/<input type="image".*?>//g;	
				
			if ($ok > 0){
				print qq|<table border="0" cellspacing="0" cellpadding="2" width="400">
				<tr>
					<td><b>Shipment Info $rec->{'Provider'}</b></td>
				</tr>
				<tr>
					<td>$output</td>
				</tr>
				</table>\n|;
			}else{
				print qq|<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
				<tr>
					<td><b>Shipping Info $rec->{'Provider'}</b></td>
				</tr>
				<tr>
					<td>$rec->{'Provider'}<br>$rec->{'Tracking'}<br>$output</td>
				</tr>
				</table>\n|;
			}
			#return ($resp->content);
		}else{
			print "Error: " . $resp->status_line . "\n<BR>";
		}
	}
}

sub prod_typermas {
# --------------------------------------------------------  

	my ($sth) = &Do_SQL("SELECT * FROM sl_rmas WHERE id_orders_products ='$in{'id_orders_products'}' AND id_customers = '$in{'id_customers'}';");
	print "Content-type: text/html\n\n";
	print qq|<table border="0" cellspacing="0" cellpadding="4" width="350" class="formtable">
					<tr>
					  <td class="menu_bar_title" align="center">Id Type</td>
						<td class="menu_bar_title" align="center">Type (rma/rfa/rsa)</td>
						<td class="menu_bar_title" align="center">Type</td>
						<td class="menu_bar_title" align="center">Ret Reason</td>
						<td class="menu_bar_title" align="center">Date</td>
					</tr>|;
	while ($rec = $sth->fetchrow_hashref){
		print qq|	<tr>
							<td class="smalltext" align="right" valign="top" nowrap>$rec->{'ID_rmas'}   </td>
							<td class="smalltext" align="right" valign="top" nowrap>$rec->{'Type_Rmas'} </td>
							<td class="smalltext" align="right" valign="top" nowrap>$rec->{'Type'}   </td>
							<td class="smalltext" align="right" valign="top" nowrap>$rec->{'Ret_Reason'}   </td>
							<td class="smalltext" align="right" valign="top" nowrap>$rec->{'Date'}   </td>
						</tr>|;
	}
	print "</table> ";
	return;	
}





sub order_tocancelled {
# --------------------------------------------------------
	## To Cancelled
	## status=Cancelled
	## Add Note : Order	Cancelled Date
	
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Cancelled' WHERE ID_orders='$in{'id_orders'}';");	
	&add_order_notes_by_type($in{'id_orders'},"Order	Cancelled","High");
	&auth_logging('opr_orders_stCancelled',$in{'id_orders'});
	&status_logging($in{'id_orders'},'Cancelled');
		
	print "Content-type: text/html\n\n";
	print qq|
					<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
					<tr>
						<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Cancelled</b><p>&nbsp;</p></td>
					</tr>
					</table> |;
}

sub order_topending {
# --------------------------------------------------------
	## To Pending
	## status=Pending
	## Add Note : Check Order
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Pending' WHERE ID_orders='$in{'id_orders'}';");	
	&add_order_notes_by_type($in{'id_orders'},"Check Order","Medium");
	&auth_logging('opr_orders_stPending',$in{'id_orders'});
	&status_logging($in{'id_orders'},'Pending');

	print "Content-type: text/html\n\n";
	print qq|
					<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
					<tr>
						<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Pending</b><p>&nbsp;</p></td>
					</tr>
					</table>	|;
}


sub updateshp {
# --------------------------------------------------------
	## To Pending
	## status=Pending
	## Add Note : Check Order
	# Last Modification by JRG : 03/13/2009 : Se agrega log
	my ($sth) = &Do_SQL("UPDATE sl_orders_products SET Tracking='$in{'trknum'}',ShpProvider='$in{'shpprovider'}',ShpDate='$in{'shpdate'}' WHERE ID_orders_products='$in{'id_orders_products'}';");
	&auth_logging('orders_products_updated',$in{'id_orders'});
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Shipped' WHERE ID_orders='$in{'id_orders'}';");
	&auth_logging('opr_orders_stShipped',$in{'id_orders'});
	&status_logging($in{'id_orders'},'Shipped');

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_import_log WHERE ID_import_log='$in{'trknum'}';");
	if ($sth->fetchrow == 0){
		my ($sth) = &Do_SQL("INSERT INTO sl_import_log SET ID_import_log='$in{'trknum'}',Type='$in{'shpprovider'}',ID_orders='$in{'id_orders'}',ID_orders_products='$in{'id_orders_products'}',IData='---',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
	}
	
	#my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$in{'id_orders'}',Notes='Check Order',Type='Medium',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
	#&auth_logging('opr_orders_to_pend',$in{'id_orders'});


	#id_orders_products=$col->{'ID_orders_products'}&shpdate=$rec{'shpdate'}&trknum
	#shpprovider

	print "Content-type: text/html\n\n";
	print qq|
					<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#B7FFB7">
					<tr>
						<td align="center"><p>&nbsp;</p><b>Item Set to Shipped : $in{'shpdate'}</b>
			
						<p>&nbsp;</p></td>
					</tr>
					</table>	|;
	#$in{'id_orders_products'}<br>
	#$in{'shpdate'}<br>
	#$in{'trknum'}<br>
	#$in{'shpprovider'}
	
}


sub order_topostdated {
# --------------------------------------------------------
	## To Postdated
	## status=Postdated
	## Add Note : Order Post Dated
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Pending',StatusPay='Post-Dated' WHERE ID_orders='$in{'id_orders'}';");	
	&add_order_notes_by_type($in{'id_orders'},"Order Post Dated","Medium");
	&auth_logging('opr_orders_to_pd',$in{'id_orders'});
	&auth_logging('opr_orders_stPending',$in{'id_orders'});
	&status_logging($in{'id_orders'},'Pending');

	print "Content-type: text/html\n\n";
	print qq|
					<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
					<tr>
						<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Post Dated</b><p>&nbsp;</p></td>
					</tr>
					</table> |;
}


sub order_toreview_address {
# --------------------------------------------------------
	## To Review address
	## status=Review
	## Add Note : Review Address
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Pending',StatusPay='Review Address' WHERE ID_orders='$in{'id_orders'}';");	
	&add_order_notes_by_type($in{'id_orders'},"Review Address","Medium");
	&auth_logging('opr_orders_to_radrs',$in{'id_orders'});
	&auth_logging('opr_orders_stPending',$in{'id_orders'});
	&status_logging($in{'id_orders'},'Pending');
	
	print "Content-type: text/html\n\n";
	print qq|
					<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
					<tr>
						<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Review Address</b><p>&nbsp;</p></td>
					</tr>
					</table>	|;
}

sub showscript {
# --------------------------------------------------------
# Last Modified on: 07/14/08 11:32:53a 
# Last Modified by: MCC C. Gabriel Varela S: Se cambia load_paguitos por load_script_variables
# Last Modified on: 08/13/08 12:20:53p
# Last Modified by: MCC C. Gabriel Varela S: Se adec?a la funci?n para cargar script de promoci?n mail-in rebate
# Last Modified on: 09/03/08 19:13:41
# Last Modified by: MCC C. Gabriel Varela S: Nueva promoci?n
# Last Modified on: 09/04/08 11:24:14
# Last Modified by: MCC C. Gabriel Varela S: Se hace que siempre apliquen los nuevos speeches
	if($in{'name'}eq"script" or $in{'name'}eq"scriptobj1" or $in{'name'}eq"scriptobj3" or $in{'name'}eq"scriptobj4" or $in{'name'}eq"scriptobj5" or $in{'name'}eq"scriptobj6" or $in{'name'}eq"scriptobj7"){
		if($cfg{'lastpromo'}){
			if ($in{'id_products'}=~ /$cfg{'lastpromoprods'}/ or 1){
				$in{'name'}.="lastp";
			}
		}elsif($cfg{'mailinrebatepromo'}){
			if ($in{'id_products'}=~ /$cfg{'discmailinrebate'}/ or 1){
				$in{'name'}.="mailinrebate";
			}
		}
		&load_script_variables($in{'id_products'});
	}

	print "Content-type: text/html\n\n";
	my ($fname) = $cfg{'path_templates'}."/mod/".$usr{'application'}."/".$in{'name'} .".html";
	$fname =~ s/\[lang\]/$usr{'pref_language'}/gi;
	if(-e $fname){
		print &build_page("$in{'name'}.html");	
	}else{
		print &load_name('sl_speech','Type',$in{'name'},'Speech') ."</p><p align='right' class='smalltxt'>$va{'speechname'}</p>";
	}
}




sub add_return {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' and Status='Active' and ID_products like '1%';");
	print qq|
		<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
			<tr>
	 			<td class="menu_bar_title" align="center">ID_orders</td>
	 			<td class="menu_bar_title" align="center">Description</td>
	 			<td class="menu_bar_title" align="center">Price</td>
	 		</tr>\n|;
	while ($rec = $sth->fetchrow_hashref){
		$d = 1 - $d;
		print qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=orders&view=$rec->{'ID_orders'}&addreturn=$rec->{'ID_orders_products'}&reason=$in{'reason'}')">
				<td class="smalltext" valign="top" nowrap>|.&format_sltvid($rec->{'ID_products'}).qq|</a></td>
				<td class="smalltext">|.&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Model]<br>[Name]').qq|</td>
				<td class="smalltext" align="right" valign="top" nowrap>|.&format_price($rec->{'SalePrice'}).qq|</td>
			</tr>\n|;		
	}
	print qq|
			<tr>
				<td class="smalltext" colspan="6"></td>
			</tr>
		</table>
		\n|;
}

sub html_record_form {
# --------------------------------------------------------
	my (%rec) = @_;		# Load any defaults to put in the VALUE field.
	my ($page);
    for my $i(0.. $#headerfields){
		
		$field = lc($headerfields[$i]);
		$page .= qq|\n			<tr>\n			  <td>&nbsp;</td>\n			  <td valign="top" nowrap>$titlefields[$i] : </td>\n|;
		if ($db_valid_types{$field} eq 'selection'){
			$page .= qq|		<td class="smalltext">| . &build_select_field ('ajax'.$field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'radio') {
			$page .= qq| 		<td class="smalltext">| . &build_radio_field('ajax'.$field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'checkbox' ) {
			$page .= qq| 		<td class="smalltext">| . &build_checkbox_field ('ajax'.$field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'date') {
			$page .=  qq|<td><input type="text" id="ajax$field" NAME="ajax$field" VALUE="$rec{$field}" SIZE="25" onFocus='focusOn( this )' onBlur='focusOff( this )'>
									yyyy/mm/dd</td>|;
		}else{
			$page .= qq| 	<td><input type=text  NAME="ajax$field" VALUE="$rec{$field}" SIZE="25" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		}
		$page .= "			</tr>\n";
	}
	return $page;
}

sub html_record_form_hidden_fields {
# --------------------------------------------------------
	my (%rec) = @_;		# Load any defaults to put in the VALUE field.
	my ($page);
    for my $i(0.. $#headerfields){
		
		$field = lc($headerfields[$i]);
		$page .= qq|\n			<tr>\n			  <td>&nbsp;</td>\n			  <td valign="top" nowrap>$titlefields[$i] : </td>\n|;
		if ($db_valid_types{$field} eq 'selection'){
			$page .= qq|		<td class="smalltext">| . &build_select_field ('ajax'.$field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'radio') {
			$page .= qq| 		<td class="smalltext">| . &build_radio_field('ajax'.$field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'checkbox' ) {
			$page .= qq| 		<td class="smalltext">| . &build_checkbox_field ('ajax'.$field, $rec{$field}) . qq|</td>\n|;
		}elsif ($db_valid_types{$field} eq 'date') {
			$page .=  qq|<td><input type="text" id="ajax$field" NAME="ajax$field" VALUE="$rec{$field}" SIZE="25" onFocus='focusOn( this )' onBlur='focusOff( this )'>
									yyyy/mm/dd</td>|;
		}else{
			$page .= qq| 	<td><input type=text  NAME="ajax$field" VALUE="$rec{$field}" SIZE="25" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>\n|;
		}
		$page .= "			</tr>\n";
	}
	for my $j(0.. $#remfields) {
		my $hidden_field = lc($remfields[$j]);
		$page .= qq| 	<input type="hidden"  name="ajax$hidden_field" value="$rec{$hidden_field}" size="25" onFocus='focusOn( this )' onBlur='focusOff( this )' />\n|;
	}
	if ($#remfields > 1) {
		$page .= qq|<input type="hidden" name="partial_update" value="1" />|;
	}
	
	return $page;
}

sub show_risk_orders {
# --------------------------------------------------------
	if(!$in{'noajax'}){
		print "Content-type: text/html\n\n";
	}

	my ($rmsg) = &check_rman($in{'id_orders'});
	$rmsg =~ s/   /<br>/g;
	print qq|<div id="risk_order">|;
	print qq|<table border="0" cellspacing="0" cellpadding="5" width="100%" style="border:1px solid black;font-family: arial;font-size:12px;margin-bottom:8px;">
				<tr>
					<td align="center" colspan="2" bgcolor="#222222"><font color="#ffffff" size="3" face="century gothic, verdana">Order Analysis</td>
				</tr>
				<tr>
					<td class="smalltext">Totals</td>
					<td class="smalltext">|.&check_ord_totals($in{'id_orders'}).qq|</td>
				</tr>
				<tr>
					<td class="smalltext" nowrap valign="top">Risk management</td>
					<td class="smalltext">$rmsg</td>
				</tr>
			</table>|;
	
	########################################
	##### SAME CREDIT CARD NUMBER
	########################################		
	my ($sth2) = &Do_SQL("SELECT card_number FROM sl_orders_payments inner join sl_orders_cardsdata ON sl_orders_payments.id_orders_payments = sl_orders_cardsdata.id_orders_payments
	 WHERE sl_orders_payments.ID_orders='$in{'id_orders'}' AND Type='Credit-Card' AND Status='Approved' AND (AuthCode<>'0000' and AuthCode IS NOT NULL)");
	my ($cc) = $sth2->fetchrow();
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	print qq|	<table border="0" cellspacing="0" cellpadding="3" width="100%" style="border:1px solid black;font-family: arial;font-size:12px;margin-bottom:10px;">
				<tr>
					<td colspan='8' align="left"  bgcolor="#222222"><font color="#ffffff" size="2" face="verdana">Orders With The Same <b>Credit Card Number</b> Upto 15</td>
				</tr>
				<tr>
					<td align="center" bgcolor="#CEFFCE" nowrap>ID Order</td>
					<td align="center" bgcolor="#CEFFCE">Date</td>
					<td align="center" bgcolor="#CEFFCE">Name</td>
					<td align="center" bgcolor="#CEFFCE">Status</td>
					<td align="center" bgcolor="#CEFFCE">StatusPay</td>
					<td align="center" bgcolor="#CEFFCE">StatusPrd</td>
					<td align="center" bgcolor="#CEFFCE">OrderNet</td>
					<td align="center" bgcolor="#CEFFCE">Balance</td>
				</tr>\n|;
	my($count);
	if ($cc ne ''){
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date AS Date,sl_orders.Status AS Status,Ordernet,ID_customers,StatusPay,StatusPrd 
							FROM sl_orders, sl_orders_payments, sl_orders_cardsdata 
							WHERE sl_orders.ID_orders<>'$in{'id_orders'}' 
							AND sl_orders.ID_orders = sl_orders_payments.ID_orders 
							AND sl_orders_payments.id_orders_payments = sl_orders_cardsdata.id_orders_payments  
							AND card_number='$cc' 
							GROUP BY sl_orders.ID_orders LIMIT 0,15;");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
			$balance =  $sth2->fetchrow;
			$d = 1 - $d;
			print qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&tab=2')">
					<td class='smalltext' valign="top" nowrap>$rec->{'ID_orders'}</td>
					<td class='smalltext' valign="top" nowrap>$rec->{'Date'}</td>
					<td class='smalltext' valign="top">|.&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[FirstName] [LastName1]").qq|</td>
					<td class='smalltext' valign="top">$rec->{'Status'}</td>
					<td class='smalltext' valign="top">$rec->{'StatusPay'}</td>
					<td class='smalltext' valign="top">$rec->{'StatusPrd'}</td>
					<td class='smalltext' valign="top">|.&format_price($rec->{'Ordernet'}).qq|</td>
					<td class='smalltext' valign="top">|.&format_price($balance).qq|</td>
				</tr>\n|;
			++$count;
		}
		if (!$count){
			print qq|
				<tr>
					<td colspan='8' align="center" class='smalltext'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "</table>";
	}

	########################################
	##### SAME SHIPPING ADDRESS
	########################################		
	print qq|	<table border="0" cellspacing="0" cellpadding="3" width="100%" style="border:1px solid black;font-family: arial;font-size:12px;margin-bottom:10px;">
				<tr>
					<td colspan='8' align="left"  bgcolor="#222222"><font color="#ffffff" size="2" face="verdana">Orders With The Same<b> Address</b> Upto 15</td>
				</tr>
				<tr>
					<td align="center" bgcolor="#CEFFCE">ID Order</td>
					<td align="center" bgcolor="#CEFFCE">Date</td>
					<td align="center" bgcolor="#CEFFCE">Name</td>
					<td align="center" bgcolor="#CEFFCE">Status</td>
					<td align="center" bgcolor="#CEFFCE">StatusPay</td>
					<td align="center" bgcolor="#CEFFCE">StatusPrd</td>
					<td align="center" bgcolor="#CEFFCE">OrderNet</td>
					<td align="center" bgcolor="#CEFFCE">Balance</td>
				</tr>\n|;
	my($count);
	my ($sth) = &Do_SQL("SELECT Address1,Zip,shp_Address1,shp_Zip FROM sl_orders WHERE ID_orders='$in{'id_orders'}';");
	my ($Address1,$Zip,$shp_Address1,$shp_Zip) = $sth->fetchrow_array();
	$Address1 = &filter_values($Address1);
	$shp_Address1 = &filter_values($shp_Address1);
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date AS Date,sl_orders.Status AS Status,Ordernet,ID_customers,StatusPay,StatusPrd FROM sl_orders USE INDEX ( Zip, shp_Zip ),sl_orders_payments WHERE ((Address1='$Address1' AND Zip='$Zip') OR (shp_Address1='$shp_Address1' AND shp_Zip='$shp_Zip')) AND sl_orders.ID_orders<>'$in{'id_orders'}' AND sl_orders.ID_orders=sl_orders_payments.ID_orders GROUP BY sl_orders.ID_orders LIMIT 0,15;");
	while ($rec = $sth->fetchrow_hashref){
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
		$balance =  $sth2->fetchrow;
		$d = 1 - $d;
		print qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&tab=2')">
				<td class='smalltext' valign="top" nowrap>$rec->{'ID_orders'}</td>
				<td class='smalltext' valign="top" nowrap>$rec->{'Date'}</td>
				<td class='smalltext' valign="top">|.&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[FirstName] [LastName1]").qq|</td>
				<td class='smalltext' valign="top">$rec->{'Status'}</td>
				<td class='smalltext' valign="top">$rec->{'StatusPay'}</td>
				<td class='smalltext' valign="top">$rec->{'StatusPrd'}</td>
				<td class='smalltext' valign="top">|.&format_price($rec->{'Ordernet'}).qq|</td>
				<td class='smalltext' valign="top">|.&format_price($balance).qq|</td>
			</tr>\n|;
		++$count;
	}


	########################################
	##### SAME PHONE NUMBER
	########################################		
	my ($sth)= &Do_SQL("SELECT Phone1,Phone2,Cellphone FROM sl_orders LEFT JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$in{'id_orders'}';");
	my ($rec) = $sth->fetchrow_hashref();
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	print qq|	<table border="0" cellspacing="0" cellpadding="3" width="100%" style="border:1px solid black;font-family: arial;font-size:12px;margin-bottom:10px;">
				<tr>
					<td colspan='8' align="left"  bgcolor="#222222"><font color="#ffffff" size="2" face="verdana">Orders With The Same <b>Phone Number</b> Upto 15</td>
				</tr>
				<tr>
					<td align="center" bgcolor="#CEFFCE" nowrap>ID Order</td>
					<td align="center" bgcolor="#CEFFCE">Date</td>
					<td align="center" bgcolor="#CEFFCE">Name</td>
					<td align="center" bgcolor="#CEFFCE">Status</td>
					<td align="center" bgcolor="#CEFFCE">StatusPay</td>
					<td align="center" bgcolor="#CEFFCE">StatusPrd</td>
					<td align="center" bgcolor="#CEFFCE">OrderNet</td>
					<td align="center" bgcolor="#CEFFCE">Balance</td>
				</tr>\n|;
	my($count);

	## Check Order / Phone
	my @aryp;
	($rec->{'Phone1'}) and ( push(@aryp, qq|Phone1 = '|. &filter_values($rec->{'Phone1'}) .qq|'|) );
	($rec->{'Phone2'}) and ( push(@aryp, qq|Phone2 = '|. &filter_values($rec->{'Phone2'}) .qq|'|) );
	($rec->{'CellPhone'}) and ( push(@aryp, qq|CellPhone = '|. &filter_values($rec->{'CellPhone'}) .qq|'|) );

	if(scalar @aryp) {

		push(@ary_qty_index, 'ID_customers');
		$str_qty_where .= " (". join(' OR ', @aryp) .") ";
		
		my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders,sl_orders.Date AS Date,sl_orders.Status AS Status,Ordernet,ID_customers,StatusPay,StatusPrd FROM sl_orders INNER JOIN sl_customers USING(ID_customers) INNER JOIN sl_orders_payments USING(ID_orders) WHERE sl_orders.ID_orders<>'$in{'id_orders'}' AND $str_qty_where GROUP BY sl_orders.ID_orders LIMIT 0,15;");
		while ($rec = $sth->fetchrow_hashref){
			my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND (AuthCode='' OR AuthCode IS NULL or AuthCode='0000') AND Status IN ('Approved','Denied')");
			$balance =  $sth2->fetchrow;
			$d = 1 - $d;
			print qq|
				<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="trjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}&tab=2')">
					<td class='smalltext' valign="top" nowrap>$rec->{'ID_orders'}</td>
					<td class='smalltext' valign="top" nowrap>$rec->{'Date'}</td>
					<td class='smalltext' valign="top">|.&load_db_names('sl_customers','ID_customers',$rec->{'ID_customers'},"[FirstName] [LastName1]").qq|</td>
					<td class='smalltext' valign="top">$rec->{'Status'}</td>
					<td class='smalltext' valign="top">$rec->{'StatusPay'}</td>
					<td class='smalltext' valign="top">$rec->{'StatusPrd'}</td>
					<td class='smalltext' valign="top">|.&format_price($rec->{'Ordernet'}).qq|</td>
					<td class='smalltext' valign="top">|.&format_price($balance).qq|</td>
				</tr>\n|;
			++$count;
		}
		if (!$count){
			print qq|
				<tr>
					<td colspan='8' align="center" class='smalltext'>|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		print "</table>";
	}


	if (!$count){
		print qq|
			<tr>
				<td colspan='8' align="center" class='smalltext'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "</table>";
	print qq|</div>|;
}

#GV Inicia
sub load_script_variables{
# --------------------------------------------------------
my ($idproducts)=@_;
#$idproducts=1;
#Acci?n: Creaci?n
#Comentarios:
# --------------------------------------------------------
# Forms Involved: 
# Created on: 28/may/2008 16:14PM GMT -0600
# Last Modified on:
# Last Modified by:
# Author: MCC C. Gabriel Varela S.
# Description :  Genera las variables para tomarse en cuenta por el archivo: Y:\domains\dev.direksys.com\cgi-bin\templates\en\app\cc-inbound\script.html
# Parameters : 

# Last Modified on: 07/14/08 11:31:37
# Last Modified by: MCC C. Gabriel Varela S: Se cambia el nombre de la funci?n de load_paguitos a load_script_variables
#  &converts_in_to_va();
#  &converts_cses_to_va();

# Last Modified on: 07/14/08 16:22:24
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a la funci?n load_variables que carga los valores para ser utilizados en los speeches


	&load_variables();
	my $sth=&Do_SQL("SELECT * FROM sl_products WHERE ID_products=$idproducts");
	my $rec=$sth->fetchrow_hashref();
	$va{'productname'}=$rec->{'Name'};
	$va{'months'}=$rec->{'Flexipago'};
	$va{'weeks'}=$rec->{'Flexipago'}*4;
	$va{'price'} = $rec->{'SPrice'};
	
	
	if ($rec->{'FPPrice'}>0){
		$va{'discountporc'} = int($rec->{'SPrice'}/$rec->{'FPPrice'});
		$va{'discountvakue'} = &format_price($rec->{'FPPrice'}-$rec->{'SPrice'});
		$va{'onepayment'} = &format_price($rec->{'SPrice'});
		$va{'weeklyprice'}=&format_price($rec->{'FPPrice'}/$rec->{'Flexipago'}/4);
		$va{'monthlyprice'}=&format_price($rec->{'FPPrice'}/$rec->{'Flexipago'});
		$va{'sprice'}=&format_price($rec->{'FPPrice'});
		$va{'weekdownpayment'}=&format_price($rec->{'FPPrice'}/$rec->{'Flexipago'}/4+99+$va{'shipping'});
	}else{
		if ($idproducts =~ /$cfg{'disc40'}/){
			$va{'discountporc'}= 40;
			$va{'discountvakue'}=&format_price($rec->{'SPrice'}*40/100);
			$va{'onepayment'} = &format_price($rec->{'SPrice'}-$rec->{'SPrice'}*40/100);
		}elsif ($idproducts =~ /$cfg{'disc30'}/){
			$va{'discountporc'}= 30;
			$va{'discountvakue'}=&format_price($rec->{'SPrice'}*30/100);
			$va{'onepayment'} = &format_price($rec->{'SPrice'}-$rec->{'SPrice'}*30/100);
		}else{
			$va{'discountporc'}=$cfg{'fpdiscount'.$rec->{'Flexipago'}};
			$va{'discountvakue'}=&format_price($rec->{'SPrice'}*$cfg{'fpdiscount'.$rec->{'Flexipago'}}/100);
			$va{'onepayment'} = &format_price($rec->{'SPrice'}-$rec->{'SPrice'}*$cfg{'fpdiscount'.$rec->{'Flexipago'}}/100);
		}
		$va{'weeklyprice'}=&format_price($rec->{'SPrice'}/$rec->{'Flexipago'}/4);
		$va{'monthlyprice'}=&format_price($rec->{'SPrice'}/$rec->{'Flexipago'});
		$va{'sprice'}=&format_price($rec->{'SPrice'});
		$va{'weekdownpayment'}=&format_price($rec->{'SPrice'}/$rec->{'Flexipago'}/4+99+$va{'shipping'});
	}
	
	$va{'beweekly3'} = &format_price($rec->{'SPrice'} / 3);
	$va{'shipping'} = &load_regular_shipping($idproducts);
	$va{'shipping'} = &format_price($va{'shipping'});
	
	my $sth=&Do_SQL("SELECT DATE_ADD(CURDATE(), INTERVAL 2 WEEK)");
	$va{'secondpaybeweekly3'} = $sth->fetchrow;
	
	my $sth=&Do_SQL("SELECT DATE_ADD(CURDATE(), INTERVAL 1 MONTH)");
	$va{'tirdpaybeweekly3'} = $sth->fetchrow;
	
	$va{'firstpayment'} = &format_price($rec->{'SPrice'}/$rec->{'Flexipago'}+&load_regular_shipping($idproducts),2);
	
	return;
}

#GV Inicia 20jun2008
sub showpackinglist{
# --------------------------------------------------------
# Created on: 20/jun/2008 10:28AM GMT -0600
# Author: MCC C. Gabriel Varela S.
# Last Modified on: 07/21/08 @ 17:51:51
# Last Modified by: Carlos Haas
# Description : Mostrar? el packinglist al procesar un return cuando el return sea del tipo Exchange o Re Ship
# Parameters : 
#
# Last Modified on: 10/14/08  16:22:00
# Last Modified by: Roberto Barcenas
# Last Modified Desc: Change to template to show styles			   

	print "Content-type: text/html\n\n";
	print &build_page("packinglist_blankview.html");	
}
#GV Termina 20jun2008
#GV Termina

sub showparts{
# --------------------------------------------------------
# fORMS iNVOLVED: 
# cREATED ON: 24/JUN/2008 04:04 pm gmt -0600
# lAST mODIFIED ON: 07/11/2008
# lAST mODIFIED BY: MCC C Gabriel Varela S: Se agrega condici?n de id de return
# aUTHOR: mcc c. gABRIEL vARELA s.
# dESCRIPTION :  mOSTRAR? LA LISTA DE PARTES DE ACUERDO A LOS upcS INTRODUCIDOS Y ADEM?S LOS QUE FORMAN PARTE DE UN SET
# pARAMETERS : 
	#GV Inicia modificaci?n 24jun2008
	#GV Inicia modificaci?n 23jun2008
	$upcs=$in{'upcs'};
	my($sth1)=&Do_SQL("SELECT sl_skus.UPC, IF( ISNULL( sl_products.ID_products ) , sl_parts.Model, sl_products.Model ) AS Model, IF( ISNULL( sl_products.ID_products ) , sl_parts.Name, sl_products.Name ) AS Name, IF( ISNULL( ID_returns_upcs ) , 'NO', 'YES' ) AS StatusP
											FROM sl_skus
											LEFT JOIN sl_returns_upcs ON ( sl_skus.UPC = sl_returns_upcs.UPC and ID_returns=$in{'id_returns'}) 
											LEFT JOIN sl_parts ON ( id_products = id_parts ) 
											LEFT JOIN sl_products ON ( sl_skus.id_products = sl_products.id_products )
											WHERE sl_skus.UPC in(-1$upcs)");
											#GV Termina modificaci?n 23jun2008
	my (@c) = split(/,/,$cfg{'srcolors'});
	while($rec1=$sth1->fetchrow_hashref())
	{
		$d = 1 - $d;
		$va{'ret'}.="	<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>
							<td class='smalltext'>$rec1->{'UPC'}</td>
							<td class='smalltext'>$rec1->{'Model'}/$rec1->{'Name'}</td>
							<td class='smalltext'>$rec1->{'StatusP'}</td>
						</tr>";
	}
	#GV Termina modificaci?n 24jun2008
	print "Content-type: text/html\n\n";
	print &build_page("/forms/list_parts.html");	
}



sub check_avs {
# --------------------------------------------------------
# Created on: 01/08/09 @ 13:39:28
# Author: Carlos Haas
# Last Modified on: 01/08/09 @ 13:39:28
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#	
	require "cybersubs.cgi";
	print "Content-type: text/html\n\n";
	
	 
	## looking for ID_orders_payments
	my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE Type='Credit-Card' AND  AuthCode IS NOT NULL AND ID_orders='$in{'id_orders'}' AND Status IN ('Approved','Financed') LIMIT 1;");
	$in{'id_orders_payments'}=$sth->fetchrow;
	
	if (!$in{'id_orders_payments'}){
		my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE Type='Credit-Card' AND ID_orders='$in{'id_orders'}' ORDER BY ID_orders_payments DESC LIMIT 1;");
		$in{'id_orders_payments'}=$sth->fetchrow;
	}
	#print "$in{'id_orders'} $in{'id_orders_payments'}<BR>SELECT ID_orders_payments FROM sl_orders_payments WHERE Status IN ('Approved','Financed') AND ID_orders='$in{'id_orders'}' ORDER BY ID_orders_payments DESC LIMIT 1;";
	
	&checkavs;
}


sub show_products_speech{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 8/7/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($output);
	if($in{'id_speech'}){
		my ($sth) = &Do_SQL("SELECT Speech FROM sl_speech WHERE Type = 'Product Script' AND STATUS = 'Active' AND ID_speech='$in{'id_speech'}'");
		$output = $sth->fetchrow;
	}
	if(!$output){
		$output = "<div class='smalltext'>".&trans_txt('search_nomatches')."</div>";
	}
	print "Content-type: text/html\n\n";
	print $output;
}



sub fast_back_inventory{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	$va{'whs'} = "<option value='-99' selected>--</option>".&build_select_notdropshippers_warehouses."</select>";
	print "Content-type: text/html\n\n";
	print &build_page("fastbacktoinventory.html");
}

sub manage_lists{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 02/19/09 13:30:57
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#	my $user,$order,$type;
#	$user=$usr{'id_admin_users'};
#	$type=$in{'db'};
#	$order=$type;
#	$order=~s/sl_/id_/g;
#	$order=$in{$order};
#	$in{'user'}=$user;
#	$in{'id'}=$order;
#	$in{'table'}=$type;
# Last Modified on: 02/25/09 11:42:03
# Last Modified by: MCC C. Gabriel Varela S: Permite agregar cuando se seleccionan Lista, Usuario y Grupo
# Last Modified on: 02/26/09 11:31:51
# Last Modified by: MCC C. Gabriel Varela S: Se incluye columna application al mostrar los usuarios y se aplica orden.
# Last Modified on: 03/12/09 12:51:42
# Last Modified by: MCC C. Gabriel Varela S: Se pone condici?n de existencia de id
# Last Modification by JRG : 03/13/2009 : Se agrega log
# Last Modified on: 03/19/09 10:48:44
# Last Modified by: MCC C. Gabriel Varela S: Se arregla que guarde por grupo con el comando correcto.
# Last Modified RB: 05/11/09  17:53:29 -- $cmdn para tomar el comando sin _
# Last Modified RB: 05/20/09  15:43:18 -- userGroup < 3 pueden eliminar.
# Last Modified on: 06/03/09 10:10:07
# Last Modified by: MCC C. Gabriel Varela S: Se corrige para tomar el comando de verdad.
# Last Modified on: 06/08/09 10:59:09
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a write_to_list
# Last Modified on: 09/16/09 11:11:54
# Last Modified by: MCC C. Gabriel Varela S: Se adapta cookie para multi compa??a
	#&cgierr("Mesa$usr{'id_admin_users'}")if($in{'user'});
	if($in{'id'})
	{
		$va{'script_url'}= $cfg{'pathcgi_lists'};
		if($in{'dropli'})
		{
			&Do_SQL("Update sl_lists set Status='Inactive' where ID_lists=$in{'dropli'}");
			&auth_logging('list_updated',$in{'dropli'});
		}
		if($in{'action'})
		{
			if($in{'list'} ne "")
			{
				&write_to_list($in{'list'},$in{'cmdo'},$in{'user'},$in{'group'},$in{'id'},$in{'table'});
			}
		}
		if($in{'bookmark'})
		{
			&set_favorites("$in{'table'}$in{'e'}$in{'color'}",$in{'id'});
		}
		#$sth=&Do_SQL("Select ID_lists,Name,ID_users,application,if(ID_users=$usr{'id_admin_users'} or ID_admin_users=$usr{'id_admin_users'},1,0)as Deletable from sl_lists where tbl_name='$in{'table'}' and ID_table=$in{'id'} and Status='Active'");
		$sth=&Do_SQL("Select ID_lists,Name,ID_users,application,
					if(ID_users=$usr{'id_admin_users'} or sl_lists.ID_admin_users=$usr{'id_admin_users'} OR 
					0 < (SELECT ID_admin_users FROM admin_users						
				WHERE ID_admin_users =$usr{'id_admin_users'} ),1,0)as Deletable,concat(LastName,',',FirstName)as UserName
				FROM sl_lists 
				INNER JOIN admin_users ON (sl_lists.ID_users=admin_users.ID_admin_users)
				WHERE tbl_name='$in{'table'}' 
				  AND ID_table=$in{'id'} 
				  AND sl_lists.Status='Active'
				ORDER BY application,UserName");
		#0 < (SELECT IF( userGroup <3, 1, 0 ) FROM admin_users
		if($sth->rows>0)
		{
			while($rec=$sth->fetchrow_hashref)
			{
				$caddrop="";
				$caddrop= qq| <a href="$va{'script_url'}?cmd=manage_lists&ajaxbuild=manage_lists&id=$in{'id'}&table=$in{'table'}&path=$in{'path'}&dropli=$rec->{'ID_lists'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>| if($rec->{'Deletable'});
				$va{'searchresults'}.="<tr>
									<td style='font-size:7pt' valign='top'>$caddrop</td>
									<td style='font-size:7pt' valign='top'>$rec->{'Name'}</td>
									<td style='font-size:7pt' valign='top'>$rec->{'UserName'}</td>
									<td style='font-size:7pt' valign='top'>".&load_name('admin_users','ID_admin_users',$rec->{'ID_users'},'application')."</td>
								</tr>";
			}
		}
		else
		{
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='2' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;
		}
		&get_favorites("$in{'table'}$in{'e'}",$in{'id'});
		print "Content-type: text/html\n\n";
		print &build_page('lists.html')."<SCRIPT language='JavaScript'>

			function setCookie(c_name,valuet,expiredays,color){
				var exdate=new Date();
				var prevcont;
				prevcont=getCookie(c_name);
				var RegularExpression  =  new RegExp(valuet);
				var RegularExpression1  =  new RegExp('('+valuet+'\,?)','ig');
				if(prevcont.match(RegularExpression)){
					prevcont=prevcont.replace(RegularExpression1,'');
					movepic('bookmark'+color,'$va{'imgurl'}/app_bar/small_bookmarks'+color+'off.gif');
				}else{
					prevcont+=valuet+',';
					movepic('bookmark'+color,'$va{'imgurl'}/app_bar/small_bookmarks'+color+'on.gif');
				}
				exdate.setDate(exdate.getDate()+expiredays);
				document.cookie=c_name+ '=' +prevcont+
				((expiredays==null) ? '' : ';expires='+exdate.toGMTString())+';path=/;';
			}
			function getCookie(c_name){
				if (document.cookie.length>0){
					c_start=document.cookie.indexOf(c_name + '=');
					if (c_start!=-1){ 
						c_start=c_start + c_name.length+1; 
						c_end=document.cookie.indexOf(';',c_start);
						if (c_end==-1) c_end=document.cookie.length;
						return unescape(document.cookie.substring(c_start,c_end));
					} 
				}
				return '';
			}
			<!-- This script and many more are available free online at -->
			<!-- The JavaScript Source!! http://javascript.internet.com -->
			
			<!-- Begin
				function movepic(img_name,img_src) {
					document[img_name].src=img_src;
				}
			// End -->
			</SCRIPT>";
	}
}





sub build_chartinfo{
#-----------------------------------------
# Created on: 06/24/09  16:57:54 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
	
	my ($cmd,$chart_type,$dfields) = @_;
	$cmd = 'buildchart_'.$cmd;
	&$cmd($chart_type,$dfields);
}


sub check_xcallnote_view{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	
	my (@c) = split(/,/,$cfg{'srcolors'});	
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});	
	my ($sth) = &Do_SQL("SELECT ID_cdr_s7_notes,Notes,Type,cdr_s7_notes.Date,User FROM cdr_s7_notes WHERE src = '$in{'id_cdr'}' AND calldate = '$in{'calldate'}' ORDER BY Date,Time ;",1);
		while(my ($id,$notes,$type,$date,$user) = $sth->fetchrow()){
			$d = 1 - $d;
			$va{'searchresults'} .="<tr bgcolor='$c[$d]'>
																<td width='15%' nowrap>$date</td>
																<td width='25%'>$type</td>
																<td width='50%'>$notes</td>
																<td width='10%' nowrap>$user</td>
															</tr>";
		}
	&connect_db_w($cfg{'dbi_db'},$cfg{'dbi_host'},$cfg{'dbi_user'},$cfg{'dbi_pw'});
	
	print "Content-type: text/html\n\n";
	print &build_page("callnotes_view.html");
}


sub check_xcallnote_post{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	
	$va{'javascriptvar'}='';
	if($in{'btn_submit'} and $in{'note'} and $in{'type'} ne ''){
		my ($user) = &load_name('admin_users','ID_admin_users',$usr{'id_admin_users'},"CONCAT(FirstName,' ',LastName)");
		
		
		&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
		&Do_SQL("INSERT INTO cdr_s7_notes VALUES(0,'$in{'id_cdr'}','$in{'calldate'}',$in{'e'},'".&filter_values($in{'note'})."','$user','$in{'type'}',CURDATE(),CURTIME(),$usr{'id_admin_users'});",1);
		&connect_db_w($cfg{'dbi_db'},$cfg{'dbi_host'},$cfg{'dbi_user'},$cfg{'dbi_pw'});
		
		$va{'javascriptvar'}="<script type='text/javascript'>
	//<![CDATA[
		onload = function(){
			top.location.href='$in{'original_path'}?cmd=$in{'cmd'}&action=$in{'action'}&id_cdr=$in{'id_cdr'}&from_date=$in{'from_date'}&to_date=$in{'to_date'}&from_time=$in{'from_time'}&to_time=$in{'to_time'}&duration=$in{'duration'}&nh=$in{'nh'}';
		}
	//]]>
	</script>";
	}elsif($in{'btn_submit'} and $in{'note'}){
		$va{'message'} = "Debes Elegir una Calificaci&oacute;n para la Nota";
	}elsif($in{'btn_submit'}){
		$va{'message'} = "La nota no puede ser vac&iacute;a";
	}
	
	print "Content-type: text/html\n\n";
	print &build_page("callnotes_post.html");
}

sub capture_email{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/17/10 16:53:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 04/12/11 02:32:09 PM
# Last Modified by: MCC C. Gabriel Varela S: Se integra secret_cupon_applied
	print "Content-type: text/html\n\n";
	load_callsession();
	$in{'secret_cupon_applied'}=$cses{'secret_cupon_applied'};
	print &build_page("request_email.html");
}




sub add_assign{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/17/10 16:53:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :

	if ($in{'action'}){
		#validaciones
		if (!$in{'product_assign'} or !$in{'grupo_assign'} or !$in{'datefrom'} or !$in{'dateto'}){
			$va{'tabmessages'} = &trans_txt('reqfields');
		}else{
			$in{'id_dmas'}=~s/\|/,/gi;
			$va{'tabmessages'} = &trans_txt('mm_numbers_assignadded');
			my ($sth) = &Do_SQL("INSERT INTO sl_numbers_assign SET id_numbers='$in{'id_numbers'}',product_assign='$in{'product_assign'}',grupo_assign='$in{'grupo_assign'}',ID_categories='$in{'id_categories'}',channel_assign='$in{'channel_assign'}',datefrom='$in{'datefrom'}',dateto='$in{'dateto'}',id_dmas='$in{'id_dmas'}',Status_assign='New',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			delete($in{'product_assign'});
			delete($in{'grupo_assign'});
			delete($in{'datefrom'});
			delete($in{'dateto'});
			delete($in{'id_categories'});
			delete($in{'channel_assign'});
			delete($in{'id_dmas'});
			&auth_logging('mm_numbers_assignadded',$in{'id_numbers'});
			$va{'javascriptvar'}="<script type='text/javascript'>
	//<![CDATA[
		onload = function(){
			top.location.href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mm_numbers&view=$in{'id_numbers'}&tab=1#tabsl';
		}
	//]]>
	</script>";
		}
	}
	print "Content-type: text/html\n\n";
	print &build_page("numbers_tab1_add_assign.html");
}

sub change_cust_password{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 05/17/10 16:53:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last modified on 21 Dec 2010 13:19:58
# Last modified by: MCC C. Gabriel Varela S. :Se cambia crypt por sha1
# Last Time Modified by RB on 09/07/2011: Se actualiza el proceso para hacerlo igual que innovashop. Ahora solo se envia un link para que el cliente sea quien cambie su clave por una que pueda recordar mas facilmente en cualquiera de los 3 sitios de shoppingcart

	use Digest::Perl::MD5 'md5_hex';   ## Uso en Produccion
	##use Digest::MD5 'md5_hex';        ## Uso en Dev / Ya no es necesario
	
	my $sth=&Do_SQL("Select * from sl_customers where ID_customers=$in{'id_customers'}");
	$rec=$sth->fetchrow_hashref;
	$in{'email'}=$rec->{'Email'} if !$in{'email'};
	$va{'firstname'}=$rec->{'FirstName'};
	if ($in{'action'}){
		#validaciones
		$err=0;
		if($in{'email'}eq''){
			$error{'email'} = &trans_txt("required");
			++$err;
		}

		if($in{'action_change'}eq''){
			$error{'action_change'} = &trans_txt("required");
			++$err;
		}
		
		if($err>0){
			$va{'tabmessages'}='Some of the fields are invalid or missing. Fill them properly and try again.';
		}elsif($in{'action_change'}eq'Yes')		{
			## Actualizamos email
			&Do_SQL("UPDATE sl_customers SET Email='".&filter_values($in{'email'})."' WHERE ID_customers=$in{'id_customers'};");

			### Setting confirmation string in sl_vars
			$va{'string_confirmation'} = md5_hex(gen_passwd());
			$va{'urlconfirm_innovashop'}=$cfg{'urlconfirm_innovashop'};
			$va{'urlconfirm_naturaliv'}=$cfg{'urlconfirm_naturaliv'};
			$va{'urlconfirm_naturista'}=$cfg{'urlconfirm_naturista'};

			&Do_SQL("DELETE FROM sl_vars WHERE Vname='ishop_".$id_customers."_conf' OR Subcode = '$id_customers'; ");
			my $xconfirmation =&Do_SQL("INSERT INTO sl_vars SET VName='newpasswd_code', VValue='".$va{'string_confirmation'}."',Subcode='".$in{'id_customers'}."', Definition_En = 'Direksys Reset Customer Password' ");

		  
		  
			### Sending email & displaying the success creation
			$message_mail = &build_page('mypassword_email_confirmation.html');
			$va{'message_mail'} = $message_mail;
			$to = $in{'email'};
			$subject = trans_txt('mypassword_confirmation');

			$headers = 'From: <' . $cfg{'cservice_email'} . ">\r\n" .
			'Reply-To: ' . $cfg{'cservice_email'} . "\r\n";
			$sendmail=&send_text_mail($cfg{'cservice_email'},$in{'email'},$subject,$message_mail);
			if($sendmail eq 'ok'){
				$va{'tabmessages'}="<br><br>Email sent to customer. ";
			}else{
				$va{'tabmessages'}='<br><br>The confirmation email could not be sent. Error: '.$sendmail;
			}
	
			$va{'tabmessages'} .= "Links for password reseting<br>
							$va{'urlconfirm_innovashop'}$va{'string_confirmation'}-R<br>
							$va{'urlconfirm_naturaliv'}$va{'string_confirmation'}-R<br>
							$va{'urlconfirm_naturista'}$va{'string_confirmation'}-R" if ($usr{'usergroup'} <= 2);

			&Do_SQL("Insert into sl_customers_notes set ID_customers=$in{'id_customers'}, Notes='Password change required by user.',Type='Medium',Date=curdate(),Time=curtime(),ID_admin_users=$usr{'id_admin_users'}");
			$in{'db'}='sl_customers';
			&auth_logging('customer_chg_pass',$in{'id_customers'});
		}
		else
		{
			$va{'tabmessages'}='The password has not been changed because you chose NO';
		}
	}

  
	print "Content-type: text/html\n\n";
	print &build_page("change_cust_password.php");
}


sub inbound_price_plus_tax{	
# --------------------------------------------------------  
# Description: Imprime en Inbound una tabla con los precios del producto con taxes dependiendo del zipcode
# Last Modified RB: 01/12/11  21:15:44 -- Se cambia modo de muestra de tabla por un fancybox
# Last Modified RB: 01/18/11  19:00:44 -- Se agrega calculo de shipping y precio total en la tabla fancybox
# Last Modified RB: 03/16/11  19:40:44 -- Se agregan fechas probables de entrega para TDC y COD
# Last Modified RB: 03/21/11  10:15:00 -- Se corrige el calculo de las fechas.
# Last Modified by RB on 04/15/2011 12:37:37 PM : Se agrega cero(id_orders) como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:13:05 PM : Se agrega City como parametro para calculate_taxes
# Last Time Modified by RB on 03/06/2012: Se agrego calculo de comision maxima para operadores de inbound

	my ($prices,$pprice);
	print "Content-type: text/html\n\n";

	if($in{'e'} ne '1' and $in{'e'} ne '6' and $in{'e'} ne '8'){

		########
		######## Metodos de pago aceptados
		########					
		my ($sth) = &Do_SQL("SELECT ID_zones,Name,Payment_Type,ExpressShipping FROM sl_zones INNER JOIN sl_zipcodes USING(ID_zones) WHERE ZipCode = '$in{'zipcode'}';");
		my ($idz,$zn,$pt,$es) = $sth->fetchrow();

		$va{'paytype_accepted'} = '';
		$va{'zone_name'} = '';
		$va{'warehouses_zone'} = '';

		$esp = &load_name('sl_products','ID_products',$in{'id_products'},'ExpressShipping');
		$va{'express_allowed'} = ($cfg{'express_delivery'} and $esp eq 'Yes' and $es eq 'Yes') ? 'on' : 'off';

		if($pt ne ''){

			$va{'zone_name'} = $zn;
			my @ary = split(/,/, $pt);
			for(0..$#ary){

				if($_ == 0){
					$va{'paytype_accepted'} .= qq|<tr>\n|;
				}elsif($_ % 3 == 0){
					$va{'paytype_accepted'} .= qq|</tr>\n<tr>\n|;
				}

				$va{'paytype_accepted'} .= qq|<td style="height:60px;width:100px;background:#F39814;color:#FFFFFF;text-align:center;font-size:1.2em" align="center">$ary[$_]</td>|;

			}

			my $x = 0;
			my ($sth1) = &Do_SQL("SELECT Name FROM sl_warehouses INNER JOIN sl_zones_warehouses USING(ID_warehouses) WHERE ID_zones = '$idz';");
			while( my($wn) = $sth1->fetchrow()) {

				if($x == 0){
					$va{'warehouses_zone'} .= qq|<tr>\n|;
				}elsif($x % 3 == 0){
					$va{'warehouses_zone'} .= qq|</tr>\n<tr>\n|;
				}

				$va{'warehouses_zone'} .= qq|<td style="height:60px;width:100px;background:#F39814;color:#FFFFFF;text-align:center;font-size:1.2em" align="center">$wn</td>|;
				$x++;
			}
			(!$x) and (qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|);

		}else{
			$va{'paytype_accepted'} .= qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|;
			$va{'warehouses_zone'} .= qq|<td style="height:60px;width:300px;background:#F39814;color:#FFFFFF" align="center">|.&trans_txt('search_nomatches').qq|</td>|;
		}


		print build_page("console_show_prices_gross.html");
		return;
	}



	if ($in{'id_products'}>0  and length($in{'id_products'}) == 6 and $in{'zipcode'} and length($in{'zipcode'}) == 5){		

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products WHERE Status NOT IN('Testing','Inactive') AND ID_products='$in{'id_products'}'");
			if ($sth->fetchrow()>0){
					my ($sth) = &Do_SQL("SELECT * FROM sl_products WHERE Status NOT IN('Testing','Inactive') AND ID_products='$in{'id_products'}'");
					$rec = $sth->fetchrow_hashref();
					

					## Cities
					my $this_city; 
					my ($sth) = &Do_SQL("SELECT CONCAT(State,'-',StateFullName)AS State, case CityAliasName when CityAliasName is not null then CityAliasName else City end as City, PrimaryRecord FROM sl_zipcodes WHERE ZipCode='$in{'zipcode'}' ORDER BY State,City;");
					if($sth->rows() > 0){
						while(my($state, $city, $primary) = $sth->fetchrow()){
							$va{'cities'} .= '<tr><td align="left">'.$state.'</td><td align="left">'.$city.'</td></tr>';	
						}
						$this_city = $city if $primary eq 'P';
					}else{
						$va{'cities'} .= '<tr><td align="left">'.&trans_txt('search_nomatches').'</td></tr>';	
					}
					
				
					#my $state = &load_name('sl_zipcodes','ZipCode',$in{'zipcode'},'StateFullName');
					my $state = &load_db_names('sl_zipcodes','ZipCode',$in{'zipcode'},"[State]-[StateFullName]");
					my $taxes = &calculate_taxes($in{'zipcode'},$state,$this_city,0);
					
					$va{'taxes'} = $taxes*100;
					$va{'zipcode'} = $in{'zipcode'};
					
					## Fixed/Variable/Table Shipping ? 
					my $shpcal  = &load_name('sl_products','ID_products',$in{'id_products'},'shipping_table');
					my $shpmdis = &load_name('sl_products','ID_products',$in{'id_products'},'shipping_discount');				
					my $idpacking = &load_name('sl_products','ID_products',$in{'id_products'},'ID_packingopts');
					($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($cses{'edt'},$cses{'items_'.$i.'_size'},1,1,$cses{'items_'.$i.'_weight'},$idpacking,$shpcal,$shpmdis,$in{'id_products'});
					
					my $shp = $state=='PR-Puerto Rico' ? $shptotal1pr : $shptotal1;
							
					$pprice  = &format_price($rec->{'SPrice'}+($rec->{'SPrice'}*$taxes),2);
					$spricet = &format_number($rec->{'SPrice'},2);
					$tsprice = &format_price($rec->{'SPrice'} * $taxes,2);
		
					## Calculo de comision maxima
					my ($sth) = &Do_SQL("SELECT pbase_order,pbase_sale,tdc_C55*100/100,ticket_c200*100/100 FROM sl_rewards WHERE user_type = '$usr{'user_type'}';");
					my ($pbase_order, $pbase_sale,$bono_tdc,$bono_ticket) = $sth->fetchrow();
					
					my $base_order = $pbase_order ? $rec->{'SPrice'} * $pbase_order / 100 : 0;
					my $pct_max = round($pbase_sale + $bono_ticket + $bono_tdc, 2);
					my $sprice_bonus = $base_order ? $rec->{'SPrice'} * $pct_max /100 : 0;
					my $sprice1_bonus = $base_order ? $rec->{'SPrice1'} * $pct_max /100 : 0;
					my $sprice2_bonus = $base_order ? $rec->{'SPrice2'} * $pct_max /100 : 0;
					my $sprice3_bonus = $base_order ? $rec->{'SPrice3'} * $pct_max /100 : 0;
					my $sprice4_bonus = $base_order ? $rec->{'SPrice4'} * $pct_max /100 : 0;
					$va{'reward_info'} = $sprice_bonus ? '<p align="left" style="font-size:x-small;margin:10px;">* Comisi&oacute;n aproximada  basada en porcentaje m&aacute;ximo de ganancia <font color="red">('.$pct_max.'%)</font></p>'  : '<p align="left" style="font-size:x-small;margin:10px;">* Comisi&oacute;n no aplicable</p>';
		
					$va{'price_taxes'} .='<tr><td align="left">Al Aire</td><td align="right">'.&format_price($rec->{'SPrice'}).'</td><td align="right">'.$tsprice.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">'.&format_price($rec->{'SPrice'} + $shp + ($rec->{'SPrice'} * $taxes),2).'</td><td align="right">* '.&format_price($sprice_bonus).'</td></tr>';
					# ($rec->{'SPrice1'}!=0) and ($tsprice1 = &format_price($rec->{'SPrice1'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 1</td><td align="right">'.&format_price($rec->{'SPrice1'}).'</td><td align="right">'.$tsprice1.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">'.&format_price($rec->{'SPrice1'} + $shp + ($rec->{'SPrice1'} * $taxes),2).'</td><td align="right">* '.&format_price($sprice1_bonus).'</td></tr>');
					# ($rec->{'SPrice2'}!=0) and ($tsprice2 = &format_price($rec->{'SPrice2'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 2</td><td align="right">'.&format_price($rec->{'SPrice2'}).'</td><td align="right">'.$tsprice2.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">'.&format_price($rec->{'SPrice2'} + $shp + ($rec->{'SPrice2'} * $taxes),2).'</td><td align="right">* '.&format_price($sprice2_bonus).'</td></tr>');
					# ($rec->{'SPrice3'}!=0) and ($tsprice3 = &format_price($rec->{'SPrice3'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 3</td><td align="right">'.&format_price($rec->{'SPrice3'}).'</td><td align="right">'.$tsprice3.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">'.&format_price($rec->{'SPrice3'} + $shp + ($rec->{'SPrice3'} * $taxes),2).'</td><td align="right">* '.&format_price($sprice3_bonus).'</td></tr>');
					# ($rec->{'SPrice4'}!=0) and ($tsprice4 = &format_price($rec->{'SPrice4'} * $taxes,2)) and ($va{'price_taxes'} .='<tr><td align="left">Downsale 4</td><td align="right">'.&format_price($rec->{'SPrice4'}).'</td><td align="right">'.$tsprice4.'</td><td align="right">'.&format_price($shp,2).'</td><td align="right">'.&format_price($rec->{'SPrice4'} + $shp + ($rec->{'SPrice4'} * $taxes),2).'</td><td align="right">* '.&format_price($sprice4_bonus).'</td></tr>');


					for my $i(1..4){
						if ($rec->{'SPrice'.$i}!=0) {
							if ($rec->{'SPrice'.$i.'Name'}){
								$pname = $rec->{'SPrice'.$i.'Name'};
							}else{
								$pname = 'Downsale '. $i;
							}
							my $sprice_bonus = $base_order ? $rec->{'SPrice'.$i} * $pct_max /100 : 0;

							$va{'price_taxes'} .= qq|<tr>
														<td align='left'>$pname</td>
														<td align='right'>|.&format_price($rec->{'SPrice'.$i}).qq|</td>
														<td align='right'>|.&format_price($rec->{'SPrice'.$i} * $taxes,2).qq|</td>
														<td align='right'>|.&format_price($shp,2) . qq|</td>
														<td align='right'>|.&format_price($rec->{'SPrice'.$i} + $shp + ($rec->{'SPrice'.$i} * $taxes),2) . qq|</td>
														<td align='right'>*|.&format_price($sprice_bonus).qq|</td>
													</tr>|;
							
						}
					}



					## Delivery Dates
					my ($sth) = &Do_SQL("SELECT IF(DAYOFWEEK(CURDATE()) = 1,2,IF(DAYOFWEEK(CURDATE()) = 7,3,1))AS DateSum;");
					my($dateto) = 10 + $sth->fetchrow();	
						
					
					## TDC between 4-10 days
					my ($sth) = &Do_SQL("SELECT IF(TIMESTAMPDIFF(SECOND,CONCAT(CURDATE(),' 16:00:00'),NOW()) >= 1,DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 4 DAY))AS FirstDate,
															IF(TIMESTAMPDIFF(SECOND,CONCAT(CURDATE(),' 16:00:00'),NOW()) >= 1,DATE_ADD(CURDATE(), INTERVAL $dateto+2  DAY), DATE_ADD(CURDATE(), INTERVAL $dateto DAY))AS LastDate;");
					my($firstdate,$lastdate) = $sth->fetchrow();
					
					## Evaluate wether is a weekend day any of the dates
					my($sth) = &Do_SQL("SELECT IF(DAYOFWEEK('$firstdate') = 1,DATE_ADD('$firstdate',INTERVAL 1 Day),IF(DAYOFWEEK('$firstdate') = 7, DATE_ADD('$firstdate',INTERVAL 2 Day), '$firstdate'))AS FirstDate,
												IF(DAYOFWEEK('$lastdate') = 1,DATE_ADD('$lastdate',INTERVAL 1 Day),IF(DAYOFWEEK('$lastdate') = 7, DATE_ADD('$lastdate',INTERVAL 2 Day), '$lastdate'))AS LastDate;");
					my($firstdate,$lastdate) = $sth->fetchrow();				
					$va{'tdc_deliverydates'} = qq|$firstdate a $lastdate|;
					
					## COD Depends on driver delivery dates
					my ($strcod);
					my ($sth) = &Do_SQL("SELECT Name,Delivery_days,Delivery_hours,service_days FROM sl_deliveryschs WHERE Zip='$in{'zipcode'}' AND Status='Active';");
					DRIVERS:while(my($pname,$ddays,$dhours,$sdays) = $sth->fetchrow()){
						if($pname !~ /ups|fedex/i){
							## Driver?
							$va{'cod_deliverydates'} .=	qq|<tr><td align="left">$pname (COD)</td><td align="left">$ddays</td></tr>|;
						}else{
							## UPS/Fedex
							my ($sth) = &Do_SQL("SELECT IF(TIMESTAMPDIFF(SECOND,CONCAT(CURDATE(),' 16:00:00'),NOW()) >= 1,DATE_ADD(CURDATE(), INTERVAL $sdays+1 DAY), DATE_ADD(CURDATE(), INTERVAL $sdays DAY))AS FirstDate;");
							my($firstdate) = $sth->fetchrow();
							
							my($sth) = &Do_SQL("SELECT IF(DAYOFWEEK('$firstdate') = 1,DATE_ADD('$firstdate',INTERVAL 1 Day),IF(DAYOFWEEK('$firstdate') = 7, DATE_ADD('$firstdate',INTERVAL 2 Day), '$firstdate'))AS FirstDate;");
							$ddays = $sth->fetchrow();
							$va{'cod_deliverydates'} .=	qq|<tr><td align="left">$pname (COD)</td><td align="left">$ddays</td></tr>|;
						}
						
					}
					
					$fancybox_prices_cities = build_page("console_show_prices_cities.html");
				
			}else{
				$fancybox_prices_cities =qq|Error:No se encontro el producto|;
			}

	}else{
			$fancybox_prices_cities =qq|Error:Datos faltantes|;	
	}
	
	print $fancybox_prices_cities;
	return;
	
}

sub secret_cupon{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/30/11 9:23 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 04/11/11 05:48:59 PM
# Last Modified by: MCC C. Gabriel Varela S: Se cambia tama�o del modal para hacelo m�s largo
# Last Modified on: 04/13/11 12:59:24 PM
# Last Modified by: MCC C. Gabriel Varela S: Se quita validaci�n de secret_cupon_applied
#Last modified on 1 Jun 2011 12:49:01
#Last modified by: MCC C. Gabriel Varela S. :enable or disable flag is now considered


	print "Content-type: text/html\n\n";
	#Se valida que no se haya utilizado ya el cupon
	load_callsession();
# 	if($cses{'secret_cupon_applied'}==1)
# 	{
# 		print "El cup&oacute;n ya se utiliz&oacute;";
# 	}
# 	#Se valida que la palabra sea la correcta:
# 	els
	if(!$cfg{'coupons_new_way_use'})
	{
		print "Option not available";
		return;
	}
	if(!$in{'cupon'} or $in{'cupon'} eq '' or $in{'cupon'} ne $cfg{'coupons_secret_word'})
	{
		print "Invalid or missing coupon";
	}
	else
	{
		#Imprime las opciones de productos y pide email con iframe
		#Exporta tambi�n los valores de $cses
		load_callsession();
		print qq|
		<iframe src="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=ajax_cupon_window" width="490" height=350>
		  <p>Your browser does not support iframes.</p>
		</iframe>|;
		#print &build_page("secret_cupon.php");
# 			print "This is called from ajaxbuild: $in{'cupon'}";
	}
}

sub ajax_cupon_window{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 3/30/11 11:21 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 04/12/11 01:38:36 PM
# Last Modified by: MCC C. Gabriel Varela S: Se agrega validaci�n del email. Se copia de funci�n send_text_mail. Tambi�n se agrega variable secret_cupon_item
# Last Modified on: 04/13/11 01:30:59 PM
# Last Modified by: MCC C. Gabriel Varela S: Se quita validaci�n de secret_cupon_applied y se modifica para poder cambiar el producto cuantas veces se desee.
#Tambi�n se hace que se pongan por defecto los elementos que ya se eligieron si ya existen.
# Last Modified on: 04/14/11 03:09:53 PM
# Last Modified by: MCC C. Gabriel Varela S: Se cambia extensi�n de archivo secret_cupon de php a html
#Last modified on 31 May 2011 14:14:50
#Last modified by: MCC C. Gabriel Varela S. :The price and shipping is taken from configuration now
	print "Content-type: text/html\n\n";
	my $ref_item;
	if($in{'action'}==1)
	{
		#validaciones
		$err=0;
		if($in{'email'}eq'')
		{
			$error{'email'} = &trans_txt("required");
			++$err;
		}
		if($in{'id_products'}eq'')
		{
			$error{'id_products'} = &trans_txt("required");
			++$err;
		}
		if ($in{'email'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{'email'} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ )
		{
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}
		if($err>0)
		{
			$va{'tabmessages'}='Algunos de los campos son requeridos o est�n inv�lidos. Corr�galos e intente nuevamente.';
		}
		else
		{
# 			print "Here are cses:";
			load_callsession();
			if($cses{'secret_cupon_applied'}==1 and 0)
			{
				$va{'tabmessages'}="El cup&oacute;n ya se utiliz&oacute;";
			}
			else
			{
# 			foreach $key (keys %cses) 
# 			{
# 				print "$key: $cses{$key}\n<br>";
# 			}
				$in{'id_prod'}=$in{'id_products'};
				delete($va{'msg_sku'});
				if($in{'choice1'} or $in{'choice2'} or $in{'choice3'} or $in{'choice4'}){
					my ($query);
					for (1..4){
						if ($in{'choice'.$_}){
							$query .= " AND choice$_='$in{'choice'.$_}'";
						}
					}
					$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$in{'id_prod'}' $query AND Status != 'Inactive'");
					if ($sth->fetchrow()>0){
						$sth = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products='$in{'id_prod'}' $query AND Status != 'Inactive'");
						$rec = $sth->fetchrow_hashref;
						($rec->{'Status'} eq 'Backorder')	and ($va{'msg_backorder'}	=	'<tr><td colspan="4" align="center" class="stdtxterr">El Producto agregado esta en Backorder</td></tr>');
						
						if(!$cses{'secret_cupon_applied'})
						{
							++$cses{'items_in_basket'};
							$ref_item=$cses{'items_in_basket'};
						}
						else
						{
							$ref_item=$cses{'secret_cupon_item'};
						}
						$cses{'items_'.$ref_item.'_id'} = $rec->{'ID_sku_products'};
						$cses{'items_'.$ref_item.'_qty'} = 1;
						if ($cfg{'multiprice'}){
							$cses{'items_'.$ref_item.'_pnum'} = $in{'pricenumber'};
						}
					}else{
						$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products='$in{'id_prod'}'");
						if ($sth->fetchrow()>0){
							$va{'msg_sku'} = 1;	
						}
					}
				}else{
					## Load Promo
					my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='promo$in{'id_prod'}';");
					$cfg{'promo'.$in{'id_prod'}} = $sth->fetchrow;
					if ($cfg{'promo'.$in{'id_prod'}} and 0){
						$va{'msg_sku'} =1;
						my (@pary) = split(/\|/,$cfg{'promo'.$in{'id_prod'}});
						for (0..$#pary){
							if ($in{'idp'.$pary[$_].($_+1)}){
								++$cses{'items_in_basket'};
								$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $in{'idp'.$pary[$_].($_+1)};
								$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;
								$cses{'items_'.$cses{'items_in_basket'}.'_relid'} = $in{'id_prod'};
								$cses{'items_'.$cses{'items_in_basket'}.'_pnum'} = $in{'pricenumber'}if ($cfg{'multiprice'});
								$cses{'items_'.$cses{'items_in_basket'}.'_promo'} = $in{'id_prod'}+ 100000000; 
								delete($va{'msg_sku'});
							}
						}
					}else{
							$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$in{'id_prod'} AND Status !='Inactive' ");
							if ($sth->fetchrow == 1){
								$sth = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$in{'id_prod'} AND Status !='Inactive' ");
								$rec = $sth->fetchrow_hashref;
								($rec->{'Status'} eq 'Backorder')	and ($va{'msg_backorder'}	=	'<tr><td colspan="4" align="center" class="stdtxterr">El Producto agregado esta en Backorder</td></tr>');
								if(!$cses{'secret_cupon_applied'})
								{
									++$cses{'items_in_basket'};
									$ref_item=$cses{'items_in_basket'};
								}
								else
								{
									$ref_item=$cses{'secret_cupon_item'};
								}
							  $rec->{'ID_sku_products'}=$in{'id_prod'}+ 100000000;
								$cses{'items_'.$ref_item.'_id'} = $rec->{'ID_sku_products'};
								$cses{'items_'.$ref_item.'_qty'} = 1;
								if ($cfg{'multiprice'}){
									$cses{'items_'.$ref_item.'_pnum'} = $in{'pricenumber'};
								}
						}else{
							$va{'msg_sku'} =1;
						}
					}
				}
				################################
				## Choices List
				################################
				if ($va{'msg_sku'} and $cfg{'promo'.$in{'id_prod'}}){
					$va{'msg_sku'} = qq|
						<form action="/cgi-bin/mod/sales/console" method="post" name="sitform"  onsubmit="return checkchoices();">
							<input type="hidden" name="cmd" value="console_order">
							<input type="hidden" name="step" value="2">
							<input type="hidden" name="action" value="add_to_basket">
							<input type="hidden" name="skupro" value="1">
							<input type="hidden" name="pricenumber" value="$in{'pricenumber'}">
							<input type="hidden" name="id_products" value="$in{'id_prod'}">

						<tr>
							<td align="center" class="titletext" colspan="4">Debe seleccionar una opcion de la Lista</td>
					</tr>\n|;
					my (@pary) = split(/\|/,$cfg{'promo'.$in{'id_prod'}});
					for (0..$#pary){
						$va{'msg_sku'} .= qq|
						<tr>
							<td align="center" class="menu_bar_title" colspan="4">Opciones de Productos : $pary[$_] |.&load_db_names('sl_products','ID_products',$pary[$_],'[Name]/[Model]') . qq|</td>
						</tr>|;
						my $is_checked=0;
						my ($choices);
						my (@c) = split(/,/,$cfg{'srcolors'});						
						my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$pary[$_] and Status != 'Inactive' ORDER BY ID_sku_products");
						while ($rec = $sth->fetchrow_hashref){
							$d = 1 - $d;
							my $cadchecked='';
							(!$is_checked) and ($cadchecked='checked="checked"') and ($is_checked=1);
							$backorder='';
							($rec->{'Status'} eq 'Backorder')	and ($backorder	=	'<span style="color:red;">[Backorder]</span>');
							$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
							$va{'msg_sku'} .= qq| 
									<tr bgcolor='$c[$d]'>
										<td class='smalltext' colspan="2" nowrap>
												<input type='radio' class='radio' name='idp$pary[$_]|.($_+1).qq|' value='$rec->{'ID_sku_products'}' $cadchecked>
												|.&format_sltvid($rec->{'ID_sku_products'}).qq|</td>
										<td class='smalltext' colspan="2">$choices $backorder</td>
									</tr>\n|;
						}
						##onClick="trjump('$script_url?cmd=console_order&step=2&action=add_to_basket&skupro=1&id_products=$pary[$_]&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}')
					}
					$va{'msg_sku'} .= qq|
					<form>
						<tr>
							<td align="center" class="titletext" colspan="4"><input type="submit" class="button" value="Agregar al Carro"</td>
					</tr></form>\n|;
					
				}elsif ($va{'msg_sku'}){
					
					my $linkmultiprice = '';
					$linkmultiprice = "&pricenumber=$in{'pricenumber'}"	if $cfg{'multiprice'};
					
					$va{'msg_sku'} = qq|
						<tr>
							<td align="center" class="titletext" colspan="4">Debe seleccionar una opcion de la Lista</td>
						</tr>									
						<tr>
							<td align="center" class="menu_bar_title" colspan="4">Opciones de Productos</td>
						</tr>|;
									
					my ($choices);
					my (@c) = split(/,/,$cfg{'srcolors'});						
					my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$in{'id_prod'} and Status != 'Inactive' ORDER BY ID_sku_products");
					while ($rec = $sth->fetchrow_hashref){
						$d = 1 - $d;
						$backorder='';
						$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
						($rec->{'Status'} eq 'Backorder')	and ($backorder	=	'<span style="color:red;">(Backorder)</span>');
						$va{'msg_sku'} .= qq| 
								<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' onClick="trjump('$script_url?cmd=console_order&step=2&action=add_to_basket&skupro=1&id_products=$in{'id_prod'}&choice1=$rec->{'choice1'}&choice2=$rec->{'choice2'}&choice3=$rec->{'choice3'}&choice4=$rec->{'choice4'}$linkmultiprice')">
									<td class='smalltext' colspan="2" nowrap>|.&format_sltvid($rec->{'ID_sku_products'}).qq|</td>
									<td class='smalltext' colspan="2">$choices $backorder</td>
								</tr>\n|;
					}	
				}
				$cses{'secret_cupon_applied'}=1;
				$cses{'cupon_email'}=$in{'email'};
				$cses{'email'}=$in{'email'};
				$cses{'cupon_id_products'}=$in{'id_products'};
				$cses{'items_'.$ref_item.'_downpayment'} = 0;
				$cses{'items_'.$ref_item.'_fpprice'} = $cfg{'coupons_secret_price'};
				$cses{'items_'.$ref_item.'_fpago'} = 1;
				$cses{'items_'.$ref_item.'_msprice'} = $cfg{'coupons_secret_price'};
				$cses{'items_'.$ref_item.'_payments'} = 1;
				$cses{'items_'.$ref_item.'_pnum'} = 1;
				$cses{'items_'.$ref_item.'_price'} = $cfg{'coupons_secret_price'};
				$cses{'items_'.$ref_item.'_shp1'} = $cfg{'coupons_secret_shipping'};
				$cses{'items_'.$ref_item.'_shp2'} = $cfg{'coupons_secret_shipping'};
				$cses{'items_'.$ref_item.'_shp3'} = $cfg{'coupons_secret_shipping'};
# 				$cses{'items_'.$ref_item.'_promo'} = 1;
				$cses{'items_'.$ref_item.'_secret_cupon'} = 1;
				$cses{'secret_cupon_item'} = $ref_item;
				$va{'tabmessages'}='El cup�n se ha aplicado, ahora puede cerrar la ventana';
				save_callsession();
			}
		}
	}
	else
	{
		load_callsession();
		$in{'id_products'}=substr($cses{'items_'.$cses{'secret_cupon_item'}.'_id'},3,6);
		$in{'email'}=$cses{'cupon_email'};
	}
	$va{'products_info'}=build_coupons_products_info();
	#print &build_page('secret_cupon_email.html');
	print &build_page("secret_cupon.html");
}

sub click_to_call{
# --------------------------------------------------------  
	#($end,$username,$password,$server,%command) 
	#my ($server)   = '63.95.246.131';
	#my ($username) = 'direksysdev';
	#my ($password) = '32-221611';
		
	print "Content-type: text/html\n\n";
	if (length($in{'num'}) == 10 and $usr{'extension'}>0){

		if (!$in{'inframe'} and !$in{'action'}){
			print qq|
			<iframe src="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=click_to_call&num=$in{'num'}&id=$in{'id'}&inframe=1" width="400" height="150">
			  <p>Your browser does not support iframes.</p>
			</iframe>|;
		}elsif($in{'action'} and $in{'calif'}){
			print "<link REL='STYLESHEET' HREF='/sitimages/default/main.css' TYPE='text/css'>";
			print "<p>&nbsp;</p><p align='center'>Llamada, Calificada</p><p>&nbsp;</p>";
			my ($sth) = &Do_SQL("UPDATE sl_leads_calls SET Calif='$in{'calif'}' WHERE ID_leads_calls='$in{'id_outcalls'}'");
		}else{
			my (%command)  = (ACTION => 'Originate',Channel => 'SIP/'.$usr{'extension'},Exten => '8'.$in{'num'},Priority => '1',Context => 'from-internal',	Async => 'True',	Callerid => "<$in{'num'}>");
			@ary = &send_cmd_to_ast(0,$cfg{'outserver_user'},$cfg{'outserver_pass'},$cfg{'outserver'},%command );
			if (!$in{'id_outcalls'}){
				my ($sth) = &Do_SQL("INSERT INTO sl_leads_calls SET ID_leads='$in{'num'}',IO='Out',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				$id_calls = $sth->{'mysql_insertid'};
			}
			$fmt_number = '('.substr($in{'num'},0,3).') '.substr($in{'num'},3,3) . ' - ' . substr($in{'num'},-4);

			print qq| 
		<link REL='STYLESHEET' HREF='/sitimages/default/main.css' TYPE='text/css'>
	    <form action="/cgi-bin/common/apps/ajaxbuild" method="post">
		    <input type="hidden" name="ajaxbuild" value="click_to_call">
		    <input type="hidden" name="num" value="$in{'num'}">
		    <input type="hidden" name="id" value="$in{'id'}">
		    <input type="hidden" name="action" value="1">
		    <input type="hidden" name="id_outcalls" value="$id_calls">
	    <p>Llamando a : $fmt_number
		<table border="0" cellspacing="0" cellpadding="0" width="100%" class="formtable">
	 		<tr>
	 			<td class="menu_bar_title"  align="center">Calificar llamada</td>
	 		</tr>
	 		<tr>
	 			<td><input type='radio' class='radio' name='calif' value='No Contesta'> No contesta / Acupado / Voicemail</td>
	 		</tr>
	 		<tr>
	 			<td><input type='radio' class='radio' name='calif' value='DNC'> No Volver a Llamar (DNC)</td>
	 		</tr>	 
	 		<tr>
	 			<td><input type='radio' class='radio' name='calif' value='Contestada' checked> Contestada</td>
	 		</tr>
	 		<tr>
	 			<td align="center"><input type='submit' class='button' name='action' value='Calificar'></td>
	 		</tr>
	 	</table>
	 	</form>\n|;
		}
	}else{
		print "<p>&nbsp;</p><p align='center'>Error, Numero inv�lido o su usuario no tiene una extension definida</p><p>&nbsp;</p>";
	}
	#print join('',@ary);
	#foreach ( @ary ) {
	#	print "$_\n";
	#}
	#print "</pre>";
}

sub email_and_cellphone{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 5/02/11 9:23 AM
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 5 May 2011 11:08:50
#Last modified by: MCC C. Gabriel Varela S. :Se hace que no se muestren los campos si ya la informaci�n est� correcta.
#Se quitan caracteres no num�ricos a celular antes de ser validado.
#campo concat_mode
#Last modified on 23 May 2011 14:04:32
#Last modified by: MCC C. Gabriel Varela S. :Se cambia orden de evaluaciones.
	print "Content-type: text/html\n\n";
	my $ref_item;
	if($in{'action'}==1)
	{
		#validaciones
		$err=0;
		
		if($in{'contact_mode'}eq'')
		{
			$error{'contact_mode'} = &trans_txt("required");
			++$err;
		}
		
		if ($in{'email'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{'email'} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and $in{'email'} ne '')
		{
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}
		
		#Formato para celular
		$in{'cellphone'}=~s/\D//g;
		if ($in{'cellphone'} !~ /[0-9]{10}/ and $in{'cellphone'}ne '')
		{
			$error{'cellphone'} = &trans_txt("invalid");
			++$err;
		}
		
		if($in{'email'}eq'' and $in{'contact_mode'}eq'email')
		{
			$error{'email'} = &trans_txt("required");
			++$err;
		}
		if($in{'cellphone'}eq'' and $in{'contact_mode'}eq'sms')
		{
			$error{'cellphone'} = &trans_txt("required");
			++$err;
		}
		
		#Aqu� se guardan los datos por si alguno de los 2 est� correcto
		if($error{'email'}eq'')
		{
			load_callsession();
			$cses{'email'}=$in{'email'};
			save_callsession();
		}
		if($error{'cellphone'}eq'')
		{
			load_callsession();
			$cses{'cellphone'}=$in{'cellphone'};
			save_callsession();
		}
		if($error{'contact_mode'}eq'')
		{
			load_callsession();
			$cses{'contact_mode'}=$in{'contact_mode'};
			save_callsession();
		}
# 		cgierr("if($error{'cellphone'} ne '' and $error{'email'} ne '')");
# 		if($error{'cellphone'} ne '' and $error{'email'} ne '')
		if($err>0)
		{
			$va{'tabmessages'}='Algunos de los campos son requeridos o est�n inv�lidos. Corr�galos e intente nuevamente.';
		}
		else
		{
# 			print "Here are cses:";
			load_callsession();
			if($cses{'email'}  ne '' and $cses{'cellphone'} ne '' and $cses{'contact_mode'} ne '' and $in{'email'}eq$cses{'email'} and $in{'cellphone'}eq$cses{'cellphone'} and $in{'contact_mode'}eq$cses{'contact_mode'})
			{
# 				print "Gracias por la informaci�n proporcionada y autorizar a ponernos en contacto con usted por �ste medio, ahora puede cerrar la ventana";
				$va{'tabmessages'}="Gracias por la informaci�n proporcionada y autorizar a ponernos en contacto con usted por �ste medio, ahora puede cerrar la ventana";
				print &build_page("email_and_cellphone_done.html");
				return;
			}
			else
			{
# 			foreach $key (keys %cses) 
# 			{
# 				print "$key: $cses{$key}\n<br>";
# 			}
				$cses{'email'}=$in{'email'};
				$cses{'cellphone'}=$in{'cellphone'};
				$cses{'contact_mode'}=$in{'contact_mode'};
				
				$va{'tabmessages'}='Los datos se han verificado y son correctos, ahora puede cerrar la ventana';
				save_callsession();
				print &build_page("email_and_cellphone_done.html");
				return;
			}
		}
	}
	else
	{
		load_callsession();
		$in{'email'}=$cses{'email'};
		$in{'cellphone'}=$cses{'cellphone'};
		$in{'contact_mode'}=$cses{'contact_mode'};
	}
	$va{'products_info'}=build_coupons_products_info();
	#print &build_page('secret_cupon_email.html');
	print &build_page("email_and_cellphone.html");
}

sub secret_cupon_followup{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 27 May 2011 18:57:43
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 31 May 2011 16:19:29
#Last modified by: MCC C. Gabriel Varela S. :Se agrega id_orders e id_customers
#Last modified on 8 Jun 2011 13:53:32
#Last modified by: MCC C. Gabriel Varela S. :The information is now asked in a new window
	print "Content-type: text/html\n\n";
	if(!$cfg{'coupons_new_way_use'})
	{
		print "Option not available";
		return;
	}
	#Se valida que no se haya utilizado ya el cup�n
	if(!$in{'cupon'} or $in{'cupon'} eq '' or $in{'cupon'} ne $cfg{'coupons_secret_word'})
	{
		$va{'tabmessages'}="Invalid or missing coupon";
		print &build_page("secret_cupon_followup_ask_coupon.html");
# 		print "Invalid or missing coupon";
	}
	else
	{
		$in{'id_orders'}=$in{'view'} if($in{'id_orders'} eq'' and $in{'view'} ne '');
		print qq|
		<iframe src="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=ajax_cupon_window_followup&id_orders=$in{'id_orders'}&id_customers=$in{'id_customers'}" width="490" height=350>
		  <p>Your browser does not support iframes.</p>
		</iframe>|;
	}
}

sub ajax_cupon_window_followup{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 27 May 2011 18:58:53
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 31 May 2011 12:28:29
#Last modified by: MCC C. Gabriel Varela S. :Se contin�a el desarrollo
#Last modified on 1 Jun 2011 10:57:28
#Last modified by: MCC C. Gabriel Varela S. :recalc_totals is included and the confirmation string is deleted from the notes

	print "Content-type: text/html\n\n";
	if($in{'action'}==1)
	{
		#validaciones
		$err=0;
		if($in{'email'}eq'')
		{
			$error{'email'} = &trans_txt("required");
			++$err;
		}
		if($in{'id_products'}eq'')
		{
			$error{'id_products'} = &trans_txt("required");
			++$err;
		}
		if ($in{'email'} =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ or $in{'email'} !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ )
		{
			$error{'email'} = &trans_txt("invalid");
			++$err;
		}
		if($err>0)
		{
			$va{'tabmessages'}='Algunos de los campos son requeridos o est�n inv�lidos. Corr�galos e intente nuevamente.';
		}
		else
		{
# 			print "Here are cses:";
			#Verificar que no se haya aplicado ya la promoci�n.
			my $sth=&Do_SQL("Select * 
			from sl_orders_products 
			where ID_orders='$in{'id_orders'}'
			and SalePrice=$cfg{'coupons_secret_price'}
			and Shipping=$cfg{'coupons_secret_shipping'}
			and Status='Active'");
			my $rows=$sth->rows();
			if($rows >0 and 0)
			{
				$va{'tabmessages'}="The order has already a promo product.";
			}
			else
			{
				$in{'id_prod'}=$in{'id_products'};
				delete($va{'msg_sku'});
				
				
					$sth = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_products=$in{'id_prod'} AND Status !='Inactive' ");
					if ($sth->fetchrow == 1){
						$sth = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products=$in{'id_prod'} AND Status !='Inactive' ");
						$rec = $sth->fetchrow_hashref;
						($rec->{'Status'} eq 'Backorder')	and ($va{'msg_backorder'}	=	'<tr><td colspan="4" align="center" class="stdtxterr">El Producto agregado esta en Backorder</td></tr>');
						$rec->{'ID_sku_products'}=$in{'id_prod'}+ 100000000;
				}else{
					$va{'msg_sku'} =1;
				}
				
				#update the customer email
				&Do_SQL("update sl_customers set email='$in{'email'}' where id_customers='$in{'id_customers'}'");
				
				#get ordertax
				$ordertax=&load_name('sl_orders','ID_orders',$in{'id_orders'},'OrderTax');
				
				#Insert the product
				&Do_SQL("Insert into sl_orders_products set
				ID_products='".(100000000+$in{'id_products'})."',
				ID_orders='$in{'id_orders'}',
				Quantity=1,
				SalePrice=$cfg{'coupons_secret_price'},
				Shipping=$cfg{'coupons_secret_shipping'},
				Tax=".($cfg{'coupons_secret_price'}*$ordertax).",
				FP=1,
				Status='Active',
				Date=curdate(),
				Time=curtime(),
				ID_admin_users='$usr{'id_admin_users'}'");
				
				#Look for the last payment
				my $sth_payment=&Do_SQL("Select *,
				if((Authcode='' or isnull(Authcode) or AuthCode='0000')
				and(AuthDateTime='' or isnull(AuthDateTime) )
				and (Captured='No' or Captured='' or isnull(Captured))
				and (CapDate='0000:00:00' or isnull(Capdate))
				and Amount>0,1,0)as is_editable
				from sl_orders_payments
				where ID_orders='$in{'id_orders'}'
				and Status='Approved'
				order by ID_orders_payments desc
				limit 1");
				$rec_payment=$sth_payment->fetchrow_hashref;
				
				if($rec_payment->{'is_editable'} eq'0' or !$rec_payment->{'is_editable'})
				{
					#Insert the payment
					&Do_SQL("Insert into sl_orders_payments set
					ID_orders='$in{'id_orders'}',
					Type='$rec_payment->{'Type'}',
					PmtField1='$rec_payment->{'PmtField1'}',
					PmtField2='$rec_payment->{'PmtField2'}',
					PmtField3='$rec_payment->{'PmtField3'}',
					PmtField4='$rec_payment->{'PmtField4'}',
					PmtField5='$rec_payment->{'PmtField5'}',
					PmtField6='$rec_payment->{'PmtField6'}',
					PmtField7='$rec_payment->{'PmtField7'}',
					PmtField8='$rec_payment->{'PmtField8'}',
					PmtField9='$rec_payment->{'PmtField9'}',
					Amount=".($cfg{'coupons_secret_price'}*(1+$ordertax)+$cfg{'coupons_secret_shipping'}).",
					Paymentdate=curdate(),
					Status='Approved',
					Date=curdate(),
					Time=curtime(),
					ID_admin_users='$usr{'id_admin_users'}'
					");
				}
				else
				{
					#Update the payment amount
					&Do_SQL("Update sl_orders_payments
					set Amount=Amount+".($cfg{'coupons_secret_price'}*(1+$ordertax)+$cfg{'coupons_secret_shipping'})."
					where ID_orders='$in{'id_orders'}';");
				}				
				
				&add_order_notes_by_type($in{'id_orders'},"Se ha agregado un producto por medio de cup�n secreto.","Low");
				
				#Inserta log
				$in{'db'}='sl_orders';
				&auth_logging('orders_secret_coupon',$in{'id_orders'});
				
				#env�a email
				$va{'firstname'}=&load_name('sl_customers','ID_customers',$in{'id_customers'},'FirstName');
				use MIME::Base64;
				my $varcustomer,$varorder;
				$varcustomer=encode_base64($in{'id_customers'});
				$varorder=encode_base64($in{'id_orders'});
				$varcustomer=substr($varcustomer,0,length($varcustomer)-1);
				$varorder=substr($varorder,0,length($varorder)-1);
				$va{'confirmation_string'}=$varcustomer.'-g-'.$varorder;
				$va{'name'}=&load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[FirstName] [LastName1] [LastName2]');
				$message_mail = &build_page('secret_cupon_followup_email.html');
				$sendmail=&send_text_mail($cfg{'cservice_email'},$in{'email'},$cfg{'coupons_secret_subject'},$message_mail);
				if($sendmail eq 'ok')
				{
					my ($sth)=&Do_SQL("insert into sl_customers_notes 
					set ID_customers='$in{'id_customers'}',
					notes='Se ha enviado el email de confirmaci�n de producto gratis. ',
					Type='Low',
					Date=curdate(),
					Time=curtime(),
					ID_admin_users='$usr{'id_admin_users'}'");
				}
				else
				{
					my ($sth)=&Do_SQL("insert into sl_customers_notes 
					set ID_customers='$in{'id_customers'}',
					notes='No se pudo enviar el email de confirmaci�n, raz�n: $sendmail. ',
					Type='Low',
					Date=curdate(),
					Time=curtime(),
					ID_admin_users='$usr{'id_admin_users'}");
				}
				$in{'shp_zip'}=&load_name('sl_orders','ID_orders',$in{'id_orders'},'shp_Zip');
				$in{'shp_state'}=&load_name('sl_orders','ID_orders',$in{'id_orders'},'shp_State');
				&recalc_totals($in{'id_orders'});
				$va{'tabmessages'}='El cup�n se ha aplicado, ahora puede cerrar la ventana';
				$va{'location'}=$cfg{'pathcgi_fup_dbman'};
				print &build_page("secret_cupon_followup_done.html");
				return;
			}
		}
	}
	print &build_page("secret_cupon_followup.html");

}

sub search_address1{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 6 Jun 2011 12:29:45
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: text/html\n\n";
	#Se valida que no se haya utilizado ya el cup�n
# 	load_callsession();
# 	if($cses{'secret_cupon_applied'}==1)
# 	{
# 		print "El cup&oacute;n ya se utiliz&oacute;";
# 	}
# 	#Se valida que la palabra sea la correcta:
# 	els
	if(!$cfg{'search_address_use'})
	{
		print "Option not available";
		return;
	}
# 	if(!$in{'number'} or $in{'number'} eq '' or !$in{'zipcode'} or $in{'zipcode'} eq '')
# 	{
# 		print "Invalid or missing information";
# 	}
# 	else
# 	{
		print qq|
		<iframe src="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=search_address_window&search_address_number=$in{'number'}&search_address_zip=$in{'zipcode'}&step=$in{'step'}" width="490" height="300">
		  <p>Your browser does not support iframes.</p>
		</iframe>|;
# 	}
}

#########################################################################################
#########################################################################################
#   Function: string_trim
#
#       Es: Elimina espacios en blanco a la izquierda y derecha de una cadena
#
#       En: Removes white space to the left and right of a string
#
#
#
#   Created on: 06/11/2012  12:11
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#      - string .- Cadena que necesita ser procesada
#
#   Returns:
#
#      - string .- Cadena procesada
#
sub string_trim {

	$string =~ s/^\s+//;
	$string =~ s/\s+$//;

	return string;
}

sub search_address_window{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 6 Jun 2011 12:41:38
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
#Last modified on 7 Jun 2011 10:43:59
#Last modified by: MCC C. Gabriel Varela S. :Se crean los cses si no hay errores
#Last modified on 9 Jun 2011 13:22:25
#Last modified by: MCC C. Gabriel Varela S. :The billing information is set if it hasn't
#Last modified on 13 Jun 2011 16:20:43
#Last modified by: MCC C. Gabriel Varela S. :hash states is defined
	print "Content-type: text/html\n\n";
	my $ref_item;
	
	if($in{'action_choose'}==1){
		#validations
		$err=0;
		if($in{'search_address_number'} eq ''){
			$error{'search_address_number'} = &trans_txt("required");
			++$err;
		}elsif ($in{'search_address_number'} !~ /^\d+$/){
			$error{'search_address_number'} = &trans_txt("invalid");
			++$err;
		}
		if($in{'search_address_zip'} eq ''){
			$error{'search_address_zip'} = &trans_txt("required");
			++$err;
		}elsif ($in{'search_address_zip'} !~ /^\d{5}$/){
			$error{'search_address_zip'} = &trans_txt("invalid");
			++$err;
		}
		
		if($in{'search_address_city'} eq '')	{
			$error{'search_address_city'} = &trans_txt("required");
			++$err;
		}
		if($in{'search_address_state'} eq '')	{
			$error{'search_address_state'} = &trans_txt("required");
			++$err;
		}
		if($in{'street_address'} eq '')	{
			$error{'street_address'} = &trans_txt("required");
			++$err;
		}
		
		
		
		if($err>0){
			$va{'tabmessages'}='Algunos de los campos son requeridos o est�n inv�lidos. Corr�galos e intente nuevamente.';
			#Realiza la b�squeda
			($va{'addresses'},$va{'address_number'},$va{'address_city'},$va{'address_state'},$va{'address_zip'},@possible_addresses)=&search_address_m($in{'search_address_number'},$in{'search_address_zip'});
# 			$va{'possible_addresses'}='';
			for(1..$va{'addresses'}){
				$va{'possible_addresses'}.="<input type='radio' name='street_address' value='$possible_addresses[$_]'>$possible_addresses[$_]<br>" if($possible_addresses[$_] ne '');
			}
			print &build_page("search_address_results.html");
			return;
		}else{
			$va{'tabmessages'}='La direcci�n se ha establecido de forma adecuada. Ahora puede cerrar la ventana.';
			
			my %states=('AL'=>'AL-Alabama',
				'AK'=>'AK-Alaska',
				'AZ'=>'AZ-Arizona',
				'AR'=>'AR-Arkansas',
				'CA'=>'CA-California',
				'CO'=>'CO-Colorado',
				'CT'=>'CT-Connecticut',
				'DE'=>'DE-Delaware',
				'FL'=>'FL-Florida',
				'GA'=>'GA-Georgia',
				'HI'=>'HI-Hawaii',
				'ID'=>'ID-Idaho',
				'IL'=>'IL-Illinois',
				'IN'=>'IN-Indiana',
				'IA'=>'IA-Iowa',
				'KS'=>'KS-Kansas',
				'KY'=>'KY-Kentucky',
				'LA'=>'LA-Louisiana',
				'ME'=>'ME-Maine',
				'MD'=>'MD-Maryland',
				'MA'=>'MA-Massachusetts',
				'MI'=>'MI-Michigan',
				'MN'=>'MN-Minnesota',
				'MS'=>'MS-Mississippi',
				'MO'=>'MO-Missouri',
				'MT'=>'MT-Montana',
				'NE'=>'NE-Nebraska',
				'NV'=>'NV-Nevada',
				'NH'=>'NH-New Hampshire',
				'NJ'=>'NJ-New Jersey',
				'NM'=>'NM-New Mexico',
				'NY'=>'NY-New York',
				'NC'=>'NC-North Carolina',
				'ND'=>'ND-North Dakota',
				'OH'=>'OH-Ohio',
				'OK'=>'OK-Oklahoma',
				'OR'=>'OR-Oregon',
				'PA'=>'PA-Pennsylvania',
				'PR'=>'PR-Puerto Rico',
				'RI'=>'RI-Rhode Island',
				'SC'=>'SC-South Carolina',
				'SD'=>'SD-South Dakota',
				'TN'=>'TN-Tennessee',
				'TX'=>'TX-Texas',
				'UT'=>'UT-Utah',
				'VT'=>'VT-Vermont',
				'VA'=>'VA-Virginia',
				'WA'=>'WA-Washington',
				'WV'=>'WV-West Virginia',
				'WI'=>'WI-Wisconsin',
				'WY'=>'WY-Wyoming');
			
			#Aqu� se crean los cses
			load_callsession();
			if($in{'step'}=~/4/){
				$cses{'address1'} = $in{'street_address'};
				$cses{'zip'}=$in{'search_address_zip'};
				$cses{'city'}=$in{'search_address_city'};
				$cses{'state'}=$states{$in{'search_address_state'}};
				$cses{'customers.address1'}=$in{'street_address'};
			}
			
# 			$cses{'customers.zip'}=$in{'search_address_zip'};
# 			$cses{'customers.city'}=$in{'search_address_city'};
# 			$cses{'customers.state'}=$in{'search_address_state'};
			
			$in{'customers.address1'}=$in{'street_address'};
			$in{'zip'}=$in{'search_address_zip'};
			$in{'city'}=$in{'search_address_city'};
			$in{'state'}=$states{$in{'search_address_state'}};
			
			if($in{'sameshipping'} or $in{'step'}=~/5/){
				$cses{'shp_address1'}=$in{'street_address'};
				$cses{'shp_zip'}=$in{'search_address_zip'};
				$cses{'shp_city'}=$in{'search_address_city'};
				$cses{'shp_state'}=$states{$in{'search_address_state'}};
				
				$cses{'address1'}=$in{'street_address'}if($in{'sameshipping'} or !$cses{'address1'});
				$cses{'zip'}=$in{'search_address_zip'}if($in{'sameshipping'} or !$cses{'zip'});
				$cses{'city'}=$in{'search_address_city'}if($in{'sameshipping'} or !$cses{'city'});
				$cses{'state'}=$states{$in{'search_address_state'}}if($in{'sameshipping'} or !$cses{'state'});
				
				$in{'shp_zip'}=$in{'search_address_zip'};
				$in{'shp_city'}=$in{'search_address_city'};
				$in{'shp_state'}=$states{$in{'search_address_state'}};
				
				$in{'city_to_show'} .= $in{'search_address_city'}.' | ';
			}
			save_callsession();

			$cfg{'pathcgi_cci_cons'} = '/cgi-bin/mod/sales/admin';
			$va{'location'}=$cfg{'pathcgi_cci_cons'};
			print &build_page("search_address_results_done.html");
			return;
		}
	}
	
	if($in{'action'}==1 or($in{'search_address_number'} ne '' and $in{'search_address_zip'} ne '')){
		#validaciones
		$err=0;
		if($in{'search_address_number'}eq''){
			$error{'search_address_number'} = &trans_txt("required");
			++$err;
		}elsif ($in{'search_address_number'} !~ /^\d+$/){
			$error{'search_address_number'} = &trans_txt("invalid");
			++$err;
		}
		if($in{'search_address_zip'}eq''){
			$error{'search_address_zip'} = &trans_txt("required");
			++$err;
		}elsif ($in{'search_address_zip'} !~ /^\d{5}$/){
			$error{'search_address_zip'} = &trans_txt("invalid");
			++$err;
		}
		if($err>0){
			$va{'tabmessages'}='Algunos de los campos son requeridos o est�n inv�lidos. Corr�galos e intente nuevamente.';
			print &build_page("search_address.html");
			return;
		}else{
			#Realiza la b�squeda
			($va{'addresses'},$va{'address_number'},$va{'address_city'},$va{'address_state'},$va{'address_zip'},@possible_addresses)=&search_address_m($in{'search_address_number'},$in{'search_address_zip'});
# 			$va{'possible_addresses'}='';
			for(0..$#possible_addresses){
				$va{'possible_addresses'} .= "<input type='radio' name='street_address' value='$possible_addresses[$_]'>$possible_addresses[$_] <br>" if($possible_addresses[$_] ne '');
			}
			if($va{'possible_addresses'} eq ''){
				$va{'tabmessages'}=&trans_txt('search_nomatches');
				print &build_page("search_address.html");
				return;
			}
			print &build_page("search_address_results.html");
			return;
		}
	}
	print &build_page("search_address.html");
}

sub getCityState{
# --------------------------------------------------------
# Created on: 06/03/2011 01:26:18 PM  
# Author: Roberto Barcenas
# Description : Regresa una cadena con Ciudad~Estado
# Parameters : zipcode
#  

  my ($query);
	if ($cfg{'state_exclude'}){
		$query = "AND State!='$cfg{'state_exclude'}'";
	}elsif	($cfg{'state_only'}){
		$query = "AND State='$cfg{'state_only'}'";
	}
	my ($sth) = &Do_SQL("SELECT * FROM sl_zipcodes WHERE ZipCode='$in{'zip'}' /*AND PrimaryRecord='P'*/ $query GROUP BY city;");
	my $city='';
	my $state='';
	while($tmp = $sth->fetchrow_hashref()){
		if ($tmp->{'ZipCode'}>0){
			$city .= $tmp->{'City'}.' | ';
			$state = $tmp->{'State'}."-".$tmp->{'StateFullName'};
		}
	}
	$city =~ s/\s*$//;
  chop($city);

  print "Content-type: text/html\n\n";
  print $city.'~'.$state;

}

sub review_customers_window{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 15 Jun 2011 15:39:24
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: text/html\n\n";
	
	if($in{'action_choose'}==1)
	{
		#validations
		$err=0;
		if($in{'id_customers'}eq'')
		{
			$error{'id_customers'} = &trans_txt("required");
			++$err;
		}
		if($err>0)
		{
			$va{'tabmessages'}='Some of the fields are incorrect or invalid. Fill them properly and try again.';
			#Realiza la b�squeda
			
			print &build_page("review_customer_results.html");
			return;
		}
		else
		{
			$va{'location'}=$cfg{'pathcgi_adm_admin'};
			$va{'tabmessages'}="El cliente se ha elegido de forma exitosa.";
			#Realiza la b�squeda
			
			print &build_page("review_customer_results_done.html");
			return;
		}
	}
	
	my $where="";
	if($in{'name'} ne '')
	{
		$where=" or firstname like '%$in{'name'}%' ";
	}
# 	if($in{'firstlastname'} ne '')
# 	{
# 		$where=" or lastname1 like '%$in{'firstlastname'}%' ";
# 	}
# 	if($in{'secondlastname'} ne '')
# 	{
# 		$where=" or lastname2 like '%$in{'secondlastname'}%' ";
# 	}
	if($in{'phone1'} ne '')
	{
		$where=" or phone1 like '%$in{'phone1'}%' ";
	}
	if($in{'cellphone'} ne '')
	{
		$where=" or cellphone like '%$in{'cellphone'}%' ";
	}
	if($in{'address1'} ne '')
	{
		$where=" or address1 like '%$in{'address1'}%' ";
	}
	if($in{'email'} ne '')
	{
		$where=" or email like '%$in{'email'}%' ";
	}
	my $sth=&Do_SQL("Select id_customers, firstname, lastname1, phone1,phone2,cellphone,address1,email
	from sl_customers
	where 0 $where");
	while($rec=$sth->fetchrow_hashref)
	{
		$va{'possible_customers'}.="<input type='radio' name='id_customers' value='$rec->{'id_customers'}'>$rec->{'id_customers'}: $rec->{'firstname'} $rec->{'lastname1'} $rec->{'lastname2'}<br>Phones: $rec->{'phone1'} $rec->{'phone2'}<br>Cellphone: $rec->{'cellphone'}<br>Email: $rec->{'email'}<br>Address: $rec->{'address1'}<br><br>";
	}
	if($va{'possible_customers'}eq'')
	{
		$va{'possible_customers'}=&trans_txt('search_nomatches');
	}
	
	print &build_page("review_customer_results.html");
}

sub review_customers{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 16 Jun 2011 10:58:14
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: text/html\n\n";
	print qq|
	<iframe src="/cgi-bin/common/apps/ajaxbuild?ajaxbuild=review_customers_window&address1=$in{'address1'}&cellphone=$in{'cellphone'}&phone1=$in{'phone1'}&email=$in{'email'}" width="490" height=350>
	  <p>Your browser does not support iframes.</p>
	</iframe>|;
}



sub update_callcenter_availability{
# --------------------------------------------------------
# Forms Involved: mm_callcenters_availability
# Created on: 10 Nov 2011 19:45:14
# Author: Roberto Barcenas
# Description :
# Description: Actualiza un registro de S7 en la tabla sl_callcenters
# Parameters :
# Last Modified RB: 11/10/11

	print "Content-type: text/html\n\n";

	if($in{'id'} and $in{'from_time'} and $in{'to_time'}){
		my $from_time=$in{'from_time'}.':00';
		my $to_time=$in{'to_time'}.':00';
		($to_time eq '24:00:00'  or $to_time eq '23:59:00') and ($to_time='23:59:59');
	

		&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
		print "UPDATE sl_callcenters SET FromTime='$from_time', ToTime='$to_time' WHERE ID_Callcenter='$in{'id'}';";

		my ($sth)=&Do_SQL("UPDATE sl_callcenters SET FromTime='$from_time', ToTime='$to_time' WHERE ID_Callcenter='$in{'id'}';",1);
		if($sth->rows() == 1){
			$in{'db'}='sl_callcenters';
			$in{'cmd'}='med_callcenters_availability';
			&auth_logging('schedule_updated',$in{'id'},1);
			print 'ok';
		}else{
			print  $sth->errmsg();
		}
	}else{
		print 'Data Missed';
	}
}


sub get_xamount{
# --------------------------------------------------------
# Forms Involved: eco_orders
# Created on: 23 Nov 2011 19:15:14
# Author: Roberto Barcenas
# Description :
# Description: Devuelve el total de Amount a pagar
# Parameters :
# Last Modified RB:

	print "Content-type: text/html\n\n";

	if($in{'city'} and $in{'state'} and $in{'zip'} and $in{'sprice'}){

		my $state=$in{'state'};
		my $city=$in{'city'};
		my $zip=$in{'zip'};

		my $amount=0;
		my $sprice=$in{'sprice'};
		my $shipping = $in{'shp'} > 0 ? $in{'shp'} : 0;
		

		my $taxes = calculate_taxes($zip,$state,$city,0);

		$amount = $sprice + $shipping + ($sprice*$taxes);

		if($amount > 0){
			print $amount;
		}else{
			print "error:$amount = $sprice + $shipping + ($sprice*$taxes);";
		}
	}else{
		print "error:Data Missing";
	}
	return;
}

sub assign_did{
# --------------------------------------------------------
# Forms Involved: eco_orders
# Created on: 23 Nov 2011 19:15:14
# Author: Carlos Haas
# Description :
# Description: Assign DID to Order
# Parameters :
# Last Modified RB on 106/15/2012: Se completa manejo de sl_leads y sl_leads_calls

	$in{'did'} = int($in{'did'});
	$in{'id_orders'} = int($in{'id_orders'});
	$in{'products'} =~ s/<br>/&nbsp;/g;
	($in{'contract'}) and ($in{'contract'} = int($in{'contract'}));

	print "Content-type: text/html\n\n";
	if ($in{'did'}){
	
		if($in{'contract'}){
	
				my $setcontract = $in{'contract'} ? ",ID_mediacontracts='$in{'contract'}' " : '';
				my $dids7 = $in{'did'} < 9991 ? &load_name('sl_mediadids','didmx',$in{'did'},'didusa') : '999' . $in{'did'};

				## leads and leads_calls
				my $order_date = load_db_names('sl_orders','ID_orders',$in{'id_orders'},'[Date] [Time]');
				my $idc = load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
				my $order_phone = load_name('sl_customers','ID_customers',$idc,'Phone1');
				my $destination = load_name('sl_mediacontracts','ID_mediacontracts',$in{'contract'},'Destination');
				

				my $q1 = "UPDATE sl_orders SET DNIS='$in{'did'}', DIDS7='".$dids7."' $setcontract  WHERE ID_orders='$in{'id_orders'}';";
				my $q2 = "INSERT IGNORE INTO sl_leads SET ID_leads='$order_phone', Status='Active',Date=DATE(SUBTIME('$order_date','00:01:00')), Time=TIME(SUBTIME('$order_date','00:01:00')), ID_admin_users=2;";
				my $q3 = "INSERT IGNORE INTO sl_leads_calls SET ID_leads='$order_phone',IO='In',DIDUS='$dids7',Destination='$destination',Duration='900', ID_order_assign=0, ID_orders='$in{'id_orders'}', ID_mediacontract_assign=0, ID_mediacontracts = '$in{'contract'}', Date=DATE(SUBTIME('$order_date','00:01:00')), Time=TIME(SUBTIME('$order_date','00:01:00')), ID_admin_users=2;";

				# sl_orders
				my $sth2 = &Do_SQL($q1);
				# sl_leads
				my $sth2 = &Do_SQL($q2);
				# sl_leads_calls
				my $sth2 = &Do_SQL($q3);

				
				&add_order_notes_by_type($in{'id_orders'},"Contract and DID Assigned","Low");
				&auth_logging('sl_orders_contractassigned',$in{'id_orders'});

				#print '/*Order*/ $q1\n/*Lead*/ $q2\n/*LeadCall*/ $q3\n';
				print '<td class="stdtxterr">Assignado</td>';
				return;

		}
		
	}

	print qq|	<table border="0" cellspacing="0" cellpadding="2" width="540" height="420" bgcolor="#FFFFFF">
				<tr>
					<td colspan='3' align="center" class='smalltext'>Order ID: $in{'id_orders'} \@ $in{'date'}   $in{'time'}<br>$in{'products'}</td>
				</tr>
				<tr>
					<td align="center" bgcolor="#CEFFCE">Offer</td>
					<td align="center" bgcolor="#CEFFCE">Station</td>
					<td align="center" bgcolor="#CEFFCE">Day Time</td>
				</tr>\n|;

	my ($dma, $tmp, $n);

	#
	# NOTA
	# revisar que no se pase de los 7 dias
	# Agregar la opcion de asociar al grupo "Goteo"
	#


	#######################################
	#### Contrcts by Area code & DMA
	#######################################
	print qq|	
				<tr>
					<td align="center" colspan="3" class='smalltext'>Contracts by areacode $in{'areacode'} & Zipcode $in{'zip'}</td>
				</tr>\n|;
	$in{'areacode'} = " OR AreCode in ($in{'areacode'})" if ($in{'areacode'}); 
	my ($sth3) = &Do_SQL("SELECT DMA_DESC FROM sl_zipdma WHERE ZipCode='$in{'zip'}' $in{'areacode'} GROUP BY DMA_DESC");
	while($tmp = $sth3->fetchrow()){
		$dma .= "'$tmp',";
	}
	chop($dma);
	$dma = " AND DMA IN ($dma)"	if ($dma);
	my ($sth3) = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE DATEDIFF('$in{'date'} 00:00:00',CONCAT(ESTDay,' 00:00:00')) BETWEEN 0 AND 7 $dma GROUP BY ESTDay,DestinationDID ORDER BY ESTDay DESC LIMIT 0,5");
	while($tmp = $sth3->fetchrow_hashref()){
		++$n;
		print qq|
			<tr class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=assign_did&id_orders=$in{'id_orders'}&did=$tmp->{'DestinationDID'}&contract=$tmp->{'ID_mediacontracts'}'); \$('.close').click(); \$('#assign_$in{'id_orders'}').html('<b>Assigned: $tmp->{'DestinationDID'}</b>');">
				<td class='smalltext'>$tmp->{'Offer'}</td>
				<td class='smalltext'>($tmp->{'DestinationDID'}) $tmp->{'Station'}</td>
				<td class='smalltext'>$tmp->{'ESTDay'} &nbsp; $tmp->{'ESTTime'}</td>
			</tr>\n|;
	}
	#######################################
	#### Contracts NATIONAL
	#######################################
	print qq|	
				<tr>
					<td align="center" colspan="3" class='smalltext'>Contracts by dma NATIONAL</td>
				</tr>\n|;
	my ($sth3) = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE DATEDIFF('$in{'date'} 00:00:00',CONCAT(ESTDay,' 00:00:00')) BETWEEN 0 AND 7 AND DMA='NACIONAL' GROUP BY ESTDay,DestinationDID ORDER BY ESTDay DESC LIMIT 0,5");
	while($tmp = $sth3->fetchrow_hashref()){
		++$n;
		print qq|
			<tr class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=assign_did&id_orders=$in{'id_orders'}&did=$tmp->{'DestinationDID'}&contract=$tmp->{'ID_mediacontracts'}'); \$('.close').click(); \$('#assign_$in{'id_orders'}').html('<b>Assigned: $tmp->{'DestinationDID'}</b>');">
				<td class='smalltext'>$tmp->{'Offer'}</td>
				<td class='smalltext'>($tmp->{'DestinationDID'}) $tmp->{'Station'}</td>
				<td class='smalltext'>$tmp->{'ESTDay'} &nbsp; $tmp->{'ESTTime'}</td>
			</tr>\n|;
	}
	#######################################
	#### Contrcts Same State
	#######################################
	print qq|	
				<tr>
					<td align="center" colspan="3" class='smalltext'>Contracts by $in{'state'}</td>
				</tr>\n|;
	#my ($sth3) = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE DATEDIFF('$in{'date'} 00:00:00',CONCAT(ESTDay,' 00:00:00')) BETWEEN 0 AND 7 AND  DMA IN (SELECT `DMA_DESC` FROM `sl_zipdma` WHERE State='".substr($in{'state'},0,2)."' AND DMA_DESC<>'' GROUP BY `DMA_DESC`) GROUP BY ESTDay,DestinationDID ORDER BY ESTDay DESC LIMIT 0,5");
	my ($sth3) = &Do_SQL("SELECT * FROM sl_mediacontracts
					INNER JOIN
					(SELECT `DMA_DESC` FROM `sl_zipdma` WHERE State='".substr($in{'state'},0,2)."' AND DMA_DESC<>'' GROUP BY `DMA_DESC`)AS tmp
					ON DMA = DMA_DESC
					WHERE DATEDIFF('$in{'date'} 00:00:00',CONCAT(ESTDay,' 00:00:00')) BETWEEN 0 AND 7
					GROUP BY DestinationDID ORDER BY ESTDay DESC LIMIT 0,5;");
	while($tmp = $sth3->fetchrow_hashref()){
		++$n;
		print qq|
			<tr class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=assign_did&id_orders=$in{'id_orders'}&did=$tmp->{'DestinationDID'}&contract=$tmp->{'ID_mediacontracts'}'); \$('.close').click(); \$('#assign_$in{'id_orders'}').html('<b>Assigned: $tmp->{'DestinationDID'}</b>');">
				<td class='smalltext'>$tmp->{'Offer'}</td>
				<td class='smalltext'>($tmp->{'DestinationDID'}) $tmp->{'Station'}</td>
				<td class='smalltext'>$tmp->{'ESTDay'} &nbsp; $tmp->{'ESTTime'}</td>
			</tr>\n|;
	}


	#######################################
	#### No Contract
	#######################################
	
	print qq|
			<tr>
				<td align="center" colspan="3" class='smalltext'>Contract Unknown</td>
			</tr>\n|;

	my ($sth4) = &Do_SQL("SELECT * FROM sl_mediacontracts WHERE DestinationDID = '9996' AND ESTDay <= '$in{'date'}' ORDER BY ESTDay DESC LIMIT 2;");
	while($tmp = $sth4->fetchrow_hashref()){
		++$n;
		print qq|
			<tr class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=assign_did&id_orders=$in{'id_orders'}&did=$tmp->{'DestinationDID'}&contract=$tmp->{'ID_mediacontracts'}'); \$('.close').click(); \$('#assign_$in{'id_orders'}').html('<b>Assigned: $tmp->{'DestinationDID'}</b>');">
				<td class='smalltext'>$tmp->{'Station'}</td>
				<td class='smalltext'>($tmp->{'DestinationDID'}) $tmp->{'Station'}</td>
				<td class='smalltext'>$tmp->{'ESTDay'} &nbsp; $tmp->{'ESTTime'}</td>
			</tr>\n|;
	}

	return ;
}


#	Function: update_mediacontracts
#   		Update via ajx field values from sl_mediacontracts records
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#		- Roberto Barcenas on 02/06/2012: Se agrega nota de edicion
#		- Roberto Barcenas on 04/03/2012: Se agrega edicion de estday esttime
#		- Roberto Barcenas on 04/09/2012: Se agrega edicion de offer
#		- Roberto Barcenas on 05/07/2012: Se agrega reseteo de goteo
#
#   	Parameters:
#		- id_mediacontracts : ID_mediacontracts
#		- field: Field name
#		- old: Field old value
#		- val: Field New Value
#
#   	Returns:
#		- ok
#		- error message
#
#   	See Also:
#
sub update_mediacontracts{

	print "Content-type: text/html\n\n";

	if(!$in{'id_mediacontracts'} or !$in{'field'} or !$in{'val'}){
		print "error = $in{'id_mediacontracts'} - $in{'field'} - $in{'val'}";
		return;
	}

	## Field updating
	my $field;
	($in{'field'} eq 'cost') and  ($field = 'Cost');
	($in{'field'} eq 'offer') and  ($field = 'Offer');
	($in{'field'} eq 'destination') and  ($field = 'Destination');


	#print "error:UPDATE sl_mediacontracts SET $field ='$in{'val'}' WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';";
	#return;

	my ($sth)=&Do_SQL("UPDATE sl_mediacontracts SET $field ='$in{'val'}' WHERE ID_mediacontracts = '$in{'id_mediacontracts'}';");
	if($sth->rows() == 1){
		$in{'db'}='sl_mediacontracts';
		$in{'cmd'}='mm_contracts';
		&auth_logging('mediacontracts_cost_updated',$in{'id_mediacontracts'});
		my ($sth) = &Do_SQL("INSERT INTO sl_mediacontracts_notes SET ID_mediacontracts='$in{'id_mediacontracts'}',Notes='$field edited\nOld:".$in{'old'}."\nNew:".$in{'val'}."',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		#print 'ok';
		print '<td class="stdtxterr">Assignado</td>';
	}else{
		print  "error:".$sth->errmsg();
	}
	return;
}


sub overlay_products_prior{
# --------------------------------------------------------
# Forms Involved: mer_products_view.html, 
# Created on: 07 Feb 2012 14:00:14
# Author: Roberto Barcenas
# Description :
# Description: Muestra formulario con datos a modificar de sl_products_prior
# Parameters :
# Last Modified 

	use HTML::Entities;
	use Data::Dumper;

	print "Content-type: text/html\n\n";

	if(!$in{'id_row'}){
		$va{'message'} .= &trans_txt('search_nomatches');
		return;
	}
		
	#valid amazon 
    $va{"disableasin"} = $in{'belongsto'} =~ /amazon/ ?  '' : "disabled='disabled'";
    $va{"disablesku"} = $in{'belongsto'} =~ /amazon/ ?  '' : "disabled='disabled'";
    
    #valid shoppingcart
    $va{"disableshop"} = lc($in{'belongsto'}) =~ /innovashop|naturaliv|naturistashop|allnatpro/ ?  '' : "disabled='disabled'";
 
 	#my $id_products_prior = int($in{'id_row'});
	my $id_products = int($in{'id_row'});

	## Datos para formulario
	$str_sql = "Select * from sl_products_prior where ID_products=$id_products AND BelongsTo='$in{'belongsto'}' ";
	#print $str_sql."<hr>";

	my $sth=&Do_SQL($str_sql);
	my $rec=$sth->fetchrow_hashref();
	foreach $key (keys %{$rec}){
		$in{lc($key)} = $rec->{$key};
	}

	#$in{'item_title'} = &load_name('sl_products_w','id_products',$in{'id_products'},'Name');

	print &build_page('func:overlay_products_prior.html');
	return;
}

sub overlay_products_prior_desc{
# --------------------------------------------------------
# Forms Involved: mer_products_view.html, 
# Created on: 20 Abr 2012 9:38:14
# Author: Pablo Hdez
# Description :
# Description: Muestra formulario con datos a modificar de sl_products_prior
# Parameters :
# Last Modified RB on 08/23/2012: Se agrego posibilidad de editar smalldescription para uso en websites lineales 

    use HTML::Entities;
    use Data::Dumper;

    print "Content-type: text/html\n\n";

    if(!$in{'id_row'}){
        $va{'message'} .= &trans_txt('search_nomatches');
        return;
    }
    #my $id_products_prior = int($in{'id_row'});
    my $id_products = int($in{'id_row'});

    ## Datos para formulario
    $str_sql = "Select * from sl_products_prior where ID_products=$id_products AND BelongsTo='$in{'belongsto'}' ";
    #print $str_sql."<hr>";

    my $sth=&Do_SQL($str_sql);
    my $rec=$sth->fetchrow_hashref();
    foreach $key (keys %{$rec}){
        $in{lc($key)} = $rec->{$key};
    }

    if($in{'belongsto'} !~ /amazon|innovashop|naturaliv|allnatpro|naturistashop/ ){
    	$in{'toolbarset'} = 'Basic';
 		$in{'toolbarheight'} = '100';

 		$va{'fckcreatehtml_sp'} = &FCKCreateHtml('smalldescription_sp_fck',$in{'smalldescription'});
 		$va{'fckcreatehtml_en'} = &FCKCreateHtml('smalldescription_en_fck',$in{'smalldescription_en'});

 		print &build_page('func:overlay_products_prior_lineal_desc.html');
    }else{
    	$va{'fckcreatehtml'} = &FCKCreateHtml('description_fck',$in{'description'});	
    	print &build_page('func:overlay_products_prior_desc.html');
    }
 
    return;
}


sub overlay_products_prior_links{
# --------------------------------------------------------
# Forms Involved: mer_products_view.html, 
# Created on: 17 Feb 2012 14:00:14
# Author: Oscar Sanchez
# Description :
# Description: Muestra formulario con datos a modificar de sl_products_prior
# Parameters :
# Last Modified 

	print "Content-type: text/html\n\n";

	if(!$in{'id_row'}){
		$va{'message'} .= &trans_txt('search_nomatches');
		return;
	}

	my $id_products = int($in{'id_row'});
	my $belongsto = $in{'belongsto'};
	my $list_name = "";

	## Datos para formulario
	my $sth=&Do_SQL("Select * from sl_products_w where ID_products=$id_products and BelongsTo='$belongsto' ");
	my $num_count = 0;
	while ($rec = $sth->fetchrow_hashref) {
	$num_count++;
	$list_name .= "<tr><td width='35%'>Name : <span class='smallfieldterr'>[er_name]</span></td>
<td class='smalltext'><input type='text' size='50' onFocus='focusOn( this )' onBlur='focusOff( this )' name='ID_products_w_$rec->{'ID_products_w'}' value='$rec->{'Name'}'></td>
<td><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_products&view=$id_products&tab=18&drop_link=$rec->{'ID_products_w'}&belongsto=$belongsto&action=1'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png'></a></td>
</tr>\n";
	}  # End while

	if ($num_count == 0){
		$list_name = "<tr style='background-color:#EEEED1;'><td width='35%'>New URL: <span class='smallfieldterr'>[er_another_name]</span></td><td class='smalltext'><input type='text' name='another_name' value='[in_another_name]' size='50' onFocus='focusOn( this )' onBlur='focusOff( this )'></td><td>&nbsp;</a></tr>";
	}

	$va{'list_name'} = $list_name;
	$in{'id_products'} = $id_products;

	print &build_page('func:overlay_products_prior_links.html');
	return;
}

sub update_ccbonus{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 27 Feb 2012 17:55:14
# Author: Pablo Hernandez
# Description :
# Description: Actualiza la formula de un grupo de ususario
# Parameters :
# Last Modified : 
	
	print "Content-type: text/html\n\n";
	
	if(!$in{'id_reward'}){
		print "error = $in{'id_reward'}";
		return;
	}
	my ($sth)=&Do_SQL("UPDATE sl_rewards SET Expression='".&filter_values($in{'val'})."' WHERE ID_reward='$in{'id_reward'}';");
	if($sth->rows() == 1){
		$in{'db'}='sl_rewards';
		$in{'cmd'}='ccbonus';
		&auth_logging('ccbonus_updated',$in{'id_reward'});
		print 'ok';
	}else{
		print  "error:".$sth->errmsg();
	}
	return;
}

sub overlay_products_prior_promo{
# --------------------------------------------------------
# Forms Involved: overlay_products_prior_promo.html, 
# Created on: 17 Jul 2012 9:00:10
# Author: Pablo Hdez. H.
# Description :
# Description: Muestra formulario con precios a modificar de sl_products_prior
# Parameters :
# Last Modified 

    use HTML::Entities;
    use Data::Dumper;

    print "Content-type: text/html\n\n";

    if(!$in{'id_row'}){
        $va{'message'} .= &trans_txt('search_nomatches');
        return;
    }
       
    my $id_products = int($in{'id_row'});

    ## Datos para formulario
    $str_sql = "Select * from sl_products_prior where ID_products=$id_products AND BelongsTo='$in{'belongsto'}' ";

    my $sth=&Do_SQL($str_sql);
    my $rec=$sth->fetchrow_hashref();
    foreach $key (keys %{$rec}){
        $in{lc($key)} = $rec->{$key};
    }
     
    print &build_page('func:overlay_products_prior_promo.html');
    return;
}

sub report_quickchg{
# --------------------------------------------------------
# Forms Involved: overlay_products_prior_promo.html, 
# Created on: 17 Jul 2012 9:00:10
# Author: Pablo Hdez. H.
# Description :
# Description: Muestra formulario con precios a modificar de sl_products_prior
# Parameters :
# Last Modified 


    print "Content-type: text/html\n\n";

       
	my (@ary) = split (/,/,$in{'glist'});
	
	print qq|<table border="0" cellspacing="0" cellpadding="4" width="120" class="formtable">
			<tr>
				<td class="menu_bar_title" colspan="2">|.&trans_txt('groupby').qq|</td>
			</tr>\n|;
	my ($url) = $in{'url'};
	$url =~ s/groupby=/groupbyold=/;
	for (0..$#ary){
		print "			<tr>\n";
		print qq|	
		<tr>
			<td colspan="2" class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/admin?$url&groupby=$ary[$_]');">
				$ary[$_]
			</td>
		</tr>\n|;
	}
	if ($in{'url'} =~ /=ASC/){
		$in{'url'} =~ s/=ASC/=DESC/;
		print qq|	
			<tr>
				<td class="smalltext"><font color="red">ASC</font></td>
				<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/admin?$in{'url'}');">DESC</td>
			</tr>\n|;
	}elsif($in{'url'} =~ /=DESC/){
		$in{'url'} =~ s/=DESC/=ASC/;
		print qq|	
			<tr>
				<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/admin?$in{'url'}');">ASC</td>
				<td class="smalltext"><font color="red">DESC</font></td>
			</tr>\n|;
	}else{
		print qq|	
			<tr>
				<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/admin?$in{'url'}&sortorder=ASC');">ASC</td>
				<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="trjump('/cgi-bin/mod/$usr{'application'}/admin?$in{'url'}&sortorder=DESC');">DESC</td>
			</tr>\n|;
	}
	print "</table> ";
    return;
}


############################################################################################
############################################################################################
#	Function: assign_leads_flash
#   		Update via ajax ID_admin_users filed value from sl_flash_leads table
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By: None
#
#   Parameters:
#		- id_flash_leads : ID_flash_leads
#		- old: Old Admin user
#		- new: New Admin User Assigned
#
#   	Returns:
#		- ok
#		- error message
#
#   	See Also:
#
sub assign_leads_flash{
############################################################################################
############################################################################################

	print "Content-type: text/html\n\n";

	if(!$in{'id_leads_flash'} or !$in{'old'} or !$in{'new'}){
		print "error = $in{'id_leads_flash'} - $in{'old'} - $in{'new'}";
		return;
	}

	$in{'new'} =~ /^(\d+)/;
	$in{'new'} = $1;
	$in{'old'} =~ /^(\d+)/;
	$in{'old'} = $1;

	#print "error:UPDATE sl_leads_flash SET ID_admin_users ='$in{'new'}' WHERE ID_leads_flash = '$in{'id_leads_flash'}';";
	#return;
	my $old_agent = &load_db_names('admin_users','ID_admin_users',$in{'old'},'[FirstName] [LastName]');
	my $new_agent = &load_db_names('admin_users','ID_admin_users',$in{'new'},'[FirstName] [LastName]');

	my ($sth)=&Do_SQL("UPDATE sl_leads_flash SET ID_admin_users ='$in{'new'}' WHERE ID_leads_flash = '$in{'id_leads_flash'}';");
	if($sth->rows() == 1){
		$in{'db'}='sl_leads_flash';
		$in{'cmd'}='leads_flash';
		&auth_logging('leadsflash_admin_assigned',$in{'id_leads_flash'});
		my ($sth) = &Do_SQL("INSERT INTO sl_leads_flash_notes SET ID_leads_flash='$in{'id_leads_flash'}',Type='AssignedTo',Notes='Old:". $old_agent . "(". $in{'old'}.")\nNew:". $new_agent ."(".$in{'new'}.")',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		print 'ok';
	}else{
		print  "error:".$sth->errmsg();
	}
	return;
}


############################################################################################
############################################################################################
#	Function: update_packing_globalexport
#   		Show via ajax orders by pay type
#
#	Created by:
#		_Pablo Hdez_
#
#	Modified By: None
#
#   Parameters:
#		- export_order : 1
#	
#   	Returns:
#		- html 
#		- error message
#
#   	See Also:
#
sub update_packing_globalexport{
############################################################################################
############################################################################################
	print "Content-type: text/html\n\n";
    
	if(!$in{'id_orders'} or !$in{'id_warehouses_batches'} ){
		print "error = $in{'id_orders'} - $in{'id_warehouses_batches'}";
		return;
	}
    my $status_changed = '';
	### Insert warehouses_batches Orders 
	my $Query = "SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders = '".&filter_values($in{'id_orders'})."';";
	 
	my ($sth) = &Do_SQL($Query);
	while ($rec = $sth->fetchrow_hashref){
		$Query = "SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products=$rec->{'ID_orders_products'} AND Status IN('In Fulfillment','Error');";
		
		($sth2) = &Do_SQL($Query);
		($count)=$sth2->fetchrow_array();
		if($count == 0 ){
			$Query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'}).", ID_orders_products=".int($rec->{'ID_orders_products'}).", Status='In Fulfillment', Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'; ";
			($sth3) = &Do_SQL($Query);
			$status_changed='add';
		}elsif($count > 0 ){
			$Query = "DELETE FROM sl_warehouses_batches_orders WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'})." AND ID_orders_products=".int($rec->{'ID_orders_products'})."; ";
			($sth4) = &Do_SQL($Query);
			$status_changed='droped';
		}					
	}
	
	my $Query = "SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=".&filter_values($in{'id_orders'}).";";
	my ($sth) = &Do_SQL($Query);
	if($sth->fetchrow>0){
	    $in{'db'}='sl_warehouses_batches';
		$in{'cmd'}='update_packing_globalexport';
		&auth_logging('warehouses_batches_orders_item_'.$status_changed,$in{'id_warehouses_batches'});
		my ($sth5) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET ID_warehouses_batches='$in{'id_warehouses_batches'}',Notes='item $status_changed:".&filter_values($in{'id_orders'})."',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		print 'ok';
	}else{
		print  "error:".$DBI::errstr;
	}

	## Nota y Log para orden asignada
	$in{'db'} = 'sl_orders';
	## Nota orden enviada en batch			
	&add_order_notes_by_type($in{'id_orders'},&trans_txt('order_batchdropped'),"High");
	&auth_logging('order_batchdropped', $in{'id_orders'});

	return;
}


############################################################################################
############################################################################################
#	Function: chg_warehouse_batch
#   		Change the batch orders owmer
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		- id_warehouses_batches : ID_warehouses_batches
#		- old: Field old value
#		- new: Field New Value
#
#   	Returns:
#		- ok
#		- error message
#
#   	See Also:
#
sub chg_warehouse_batch{
############################################################################################
############################################################################################

	print "Content-type: text/html\n\n";

	if(!$in{'id_batch'} or !$in{'old'} or !$in{'new'}){
		print "error = $in{'id_batch'} - $in{'old'} - $in{'new'}";
		return;
	}
	
	### New Batch
 	my $new = $in{'new'};
	my($id_new_batch) = &create_warehouse_batch_file($new);


	if(!$id_new_batch){
		print "Error",
		return;
	}

	## Old Batch got orders?
	my ($sth)=&Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_warehouses_batches = '$in{'id_batch'}';");
	my($total) = $sth->fetchrow();

	if($total){
		my ($sth)=&Do_SQL("UPDATE sl_warehouses_batches_orders SET ID_warehouses_batches ='$id_new_batch' WHERE ID_warehouses_batches = '$in{'id_batch'}';");
		if($sth->rows() > 0){
			$in{'db'}='sl_warehouses_batches';
			$in{'cmd'}='warehouses_batches';
			my ($sth)=&Do_SQL("UPDATE sl_warehouses_batches SET Status ='Assigned' WHERE ID_warehouses_batches = '$id_new_batch';");
			&auth_logging('batch_orders_changed',$in{'id_warehouses_batches'});
			my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET ID_warehouses_batches='$in{'id_batch'}',Notes='Warehouse Changed\nOld:".$in{'old'}."\nNew:".$in{'new'}."',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			print $id_new_batch;
		}else{
			print  "error:".$sth->errmsg();
		}
	}else{
		print $id_new_batch;
	}	
	return;
}

#############################################################################
#############################################################################
# Function: load_orders_filtered
#
# Es: carga las ordenes filtradas por zona y con opcion de seleccionarlas con un checkbox.
# En: orders filtered by load zone and select option with a checkbox.
#
# Created on: 26/12/2012 05:55:00
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
# - id_zone: ID de la zona
#
# Returns:
#
# - output : grid de orders
#
# See Also:
#
#  Todo:
#
sub load_orders_filtered {
#############################################################################
#############################################################################

	my($id_zones) = int($in{'id_zones'});
	#$zones =~ s/\|/\,/g;
	my($id_warehouses) = int($in{'id_warehouses'});

	$va{'output'} = '';
	my ($registers) = 0;
	my ($add_sql) = '';
	my ($ptype) = $in{'ptype'};
	my ($from_date) = $in{'from_date'};
	my ($to_date) = $in{'to_date'};

	$add_sql = " AND sl_orders.Ptype='COD'";
	$add_sql .= ($id_zones and $id_zones != 0)?" AND sl_orders.ID_zones = ".$id_zones." ":" AND sl_orders.ID_zones != 0 AND sl_orders.ID_zones IS NOT NULL";
	$add_sql .= ($from_date and $from_date ne '')?" AND sl_orders.Date >='".$from_date."'":'';
	$add_sql .= ($to_date and $to_date ne '')?" AND sl_orders.Date <='".$to_date."'":'';

	#------------------------------------------------------------
	my ($sql) = "SELECT sl_orders_products.ID_products, sl_orders_products.ID_orders, PaymentsCOD, PaymentsNotCOD, sl_orders.Date, sl_orders.shp_Zip, sl_orders.shp_City, sl_orders.shp_State, sl_orders.shp_Country, sl_orders.ID_warehouses, sl_zones.Name as Zone
	FROM sl_orders_products
	INNER JOIN sl_orders ON (sl_orders_products.ID_orders=sl_orders.ID_orders)	
	INNER JOIN (SELECT ID_orders,sum(if(Type='COD',1,0))as PaymentsCOD,sum(if(Type!='COD',1,0))as PaymentsNotCOD FROM sl_orders_payments GROUP BY ID_orders HAVING PaymentsCOD>0) AS tempo ON (tempo.ID_orders=sl_orders.ID_orders)
	LEFT JOIN (SELECT sl_orders.ID_orders FROM sl_orders 
		INNER JOIN sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
		INNER JOIN sl_warehouses_batches_orders ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		WHERE sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
		GROUP BY sl_orders.ID_orders )AS tmp ON (tmp.ID_orders=sl_orders.ID_orders)
	INNER JOIN sl_zones ON(sl_orders.ID_zones=sl_zones.ID_zones)
	WHERE 1=1 $add_sql
	/*AND tmp.ID_orders IS NULL*/
	AND sl_orders_products.ID_products not like '6%' 
	AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
	AND (isnull(Tracking) or Tracking='')
	AND (isnull(ShpProvider) or ShpProvider='')
	AND shp_type=$cfg{'codshptype'}
	AND sl_orders.Status='Processed'
	AND StatusPrd='In Fulfillment'
	AND sl_orders_products.Status = 'Active'
	AND sl_orders_products.SalePrice > 0
	AND sl_orders_products.Quantity > 0
	AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')
	GROUP BY sl_orders_products.ID_orders";
	#------------------------------------------------------------	
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $page_limit = '';
	my ($sth) = &Do_SQL("$sql");
	$va{'matches'} = $sth->rows;
	if ($va{'matches'} > 0){				
		(!$in{'nh'}) and ($in{'nh'} = 1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'}, $qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/ajaxbuild", $va{'matches'}, $usr{'pref_maxh'});
		
		$page_limit = " LIMIT $first,$usr{'pref_maxh'}";

		my (@c) = split(/,/,$cfg{'srcolors'});
	}
	$sth = &Do_SQL("$sql $page_limit");

	$va{'output'} .= '
	<table border="0" cellspacing="0" cellpadding="2" width="100%">
		<tr>
		    <td class="tbltextttl">Orders : '.$va{'matches'}.'</td>
		    <td align="right" class="tbltextttl">Pages: '.$va{'pageslist'}.'</td>
		</tr>
    </table>
	<table border="0" cellspacing="0" cellpadding="4" width="100%" class="container_white">
		<tr class="menu_bar_title">
			<th width="5%" align="center"><input type="checkbox" class="selectall" typed="checkbox_orders" /></th>
			<th width="10%" align="center">Order ID</th>
			<th width="15%" align="center">Date</th>
			<th width="10%" align="center">Zip</th>
			<th width="15%" align="center">City</th>
			<th width="15%" align="center">State</th>
			<th width="10%" align="center">Zone</th>
			<th width="20%" align="center">Warehouse</th>
		</tr>';

	$color = '#ffffff';
    while ($rec = $sth->fetchrow_hashref) {
    	my $warehouse_name = &load_name('sl_warehouses','ID_warehouses',$rec->{'ID_warehouses'},'Name');

	    $va{'output'} .= '
	    <tr onmouseover="m_over(this)" onmouseout="m_out(this)" bgcolor="'.$color.'" >
			<td align="center"><input type="checkbox" name="checkbox_orders" value="'.$rec->{'ID_orders'}.'" class="checkbox_orders"></td>
			<td align="left">'.$rec->{'ID_orders'}.'</td>
			<td align="center">'.$rec->{'Date'}.'</td>
			<td align="center">'.$rec->{'shp_Zip'}.'</td>
			<td align="left">'.$rec->{'shp_City'}.'</td>
			<td align="left">'.$rec->{'shp_State'}.'</td>
			<td align="left">'.$rec->{'Zone'}.'</td>
			<td align="left">'.$warehouse_name.'</td>
		</tr>';
		if($color eq '#ffffff') { $color = '#f2f2f2'; }else { $color = '#ffffff'; }
	
		$registers++;
	}

	if($registers == 0) {
		$va{'output'} .= '
	    <tr>
			<td colspan="7" align="center">'.&trans_txt('notmatch').'</td>
		</tr>';
	}

	$va{'output'} .= '
	</table>
	<script>
	<!--
	$(document).ready(function() {
		$(".selectall").click(function () {
			if($(this).attr("checked")) {
				$("input.checkbox_orders").attr("checked","checked"); 	
			}else {
				$("input.checkbox_orders").removeAttr("checked"); 	
			}
			
	    });
	});
	-->
	</script>
	';

	print "Content-type: text/html\n\n";
	print $va{'output'};

}

#############################################################################
#############################################################################
# Function: load_warehouses_filteredword
#
# Es: carga las almacenes existentes y con opcion de seleccionarlas con un checkbox.
# En: existing loading warehouses and select option with a checkbox.
#
# Created on: 11/12/2012 10:33:00
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
# - 
#
# Returns:
#
# - output : grid de warehouse encontrados
#
# See Also:
#
#  Todo:
#
sub load_warehouses_filteredword {
#############################################################################
#############################################################################

	$va{'output'} = '';
	my ($registers) = 0;
	my($id_zones) = int($in{'id_zones'});
	if($id_zones == 0) { $id_zones = -1; }
	#$zones =~ s/\|/\,/g;

	my ($add_sql) = '';
	$add_sql .= ($id_zones and $id_zones != 0)?" AND ID_zones = ".$id_zones." ":" AND ID_zones IS NOT NULL AND ID_zones != 0";
	my ($sql) = "
	SELECT w.ID_warehouses, w.Name, w.Type, z.Name as Zone,
	(SELECT count(*)
	FROM sl_orders 
	INNER JOIN sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
	WHERE 1=1
		AND sl_orders_products.ID_products not like '6%' 
		AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
		AND (isnull(Tracking) or Tracking='')
		AND (isnull(ShpProvider) or ShpProvider='')
		AND shp_type=$cfg{'codshptype'}
		AND sl_orders.Status='Processed'
		AND StatusPrd='In Fulfillment'
		AND sl_orders_products.Status = 'Active'
		AND sl_orders_products.SalePrice > 0
		AND sl_orders_products.Quantity > 0
		AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')
	AND (`ID_warehouses` IS NULL OR `ID_warehouses` = 0)
	AND sl_orders.ID_zones=zw.ID_zones)as orderscovered,
	(SELECT count(*)
	FROM sl_orders 
	INNER JOIN sl_orders_products ON sl_orders_products.ID_orders=sl_orders.ID_orders
	WHERE 1=1
		AND sl_orders_products.ID_products not like '6%' 
		AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
		AND (isnull(Tracking) or Tracking='')
		AND (isnull(ShpProvider) or ShpProvider='')
		AND shp_type=$cfg{'codshptype'}
		AND sl_orders.Status='Processed'
		AND StatusPrd='In Fulfillment'
		AND sl_orders_products.Status = 'Active'
		AND sl_orders_products.SalePrice > 0
		AND sl_orders_products.Quantity > 0
		AND sl_orders.Status not in ('Shipped','Void', 'Cancelled','System Error')
	AND `ID_warehouses` = w.ID_warehouses
	AND sl_orders.ID_zones=zw.ID_zones)as ordersassigned
	FROM sl_warehouses w
	INNER JOIN sl_zones_warehouses zw USING(ID_warehouses)
	INNER JOIN sl_zones z USING(ID_zones)
	WHERE w.Status='Active' $add_sql
	AND Type IN('Virtual','Outsource')
	ORDER BY Name";
	# - - - - - - - - - - - -- - - - - -- - - - 
	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	my $page_limit = '';
	my ($sth) = &Do_SQL("$sql");
	$va{'matches'} = $sth->rows;
	if ($va{'matches'} > 0){				
		(!$in{'nh'}) and ($in{'nh'} = 1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'}, $qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/ajaxbuild", $va{'matches'}, $usr{'pref_maxh'});
		
		if ($in{'print'}){
			$page_limit = '';
			print "Content-type: text/html\n\n";			
			print &build_page('header_print.html');

		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";

		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
	}
	$sth = &Do_SQL("$sql $page_limit");
	#- - - - - - - - - - - - - - - - - - - -
	
	$va{'output'} .= '
	<table border="0" cellspacing="0" cellpadding="2" width="100%">
		<tr>
		    <td class="tbltextttl">Warehouses : '.$va{'matches'}.'</td>
		    <td align="right" class="tbltextttl">Pages: '.$va{'pageslist'}.'</td>
		</tr>
    </table>
	<table border="0" cellspacing="0" cellpadding="4" width="100%" class="container_white">
		<tr class="menu_bar_title">
			<th></th>
			<th></th>
			<th></th>
			<th></th>
			<th></th>
			<th colspan="2">Orders</th>
			<th></th>
    	</tr>
		<tr class="menu_bar_title">
			<th align="center"></th>
			<th align="center">ID warehouse</th>
			<th align="center">Name</th>
			<th align="center">Type</th>
			<th align="center">Zone</th>
			<th align="center">Covered</th>
 			<th align="center">Assigned</th>
 			<th align="center"></th>
		</tr>';

	$color = '#ffffff';
    while ($rec = $sth->fetchrow_hashref) {
	    $va{'output'} .= '
	    <tr onmouseover="m_over(this)" onmouseout="m_out(this)" bgcolor="'.$color.'" >
			<td width="5%" align="center"><input type="radio" name="id_warehouses" value="'.$rec->{'ID_warehouses'}.'" class="checkbox_warehouses"></td>
			<td width="10%" align="left">'.$rec->{'ID_warehouses'}.'</td>
			<td width="20%" align="left">'.$rec->{'Name'}.'</td>
			<td width="20%" align="left">'.$rec->{'Type'}.'</td>
			<td width="10%" align="left">'.$rec->{'Zone'}.'</td>
			<td width="10%" align="center">'.$rec->{'orderscovered'}.'</td>
			<td width="10%" align="center">'.$rec->{'ordersassigned'}.'</td>
			<td width="15%" align="center">';
			if($rec->{'ordersassigned'} and int($rec->{'ordersassigned'}) > 0) {
				$va{'output'} .= '
				<a href="javascript:prnwin(\'/cgi-bin/mod/'.$usr{'application'}.'/admin?cmd='.$in{'cmd'}.'&action=1&printinvoices=invoices&id_warehouses='.$rec->{'ID_warehouses'}.'\')">
					<img src="'.$va{'imgurl'}.'/'.$usr{'pref_style'}.'/b_print.png" title="print invoices" alt="print invoices" width="15" height="15" border="0">
				</a>';

				$va{'output'} .= '
				<a href="/cgi-bin/mod/'.$usr{'application'}.'/admin?cmd='.$in{'cmd'}.'&action=1&export=endicia&id_warehouses='.$rec->{'ID_warehouses'}.'">
					<img src="'.$va{'imgurl'}.'/'.$usr{'pref_style'}.'/b_xls.gif" title="export" alt="export" width="15" height="15" border="0">
				</a>';

				$va{'output'} .= '
				<a href="/cgi-bin/mod/'.$usr{'application'}.'/admin?cmd=cod_orderstobatch&action=1&export=global&id_warehouses='.$rec->{'ID_warehouses'}.'" title="assign batches" alt="assign batches">Assign Batches</a>';				
			}
		$va{'output'} .= '
			</td>
		</tr>';
		if($color eq '#ffffff') { $color = '#f2f2f2'; }else { $color = '#ffffff'; }
	
		$registers++;
	}
	if($registers == 0) {
		$va{'output'} .= '
	    <tr>
			<td colspan="4" align="center">'.&trans_txt('notmatch').'</td>
		</tr>';
	}

	$va{'output'} .= '
	</table>';

	print "Content-type: text/html\n\n";
	print $va{'output'};

}

sub load_warehouses_filtered {
#############################################################################
#############################################################################

	$va{'output'} = '';
	my ($registers) = 0;
	my($zones) = $in{'id_zones'};
	$zones =~ s/\|/\,/g;

	my ($add_sql) = '';
	my ($whrestrict) = int($in{'whrestrict'});
	#$add_sql .= ($zones and $zones ne '' and $whrestrict and $whrestrict == 1)?" AND ID_zones IN (".$zones.")":'';
	$add_sql .= ($zones and $zones ne '')?" AND ID_zones IN (".$zones.")":'';
	my ($sql) = "SELECT w.ID_warehouses, w.Name, w.Type 
	FROM sl_warehouses w";
	$sql .= ($whrestrict and $whrestrict == 1)?" INNER JOIN ":" LEFT JOIN ";
	$sql .= " sl_zones_warehouses zw USING(ID_warehouses) WHERE w.Status='Active' 
	$add_sql
	AND Type IN('Virtual','Outsource')
	ORDER BY Name";

	my ($sth) = &Do_SQL($sql);

	$va{'output'} .= '
	<table border="0" cellspacing="0" cellpadding="4" width="100%" class="container_white">
		<tr>
			<th></th>
			<th></th>
			<th></th>
			<th></th>
			<th></th>
			<th colspan="2">Orders</th>
    	</tr>
		<tr class="menu_bar_title">
			<th align="center"></th>
			<th align="center">ID warehouse</th>
			<th align="center">Name</th>
			<th align="center">Type</th>
			<th align="center">Zone</th>
			<th align="center">Covered</th>
 			<th align="center">Assigned</th>
		</tr>';

	$color = '#ffffff';
    while ($rec = $sth->fetchrow_hashref) {
	    $va{'output'} .= '
	    <tr onmouseover="m_over(this)" onmouseout="m_out(this)" bgcolor="'.$color.'" >
			<td width="10%" align="center"><input type="radio" name="id_warehouses" value="'.$rec->{'ID_warehouses'}.'" class="checkbox_warehouses"></td>
			<td width="10%" align="left">'.$rec->{'ID_warehouses'}.'</td>
			<td width="30%" align="left">'.$rec->{'Name'}.'</td>
			<td width="20%" align="left">'.$rec->{'Type'}.'</td>

			<td width="10%" align="left">'.$rec->{'Zone'}.'</td>
			<td width="10%" align="left">'.$rec->{'orderscovered'}.'</td>
			<td width="10%" align="left">'.$rec->{'ordersassigned'}.'</td>
		</tr>';
		if($color eq '#ffffff') { $color = '#f2f2f2'; }else { $color = '#ffffff'; }
	
		$registers++;
	}
	if($registers == 0) {
		$va{'output'} .= '
	    <tr>
			<td colspan="4" align="center">'.&trans_txt('notmatch').'</td>
		</tr>';
	}

	$va{'output'} .= '
	</table>';

	print "Content-type: text/html\n\n";
	print $va{'output'};

}

#############################################################################
#############################################################################
# Function: overlay_customers_address
#
# Es: Carga formulario para agregar/editar direcciones de clientes.
# En: Load to add/edit customer addresses.
#
# Created on: 25/02/2012 10:33:00
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub overlay_customers_address {
#############################################################################
#############################################################################

	use HTML::Entities;
	use Data::Dumper;

	print "Content-type: text/html\n\n";

	my $id_customers_addresses = $in{'id_row'} ? int($in{'id_row'}) : 0;

	if($id_customers_addresses) {

		## Datos para formulario
		$str_sql = "SELECT * FROM cu_customers_addresses WHERE ID_customers_addresses = '$id_customers_addresses';";

		my $sth=&Do_SQL($str_sql);
		my $rec=$sth->fetchrow_hashref();
		foreach $key (keys %{$rec}){
			$in{'ca_'.lc($key)} = $rec->{$key};
			$str .= 'ca_'.lc($key) . " = " . $rec->{$key} . "<br>";
		}
		#&cgierr($str);
		$in{'id_customers_addresses'} = $rec->{'ID_customers_addresses'};
		$in{'id_customers'} = $rec->{'ID_customers'};
	}
	$in{'ca_country'} = 'MEXICO' if !$in{'ca_country'};
	$in{'ca_primaryrecord'} = 'No' if !$in{'ca_primaryrecord'};

	print &build_page('func:overlay_customers_address.html');
	return;
}


#############################################################################
#############################################################################
# Function: overlay_customers_parts
#
# Es: Carga formulario para agregar/editar SKUs especificos de clientes.
# En: Load to add/edit customer SKU codes.
#
# Created on: 25/02/2012 10:33:00
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub overlay_customers_parts {
#############################################################################
#############################################################################

	use HTML::Entities;
	use Data::Dumper;

	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$in{'id_row'}){
		
		print &build_page('func:overlay_customers_parts_add.html');

	}else {
		my $id_customers_parts = int($in{'id_row'});

		## Datos para formulario
		$str_sql = "select * from sl_customers_parts INNER JOIN sl_parts using(id_parts) where ID_customers_parts=$id_customers_parts";

		my $sth=&Do_SQL($str_sql);
		my $rec=$sth->fetchrow_hashref();
		foreach $key (keys %{$rec}){
			$in{'new_'.lc($key)} = $rec->{$key};
		}
		
		$in{'id_customers_parts'} = $rec->{'ID_customers_parts'};
		$in{'id_customers'} = $rec->{'ID_customers'};
		$in{'tags_parts'} = $rec->{'Name'};

		print &build_page('func:overlay_customers_parts.html');
	}

	return;
}

sub data_customers_parts {
# --------------------------------------------------------
	my $output='';
	if(int($in{'id_customers'})>0) {

		my ($sth) = &Do_SQL("SELECT * FROM sl_parts WHERE Status='Active' AND ID_parts NOT IN(SELECT id_parts FROM sl_customers_parts WHERE ID_customers='".$in{'id_customers'}."')");
		while ($rec = $sth->fetchrow_hashref()){
			$output .= '"'.$rec->{'ID_parts'}.'||'.$rec->{'Name'}.'",';

		}
	}
	chop($output);

	return $output;
}

#########################################################################################
#########################################################################################
#   Function: edit_bills_pos
#
#   Es: Edita el monto de los bill_pos
#
#   Created on: 19/02/2013  19:11
#
#   Author: Enrique Pe�a
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
sub edit_bills_pos {
#########################################################################################
#########################################################################################
	print "Content-type: text/html\n\n";
	my $tab = ( $in{'id_po_adj'} ) ? 8 : 1;
	$tab = 9 if( $in{'id_po_item'} );
	$va{'script_url'} = $in{'script_url'};
	$va{'hiddenfields'} = qq|
	<input type="hidden" name="cmd" value="[in_cmd]">
	<input type="hidden" name="tab" value="$tab">
	<input type="hidden" name="view" value="[in_id_bills]">
	<input type="hidden" name="updateinfo" value="1">
	<input type="hidden" name="id_po" value="[in_id_po]">
	<input type="hidden" name="id_po_adj" value="[in_id_po_adj]">
	<input type="hidden" name="id_po_item" value="[in_id_po_item]">
	<input type="hidden" name="id_bills_pos" value="[in_id_bills_pos]">
	<input type="hidden" name="id_purchaseorders" value="[in_id_purchaseorders]">
	<input type="hidden" name="nh" value="[in_nh]">\n|;
	
	&load_cfg('sl_bills_pos');
	@headerfields = ($db_cols[3]);
	@titlefields  = ($db_cols[3]);
	%rec = &get_record('ID_bills_pos',$in{'id_bills_pos'},'sl_bills_pos');
	$va{'this_amt'} = ($rec{'amount'} > 0 and !$in{'id_po_item'}) ? round($rec{'amount'},2) : round($in{'amtdue'},2);
	#&cgierr($in{'amtdue'});

	#$va{'searchform'} = &html_record_form (&get_record('ID_bills_pos',$in{'id_bills_pos'},'sl_bills_pos'));
	#[va_searchform]

	print &build_page('func:overlay_bills_pos_amount.html');
}

#########################################################################################
#########################################################################################
#   Function: edit_bills_applies
#
#   Es: Edita el monto de los bill_pos
#
#   Created on: 19/02/2013  19:11
#
#   Author: Enrique Pe�a
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
sub edit_bills_applies {
#########################################################################################
#########################################################################################
	print "Content-type: text/html\n\n";
	
	$va{'script_url'} = $in{'script_url'};
	$va{'hiddenfields'} = qq|
	<input type="hidden" name="cmd" value="[in_cmd]">
	<input type="hidden" name="tab" value="3">
	<input type="hidden" name="view" value="[in_id_bills]">
	<input type="hidden" name="up_amount" value="1">
	<input type="hidden" name="bill_use"  value="[in_bill_use]">
	<input type="hidden" name="vendor"  value="[in_idvendor]">
	<input type="hidden" name="id_bills_apps" value="[in_id_bills_apps]">\n|;
	
	&load_cfg('sl_bills_applies');
	@headerfields = ($db_cols[3]);
	@titlefields  = ($db_cols[3]);
	$va{'searchform'} = &html_record_form (&get_record('ID_bills_applies',$in{'in_id_bills_apps'},'sl_bills_applies'));

	print &build_page('forms:general_form.html');
}


#############################################################################
#############################################################################
# Function: locations_from_warehouse
#
# Es: 
# En: 
#
# Created on: 17/04/2013 10:33:00
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub locations_from_warehouse {
#############################################################################
#############################################################################
	my $id_warehouses = $in{'id_warehouses'};
	my $id_select = $in{'id_select'};
	my $name_select = $in{'name_select'};
	my $output='';

	$output .= '<select name="'.$name_select.'" id="'.$id_select.'" onfocus="focusOn( this )" onblur="focusOff( this )">';
	$output .= &build_select_locations($id_warehouses);	
	$output .= '</select>';

	print "Content-type: text/html\n\n";
	print $output;
}

#############################################################################
#############################################################################
# Function: exchange_rate
#
# Es: Obtiene el Tipo de cambio de Dolar del Diario Oficial de la Federacion guardado en Direksys
# En: 
#
# Created on: 06/06/2013
#
# Author: Alejandro Diaz
#
# Modifications:
#
# Parameters:
#
#
# Returns:Return the current Dolar Exchange Rate 
#
#
# See Also:
#
#  Todo:
#
sub exchange_rate {
#############################################################################
#############################################################################
	my ($sth) = &Do_SQL("SELECT exchange_rate FROM sl_exchangerates WHERE Date=CURDATE();");
	my $output = $sth->fetchrow_array();

	print "Content-type: text/html\n\n";
	print $output;
}

#############################################################################
#############################################################################
# Function: exchange_rate
#
# Es: Extrae el tipo de cambio de Dolar del Diario Oficial de la Federacion
# En: 
#
# Created on: 02/05/2013 05:33:00
#
# Author: Alejandro Diaz
#
# Modifications: 06/06/2013
#
# Parameters:
#
#
# Returns:Return the current Dolar Exchange Rate 
#
#
# See Also:
#
#  Todo:
#
sub exchange_rate_dof {
#############################################################################
#############################################################################
	use XML::Simple;
	use LWP::UserAgent;
	use Data::Dumper;

	my $ua = new LWP::UserAgent;
	my $response = $ua->get('http://www.dof.gob.mx/indicadores.xml');
	my $xmlString = $response->content; 

	my $ref = XMLin($xmlString);
	my $exchange_rate = $ref->{channel}->{item}->[0]->{description};

	print "Content-type: text/html\n\n";
	print $exchange_rate;
}

#############################################################################
#############################################################################
# Function: banks_movs_accounts_details
#
# Es: Obtiene los detalles de una cuenta y crea una linea html
# En: 
#
# Created on: 04/07/2013
#
# Author: EO
#
# Modifications:
#
# Parameters:
#
#
# Returns:Account details
#
#
# See Also:
#
#  Todo:
#
sub banks_movs_accounts_details {
#############################################################################
#############################################################################
	my $id_accounts = &filter_values($in{'id_accounts'});
	my $amount = &filter_values($in{'amount'});
	my ($sth) = &Do_SQL("SELECT Name, Description, ID_accounting FROM sl_accounts WHERE ID_accounts='$id_accounts';");
	#my $output = $sth->fetchrow_array();
	my ($name,$description,$id_accounting) = $sth->fetchrow();
	my $output = qq|
		<tr>
			<td align="center"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0' style="cursor:pointer;"  name="img_drop_acc" onclick="drop_acc(this);" /></td>
			<td align="center">$name</td>
			<td align="center">$description</td>
			<td align="center">
				$amount
				<input type="hidden" name="acc_amount" value="$amount" />
				<input type="hidden" name="acc_id_accounts" value="$id_accounts" />		
			</td>
		</tr>|;
		
	if (!$name) {
		$output = '';
	}
	
	print "Content-type: text/html\n\n";
	print $output;
}


#############################################################################
#############################################################################
#   Function: zones_edit
#
#       Es: Actualiza la tabla sl_zones
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#       - id = id_zones
#		- field = Payment_Type
#		- val = String with values
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_zones>
#
sub zones_edit {
#############################################################################
#############################################################################

	my $id_zones = int($in{'id'});
	my $field = &filter_values($in{'field'});
	my $vals = &filter_values($in{'val'});
	

	print "Content-type: text/html\n\n";

	if(!$id_zones or !$field or !$vals){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}

	my $query = "UPDATE sl_zones SET $field = '$vals' WHERE ID_zones = '$id_zones';";
	my ($sth) = &Do_SQL($query);
	my $t = $sth->rows();

	if($t > 0){
		$in{'db'} = "sl_zones";
		&auth_logging('zones_pm_updated',$id_zones);
		print "ok";
	}

	return;
}

#############################################################################
#############################################################################
#   Function: get_address_by_zc
#
#       Es: Obtiene la colonia y estado en base al código postal
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       - Zip Code = zip_code
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub get_address_by_zc {
#############################################################################
#############################################################################

	my $zip_code = &filter_values($in{'zip_code'});
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$zip_code){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}
	
	my $query_count = "SELECT COUNT(*) FROM sl_zipcodes WHERE ZipCode = '$zip_code';";
	my ($sth_count) = &Do_SQL($query_count);
	my $num_rows = $sth_count->fetchrow();
	
	if ($num_rows > 0) {
		
		
		
		my $query = "SELECT ID_zipcodes, State, StateFullName, City, CountyName FROM sl_zipcodes WHERE ZipCode = '$zip_code';";
		my ($sth) = &Do_SQL($query);
		
		if ($in{'type'} and $in{'type'} eq 'get_num_results') {
			print $num_rows;
			return;
		}
		if ($in{'type'} and $in{'type'} eq 'get_result') {
			$rec = $sth->fetchrow_hashref();
			print "$rec->{'CountyName'}|$rec->{'City'}|$rec->{'StateFullName'}";
			return;
		}
		
		#my ($results) = $sth->fetchrow_hashref();
		my $table = qq|<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
							<tbody>
								<tr>
									 <td class="menu_bar_title">CP</td>
									 <td class="menu_bar_title"></td>
									 <td class="menu_bar_title"></td>
									 <td class="menu_bar_title"></td>
									 <td class="menu_bar_title">Colonia</td>
									 <td class="menu_bar_title">Municipio</td>
									 <td class="menu_bar_title">Estado</td>
								</tr>|;
		while ($rec = $sth->fetchrow_hashref()) {
			$table .= qq|
							<tr bgcolor="#ffffff" onmouseover="m_over(this)" onmouseout="m_out(this)" style="" onclick="javascript:get_address_data(this);">
								<td><img src="$va{'imgurl'}/$usr{'pref_style'}/tri.gif" border="0" />$zip_code <input type="hidden" value="$zip_code" name="zip_code_aux" /> </td>
								<td>&nbsp;</td>
								<td>&nbsp;</td>
								<td>&nbsp;</td>
								<td>$rec->{'CountyName'} <input type="hidden" value="$rec->{'CountyName'}" name="county_name_aux" /></td>
								<td>$rec->{'City'} <input type="hidden" value="$rec->{'City'}" name="city_aux" /></td>
								<td class="smalltext">
									$rec->{'StateFullName'} <input type="hidden" value="$rec->{'StateFullName'}" name="state_full_name_aux" />
								</td>
							</tr>|;
		}
		$table .= qq|		<tr>
								<td class="smalltext" colspan="7"></td>
							</tr>
						</tbody>
					</table>|;
		print $table;
		
	} else {
		print "Error";
	}
	return;
}

#############################################################################
#############################################################################
#   Function: get_state_zc
#
#       Es: Obtiene el estado
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       - State = state_name
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub get_state_zc {
#############################################################################
#############################################################################
	use Encode;
	use URI::Escape;
	my $state_name = &filter_values(Encode::decode('UTF8',uri_unescape($in{'state_name'})));
	$state_name = Encode::encode("iso-8859-1",$state_name);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$state_name){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}
	
	my $query_count = "SELECT COUNT(*) FROM sl_zipcodes WHERE StateFullName LIKE '%$state_name%' OR State LIKE '%$state_name%';";
	my ($sth_count) = &Do_SQL($query_count);
	my $num_rows = $sth_count->fetchrow();
	
	if ($num_rows > 0) {
		my $query = "SELECT DISTINCT StateFullName FROM sl_zipcodes WHERE StateFullName LIKE '%$state_name%' OR State LIKE '%$state_name%';";
		my ($sth) = &Do_SQL($query);
		my $js_array = '';
		while ($rec = $sth->fetchrow_hashref()) {
			$js_array .= qq|"$rec->{'StateFullName'}",|;
		}
		$js_array =~ s/\,+$//g;
		print '['.$js_array.']';
		return;
	} else {
		print "Error";
	}
	return;
}

#############################################################################
#############################################################################
#   Function: get_city_zc
#
#       Es: Obtiene el estado
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       - State = state_name
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub get_city_zc {
#############################################################################
#############################################################################
	use Encode;
	use URI::Escape;
	
	my $state_name = &filter_values(Encode::decode('UTF8',$in{'state_name'}));
	my $city_name = &filter_values(Encode::decode('UTF8',$in{'city_name'}));
	$state_name = Encode::encode("iso-8859-1",$state_name);
	$city_name = Encode::encode("iso-8859-1",$city_name);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$state_name){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}
	
	my $query_count = "SELECT COUNT(*) FROM sl_zipcodes WHERE StateFullName = '$state_name' AND City LIKE '%$city_name%';";
	my ($sth_count) = &Do_SQL($query_count);
	my $num_rows = $sth_count->fetchrow();
	
	if ($num_rows > 0) {
		my $query = "SELECT DISTINCT City FROM sl_zipcodes WHERE StateFullName = '$state_name' AND City LIKE '%$city_name%';";
		my ($sth) = &Do_SQL($query);
		my $js_array = '';
		while ($rec = $sth->fetchrow_hashref()) {
			$js_array .= qq|"$rec->{'City'}",|;
		}
		$js_array =~ s/\,+$//g;
		print '['.$js_array.']';
		return;
	} else {
		print "Error";
	}
	return;
}

#############################################################################
#############################################################################
#   Function: get_urbanization_zc
#
#       Es: Obtiene el estado
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       - State = state_name
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub get_urbanization_zc {
#############################################################################
#############################################################################
	use Encode;
	use URI::Escape;
	my $state_name = &filter_values(Encode::decode('UTF8',$in{'state_name'}));
	my $city_name = &filter_values(Encode::decode('UTF8', uri_unescape($in{'city_name'})));
	my $county_name = &filter_values(Encode::decode('UTF8',$in{'urbanization_name'}));
	$state_name=Encode::encode("iso-8859-1",$state_name);
	$city_name=Encode::encode("iso-8859-1",$city_name);
	$county_name=Encode::encode("iso-8859-1",$county_name);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$state_name){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}
	
	
	my $query_count = "SELECT COUNT(*) FROM sl_zipcodes WHERE StateFullName = '$state_name' AND City = '$city_name' AND CountyName LIKE '%$county_name%';";
	my ($sth_count) = &Do_SQL($query_count);
	my $num_rows = $sth_count->fetchrow();
	
	if ($num_rows > 0) {
		my $query = "SELECT DISTINCT CountyName FROM sl_zipcodes WHERE StateFullName = '$state_name' AND City = '$city_name' AND CountyName LIKE '%$county_name%';";
		my ($sth) = &Do_SQL($query);
		my $js_array = '';
		while ($rec = $sth->fetchrow_hashref()) {
			$js_array .= qq|"$rec->{'CountyName'}",|;
		}
		$js_array =~ s/\,+$//g;
		print '['.$js_array.']';
		return;
	} else {
		print "Error";
	}
	return;
}

#############################################################################
#############################################################################
#   Function: get_zc_by_address
#
#       Es: Obtiene el estado
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       - State = state_name
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub get_zc_by_address {
#############################################################################
#############################################################################
	use Encode;
	use URI::Escape;
	my $state_name = &filter_values(Encode::decode('UTF8',$in{'state_name'}));
	my $city_name = &filter_values(Encode::decode('UTF8', uri_unescape($in{'city_name'})));
	my $county_name = &filter_values(Encode::decode('UTF8',$in{'urbanization_name'}));
	$state_name=Encode::encode("iso-8859-1",$state_name);
	$city_name=Encode::encode("iso-8859-1",$city_name);
	$county_name=Encode::encode("iso-8859-1",$county_name);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$state_name){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}
	
	
	my $query_count = "SELECT COUNT(*) FROM sl_zipcodes WHERE StateFullName = '$state_name' AND City = '$city_name' AND CountyName = '$county_name';";
	my ($sth_count) = &Do_SQL($query_count);
	my $num_rows = $sth_count->fetchrow();
	
	if ($num_rows > 0) {
		my $query = "SELECT * FROM sl_zipcodes WHERE StateFullName = '$state_name' AND City = '$city_name' AND CountyName = '$county_name';";
		my ($sth) = &Do_SQL($query);
		
		my $table = qq|<table border="0" cellspacing="0" cellpadding="4" width="100%" class="formtable">
							<tbody>
								<tr>
									 <td class="menu_bar_title">CP</td>
									 <td class="menu_bar_title"></td>
									 <td class="menu_bar_title"></td>
									 <td class="menu_bar_title"></td>
									 <td class="menu_bar_title">Colonia</td>
									 <td class="menu_bar_title">Municipio</td>
									 <td class="menu_bar_title">Estado</td>
								</tr>|;
		
		
		while ($rec = $sth->fetchrow_hashref()) {
			$table .= qq|
							<tr bgcolor="#ffffff" onmouseover="m_over(this)" onmouseout="m_out(this)" style="" onclick="javascript:get_address_data(this);">
								<td><img src="[va_imgurl]/[ur_pref_style]/tri.gif" border="0" />$rec->{'ZipCode'} <input type="hidden" value="$rec->{'ZipCode'}" name="zip_code_aux" /> </td>
								<td>&nbsp;</td>
								<td>&nbsp;</td>
								<td>&nbsp;</td>
								<td>$rec->{'CountyName'} <input type="hidden" value="$rec->{'CountyName'}" name="county_name_aux" /></td>
								<td>$rec->{'City'} <input type="hidden" value="$rec->{'City'}" name="city_aux" /></td>
								<td class="smalltext">
									$rec->{'StateFullName'} <input type="hidden" value="$rec->{'StateFullName'}" name="state_full_name_aux" />
								</td>
							</tr>|;
		}
		$table .= qq|		<tr>
								<td class="smalltext" colspan="7"></td>
							</tr>
						</tbody>
					</table>|;
		print $table;
		return;
	} else {
		print "Error";
	}
	return;
}

#############################################################################
#############################################################################
#   Function: get_locations
#
#       Es: Obtiene el estado
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       - State = state_name
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub get_locations {
#############################################################################
#############################################################################
	use Encode;
	use URI::Escape;
	my $back_to_wh = &filter_values(Encode::decode('UTF8',uri_unescape($in{'back_to_wh'})));
	$back_to_wh = Encode::encode("iso-8859-1",$back_to_wh);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";

	if(!$back_to_wh){
		print "Error: " .&trans_txt('reqfields_short');
		return;
	}
	
	my $query_count = "SELECT COUNT(*) FROM sl_locations WHERE ID_warehouses = '$back_to_wh';";
	my ($sth_count) = &Do_SQL($query_count);
	my $num_rows = $sth_count->fetchrow();
	
	if ($num_rows > 0) {
		my $query = "SELECT TRIM(Code)AS Code FROM sl_locations WHERE ID_warehouses = '$back_to_wh';";
		my ($sth) = &Do_SQL($query);
		my $js_array = '';
		while ($rec = $sth->fetchrow_hashref()) {
			$js_array .= qq|<option value="$rec->{'Code'}">$rec->{'Code'}</option>\n|;
		}
		$js_array =~ s/\,+$//g;
		print $js_array;
		return;
	} else {
		print "Error";
	}
	return;
}

#############################################################################
#############################################################################
#   Function: update_invoicedata
#
#       Es: 
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _EO_
#
#    Modifications:
#
#   Parameters:
#
#       -  = 
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub update_invoicedata{
	print "Content-type: text/html\n\n";

	if(!$in{'id_invoices'} or !$in{'field'} or !$in{'val'}){
		print "error = $in{'id_invoices'} - $in{'field'} - $in{'val'}";
		return;
	}

	my $field = ucfirst($in{'field'});
	$in{'val'} =~ s/\(|\)|-| //g;

	my ($sth)=&Do_SQL("UPDATE cu_invoices SET $field ='".&filter_values($in{'val'})."' WHERE ID_invoices = '$in{'id_invoices'}' LIMIT 1;");
	if($sth->rows() == 1){
		$in{'db'}='cu_invoices';
		$in{'cmd'}='cuinvoices';
		&auth_logging('cuinvoices_updated',$in{'id_invoices'});
		my ($sth) = &Do_SQL("INSERT INTO cu_invoices_notes SET ID_invoices='$in{'id_invoices'}',Notes='$field edited',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		print 'ok';
	}else{
		print  "error:".$sth->errmsg();
	}
	return;
}


#############################################################################
#############################################################################
#   Function: overlay_warehouses_batches_products
#
#       Es: Muestra Tabla de productos en una orden que han estado en alguna otra remesa y su status
#       En: 
#
#
#    Created on: 09/25/2013  16:20:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#       - id_orders = state_name
#		- id_warehouses_batches
#		
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
#	<>
#
sub overlay_warehouses_batches_products {
#############################################################################
#############################################################################

	use HTML::Entities;
	use Data::Dumper;

	print "Content-type: text/html\n\n";

	if(!$in{'ido'} or !$in{'idwb'}){
		$va{'message'} .= &trans_txt('search_nomatches');
		return;
	}

	my $this_batch = int($in{'idwb'});
	my $id_orders = int($in{'ido'});
	my $flag = 0;
	my (@c) = split(/,/,$cfg{'srcolors'});
		
	my ($sth) = &Do_SQL("SELECT
							 sl_orders_products.ID_orders_products,
							sl_orders_products.ID_products,
							Related_ID_products,
							sl_products.Name,
							sl_services.Name,
							sl_parts.Name,
							ID_warehouses_batches,
							sl_warehouses_batches_orders.Status,
							sl_warehouses_batches_orders.Date
		 				FROM `sl_orders_products` 
						INNER JOIN sl_warehouses_batches_orders 
						USING(ID_orders_products)
						LEFT JOIN sl_products ON RIGHT(sl_orders_products.ID_products,6) = sl_products.ID_products
						LEFT JOIN sl_services ON sl_orders_products.ID_products - 600000000 = ID_services
						LEFT JOIN sl_parts ON Related_ID_products - 400000000 = ID_parts
						WHERE ID_orders = '$id_orders' AND LEFT(sl_orders_products.ID_products,1) <> 6
						ORDER BY ID_warehouses_batches,sl_orders_products.ID_orders_products;");

	while(my ($idop,$id_products, $id_related, $pname, $sname, $skname, $idwb, $rst, $rdate) = $sth->fetchrow() ){

		if($flag < $idwb ) { $d = 1 - $d; $flag = $idwb; }
		my $this_style = $flag == $this_batch ? qq|class="smalltext"| : '';

		($id_related > 0 and substr($id_products,-6) eq '000000') and ($id_products = $id_related);
		($sname ne '') and ($pname = $sname);
		($skname ne '') and ($pname = $skname);

		$va{'searchform'} .= qq|<tr bgcolor='$c[$d]' onmouseout="m_out(this)" onmouseover="m_over(this)" $this_style>\n
									<td nowrap>|. &format_sltvid($id_products) .qq|</td>\n
									<td>$idop</td>\n
									<td>$pname</td>\n
									<td>$idwb</td>\n
									<td nowrap>$rdate</td>\n
									<td align="right" nowrap>$rst</td>\n
								</tr>|;



	}


	

	print &build_page('func:overlay_warehouses_batches_products.html');
	return;
}

sub EnterShipmentAjax{
# --------------------------------------------------------
# Created on: 17 Apr 2014 11:44:14
# Author: Arturo Hernandez
# Description :
# Parameters :
	use JSON;
	print "Content-type: text/html\n\n";
	my @json ;
	if($in{'line'} == 1){	
		$json{'line'} = 1;
		if ($in{'lastline'} =~ /^$cfg{'prefixentershipment'}(\d+)/i){
			$id_orders = $1;
			if(&check_batches($id_orders)){
				$local_delivery_sql = $in{'localdelivery'} ? ' AND Ptype="COD"': ' AND (Ptype="Credit-Card" OR Ptype="Referenced Deposit")';
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders=". $id_orders ." AND Status = 'Processed' $local_delivery_sql;");
					if ($sth->fetchrow==0){
						$id_orders = 0;
						$json{'error'} = 'yes';
						$json{'message'} = trans_txt('entershipment_scan_order_unknown');
					}else{
						$json{'error'} = 'no';
						$json{'status'} = 'getOrder';
						$json{'lineProcess'} = $in{'line'};
						$json{'order'} = $id_orders;
						my ($sth2) = &Do_SQL("SELECT Address1, Address2, Address3, Urbanization, City, State, Zip, Country FROM sl_orders WHERE ID_orders = ". $id_orders .";");
						my ($rec) = $sth2->fetchrow_hashref;
						$json{'address'} = $rec->{'Address1'}.' '.$rec->{'Urbanization'}.' '.$rec->{'City'}.' '.$rec->{'State'}.' '.$rec->{'Zip'};
						my ($sthz) = &Do_SQL("SELECT CONCAT('(', sl_zones.ID_zones,') ', sl_zones.Name) FROM sl_orders INNER JOIN sl_zones ON sl_orders.ID_zones = sl_zones.ID_zones WHERE ID_orders = ". $id_orders .";");
						$json{'zone'} = $sthz->fetchrow();
						my ($sth3)=&Do_SQL("SELECT * FROM sl_vars WHERE VName='Auth Order' AND VValue LIKE '$id_orders,%'");
						my ($rec3) = $sth3->fetchrow_hashref;
						my (@parts) = split(/,/,$rec3->{'VValue'});
						$json{'authcode'} = $parts[2];
						my ($sth4)=&Do_SQL("SELECT
							sl_warehouses.Name,
							sl_warehouses_batches_orders.ID_warehouses_batches
							from sl_orders_products 
							left join sl_warehouses_batches_orders 
								on sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
							INNER JOIN sl_warehouses_batches
								ON sl_warehouses_batches_orders.ID_warehouses_batches = sl_warehouses_batches.ID_warehouses_batches
							INNER JOIN sl_warehouses
								ON sl_warehouses_batches.ID_warehouses = sl_warehouses.ID_warehouses
							WHERE sl_warehouses_batches_orders.Status='In Fulfillment'
							AND sl_orders_products.ID_orders='$id_orders'
							GROUP BY sl_warehouses_batches_orders.ID_warehouses_batches");
						my ($rec4) = $sth4->fetchrow_hashref;
						$json{'warehouses_batches'} = $rec4->{'ID_warehouses_batches'};
						$json{'name_driver'} = $rec4->{'Name'};
						
						my ($z) = 0;
						my ($sth) = &Do_SQL("SELECT sl_skus.ID_sku_products, sl_skus.UPC, sl_skus_parts.ID_parts, sl_parts.Name, sl_skus_parts.Qty
											FROM sl_skus_parts
											INNER JOIN sl_skus 
												ON sl_skus.ID_products = sl_skus_parts.ID_parts  AND sl_skus.ID_sku_products = 400000000+sl_skus_parts.ID_parts
											INNER JOIN sl_orders_products
												ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products
											INNER JOIN sl_parts
												ON sl_parts.ID_parts = sl_skus_parts.ID_parts
											WHERE sl_orders_products.ID_orders = '$id_orders'
											AND sl_orders_products.Status = 'Active'
											ORDER BY sl_skus.UPC");
						while (my($sku,$upc, $ID_sku, $name, $qty) = $sth->fetchrow()){
						for my $i(1..$qty){
							if($lastupc eq $upc){
								$json{'items'}{($ID_sku.$z.$i)}{'list'} = $lastlist + 1;
							}else{
								$json{'items'}{($ID_sku.$z.$i)}{'list'} = 1;
							}
							$json{'items'}{($ID_sku.$z.$i)}{'upc'} = $upc;
							$json{'items'}{$ID_sku.$z.$i}{'sku'} = $sku;
							$json{'items'}{$ID_sku.$z.$i}{'name'} = $name;
							$lastupc = $upc;
							$lastlist = $json{'items'}{($ID_sku.$z.$i)}{'list'};
							$z++;
						}
								
						}
						$json{'totalItem'} = $z;
					}
			}else{
				$json{'error'} = 'yes';
				$json{'message'} = trans_txt('entershipment_scan_order_invalid_status');
			}
		}else{
			$json{'error'} = 'yes';
			$json{'message'} = trans_txt('entershipment_scan_order_invalid_status');
		}
	}elsif($in{'line'} == 2){
		$json{'line'} = 2;
		if($in{'lastline'} =~ /\b(1Z ?[0-9A-Z]{3} ?[0-9A-Z]{3} ?[0-9A-Z]{2} ?[0-9A-Z]{4} ?[0-9A-Z]{3} ?[0-9A-Z]|[\dT]\d\d\d ?\d\d\d\d ?\d\d\d)\b/i){
			$json{'shippment'} = 'ups';
		}elsif($in{'lastline'} =~ /(\b\d{34}\b)/){
			$json{'shippment'} = 'fedex';
		}elsif($in{'lastline'} =~ /(\b\d{22}\b)/){
			$json{'shippment'} = 'estafeta';
		}elsif($in{'lastline'} =~ /DRIVER/i){
			$json{'shippment'} = 'DRIVER';
		}else{
			$json{'error'} = 'yes';
			$json{'message'} = trans_txt('entershipment_scan_order_unknown_tracking');
		}
	} 
	elsif($in{'line'} >= 3){
		if($cfg{'submit_code'} eq lc($in{'lastline'})){
			if($cfg{'enter_shippment_full'}){
				$json{'enter_shippment_full'} = $cfg{'enter_shippment_full'};
			}
			$json{'submit'} = 'yes';
		}
		$json{'line'} = 3;
		$json{'entershipment_scan_order_noupc'} = trans_txt('entershipment_scan_order_noupc');
		#my ($sth5) = &Do_SQL("INSERT INTO sl_entershipments (ID_orders, Input, Status, Date, Time, ID_admin_users) VALUES ('$in{id_order}', '$in{trackingtxt}', 'error', CURDATE(), NOW(), 1)");
	}
	
	my $json = encode_json \%json;
	print "$json\n";
	return;
}
#############################################################################
#############################################################################
#   Function: validaterefnum
#
#       Es: Valida el cutom ref de un movimiento bancario
#       En: 
#    Created on: 30/05/2014  16:20:10
#    Author: Arturo Hernandez
#    Modifications:
#   Parameters:
#		
#  Returns:
#      - Error/string with data
sub validaterefnum{
##############################################################################
	print "Content-type: text/html\n\n";
	my ($sth2) = &Do_SQL("SELECT COUNT(*) 
						FROM sl_banks_movements 
						WHERE 1 AND Type = 'Credits' 
						AND ID_banks = '".&filter_values($in{'id_banks'})."'
						AND BankDate = '".&filter_values($in{'bankdate'})."'
						AND doc_type = '".&filter_values($in{'doc_type'})."'
						AND RefNumCustom = '".&filter_values($in{'ref'})."'");
	my ($duplicate) = $sth2->fetchrow_array();
	if($duplicate == 0){
		print 'pass';
	}else{
		print 'fail'
	}
	return;
}
#############################################################################
#############################################################################
#   Function: fastCheckOrder
#
#       Es: Busqueda rapida de Pedidos 
#       En: 
#    Created on: 05/06/2014  16:20:10
#    Author: Arturo Hernandez
#    Modifications:
#   Parameters:
#		
#  Returns:
#      - Error/string with data
sub fastCheckOrder{
#####################################################################
#####################################################################

	print "Content-type: text/html\n\n";
	print '<meta http-equiv="Content-Type" content="text/html;charset=iso-8859-1" />';

	my ($idOrder) = $in{'id_orders'};
	$in{'id_orders'} = $idOrder;

	#####
	##### Se agrega reestriccion para mostrar solo Orders de Canales de Venta que el usuario tenga asignados.
	#####
	$add_sql = "";
	if ($usr{'application'} eq 'crm' and $cfg{'use_salesorigins_restriction'} and $cfg{'use_salesorigins_restriction'}==1 and $usr{'id_salesorigins_view'} ne ''){
		
		$in{'only_records_by_salesorigins'} = $usr{'id_salesorigins_view'};
		$in{'only_records_by_salesorigins'} =~ s/\|/\,/g;
		$add_sql = " AND ID_salesorigins IN ($in{'only_records_by_salesorigins'});"
	}
	
	$sql = "SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$in{'id_orders'}' $add_sql";
	my $sth = &Do_SQL($sql);
	$view_orders_validation = $sth->fetchrow_array();
	
	if ($in{'id_orders'} and $view_orders_validation){

		my ($sth) = Do_SQL("SELECT 
			sl_orders.ID_orders,
			sl_orders.shp_name,
			sl_orders.shp_Address1,
			sl_orders.shp_Address2,
			sl_orders.shp_Address3,
			sl_orders.shp_Urbanization,
			sl_orders.shp_City,
			sl_orders.shp_State,
			sl_orders.shp_Zip,
			sl_orders.shp_Country,
			sl_orders.shp_Notes,
			sl_orders.OrderTax,
			sl_orders.OrderNet,
			sl_orders.ID_salesorigins,
			sl_orders.Ptype,
			sl_orders.Status,
			sl_customers.Phone1,
			sl_customers.Phone2,
			sl_customers.Cellphone,
			sl_customers.Email,
			sl_orders.Date,
			sl_orders.OrderShp,
			sl_customers.FirstName,
			sl_customers.LastName1,
			sl_customers.LastName2,
			sl_orders.StatusPrd,
			sl_orders.StatusPay
			FROM sl_orders 
			INNER JOIN sl_customers ON (sl_orders.ID_customers = sl_customers.ID_customers)
			WHERE sl_orders.ID_orders = '$idOrder';");

		my $rec = $sth->fetchrow_hashref;
		if ($rec->{'ID_orders'}){

			$va{'iderror'} .= 'display:none;';
			$va{'idok'} .= '';
			$va{'total'} =  &format_price(&total_orders_products($idOrder));
			$va{'customer_name'} = $rec->{'FirstName'}.' '.$rec->{'LastName1'}.' '.$rec->{'LastName2'};
			$va{'shp_name'} = $rec->{'shp_name'};
			$va{'orderdate'} = $rec->{'Date'};
			$va{'id_order'} = $rec->{'ID_orders'};
			$va{'sales_name'} = uc &load_db_names('admin_users', 'ID_admin_users', $rec->{'ID_admin_users'}, '[FirstName] [LastName]');
			$va{'address1'} = $rec->{'shp_Address1'};
			$va{'address2'} = $rec->{'shp_Address2'};
			$va{'address3'} = $rec->{'shp_Address3'};
			$va{'urbanization'} = $rec->{'shp_Urbanization'};
			$va{'city'} = $rec->{'shp_City'};
			$va{'state'} = $rec->{'shp_State'};
			$va{'country'} = $rec->{'shp_Country'};
			$va{'notes'} = $rec->{'shp_Notes'};
			$va{'zip'} = $rec->{'shp_Zip'};
			$va{'phone1'} = $rec->{'Phone1'};
			$va{'phone2'} = $rec->{'Phone2'};
			$va{'cellphone'} = $rec->{'Cellphone'};
			$va{'email'} = $rec->{'Email'};
			$va{'salesorigins'} = uc &load_db_names('sl_salesorigins', 'ID_salesorigins', $rec->{'ID_salesorigins'}, '[Channel]');
			$va{'ptype'} = $rec->{'Ptype'};
			$va{'status'} = $rec->{'Status'};
			$va{'application'} = $usr{'application'};
			$va{'statusprd'} = $rec->{'StatusPrd'};
			$va{'statuspay'} = $rec->{'StatusPay'};

			if( $in{'e'} == 4)
			{
				$sql_amazon = "	
								UNION
									SELECT * FROM 
									(
										SELECT 
											sl_skus.ID_sku_products, sl_skus.UPC, '' ID_parts, cu_products_amazon.name, sl_orders_products.Quantity
										FROM 
											(SELECT * FROM sl_orders_products WHERE ID_orders = '$rec->{'ID_orders'}') sl_orders_products
											INNER JOIN sl_skus ON sl_orders_products.related_id_products = sl_skus.ID_sku_products
											INNER JOIN cu_products_amazon ON sl_orders_products.amazon_id_products = cu_products_amazon.ID_products_amazon
										ORDER BY sl_skus.UPC
									) amazon ";
			}


			my ($sth2) = Do_SQL("
								SELECT * FROM 
								(
									SELECT 
										sl_skus.ID_sku_products, sl_skus.UPC, sl_skus_parts.ID_parts, sl_parts.Name, sl_skus_parts.Qty
									FROM 
										sl_skus_parts
										INNER JOIN sl_skus ON sl_skus.ID_products = sl_skus_parts.ID_parts
										INNER JOIN sl_orders_products ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products
										INNER JOIN sl_parts ON sl_parts.ID_parts = sl_skus_parts.ID_parts
									WHERE 
										sl_orders_products.ID_orders = '$rec->{'ID_orders'}' AND sl_orders_products.Status NOT IN('Order Cancelled', 'Inactive') 
									ORDER BY sl_skus.UPC
								) general
								$sql_amazon;");


			$va{'listproducts'} .= '<table id="resultproducts" cellpadding="0" cellspacing="0" width="100%">
										<tr>
											<td class="menu_bar_title" align="center">Cantidad</td>
											<td class="menu_bar_title" align="center">Nombre</td>
											<td class="menu_bar_title" align="center">SKU</td>
										</tr>';
			while(my($sku,$upc, $ID_sku, $name, $qty) = $sth2->fetchrow()){
				
				$va{'listproducts'} .= '<tr>
				<td align="center">'.$qty.'</td>
				<td align="left">'.$name.'</td>
				<td align="center">'.$sku.'</td>
				</tr>';
			}

			my ($sth4) = &Do_SQL("SELECT  Notes, Type, Date, Time, ID_admin_users FROM sl_orders_notes WHERE ID_orders = '$idOrder' ORDER by Date DESC, Time DESC LIMIT 5");
			$va{'noteslist'} .= '<table id="noteslist" style=";" cellpadding="0" cellspacing="0" width="100%">
									<tr>
										<td class="menu_bar_title" align="center">Date/Time/</td>
										<td class="menu_bar_title" align="center">Type</td>
										<td class="menu_bar_title" align="center">Notes</td>
									</tr>';

			while(my($notes, $type, $date, $time, $user) = $sth4->fetchrow()){
				$username = &load_db_names('admin_users', 'ID_admin_users', $user, '[FirstName] [LastName]');
				my ($res) = $j % 2;
				$color = ($res == 0) ? '#fff' : '#f2f2f2';
				$va{'noteslist'} .= '
				<tr style="background:'.$color.';height:30px;">
					<td><b>'.$date.' / '.$time.'<br>('.$user.') '.$username.'</b></td>
					<td><b>'.$type.'</b></td>
					<td><b>'.$notes.'</b></td>
				</tr>
				';
				$j++;
			}

			$va{'noteslist'} .= '</table>';
			$va{'listproducts'} .= '</table>';
			my ($sth3) = &Do_SQL("select * from sl_orders_payments where ID_orders = '$rec->{'ID_orders'}' AND Captured = 'Yes' AND CapDate != '0000-00-00' AND  CapDate IS NOT NULL");
			my $rec2 = $sth3->fetchrow_hashref;
			$va{'capdate'} = $rec2->{'CapDate'};

			## Log
			$in{'db'} = 'sl_orders';
			&auth_logging2('opr_orders_viewed_fast',$in{'id_orders'});

			&run_sp_users() if lc($rec->{'Ptype'}) eq 'cod';

		}else{
			$va{'iderror'} .= '';
			$va{'idok'} .= 'display:none;';
		}

		if( $va{'id_order'} ne '')
		{
			$in{'id_orders'} = $va{'id_order'};
		}

		$risk = &show_risk_orders();
	}else{
			$va{'iderror'} .= '';
			$va{'idok'} .= 'display:none;';
			$va{'errormsg'} .= (!$view_orders_validation)? &trans_txt('unauth_action'):$in{'id_orders'}.": ".&trans_txt('notmatch');
	}
	print &build_page('fastcheckorder.html');
	return;
}


#############################################################################
#############################################################################
#   Function: searchUser
#
#       Es: Busqueda de Usuarios 
#       En: 
#    Created on: 17/06/2014  16:20:10
#    Author: Arturo Hernandez
#    Modifications:
#   Parameters:
#		
#  Returns:
#      - Error/string with data
sub searchUser{
#############################################################################
#############################################################################

	my $sth = &Do_SQL("SELECT ID_admin_users, UPPER(CONCAT(FirstName, ' ', LastName)) AS FullName, LOWER(Email)Email, LOWER(Username)Username FROM admin_users WHERE Status='Active' AND (CONCAT(FirstName, ' ', LastName) like '".$in{'q'}."%' OR Username like '".$in{'q'}."%');");
	my %result;
	while(my($id_admin_users, $FullName, $Email, $Username) = $sth->fetchrow){
		$json .= qq|{"name":"$FullName ($Username)","id":"$id_admin_users"},|;

	}
	chop ($json);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";
	print "[$json]\n";
}

#############################################################################
#############################################################################
#   Function: searchUser
#       Es: Busqueda de Grupos de Usuarios
#       En: 
#    Created on: 08/07/2016  11:59 AM
#    Author: ISC Alejandro Diaz
#    Modifications:
#    Parameters:
#		
#    Returns:
#      - Error/string with data
sub search_group{
#############################################################################
#############################################################################

	my $sth = &Do_SQL("SELECT ID_admin_groups, UPPER(Name)Name FROM admin_groups WHERE Status='Active' AND Name like '".$in{'q'}."%';");
	my %result;
	while(my($id_admin_groups, $name) = $sth->fetchrow){
		$json .= qq|{"name":"$name (ID $id_admin_groups)","id":"$id_admin_groups"},|;
	}
	chop ($json);
	
	print "Content-type: text/html; charset=ISO-8859-1\n\n";
	print "[$json]\n";
}

#############################################################################
#############################################################################
# Function: users_by_type
#
# Es: 
# En: 
#
# Created on: 22/12/2014 12:26:00
#
# Author: Huitzilihuitl Ceja
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub users_by_type {
#############################################################################
#############################################################################
	my $users_type = $in{'users_type'};
	my $id_select = $in{'id_select'};
	my $name_select = $in{'name_select'};
	my $id_user = $in{'id_user'};
	my $output='';
	my $selected = '';


	my $sth = &Do_SQL("SELECT ID_admin_users,CONCAT(FirstName, ' ', LastName) AS FullName FROM admin_users WHERE user_type = '$users_type' AND `Status`='Active';");

	$output .= '<select name="'.$name_select.'">';
	while( my($id_admin_users, $FullName) = $sth->fetchrow ){
		$FullName = encode_entities($FullName);
		$selected = '';
		
		if( $id_user eq $id_admin_users ){ 
			$selected = "selected"; 
		}

		$output .= "<option value='$id_admin_users' $selected>$FullName</option>";
	}
	$output .= '</select>';

	print "Content-type: text/html\n\n";
	print $output;
}


#############################################################################
#############################################################################
# Function: ajax_info_cupon
#
# Es: Muestra información respecto al Cupon especificado
# En: 
#
# Created on: 26/08/15 02:00 AM
#
# Author: Huitzilihuitl Ceja
#
# Modifications: 29-01-2016 Se incluye el campo applied para mostrar su valor (Net / Gross)
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub ajax_info_cupon{
#############################################################################
#############################################################################

	print "Content-type: text/html\n\n";
	my $sth=&Do_SQL("SELECT * FROM sl_coupons WHERE PublicID ='$in{'cupon'}'");
	my $rec = $sth->fetchrow_hashref;

	if($rec->{'Name'}){

		$va{'name'}				= $rec->{'Name'};
		$va{'public_id'}		= $rec->{'PublicID'};
		$va{'company'} 			= $rec->{'Type'};
		$va{'applied'}			= $rec->{'Applied'};
		$va{'validfrom'}		= $rec->{'ValidFrom'};
		$va{'validto'} 			= $rec->{'ValidTo'};
		$va{'discount'} 		= ($rec->{'DiscPerc'}) ?  $rec->{'DiscPerc'}.'%' : &format_price($rec->{'DiscValue'});
		$va{'max_per_cust'} 	= $rec->{'MaxPerCust'};
		$va{'max_per_zip'} 		= $rec->{'MaxPerZip'};
		$va{'max_per_state'}	= $rec->{'MaxPerState'};
		$va{'min_amount'} 		= $rec->{'MinAmount'};

		print &build_page("info_cupon.html");
	}else{
		print "Invalid or missing coupon";
	}

}


#############################################################################
#############################################################################
# Function: usr_admin_tree
#
# Es: Regresa Nombre de Id Admin User y Valida
# En: 
#
# Created on: 15/04/16 
#
# Author: Fabián Cañaveral
#
# Modifications: 
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub usr_admin_tree{
#############################################################################
#############################################################################
	use JSON;
	my %response;
	print "Content-type: application/json\n\n";
	if($in{'type'} eq 'get'){
		my $where = "and id_admin_users = $in{'id_admin_users'} or id_admin_users2 = $in{'id_admin_users'} or id_admin_users3 = $in{'id_admin_users'}";
		if($in{'pos'} == 2){
			$where = "and id_admin_users = $in{'id_admin_users'} or id_admin_users3 = $in{'id_admin_users'}";
		}elsif($in{'pos'} == 3){
			$where = "and id_admin_users = $in{'id_admin_users'} or id_admin_users2 = $in{'id_admin_users'}";
		}
		my $val = &Do_SQL("select count(*) from cu_admin_users_tree where 1 $where ")->fetchrow();
		if($val > 0){
			$response{'code'}=500;
			$response{'error'}=trans_txt('error_user_have_register');
		}else{
			$response{'code'}=200;
			$response{'msg'}= &Do_SQL("select upper(concat(FirstName, ' ', LastName, ' ', MiddleName)) fullname from admin_users where status='Active' and id_admin_users = $in{'id_admin_users'}")->fetchrow();
			if($in{'pos'} == 2){
				$response{'id3'}= &Do_SQL("select id_admin_users3 from cu_admin_users_tree where id_admin_users2=$in{'id_admin_users'} limit 1")->fetchrow();
			}
			if($response{'msg'} eq ''){
				$response{'code'}=500;
				$response{'error'}=trans_txt('error_user_doest_exist');
			}
		}
		print encode_json \%response;
		return;
	}
	if($in{'type'} eq 'save'){
		&Do_SQL("INSERT INTO cu_admin_users_tree values($in{'id_admin1'},$in{'id_admin2'},$in{'id_admin3'})");
		&Do_SQL("UPDATE cu_admin_users_tree SET ID_admin_users2 = $in{'id_admin2'}, ID_admin_users3 = $in{'id_admin3'} WHERE ID_admin_users = $in{'id_admin1'};");
		$response{'code'}=200;
		print encode_json \%response;
		return;
	}
	if($in{'type'} eq 'delete'){
		&Do_SQL("delete from cu_admin_users_tree where id_admin_users=$in{'id_admin_users'} and id_admin_users2=$in{'id_admin_users2'} and id_admin_users3=$in{'id_admin_users3'}");
		$response{'code'}=200;
		print encode_json \%response;
		return;	
	}

	$response{'code'}=500;
	$response{'error'}='';
	print encode_json \%response;
	return;
}


#############################################################################
#############################################################################
#   Function: check_diestel_points
#
#       Es: Obtiene Disponible de Puntos Santander
#
#
#    Created on: 03/06/2016
#
#    Author: Fabian Cañaveral
#    Modifications:
#
#        -
#
#   Parameters:
#
#       -
#
#   See Also:
#
sub check_diestel_points {
#############################################################################
#############################################################################

	print "Content-type: application/json\n\n";
	if($cfg{'use_points'} and $cfg{'use_points'} == 1 ){
	$url = "$cfg{'url_points_ws'}?creditcard=$in{'creditcard'}&cvc=$in{'cvc'}&date=$in{'date'}&type=getPoints&e=$in{'e'}";
	print &load_webpage($url);
		return;
	}
	print '{code:500, msg: "diestel_points_disabled"}';

}

#############################################################################
#############################################################################
# Function: click_tocall
#
# Es: Genera txt para asterix
# En: 
#
# Created on: 13/05/16 
#
# Author: Fabián Cañaveral
#
# Modifications: 
#		FC on 17/06/16 Se parametrizo conexiones a server.
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub click_tocall{
#############################################################################
#############################################################################
	use JSON;
	my %response;
	
	print "Access-Control-Allow-Origin: *\n";
	print "Access-Control-Allow-Methods: GET,POST,OPTIONS\n";
	print "Content-type: text/plain\n\n";

	if(!$in{'type'} or ($cfg{'asterisk_activate'} and $cfg{'asterisk_activate'} !=1 )){
		print 'ERROR';
		return;
	}

	# Create Conexion BD Asterisk.
	&connect_db_w($cfg{'dbi_db_cc'},$cfg{'dbi_host_cc'},$cfg{'dbi_user_cc'},$cfg{'dbi_pw_cc'});
	my $path = $cfg{'path_click_to_call'};
	$in{'phone'} =~ s/[^0-9]//g;
	$va{'local'} = 55;
	my $numero = $in{'phone'};
	my $local = substr $in{'phone'}, 2;
	my $area = substr $in{'phone'}, 0, 2;
	my $serie = substr $local, 0, 4; 

	if ( !( (substr $in{'phone'}, 0, 2) =~ /55|81|33/g)) {
		$area = substr $in{'phone'}, 0, 3;
	    $local = substr $in{'phone'}, 3;
		$serie = substr $local, 0, 3; 
	}


	if(length $in{'phone'} == 10){
		if($in{'agenda'}){
		$query = "SELECT COUNT(*) FROM blacklists WHERE expression = '". $in{'phone'} ."'";
		if(&Do_SQL($query,1)->fetchrow() > 0){
			return;
			}
		}
		$SQL = "SELECT movil FROM ift WHERE SUBSTRING('$numero',7) BETWEEN inicial AND final AND `area` = $area AND serie = $serie LIMIT 1";
		$sth = &Do_SQL($SQL, 1);
		$res = $sth->fetchrow();
		if($area eq $va{'local'}){
			if($res eq '1'){
				$in{'phone'} = '044'.$in{'phone'};	
			}
		}else{
			if($res eq '1'){
				$in{'phone'} = '045'.$in{'phone'};	
			}else{
				$in{'phone'} = '01'.$in{'phone'};
			}
		}
	}
	if($in{'type'} eq 'generate'){
		$query = "select admin_users.Username_ref from admin_users where admin_users.id_admin_users = '".$usr{'id_admin_users'}."'";
		my $extension = &Do_SQL($query)->fetchrow();
		if(!$extension){
			if($in{'extension'}){
				$extension = $in{'extension'}
			}else{
				$extension = $extension ne '' ? $extension : $cfg{'asterisk_m_default_extension'};
			}
		}

		my $filename = $path. "call-from-".$extension."-".&Do_SQL("SELECT CURDATE()")->fetchrow().".call.txt";

		open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
		print $fh "Channel: ".$cfg{'asterisk_m_channel_prefix'}.$extension."\n";
		print $fh "MaxRetries: 0"."\n";
		print $fh "RetryTime: 3600"."\n";
		print $fh "WaitTime: 30"."\n";
		print $fh "Context: ".$cfg{'asterisk_m_context'}."\n";
		print $fh "Extension: ".$in{'phone'}."\n";
		print $fh "Priority: 1"."\n";
		# print $fh "Set: variablename=variablevalue"."\n";
		print $fh "CallerID: Someone <_ext".$extension."_".$in{'phone'}.">\n";

    	close $fh;
    	use Net::SCP::Expect;
		my $host = $cfg{'asterisk_host'};
		my $pass = $cfg{'asterisk_user'};
		my $user = $cfg{'asterisk_pass'};

		if($in{'agenda'}){
			$host = $cfg{'asterisk_host_agenda'};
			$pass = $cfg{'asterisk_pass_agenda'};
			$user = $cfg{'asterisk_user_agenda'};
		}
		
		if( $in{'extension'} >= 7000 && $in{'extension'} < 8000 ){
			$host = $cfg{'asterisk_host_usa'};
			$pass = $cfg{'asterisk_pass_usa'};
			$user = $cfg{'asterisk_user_usa'};
		}

		my $scpe =  Net::SCP::Expect->new(
			user =>$user,
            password => $pass,
			preserve => 1,
			recursive => 1,
			timeout => 30,
			# verbose=>1,
			auto_yes=>1
		);
		if(-e $filename){
			$scpe->scp($filename,"$host:$cfg{'asterisk_url_to_call'}");
    		unlink("$filename");
		}
   	
		print 'OK';
		return;
	}
	if($in{'type'} eq 'generate_tail'){
		&Do_SQL("INSERT INTO `cu_linealsitesregisters` (`Name`, `Email`, `Telephone`, `City`, `Company`, `URL`, `Tail`, `ID_row`,`Status`, `Date`, `Time`, `ID_admin_users`)
		VALUES 
		('".&filter_values($in{'customer_name'})."', 
		 '".&filter_values($in{'email'})."', 
		 '".&filter_values($in{'phone'})."', 
		 '".&filter_values($in{'city'})."', 
		 '".&filter_values($in{'company'})."', 
		 '".&filter_values($in{'url'})."', 
		 '".&filter_values($in{'tail'})."', 
		 '".&filter_values($in{'id_row'})."',
		 'Active', 
		 curdate(), 
		 curtime(),
		 '1');");


		my $filename = $path. "call-queue-".$in{'phone'}."-".&Do_SQL("SELECT CURDATE()")->fetchrow().".call.txt";
		$in{'customer_name'} =~ s/\s/_/g;
		open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
		if($in{'agenda'}){
			print $fh "Channel: ".$cfg{'asterisk_q_channel_prefix'}.$in{'phone'}."\@from-internal\n";
		}else{
			print $fh "Channel: ".$cfg{'asterisk_q_channel_prefix'}.$in{'phone'}."\n";
		}
		print $fh "MaxRetries: 0"."\n";
		print $fh "RetryTime: 3600"."\n";
		print $fh "WaitTime: 60"."\n";
		print $fh "Context: ".$cfg{'asterisk_q_context'}."\n";
		print $fh "Extension: ".$in{'tail'}."\n";
		print $fh "Priority: 1"."\n";
		print $fh "Set: variablename=variablevalue"."\n";
		print $fh "CallerID: Someone <".$in{'customer_name'}.'_'.$in{'phone'}.">\n";
    	close $fh;
    	use Net::SCP::Expect;
		my $scpe =  Net::SCP::Expect->new(
			user =>$cfg{'asterisk_user'},
            password => $cfg{'asterisk_pass'},
			preserve => 1,
			recursive => 1,
			auto_yes=>1,
			option => 'StrictHostKeyChecking=no'
		);

		if(-e $filename){
			$scpe->scp($filename,"$cfg{'asterisk_host'}:$cfg{'asterisk_url_to_call'}");
    		unlink("$filename");
		}

		$response{'code'}=200;
		$response{'msg'}='File Created';
		print 'OK';
		return;
	}
	
	$response{'code'}=500;
	$response{'error'}='';
	# print encode_json \%response;
	print 'ERROR';
	return;
}

sub getRecordParent{
	print "Content-type: text/html\n\n";
	$nuevacuenta=$in{'nuevacuenta'};
	my $sthOriginal=&Do_SQL("SELECT ID_accounting from sl_accounts where ID_accounting='".$nuevacuenta."' and status='Active'");	
	my $recOriginal=$sthOriginal->fetchrow_hashref();
	if($recOriginal->{'ID_accounting'}){
		print "EXISTS";
	}else{
		$id_account=$in{'padre'};
		my $sth=&Do_SQL("SELECT CONCAT(ID_accounts,'-',Name,'-',ID_accounting) as ID_account from sl_accounts where ID_accounting='".$id_account."' and status='Active'");
		my $rec=$sth->fetchrow_hashref();
		
		if($rec->{'ID_account'}){
			print $rec->{'ID_account'};	
		}else{
			print "ERROR";
		}
	}
}

sub getRecordParentByAccount{
	print "Content-type: text/html\n\n";
	$id_account=$in{'padre'};
	my $sth=&Do_SQL("SELECT ID_parent from sl_accounts where ID_accounts='".$id_account."'");

	my $rec=$sth->fetchrow_hashref();
	
	if($rec->{'ID_parent'} and $rec->{'ID_parent'}>0){
		my $sth=&Do_SQL("SELECT CONCAT(ID_accounting,'-',Name) as ID_account from sl_accounts where ID_accounts='".$rec->{'ID_parent'}."'");
		my $rec=$sth->fetchrow_hashref();

		if($rec->{'ID_account'}){
			print $rec->{'ID_account'};		
			return;
		}
		
	}
	print "ERROR";
}



sub saveTipificacion{
	print "Content-type: text/html\n\n";
	$nuevacuenta=$in{'nuevacuenta'};
	if($in{'tipo'}){
		&Do_SQL("insert into sl_call_schedules (phone, tipificacion, tipificacion_des, status, date, time, id_admin_users) values
			('".&filter_values($in{'phonenumber'})."', 
			'".&filter_values($in{'tipo'})."', 
			'".&filter_values($in{'descripcion'})."','Called', curdate(), curtime(), $usr{'id_admin_users'})
			");
		print 'Saved';
		return;
	}
	print 'ERROR';
}

#############################################################################
#############################################################################
#   Function: call_permisions
#
#       Es: Guarda los permisos para hacer llamadas
#       En:
#
#
#    Created on: 01/12/2016  16:20:10
#
#    Author: Jonathan Alcantara
#
#    Modifications:
#
#   Parameters:
#
#       - users = usuarios separados por comas
#       - permissions = allow o disallow
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
sub call_permisions {
	use Encode;
	use URI::Escape;

	print "Content-type: application/json; charset=utf-8\n\n";

	my @users_arr = split(',', $in{'users'});

	my $res = '{';
	my $result = '';

	if ($in{'users'} > 0 && $in{'type'} ne '') {
		my $query = "SELECT GROUP_CONCAT(admin_users.ID_admin_users) users_no_sale
				FROM admin_users_perms
				INNER JOIN admin_users ON admin_users.ID_admin_users = admin_users_perms.ID_admin_users
				WHERE admin_users_perms.ID_admin_users IN(".$in{'users'}.")
				AND admin_users.application != 'sales';";
		#$res .= '"query0":"'.$query.'",';
		my ($sth) = &Do_SQL($query);
		my ($users_no_sale) = $sth->fetchrow();

		if ($users_no_sale ne '') {
			$result = 'This users does not belong to Sales :'.$users_no_sale;
		} else {
			foreach my $id_admin_users(@users_arr) {
				$res .= '"id_admin_users":'.$id_admin_users.',';
				my $query = "SELECT ID_admin_users_perms, Type
					FROM admin_users_perms
					WHERE ID_admin_users = ".$id_admin_users."
					AND command = 'phone_button';";
				#$res .= '"query1":"'.$query.'",';
				my ($sth) = &Do_SQL($query);
				my ($id_admin_users_perms, $type) = $sth->fetchrow();
				if ($id_admin_users_perms > 0) {
					$res .= '"id_admin_users_perms":'.$id_admin_users_perms.',';
					$res .= '"type":"'.$type.'",';
					if ($type ne $in{'type'}) {
						my $query = "UPDATE admin_users_perms SET Type='".$in{'type'}."' WHERE  ID_admin_users_perms = ".$id_admin_users_perms.";";
						#$res .= '"query2":"'.$query.'",';
						my ($sth) = &Do_SQL($query);
					}
				} else {
					my $query = "INSERT INTO admin_users_perms (ID_admin_users, application, command, Type) VALUES ('".$id_admin_users."', 'sales', 'phone_button', '".$in{'type'}."');";
					#$res .= '"query3":"'.$query.'",';
					my ($sth) = &Do_SQL($query);
				}
			}
			$result = 'User successfully updated';
		}
	} else {
		$result = 'Error missed data';
	}
	print $res.'"res":"'.$result.'"}';
	return;
}



#############################################################################
#############################################################################
#   Function: get_accounts_segments
#
#       Es: Obtiene los segmentos o centros de costos
#       En:
#
#
#    Created on: 06/01/2017  15:00:00
#
#    Author: ISC Gilberto QC
#
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#      - JSON con respuesta del proceso Code 500 => Error, 200 => Exito, y un MSG.
#
#   See Also:
#
sub get_accounts_segments {
#############################################################################
	
	my ($output);

	### Filtro de segmentos por usuario
	my $usr_seg = &load_name('admin_users', 'ID_admin_users', $usr{'id_admin_users'}, 'ID_accounts_segments');
	my $where_usr = '';
	if( $usr_seg and int($in{'restrict'}) == 1 ){
		$usr_seg =~ s/\|/,/g;
		$where_usr = " AND ID_accounts_segments In(".$usr_seg.")";
	}

	my ($sth) = &Do_SQL("SELECT * FROM sl_accounts_segments WHERE 1 AND Status='Active' ".$where_usr." ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		my $selectedtxt = $rec->{'ID_accounts_segments'} eq int($in{'id_accounts_segments'}) ? "selected" : '';
		$output .= "<option value='$rec->{'ID_accounts_segments'}' $selectedtxt>$rec->{'Name'}</option>\n";
	}

	print "Content-type: application/json; charset=utf-8\n\n";
	print $output;
	return;
}


#############################################################################
#############################################################################
#   Function: execute_return
#
#       Es: Ejecuta el return desde el boton de la orden
#       En:
#
#
#    Created on: 22/02/2017
#
#    Author: Fabian Cañaveral			
#       - id_orders = id de la orden a cancelar
#       - process_return = 1
#  Returns:
#
#      - Error/string with data
#
#   See Also:
#
sub execute_return{
#############################################################################
#############################################################################

	require ("../subs/sub.wms.html.cgi");
	require ("../subs/dbman/opr_returns.pl");
	require ("../subs/libs/lib.orders.pl");

	if($cfg{'display_button_return'}){
		print "Content-type: application/json\n\n";
		# &cgierr(Dumper \%in);
		my $id_orders = $in{'id_orders'};
		my $qry = qq|SELECT id_salesorigins, id_customers FROM sl_orders WHERE id_orders = '$id_orders' LIMIT 1|;
		my ($id_salesorigins, $id_customers) = &Do_SQL($qry)->fetchrow();
		# return $id_customers;
		my $qry = qq|SELECT code, subcode, largecode FROM sl_vars_config WHERE command = 'warehouse_auto_return'|;
		my $rs = &Do_SQL($qry)->fetchrow_hashref();
		my $id_warehouse = $rs->{'code'};
		my $upc_location = $rs->{'subcode'};
		my $id_salesorigins_allow = $rs->{'largecode'};
		my $meraction = 'Refund';

		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers 	USING(ID_customers) WHERE ID_orders = '$id_orders';");
		my ($order_type, $ctype) = $sth->fetchrow();

		if(!$id_orders or !$id_salesorigins or !$id_customers or !$id_warehouse or !$upc_location or !$id_salesorigins_allow){
			if($id_salesorigins eq $id_salesorigins_allow){
				print qq|{"code": 500, "msg": "Available only on POS Order"}|;
				return;
			}
			print qq|{"code": 500, "msg": "General Error, try again"}|;
			return;
			# return &trans_txt('error_create_return');
		}
		if($in{'process_return'}){
			# cgierr();
			if($id_salesorigins eq $id_salesorigins_allow){
				
				## Creamos Return
				($total_products, $total_return) = &Do_SQL(qq|SELECT 
					sum(sl_orders_products.Quantity),
					sum(sl_orders_products.SalePrice + sl_orders_products.Shipping - sl_orders_products.Discount + sl_orders_products.Tax)
				FROM sl_orders_parts 
				INNER JOIN sl_orders_products ON sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products
				INNER JOIN sl_skus ON sl_skus.ID_sku_products = sl_orders_products.Related_ID_products
				WHERE 1
					AND id_orders = $id_orders|)->fetchrow();
				if(!$total_products){
					print qq|{"code": 500, "msg": "Error, on create Return"}|;
					return;
				}

				$qry = qq|SELECT 
					SUM(IF(LEFT(ID_products,1) = 8, 1 , 0)) has_return
				FROM sl_orders_products
				WHERE 1 
					AND id_orders = $id_orders;|;
				$has_return = &Do_SQL($qry)->fetchrow_hashref()->{'has_return'};
				if($has_return > 0){
					print qq|{"code": 500, "msg": "Order has previous Return"}|;
					return;
				}

				# cgierr($total_products);
				&Do_SQL("START TRANSACTION;");

				$qry = qq|INSERT INTO sl_returns(ID_orders, ID_customers, Type, generalpckgcondition, itemsqty, merAction, Amount, Status, Date, Time, ID_admin_users) VALUES
					($id_orders, $id_customers, 'Returned for Refund', 'Unknown', '$total_products', '$meraction', '$total_return','Resolved', CURDATE(), CURTIME(), $usr{'id_admin_users'})|;
				$sth = &Do_SQL($qry);
				my $id_returns = $sth->{'mysql_insertid'};
				# my $id_return = $id_returns;
				# $in{'id_return'} = $id_returns;
				if(!$id_returns){
					&Do_SQL('ROLLBACK');
					print qq|{"code": 500, "msg": "Error, on create Return"}|;
					return;
				}
				# Agregamos Return UPC
				$insert_qry = qq|INSERT INTO sl_returns_upcs (ID_returns, ID_parts, UPC, ID_warehouses, Location, Cost, Cost_Adj, Cost_Add, InOrder, Quantity, Status, Date, Time, ID_admin_users) VALUES |;
				 $qry = qq|
				 SELECT 
					'$id_returns' id_return
					, sl_skus.ID_products ID_parts
					, sl_skus.UPC
					, '$id_warehouse' id_warehouse
					, '$upc_location' upc_location
					, sl_orders_products.SalePrice
					, sl_orders_products.Shipping
					, sl_orders_products.Tax
					, sl_orders_products.Tax_percent
					, sl_orders_products.Discount
					, sl_orders_parts.Cost
					, sl_orders_parts.Cost_Adj
					, sl_orders_parts.Cost_Add
					, 'yes' inorder
					, sl_orders_products.Quantity
					, sl_orders_products.ID_orders_products
					, 'TBD' status
					, CURDATE() date
					, CURTIME() time
					, '$usr{'id_admin_users'}' id_admin_users
				FROM sl_orders_parts 
				INNER JOIN sl_orders_products ON sl_orders_parts.ID_orders_products = sl_orders_products.ID_orders_products
				INNER JOIN sl_skus ON sl_skus.ID_sku_products = sl_orders_products.Related_ID_products
				WHERE 1
					AND id_orders = $id_orders|;
				$rw = &Do_SQL($qry); 

				my $return_net = 0;
				my $return_dis = 0;
				my $return_shp = 0;
				my $return_tax = 0;
				my $return_total = 0;

				my $aux = 0;

				while($row = $rw->fetchrow_hashref()){
					$insert_qry.= qq|('$row->{'id_return'}', '$row->{'ID_parts'}', '$row->{'UPC'}', '$row->{'id_warehouse'}', '$row->{'upc_location'}', '$row->{'Cost'}', '$row->{'Cost_Adj'}', '$row->{'Cost_Add'}', '$row->{'inorder'}', '$row->{'Quantity'}', '$row->{'status'}', '$row->{'date'}', '$row->{'time'}', '$row->{'id_admin_users'}'),|;
					$return_net = &round($return_net+  $row->{'SalePrice'},2);
					$return_dis = &round($return_dis+  $row->{'Discount'},2);
					$return_shp = &round($return_shp+  0,);
					$return_tax = &round($return_tax+  $row->{'Tax'},2);
					$return_total = $return_total + $return_net - $return_dis + $return_tax;
					$aux++;
				}
				# cgierr($insert_qry);
				# cgierr(qq| $return_net,$return_dis, $return_shp, $return_tax, $return_total|);
				# Current Status ==> Processed
				chop $insert_qry;
				&Do_SQL($insert_qry);
				
				my ($status, $status_msg, $total_returned) = &return_back_to_inventory($id_returns, $id_orders);

				if ($total_returned > 0){
					&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns = '$id_returns', Notes='Back to Inventory\nSkus Processed: $total_returned\n$status_msg', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}';");
				}else{
					&Do_SQL('ROLLBACK');
					print qq|{"code": 500, "msg": "Error, on create Return"}|;
					return;
				}
				# $str_return = $return_net.'::'.$return_dis.'::'.$return_shp.'::'.$return_tax.'::'.$return_total;
				# $qry = "INSERT INTO `sl_vars` (`VName`, `VValue`) VALUES ('Return$id_returns', '$str_return');";
				# cgierr($qry);
				# use Encode qw(decode encode);
				# $qry = encode('latin1', $qry);
				&Do_SQL($qry);
				# $in{'description'} =encode('latin1', decode('utf8', $in{'description'}));
				# $rrr = &Do_SQL("SELECT * FROM sl_vars where VName = 'Return$id_returns'");
				# use Data::Dumper;
				# cgierr($qry . encode('latin1', Dumper $rrr->fetchrow_hashref));
				

				# $id_returns, $return_net, $return_dis, $return_shp, $return_tax, $return_total

				my ($id_creditmemos, $already_creditmemos) = &return_creditmemo($id_returns, $return_net, $return_dis, $return_shp, $return_tax, $return_total); 
				my $flag_accounting = 0;
				if($id_creditmemos){
					my $sumatoria = 0;

					# my $id_orders = $id_returns ? int($id_returns) : &load_name('sl_returns', 'ID_returns', $id_returns, 'ID_orders');


					########
					######## 3.2.1) Movimientos Contables (Devolucion)
					########
					my @params = ($id_orders);
					my ($this_acc_status, $this_acc_str) = &accounting_keypoints('order_products_returned_'. $ctype .'_'. $order_type, \@params );
					$flag_accounting++ if $this_acc_status;

					########
					######## 3.2.2) Movimientos Contables (Devolucion Finalizada)
					########
					my $amount_toreturn = $sumatoria > 0 ? 0 : $sumatoria;
					@params = ($id_orders,$meraction,0,$amount_toreturn);
					($this_acc_status, $this_acc_str2) = &accounting_keypoints('order_products_returnsolved_'. $ctype .'_'. $order_type, \@params );
					$flag_accounting++ if $this_acc_status;					

					# cgierr($this_acc_str ." --- ". $this_acc_str2)

					########
					######## 3.2.3) Actualizacion de tablerelated (Devolucion Finalizada)
					########
					&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_creditmemos', ID_tablerelated = '$id_creditmemos' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_tablerelated = 0 AND Status = 'Active' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',TIME),NOW()) BETWEEN 0 AND 50;");
					


					########
					######## 4) Credit Memo (Fiscal)
					########
					&export_info_for_credits_notes($id_creditmemos);

				}else{
					&Do_SQL('ROLLBACK');
					print qq|{"code": 500, "msg": "Error, on create Creditmemo"}|;
					return;
				}

				########
				######## 5) Recalc Totals
				########
				&recalc_totals($id_orders);
				
				&Do_SQL("UPDATE sl_returns SET Status='Resolved' WHERE ID_returns='$id_orders'")

				&Do_SQL('COMMIT');
				# cgierr("$status| $status_msg| $total_returned |$id_returns");
				print qq|{"code": 200, "msg": "Return Created!"}|


			}else{
				print qq|{"code": 500, "msg": "Available only on POS Order"}|;
			}
		}else{
			print qq|{"code":500, "msg" : "Generar Error, try again"}|;
		}
		# return qq|<a class="fancy_modal_iframe" href="/cgi-bin/mod/admin/dbman?cmd=opr_orders&id_orders=10157264&process_return=1"><img src="/sitimages/aqua/b_cauth.gif" style="width:25px;" title="Return Order"></a>|;
	}
}

#############################################################################
#############################################################################
#   Function: usrman_vendor
#
#       Es: Funcion que genera la cuenta de usuario para el portal de proveedores
#       En: 
#
#
#    Created on: 12/12/2016
#
#    Author: ISC Gilberto Quirino
#
sub usrman_vendor {
#############################################################################
#############################################################################

	print "Content-type: text/html\n\n";

	$usr{'id_admin_users'} = $in{'view'};
	
	if( int($in{'action'}) == 1 ){

		### Se obtienen los datos necesarios del usuario
		my $sth = &Do_SQL("SELECT ID_admin_users, Email, FirstName FROM admin_users WHERE ID_admin_users = ".int($in{'view'}).";");
		my $usr = $sth->fetchrow_hashref();

		if( int($usr->{'ID_admin_users'}) > 0 and $usr->{'ID_admin_users'} ne '' and $in{'id_vendors'} > 0 ){
			my @ids_vendors = split('-', $in{'id_vendors'});

			&Do_SQL("START TRANSACTION;");

			my $new_pswd = &gen_rand_pswd();
			$new_pswd = $in{'pswd'} if( $in{'pswd'} ne '' );
			
			foreach $idv( @ids_vendors ){
				&Do_SQL("INSERT INTO admin_users_vendors SET 
							id_admin_users = ".$usr->{'ID_admin_users'}."
							, id_vendors = ".$idv."
							, email = '".$usr->{'Email'}."'
							, password = sha1('".$new_pswd."')
							, `status` = 'Active';");
			}
			### Se actualiza la contrasena en la tabla de usuarios de direksys
			&Do_SQL("UPDATE admin_users SET Password=sha1('".$new_pswd."'), tempPasswd='".$new_pswd."' WHERE ID_admin_users = ".$usr->{'ID_admin_users'}.";");

			if( int($in{'sendmail'}) == 1 ){
				my $from_email = 'no-reply@inova.com.mx';
				my $to_email = $usr->{'Email'};
				my $subject = 'Cuenta de acceso al portal de proveedores Inova';
				my $body = 'Estimado '.$usr->{'FirstName'}.', este mensaje es para notificarle que se le ha generado una cuenta de acceso al portal de proveedores de Inova, la cual se muestra a continuación:';
				$body .= '<br />Sitio Web: https://proveedor.inova.com.mx';
				$body .= '<br />Nombre de usuario: '.$to_email;
				$body .= '<br />Contraseña (temporal): '.$new_pswd;
				$body .= '<br /><br />Por seguridad, es importante que genere su propia su contraseña una vez haya ingresado al portal.';
				$body = decode('utf-8', $body);

				### Se envía el correo de notificacion
				$rslt_mail = &send_mandrillapp_email_attachment($from_email, $to_email, $subject, $body, 'none', 'none');
			}
			
			if( ($rslt_mail->{'content'}[0]{'status'} eq 'sent' or $rslt_mail->{'content'}[0]{'status'} eq 'queued' and int($in{'sendmail'}) eq 1) or int($in{'sendmail'}) == 0 ){
				&Do_SQL("COMMIT;");

				$va{'style_msg'} = 'msg_info';
				my $sendmail_msg = ', además se ha enviado un correo de notificación a '.$usr->{'Email'} if( int($in{'sendmail'}) == 1 );
				$va{'messages'} = 'La cuenta de acceso al portal se ha creado correctamente'.$sendmail_msg.'.';
			} else {
				&Do_SQL("ROLLBACK;");

				$va{'style_msg'} = 'msg_error';
				$va{'messages'} = 'Ha ocurrido un error al intentar enviar el correo: '.$rslt_mail->{'content'}[0]{'reject_reason'}.$rslt_mail->{'content'}[0]{'status'};
			}

		} else {
			$va{'style_msg'} = 'msg_error';
			$va{'messages'} = 'Este usuario no cuenta con los datos necesarios para su acceso al portal de proveedores';
		}		

		$va{'messages'} = decode('utf-8', $va{'messages'});

		$va{'display_step1'} = 'none';
		$va{'display_step2'} = 'block';
		print &build_page('vendoruser_select.html');
	} else {
		
		my $sql = "SELECT 
						GROUP_CONCAT(ID_vendors SEPARATOR '-') AS IDs_vendors
						, CompanyName
						, RFC
						, GROUP_CONCAT(Currency SEPARATOR ' - ') AS Currency
					FROM sl_vendors 
					WHERE `Status` = 'Active' 
						AND RFC != ''
						AND RFC NOT LIKE '%--%'
						AND RFC NOT LIKE '%XX%'
						AND RFC NOT LIKE '%**%'
					GROUP BY RFC 
					ORDER BY CompanyName;";
		my $sth = &Do_SQL($sql);

		$va{'vendors_list'} = '';
		while( my $rec = $sth->fetchrow_hashref() ){
			$va{'vendors_list'} .= '<tr data-id="'.$rec->{'IDs_vendors'}.'">';
			$va{'vendors_list'} .= '<td><input type="radio" name="id_vendors" id="id_vendors_'.$rec->{'IDs_vendors'}.'" value="'.$rec->{'IDs_vendors'}.'"></td>';
			$va{'vendors_list'} .= '<td>'.$rec->{'IDs_vendors'}.'</td>';
			$va{'vendors_list'} .= '<td>'.$rec->{'RFC'}.'</td>';
			$va{'vendors_list'} .= '<td class="text-left">'.$rec->{'CompanyName'}.'</td>';
			$va{'vendors_list'} .= '<td>'.$rec->{'Currency'}.'</td>';
			$va{'vendors_list'} .= '</tr>';
		}

		$va{'display_step1'} = 'block';
		$va{'display_step2'} = 'none';
		print &build_page('vendoruser_select.html');

	}


	sub gen_rand_pswd {

		my $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890';
		my $pswd_lgth = 10;
		my $pswd = '';

		for( my $i=0; $i < $pswd_lgth; $i++ ){
			my $rand_pos = int( rand( length($chars) ) );
			$pswd .= substr($chars, $rand_pos, 1);
		}

		return $pswd;

	}
}


#############################################################################
#############################################################################
# Function: petty_cash
#
# Es: Editor de Caja Chica
# En: 
#
# Created on: 28/04/2017 
#
# Author: L.C. Huitzilihuitl Ceja
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub petty_cash{
#############################################################################
#############################################################################
	use Data::Dumper;

	if($in{'action'})
	{ 

		if( $in{'id_expenses_users'} )
		{
			$sql = "UPDATE sl_expenses_users SET 
				ID_accounts_debit = ".$in{'id_accounts_debit'}.", 
				ID_accounts_credit = ".$in{'id_accounts_credit'}.", 
				ID_accounts_debit_pettycash = ".$in{'id_accounts_debit_pettycash'}."
				WHERE ID_expenses_users = ".$in{'id_expenses_users'}.";";
		}else{
			$sql = "INSERT INTO sl_expenses_users (ID_admin_users, ID_accounts_debit, ID_accounts_credit, ID_accounts_debit_pettycash, Status, Date, Time) 
					VALUES (".$in{'id_admin_users'}.", ".$in{'id_accounts_debit'}.", ".$in{'id_accounts_credit'}.", ".$in{'id_accounts_debit_pettycash'}.", 'Active', curdate(), curtime() ) ";
		}
	
		&Do_SQL($sql);

	}

	my $sql = "SELECT ID_expenses_users, 
				IF(ID_accounts_debit is NULL, 'NULL', ID_accounts_debit) ID_accounts_debit, 
				IF(ID_accounts_credit is NULL, 'NULL', ID_accounts_credit) ID_accounts_credit, 
				IF(ID_accounts_debit_pettycash is NULL, 'NULL', ID_accounts_debit_pettycash) ID_accounts_debit_pettycash
				FROM sl_expenses_users WHERE ID_admin_users = $in{'id_admin_users'} and Status='Active';";
	my ($sth) = &Do_SQL($sql);
	( $va{'id_expenses_users'}, $va{'id_debit'}, $va{'id_credit'}, $va{'id_debit_pettycash'} ) = $sth->fetchrow;


	print "Content-type: text/html; charset=UTF-8\n\n";
	print &build_page('petty_cash.html');


}




sub editproduct{
	use Data::Dumper;
	if($in{'edit'}){
		if($in{'convert_to_promo'}){
			$in{'cmd'} = 'mer_products';
			$va{'activetab'} = '3';
			$query = qq|INSERT INTO sl_vars (VName, VValue) VALUES ('promo$in{'id_products'}', '')|;
			&Do_SQL($query);
			$query = qq|INSERT INTO sl_vars (VName, VValue) VALUES ('percent_promo$in{'id_products'}', '')|;
			&Do_SQL($query);
			print "Content-type: text/html\n\n";
			print &build_page('products_tab3_promo.html');
			return;
		}
		if($in{'convert_to_product'}){
			$query = qq|DELETE FROM sl_vars WHERE VName = 'promo$in{'id_products'}'|;
			&Do_SQL($query);
			$query = qq|DELETE FROM sl_vars WHERE VName = 'percent_promo$in{'id_products'}'|;
			&Do_SQL($query);
			print "Content-type: text/html\n\n";

			return;
		}
		if($in{'saveproducts'}){
			use JSON;
			print "Content-type: application/json\n\n";
			$in{'skus_parts'} =~ s/\\//g;
			## Limpiamos ID de caracteres extraños
			$in{'id_products'} =~s/[^0-9]//g;
			my $products_percent = decode_json $in{'skus_parts'};	
			my $products = "";
			my $product_percent = "";

			while ( ($id_sku_products, $values) = each %$products_percent ){
				$products .= $id_sku_products."|";
				$product_percent .= $values->{'percent'}."|";
			}
			chop $products;
			chop $product_percent;
			$query = qq|UPDATE sl_vars SET VValue = '$products' WHERE VName = 'promo$in{'id_products'}'|;

			&Do_SQL($query);
			$query = qq|UPDATE sl_vars SET VValue = '$product_percent' WHERE VName = 'percent_promo$in{'id_products'}'|;
			&Do_SQL($query);
			print qq|{"code":200, "msg": "Skus Actualizados"}|;

			return;
		}
		use JSON;
		print "Content-type: application/json\n\n";
		$in{'skus_parts'} =~ s/\\//g;
		## Limpiamos ID de caracteres extraños
		$in{'id_products'} =~s/[^0-9]//g;
		my $skus_parts = decode_json $in{'skus_parts'};
		my $insert = 0;
		# Borramos previos Skus_parts
		$query = qq|DELETE FROM sl_skus_parts WHERE SUBSTR(id_sku_products, 4) = $in{'id_products'}|; 
		&Do_SQL($query);
		
		$query = qq|INSERT INTO sl_skus_parts (id_sku_products, id_parts, Qty, Date, Time, id_admin_users) VALUES |;
		my $query2;
		# $updateQuery = qq||;
		while ( ($id_sku_products, $values) = each %$skus_parts ){
			$upc = $values->{'upc'};
			$query2 = qq|UPDATE sl_skus SET UPC = '$upc' WHERE ID_sku_products = '$id_sku_products'|;
			&Do_SQL($query2);
			for my $part (@{$values->{'parts'}}){
				$insert = 1;
				$query2 = qq|UPDATE sl_skus SET IsSet = 'Y' WHERE ID_sku_products = '$id_sku_products'|;
				&Do_SQL($query2);

				$query .= qq|('$id_sku_products', '$part->{'id_sku'}', '$part->{'qty'}', curdate(), curtime(), '$usr{'id_admin_users'}'),|;
			}
		    # print "$id_skus_parts , $values ";
		}
		chop $query;
		if($insert == 1){
			&Do_SQL($query);
		}
		
		print qq|{"code":200, "msg": "Skus Actualizados"}|;
	}else{
		if($in{'type'} eq 'parts'){
			print "Content-type: text/html\n\n";
			$va{'table_parts'} = qq|<table id="accounts" style="width:98%"><thead><tr>
				<th width="10"></th>
				<th>ID Parts</th>
				<th>Name</th>
				<th>Model</th>
			</tr></thead><tbody>|;
			$query = qq|SELECT ID_parts, Name, Model FROM sl_parts|;
			$parts = &Do_SQL($query);
			while($part = $parts->fetchrow_hashref()){
				$va{'table_parts'} .= qq|
				<tr data-id_part="$part->{'ID_parts'}" data-id_skus_products="$in{'id_skus_products'}" data-name="$part->{'Name'} / $part->{'Model'}">
					<td width="10px"></td>
					<td>$part->{'ID_parts'}</td>
					<td>$part->{'Name'}</td>
					<td>$part->{'Model'}</td>
				</tr>
				|;
			}
			$va{'table_parts'}.=qq|</tbody></table>|;
			print &build_page('products_parts.html');
		}elsif($in{'type'} eq 'product'){
			print "Content-type: text/html\n\n";
			$va{'table_parts'} = qq|<table id="accounts" style="width:98%"><thead><tr>
				<th width="10"></th>
				<th>ID Parts</th>
				<th>Name</th>
				<th>Model</th>
			</tr></thead><tbody>|;
			$query = qq|SELECT ID_products, Name, Model FROM sl_products WHERE status = 'On-Air'|;
			$parts = &Do_SQL($query);
			while($part = $parts->fetchrow_hashref()){
				$va{'table_parts'} .= qq|
				<tr data-id_products="$part->{'ID_products'}" data-id_skus_products="$in{'id_skus_products'}" data-name="$part->{'Name'} / $part->{'Model'}">
					<td width="10px"></td>
					<td>|.&format_sltvid($part->{'ID_products'}).qq|</td>
					<td>$part->{'Name'}</td>
					<td>$part->{'Model'}</td>
				</tr>
				|;
			}
			$va{'table_parts'}.=qq|</tbody></table>|;
			print &build_page('products_parts.html');
		}elsif($in{'type'} eq 'service'){
			print "Content-type: text/html\n\n";
			$va{'table_parts'} = qq|<table id="accounts" style="width:98%"><thead><tr>
				<th width="10"></th>
				<th>ID Parts</th>
				<th>Name</th>
				<th>Model</th>
			</tr></thead><tbody>|;
			$query = qq|SELECT ID_parts, Name, Model FROM sl_parts|;
			$parts = &Do_SQL($query);
			while($part = $parts->fetchrow_hashref()){
				$va{'table_parts'} .= qq|
				<tr data-id_part="$part->{'ID_parts'}" data-id_skus_products="$in{'id_skus_products'}" data-name="$part->{'Name'} / $part->{'Model'}">
					<td width="10px"></td>
					<td>$part->{'ID_parts'}</td>
					<td>$part->{'Name'}</td>
					<td>$part->{'Model'}</td>
				</tr>
				|;
			}
			$va{'table_parts'}.=qq|</tbody></table>|;
			print &build_page('products_parts.html');
		}
	}

}




sub savechoices {
	use Data::Dumper;
	use JSON;
	# print "Content-type: application/json\n\n";
	# print Dumper \%in;
	# exit;
	$in{'choices'} =~ s/\\//g;
	my $choices = decode_json $in{'choices'};
	my $base = 100;
	my $query = '';
	# print "\n";
	## Se borran previos skus_parts
	$query = qq|DELETE FROM sl_skus_parts WHERE SUBSTR(id_sku_products, 4) = $in{'id_products'}|; 
	&Do_SQL($query);
	## Se borran previos Choices
	$query = qq|DELETE FROM sl_skus WHERE id_products = $in{'id_products'}|; 
	# &Do_SQL($query);
	&Do_SQL($query);
	$query = qq|INSERT INTO sl_skus(`ID_sku_products`, `ID_products`, `IsSet`, `choice1`, `choice2`, `choice3`, `choice4`, `Date`, `Time`, `ID_admin_users`) VALUES|;
	for my $choice1 (@{$choices->{'lista1'}}){
		if ($#{$choices->{'lista2'}} > -1){
			for my $choice2 (@{$choices->{'lista2'}}){
				if($#{$choices->{'lista3'}} > -1){
					for my $choice3 (@{$choices->{'lista3'}}){
						if($#{$choices->{'lista4'}} > -1){
							for my $choice4 (@{$choices->{'lista4'}}){
								$query .= qq|($base$in{'id_products'}, $in{'id_products'}, 'N', '$choice1', '$choice2', '$choice3', '$choice4', curdate(), curtime(), $usr{'id_admin_users'}),|;
								$base++;
							}
						}else{
							$query .= qq|($base$in{'id_products'}, $in{'id_products'}, 'N', '$choice1', '$choice2', '$choice3', NULL, curdate(), curtime(), $usr{'id_admin_users'}),|;
							$base++;
						}
					}
				}else{
					$query .= qq|($base$in{'id_products'}, $in{'id_products'}, 'N', '$choice1', '$choice2', NULL, NULL, curdate(), curtime(), $usr{'id_admin_users'}),|;
					$base++;
				}
			}
		}else{
			$query .= qq|($base$in{'id_products'}, $in{'id_products'}, 'N', '$choice1', NULL, NULL, NULL, curdate(), curtime(), $usr{'id_admin_users'}),|;
			$base++;
		}
	}
	chop $query;
	&Do_SQL($query);

	#Regresamos Lista de Choices
	my %response = ();
	my @choices = ();
	$query = qq|SELECT * FROM sl_skus WHERE id_products = $in{'id_products'}|;
	$new_skus = &Do_SQL($query);
	while($new_sku = $new_skus->fetchrow_hashref()){
		push @choices, $new_sku;
	}
	#Regresamos Lista de Nombres de Choice
	my @choicesNames = ($in{'choicename1'}, $in{'choicename2'}, $in{'choicename3'}, $in{'choicename4'});
	$query = qq|UPDATE sl_products SET ChoiceName1 = '$in{'choicename1'}', ChoiceName2 = '$in{'choicename2'}', ChoiceName3='$in{'choicename3'}', ChoiceName4 = '$in{'choicename4'}' WHERE id_products = $in{'id_products'}|;

	&Do_SQL($query);
	$response{'choices'} = \@choices;
	$response{'choicesName'} = \@choicesNames;
	print "Content-type: application/json\n\n";
	# print Dumper \%in;
	print encode_json \%response;
	
}








#############################################################################
#############################################################################
# Function: search_products
#
# Es: Busca en catalogo de SAT
# En: 
#
# Created on: 09/08/2017
#
# Author: Fabián Cañaveral
#
# Modifications: 
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub search_products{
#############################################################################
#############################################################################
	use JSON;
	my %response;
	print "Content-type: application/json\n\n";
	$sku = $in{'data[q]'};
	my $query = qq|SELECT CONCAT(cu_products_services.ID_product_service, ' - ', cu_products_services.description ) product
		, cu_products_services.ID_product_service
		, cu_products_services.description
		FROM cu_products_services
		WHERE 1
			AND cu_products_services.description like '%$sku%'|;
	my $rs = &Do_SQL($query);
	@results = ();

	while($row = $rs->fetchrow_hashref() ){
			
		push @results, {
			id => $row->{'ID_product_service'},
			text => $row->{'product'}
		};
	}
	$response{'q'} = $sku;
	$response{'results'} = \@results;

	print encode_json \%response;
	return;
}


#############################################################################
#############################################################################
# Function: api_get_template_mail
#
# Es: Obtiene el Template del Layout
# En: 
#
# Created on: 13/10/2017
#
# Author: Huitzilihuitl
#
# Modifications: 
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo:
#
sub api_get_template_mail{
#############################################################################
#############################################################################
	use JSON;
	use URI;
	use LWP::UserAgent;


	my $url = URI->new($cfg{'api_url'}.'mailtemplate/show/'.$in{'template'});
	$url->query_form( 
						'fecha' => $in{'date'},
						'company' => $in{'company'},
						'textA' => $in{'texta'},
						'textB' => $in{'textb'},
						'textC' => $in{'textc'},
					);

	my $ua = LWP::UserAgent->new;
	my $response = $ua->get( $url, 'Authorization' => $cfg{'api_direksys_key'},	);

	print "Content-type: text/html; charset=UTF-8\n\n";
	print( $response->content );

}



#############################################################################
#############################################################################
# Function: download_file
#
# Es: Obtiene el Template del Layout
# En: 
#
# Created on: 13/10/2017
#
# Author: Huitzilihuitl
#
# Modifications: 
#
# Parameters:
#
# Returns:
#
# See Also:
#
# Todo:
#
sub download_file{
#############################################################################
#############################################################################
	use File::Slurp;

	my $path = $cfg{'background_report_path'} .$in{'e'}.'/background_reports/'. $in{'name'};
	my $text = read_file($path, err_mode => 'carp' ) ;
	
	my $mime;
	my $ext = substr $in{'name'}, rindex( $in{'name'}, '.')+1;

	if( $ext =~ m/csv/ ){
		$mime = 'text/csv';
	}elsif( $ext =~ m/xls|lsx/ ){
		$mime = 'application/vnd.ms-excel';
	}

    unless ( $text ) {
		$text = 'El archivo solicitado no se encuentra ya disponible.';
		$mime = 'text/plain';

		$query = "UPDATE sl_background_reports SET status='Delete' WHERE file='$in{'name'}';";
		&Do_SQL($query);
    }

	print "Content-type: $mime\n";
	print "Content-Disposition: attachment; filename:".$in{'name'}."\n\n";
	print $text;

}

#############################################################################
#############################################################################
# Function: delete_background_report
#
# Es: Obtiene el Template del Layout
# En: 
#
# Created on: 20/02/2018
#
# Author: Huitzilihuitl
#
# Modifications: 
#
# Parameters:
#
# Returns:
#
# See Also:
#
# Todo:
#
sub delete_background_report{
#############################################################################
#############################################################################

    my $query = "UPDATE sl_background_reports SET status='Delete' WHERE file='".$in{'file'}."';";
    &Do_SQL($query);

    print "Content-type: text/plain; charset=UTF-8\n\n";
    print $query;
}


#############################################################################
#############################################################################
# Function: unlock_users
#
# Es: Desbloquea usuario que se haya bloqueado por exceso de intentos erroneos de login
# En: 
#2018/03/02 
#
# Author: Alfredo Salazar
#
# Modifications: 
#
# Parameters:
#
# Returns:
#
# See Also:
#
# Todo:
#
sub unlock_users {
	print "Content-type: text/plain; charset=UTF-8\n\n";
	# print "Se van a bloquear ".$in{'ids_admin_users_to_unlock'};

	use Data::Dumper;
	# print Dumper(\%in);

	foreach $key (keys %cfg){
		$value = $cfg{$key};
		my %current_company;

  		if($key =~ /app_e\d/g ){  			  			
  			$company = $key;
			$company =~ s/\D//g;
			
			%current_company=&get_db_conn_data_company($company);			


			&connect_db_w($current_company{'dbi_db'},$current_company{'dbi_host'},$current_company{'dbi_user'},$current_company{'dbi_pw'});

			# Get the list of locked users for the curren company
			my $q_locked_users = 'SELECT   admin_users_locked.ID_admin_users_locked
						,admin_users_locked.ID_admin_users
						,admin_users_locked.ID_ipmanager						
				FROM admin_users_locked
				JOIN admin_users ON admin_users.ID_admin_users=admin_users_locked.ID_admin_users
				JOIN sl_ipmanager on sl_ipmanager.ID_ipmanager=admin_users_locked.ID_ipmanager
				WHERE admin_users_locked.ID_admin_users IN ('.$in{'ids_admin_users_to_unlock'}.')';


			my $e_locked_users = &Do_SQL($q_locked_users,1);			

			while($r_locked_users = $e_locked_users->fetchrow_hashref() ){				
				
				# Activate user in admin_users
				$q_enable_user='UPDATE admin_users SET Status="Active" WHERE ID_admin_users='.$r_locked_users->{'ID_admin_users'};
				$q_enable_user=&Do_SQL($q_enable_user,1);

				# Deleting Suspect IP from sl_ip manager				
				$q_qty_users_related_left = "SELECT * FROM admin_users_locked WHERE ID_ipmanager=".$r_locked_users->{'ID_ipmanager'};
				$e_qty_users_related_left = &Do_SQL($q_qty_users_related_left);
				my $rows_qty_users_related_left=$e_qty_users_related_left->rows;

				if($rows_qty_users_related_left==1){
					$q_delete_suspect_ip='DELETE FROM sl_ipmanager WHERE ID_ipmanager='.$r_locked_users->{'ID_ipmanager'};
					$e_delete_suspect_ip=&Do_SQL($q_delete_suspect_ip,1);				
				}
				

				# Deleting relational record between sl_admin_users and sl_ipmanager
				$q_admin_users_locked='DELETE FROM admin_users_locked WHERE ID_admin_users_locked='.$r_locked_users->{'ID_admin_users_locked'};
				$e_admin_users_locked=&Do_SQL($q_admin_users_locked,1);								

				# Insert Log for unlocking action				
				$in{'db'}='admin_users';
   				$in{'cmd'}='usr_admin_banned';
				&auth_logging('admin_users_unlocked',$r_locked_users->{'ID_admin_users'},1);
			}
  		}
	}
	print "OK";
}


#############################################################################
#############################################################################
# Function: get_db_conn_data_company
#
# Es: Obtiene los datos de conexion de la comapañia con el numero que se le pasa como parametro
# En: 
#2018/03/02 
#
# Author: Alfredo Salazar
#
# Modifications: 
#
# Parameters:
#
# Returns:
#
# See Also:
#
# Todo:
#
sub get_db_conn_data_company{
	my ($company) = @_;	
	
	use Switch;
		
	my $fname = "../general.e".$company.".cfg";	
	my $dbi_db=$dbi_host=$dbi_pw=$dbi_user;

	## general
	open (CFG, "<$fname") or &cgierr ("Unable to open: $fname,160,$!");
	LINE: while (<CFG>) {
		(/^#/)      and next LINE;
		(/^\s*$/)   and next LINE;
		$line = $_;
		$line =~ s/\n|\r//g;
		my ($td,$name,$value) = split (/\||\=/, $line,3);
		
		if ($td eq "conf") {
			  # $cfg{$name} = $value;
			  switch ($name) {
				case "dbi_db"		{ $dbi_db=$value; }
				case "dbi_host"		{ $dbi_host=$value; }
				case "dbi_pw"		{ $dbi_pw=$value; }
				case "dbi_user"		{ $dbi_user=$value; }
			}
			next LINE;
		}
	}
	close CFG;
	
	my %resp = (
			"dbi_db"=>$dbi_db,
			"dbi_host"=>$dbi_host,
			"dbi_pw"=>$dbi_pw,
			"dbi_user"=>$dbi_user
        );

	 return (%resp);
}

# Function: download_file
#
# Es: Obtiene el Template del Layout
# En: 
#
# Created on: 13/10/2017
#
# Author: Huitzilihuitl

sub download_pdf_order_file{
#############################################################################
#############################################################################
    use File::Slurp;

    my $path = $cfg{'path_upfiles'}.'e'.$in{'e'}.'/orders_pdf/'. $in{'name'};
    #my $text = read_file($path, err_mode => 'carp' ) ;
    my $text = read_file( $path, binmode => ':raw' ) ;

    print "Content-type:application/pdf\n";
    print "Content-Disposition:attachment;filename:'".$in{'name'}."'\n\n";
    print $text;
}

1;
