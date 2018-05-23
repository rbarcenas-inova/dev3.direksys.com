#!/usr/bin/perl
####################################################################
########              Home Page                     ########
####################################################################

sub load_inventory {
# --------------------------------------------------------
	my ($id) = @_;
	my ($output,$qty,$rec);
	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses_location WHERE ID_products='$id' AND Quantity>0;");
	while ($rec = $sth->fetchrow_hashref){
		($output) and ($output .= "<br>");
		$output .= "$rec->{'Quantity'} ($rec->{'Location'})";
		$qty += $rec->{'Quantity'};
	}
	if (!$qty){
		$output .= &trans_txt('nostock');
	}
	return ($qty,$output);
}





sub set_postpay_order{
#-----------------------------------------
# Created on: 05/22/2012  12:52:33 By  Roberto Barcenas
# Forms Involved: 
# Description : Asigna una orden para envio PostPay basado en parametros de configuracion
# Parameters : 	$in{'toupdate'}

	if(!$in{'id_warehouses'} or !$cfg{'postpay_use'} or $cfg{'postpay_wh'} !~ /$in{'id_warehouses'}/){
		return;	
	}

	my $str='';
	my @ary_orders = split(/,/,$in{'toupdate'});

	for(0..$#ary_orders){

		my $id_orders = $ary_orders[$_];

		my $sumcogs=0;
		my $sumprice=0;
		$str .= "<br><br>ID_order: $id_orders<br>";

		## Orden Nueva?
		my ($sth) = &Do_SQL("SELECT IF(COUNT(*) IS NULL,0,COUNT(*)) FROM sl_orders_parts INNER JOIN
	(
		SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders='$id_orders'
	)tmp
	USING(ID_orders_products);");

		my ($total) = $sth->fetchrow();

		if($total == 0){

			&Do_SQL("UPDATE sl_orders_products SET Status='Active' WHERE ID_orders='$id_orders' AND Status='';");

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status = 'Active'");
			$va{'matches'} = $sth->fetchrow;
			if ($va{'matches'}>0){

				my ($sth1) = &Do_SQL("SELECT ID_products, SalePrice, Discount, Quantity FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status = 'Active' ORDER BY ID_orders_products");
				while (my($idp, $sprice, $discount ,$quantity) = $sth1->fetchrow){

					my ($sthk) = &Do_SQL("SELECT IsSet FROM sl_skus WHERE ID_sku_products='$idp' and Status='Active'");
					my($isset) = $sthk->fetchrow;

					if($isset eq 'Y'){

						my $tmpcogs = 0;
						my ($sth2) = &Do_SQL("SELECT 400000000+ID_parts,Qty FROM sl_skus_parts WHERE ID_sku_products='$idp';");
						while (my($id_parts,$qty) = $sth2->fetchrow){
							my ($this_cogs, $this_cost_adj) = &load_sltvcost($id_parts);
							$tmpcogs += ($this_cogs  * $qty);
							$str .= "IDPart: $id_parts, Qty: $qty , Cost: $this_cogs, COGS: $tmpcogs<br>";
						}
						#&cgierr($str);
						$sumcogs += ( $tmpcogs * $quantity );
					}else{
						$sumcogs += &load_sltvcost(substr($idp,-6)) * $quantity;
					}

					$sumprice += ( ($sprice - $discount) * $quantity );
					$str .= "ID_products:$idp -- COGS: $sumcogs -- Price: $sumprice<br>";

				}

				$sumcogs = round($sumcogs,2);
				$sumprice = round($sumprice,2);
				my $pplimit = round($sumprice * ($cfg{'postpay_cogs'} / 100) ,2);
				$str .= "COGS: $sumcogs -- Price: $sumprice<br>";

				## Order to PostPay
				if($sumcogs <= $pplimit ){
					$str .= "$sumcogs <= $pplimit , Order To Potspay<br>";

					&add_order_notes_by_type($id_orders,&trans_txt('order_to_postpay')."\nCOGS:$sumcogs\nNet:$sumprice\nLimit:$pplimit ($cfg{'postpay_cogs'}%)","'PP Order");
				}


			}
		}
	}
	return;
}



sub get_postpay_order{
#-----------------------------------------
# Created on: 05/22/2012  12:52:33 By  Roberto Barcenas
# Forms Involved: 
# Description : Revisa si la orden esta marcada para envio mediante PostPay
# Parameters : 	$in{'id_orders'}

	my $output = '';

	my ($sth) = &Do_SQL("SELECT IF(COUNT(*) > 0,'PP','') FROM sl_orders_notes WHERE ID_orders='$in{'id_orders'}' AND Type='PP Order';");
	$output = $sth->fetchrow();

	return $output;

}


#############################################################################
#############################################################################
#   Function: wreceipt_proccess_adjustments
#
#       Es: Procesa todos los registros de ajuste en un PO que no esten aun procesados
#       En: 
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#	 2015-02-16 ISC Alejandro Diaz: Se agrega sl_purchaseorders_adj.ID_wreceipts para concer con que Recepcion se usaron los ajustes
#	 2015-03-09 ISC Gilberto Quirino, Se elimina el filtro InCOGS = 'Yes', para que genere contabilidad para todos los gastos(adj)
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub wreceipt_proccess_adjustments {
#############################################################################
#############################################################################

	my ($id_po, $id_vendors, $exchange_rate) = @_;

	### Separamos el Monto General, Monto del mismo Vendor y Tax del mismo vendor
	#my ($sth) = &Do_SQL("SELECT ID_vendors,SUM(Total-Tax), SUM(Tax)AS Tax FROM sl_purchaseorders_adj WHERE ID_purchaseorders = '$id_po' AND ID_vendors != '$id_vendors' /*AND InCOGS = 'Yes'*/ AND Status = 'Active' GROUP BY ID_vendors;");	
	my ($sth) = &Do_SQL("SELECT 
							ID_purchaseorders_adj
							, ID_vendors
							, Type
							, Total-Tax
							, Tax
							, ID_accounts
							, IF(InCOGS = 'Yes', 1, 0) InCOGS
						 FROM 
						 	sl_purchaseorders_adj 
						 WHERE 
						 	ID_purchaseorders = ". $id_po ."
						 	/*AND ID_vendors != '". $id_vendors ."' /*
						 	AND InCOGS = 'Yes'*/ 
						 	AND Status = 'Active' 
						 ORDER BY 
						 	ID_purchaseorders_adj;");	
	while(my ($id_purchaseorders_adj, $idv, $type, $amt, $tax, $id_acc, $in_cogs) = $sth->fetchrow()) {

		$va{'this_accounting_time'} = time();
		my $vendor_category =lc(&load_name('sl_vendors', 'ID_vendors', $idv, 'Category'));
		########################################################
		########################################################
		## Movimientos de contabilidad
		########################################################
		########################################################
		my @params = ( $id_purchaseorders_adj, $id_po, $idv, $in{'id_wreceipts'}, $type, $amt, $tax, $exchange_rate, $id_acc, $in_cogs );
		&accounting_keypoints('po_wreceipt_in_adjustment_'. $vendor_category, \@params );

		&Do_SQL("INSERT INTO sl_vendors_notes SET ID_vendors = '$idv', Notes='P.O. : $id_po\nW. Receipt: $in{'id_wreceipts'}\nCurrency Exchange: $exchange_rate\nAmount: ". &format_price($amt)  ."/". &format_price(&round($amt * $exchange_rate,3)) . " + ". &format_price($tax) ."/". &format_price(&round($tax * $exchange_rate,3)) . "',Type='Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}' ");
		delete($va{'this_accounting_time'});

	}

	delete($va{'movs_auxiliary'}) if $va{'movs_auxiliary'};
	my ($sth) = &Do_SQL("UPDATE sl_purchaseorders_adj SET Status = 'Processed', ID_wreceipts = '$in{'id_wreceipts'}' WHERE ID_purchaseorders = '$id_po' /*AND ID_vendors != '$id_vendors' /*AND InCOGS = 'Yes'*/ AND Status = 'Active';");

}



#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f
#
#       Es: Imprime formato en Remesa para Print Out
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_execute_print_f {
#############################################################################
#############################################################################

	my (@c) = split(/,/,$cfg{'srcolors'});

	my ($sth) = &Do_SQL("SELECT COUNT(*)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches_orders.Status <> 'Cancelled'
				 AND  sl_warehouses_batches.ID_warehouses  = $in{'id_warehouses'}
				 AND  sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}
				 GROUP BY sl_orders_products.ID_orders");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){

		my $query = "SELECT sl_orders_products.ID_orders
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses = $in{'id_warehouses'}
				AND sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}
				GROUP BY sl_orders_products.ID_orders";
		my ($sth2) = &Do_SQL($query);
		&load_cfg('sl_orders');		

		while ($rec = $sth2->fetchrow_hashref){

			my %tmpord = &get_record('ID_orders',$rec->{'ID_orders'},'sl_orders');
			my $id_customer = &load_db_names('sl_orders','ID_orders',$rec->{'ID_orders'},"[ID_customers]");
			my $customer    = &load_db_names('sl_customers','ID_customers',$id_customer,"[Lastname1] [FirstName]");
			my $str_prod; my $sumprod = 0; my $sumser = 0; my $sumtax = 0; my $sumdisc = 0; my $sumshipp = 0;

			my ($sth3) = &Do_SQL("SELECT IsSet,sl_orders_products.* 
						FROM sl_orders_products 
						INNER JOIN sl_warehouses_batches_orders 
							USING(ID_orders_products)
						LEFT JOIN sl_skus 
						       ON sl_orders_products.ID_products = sl_skus.ID_sku_products
						WHERE ID_orders = '$rec->{'ID_orders'}'
						  AND sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}
						  AND sl_orders_products.Status IN('Active','Reship','Exchange');");

			while($rprod = $sth3->fetchrow_hashref()){

				$sumprod+=$rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)!= 6;
				$sumser+=$rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)== 6;
				$sumtax+= $rprod->{'Tax'};
				$sumdisc+= $rprod->{'Discount'}*-1;
				$sumshipp+= round($rprod->{'Shipping'} + $rprod->{'ShpTax'},2);

				$items++ if (substr($rprod->{'ID_products'},0,1) != 6 and $rprod->{'IsSet'}ne'Y');
				my $item = load_name('sl_products','ID_products',substr($rprod->{'ID_products'},3),"Name") if substr($rprod->{'ID_products'},0,1)!= 6;

				$str_prod .= "<tr>
						<td class='smalltext' valign='top' align='left' colspan='5' style='font-size:10px;font-weight:bold;'>$item</td>
						<td class='smalltext' valign='top' align='right' colspan='1' style='font-size:10px;font-weight:bold;'>".&format_price($rprod->{'SalePrice'})."</td>
					</tr>" if substr($rprod->{'ID_products'},0,1) != 6;

				if($rprod->{'IsSet'}eq'Y'){
					my ($sth3) = &Do_SQL("SELECT * FROM sl_".$prefix."orders_parts WHERE ID_".$prefix."orders_products = '$rprod->{'ID_orders_products'}' ");
					while($rpart = $sth3->fetchrow_hashref()){
						$items++;
						$item = load_db_names('sl_parts','ID_parts',$rpart->{'ID_parts'},"[Model]/[Name]");

						$str_prod .= "<tr>
								<td class='smalltext' valign='top' align='left' colspan='6' style='font-size:9px;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$item</td>
							</tr>"; 
						$i++;
					}
				}
				$i++;
			}

			$va{'searchresults'} .= "<table border='0' width='100%' algin='center' style='border:1px solid;font-size:9px;'>
						<tr>
							<td align='left' style='font-size:10px;'><strong>Order</strong></td><td style='font-size:10px;'>$rec->{'ID_orders'}</td>
								<td align='right' colspan='4'>$va{'cod_to_list'}</td>
						</tr>
						<tr>
							<td align='left' style='font-size:10px;'><strong>Customer</strong></td>
							<td style='font-size:10px;'>$customer</td>
							<td align='center' valign='top' style='font-size:10px;'><strong> &nbsp; </strong> $cphone</td>
							<td align='left' valign='top' style='font-size:10px;'><strong>Address</strong></td>
							<td style='font-size:10px;' width='30%'>$tmpord{'address1'}<br>$tmpord{'address2'}</td>
							<td align='right' valign='top' style='font-size:10px;'><strong>City</strong> $tmpord{'shp_city'}, $tmpord{'shp_zip'}</td>
						</tr>
						<tr class='menu_bar_title'>
							<td align='center' colspan='5'>Item</td><td align='center' colspan='1'>Sale Price</td>
						</tr>
						$str_prod
						<tr>
							<td align='right' colspan='2'>&nbsp;</td>
							<td align='right' colspan='4'>
								<table width=100% align='right' border='0'>
									<tr>
										<td align='right' style='font-size:10px;font-weight:bold;'>Subtotal: </td>
										<td align='left' style='font-size:10px;'>".&format_price($sumprod)."</td>
										<td align='right' style='font-size:10px;font-weight:bold;'>Discounts: </td>
										<td align='left' style='font-size:10px;'>".&format_price($sumdisc)."</td>
										<td align='right' style='font-size:10px;font-weight:bold;'>Tax: </td>
										<td align='left' style='font-size:10px;'>".&format_price($sumtax)."</td>
										<td align='right' style='font-size:10px;font-weight:bold;'>Services: </td>
										<td align='left' style='font-size:10px;'>".&format_price($sumser)."</td>
										<td align='right' style='font-size:10px;font-weight:bold;'>S&H: </td>
										<td align='left' style='font-size:10px;'>".&format_price($sumshipp)."</td>
										<td align='right' style='font-size:12px;font-weight:bold;color:red'>Total: </td>
										<td align='right' style='font-size:12px;font-weight:bold;'>".&format_price($sumprod+$sumtax+$sumser+$sumshipp+$sumdisc)."</td>
									</tr>
								</table>
							</td>
						</tr>
					</table>
					&nbsp;";

		}							
	}else{
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}

}


