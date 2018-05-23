#!/usr/bin/perl
sub warning_message_product {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	my ($out);
	if ($in{'id_products'}>0){
		## Build Warnings
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_categories WHERE ID_products='$in{'id_products'}'");
		if ($sth->fetchrow ==0){
			$out .= "<li>".&trans_txt('products_war_nocat')."</li>";
		}
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_products_vendors WHERE id_products='$in{'id_products'}'");
		if ($sth->fetchrow ==0){
			$out .= "<li>".&trans_txt('products_war_noven')."</li>";
		}
		if (&load_name('sl_skus','ID_products',$in{'id_products'},'IsSet') ne 'Y'){
			my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location  WHERE RIGHT(ID_products,6)='$in{'id_products'}';");
			if ($sth->fetchrow ==0){
				$out .= "<li>".&trans_txt('products_war_noinv')."</li>";
			}
		}
		if (!$in{'sprice'}){
			$out .= "<li>".&trans_txt('products_war_price')."</li>";
		}
				
		## Check for Image
		use LWP::UserAgent;
		my ($results);
		my ($ua) = new LWP::UserAgent;
		$ua->timeout(10);
		$ua->agent("Mozilla/8.0"); # pretend we are very capable browser
		my ($req) = new HTTP::Request 'GET' => "/cgi-bin/common/apps/checkimg?id=$in{'id_products'}";
		$req->header('Accept' => 'text/html');
	
		# send request
		$res = $ua->request($req);
			
		# check the outcome
		if ($res->is_success) {
			$results = $res->content;
			if (!$results){
				$out .= "<li>".&trans_txt('products_war_noimgs')."</li>";
			}
		}else{
			$out .= "<li>".&trans_txt('products_war_noimgs')."</li>";
		}
		
		#if ($out eq ""){
		#	$out = "<td class='help_on'>No Messages</td>";
		#}
		#$out = "<td class='stdtxterr_blue'>$out</td>";		
	}		
	return $out;
}

sub build_html_textbox {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	#$in{'speech'} = &specialchar_cnv($in{'speech'});
	return &FCKCreateHtml('speech',$in{'speech'});
}

sub build_html_textbox_doc {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#
	return &FCKCreateHtml('document',$in{'document'});
}


sub build_soapps {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	return build_checkbox_from_enum('apps','admin_users_group');
}



sub payreturn{
#-----------------------------------------
# Created on: 12/01/08  16:32:32 By  Roberto Barcenas
# Forms Involved: 
# Description : Shows the icon to process the return payment
# Parameters : 	
# Last Modified RB: 02/05/09  13:06:50 - If the payment is not founded, the icon is not shown
# Last Modified RB: 02/16/09  11:58:23 - Added payment inside div tag and when clicked the div is deleted


	my ($idop,$capt,$rec,$sth,$str);
	

	$sth = &Do_SQL("SELECT ID_orders_payments,IF(Captured='No',0,1)AS Captured FROM sl_orders_payments  INNER JOIN sl_orders ON sl_orders.ID_orders = sl_orders_payments.ID_orders WHERE sl_orders.ID_orders = '$in{'id_orders'}' AND Amount = '$in{'amount'}' AND sl_orders.Date < sl_orders_payments.Date AND sl_orders_payments.Status IN ('Approved','Credit')");
	($idop,$capt) = $sth->fetchrow();
	
	if($sth->rows > 0 and !$capt){
		if ($in{'amount'} > 0){
			$str = qq| &nbsp;<div id="ppayment"><a href="#pamount" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'pamount');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=ccsale&id_orders=$in{'id_orders'}&id_orders_payments=$idop&e=$in{'e'}');delete_div('ppayment');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_fpauth.gif' title='Authorize/Capture Payment' alt='' border='0'></a></div>|;
		}else{
			$str = qq| &nbsp;<div id="prefound"><a href="#pamount" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'pamount');loadDoc('/cgi-bin/common/apps/ajaxpayment?ajaxbuild=cccredit&id_orders=$in{'id_orders'}&id_orders_payments=$idop&e=$in{'e'}');delete_div('prefound');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_fpauth.gif' title='Authorize/Capture Refund' alt='' border='0'></a></div>|; 
		}
	}elsif($sth->rows == 0){
			$str =	qq| &nbsp;<span style="color:red; font-size:11px;">Payment has been edited manually</span>	|;
	}else{
		$str =	qq| &nbsp;<span style="color:green; font-size:11px;">(Done)</span>	|; 
	}
}