#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f2
#
#       Es: Imprime formato 2 en Remesa 
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_execute_print_f2 {
#############################################################################
#############################################################################

	## ToDo. Aqui va la funcion para sacar la conciliacion de la remesa



}


#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f3
#
#       Es: Imprime formato 3 en Remesa (Product Requirement)
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications: Alejandro Diaz
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_execute_print_f3 {
#############################################################################
#############################################################################

	my $sumqty = 0; my $sumamt = 0; my $lines = 0;
	my ($sth) = &Do_SQL("SELECT 
							sl_orders_products.ID_products
							, IsSet
							, SUM(SalePrice)
							, UPC
							, SUM(Quantity)
							, CASE 
								WHEN 
									(if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products)) >=400000000 and (if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products)) < 500000000 THEN (SELECT Name FROM sl_parts WHERE ID_parts=((if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products))-400000000)) WHEN (if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products)) >=500000000 and (if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products)) < 600000000 
								THEN 
									(SELECT Name FROM sl_noninventory WHERE ID_noninventory=((if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products))-500000000)) 
								WHEN 
									(if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products)) >=600000000 
								THEN 
									(SELECT Name FROM sl_services WHERE ID_services=((if(sl_orders_products.Related_ID_products is null,sl_orders_products.ID_products,sl_orders_products.Related_ID_products))-600000000)) 
								ELSE 
									(SELECT Name FROM sl_products WHERE ID_products=RIGHT((if(sl_orders_products.Related_ID_products is null OR sl_orders_products.Related_ID_products < 100000000,sl_orders_products.ID_products,sl_orders_products.Related_ID_products))-100000000, 6)) 
							END AS Description
						FROM sl_orders_products 
						INNER JOIN sl_warehouses_batches_orders 
							USING(ID_orders_products)
						LEFT JOIN sl_skus 
						       ON sl_orders_products.ID_products = sl_skus.ID_sku_products
						WHERE sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
						  AND sl_orders_products.Status IN('Active','Reship','Exchange') 
						  AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error') 
						GROUP BY  sl_orders_products.ID_products
						ORDER BY Description ASC;");

	while(my($idp, $isset, $sprice, $upc, $qty, $description) = $sth->fetchrow()){

		++$lines;
		$upc = 'N/A' if !$upc;
		my $name = $description;
		# substr($idp,0,1) == 6 ?
		# 			load_name('sl_services','ID_services',($idp - 600000000 ),"Name") :
		# 			load_name('sl_products','ID_products',substr($idp,-6),"Name");

		$sumamt += $sprice;
		# $va{'searchresults'} .= qq|<tr>\n
		# 							<td>|.&format_sltvid($idp).qq|</td>\n
		# 							<td>$name</td>\n|;



		if($isset eq 'Y'){

			# $va{'searchresults'} .= qq|<td>&nbsp;</td>\n
			# 						<td align="right">|.&format_price($sprice).qq|</td>\n
			# 					</tr>\n|;

			my ($sth3) = &Do_SQL("SELECT 400000000 + sl_parts.ID_parts,Name, $qty * Qty FROM sl_skus INNER JOIN sl_skus_parts USING(ID_sku_products) INNER JOIN sl_parts USING(ID_parts) WHERE ID_sku_products = '$idp' ORDER BY ID_skus_parts; ");
			while(my ($id_parts, $name, $qty) = $sth3->fetchrow()){

				++$lines;
				my $upc = load_name('sl_skus','ID_sku_products',$id_parts,"UPC");
				$upc = &format_sltvid($id_parts) if !$upc;

				$sumprod += $qty;
				$va{'searchresults'} .= qq|<tr>\n
											<td>|.$upc.qq|</td>\n
											<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$name</td>\n
											<td align="right">$qty</td>\n
											<td align="right">|.&format_price($sprice).qq|</td>\n
										</tr>\n|;

			}

		}else{
			$sumprod += $qty;
			# $va{'searchresults'} .= qq|<td align="center">$qty</td>\n
			# 						<td align="right">|.&format_price($sprice).qq|</td>\n
			# 					</tr>\n|;
		}


		if ($lines == 200){
			$lines = 0;
			$va{'searchresults'} .= qq| <DIV STYLE='page-break-before:always'></DIV>|;
		}

	}

	if($sumprod){
		$va{'searchresults'} .= qq|<tr>\n
									<td colspan="2" style="border-bottom:1px solid #555555;border-top:1px solid #555555;">&nbsp;</td>\n
									<td align="right" style="border-bottom:1px solid #555555;border-left:1px solid #555555;border-top:1px solid #555555;">$sumprod</td>\n
									<td align="right" style="border-bottom:1px solid #555555;border-left:1px solid #555555;border-top:1px solid #555555;">|.&format_price($sumamt).qq|</td>\n
								</tr>\n|;

	}else{
		$va{'searchresults'} .= qq|<tr>\n
									<td colspan="4">|.&trans_txt('search_nomatches').qq|</td>\n
								</tr>\n|;
	}


}



#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f4
#
#       Es: Imprime formato 4 en Remesa (Manifest)
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_execute_print_f4 {
#############################################################################
#############################################################################

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses  = '$in{'id_warehouses'}'
				AND sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
				AND sl_orders_products.Status IN('Active','Reship','Exchange')
				AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error') 
				GROUP BY sl_orders_products.ID_orders");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		my $lines = 0; my $sumprice = 0; my $tok = 0; my $tc = 0; my $tr = 0;
		my $query  =  "SELECT sl_orders_products.ID_orders
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses = '$in{'id_warehouses'}'
				AND sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
				AND sl_orders_products.Status IN('Active','Reship','Exchange')
				AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')
				GROUP BY sl_orders_products.ID_orders ORDER BY sl_warehouses_batches_orders.Status, ID_orders";

		my ($sth2) = &Do_SQL($query);

		&load_cfg('sl_orders');		
		while ($rec = $sth2->fetchrow_hashref){

			++$x; ++$lines;
			my %tmpord = &get_record('ID_orders',$rec->{'ID_orders'},'sl_orders');
			my $id_customer = &load_db_names('sl_orders','ID_orders',$rec->{'ID_orders'},"[ID_customers]");
			my $customer    = &load_db_names('sl_customers','ID_customers',$id_customer,"[Lastname1] [FirstName]");
			my $phone    = &load_name('sl_customers','ID_customers',$id_customer,"Phone1");

			my ($sth3) = &Do_SQL("SELECT SUM(SalePrice - Discount + IF(ABS(SalePrice) > 0.05,Tax,0) + Shipping + ShpTax),
						SUM(IF(sl_warehouses_batches_orders.Status IN('Cancelled','Error'),1,0))AS Cancelled,
						SUM(IF(sl_warehouses_batches_orders.Status = 'Returned',1,0))AS Returned,
						SUM(IF(sl_warehouses_batches_orders.Status IN('In Fulfillment','Shipped','In Transit'),1,0))AS Transit
						FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders)
						LEFT JOIN sl_warehouses_batches_orders USING(ID_orders_products)
						LEFT JOIN sl_warehouses_batches USING(ID_warehouses_batches)
						WHERE ID_orders = '$rec->{'ID_orders'}'
							AND sl_orders_products.Status IN('Active','Reship','Exchange')
							AND IF(
									LEFT(ID_products,1) = 6
									, sl_orders.PostedDate IS NULL OR sl_orders.PostedDate = '' OR sl_orders.PostedDate = '0000-00-00' OR sl_orders.PostedDate = sl_orders_products.PostedDate
									, sl_warehouses_batches_orders.ID_orders_products IS NOT NULL AND sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}' AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')
							);");		

			my ($sum, $cancelled, $returned, $intransit) = $sth3->fetchrow();

			my $res_batch = 'OK';
			($intransit > 0 and !$cancelled and !$returned)  and ($tok += 1); 
			($intransit > 0 and ($cancelled > 0 or $returned > 0)) and ($res_batch = 'Partial') and ($tok += 1);
			($cancelled > 0) and ($res_batch = 'Cancelled') and ($tc += 1);
			($returned > 0) and ($res_batch = 'Returned') and ($tr += 1);

			($res_batch =~ /OK|Partial/) and ($sumprice += round($sum,3));


			$va{'searchresults'} .= qq|<tr>\n
									<td nowrap>$rec->{'ID_orders'}</td>\n
										<td>$res_batch</td>\n
										<td>$customer</td>\n
										<td>$phone</td>\n
										<td>$tmpord{'shp_state'}</td>\n
										<td>$tmpord{'shp_city'}</td>\n
										<td>$tmpord{'ptype'}</td>\n
										<td nowrap>|.&format_price($sum).qq|</td>\n
									</tr>|;

			if ($lines == 200){
				$lines = 0;
				$va{'searchresults'} .= qq| <DIV STYLE='page-break-before:always'></DIV>|;
			}

		}


		if($sumprice){
		$va{'searchresults'} .= qq|<tr>\n
									<td colspan="7"  style="border-bottom:1px solid #555555;border-left:1px solid #555555;border-top:1px solid #555555;"> Total Orders: $x &nbsp;&nbsp;&nbsp;&nbsp; Total OK: $tok &nbsp;&nbsp;&nbsp;&nbsp; Total Cancelled: $tc &nbsp;&nbsp;&nbsp;&nbsp; Total Returned: $tr </td>\n
									<td align="right" style="border-bottom:1px solid #555555;border-left:1px solid #555555;border-top:1px solid #555555;">|.&format_price($sumprice).qq|</td>\n
								</tr>\n|;
		}else{
			$va{'searchresults'} .= qq|<tr>\n
										<td colspan="8">|.&trans_txt('search_nomatches').qq|</td>\n
									</tr>\n|;
		}


	}

}