sub build_link_products{
# --------------------------------------------------------
# Created by: Jose Ramirez Garcia
# Created on: 06/30/2008
# Description : It builds the link to the product and add the sltvid format
# Notes : (Modified on : Modified by :)
	if(substr($in{'id_products'},0,1) eq 4){
		$id_products=&format_sltvid($in{'id_products'});
		$id_prod = substr($in{'id_products'},5,4);
		return qq|<a href="$va{'script_url'}?cmd=mer_parts&view=$id_prod#tabs">$id_products</a>|;
	} else {
		$id_products=&format_sltvid($in{'id_products'});
		$id_prod = substr($in{'id_products'},3,6);
		return qq|<a href="$va{'script_url'}?cmd=mer_products&view=$id_prod#tabs">$id_products</a>|;
	}
}

sub build_userlist_manifest {
# --------------------------------------------------------
	# Created on: 07/09/2008
	# Last Modified on: 
	# Last Modified by: 
	# Author: Jose Ramirez Garcia
	# Description :  It shows administration and wms users in drop down menu
	# Parameters :
	my ($output,$ext);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE application IN ('admin','wms') AND Status='Active' ORDER BY LastName");
	while ($rec = $sth->fetchrow_hashref){
		($rec->{'extension'}) ? ($ext = "($rec->{'extension'})"):
							($ext = "");
		$output .= "<option value='$rec->{'ID_admin_users'}'>$rec->{'LastName'}, $rec->{'FirstName'} $ext ($rec->{'application'})</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}



sub build_closervendor_button{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 07/22/2008
# Last Modified on: 
# Last Modified by: 
# Description : it shows the close rvendor button when status isn't received or cancelled
# Forms Involved: 
# Parameters : 
	
	if($in{'status'} ne 'Received' && $in{'status'} ne 'Cancelled'){
		$closepo = qq|
			<center><input type="button" value="Close Return" class="button" onclick="closepo()"></center>
		<script>
			function closepo(){
				if(confirm("Close Return Order?")){
					trjump('/cgi-bin/mod/admin/dbman?cmd=mer_rvendor&view=[in_id_purchaseorders]&id_purchasesorders=[in_id_purchaseorders]&closervendor=1&action=1&status=[in_status]');
				}
			}
		</script>
		|;
	}	else {
		$closepo = "";
	}
	return $closepo;
}



sub build_button_show_products_speech{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 8/7/2008
# Last Modified on:  
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($output);
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_speech WHERE Type = 'Product Script' AND STATUS = 'Active'");
	if($sth->fetchrow){
		$output .= qq|<a href="#" id="show_speech"></a>\n|;
		$output .= qq|<input type="button" value="Show script" class="button" onclick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'show_speech');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=show_products_speech&id_speech='+document.getElementById('id_products_speech').value)">|;
	}
	return $output;
}

sub posteddate_order{
#-----------------------------------------
# Forms Involved: opr_toshipped (admin.opr.cgi)
# Created on: 09/04/08  10:05:23
# Author: Roberto Barcenas
# Description : Receives an order and tries to set up its PostedDate
# Parameters : 	idorder, order_date
#
# Last Modified on: 09/04/08  10:05:23
# Last Modified by: Roberto Barcenas
# Last Modified Desc:
	
	my ($id_orders,$orddate) = @_;
	my ($posteddate,$res);
	$posteddate = '';
	$res = 'Posteddate Failed';
	#### Order with Shipping Date
	$sth_prd = &Do_SQL("SELECT ShpDate,Date FROM sl_orders_products WHERE ID_orders='$id_orders' AND ShpDate IS NOT NULL AND ShpDate<>'0000-00-00' ORDER BY ShpDate ASC");	
	($shpdate,$prd_date) = $sth_prd->fetchrow_array();
	
	
	
	### Parts Shipping Date
	#### Check Shipping Date From Notes
	$sth_prd = &Do_SQL("SELECT sl_orders_parts.ShpDate FROM sl_orders_products, sl_orders_parts WHERE ID_orders = '$id_orders' and sl_orders_products.ID_orders_products = sl_orders_parts.ID_orders_products and sl_orders_parts.ShpDate IS NOT NULL and sl_orders_parts.ShpDate <> '0000-00-00' ORDER BY sl_orders_parts.ShpDate ASC");
	$part_date = $sth_prd->fetchrow();
	if ((&date_to_unixtime($part_date) < &date_to_unixtime($shpdate) or !$shpdate) and $part_date and $part_date ne '0000-00-00'){
		 $shpdate = $part_date;
	}
	
	#### Check Shipping Date From Notes
	$sth_notes = &Do_SQL("SELECT Date FROM sl_orders_notes WHERE ID_orders='$id_orders' AND Notes like 'The Status of the Order has been changed to Shipped%' ORDER BY Date ASC");
	$note_date = $sth_notes->fetchrow();
	
	if ($note_date and $shpdate and &date_to_unixtime($prd_date)>&date_to_unixtime($note_date)){
		$posteddate = $note_date;
	}elsif ($shpdate){
		$posteddate = $shpdate;
	}elsif ($note_date){
		$posteddate = $note_date;
	}
	
	if(!$posteddate){
		$sth_prd = &Do_SQL("SELECT PostedDate FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status NOT IN('Order Cancelled', 'Inactive') AND PostedDate IS NOT NULL AND PostedDate<>'0000-00-00' ORDER BY PostedDate LIMIT 1");	
		($pdate) = $sth_prd->fetchrow_array();
	}
	
	($pdate) and ($posteddate = $pdate);
	
	if($posteddate){
		$res = 'ok';
		## Update Orders
		&Do_SQL ("UPDATE sl_orders SET PostedDate='$posteddate' WHERE ID_orders=$id_orders");
		
		## Update Products in Order
		$sth_prd = &Do_SQL("SELECT ID_orders_products,Date,SalePrice,ShpDate,ID_products FROM sl_orders_products WHERE ID_orders='$id_orders'");
		while(($id_orders_prd,$ldate,$sprice,$shpdate,$idprod) = $sth_prd->fetchrow_array()){
			if ((&date_to_unixtime($ldate)-&date_to_unixtime($orddate))>1){
				if ($sprice<0 or $idprod =~ /^4|^6/){
					&Do_SQL ("UPDATE sl_orders_products SET PostedDate='$ldate' WHERE ID_orders_products=$id_orders_prd");
				}elsif (!$shpdate and $shpdate ne '0000-00-00'){
					&Do_SQL ("UPDATE sl_orders_products SET PostedDate=NULL WHERE ID_orders_products=$id_orders_prd");
				}elsif($shpdate){
					&Do_SQL ("UPDATE sl_orders_products SET PostedDate='$shpdate' WHERE ID_orders_products=$id_orders_prd");
				}
			}else{
				&Do_SQL ("UPDATE sl_orders_products SET PostedDate='$posteddate' WHERE ID_orders_products=$id_orders_prd");
			}
		}
		
	 	## Update Payments in Order
	 	&Do_SQL ("UPDATE sl_orders_payments SET PostedDate=NULL WHERE ID_orders=$id_orders");
		$sth_pay = &Do_SQL("SELECT ID_orders_payments,Date,Amount,Paymentdate FROM sl_orders_payments WHERE ID_orders='$id_orders' AND PostedDate IS NULL");# AND Status NOT IN ('Order Cancelled', 'Cancelled')
		LINE: while( ($id_orders_pay,$ldate,$amt,$pdate) = $sth_pay->fetchrow_array()){
			$sth2 = &Do_SQL("SELECT PostedDate FROM sl_orders_payments WHERE ID_orders='$id_orders' AND Amount='$amt' AND Status='Cancelled' AND Paymentdate='$pdate'");
			$pdc = $sth2->fetchrow;
			if ($pdc ne ''){
				&Do_SQL ("UPDATE sl_orders_payments SET PostedDate='$pdc' WHERE Paymentdate='$pdate' AND ID_orders=$id_orders");
				next LINE;
			}elsif ((&date_to_unixtime($ldate)-&date_to_unixtime($orddate))>1){
				&Do_SQL ("UPDATE sl_orders_payments SET PostedDate='$ldate' WHERE ID_orders_payments=$id_orders_pay");
			}else{
        &Do_SQL ("UPDATE sl_orders_payments SET PostedDate='$posteddate' WHERE ID_orders_payments=$id_orders_pay");
			}
		}
	}
	return $res;
}


sub text_refill{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 10/10/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	my ($output) = &load_name("sl_services","ID_services",$in{'id_services_related'},"Name").": ".&load_name("sl_services","ID_services",$in{'id_services_related'},"Description");
	return $output;
}

sub refill_details{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 10/10/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if($in{'servicetype'} eq "Refill"){
		$outp = $in{'days'}." days - Product (".$in{'id_products_related'}.") ".&load_name("sl_products","ID_products",substr($in{'id_products_related'},3,6),"Name");
	}
	return $outp;
}

sub paidpo{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/17/08 15:54:53
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($sth, $rec);
	$sth=&Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders
FROM `sl_purchaseorders` 
INNER JOIN sl_wreceipts ON ( sl_purchaseorders.ID_purchaseorders = sl_wreceipts.ID_purchaseorders ) 
WHERE invoice != ''
AND NOT isnull( invoice ) 
AND InvoiceDate != ''
AND InvoiceDate != '0000-00-00'
AND NOT isnull( InvoiceDate )
AND sl_purchaseorders.ID_purchaseorders=$in{'id_purchaseorders'}");
	return "Yes" if($sth->fetchrow);
	return "No";
}

sub list_laybystatus{
#-----------------------------------------
# Created on: 11/25/08  13:09:10 By  Roberto Barcenas
# Forms Involved: opr_preorders_list
# Description : Builds an show active preorder tab by status depends on choice 
# Parameters : 
# Last modification : JRG 01/21/2009 : Se agrega la lista de cod
# Last Time Modified By RB on 2/16/10 2:06 PM : Se cambia para direccionar a Orders y se revisa que funcione para Layaway y COD
	
	my ($cad,$cod,$gen,$proc,$new,$can,$due);
	
	$cad = '';
	#&cgierr("$in{'paytype'}");
	if($in{'ptype'}){
		(!$in{'status'}) and ($gen='on') and ($new='off') and ($proc='off') and ($can='off');
		($in{'status'} and !$in{'statuspay'}) and ($gen='off')  and ($new='on') and ($proc='off') and ($can='off');
		($in{'status'} eq 'Processed') and ($gen='off') and ($new='off') and ($proc='on') and ($can='off');
		($in{'status'} eq 'Cancelled') and ($gen='off') and ($new='off') and ($proc='off') and ($can='on');
		
		if($in{'ptype'} eq 'Layaway'){
		    $due = 'off';
		    ($in{'statuspay'} eq 'Layaway Due') and ($due = 'on') and ($gen='off') and ($new='off') and ($proc='off') and ($can='off');
		    $cad = qq|<td class='gcell_$due' align='center' onClick='trjump("/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=New&statusPay=Layaway Due&so=DESC&ptype=$in{'ptype'}")'>Due</td>|;
		}

		
		
		$cad = qq|
							<table width="100%" border="0" cellspacing="0" cellpadding="0" class="gtab" align="center">
				  			<tr>
							    <td width="30%" align="center"></td>
							    <td class='gcell_$gen' align='center' onClick='trjump("/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=listall&sb=id_orders&so=DESC&ptype=$in{'ptype'}")'>All</td>
							    <td class='gcell_$new' align='center' onClick='trjump("/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=New&so=DESC&ptype=$in{'ptype'}")'>New</td>
							    <td class="gcell_$proc" align="center" onClick='trjump("/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=Processed&so=DESC&ptype=$in{'ptype'}")'>Processed</td>
							    $cad
							    <td class="gcell_$can" align="center" onClick='trjump("/cgi-bin/mod/admin/dbman?cmd=opr_orders&search=listall&sb=id_orders&status=Cancelled&so=DESC&ptype=$in{'ptype'}")'>Cancelled</td>
							  </tr>
							</table>|;
	}
}

sub list_laybypayday{
#-----------------------------------------
# Created on: 11/25/08  13:09:10 By  Roberto Barcenas
# Forms Involved: opr_preorders_payments_list
# Description : Builds an show active preorder tab by payday depends on choice 
# Parameters : 
	
	my ($cad,$td,$trd,$sd,$fd,$thd);
	$in{'range'} eq 'today' if !$in{'range'};
	($in{'range'} eq 'today') and ($td='on') and ($trd='off') and ($sd='off') and ($fd='off') and ($thd='off');
	($in{'range'} eq '3d') and ($td='off') and ($trd='on') and ($sd='off') and ($fd='off') and ($thd='off');
	($in{'range'} eq '7d') and ($td='off') and ($trd='off') and ($sd='on') and ($fd='off') and ($thd='off');
	($in{'range'} eq '15d') and ($td='off') and ($trd='off') and ($sd='off') and ($fd='on') and ($thd='off');
	($in{'range'} eq '30d') and ($td='off') and ($trd='off') and ($sd='off') and ($fd='off') and ($thd='on');
	
	$cad = qq|
						<table width="100%" border="0" cellspacing="0" cellpadding="0" class="gtab" align="center">
			  			<tr>
						    <td width="30%" align="center"></td>
						    <td class='gcell_$td' align='center' onClick='trjump("/cgi-bin/mod/admin/admin?cmd=opr_orders_payments&range=today")'>Today</td>
						    <td class='gcell_$trd' align='center' onClick='trjump("/cgi-bin/mod/admin/admin?cmd=opr_orders_payments&range=3d")'>Last  3 Days</td>
						    <td class="gcell_$sd" align="center" onClick='trjump("/cgi-bin/mod/admin/admin?cmd=opr_orders_payments&range=7d")'>Last Week</td>
						    <td class="gcell_$fd" align="center" onClick='trjump("/cgi-bin/mod/admin/admin?cmd=opr_orders_payments&range=15d")'>Last 2 Weeks</td>
						    <!--<td class='gcell_$thd' align='center' onClick='trjump("/cgi-bin/mod/admin/admin?cmd=opr_orders_payments&range=30d")'>Last Month</td>-->
						  </tr>
						</table>|;
}

sub build_select_warehouse_type {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($output);
	my (@ary) = split(/,/,$cfg{'warehouse_type'});
	for (0..$#ary){
		$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub related_adjustment{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/16/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($db, $action) = @_;
	my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_".$db."_products WHERE ID_products=600001004 AND ( isnull( Related_ID_products ) OR Related_ID_products=0)");
	$va{'error_'.$db} = $sth0->fetchrow_array;
	$error = $va{'error_'.$db};
	$va{'revised_'.$db} = 0;
	if($action){
		my($sth) = &Do_SQL("SELECT ID_".$db." FROM sl_".$db."_products WHERE ID_products=600001004 AND ( isnull( Related_ID_products ) OR Related_ID_products=0)");
		while ($rec = $sth->fetchrow_hashref){
			my($sth1) = &Do_SQL("SELECT COUNT(*) FROM sl_".$db."_products WHERE ID_".$db."='".$rec->{'ID_'.$db}."' AND LEFT(ID_products,1)<>6 ");
			$products_in_order = $sth1->fetchrow_array;
			if($products_in_order == 1){
				my ($sth1) = &Do_SQL("SELECT ID_".$db."_products, ID_products, ID_".$db." FROM sl_".$db."_products WHERE ID_".$db."='".$rec->{'ID_'.$db}."' AND ID_products<>600001004 ");
				my ($id_update_products, $id_products, $id_update) = $sth1->fetchrow_array();
				my ($sth2) = &Do_SQL("UPDATE sl_".$db."_products SET Related_ID_products='".$id_products."' WHERE ID_".$db."_products<>'".$id_update_products."' AND ID_".$db."='".$id_update."' ");
			}elsif($products_in_order > 1){
				my ($sth3) = &Do_SQL("SELECT ID_".$db."_products, ID_products, SalePrice FROM sl_".$db."_products WHERE ID_".$db."='".$rec->{'ID_'.$db}."' ");
				my (@price) = ();
				while ($pro = $sth3->fetchrow_hashref){
					my ($related_price) = "";
					if(substr($pro->{'ID_products'},0,1) != 6){
						$related_price = round($pro->{'SalePrice'} * ($cfg{'extwarrpctsfp'}/100),2);
						$pr{$pro->{'ID_products'}}=$related_price;
					}
				}
				my ($sth4) = &Do_SQL("SELECT ID_".$db."_products, ID_products, SalePrice FROM sl_".$db."_products WHERE ID_".$db."='".$rec->{'ID_'.$db}."' AND ID_products=600001004 ");
				while($upd = $sth4->fetchrow_hashref){
					@id_products=keys(%pr);
					foreach(@id_products){
						my $id = $_;
						my $precio = $pr{$_};
						my ($sth5) = &Do_SQL("SELECT COUNT(*) FROM sl_".$db."_products WHERE ID_".$db."='".$rec->{'ID_'.$db}."' AND ID_products=600001004 AND Related_ID_products='".$id."'");
						$related_num = $sth5->fetchrow_array();
						if($precio == $upd->{'SalePrice'} && $related_num < 1){
							my ($sth6) = &Do_SQL("UPDATE sl_".$db."_products SET Related_ID_products='".$id."' WHERE ID_".$db."_products='".$upd->{'ID_'.$db.'_products'}."' AND ID_products=600001004 AND ( isnull( Related_ID_products ) OR Related_ID_products=0 ) ");
#							my ($sth_log) = &Do_SQL("INSERT INTO adjustment SET ID_orders_products='".$upd->{'ID_'.$db.'_products'}."', ID_products='".$upd->{'ID_products'}."', Related_ID_products='".$id."', Price='".$upd->{'SalePrice'}."', Related_Price='".$precio."' ");
						}
					}
				}
			}
		}
		my ($sth7) = &Do_SQL("SELECT COUNT(*) FROM sl_".$db."_products WHERE ID_products=600001004 AND ( isnull( Related_ID_products ) OR Related_ID_products=0)");
		$va{'noupdated_'.$db} = $sth7->fetchrow_array;
		if($va{'noupdated_'.$db} == 0){
			$va{'error_'.$db} = 0;
			$va{'revised_'.$db} = $error;
		}elsif($va{'noupdated_'.$db} > 0){
			$va{'error_'.$db} = $va{'noupdated_'.$db};
			$va{'revised_'.$db} = $error - $va{'noupdated_'.$db};
		}
	}
	return ($va{'error_'.$db},$va{'revised_'.$db});
}




sub products_editva{
# --------------------------------------------------------
# Forms Involved:	products_form.html
# Created on: 01/25/10 12:32:51
# Author: RB.
# Description : Carga el Status de los productos en modo edicion   
# Parameters :


	if($in{'modify'}){
		if ($in{'status'} ne 'Testing'){
			my (@ary) = ('On-Air', 'Web Only','Up Sell', 'Active', 'Inactive');
			for (0..$#ary){
				if ($in{'status'} ne $ary[$_]){
					$va{'changestatus'} .= qq|<a href="/cgi-bin/mod/admin/dbman?cmd=mer_products&view=$in{'id_products'}&chgstatus=$ary[$_]&tab=$in{'tab'}">$ary[$_]</a> : |;
				}
			}
			$va{'changestatus'} = substr($va{'changestatus'},0,-2);
		}else {
			$va{changestatus} = " &nbsp; ---";
		}
		
		
		if (!$in{'testing_authby'}){
			$va{'authby'} = "---";
		}else{
			$va{'authby'} = "($in{'testing_authby'}) ". &load_db_names('admin_users','ID_admin_users',$in{'testing_authby'},'[Firstname] [Lastname]');
		}
	
	
		$va{'products_editstatus'}	=	qq|
															<tr>
														   	<td width="30%">Status : </td>
														   	<td><span class="smalltext">$in{'status'} &nbsp;&nbsp;&nbsp; </span>Change Status to : <span class='smalltext'> &nbsp; $va{'changestatus'}</span></td>
														 	</tr>|;
	}
}


sub build_sendmail_templates_list{
# --------------------------------------------------------
# Forms Involved:	eco_sendmail.html
# Created on: 06/03/2010 15:20:51
# Author: RB.
# Description : Genera radio buttons con los templates existentes para envio de email  
# Parameters :

		my $dir = $cfg{'path_templates'} . '/mod/admin/email_templates';
		$dir =~	s/\[lang\]/en/;
		my $strout = '';
	
		if(-d "$dir"){
		
		    opendir(DIR, $dir) or die $!;
				my $i=0;
		    while (my $file = readdir(DIR)) {

		       # We only want files
		        next unless (-f "$dir/$file");
		        # Use a regular expression to find files ending in .txt
		        next unless ($file =~ m/\.html$/);
		        
		       @fields = split (/\./, $file);
		       my $fname = $fields[0];
						
						$strout .= "<br>"	if $i%5==0;
						$strout .= qq|<input name="template" value="$fname" class="radio" type="radio">|. $fname .qq|&nbsp;&nbsp;&nbsp;&nbsp;|;
						$i++;
		    }
		    closedir(DIR);
		}else{
				print "No existe la ruta ". $cfg{'path_templates'} . 'email_templates';
		}
		return $strout;
}



#############################################################################
#############################################################################
#   Function: bills_amount_due_by_vendor
#
#       Es: Obtiene el Amount Due de los bills de un vendor
#       En: Gets the Amount Due of a vendor
#
#
#    Created on: 2013-06-17
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on ** by  : 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:mer_bills
#
#
sub payment_is_canceled{
	my ($id_banks_movements) = @_;

	my ($sth) = &Do_SQL("SELECT count(*) FROM sl_banks_movements_notes WHERE Type='Cancel' AND ID_banks_movements='$id_banks_movements';");
	my ($canceled)= $sth->fetchrow_array();

	return $canceled;
}


1;