#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f5
#
#       Es: Imprime formato 5 en Remesa (Packing Slip)
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_rewrite_print_f5 {
#############################################################################
#############################################################################

	$va{'cmd5'} = 'opr_orders';
	$va{'f5'} = '6';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses  = '$in{'id_warehouses'}'
					AND  sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					AND sl_orders_products.Status IN('Active','Reship','Exchange','Inactive')
				  	AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')
				 GROUP BY sl_orders_products.ID_orders");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		my $lines = 0; my $sumprice = 0;
		&Do_SQL("SET group_concat_max_len = 1073741824;");
		my $query  =  "SELECT GROUP_CONCAT(DISTINCT ID_orders ORDER BY ID_orders)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses = '$in{'id_warehouses'}'
					AND sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					AND sl_orders_products.Status IN('Active','Reship','Exchange','Inactive')
				 	AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')";

		my ($sth2) = &Do_SQL($query);
		$va{'toprint5'} = $sth2->fetchrow();

	}

	$va{'toprint5'} .= qq|&id_warehouses_batches=$in{'id_warehouses_batches'}&id_warehouses=$in{'id_warehouses'}|;

}


#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f6
#
#       Es: Imprime formato 6 en Remesa (Shipping Label)
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:24092014::AD::Se agrega estaus 'Inactive' a filtro
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_rewrite_print_f6 {
#############################################################################
#############################################################################

	$va{'cmd6'} = 'opr_orders';
	$va{'f6'} = '7';


	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses  = $in{'id_warehouses'}
				 	AND  sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}
				 	AND sl_orders_products.Status IN('Active','Reship','Exchange','Inactive')
				  	AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')
				 GROUP BY sl_orders_products.ID_orders");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		my $lines = 0; my $sumprice = 0;
		&Do_SQL("SET group_concat_max_len = 1073741824;");
		my $query  =  "SELECT GROUP_CONCAT(DISTINCT sl_orders_products.ID_orders)
						FROM sl_warehouses_batches_orders
						INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
						INNER JOIN sl_orders_products USING(ID_orders_products)
						WHERE sl_warehouses_batches.ID_warehouses = '$in{'id_warehouses'}'
							AND   sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
							AND sl_orders_products.Status IN('Active','Reship','Exchange','Inactive')
						 	AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')";

		my ($sth2) = &Do_SQL($query);
		$va{'toprint6'} = $sth2->fetchrow();

	}

	$va{'toprint6'} .= qq|&id_warehouses_batches=$in{'id_warehouses_batches'}&id_warehouses=$in{'id_warehouses'}&print_upc=1|;
}

#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f7
#
#       Es: Imprime formato 7 en Remesa (Packing Slip)
#       En: 
#
#
#    Created on: 2013-09-25
#
#    Author: _Alejandro Diaz_
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_rewrite_print_f7 {
#############################################################################
#############################################################################

	$va{'cmd7'} = 'opr_orders';
	$va{'f7'} = '6';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses  = '$in{'id_warehouses'}'
					AND  sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					AND sl_orders_products.Status IN('Active','Reship','Exchange','Inactive')
				  	AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')
				 GROUP BY sl_orders_products.ID_orders");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		my $lines = 0; my $sumprice = 0;
		&Do_SQL("SET group_concat_max_len = 1073741824;");
		my $query  =  "SELECT GROUP_CONCAT(DISTINCT sl_orders_products.ID_orders)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses = '$in{'id_warehouses'}'
					AND sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					AND sl_orders_products.Status IN('Active','Reship','Exchange','Inactive')
					AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')";

		my ($sth2) = &Do_SQL($query);
		$va{'toprint7'} = $sth2->fetchrow();

	}

	# $va{'toprint7'} .= qq|&id_warehouses_batches=$in{'id_warehouses_batches'}&id_warehouses=$in{'id_warehouses'}&print_upc=1|;
	$va{'toprint7'} .= qq|&id_warehouses_batches=$in{'id_warehouses_batches'}&id_warehouses=$in{'id_warehouses'}&print_upc=1|;
}

#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f8
#
#       Es: Imprime formato 8 de Remesa Ordenado(New Product Requirement)
#       En: 
#
#
#    Created on: 2014-01-20
#
#    Author: ISC Alejandro Diaz
#
#
#
#   Parameters:
#
#      - id_po: ID_warehouses_batches
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_execute_print_f8 {
#############################################################################
#############################################################################

	my $sumqty = 0; my $sumamt = 0; my $lines = 0;
	my ($sth3) = &Do_SQL("
	SELECT products.ID_products, parts.SKU, parts.Name, products.Quantity * parts.Qty AS Quantity, products.SalePrice
	FROM (
		SELECT sl_orders_products.ID_products, IsSet, SUM(SalePrice)SalePrice, UPC, SUM(Quantity)Quantity
		FROM sl_orders_products 
		INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
		LEFT JOIN sl_skus ON sl_orders_products.ID_products = sl_skus.ID_sku_products
		WHERE sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
		AND sl_orders_products.Status IN('Active','Reship','Exchange')
		AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error') 
		GROUP BY sl_orders_products.ID_products
	)products
	INNER JOIN (
		SELECT 400000000 + sl_parts.ID_parts as SKU, Name, Qty, IsSet, ID_sku_products
		FROM sl_skus 
		INNER JOIN sl_skus_parts USING(ID_sku_products) 
		INNER JOIN sl_parts USING(ID_parts) 
		ORDER BY ID_skus_parts
	) parts ON parts.ID_sku_products=products.ID_products
	ORDER BY parts.Name;");
	while(my ($idp, $id_parts, $name, $qty, $sprice) = $sth3->fetchrow()){

		++$lines;
		$sumamt += $sprice;
		$sumprod += $qty;
		my $upc = load_name('sl_skus','ID_sku_products',$id_parts,"UPC");
		$upc = &format_sltvid($id_parts) if !$upc;

		$va{'searchresults'} .= qq|<tr>\n
									<td>|.$upc.qq|</td>\n
									<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$name</td>\n
									<td align="right">$qty</td>\n
									<td align="right">|.&format_price($sprice).qq|</td>\n
								</tr>\n|;

	}

	if ($lines == 200){
		$lines = 0;
		$va{'searchresults'} .= qq| <DIV STYLE='page-break-before:always'></DIV>|;
	}

	if($sumprod){
		$va{'searchresults'} .= qq|<tr>\n
									<td colspan="2" style="border-bottom:1px solid #555555;border-top:1px solid #555555;">&nbsp;</td>\n
									<td align="right" style="border-bottom:1px solid #555555;border-left:1px solid #555555;border-top:1px solid #555555;">$sumprod</td>\n
									<td align="right" style="border-bottom:1px solid #555555;border-left:1px solid #555555;border-top:1px solid #555555;">|.&format_price($sumamt).qq|</td>\n
								</tr>\n|;

	}else{
		$va{'searchresults'} .= qq|<tr>\n
									<td colspan="4">|.&trans_txt('search_nomatches').qq|</td>\n
								</tr>\n|;
	}

}

#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f9
#
#       Es: Imprime formato 9 en Remesa
#       En: 
#
#
#    Created on: 2014-04-14
#
#    Author: _Alejandro Diaz_
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_rewrite_print_f9 {
#############################################################################
#############################################################################

	$va{'cmd9'} = 'opr_orders';
	$va{'f8'} = '7';

	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses  = '$in{'id_warehouses'}'
					AND  sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					AND sl_orders_products.Status IN('Active','Reship','Exchange')
				  	AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')
				 GROUP BY sl_orders_products.ID_orders");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

		my $lines = 0; my $sumprice = 0;
		&Do_SQL("SET group_concat_max_len = 1073741824;");
		my $query  =  "SELECT GROUP_CONCAT(DISTINCT sl_orders_products.ID_orders)
				FROM sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches USING(ID_warehouses_batches)
				INNER JOIN sl_orders_products USING(ID_orders_products)
				WHERE sl_warehouses_batches.ID_warehouses = '$in{'id_warehouses'}'
					AND sl_warehouses_batches_orders.ID_warehouses_batches = '$in{'id_warehouses_batches'}'
					AND sl_orders_products.Status IN('Active','Reship','Exchange')
					AND sl_warehouses_batches_orders.Status NOT IN ('Cancelled','Error')";

		my ($sth2) = &Do_SQL($query);
		$va{'toprint9'} = $sth2->fetchrow();

	}

	$va{'toprint9'} .= qq|&id_warehouses_batches=$in{'id_warehouses_batches'}&id_warehouses=$in{'id_warehouses'}&print_upc=1|;

}

#############################################################################
#############################################################################
#   Function: warehouses_batches_export
#
#       Es: Exporta los diferentes formatos. En formato historico aparecen las ordenes canceladas, en formato vista de remesas no. 
#       En: 
#
#
#    Created on: 2013-06-05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_po: ID_purchaseorders
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#		<warehouses_batches_export_layout>
#
sub warehouses_batches_export {
#############################################################################
#############################################################################

	## ToDo. Formatos diferentes por empresa. Validar $in{'e'}
	# print "Content-type: text/html\n\n";
	# print "Content-Type: text/csv\n";
	# print "Content-disposition: attachment; filename=".$in{'cmd'}."_".&get_date().".csv\n\n";

	&auth_logging('warehouses_batches_export');
	$va{'cmd'} = 'warehouses_batches';
	my $mod2;
	my $modhead; 
	my $modhead_history;
	my $str_to_print='';

	$in{'id_warehouses'} =~ s/\|/,/g;
	$in{'id_warehouses'} =~ s/$\,//;

	if($in{'history'}){

		(!$in{'from_date'}) and ($in{'from_date'} = &get_sql_date());
		(!$in{'to_date'}) and ($in{'to_date'} = &get_sql_date());

		(!$in{'f'}) and ($in{'f'} = 1 );

		$mod2 = $in{'id_warehouses'} ? " AND sl_warehouses_batches.ID_warehouses IN (".$in{'id_warehouses'}.") " : "";
		
		if($in{'f'} != 5 and $in{'f'} != 6){
			$modhead = '"MENSAJERIA","EN REMESA",';
		}
			
	}


	if($in{'id_warehouses'} eq '' && $in{'id_warehouses_batches'} ){
		my $sth = &Do_SQL("SELECT ID_warehouses  FROM sl_warehouses_batches WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'}));
		$in{'id_warehouses'} = $sth->fetchrow;
	}

	my $mod = $in{'from_date'} ? " $mod2 AND sl_warehouses_batches.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' " : " AND sl_warehouses_batches.ID_warehouses  IN(".$in{'id_warehouses'}.") AND  sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}";

	###########
	########### Headers Print	

	# print $modhead . $sys{'db_'.$va{'cmd'}.'_expo'.$in{'f'}} . "\n";
	$str_to_print .= $modhead . $sys{'db_'.$va{'cmd'}.'_expo'.$in{'f'}} . "\n";


	my ($sth) = &Do_SQL("SELECT COUNT(*)
	FROM sl_warehouses_batches_orders
	INNER JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
	INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
	WHERE 1 $mod
	GROUP BY sl_orders_products.ID_orders");
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0) {

		my $query  =  "SELECT 
			sl_orders_products.ID_orders
			,sl_orders_products.ID_products
			,(sl_orders_products.SalePrice + sl_orders_products.Shipping + sl_orders_products.Tax) as cost
			, sl_warehouses_batches_orders.ID_warehouses_batches
			, sl_warehouses_batches.ID_warehouses
			, sl_warehouses_batches.Date
			, sl_warehouses_batches.Time
			, sl_warehouses_batches.Status
			, sl_warehouses_batches_orders.ScanDate
			, sl_warehouses.Name AS Warehouse
		FROM sl_warehouses_batches_orders
		INNER JOIN sl_warehouses_batches ON sl_warehouses_batches.ID_warehouses_batches=sl_warehouses_batches_orders.ID_warehouses_batches
		INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_warehouses_batches.ID_warehouses
		INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
		WHERE 1 $mod
		GROUP BY sl_orders_products.ID_orders,sl_warehouses_batches_orders.ID_warehouses_batches 
		ORDER BY sl_warehouses_batches.ID_warehouses_batches,sl_orders_products.ID_orders;";

		my ($sth2) = &Do_SQL($query);
		&load_cfg('sl_orders');		

		ORDERS: while ($rec = $sth2->fetchrow_hashref){

			my $intransit=0; my $cancelled=0; my $returned=0;

			$in{'id_warehouses_batches'} = $rec->{'ID_warehouses_batches'};
			$in{'date'} = $rec->{'Date'};
			$in{'time'} = $rec->{'Time'};
			my $wb_status = $rec->{'Status'};
			my $modhead_history =$rec->{'Warehouse'};

			$query = "SELECT 
			sl_customers.ID_customers,
			UPPER(CONCAT(IFNULL(sl_customers.LastName1,''),' ',IFNULL(sl_customers.FirstName,''))),
			UPPER(CONCAT(IFNULL(FirstName,''),' ',IFNULL(Lastname1,''),' ',IFNULL(Lastname2,''))),
			sl_customers.Phone1,
			sl_customers.Phone2,
			sl_customers.Cellphone,
			sl_customers.atime,
			IF(sl_customers.Email = '' OR sl_customers.Email IS NULL,'info\@inova.com',sl_customers.Email) Email,
			sl_salesorigins.Channel
			, REPLACE(sl_orders.shp_address1,'\"','')shp_address1
			, REPLACE(sl_orders.shp_address2,'\"','')shp_address2
			, REPLACE(sl_orders.shp_address3,'\"','')shp_address3
			, sl_orders.shp_Urbanization
			, REPLACE(sl_orders.shp_Notes,'\"','')shp_Notes
			, REPLACE(sl_orders.OrderNotes,'\"','')OrderNotes
			, sl_orders.Ptype
			, LPAD(sl_orders.shp_Zip,5,'0') shp_Zip
			, UPPER(sl_orders.shp_State) AS shp_State
			, UPPER(sl_orders.shp_City) AS shp_City
			, sl_orders.Date
			, sl_orders.ID_orders
			, sl_orders.Status
			FROM sl_orders
			INNER JOIN sl_customers ON sl_orders.ID_customers=sl_customers.ID_customers
			INNER JOIN sl_salesorigins ON sl_salesorigins.ID_salesorigins=sl_orders.ID_salesorigins
			WHERE sl_orders.ID_orders=$rec->{'ID_orders'}";
			my ($sth3) = &Do_SQL($query);
			my ($id_customer, $customer, $customer_full_name, $phone, $phone2, $phone3, $atime, $email, $origin, $shp_address1, $shp_address2, $shp_address3, $shp_urbanization, $shp_notes, $ordernotes, $ptype, $shp_zip, $shp_state, $shp_city, $date, $id_orders, $status) = $sth3->fetchrow_array();

			my $sumprod = 0; my $sumser = 0; my $sumtax = 0; my $sumdisc = 0; my $sumshipp = 0;my $tracking;
			
			my $address	= "$shp_address1 $shp_address2 $shp_address3";
			my $address1= $shp_address1;
			my $address23= "$shp_address2 $shp_address3";
			my $between_streets = $shp_address2;
			my $reference = $shp_address3;
			my $prods=''; my $reship=0; my $exchange=0;
			my $catname;
			my $suburb = $shp_urbanization;
			my $notes = $shp_notes;
			my $order_notes = $ordernotes;

			# f3
			my $street_number = $shp_address1;
			
			#f5
			#my %tmpprod = &get_record('ID_products',$rec->{'ID_products'},'sl_products');
			my $f5_ID_orders=$rec->{'ID_orders'}; #OrdVta
			my $f5_warehouse_name=$modhead_history; #mensajeria
			my $f5_warehouse_batch=$rec->{'ID_warehouses_batches'}; #remesa
			my $f5_tpay=$ptype; #Tipo de pago
			my $f5_tot=$rec->{'cost'}; #Cost;
			my $f5_customer=$customer; #Cliente
			my $f5_zip=$shp_zip; #CP
			my $f5_state=$shp_state; #Estado
			my $f5_city=$shp_city; #Municipio
			my $f5_address=$address; #calle
			my $f5_urbanization=$suburb; #colonia
			my $f5_streets=$reference; #Entre calles
			my $f5_reference=$notes; #referencias
			my $f5_notes=$notes; #notas
			my $f5_ordnotes=$order_notes; #notas de orden
			my $f5_phone=$phone; #telcasa
			my $substringid=substr $rec->{'ID_products'}, 3, 6;
			my $f5_product=&load_name('sl_products', 'ID_products',$substringid, 'Name' );

			#cgierr("Name ". $f5_product);
			 # use Data::Dumper;
			 # cgierr(Dumper \%f5_product);

			my ($scandate) = $rec->{'ScanDate'};

			my ($stht) = &Do_SQL("SELECT COUNT(DISTINCT ID_warehouses_batches) -1 FROM sl_orders_products 
			INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)
			WHERE ID_orders = '$rec->{'ID_orders'}' 
			GROUP BY ID_orders;");

			my ($t) = $stht->fetchrow();
			$t = 0 if $t < 0;
			my $tracking = $rec->{'ID_orders'} . $t;


			$sth3 = &Do_SQL("SELECT IsSet,sl_orders_products.*,
			IF(sl_warehouses_batches_orders.Status IN('Cancelled','Error') AND ID_warehouses_batches = $in{'id_warehouses_batches'},1,0)AS Cancelled,
			IF(sl_warehouses_batches_orders.Status = 'Returned' AND ID_warehouses_batches = $in{'id_warehouses_batches'},1,0)AS Returned,
			IF(sl_warehouses_batches_orders.Status IN('In Fulfillment','Shipped','In Transit') AND ID_warehouses_batches = $in{'id_warehouses_batches'},1,0)AS Transit 
			FROM sl_orders_products 
			LEFT JOIN sl_warehouses_batches_orders USING(ID_orders_products)
			LEFT JOIN sl_skus ON sl_orders_products.ID_products = sl_skus.ID_sku_products
			WHERE ID_orders = $rec->{'ID_orders'}
			AND (sl_orders_products.Status IN('Active','ReShip','Exchange') OR (sl_orders_products.Status = 'Inactive' AND sl_warehouses_batches_orders.Status = 'Returned'))
			AND IF( LEFT(sl_orders_products.ID_products,1) = 6,1, sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products AND ID_warehouses_batches = $in{'id_warehouses_batches'})
			GROUP BY sl_orders_products.ID_orders_products;");

			$prodline = 0;
			while($rprod = $sth3->fetchrow_hashref()){
				++$prodline;
						
				###
				### Product Family
				###
				if($prodline == 1) {
					
					if(!$idcat){
						
						my ($sthc) = Do_SQL("SELECT ID_categories FROM sl_products_categories WHERE ID_products = RIGHT($rprod->{'ID_products'},6) LIMIT 1;");
						$idcat = $sthc->fetchrow();

					}

					$catname = $idcat ? &load_name('sl_categories','ID_categories', $idcat, 'Title') : 'N/A';

				}

				$sumprod += $rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)!= 6;
				$sumser += $rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)== 6;
				$sumtax += $rprod->{'Tax'} if abs($rprod->{'SalePrice'}) > 0.05;
				$sumdisc += $rprod->{'Discount'};
				$sumshipp += $rprod->{'Shipping'};
				$sumshipp += $rprod->{'ShpTax'} if abs($rprod->{'Shipping'}) > 0.05;

				#$tracking = $rprod->{'Tracking'};
				($rprod->{'Reship'}) and ($reship=1) and ($exchange=0);
				($rprod->{'Exchange'}) and ($exchange=1) and ($reship=0);

				$items++ if (substr($rprod->{'ID_products'},0,1) != 6 and $rprod->{'IsSet'}ne'Y');

				($rprod ->{'In Transit'}) and ($intransit += 1);
				($rprod ->{'Cancelled'}) and ($cancelled += 1);
				($rprod ->{'Returned'}) and ($returned += 1);

			undef $idcat;

			}
			
			$sumshipp = round($sumshipp,2);
			my $sumtot = round($sumprod + $sumser + $sumtax + $sumshipp - $sumdisc,2);
			my $carriage = $sumtot;

			if ($in{'f'} == 7) {
				if ($carriage < 4000) {
					$carriage = '';
				}
			}
			my $res_batch = 'OK';

			($intransit > 0 and ($cancelled > 0 or $returned > 0)) and ($res_batch = 'Partial');
			($cancelled > 0) and ($res_batch = 'Cancelled');
			($returned > 0) and ($res_batch = 'Returned');
			($wb_status eq 'Void') and ($res_batch = 'Void');

			#### Estatus de los productos del pedido actual en la remesa
			my $qry_st_prod = "SELECT GROUP_CONCAT(DISTINCT sl_warehouses_batches_orders.Status)
								FROM sl_warehouses_batches_orders
									INNER JOIN sl_orders_products ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products
								WHERE sl_warehouses_batches_orders.ID_warehouses_batches = ".$in{'id_warehouses_batches'}." AND sl_orders_products.ID_orders = ".$rec->{'ID_orders'}."
								GROUP BY sl_warehouses_batches_orders.ID_warehouses_batches;";
			my $sth_st_prod = &Do_SQL($qry_st_prod);
			my $stat_prod_batch = $sth_st_prod->fetchrow();

			####
			#### In Batch View Cancelled Orders should be Skipped
			####
			(!$in{'history'} and $res_batch eq 'Cancelled') and (next ORDERS);

			####
			#### Driver in History
			####
			if($in{'f'} != 5 and $in{'f'} != 6){
				# ($in{'history'}) and (print qq|"$modhead_history","$res_batch",|);
				($in{'history'}) and ($str_to_print .= qq|"$modhead_history","$res_batch",|);
			}
			if(!$va{'export_perm'}){

				$str_to_print .= qq|"$id_orders"\n|;

			}else{


				if($in{'f'} ==  1){

					#REMESA,NOMBRE,CP,DOMICILIO,COLONIA,TELEFONOS,MUNICIPIO,ESTADO,MTOTAL,PRODUCTOS,NUMGUIA,ORDVTA,REENVIO,CAMBIOFIS,TPAGO,INDICACIONES,OBSERVACIONES
					$str_to_print .= qq|"$in{'id_warehouses_batches'}","$customer","$shp_zip","$address","$shp_urbanization","$phone","$shp_city","$shp_state","$sumtot","$prods","$tracking","$id_orders","$reship","$exchange","$ptype","$shp_notes","$ordernotes"\n|;

				}elsif($in{'f'} ==  2){

					if($phone2 ne ''){ $phone2 = '/ '.$phone2; }
					if($phone3 ne ''){ $phone3 = '/ '.$phone3; }

					#REMESA,NOMBRE,CP,DOMICILIO,COLONIA,ENTRE CALLES,TELEFONOS,MUNICIPIO,ESTADO,MTOTAL,NUMGUIA,ORDVTA,TPAGO,INDICACIONES,TIEMPO_DISPONIBLE
					$str_to_print .= qq|"$in{'id_warehouses_batches'}","$customer","$shp_zip","$address1","$address23","$shp_urbanization","$phone $phone2 $phone3","$shp_city","$shp_state","$sumtot","$tracking","$id_orders","$ptype","$shp_notes","$catname","$atime"\n|;
				
				}elsif($in{'f'} == 3){	

					$str_to_print .= qq|"$in{'id_warehouses_batches'}","$stat_prod_batch","$date","$scandate","$origin","$ptype","$status","$id_orders","$tracking","$sumshipp","$sumtot","$customer","$shp_zip","$shp_state","$shp_city","$address1","$suburb","$between_streets","$reference","$notes","$order_notes","$phone","$in{date}","$in{time}","$catname"\n|; 
				}elsif($in{'f'} == 4){

					# REC	COMPANY	CONTACT	ADR1	ADR2	CITY	STATE	ZIPCODE	WEIGHT	PHONE	LENGTH	WIDTH	HEIGHT	REF	INVOICE	PO	CARRIAGE	SERVICE	PACKAGING	DESCRIPTION	RECIPIENT EMAIL	COUNTRY	COD	AMOUNT	DEP
					my ($sth_state) = &Do_SQL("SELECT sl_vars.Subcode, sl_vars.Definition_Sp FROM sl_vars WHERE VName = 'estados_fedex' AND VValue=(SELECT State FROM sl_zipcodes WHERE StateFullName='$shp_state' LIMIT 1);");
					my ($fedex_abb, $fedex_state) = $sth_state->fetchrow_array();


					if($ptype eq 'COD'){

						$str_to_print .= qq|"$tracking","|.uc(&replace_accents($shp_address2)).qq|","|.uc(&replace_accents($customer_full_name)).qq|","|.uc(&replace_accents($shp_address1)).qq|","|.uc(&replace_accents($shp_urbanization)).qq|","|.uc(&replace_accents($shp_city)).qq|","$fedex_abb","$shp_zip","10","$phone","105","40","15","$tracking","|.uc(&replace_accents($atime)).qq|","|.uc(&replace_accents($shp_address3)).qq| |.uc(&replace_accents($shp_notes)).qq| |.uc(&replace_accents($ordernotes)).qq|","$sumtot","XS","YOUR PACKAGING","SINGLE SALES","|.lc($email).qq|","MX","Y","$sumtot","$in{'id_warehouses_batches'}"\n|;
					
					}else{

						$str_to_print .= qq|"$tracking","|.uc(&replace_accents($shp_address2)).qq|","|.uc(&replace_accents($customer_full_name)).qq|","|.uc(&replace_accents($shp_address1)).qq|","|.uc(&replace_accents($shp_urbanization)).qq|","|.uc(&replace_accents($shp_city)).qq|","$fedex_abb","$shp_zip","10","$phone","105","40","15","$tracking","|.uc(&replace_accents($atime)).qq|","|.uc(&replace_accents($shp_address3)).qq| |.uc(&replace_accents($shp_notes)).qq| |.uc(&replace_accents($ordernotes)).qq|","$sumtot","XS","YOUR PACKAGING","SINGLE SALES","|.lc($email).qq|","MX","","","$in{'id_warehouses_batches'}"\n|;
					}
				}elsif($in{'f'} == 5){	
					           #ORDVTA	,        MENSAJERIA	,         REMESA	,          TPAGO	,TOTAL	,   CLIENTE	,       CP	,   ESTADO	,  MUNICIPIO   ,CALLE	,    COLONIA	,     ENTRE CALLES,     REFERENCIAS	,  NOTAS	,NOTAS DE ORDEN	,TELCASA   ,PRODUCTO																			
					$str_to_print .= qq|"$f5_ID_orders","$f5_warehouse_name","$f5_warehouse_batch","$f5_tpay","$f5_tot","$f5_customer","$f5_zip","$f5_state","$f5_city","$f5_address","$f5_urbanization","$f5_streets","$f5_reference","$f5_notes","$f5_ordnotes","$f5_phone","$f5_product"\n|; 
				}elsif($in{'f'} == 6){				
					           				#NUMGUIA  PAQUETES						NOMBRE								PAIS						NOMBRE										DOMICILIO			  				COLONIA				CP    TELEFONOS		MUNICIPIO	 ESTADO			REMESA				MENSAJERIA 			FECHA REMESA
					$str_to_print .= qq|"$tracking","PAQUETES","|.uc(&replace_accents($customer_full_name)).qq|","","","MX","|.uc(&replace_accents($customer_full_name)).qq|","$shp_address1, $shp_address3, $shp_address2","","$shp_urbanization","$shp_zip","$phone","","$shp_city","$shp_state","$f5_warehouse_batch","$f5_warehouse_name","$rec->{'Date'}"\n|; 
				}elsif($in{'f'} == 7){				
					# REC	COMPANY	CONTACT	ADR1	ADR2	CITY	STATE	ZIPCODE	WEIGHT	PHONE	LENGTH	WIDTH	HEIGHT	REF	INVOICE	PO	CARRIAGE	SERVICE	PACKAGING	DESCRIPTION	RECIPIENT EMAIL	COUNTRY	COD	AMOUNT	DEP
					my ($sth_state) = &Do_SQL("SELECT sl_vars.Subcode, sl_vars.Definition_Sp FROM sl_vars WHERE VName = 'estados_fedex' AND VValue=(SELECT State FROM sl_zipcodes WHERE StateFullName='$shp_state' LIMIT 1);");
					my ($fedex_abb, $fedex_state) = $sth_state->fetchrow_array();

					my $shp_address2_custom = "COL. ".$shp_urbanization.". ENTRE ".$shp_address2.". ".$shp_notes;

					if($ptype eq 'COD'){

						$str_to_print .= qq|"$tracking","|.uc(&replace_accents($customer_full_name)).qq|","|.uc(&replace_accents($customer_full_name)).qq|","|.uc(&replace_accents($shp_address1)).qq|","|.uc(&replace_accents($shp_address2_custom)).qq|","|.uc(&replace_accents($shp_city)).qq|","$fedex_abb","\t|.$shp_zip.qq|","10","$phone","105","40","15","$tracking","|.uc(&replace_accents($atime)).qq|","|.uc(&replace_accents($shp_address3)).qq| |.uc(&replace_accents($shp_notes)).qq| |.uc(&replace_accents($ordernotes)).qq|","$carriage","XS","YOUR PACKAGING","SINGLE SALES","|.lc($email).qq|","MX","Y","$sumtot","$in{'id_warehouses_batches'}"\n|;
					
					}else{

						$str_to_print .= qq|"$tracking","|.uc(&replace_accents($customer_full_name)).qq|","|.uc(&replace_accents($customer_full_name)).qq|","|.uc(&replace_accents($shp_address1)).qq|","|.uc(&replace_accents($shp_address2_custom)).qq|","|.uc(&replace_accents($shp_city)).qq|","$fedex_abb","\t|.$shp_zip.qq|","10","$phone","105","40","15","$tracking","|.uc(&replace_accents($atime)).qq|","|.uc(&replace_accents($shp_address3)).qq| |.uc(&replace_accents($shp_notes)).qq| |.uc(&replace_accents($ordernotes)).qq|","$carriage","XS","YOUR PACKAGING","SINGLE SALES","|.lc($email).qq|","MX","","","$in{'id_warehouses_batches'}"\n|;
					}
				}

			} #$va{'export_perm'}

		}

	}

	print "Content-Type: text/csv\n";
	print "Content-disposition: attachment; filename=".$in{'cmd'}."_".&get_date().".csv\n\n";
	print $str_to_print;

	return;

}


#############################################################################
#############################################################################
#   Function: sl_warehouses_batches_execute_print_f10
#
#       Es: Format INVOICES
#       En: 
#
#
#    Created on: 30 - 08 - 2017
#
#    Author: Fabian Cañaveral
#
#
#
#   Parameters:
#
#      - id_po: ID_warehouses_batches
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<view_warehouses_batches>
#
sub warehouses_batches_execute_print_f10 {
#############################################################################
#############################################################################
	use JSON;
	use LWP::UserAgent;
	use Data::Dumper;
	my %args = @_;
	my %response;
	my $ua = LWP::UserAgent->new;
	my %parameters = %args;
	my $id_invoices  = &Do_SQL(qq|
		select group_concat(Distinct i.ID_invoices)
		from sl_warehouses_batches wb
		inner join sl_warehouses_batches_orders wbo on wb.ID_warehouses_batches = wbo.ID_warehouses_batches
		inner join sl_orders_products op on op.ID_orders_products = wbo.ID_orders_products
		inner join sl_orders o on o.ID_orders = op.ID_orders
		inner join cu_invoices_lines il on o.ID_orders = il.ID_orders
		inner join cu_invoices i on i.ID_invoices = il.ID_invoices
		where 1
			and wb.id_warehouses_batches = '$in{'toprint'}'
			and i.`Status` = 'Certified'
			and i.invoice_type = 'Traslado'
		group by o.ID_orders
		|)->fetchrow();
	my $url = $cfg{'api_getinvoice_url'}.qq|?e=$in{'e'}&invoices=$id_invoices&format=pdf|;
	# cgierr($url);
	my $response = $ua->get(
		$url,
		"Authorization" => "Bearer $cfg{'api_getinvoice_token'}"
	);

	use MIME::Base64;
	if($response){
    	$encoded = encode_base64($response->content);
	}
    $va{'ids'} = $id_invoices;
    $va{'pdf'} = $encoded;
	# my $old_fh = select(STDOUT);
	# $| = 1;
	# select($old_fh);
	# print "Content-Type: application/pdf\n\n";
	# # print "Content-Length: " .length($response->content) . "\n\n";
	# print $response->content;
	# exit();
	# $va{'response'} = 
	# cgierr('HOLA');

}


1;