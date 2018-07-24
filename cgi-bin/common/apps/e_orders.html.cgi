#!/usr/bin/perl

sub stdedition{
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	my ($err, $key, $idx, $rec);
	##################################################
	#### Defaults / Validation
	##################################################	
	$in{'id_orders'} = int($in{'id_orders'});

	###############
	###############
	###############
	## Order has exchange records?
	###############
	###############
	###############
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders = '$in{'id_orders'}' AND merAction = 'Exchange' AND Status = 'Resolved';");
	my ($exchange_on) = $sth->fetchrow();

	# Contemplate tax zero
	if ($cfg{'e_orders_tax_zero'} and $cfg{'e_orders_tax_zero'} ne '' and !$in{'taxmode'}){		
		my $sth = &Do_SQL("SELECT count(*) FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE sl_customers.Currency != '' AND sl_customers.Currency != '$cfg{'e_orders_tax_zero'}' AND ID_orders='$in{'id_orders'}'");
		my $tax_zero = $sth->fetchrow_array;
		if ($tax_zero){
			$in{'taxmode'} = 'off';
		}
	}
	$in{'taxmode'} = 'on' if (!$in{'taxmode'});

	$va{'status'} = &load_name("sl_orders","ID_orders",$in{'id_orders'},"Status");
	$va{'id_orders'} = $in{'id_orders'};
	my ($locked) = ($va{'status'} =~ /Shipped|Processed|Cancelled|System Error/ and !&check_permissions('edit_order_forced_mode','','')) ? 1 : 0;

	if (&check_permissions('edit_order_ajaxmode','','') and $in{'id_orders'} and !$locked) {
		
		#### Individual perms
		$va{'productlist_visible'} = '';
		$va{'paymentlist_visible'} = '';
		if( int($cfg{'edit_order_perm'}) == 1 ){
			$va{'productlist_visible'} = (&check_permissions('edit_order_products','','')) ? '' : "display: none;";
			$va{'paymentlist_visible'} = (&check_permissions('edit_order_payments','','')) ? '' : "display: none;";
		}

		##################################################
		#### Actions
		##################################################
		if ($in{'action'} and ($in{'tax_onoff.x'} or $in{'tax_onoff'})){
			if (&check_permissions('edit_order_taxonoff','','') or &check_permissions('edit_order_forced_mode','','')){
				### Check Permision
				if ($in{'taxmode'} eq 'on'){
					$in{'taxmode'} = 'off';
				}else{
					$in{'taxmode'} = 'on';
				}
			}else{
				$va{'message'} = &trans_txt('apporders_taxunauth');
			}
		}

		if ($in{'return'}){

			delete($in{'add_product'});
			delete($in{'add_sku'});
			delete($in{'add_service'});
			delete($in{'add_promo'});
			delete($in{'add_cod'});
			delete($in{'add_card'});
			delete($in{'add_deposit'});
			delete($in{'add_depositref'});
			delete($in{'to_edit'});
			delete($in{'save'});

		}elsif($in{'action'} and ($in{'add_product.x'} or $in{'add_product'})){
			$in{'add_product'} = 1;
		}elsif($in{'action'} and ($in{'add_sku.x'} or $in{'add_sku'})){
			$in{'add_sku'} = 1;
		}elsif($in{'action'} and ($in{'add_service.x'} or $in{'add_service'})){
			$in{'add_service'} = 1;
		}elsif($in{'action'} and ($in{'add_promo.x'} or $in{'add_promo'})){
			$in{'add_promo'} = 1;
		}elsif($in{'action'} and ($in{'add_cod.x'} or $in{'add_cod'})){
			$in{'add_cod'} = 1;
		}elsif($in{'action'} and ($in{'add_card.x'} or $in{'add_card'})){
			$in{'add_card'} = 1;
		}elsif($in{'action'} and ($in{'add_deposit.x'} or $in{'add_deposit'})){
			$in{'add_deposit'} = 1;
		}elsif($in{'action'} and ($in{'add_depositref.x'} or $in{'add_depositref'})){
			$in{'add_depositref'} = 1;
		}elsif($in{'action'} and ($in{'to_enable.x'} or $in{'to_enable'})){
			$in{'to_enable'} = 1;
		}elsif($in{'action'} and ($in{'to_disable.x'} or $in{'to_disable'})){
			$in{'to_disable'} = 1;
		}elsif($in{'action'} and ($in{'to_duplicate.x'} or $in{'to_duplicate'})){
			$in{'to_duplicate'} = 1;
		}elsif($in{'action'} and ($in{'to_edit.x'} or $in{'to_edit'})){
			$in{'to_edit'} = 1;
		}elsif($in{'action'} and ($in{'save.x'} or $in{'add_card'})){
			$in{'save'} = 1;
		}


		##################################################
		############ PRODUCTS FROM ACTUAL ORDER
		##################################################
		$query_add = '';
		if($cfg{'productos_create_newline'}){
			$query_add = qq| AND status not in('Inactive') |;
		}
		my $sth = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}' $query_add ORDER BY ID_orders_products, Status");
		while ($rec = $sth->fetchrow_hashref){

			++$va{'prod_matches'};
			$prods{'idordersproducts_'.$va{'prod_matches'}} = $rec->{'ID_orders_products'};
			$prods{'idproducts_'.$rec->{'ID_orders_products'}} = $rec->{'ID_products'};
			$prods{'idrelated_'.$rec->{'ID_orders_products'}} = $rec->{'Related_ID_products'};
			$prods{'idpromo_'.$rec->{'ID_orders_products'}} = $rec->{'Related_ID_products'} if ($rec->{'Related_ID_products'});
			$prods{'quantity_'.$rec->{'ID_orders_products'}} = $rec->{'Quantity'};
			$prods{'idprice_'.$rec->{'ID_orders_products'}} = $rec->{'ID_products_prices'};
			$prods{'saleprice_'.$rec->{'ID_orders_products'}} = ($rec->{'Quantity'} > 0)?($rec->{'SalePrice'}/$rec->{'Quantity'}):0;
			$prods{'discount_'.$rec->{'ID_orders_products'}} = $rec->{'Discount'};
			$prods{'shipping_'.$rec->{'ID_orders_products'}} = $rec->{'Shipping'};
			$prods{'shpdate_'.$rec->{'ID_orders_products'}} = $rec->{'ShpDate'};
			$prods{'shpdate_'.$rec->{'ID_orders_products'}} = '' if ($prods{'shpdate_'.$rec->{'ID_orders_products'}} eq '0000-00-00');
			$prods{'taxp_'.$rec->{'ID_orders_products'}} = $rec->{'Tax_percent'};
			$prods{'taxp_'.$rec->{'ID_orders_products'}} = 0 if (!$prods{'taxp_'.$rec->{'ID_orders_products'}});
			$prods{'taxshp_'.$rec->{'ID_orders_products'}} = $rec->{'ShpTax_percent'};
			$prods{'taxshp_'.$rec->{'ID_orders_products'}} = 0 if (!$prods{'taxshp_'.$rec->{'ID_orders_products'}});
			$prods{'status_'.$rec->{'ID_orders_products'}} = $rec->{'Status'};
			
			## New Info
			my (@ary) = ('quantity_','idprice_','saleprice_','discount_','shipping_','status_');
			for my $i(0..$#ary){
				if ($in{'new'.$ary[$i].$rec->{'ID_orders_products'}} and !$in{'reset'}){
					$prods{'new'.$ary[$i].$rec->{'ID_orders_products'}} = $in{'new'.$ary[$i].$rec->{'ID_orders_products'}}
				}else{
					$prods{'new'.$ary[$i].$rec->{'ID_orders_products'}} = $prods{$ary[$i].$rec->{'ID_orders_products'}}
				}
			}
		}


		##################################################
		############ PRODUCTS FORM IN (new Lines)
		##################################################
		if(!$in{'reset'}){

			foreach my $key (keys %in){
				if ($key =~ /newproduct_(\d+)/){
					$idx = $1;
					$prods{'newproduct_'.$idx} = 1;
					$prods{'newidproducts_'.$idx} = $in{'newidproducts_'.$idx};
					$prods{'newidrelated_'.$idx} = $in{'newidrelated_'.$idx};
					$prods{'newquantity_'.$idx} = $in{'newquantity_'.$idx};
					$prods{'newidprice_'.$idx} = $in{'newidprice_'.$idx};
					$prods{'newsaleprice_'.$idx} = $in{'newsaleprice_'.$idx};
					$prods{'newshipping_'.$idx} = $in{'newshipping_'.$idx};
					$prods{'newdiscount_'.$idx} = $in{'newdiscount_'.$idx};
					$prods{'newstatus_'.$idx} = $in{'newstatus_'.$idx};
					$prods{'newstatus_'.$idx} = 'Exchange' if (!$prods{'newstatus_'.$idx} and $exchange_on);
					$prods{'newstatus_'.$idx} = 'Active' if (!$prods{'newstatus_'.$idx});
					$prods{'newidpromo_'.$idx} = $in{'newidpromo_'.$idx} if ($in{'newidpromo_'.$idx});
					$in{'lastidx'} = $idx if($in{'lastidx'}<$idx);
				}
			}
		}


		##################################################
		############ PAYMENTS FROM ACTUAL ORDER
		##################################################
		my $sth = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders=$in{'id_orders'}");
		while ($rec = $sth->fetchrow_hashref){
			++$va{'pmts_matches'};
			$pmts{'idorderspayments_'.$va{'pmts_matches'}} = $rec->{'ID_orders_payments'};
			$pmts{'type_'.$rec->{'ID_orders_payments'}} = $rec->{'Type'};
			$pmts{'amount_'.$rec->{'ID_orders_payments'}} = $rec->{'Amount'};
			$pmts{'paymentdate_'.$rec->{'ID_orders_payments'}} = $rec->{'Paymentdate'};
			$pmts{'capdate_'.$rec->{'ID_orders_payments'}} = $rec->{'CapDate'};
			$pmts{'capdate_'.$rec->{'ID_orders_payments'}} = '' if ($pmts{'capdate_'.$rec->{'ID_orders_payments'}} eq '0000-00-00');
			for (1..11){
				$pmts{'pmtfield'.$_.'_'.$rec->{'ID_orders_payments'}} = $rec->{'PmtField'.$_};	
			}
			$pmts{'status_'.$rec->{'ID_orders_payments'}} = $rec->{'Status'};
			## New Info
			if(!$in{'reset'}){
				my (@ary) = ('updamount_','updpaymentdate_','updstatus_');
				for (0..$#ary){
					if ($in{$ary[$_].$rec->{'ID_orders_payments'}}){
						$pmts{$ary[$_].$rec->{'ID_orders_payments'}} = $in{$ary[$_].$rec->{'ID_orders_payments'}};
					}
				}
			}
		}

		##################################################
		############ PAYMENTS FORM IN (new Lines)
		##################################################
		if(!$in{'reset'}){
			foreach my $key (keys %in){
				if ($key =~ /newpmt_(\d+)/){
					$idx = $1;
					$pmts{'newpmt_'.$idx} = 1;
					$pmts{'newpmttype_'.$idx} = $in{'newpmttype_'.$idx};
					$pmts{'newamount_'.$idx} = $in{'newamount_'.$idx};
					$pmts{'newpaymentdate_'.$idx} = $in{'newpaymentdate_'.$idx};
					$pmts{'newpmtstatus_'.$idx} = $in{'newpmtstatus_'.$idx};
					$pmts{'newpmtpuntos_'.$idx} = $in{'newpmtpuntos_'.$idx};
					for (1..11){
						$pmts{'newpmtfield'.$_.'_'.$idx} = $in{'newpmtfield'.$_.'_'.$idx};	
					}
					$in{'lastpidx'} = $idx if($in{'lastpidx'}<$idx);
				}
			}
		}
		##################################################
		############ Actions in Same Page
		##################################################		
		if ($in{'to_enable'}){
			$va{'message'} = &to_enable;
		}elsif($in{'to_disable'}){
			$va{'message'} = &to_disable;
		}elsif($in{'to_duplicate'}){
			$va{'message'} = &to_duplicate;
		}
		$va{'productslist'} = &build_productslist;
		$va{'paymentslist'} = &build_paymentlist;
		
		
		
		##################################################
		############ Difference and Submit Button
		##################################################
		$va{'tdifference'} =  &round($va{'totalproducts'},$sys{'fmt_curr_decimal_digits'})-&round($va{'totalpayments'},$sys{'fmt_curr_decimal_digits'});
		$va{'tdiff'}       = &format_price($va{'tdifference'});
		if ($va{'tdifference'} ne 0){
			++$err;
			if ($in{'save'}){
				delete($in{'save'});
				$va{'productslist'} = &build_productslist;
			}
		}elsif($in{'save'}){
			print &confirmation;
			return;
		}
		
		## 9006864
		## 9002354
		
		##################################################
		############ Actions in NEW Page
		##################################################		
		if ($in{'add_product'}){
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			print &add_product();
		}elsif($in{'add_sku'}){
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			print &add_sku();
		}elsif($in{'add_service'}){
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			print &add_service();
		}elsif($in{'add_promo'}){
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			print &add_promo();
		}elsif($in{'add_cod'}){
			print &add_cod;
		}elsif($in{'add_card'}){
			print &add_card;
		}elsif($in{'add_deposit'}){
			print &add_deposit;
		}elsif($in{'add_depositref'}){
			print &add_depositref;
		}elsif($in{'to_edit'}){
			print &to_edit;
		}else{
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			if ($err>0){
				$va{'btndiffclass'} = 'diff';
				$va{'btndiff'} = qq|<input type="image" src="/sitimages/orders/calc.png" class="calc" name="recalc" value="on" border="0">|;
			}else{
				$va{'btndiffclass'} = 'diffok';
				$va{'btndiff'} = qq|<input type="image" src="/sitimages/orders/update.png" class="calc" name="save" value="on" border="0">|;
			}
			$orderShipment = $cfg{'use_default_shipment'} and $cfg{'use_default_shipment'} == 1 ? true : false;
			$va{'display'} = 'none';
			if($orderShipment){
				$va{'display'} = 'block';
			}
			print &build_page('apporders/stdedition.html');
		}
	}else{
		if ($locked){
			$va{'message'} = "<b>".$va{'id_orders'}."</b>".&trans_txt('apporders_cant_edit')." <b>".$va{'status'}."</b>.";
			print &build_page('locked.html');
		}else{
			##ToDo: Pagina de no autorizado
			print &build_page('unauth_small.html');
		}
	}
}
sub build_productslist{
# --------------------------------------------------------
	my ($key, $output, $d, %rec, $print_line, $idx, $id_products);
	my (@c) = split(/,/,$cfg{'srcolors'});

	my ($idcust) = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
	foreach my $key (sort { $prods{$a} <=> $prods{$b} } keys %prods){
		$print_line = 0;
		my $line_bg_style = '';

		if ($key =~ /idordersproducts_(\d+)/){

			###################################
			### Building Existing Lines
			###################################
			%rec = ();
			$rec{'id_orders_products'} = $prods{'idordersproducts_'.$1};
			# &cgierr($prods{'idrelated_'.$rec{'id_orders_products'}}.'-->');

			if ($prods{'idrelated_'.$rec{'id_orders_products'}} < 500000000 and $prods{'idrelated_'.$rec{'id_orders_products'}} > 400000000){

				#####################
				#####################
				#####################
				# is an SKU
				#####################
				#####################
				#####################
				$rec{'ptype'} = 'sku';
				$rec{'id_products'} = &format_sltvid($prods{'idrelated_'.$rec{'id_orders_products'}});
				$id_products = $prods{'idrelated_'.$rec{'id_orders_products'}};
				$rec{'prodname'} = &load_name('sl_parts','ID_parts',substr($prods{'idrelated_'.$rec{'id_orders_products'}},3,9),'Name');
				$_status = '';
				if($prods{'newstatus_'.$rec{'id_orders_products'}} eq 'Inactive'){
					$_status = 'readonly="readonly"';
				}
				$rec{'quantity'} = qq|<input type="text" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" $_status>\n|;

			}elsif($prods{'idproducts_'.$rec{'id_orders_products'}} < 700000000 and $prods{'idproducts_'.$rec{'id_orders_products'}} > 600000000 or ($prods{'idrelated_'.$rec{'id_orders_products'}} < 700000000 and $prods{'idrelated_'.$rec{'id_orders_products'}} > 600000000)){

				#####################
				#####################
				#####################
				## is a Service
				#####################
				#####################
				#####################

				if ($prods{'idproducts_'.$rec{'id_orders_products'}} < 700000000 and $prods{'idproducts_'.$rec{'id_orders_products'}} > 600000000){
					$rec{'ptype'} = 'services';
					$rec{'id_products'} = &format_sltvid($prods{'idproducts_'.$rec{'id_orders_products'}});
					$id_products = $prods{'idproducts_'.$rec{'id_orders_products'}};
					$rec{'prodname'} = &load_name('sl_services','ID_services',substr($prods{'idproducts_'.$rec{'id_orders_products'}},3,9),'Name');
					$prods{'newquantity_'.$rec{'id_orders_products'}} = 1 if (!$prods{'newquantity_'.$rec{'id_orders_products'}});				
					if (!&check_permissions('edit_order_edit_qty','','')){
						$rec{'quantity'} = qq|<input type="hidden" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" >$prods{'newquantity_'.$rec{'id_orders_products'}}\n|;
					}else{
						$_status = '';
						if($prods{'newstatus_'.$rec{'id_orders_products'}} eq 'Inactive'){
							$_status = 'readonly="readonly"';
						}
						$rec{'quantity'} = qq|<input type="text" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" $_status>\n|;
					}
				}else{
					$rec{'ptype'} = 'services';
					$rec{'id_products'} = &format_sltvid($prods{'idrelated_'.$rec{'id_orders_products'}});
					$id_products = $prods{'idrelated_'.$rec{'id_orders_products'}};
					$rec{'prodname'} = &load_name('sl_services','ID_services',substr($prods{'idrelated_'.$rec{'id_orders_products'}},3,9),'Name');
					$prods{'newquantity_'.$rec{'id_orders_products'}} = 1 if (!$prods{'newquantity_'.$rec{'id_orders_products'}});				
					if (!&check_permissions('edit_order_edit_qty','','')){
						$rec{'quantity'} = qq|<input type="hidden" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" >$prods{'newquantity_'.$rec{'id_orders_products'}}\n|;
					}else{
						$_status = '';
						if($prods{'newstatus_'.$rec{'id_orders_products'}} eq 'Inactive'){
							$_status = 'readonly="readonly"';
						}
						$rec{'quantity'} = qq|<input type="text" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" $_status>\n|;
					}

				}

			}elsif($prods{'idproducts_'.$rec{'id_orders_products'}} < 900000000 and $prods{'idproducts_'.$rec{'id_orders_products'}} > 800000000){

				#####################
				#####################
				#####################
				## is a Credit Memo
				#####################
				#####################
				#####################
				$rec{'ptype'} = 'services';
				$rec{'id_products'} = &format_sltvid($prods{'idproducts_'.$rec{'id_orders_products'}});
				$id_products = $prods{'idproducts_'.$rec{'id_orders_products'}};

				my ($sth) = &Do_SQL("SELECT `sl_creditmemos`.Description FROM sl_orders_products INNER JOIN sl_creditmemos_products ON Related_ID_products = ID_creditmemos INNER JOIN sl_creditmemos USING(ID_creditmemos) WHERE ID_orders = '$in{'id_orders'}' AND sl_orders_products.ID_products = '$id_products' GROUP BY ID_creditmemos;");
				$rec{'prodname'} = $sth->fetchrow();				
				$rec{'quantity'} = qq|<input type="hidden" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" >$prods{'newquantity_'.$rec{'id_orders_products'}}\n|;
				
			}else{

				#####################
				#####################
				#####################
				## is a Product
				#####################
				#####################
				#####################
				$rec{'ptype'} = 'products';
				$rec{'id_products'} = &format_sltvid($prods{'idproducts_'.$rec{'id_orders_products'}});
				$id_products = $prods{'idproducts_'.$rec{'id_orders_products'}};
				$rec{'prodname'} = &load_db_names('sl_products','ID_products',substr($prods{'idproducts_'.$rec{'id_orders_products'}},3,9),'[Name] / [Model]');
				$rec{'quantity'} = 1;

			}

			if (!&check_permissions('edit_order_forced_mode','','') and ($prods{'newstatus_'.$rec{'id_orders_products'}} =~ /Inactive|Returned/ or $prods{'shpdate_'.$rec{'id_orders_products'}})){

				#####################
				#####################
				#####################
				## User not allowed to make changes
				#####################
				#####################
				#####################	
				$rec{'unitprice'} = qq|<input type="hidden" name="newsaleprice_$rec{'id_orders_products'}" value="$prods{'newsaleprice_'.$rec{'id_orders_products'}}" >\n|. &format_price($prods{'newsaleprice_'.$rec{'id_orders_products'}});
				$rec{'discount'}  = qq|<input type="hidden" name="newdiscount_$rec{'id_orders_products'}" value="$prods{'newdiscount_'.$rec{'id_orders_products'}}" >\n|. &format_price($prods{'newdiscount_'.$rec{'id_orders_products'}});
				$rec{'shipping'}  = qq|<input type="hidden" name="newshipping_$rec{'id_orders_products'}" value="$prods{'newshipping_'.$rec{'id_orders_products'}}" >\n|. &format_price($prods{'newshipping_'.$rec{'id_orders_products'}});
				$rec{'shipping'}  .= qq|<input type="hidden" name="newstatus_$rec{'id_orders_products'}" value="$prods{'newstatus_'.$rec{'id_orders_products'}}" >\n|;

			}else{

				#####################
				#####################
				#####################
				## User with permissions Granted
				#####################
				#####################
				#####################
				$rec{'unitprice'} = qq|<input type="text" size="10" name="newsaleprice_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newsaleprice_'.$rec{'id_orders_products'}}" >\n|;
				$_status = '';
				if($prods{'newstatus_'.$rec{'id_orders_products'}} eq 'Inactive'){
					$_status = 'readonly="readonly"';
				}
				$rec{'discount'}  = qq|<input type="text" size="10" name="newdiscount_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newdiscount_'.$rec{'id_orders_products'}}" $_status>\n|;
				$rec{'shipping'}  = qq|<input type="text" size="10" name="newshipping_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newshipping_'.$rec{'id_orders_products'}}" $_status>\n|;
				$rec{'shipping'}  .= qq|<input type="hidden" name="newstatus_$rec{'id_orders_products'}" value="$prods{'newstatus_'.$rec{'id_orders_products'}}" >\n|;
			}

			### Additional permission to edit Prices
			if(!&check_permissions('edit_order_edit_price','','') or ($rec{'id_orders_products'} > 0 and $prods{'idproducts_'.$rec{'id_orders_products'}} < 600000000 and $prods{'idrelated_'.$rec{'id_orders_products'}} > 0 )){
				$rec{'unitprice'} = qq|<input type="hidden" name="newsaleprice_$rec{'id_orders_products'}" value="$prods{'newsaleprice_'.$rec{'id_orders_products'}}" >\n|. &format_price($prods{'newsaleprice_'.$rec{'id_orders_products'}});
				$rec{'shipping'}  = qq|<input type="hidden" name="newshipping_$rec{'id_orders_products'}" value="$prods{'newshipping_'.$rec{'id_orders_products'}}" >\n|. &format_price($prods{'newshipping_'.$rec{'id_orders_products'}});
				$rec{'shipping'}  .= qq|<input type="hidden" name="newstatus_$rec{'id_orders_products'}" value="$prods{'newstatus_'.$rec{'id_orders_products'}}" >\n|;
			}

			### Additional permission to edit Discount
			if(!&check_permissions('edit_order_edit_discount','','')){
				$rec{'discount'}  = qq|<input type="hidden" name="newdiscount_$rec{'id_orders_products'}" value="$prods{'newdiscount_'.$rec{'id_orders_products'}}" >\n|. &format_price($prods{'newdiscount_'.$rec{'id_orders_products'}});
			}

			### Promo in Order
			if ($rec{'id_orders_products'} > 0  and $prods{'idproducts_'.$rec{'id_orders_products'}} < 600000000 and $prods{'idrelated_'.$rec{'id_orders_products'}} > 0 and $prods{'idrelated_'.$rec{'id_orders_products'}} < 400000000){
				$_status = '';
				if($prods{'newstatus_'.$rec{'id_orders_products'}} eq 'Inactive'){
					$_status = 'readonly="readonly"';
				}

				$rec{'unitprice'} .= qq|<input type="hidden" name="newidpromo_$rec{'id_orders_products'}" value="$prods{'idrelated_'.$rec{'id_orders_products'}}" $_status>\n|;
				$rec{'shipping'}  = qq|<input type="text" size="10" name="newshipping_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newshipping_'.$rec{'id_orders_products'}}" $_status>\n|;
				$rec{'shipping'}  .= qq|<input type="hidden" name="newstatus_$rec{'id_orders_products'}" value="$prods{'newstatus_'.$rec{'id_orders_products'}}" $_status>\n|;
			}

			
			#######
			######## 1721.55
			######### TODO: AQUI ME QUEDE.  - Revisando ediciones que queden con status Exchange


			my ($tax_prd) = &calc_taxprod($id_products, $rec{'id_orders_products'});
			$rec{'tax'} = &round($tax_prd *100,2) ."%";
			
			### Check Line Condition
			$rec{'linetype'} = &trans_txt('cond_original');
			my (@ary) = ('quantity_','idprice_','saleprice_','discount_','shipping_','status_');
			for my $i(0..$#ary){
				if ($prods{'new'.$ary[$i].$rec{'id_orders_products'}} ne $prods{$ary[$i].$rec{'id_orders_products'}}){
					$rec{'linetype'} = "<span style='Color:Red'>".&trans_txt('cond_edited')."</span>";
				}
			}
			### Locked Shipped Lines
			if ($prods{'shpdate_'.$rec{'id_orders_products'}} and !&check_permissions('edit_order_forced_mode','','')){
				$rec{'action'} = "";
				$rec{'linetype'} = "<b>".&trans_txt('cond_shipped')."</b>";	
			}else{
				$rec{'action'}   = qq|<input type="checkbox" name="action_$rec{'id_orders_products'}" value="on" class="checkbox">|;
			}
			$print_line = 1;


		}elsif($key =~ /newproduct_(\d+)/){

			###################################
			### Building New Lines
			###################################
			%rec = ();
			my ($idx) = $1;
			$rec{'id_orders_products'} = $idx;
			$line_bg_style = qq|style="background-color:#DBF0E6;font-weight:bold;"|;
			

			if ($prods{'newidrelated_'.$idx} < 500000000 and $prods{'newidrelated_'.$idx} > 400000000){

				#####################
				#####################
				#####################
				## is a sku
				#####################
				#####################
				#####################
				$rec{'ptype'} = 'sku';
				$rec{'id_products'} = &format_sltvid($prods{'newidrelated_'.$idx});
				$id_products = $prods{'newidrelated_'.$idx};
				$rec{'prodname'} = &load_name('sl_parts','ID_parts',substr($prods{'newidrelated_'.$idx},3,9),'Name');
				$rec{'quantity'} = qq|<input type="text" size="10" name="newquantity_$idx" class="inputsm" value="$prods{'newquantity_'.$idx}" >\n|;
				$rec{'shipping'}  = qq|<input type="text" size="10" name="newshipping_$idx" class="inputsm" value="$prods{'newshipping_'.$idx}" >\n|;

			}elsif($prods{'newidproducts_'.$idx}<700000000 and $prods{'newidproducts_'.$idx}>600000000){

				#####################
				#####################
				#####################
				## is a service
				#####################
				#####################
				#####################
				$rec{'ptype'} = 'services';
				$rec{'id_products'} = &format_sltvid($prods{'newidproducts_'.$idx});
				$id_products = $prods{'newidproducts_'.$idx};
				$rec{'prodname'} = &load_name('sl_services','ID_services',substr($prods{'newidproducts_'.$idx},3,9),'Name');
				# $rec{'quantity'} = 1;
				$prods{'newquantity_'.$idx} = 1 if (!$prods{'newquantity_'.$idx});
				
				if (!&check_permissions('edit_order_edit_qty','','')){
					$rec{'quantity'} = qq|<input type="hidden" size="10" name="newquantity_$idx" class="inputsm" value="$prods{'newquantity_'.$idx}" >$prods{'newquantity_'.$idx}\n|;
				}else{
					$rec{'quantity'} = qq|<input type="text" size="10" name="newquantity_$idx" class="inputsm" value="$prods{'newquantity_'.$idx}" >\n|;
				}

				$rec{'shipping'}  = qq|<input type="hidden" name="newshipping_$idx" value="0" >---\n|;

			}elsif($prods{'newidproducts_'.$idx} < 900000000 and $prods{'newidproducts_'.$idx} > 800000000){

				#####################
				#####################
				#####################
				## is a Credit Memo
				#####################
				#####################
				#####################
				$rec{'ptype'} = 'services';
				$rec{'id_products'} = &format_sltvid($prods{'idproducts_'.$rec{'id_orders_products'}});
				$id_products = $prods{'idproducts_'.$rec{'id_orders_products'}};

				my ($sth) = &Do_SQL("SELECT `sl_creditmemos`.Description FROM sl_orders_products INNER JOIN sl_creditmemos_products ON Related_ID_products = ID_creditmemos INNER JOIN sl_creditmemos USING(ID_creditmemos) WHERE ID_orders = '$in{'id_orders'}' AND sl_orders_products.ID_products = '$id_products' GROUP BY ID_creditmemos;");
				$rec{'prodname'} = $sth->fetchrow();				
				$rec{'quantity'} = qq|<input type="hidden" size="10" name="newquantity_$rec{'id_orders_products'}" class="inputsm" value="$prods{'newquantity_'.$rec{'id_orders_products'}}" >$prods{'newquantity_'.$rec{'id_orders_products'}}\n|;

			}else{

				## is a Product
				$rec{'ptype'} = 'products';
				$rec{'id_products'} = &format_sltvid($prods{'newidproducts_'.$idx});
				$rec{'id_products'} = &format_sltvid($prods{'newidproducts_'.$idx});
				
				$id_products = $in{'newidproducts_'.$idx};
				$rec{'prodname'} = &load_db_names('sl_products','ID_products',substr($prods{'newidproducts_'.$idx},3,9),'[Name] / [Model]');
				$rec{'quantity'} = 1;
				$prods{'newquantity_'.$idx} = 1;
				$rec{'shipping'}  = qq|<input type="text" size="10" name="newshipping_$idx" class="inputsm" value="$prods{'newshipping_'.$idx}" >\n|;

			}
			
			if ($in{'newidpromo_'.$idx}){

				$rec{'unitprice'} = qq|<input type="hidden" size="10" name="newsaleprice_$idx" class="inputsm" value="$prods{'newsaleprice_'.$idx}" >$prods{'newsaleprice_'.$idx}\n|;
				$rec{'unitprice'} .= qq|<input type="hidden" name="newidprice_$idx" value="$prods{'newidprice_'.$idx}">\n|;
				$rec{'unitprice'} .= qq|<input type="hidden" name="newidpromo_$idx" value="$in{'newidprice_'.$idx}">\n|;
				$rec{'discount'}  = qq|<input type="hidden" size="10" name="newdiscount_$idx" class="inputsm" value="$prods{'newdiscount_'.$idx}" >$prods{'newdiscount_'.$idx}\n|;

			}else{

				###################
				## Excepcion: Precio de de Ultima Compra para Cliente Intercompañia
				###################
				my $locked_price = ($cfg{'e_orders_use_last_po_price'} and $cfg{'e_orders_use_last_po_price'}==1 and ($cfg{'e_orders_use_last_po_price_'.$idcust} and $cfg{'e_orders_use_last_po_price_'.$idcust} ne ''))?1:0;

				if (!&check_permissions('edit_order_edit_price','','') or $locked_price){

					$rec{'unitprice'} = qq|<input type="hidden" name="newsaleprice_$idx" class="inputsm" value="$prods{'newsaleprice_'.$idx}" >\n|. &format_price($prods{'newsaleprice_'.$rec{'id_orders_products'}});

				}else{

					$rec{'unitprice'} = qq|$locked_price<input type="text" size="10" name="newsaleprice_$idx" class="inputsm" value="$prods{'newsaleprice_'.$idx}" >\n|;

				}

				$rec{'unitprice'} .= qq|<input type="hidden" name="newidprice_$idx" value="$prods{'newidprice_'.$idx}">\n|;
				### Validate permission to edit Discount
				if (!&check_permissions('edit_order_edit_discount','','')){
					$rec{'discount'}  = qq|<input type="hidden" size="10" name="newdiscount_$idx" class="inputsm" value="$prods{'newdiscount_'.$idx}" >$prods{'newdiscount_'.$idx}\n|;
				}else{
					$rec{'discount'}  = qq|<input type="text" size="10" name="newdiscount_$idx" class="inputsm" value="$prods{'newdiscount_'.$idx}" >\n|;
				}

			}

			$rec{'linetype'} = &trans_txt('cond_new');
			$rec{'action'}   = qq|<input type="checkbox" name="action_$idx" value="on" class="checkbox">
							<input type="hidden" name="newproduct_$idx" value="1">
							<input type="hidden" name="newidproducts_$idx" value="$prods{'newidproducts_'.$idx}">
							<input type="hidden" name="newstatus_$idx" value="$prods{'newstatus_'.$idx}">
							<input type="hidden" name="newidrelated_$idx" value="$prods{'newidrelated_'.$idx}">|;
			$print_line = 1;

		}


		if ($print_line){

			my ($tax_shp) = &calc_taxshp($id_products);
			my ($tax_prd) = &calc_taxprod($id_products, $rec{'id_orders_products'});

			if ($prods{'newstatus_'.$rec{'id_orders_products'}} eq 'Inactive'){

				$style_status = "style='text-decoration: line-through;'";

			}else{

				## Only Active Products
				$rec{'tax'}       = &round($tax_prd *100,2) ."%";
				$va{'total_quantity'} += $prods{'newquantity_'.$rec{'id_orders_products'}};
				$va{'total_discount'} += $prods{'newdiscount_'.$rec{'id_orders_products'}};
				$va{'total_shipping'} += $prods{'newshipping_'.$rec{'id_orders_products'}};
				$va{'total_subtotal'} += (($prods{'newquantity_'.$rec{'id_orders_products'}}*$prods{'newsaleprice_'.$rec{'id_orders_products'}})-$prods{'newdiscount_'.$rec{'id_orders_products'}});
				$va{'tax_product'}     = &round(((($prods{'newquantity_'.$rec{'id_orders_products'}} * $prods{'newsaleprice_'.$rec{'id_orders_products'}}) - $prods{'newdiscount_'.$rec{'id_orders_products'}}) * $tax_prd),$sys{'fmt_curr_decimal_digits'});
				$va{'tax_shipping'}	   = &round(($prods{'newshipping_'.$rec{'id_orders_products'}}* $tax_shp),$sys{'fmt_curr_decimal_digits'});
				$va{'total_tax'}      += ($va{'tax_product'} + $va{'tax_shipping'});

				$style_status = "";
				$va{'total'} += (($prods{'newquantity_'.$rec{'id_orders_products'}}*$prods{'newsaleprice_'.$rec{'id_orders_products'}})-$prods{'newdiscount_'.$rec{'id_orders_products'}})
					+ 
					$prods{'newshipping_'.$rec{'id_orders_products'}}
					+
					($va{'tax_shipping'} + $va{'tax_product'});
			}
			### Format Data
			my ($tmp_subtotal) = (($prods{'newquantity_'.$rec{'id_orders_products'}} * $prods{'newsaleprice_'.$rec{'id_orders_products'}}) - $prods{'newdiscount_'.$rec{'id_orders_products'}});
			my ($tmp_shipping) = $prods{'newshipping_'.$rec{'id_orders_products'}};
			my ($tmp_tax)      = ($va{'tax_shipping'} + $va{'tax_product'});
			
			$rec{'subtotal'} = &format_price($tmp_subtotal);
			$rec{'total'} =  &format_price($tmp_subtotal + $tmp_shipping + $tmp_tax);
		}


		if ($print_line and ($in{'add_product'} or $in{'add_sku'} or $in{'add_service'} or $in{'add_promo'} or $in{'add_cod'} or $in{'add_card'} or $in{'add_deposit'} or $in{'add_depositref'} or $in{'to_edit'} or $in{'save'})){

			if ($key =~ /newproduct_(\d+)/){

				$output .= "<input type='hidden' name='newproduct_$1' value='1'>\n";
				$output .= "<input type='hidden' name='newidproducts_$1' value='$prods{'newidproducts_'.$1}'>\n";
				$output .= "<input type='hidden' name='newidrelated_$1' value='$prods{'newidrelated_'.$1}'>\n";
				$output .= "<input type='hidden' name='newsaleprice_$1' value='$prods{'newsaleprice_'.$1}'>\n";
				$output .= "<input type='hidden' name='newidprice_$1' value='$prods{'newidprice_'.$1}'>\n";
				$output .= "<input type='hidden' name='newdiscount_$1' value='$prods{'newdiscount_'.$1}'>\n";
				$output .= "<input type='hidden' name='newshipping_$1' value='$prods{'newshipping_'.$1}'>\n";
				$output .= "<input type='hidden' name='newquantity_$1' value='$prods{'newquantity_'.$1}'>\n";
				$output .= "<input type='hidden' name='newstatus_$1' value='$prods{'newstatus_'.$1}'>\n";
				$output .= "<input type='hidden' name='newidpromo_$1' value='$prods{'newidpromo_'.$1}'>\n" if($prods{'newidpromo_'.$1});

			}else{

				$output .= "<input type='hidden' name='newsaleprice_$rec{'id_orders_products'}' value='$prods{'newsaleprice_'.$rec{'id_orders_products'}}'>\n";
				$output .= "<input type='hidden' name='newdiscount_$rec{'id_orders_products'}' value='$prods{'newdiscount_'.$rec{'id_orders_products'}}'>\n";
				$output .= "<input type='hidden' name='newshipping_$rec{'id_orders_products'}' value='$prods{'newshipping_'.$rec{'id_orders_products'}}'>\n";
				$output .= "<input type='hidden' name='newquantity_$rec{'id_orders_products'}' value='$prods{'newquantity_'.$rec{'id_orders_products'}}'>\n";
				$output .= "<input type='hidden' name='newstatus_$rec{'id_orders_products'}' value='$prods{'newstatus_'.$rec{'id_orders_products'}}'>\n";
			}

		}elsif($print_line){

			$d = 1 - $d;
			
			++$va{'prodlines'};
		
			$line_bg_style = qq|style="background-color:#FEE3C5;font-weight:bold;"| if (!$style_status and $rec{'linetype'} !~ /New|Original/);
			$output .= qq|
				<tr bgcolor='$c[$d]' $line_bg_style>
					<td valign="top" align="center" $style_status>$rec{'action'}</td>
					<td valign="top" $style_status nowrap>$rec{'id_products'}</td>
					<td valign="top" $style_status>$rec{'prodname'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'quantity'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'unitprice'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'subtotal'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'discount'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'shipping'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'tax'}</td>
					<td valign="top"  nowrap align="right" class="num" $style_status>$rec{'total'}</td>
					<td valign="top" align="center" $style_status>$rec{'linetype'}</td>
				</tr>\n|;
		}

	}


	if ($output){

		$va{'totalproducts'} =  $va{'total'};
		$va{'total_quantity'} = &format_number($va{'total_quantity'});
		$va{'total_discount'} = &format_price($va{'total_discount'});
		$va{'total_shipping'} = &format_price($va{'total_shipping'});
		$va{'total_subtotal'} = &format_price($va{'total_subtotal'});
		$va{'total_tax'} = &format_price($va{'total_tax'});
		$va{'total_print'} = $va{'total'};
		$va{'total'} = &format_price($va{'total'});
		
	}else{

		$output = qq|<tr>
				<td colspan='11' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;

	}


	return $output;
}


sub build_paymentlist {
# --------------------------------------------------------
	my ($key, $output, $d, %rec, $print_line, $idx, $id_products);
	my (@c) = split(/,/,$cfg{'srcolors'});

	foreach my $key (sort { $pmts{$a} <=> $pmts{$b} } keys %pmts){

		$print_line = 0;
		my $line_bg_style = '';


		if ($key =~ /idorderspayments_(\d+)/){
			
			###################################
			### Building Existing Lines
			###################################
			%rec = ();
			$rec{'id_orders_payments'} = $pmts{'idorderspayments_'.$1};

			if ($pmts{'type_'.$rec{'id_orders_payments'}} eq 'COD' or $pmts{'type_'.$rec{'id_orders_paymnts'}} eq 'Deposit' or $pmts{'type_'.$rec{'id_orders_payments'}} eq 'Referenced Deposit'){

				## IS COD / Deposit / Referenced Deposit
				$rec{'type'} = $pmts{'type_'.$rec{'id_orders_payments'}};
				$rec{'amount'} = $pmts{'amount_'.$rec{'id_orders_payments'}};
				$rec{'info'} = '---';
				$rec{'capdate'} = $pmts{'capdate_'.$rec{'id_orders_payments'}};
				$rec{'capdate'} = '' if ($rec{'capdate'} eq '0000-00-00');
				$rec{'paymentdate'} = $pmts{'paymentdate_'.$rec{'id_orders_payments'}};
				$rec{'paymentdate'} = '---' if ($rec{'paymentdate'} eq '0000-00-00');

			}else{

				## IS Credit Card
				$rec{'type'} = $pmts{'type_'.$rec{'id_orders_payments'}};
				$rec{'amount'} = $pmts{'amount_'.$rec{'id_orders_payments'}};
				$rec{'capdate'} = $pmts{'capdate_'.$rec{'id_orders_payments'}};
				$rec{'capdate'} = '' if ($rec{'capdate'} eq '0000-00-00');
				$rec{'info'} = $pmts{'pmtfield2_'.$rec{'id_orders_payments'}}."<br>".$pmts{'pmtfield1_'.$rec{'id_orders_payments'}} . "<br>#### #### #### ".substr($pmts{'pmtfield3_'.$rec{'id_orders_payments'}},-4)."<br>";
				$rec{'info'} .= $pmts{'newpmtfield8_'.$rec{'id_orders_payments'}}." ".&trans_txt('apporders_payments') if ($pmts{'newpmtfield8_'.$rec{'id_orders_payments'}});
				$rec{'paymentdate'} = $pmts{'paymentdate_'.$rec{'id_orders_payments'}};

			}

			### Check if there is an Updated
			$rec{'linetype'} = &trans_txt('cond_original');
			my (@ary) = ('updamount_','updpaymentdate_','updstatus_');
			for (0..$#ary){
				if ($pmts{$ary[$_].$rec{'id_orders_payments'}}){
					$rec{substr($ary[$_], 3,-1)} = $pmts{$ary[$_].$rec{'id_orders_payments'}};
					$rec{'linetype'} = "<span style='Color:Red'>".&trans_txt('cond_edited')."</span>";
				}
			}
			$print_line = 1;

			if ($in{'add_cod'} or $in{'add_card'} or $in{'add_deposit'} or $in{'add_depositref'} or $in{'to_edit'}){
				$rec{'action'} = "";
			}else{
				$sql = "SELECT sl_orders_parts.Cost AS Cost, SUM(sl_orders_parts.Cost) * $quantity AS TCost, sl_orders_parts.Cost_Adj FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' AND sl_orders_products.ID_orders_products = '$id_orders_products' AND ID_parts = '$id_parts' GROUP BY ID_orders_products;";
				
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders_payments='$rec{'id_orders_payments'}' AND (CapDate IS NOT NULL AND Capdate!='0000-00-00') AND LENGTH(AuthCode)>=3;");
				my ($restricted) = $sth->fetchrow();
				
				if (!$restricted or $rec{'type'} eq 'Credit-Card'){
					$rec{'action'}   = qq|<input type="checkbox" name="pmtaction_$rec{'id_orders_payments'}" value="on" class="checkbox">|;
				}
			}

			if ($rec{'capdate'} and !&check_permissions('edit_order_forced_mode','','')){
				$rec{'linetype'} = "<b>".&trans_txt('cond_paid')."</b>";
			}
			
		}elsif ($key =~ /newpmt_(\d+)/){

			###################################
			### Building New Lines
			###################################
			%rec = ();
			my ($idx) = $1;
			$rec{'id_orders_payments'} = $idx;
			$line_bg_style = qq|style="background-color:#DBF0E6;font-weight:bold;"|;


			if ($pmts{'newpmttype_'.$idx} eq 'COD' or $pmts{'newpmttype_'.$idx} eq 'Deposit'){
				## IS COD
				$rec{'type'} = $pmts{'newpmttype_'.$idx};
				$rec{'amount'} = $pmts{'newamount_'.$idx};
				$rec{'info'} = '---';
				$rec{'paymentdate'} = $pmts{'newpaymentdate_'.$idx};
				$rec{'paymentdate'} = '---' if ($rec{'paymentdate'} eq '0000-00-00');
			}else{
				## IS Credit Card
				$rec{'type'} = $pmts{'newpmttype_'.$idx};
				$rec{'amount'} = $pmts{'newamount_'.$idx};
				$rec{'info'} = $pmts{'newpmtfield2_'.$idx}."<br>".$pmts{'newpmtfield1_'.$idx} . "<br>#### #### #### ".substr($pmts{'newpmtfield3_'.$idx},-4). "<br>".$pmts{'newpmtfield8_'.$idx}." ".&trans_txt('apporders_payments');
				$rec{'paymentdate'} = $pmts{'newpaymentdate_'.$idx};
				
			}
			$rec{'linetype'} = &trans_txt('cond_new');
			$print_line = 1;

			if ($in{'add_cod'} or $in{'add_card'} or $in{'add_deposit'} or $in{'add_depositref'} or $in{'to_edit'}){
				$rec{'action'} = "";
			}else{
				$rec{'action'}   = qq|<input type="checkbox" name="pmtaction_$rec{'id_orders_payments'}" value="on" class="checkbox">|;
			}

		}

		if ($print_line){

			$d = 1 - $d;
			++$va{'paylines'};

			($rec{'linetype'} eq 'Edited') and ($line_bg_style = qq|style="background-color:#FEE3C5;font-weight:bold;"|);
			if ( ($pmts{'updstatus_'.$rec{'id_orders_payments'}} ne 'Approved' and $pmts{'updstatus_'.$rec{'id_orders_payments'}} ne 'Credit' and $pmts{'newpmtstatus_'.$rec{'id_orders_payments'}} ne 'Approved' and $pmts{'newpmtstatus_'.$rec{'id_orders_payments'}} ne 'Credit') and ($pmts{'status_'.$rec{'id_orders_payments'}} eq 'Cancelled' or $pmts{'updstatus_'.$rec{'id_orders_payments'}} eq 'Cancelled' or $pmts{'newpmtstatus_'.$rec{'id_orders_payments'}} eq 'Cancelled') ){ 
				$style_status = "style='text-decoration: line-through;'";
			}else{
				## totals
				$style_status = "";
				$va{'ptotal'} += $rec{'amount'} ;
			}
		
			$output .= qq|
			<tr bgcolor='$c[$d]'>
						<td valign="top" align="center" $style_status>$rec{'action'}</td>
						<td valign="top" $style_status>$rec{'type'}</td>
						<td valign="top" $style_status>$rec{'info'}</td>
						<td valign="top" class="num" $style_status>|.&format_price($rec{'amount'}).qq|</td>
						<td valign="top" align='center' $style_status>$rec{'paymentdate'}</td>
						<td valign="top" align="center" $style_status>$rec{'linetype'}</td>
					</tr>\n|;

		}
	}

	if ($output){

		$va{'totalpayments'} = $va{'ptotal'};
		$va{'ptotal'} = &format_price($va{'ptotal'});

	}else{

		$output = qq|<tr>
				<td colspan='11' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;

	}


	return $output;
}


sub add_product{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";

	if (!$cfg{'e_orders_lock_product'}){

		foreach my $key (keys %in){
			if ($key =~ /^id_products\.(\d+)$/){
				$in{'id_products'} = $1;
			}elsif ($key =~ /^id_products\.(\d+)-(\d+)$/){
				$in{'id_products'} = $1;
				$in{'id_products_prices'} = $2;
			}elsif ($key =~ /^id_products\.(\d+)-add$/){
				$in{'id_products'} = $1 ;
				$in{'id_products_prices'} = 'add';
			}
		}
		
		if ($in{'search'}){

			my ($query);
			if ($in{'keyword'}){
				$in{'keyword'} = &filter_text_match($in{'keyword'});
				$query = " AND (MATCH(sl_products.Name) AGAINST('*".&filter_values($in{'keyword'})."*' IN BOOLEAN MODE) OR MATCH(sl_products.Model) AGAINST('*".&filter_values($in{'keyword'})."*' IN BOOLEAN MODE))";
			}elsif($in{'id_products'}){
				$in{'id_products'} =~ s/-//g;
				$in{'id_products'} = int($in{'id_products'});
				$query = " AND sl_products.ID_products='".$in{'id_products'}."'";
			}

			# Filter only Products
			$query .= " AND sl_products.ID_products NOT IN ( SELECT REPLACE(VName,'promo','') ID_products FROM sl_vars WHERE sl_vars.VName LIKE ('promo%') )";

			if ($query){
				$id_salesorigins = &load_name('sl_orders', 'ID_orders', $in{'id_orders'}, 'ID_salesorigins');
				my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_products INNER JOIN sl_products_prices USING(ID_products) WHERE 1 $query AND sl_products.Status IN ('Active','On-Air') AND sl_products_prices.Origins LIKE '%|".$id_salesorigins."|%' GROUP BY sl_products.ID_products");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					my $sth = &Do_SQL("
						SELECT sl_products.ID_products
							, sl_products.Name  
							, sl_products.Model 
							, sl_products.Status 
						FROM sl_products 
							INNER JOIN sl_products_prices USING(ID_products) 
						WHERE 1 $query AND sl_products.Status IN ('Active','On-Air') AND sl_products_prices.Origins LIKE '%|".$id_salesorigins."|%' 
						GROUP BY sl_products.ID_products 
						LIMIT 0,50");
					while ($rec = $sth->fetchrow_hashref){
						$va{'searchresult'} .= qq|
							<tr bgcolor='$c[$d]'>
								<td valign="top" align="center"><input type='submit' name='id_products.$rec->{'ID_products'}' value='S' class="sbutton"></td>
								<td valign="top">|.&format_sltvid($rec->{'ID_products'}).qq|</td>
								<td valign="top">$rec->{'Name'} / $rec->{'Model'}</td>
								<td valign="top">$rec->{'Status'}</td>
							</tr>\n|;
					}
					delete($va{'divsearch'});
				}else{
					$va{'message'} = &trans_txt('reqfields_short');
				}
			}else{
				$va{'message'} = &trans_txt('reqfields_short');
			}

		}elsif ($in{'id_products'}>0 and !$in{'id_products_prices'}){

			delete($va{'divpinfo'});
			my $sth = &Do_SQL("SELECT ID_products, Name, Model, Status FROM sl_products WHERE ID_products=$in{'id_products'} AND Status IN ('Active','On-Air') LIMIT 1;");
			$rec = $sth->fetchrow_hashref;
			$va{'id_products'} = &format_sltvid($rec->{'ID_products'});
			$va{'name'}  = $rec->{'Name'};
			$va{'model'} = $rec->{'Model'};
			$va{'status'} = $rec->{'Status'};
			
			my ($ptype, $id_salesorigins) = &load_name('sl_orders', 'ID_orders', $in{'id_orders'}, 'Ptype, ID_salesorigins');
			my $sth = &Do_SQL("SELECT * FROM sl_products_prices WHERE ID_products=$in{'id_products'} AND PayType='$ptype' AND Status = 'Active' AND Origins LIKE '%|".$id_salesorigins."|%'");
			while ($tmp = $sth->fetchrow_hashref){
				$va{'priceslist'} .= qq|&nbsp; 
				<input type='submit' name='id_products.$tmp->{'ID_products'}-$tmp->{'ID_products_prices'}' value='$tmp->{'Name'} |.&format_price($tmp->{'Price'}).qq|' class='button'>
				\n|;
			}
			$va{'priceslist'} = qq|<input type='submit' name='id_products.$rec->{'ID_products'}-add' value='|.&trans_txt('btn_add').qq|' class='button'>\n| if (!$va{'priceslist'});
		
		}elsif($in{'id_products'}>0 and ($in{'id_products_prices'}>0 or $in{'id_products_prices'} eq 'add')){

			my ($idx) = $in{'lastidx'}+1;
			$va{'newproduct'} = qq|<input type="hidden" name="newproduct_$idx" value="1">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newidproducts_$idx" value="100$in{'id_products'}">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newquantity_$idx" value="1">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newidprice_$idx" value="$in{'id_products_prices'}">\n|;
			if ($in{'id_products_prices'}>0){
				if (&load_name('sl_products','ID_products',$in{'id_products'},'PriceType') eq 'Gross'){
					my ($taxp) = &calc_taxprod(100000000+$in{'id_products'});
					
					$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="|.
					&round(&load_name('sl_products_prices','ID_products_prices',$in{'id_products_prices'},'Price')/(1+$taxp),$sys{'fmt_curr_decimal_digits'})
					.qq|">\n|;
				}else{
					$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="|.&load_name('sl_products_prices','ID_products_prices',$in{'id_products_prices'},'Price').qq|">\n|;
				}
			}else{
				$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="0">\n|;
			}
			$va{'newproduct'} .= qq|<input type="hidden" name="newshipping_$idx" value="0">\n|;
			$va{'message'} = &trans_txt('apporders_itemadded');

		}

		return &build_page('apporders/add_product.html');

	}else{

		$va{'message'} = &trans_txt('apporders_cant_add_product');
		return &build_page('locked.html');

	}
}


sub add_sku{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";
	my ($idcust) = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');

	if (!$cfg{'e_orders_lock_sku'}){
	
		foreach my $key (keys %in){
			if ($key =~ /^id_products\.(\d+)$/){
				$in{'id_products'} = 400000000+$1;
			}elsif ($key =~ /^id_products\.(\d+)-(\d+)$/){
				$in{'id_products'} = 400000000+$1 if ($in{'id_products'} < 400000000);
				$in{'id_products_prices'} = $2;
			}elsif ($key =~ /^id_products\.(\d+)-add$/){
				$in{'id_products'} = $1 ;
				$in{'id_products_prices'} = 'add';
			}
		}
 
		if ($in{'search'}){

			my ($query);
			if ($in{'name'}){

				$query = " AND Name LIKE '%".&filter_values($in{'name'})."%'";

			}elsif($in{'upc'}){

				my ($id) = &load_name('sl_skus','UPC',$in{'upc'}, 'ID_sku_products');
				if ($id >0){ 
					$id -= 400000000;
					$query = " sl_parts.ID_parts='".$id."'";
				}
				$query .= " OR " if($query ne '' and $cfg{'e_orders_use_price_by_customer'});
				$query = " AND ($query sl_customers_parts.sku_customers LIKE '%".&filter_values($in{'upc'})."%')" if ($cfg{'e_orders_use_price_by_customer'});

			}elsif($in{'id_products'}){

				$in{'id_products'} =~ s/-//g;
				$in{'id_products'} = int($in{'id_products'});
				if ($in{'id_products'}>400000000){
					$in{'id_products'} -= 400000000;
				}
				$query = "AND sl_parts.ID_parts='".$in{'id_products'}."'";
			}

			my $sql = "SELECT COUNT(*) FROM sl_parts INNER JOIN sl_customers_parts USING(ID_parts) WHERE 1 $query AND sl_parts.Status = 'Active' AND sl_customers_parts.ID_customers ='$idcust';";
			$sql = "SELECT COUNT(*) FROM sl_parts WHERE 1 $query AND Status = 'Active'" if(!$cfg{'e_orders_use_price_by_customer'});

			my $sth = &Do_SQL($sql);
			$va{'matches'} = $sth->fetchrow;
			if ($va{'matches'}>0){
				$sql = (!$cfg{'e_orders_use_price_by_customer'}) ?
						"SELECT * FROM sl_parts LEFT JOIN sl_skus ON ID_sku_products = 400000000 + ID_parts WHERE 1 ". $query ." AND sl_parts.Status = 'Active' LIMIT 0,50 " : 
						"SELECT * FROM sl_parts INNER JOIN sl_customers_parts USING(ID_parts) LEFT JOIN sl_skus ON ID_sku_products = 400000000 + ID_parts WHERE 1 ". $query ." AND sl_parts.Status = 'Active' AND sl_customers_parts.ID_customers = ". $idcust ." LIMIT 0,50";

				my $sth = &Do_SQL($sql);
				while ($rec = $sth->fetchrow_hashref){
					my ($select_item) = qq|<input type='submit' name='id_products.$rec->{'ID_products'}' value='S' class="sbutton">|;
					$rec->{'sku_customers'} = '' if (!$rec->{'sku_customers'});
					$rec->{'SPrice'} = 0 if(!$rec->{'SPrice'});
					$sprice = &format_price($rec->{'SPrice'});
					
					###################
					## Excepcion: Precio de de Ultima Compra para Cliente Intercompañia
					###################
					if ($cfg{'e_orders_use_last_po_price'} and $cfg{'e_orders_use_last_po_price'}==1){
						if ($cfg{'e_orders_use_last_po_price_'.$idcust} and $cfg{'e_orders_use_last_po_price_'.$idcust} ne ''){
							my ($tmp_cost, $tmp_adj, $tmp_add) = &load_last_purchase_cost($rec->{'ID_sku_products'});
							my $price_customer = (1 + ($cfg{'e_orders_use_last_po_price_'.$idcust}/100)) * $tmp_cost;
							if ($price_customer){
								$sprice = $price_customer;
							}else{
								$sprice = "<span style='color:#FB283E;'>Not Found</span>";
								$select_item = '';
							}
						}
					}

					$va{'searchresult'} .= qq|
						<tr bgcolor='$c[$d]'>
							<td valign="top" align="center">$select_item</td>
							<td valign="top">|.&format_sltvid(400000000+$rec->{'ID_parts'}).qq|</td>
							<td valign="top">$rec->{'Name'}</td>
							<td valign="top">$rec->{'UPC'}</td>
							<td valign="top">$rec->{'sku_customers'}</td>
							<td valign="top" align="right">$sprice</td>
							<td valign="top">$rec->{'Status'}</td>
						</tr>\n|;
				}
				delete($va{'divsearch'});
			}else{
				$va{'message'} = &trans_txt('reqfields_short');
			}

		}elsif ($in{'id_products'}>0 and !$in{'id_products_prices'}){

			delete($va{'divpinfo'});

			$sql = "SELECT * FROM sl_parts LEFT JOIN sl_skus ON ID_sku_products=400000000+ID_parts WHERE ID_parts=".($in{'id_products'}-400000000)." AND sl_parts.Status = 'Active'";

			my $sth = &Do_SQL($sql);
			$rec = $sth->fetchrow_hashref;
			$id_products = 400000000+$rec->{'ID_parts'};
			$va{'id_products'} = &format_sltvid(400000000+$rec->{'ID_parts'});
			$va{'name'}  = $rec->{'Name'};
			$va{'upc'} = $rec->{'UPC'};
			$va{'status'} = $rec->{'Status'};
			my $sth = &Do_SQL("SELECT * FROM sl_customers_parts WHERE ID_parts=$rec->{'ID_parts'} AND ID_customers='$idcust'");
			while ($rec = $sth->fetchrow_hashref){

				if ($cfg{'e_orders_use_price_by_customer'} and $cfg{'e_orders_use_price_by_customer'} == 1){
					###################
					## Excepcion: Precio de de Ultima Compra para Cliente Intercompañia
					###################
					if ($cfg{'e_orders_use_last_po_price'} and $cfg{'e_orders_use_last_po_price'}==1){
						if ($cfg{'e_orders_use_last_po_price_'.$idcust} and $cfg{'e_orders_use_last_po_price_'.$idcust} ne ''){
							my ($tmp_cost, $tmp_adj, $tmp_add) = &load_last_purchase_cost($id_products);
							my $price_customer = (1 + ($cfg{'e_orders_use_last_po_price_'.$idcust}/100)) * $tmp_cost;
							
							$rec->{'SPrice'} = $price_customer;
						}
					}

					$va{'priceslist'} .= qq|&nbsp; <input type='submit' name='id_products.|.$id_products.qq|-$rec->{'ID_customers_parts'}' value='$rec->{'Name'} |.&format_price($rec->{'SPrice'}).qq|' class='button'>\n|;
				}else{
					$va{'priceslist'} .= qq|&nbsp; <input type='submit' name='id_products.|.$id_products.qq|-$rec->{'ID_products_prices'}' value='$rec->{'Name'} |.&format_price($rec->{'Price'}).qq|' class='button'>\n|;
				}

			}
			
			$va{'priceslist'} = qq|<input type='submit' name='id_products.|.$id_products.qq|-add' value='|.&trans_txt('btn_add').qq|' class='button'>\n| if (!$va{'priceslist'});

		}elsif($in{'id_products'}>0 and ($in{'id_products_prices'}>0 or $in{'id_products_prices'} eq 'add')){

			my ($idx) = $in{'lastidx'}+1;

			if ($cfg{'e_orders_use_price_by_customer'} and $cfg{'e_orders_use_price_by_customer'} == 1){
				$va{'newproduct'} = qq|<input type="hidden" name="newproduct_$idx" value="1">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newidproducts_$idx" value="100000000">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newidrelated_$idx" value="$in{'id_products'}">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newquantity_$idx" value="1">\n|;
				# $va{'newproduct'} .= qq|<input type="hidden" name="newidprice_$idx" value="$in{'id_products_prices'}">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newidcustomersparts_$idx" value="$in{'id_products_prices'}">\n|;
			}else{
				$va{'newproduct'} = qq|<input type="hidden" name="newproduct_$idx" value="1">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newidproducts_$idx" value="$in{'id_products'}">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newidrelated_$idx" value="$in{'id_products'}">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newquantity_$idx" value="1">\n|;
				$va{'newproduct'} .= qq|<input type="hidden" name="newidprice_$idx" value="$in{'id_products_prices'}">\n|;
			}

			if ($in{'id_products_prices'}>0){
				my $price = (!$cfg{'e_orders_use_price_by_customer'})? 0.00 : &load_name('sl_customers_parts','ID_customers_parts',$in{'id_products_prices'},'SPrice');
				###################
				## Excepcion: Precio de de Ultima Compra para Cliente Intercompañia
				###################
				if ($cfg{'e_orders_use_last_po_price'} and $cfg{'e_orders_use_last_po_price'}==1){
					if ($cfg{'e_orders_use_last_po_price_'.$idcust} and $cfg{'e_orders_use_last_po_price_'.$idcust} ne ''){
						my ($tmp_cost, $tmp_adj, $tmp_add) = &load_last_purchase_cost($in{'id_products'});
						my $price_customer = (1 + ($cfg{'e_orders_use_last_po_price_'.$idcust}/100)) * $tmp_cost;
						
						$price = $price_customer;
					}
				}
				$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="|.$price.qq|">\n|;
			}else{
				$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="0">\n|;
			}
			$va{'newproduct'} .= qq|<input type="hidden" name="newshipping_$idx" value="0">\n|;
			$va{'message'} = &trans_txt('apporders_itemadded');
			
			## Se limpia el formulario de busqueda
			delete($in{'id_products'});
			delete($in{'upc'});
			delete($in{'name'});

		}

		return &build_page('apporders/add_sku.html');

	}else{

		$va{'message'} = &trans_txt('apporders_cant_add_sku');
		return &build_page('locked.html');

	}
}

sub add_service{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";
	
	if (!$cfg{'e_orders_lock_service'}){

		foreach my $key (keys %in){
			if ($key =~ /^id_products\.(\d+)$/){
				$in{'id_products'} = 600000000+$1;
			}elsif ($key =~ /^id_products\.(\d+)-(\d+)$/){
				$in{'id_products'} = 600000000+$1;
				$in{'id_products_prices'} = $2;
			}elsif ($key =~ /^id_products\.(\d+)-add$/){
				$in{'id_products'} = $1 ;
				$in{'id_products_prices'} = 'add';
			}
		}
		
		if ($in{'search'}){

			my ($query);
			if ($in{'keyword'}){

				$query = "Name LIKE '%".&filter_values($in{'keyword'})."%'";

			}elsif($in{'id_products'}){

				$in{'id_products'} =~ s/-//g;
				$in{'id_products'} = int($in{'id_products'});
				$query = "ID_services='".$in{'id_products'}."'";

			}

			if ($query){

				my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_services WHERE $query AND Status = 'Active'");
				$va{'matches'} = $sth->fetchrow;

				if ($va{'matches'}>0){

					my $sth = &Do_SQL("SELECT * FROM sl_services WHERE $query AND Status = 'Active' LIMIT 0,50");
					while ($rec = $sth->fetchrow_hashref){

						$va{'searchresult'} .= qq|
							<tr bgcolor='$c[$d]'>
								<td valign="top" align="center"><input type='submit' name='id_products.$rec->{'ID_services'}' value='S' class="sbutton"></td>
								<td valign="top">|.&format_sltvid(600000000+$rec->{'ID_services'}).qq|</td>
								<td valign="top">$rec->{'Name'}</td>
								<td valign="top" align="right">|.&format_price($rec->{'SPrice'}). qq|</td>
								<td valign="top">$rec->{'Status'}</td>
							</tr>\n|;

					}
					delete($va{'divsearch'});

				}else{

					$va{'message'} = &trans_txt('reqfields_short');

				}

			}else{

				$va{'message'} = &trans_txt('reqfields_short');

			}

		}elsif ($in{'id_products'}>0 and !$in{'id_products_prices'}){

			delete($va{'divpinfo'});
			my $sth = &Do_SQL("SELECT * FROM sl_services WHERE ID_services=".($in{'id_products'}-600000000)." AND Status = 'Active'");
			$rec = $sth->fetchrow_hashref;
			$id_products = 600000000+$rec->{'ID_services'};
			$va{'id_products'} = &format_sltvid(600000000+$rec->{'ID_services'});
			$va{'name'}  = $rec->{'Name'};
			$va{'status'} = $rec->{'Status'};
			$va{'price'} = &format_price($rec->{'SPrice'});
			
			$va{'priceslist'} = qq|<input type='submit' name='id_products.|.$id_products.qq|-add' value='|.&trans_txt('btn_add').qq|' class='button'>\n|;

		}elsif($in{'id_products'}>0 and ($in{'id_products_prices'}>0 or $in{'id_products_prices'} eq 'add')){

			($service_price, $service_tax, $service_tax_rate) = &services_tax(($in{'id_products'}-600000000));

			my ($idx) = $in{'lastidx'}+1;
			$va{'newproduct'} = qq|<input type="hidden" name="newproduct_$idx" value="1">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newidproducts_$idx" value="$in{'id_products'}">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newidrelated_$idx" value="$in{'id_products'}">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newquantity_$idx" value="1">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newidprice_$idx" value="0">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="|.$service_price.qq|">\n|;
			$va{'newproduct'} .= qq|<input type="hidden" name="newshipping_$idx" value="0">\n|;
			$va{'message'} = &trans_txt('apporders_itemadded');

		}

		return &build_page('apporders/add_service.html');

	}else{

		$va{'message'} = &trans_txt('apporders_cant_add_service');
		return &build_page('locked.html');

	}

}

sub add_promo{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";
	
	if (!$cfg{'e_orders_lock_promo'}){

		foreach my $key (keys %in){
			if ($key =~ /^id_promo\.(\d+)$/){
				$in{'id_promo'} = $1;
			}elsif ($key =~ /^id_promo\.(\d+)-(\d+)$/){
				$in{'id_promo'} = $1;
				$in{'id_products_prices'} = $2;
			}elsif ($key =~ /^id_products\.(\d+)-add$/){
				$in{'id_promo'} = $1 ;
				$in{'id_products_prices'} = 'add';
			}
		}

		if ($in{'search'}){

			my ($query);
			if ($in{'keyword'}){
				$in{'keyword'} = &filter_text_match($in{'keyword'});
				$query = " (MATCH(sl_products.Model) AGAINST('*".&filter_values($in{'keyword'})."*' IN BOOLEAN MODE) OR MATCH(sl_products.Name) AGAINST('*".&filter_values($in{'keyword'})."*' IN BOOLEAN MODE)) ";
			}elsif($in{'id_promo'}){
				$in{'id_promo'} =~ s/-//g;
				$in{'id_promo'} = int($in{'id_promo'});
				$query = " sl_products.ID_products='".$in{'id_promo'}."'";
			}

			if ($query){

				my $sth = &Do_SQL("SELECT COUNT(*) 
					FROM sl_products INNER JOIN (
						SELECT REPLACE(VName,'promo','') ID_products, sl_vars.VValue Promo
						FROM sl_vars 
						WHERE sl_vars.VName LIKE ('promo%')
					) promos ON promos.ID_products=sl_products.ID_products
					WHERE  1 AND sl_products.Status='On-Air' AND $query ");
				$va{'matches'} = $sth->fetchrow;
				if ($va{'matches'}>0){
					my $sth = &Do_SQL("SELECT * FROM sl_products INNER JOIN (
						SELECT REPLACE(VName,'promo','') ID_products, sl_vars.VValue Promo
						FROM sl_vars 
						WHERE sl_vars.VName LIKE ('promo%')
					) promos ON promos.ID_products=sl_products.ID_products
					WHERE  1 AND sl_products.Status='On-Air' AND $query LIMIT 0,50");
					while ($rec = $sth->fetchrow_hashref){
						$va{'searchresult'} .= qq|
							<tr bgcolor='$c[$d]'>
								<td valign="top" align="center"><input type='submit' name='id_promo.$rec->{'ID_products'}' value='S' class="sbutton"></td>
								<td valign="top">|.&format_sltvid($rec->{'ID_products'}).qq|</td>
								<td valign="top">$rec->{'Name'} / $rec->{'Model'}</td>
								<td valign="top">$rec->{'Status'}</td>
							</tr>\n|;
					}
					delete($va{'divsearch'});
				}else{
					$va{'message'} = &trans_txt('reqfields_short');
				}

			}else{

				$va{'message'} = &trans_txt('reqfields_short');

			}

		}elsif ($in{'id_promo'}>0 and !$in{'id_products_prices'}){

			delete($va{'divpinfo'});
			my $sth = &Do_SQL("SELECT * FROM sl_products WHERE ID_products=$in{'id_promo'} AND Status IN ('Active','On-Air') LIMIT 0,50");
			$rec = $sth->fetchrow_hashref;
			$va{'id_promo'} = &format_sltvid($rec->{'ID_products'});
			$va{'name'}  = $rec->{'Name'};
			$va{'model'} = $rec->{'Model'};
			$va{'status'} = $rec->{'Status'};
			my ($ptype) = &load_name('sl_orders','ID_orders',$in{'id_orders'},'Ptype');
			my $sth = &Do_SQL("SELECT * FROM sl_products_prices WHERE ID_products=$in{'id_promo'} AND PayType='$ptype' AND Status = 'Active'");
			while ($tmp = $sth->fetchrow_hashref){
				$va{'priceslist'} .= qq|&nbsp; 
				<input type='submit' name='id_promo.$tmp->{'ID_products'}-$tmp->{'ID_products_prices'}' value='$tmp->{'Name'} |.&format_price($tmp->{'Price'}).qq|' class='button'>
				\n|;
			}

			$va{'message'} = &trans_txt('apporders_promo_pricing_not_available') if (!$va{'priceslist'});
			$va{'priceslist'} = qq|<input type='submit' name='id_promo.$rec->{'ID_products'}-add' value='|.&trans_txt('btn_add').qq|' class='button'>\n| if (!$va{'priceslist'});

		}elsif($in{'id_promo'}>0 and ($in{'id_products_prices'}>0 or $in{'id_products_prices'} eq 'add')){

			# my $sth = &Do_SQL("SELECT Vvalue as ID_products FROM sl_vars WHERE sl_vars.VName LIKE ('promo$in{'id_promo'}');");
			my $sth = &Do_SQL("SELECT 
				(SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName LIKE ('promo$in{'id_promo'}'))ID_products
				, (SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName LIKE ('percent_promo$in{'id_promo'}'))Percents");
			my ($promo,$percents) = $sth->fetchrow;
			my (@products) = split(/\|/,$promo);
			my $products = @products;
			my (@percents);
			if ($percents){
				@percents = split(/\|/,$percents);
			}

			for(0..$#products){
				if($products[$_]>0){
					my ($sth) = &Do_SQL("SELECT ID_products,Model,Name FROM sl_products WHERE ID_products = $products[$_];");
					my ($id_products,$model,$name) = $sth->fetchrow();

					my ($idx) = $in{'lastidx'}+$_+1;
					$va{'newproduct'} .= qq|<input type="hidden" name="newidpromo_$idx" value="$in{'id_promo'}">\n|;
					$va{'newproduct'} .= qq|<input type="hidden" name="newproduct_$idx" value="1">\n|;
					$va{'newproduct'} .= qq|<input type="hidden" name="newidproducts_$idx" value="100$id_products">\n|;
					$va{'newproduct'} .= qq|<input type="hidden" name="newidrelated_$idx" value="$in{'id_promo'}">\n|;
					$va{'newproduct'} .= qq|<input type="hidden" name="newquantity_$idx" value="1">\n|;
					$va{'newproduct'} .= qq|<input type="hidden" name="newidprice_$idx" value="$in{'id_products_prices'}">\n|;
					if ($in{'id_products_prices'}>0){

						if (&load_name('sl_products','ID_products',$id_products,'PriceType') eq 'Gross'){
							my ($taxp) = &calc_taxprod(100000000+$id_products);
							my $price = &round(&load_name('sl_products_prices','ID_products_prices',$in{'id_products_prices'},'Price')/(1+$taxp),$sys{'fmt_curr_decimal_digits'});
							
							if ($percents){
								$price = ($percents[$_] == 0)? 0 : ($percents[$_] * $price) / 100;
							}else{								
								$price = $price / $products;
							}

							$price = &round($price,$sys{'fmt_curr_decimal_digits'});							
							$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="|.$price.qq|">\n|;
						}else{
							my $price = &load_name('sl_products_prices','ID_products_prices',$in{'id_products_prices'},'Price');
							
							if ($percents){
								$price = ($percents[$_] == 0)? 0 : ($percents[$_] * $price) / 100;
							}else{								
								$price = $price / $products;
							}

							$price = &round($price,$sys{'fmt_curr_decimal_digits'});
							$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="|.$price.qq|">\n|;
						}
					}else{
						$va{'newproduct'} .= qq|<input type="hidden" name="newsaleprice_$idx" value="0">\n|;
					}
					$va{'newproduct'} .= qq|<input type="hidden" name="newshipping_$idx" value="0">\n|;
				}
			}
			$va{'message'} = &trans_txt('apporders_itemadded');
		}

		return &build_page('apporders/add_promo.html');

	}else{

		$va{'message'} = &trans_txt('apporders_cant_add_service');
		return &build_page('locked.html');

	}

}

sub add_cod{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";

	if (!$cfg{'e_orders_lock_cod'}){
	
		if($in{'amount'} and $in{'action'}){
			my $sth = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders=$in{'id_orders'} AND Type='COD' AND (CapDate IS NULL OR CapDate='0000-00-00') AND Status NOT IN('Cancelled')");
			my ($id_payment) = $sth->fetchrow;
			if ($id_payment >0 and $pmts{'amount_'.$id_payment}){
				### Update existing COD payment
				if (($pmts{'amount_'.$id_payment} + $in{'amount'})>0){
					$pmts{'updamount_'.$id_payment} = $pmts{'amount_'.$id_payment} + $in{'amount'};
				}else{
					++$err;
					$error{'amount'} = &trans_txt('invalid');
				}
			}else{
				### Create new Payment
				for (1..$in{'lastpidx'}){
					if ($pmts{'newpmttype_'.$_} eq 'COD'){
						if (($pmts{'newamount_'.$_} + $in{'amount'})>0){
							$pmts{'newamount_'.$_} = $pmts{'newamount_'.$_} + $in{'amount'};
							$pmts{'newpmtstatus_'.$_} = 'Approved';
						}else{
							++$err;
							$error{'amount'} = &trans_txt('invalid');
						}
						$in{'amount'} = 0;
					}
				}
				if ($in{'amount'}>0){
					my ($idx) = $in{'lastpidx'}+1;
					$pmts{'newpmt_'.$idx} = 1;
					$pmts{'newpmttype_'.$idx} = 'COD';
					$pmts{'newamount_'.$idx} = $in{'amount'};
					$pmts{'newpmtstatus_'.$idx} = 'Approved';
				}elsif($in{'amount'}<0){
					++$err;
					$error{'amount'} = &trans_txt('invalid');
				}
			}
			if ($err>0){
				$va{'message'} = &trans_txt('reqfields_short');
			}else{
				$va{'message'} = &trans_txt('apporders_codadded');
			}
		}else{
			$in{'amount'} = $va{'tdifference'} if (!$in{'amount'});
			if($in{'amount'}>0){
				$va{'diffmessage'} = &trans_txt('apporders_addpayment');
			}elsif($in{'amount'}<0){
				$va{'diffmessage'} = &trans_txt('apporders_addcredit');
			}else{
				$va{'diffmessage'} = &trans_txt('apporders_nopayment');
			}
		}
		### Build hidden Data for Payments.. Only Update of Amont, Payment Date, or Status
		$va{'paymentsupdlist'} = &hidden_pmtdata;
		return &build_page('apporders/add_cod.html');
	}else{
		$va{'message'} = &trans_txt('apporders_cant_add_cod');
		return &build_page('locked.html');
	}

	
}

sub add_card{
# --------------------------------------------------------
	if (!$cfg{'e_orders_lock_creditcard'}){
		if($in{'action'} eq 'addcard'){
			my ($err);
			$in{'pmtfield4'} = $in{'month'}.$in{'year'};
			my (@cols) = ('pmtfield1','pmtfield2','pmtfield3','pmtfield4','pmtfield5','pmtfield6','paymentdate','amount','pmtfield8');
			for (0..$#cols){
				if (!$in{$cols[$_]}	){
					$error{$cols[$_]} = &trans_txt('required');
					++$err;
				}
			}		
			if ($err>0){
				$va{'message'} = &trans_txt('reqfields_short');
			}else{
				my ($idx) = $in{'lastpidx'}+1;
				$pmts{'newpmt_'.$idx} = 1;
				$pmts{'newpmttype_'.$idx} = 'Credit-Card';
				$pmts{'newamount_'.$idx} = $in{'amount'};
				$pmts{'newpaymentdate_'.$idx} = $in{'paymentdate'};
				$pmts{'newpmtstatus_'.$idx} = 'Approved';
				$pmts{'newpmtpuntos_'.$idx} = $in{'activate_points'};
				$in{'pmtfield7'} = 'CreditCard';
				for (1..11){
					$pmts{'newpmtfield'.$_.'_'.$idx} = $in{'pmtfield'.$_};	
				}
				$va{'message'} = &trans_txt('apporders_cardadded');
			}
		}else{
			$in{'amount'} = $va{'tdifference'} if (!$in{'amount'});
			if($in{'amount'}>0){
				$va{'diffmessage'} = &trans_txt('apporders_addpayment');
			}elsif($in{'amount'}<0){
				$va{'diffmessage'} = &trans_txt('apporders_addcredit');
			}else{
				$va{'diffmessage'} = &trans_txt('apporders_nopayment');
			}
		}
		### Build hidden Data for Payments.. Only Update of Amont, Payment Date, or Status
		$va{'paymentsupdlist'} = &hidden_pmtdata;
		return &build_page('apporders/add_card.html');
	}else{
		$va{'message'} = &trans_txt('apporders_cant_add_creditcard');
		return &build_page('locked.html');
	}
}

sub add_deposit{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";

	if (!$cfg{'e_orders_lock_deposit'}){
		
		if($in{'amount'} and $in{'action'}){

			my $sth = &Do_SQL("SELECT 
				(SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders=$in{'id_orders'} AND Type='Deposit' AND (CapDate IS NULL OR CapDate='0000-00-00') AND Status NOT IN('Cancelled'))as ID_orders_payments
				, CURDATE() as paymentdate");
			my ($id_payment, $paymentdate) = $sth->fetchrow;
			if ($id_payment >0 and $pmts{'amount_'.$id_payment}){
				### Update existing Deposit payment
				if (($pmts{'amount_'.$id_payment} + $in{'amount'})>0){
					$pmts{'updamount_'.$id_payment} = $pmts{'amount_'.$id_payment} + $in{'amount'};
				}else{
					++$err;
					$error{'amount'} = &trans_txt('invalid');
				}
			}else{
				### Create new Payment
				for (1..$in{'lastpidx'}){
					if ($pmts{'newpmttype_'.$_} eq 'Deposit'){
						if (($pmts{'newamount_'.$_} + $in{'amount'})>0){
							$pmts{'newamount_'.$_} = $pmts{'newamount_'.$_} + $in{'amount'};
							$pmts{'newpmtstatus_'.$_} = 'Approved';
						}else{
							++$err;
							$error{'amount'} = &trans_txt('invalid');
						}
						$in{'amount'} = 0;
					}
				}
				if ($in{'amount'}>0){
					my ($idx) = $in{'lastpidx'}+1;
					$pmts{'newpmt_'.$idx} = 1;
					$pmts{'newpmttype_'.$idx} = 'Deposit';
					$pmts{'newamount_'.$idx} = $in{'amount'};
					$pmts{'newpmtstatus_'.$idx} = 'Approved';
					$pmts{'newpaymentdate_'.$idx} = "$paymentdate";
				}elsif($in{'amount'}<0){
					++$err;
					$error{'amount'} = &trans_txt('invalid');
				}
			}
			if ($err>0){
				$va{'message'} = &trans_txt('reqfields_short');
			}else{
				$va{'message'} = &trans_txt('apporders_depositadded');
			}
		}else{
			$in{'amount'} = $va{'tdifference'} if (!$in{'amount'});
			if($in{'amount'}>0){
				$va{'diffmessage'} = &trans_txt('apporders_addpayment');
			}elsif($in{'amount'}<0){
				$va{'diffmessage'} = &trans_txt('apporders_addcredit');
			}else{
				$va{'diffmessage'} = &trans_txt('apporders_nopayment');
			}
		}
		### Build hidden Data for Payments.. Only Update of Amont, Payment Date, or Status
		$va{'paymentsupdlist'} = &hidden_pmtdata;
		return &build_page('apporders/add_deposit.html');
	}else{
		$va{'message'} = &trans_txt('apporders_cant_add_deposit');
		return &build_page('locked.html');
	}
}

sub add_depositref{
# --------------------------------------------------------
	$va{'divsearch'} = "visibility:hidden;";
	$va{'divpinfo'} = "visibility:hidden;";

	if (!$cfg{'e_orders_lock_depositref'}){
		
		$in{'pmtfield3'} = &ref_banco_azteca($in{'id_orders'});
		if($in{'amount'} and $in{'action'}){


			my $sth = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders=$in{'id_orders'} AND Type='Referenced Deposit' AND (CapDate IS NULL OR CapDate='0000-00-00') AND Status NOT IN('Cancelled')");
			my ($id_payment) = $sth->fetchrow;
			if ($id_payment >0 and $pmts{'amount_'.$id_payment}){
				### Update existing Deposit payment
				if (($pmts{'amount_'.$id_payment} + $in{'amount'})>0){
					$pmts{'updamount_'.$id_payment} = $pmts{'amount_'.$id_payment} + $in{'amount'};
				}else{
					++$err;
					$error{'amount'} = &trans_txt('invalid');
				}
			}else{
				### Create new Payment
				for (1..$in{'lastpidx'}){

					if ($pmts{'newpmttype_'.$_} eq 'Referenced Deposit'){

						if (($pmts{'newamount_'.$_} + $in{'amount'}) > 0){

							$pmts{'newamount_'.$_} = $pmts{'newamount_'.$_} + $in{'amount'};
							$pmts{'newpmtstatus_'.$_} = 'Approved';

						}else{

							++$err;
							$error{'amount'} = &trans_txt('invalid');

						}
						$in{'amount'} = 0;
					}
				}

				if ($in{'amount'}>0){

					my ($idx) = $in{'lastpidx'}+1;
					$pmts{'newpmt_'.$idx} = 1;
					$pmts{'newpmttype_'.$idx} = 'Referenced Deposit';
					$pmts{'newamount_'.$idx} = $in{'amount'};
					$pmts{'newpmtstatus_'.$idx} = 'Approved';

				}elsif($in{'amount'} < 0){

					++$err;
					$error{'amount'} = &trans_txt('invalid');

				}

			}

			if ($err>0){
				$va{'message'} = &trans_txt('reqfields_short');
			}else{
				$va{'message'} = &trans_txt('apporders_depositrefadded');
			}
		}else{
			$in{'amount'} = $va{'tdifference'} if (!$in{'amount'});
			if($in{'amount'}>0){
				$va{'diffmessage'} = &trans_txt('apporders_addpayment');
			}elsif($in{'amount'}<0){
				$va{'diffmessage'} = &trans_txt('apporders_addcredit');
			}else{
				$va{'diffmessage'} = &trans_txt('apporders_nopayment');
			}
		}
		### Build hidden Data for Payments.. Only Update of Amont, Payment Date, or Status
		$va{'paymentsupdlist'} = &hidden_pmtdata;
		return &build_page('apporders/add_depositref.html');
	}else{
		$va{'message'} = &trans_txt('apporders_cant_add_depositref');
		return &build_page('locked.html');
	}
}

sub to_enable{
# --------------------------------------------------------
	my ($key);
	my ($promo);
	foreach $key (keys %in){
		if ($key =~ /pmtaction_(\d+)/){
			if (!$pmts{'capdate_'.$1} or $pmts{'capdate_'.$1} eq '0000-00-00'){
				if ($pmts{'status_'.$1}){
					$pmts{'updstatus_'.$1} = $pmts{'amount_'.$1} >= 0  ? 'Approved' : 'Credit';
				}else{
					$pmts{'newpmtstatus_'.$1} = $pmts{'newpmtamount_'.$1} >= 0  ? 'Approved' : 'Credit';
				}
			}
		}elsif($key =~ /action_(\d+)/){
			if (!$prods{'shpdate_'.$1}){
				$prods{'newstatus_'.$1} = 'Active';
				
				if ($prods{'newidpromo_'.$1} or $prods{'idpromo_'.$1}){
					$promo = ($prods{'newidpromo_'.$1})? $prods{'newidpromo_'.$1} : $prods{'idpromo_'.$1};
					foreach $key (keys %in){
						if(($key =~ /newidpromo_(\d+)/ and $prods{'newidpromo_'.$1}==$promo) or ($key =~ /idpromo_(\d+)/ and $prods{'idpromo_'.$1}==$promo)){
							if (!$prods{'shpdate_'.$1}){
								$prods{'newstatus_'.$1} = 'Active';
							}
						}
					}
				}
			}			
		}
	}

	return &trans_txt('done');
}				

sub to_disable{
# --------------------------------------------------------
	my ($key);
	my ($promo);
	foreach $key (keys %in){
		if ($key =~ /pmtaction_(\d+)/){
			if (!$pmts{'capdate_'.$1} or $pmts{'capdate_'.$1} eq '0000-00-00'){
				if ($pmts{'status_'.$1}){
					$pmts{'updstatus_'.$1} = 'Cancelled';
				}else{
					$pmts{'newpmtstatus_'.$1} = 'Cancelled';
				}
			}
		}elsif($key =~ /action_(\d+)/){
			if (!$prods{'shpdate_'.$1}){
				$prods{'newstatus_'.$1} = 'Inactive';
				if ($prods{'newidpromo_'.$1} or $prods{'idpromo_'.$1}){
					$promo = ($prods{'newidpromo_'.$1})? $prods{'newidpromo_'.$1} : $prods{'idpromo_'.$1};
					foreach $key (keys %in){
						if(($key =~ /newidpromo_(\d+)/ and $prods{'newidpromo_'.$1}==$promo) or ($key =~ /idpromo_(\d+)/ and $prods{'idpromo_'.$1}==$promo)){
							if (!$prods{'shpdate_'.$1}){
								$prods{'newstatus_'.$1} = 'Inactive';
							}
						}
					}
				}
				# else{
					# if ($prods{'newproduct_'.$1} and $prods{'newstatus_'.$1}){
					# 	delete($prods{'newproduct_'.$1});
					# 	delete($prods{'newquantity_'.$1});
					# 	delete($prods{'newsaleprice_'.$1});
					# 	delete($prods{'newidprice_'.$1});
					# 	delete($prods{'newdiscount_'.$1});
					# 	delete($prods{'newshipping_'.$1});
					# 	delete($prods{'newstatus_'.$1});
					# 	delete($prods{'newidrelated_'.$1});
					# }else{
						# $prods{'newstatus_'.$1} = 'Inactive';
					# }
				# }
			}else{
				return &trans_txt('cond_shipped');
			}
		}
	}

	return &trans_txt('done');
}

sub to_duplicate{
# --------------------------------------------------------
	foreach $key (keys %in){
		if ($key =~ /pmtaction_(\d+)/){
			if ($pmts{'newpmttype_'.$1} eq 'COD'){
				++$in{'lastpidx'};
				$pmts{'newpmt_'.$in{'lastpidx'}} = 1;
				$pmts{'newpmttype_'.$in{'lastpidx'}} = 'COD';
				$pmts{'newamount_'.$in{'lastpidx'}} = $pmts{'newamount_'.$1};
				$pmts{'newpmtstatus_'.$in{'lastpidx'}} = 'Approved';
			}elsif($pmts{'type_'.$1} eq 'COD'){
				++$in{'lastpidx'};
				$pmts{'newpmt_'.$in{'lastpidx'}} = 1;
				$pmts{'newpmttype_'.$in{'lastpidx'}} = 'COD';
				$pmts{'newamount_'.$in{'lastpidx'}} = $pmts{'amount_'.$1};
				$pmts{'newpmtstatus_'.$in{'lastpidx'}} = 'Approved';
			}elsif($pmts{'newpmttype_'.$1} eq 'Credit-Card'){
				++$in{'lastpidx'};
				$pmts{'newpmt_'.$in{'lastpidx'}} = 1;
				$pmts{'newpmttype_'.$in{'lastpidx'}} = 'Credit-Card';
				$pmts{'newamount_'.$in{'lastpidx'}} = $pmts{'newamount_'.$1};
				$pmts{'newpaymentdate_'.$in{'lastpidx'}} = $pmts{'newpaymentdate_'.$1};
				$pmts{'newpmtstatus_'.$in{'lastpidx'}} = 'Approved';
				for (1..11){
					if($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1){
						if( $_ == 3 ){
							my $cc_number = &load_name('sl_orders_cardsdata', 'ID_orders_payments', $1, 'card_number');
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = (!$cc_number) ? $pmts{'newpmtfield'.$_.'_'.$1} : &LeoDecrypt($cc_number);
						}elsif( $_ == 4 ){
							my $cc_date = &load_name('sl_orders_cardsdata', 'ID_orders_payments', $1, 'card_date');
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = (!$cc_date) ? $pmts{'newpmtfield'.$_.'_'.$1} : &LeoDecrypt($cc_date);
						}elsif( $_ == 5 ){
							my $cc_cvn = &load_name('sl_orders_cardsdata', 'ID_orders_payments', $1, 'card_cvn');
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = (!$cc_cvn) ? $pmts{'newpmtfield'.$_.'_'.$1} : &LeoDecrypt($cc_cvn);
						}else{
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = $pmts{'newpmtfield'.$_.'_'.$1};
						}
					}else{
						$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = $pmts{'newpmtfield'.$_.'_'.$1};
					}
				}				
				
			}elsif($pmts{'type_'.$1} eq 'Credit-Card'){				
				++$in{'lastpidx'};
				$pmts{'newpmt_'.$in{'lastpidx'}} = 1;				
				$pmts{'newpmttype_'.$in{'lastpidx'}} = 'Credit-Card';
				$pmts{'newamount_'.$in{'lastpidx'}} = $pmts{'amount_'.$1};
				$pmts{'newpaymentdate_'.$in{'lastpidx'}} = $pmts{'paymentdate_'.$1};
				$pmts{'newpmtstatus_'.$in{'lastpidx'}} = 'Approved';
				for (1..11){
					if($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1){						
						if( $_ == 3 ){
							my $cc_number = &load_name('sl_orders_cardsdata', 'ID_orders_payments', $1, 'card_number');
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = (!$cc_number) ? $pmts{'pmtfield'.$_.'_'.$1} : &LeoDecrypt($cc_number);
						}elsif( $_ == 4 ){
							my $cc_date = &load_name('sl_orders_cardsdata', 'ID_orders_payments', $1, 'card_date');
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = (!$cc_date) ? $pmts{'pmtfield'.$_.'_'.$1} : &LeoDecrypt($cc_date);
						}elsif( $_ == 5 ){
							my $cc_cvn = &load_name('sl_orders_cardsdata', 'ID_orders_payments', $1, 'card_cvn');
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = (!$cc_cvn) ? $pmts{'pmtfield'.$_.'_'.$1} : &LeoDecrypt($cc_cvn);
						}else{
							$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = $pmts{'pmtfield'.$_.'_'.$1};
						}
					}else{
						$pmts{'newpmtfield'.$_.'_'.$in{'lastpidx'}} = $pmts{'pmtfield'.$_.'_'.$1};
					}
				}
			}
		}elsif($key =~ /action_(\d+)/){
			##
			if ($prods{'idproducts_'.$1}>0){
				## Duplicate From Existing Products
				if ($prods{'idrelated_'.$1} > 400000000 and $prods{'idrelated_'.$1} < 500000000){
					## Is a SKU
					++$in{'lastidx'};
					$prods{'newproduct_'.$in{'lastidx'}} = 1;
					$prods{'newidproducts_'.$in{'lastidx'}} = $prods{'idproducts_'.$1};
					$prods{'newidrelated_'.$in{'lastidx'}} = $prods{'idrelated_'.$1};
					$prods{'newquantity_'.$in{'lastidx'}} = $prods{'quantity_'.$1};
					$prods{'newidprice_'.$in{'lastidx'}} = $prods{'idprice_'.$1};
					$prods{'newsaleprice_'.$in{'lastidx'}} = $prods{'saleprice_'.$1};
					$prods{'newshipping_'.$in{'lastidx'}} = $prods{'shipping_'.$1};
					$prods{'newdiscount_'.$in{'lastidx'}} = $prods{'discount_'.$1};
				}elsif($prods{'idproducts_'.$1}<700000000 and $prods{'idproducts_'.$1}>600000000){
					## Is a Service
					++$in{'lastidx'};
					$prods{'newproduct_'.$in{'lastidx'}} = 1;
					$prods{'newidproducts_'.$in{'lastidx'}} = $prods{'idproducts_'.$1};
					$prods{'newidrelated_'.$in{'lastidx'}} = $prods{'idrelated_'.$1};
					$prods{'newquantity_'.$in{'lastidx'}} = 1;
					$prods{'newidprice_'.$in{'lastidx'}} = $prods{'idprice_'.$1};
					$prods{'newsaleprice_'.$in{'lastidx'}} = $prods{'saleprice_'.$1};
					$prods{'newshipping_'.$in{'lastidx'}} = 0;
					$prods{'newdiscount_'.$in{'lastidx'}} = $prods{'discount_'.$1};
				}else{
					## Is a Product
					++$in{'lastidx'};
					$prods{'newproduct_'.$in{'lastidx'}} = 1;
					$prods{'newidproducts_'.$in{'lastidx'}} = $prods{'idproducts_'.$1};
					$prods{'newquantity_'.$in{'lastidx'}} = 1;
					$prods{'newidprice_'.$in{'lastidx'}} = $prods{'idprice_'.$1};
					$prods{'newsaleprice_'.$in{'lastidx'}} = $prods{'saleprice_'.$1};
					$prods{'newshipping_'.$in{'lastidx'}} = $prods{'shipping_'.$1};
					$prods{'newdiscount_'.$in{'lastidx'}} = $prods{'discount_'.$1};
				}
			}elsif($prods{'newproduct_'.$1}>0){
				if ($prods{'newidrelated_'.$1} > 400000000 and $prods{'newidrelated_'.$1} < 500000000){
					## Is a SKU
					++$in{'lastidx'};
					$prods{'newproduct_'.$in{'lastidx'}} = 1;
					$prods{'newidproducts_'.$in{'lastidx'}} = $prods{'newidproducts_'.$1};
					$prods{'newidrelated_'.$in{'lastidx'}} = $prods{'newidrelated_'.$1};
					$prods{'newquantity_'.$in{'lastidx'}} = $prods{'newquantity_'.$1};
					$prods{'newidprice_'.$in{'lastidx'}} = $prods{'newidprice_'.$1};
					$prods{'newsaleprice_'.$in{'lastidx'}} = $prods{'newsaleprice_'.$1};
					$prods{'newshipping_'.$in{'lastidx'}} = $prods{'newshipping_'.$1};
					$prods{'newdiscount_'.$in{'lastidx'}} = $prods{'newdiscount_'.$1};
				}elsif($prods{'newidproducts_'.$1}<700000000 and $prods{'newidproducts_'.$1}>600000000){
					## Is a Service
					++$in{'lastidx'};
					$prods{'newproduct_'.$in{'lastidx'}} = 1;
					$prods{'newidproducts_'.$in{'lastidx'}} = $prods{'newidproducts_'.$1};
					$prods{'newidrelated_'.$in{'lastidx'}} = $prods{'newidrelated_'.$1};
					$prods{'newquantity_'.$in{'lastidx'}} = 1;
					$prods{'newidprice_'.$in{'lastidx'}} = $prods{'newidprice_'.$1};
					$prods{'newsaleprice_'.$in{'lastidx'}} = $prods{'newsaleprice_'.$1};
					$prods{'newshipping_'.$in{'lastidx'}} = 0;
					$prods{'newdiscount_'.$in{'lastidx'}} = $prods{'newdiscount_'.$1};
				}else{
					## Is a Product
					++$in{'lastidx'};
					$prods{'newproduct_'.$in{'lastidx'}} = 1;
					$prods{'newidproducts_'.$in{'lastidx'}} = $prods{'newidproducts_'.$1};
					$prods{'newquantity_'.$in{'lastidx'}} = 1;
					$prods{'newidprice_'.$in{'lastidx'}} = $prods{'newidprice_'.$1};
					$prods{'newsaleprice_'.$in{'lastidx'}} = $prods{'newsaleprice_'.$1};
					$prods{'newshipping_'.$in{'lastidx'}} = $prods{'newshipping_'.$1};
					$prods{'newdiscount_'.$in{'lastidx'}} = $prods{'newdiscount_'.$1};
				}	
			}
		}
	} 
	return &trans_txt('done');
}

sub to_edit{
# --------------------------------------------------------
	$va{'diverror'} = "visibility:hidden;";
	$va{'divcod'} = "visibility:hidden;";
	$va{'divcard'} = "visibility:hidden;";
	my ($key, $idx,$idpayment);

	if (!$in{'idx'} and !$in{'idpayment'}){

		foreach my $key (keys %in){
			if ($key =~ /pmtaction_(\d+)/ and !$idx and !$idpayment){

				if ($pmts{'newpmttype_'.$1} eq 'COD' or $pmts{'newpmttype_'.$1} eq 'Deposit' or $pmts{'newpmttype_'.$1} eq 'Referenced Deposit'){
					$in{'idx'} = $1;
				}elsif($pmts{'type_'.$1} eq 'COD' or $pmts{'type_'.$1} eq 'Deposit' or $pmts{'type_'.$1} eq 'Referenced Deposit' and (!$pmts{'capdate_'.$1} or !&check_permissions('edit_order_forced_mode','','')) ){
					$in{'idpayment'} = $1;
				}elsif($pmts{'newpmttype_'.$1} eq 'Credit-Card'){
					$in{'idx'} = $1;
				}elsif($pmts{'type_'.$1} eq 'Credit-Card' and (!$pmts{'capdate_'.$1}) or &check_permissions('edit_order_forced_mode','','')){
					$in{'idpayment'} = $1;
				}
			}
		}
	}

	if ($in{'update'} and ($in{'idx'} or $in{'idpayment'})){
		if ($in{'idx'}>0 and ($pmts{'newpmttype_'.$in{'idx'}} eq 'COD' or $pmts{'newpmttype_'.$in{'idx'}} eq 'Deposit')){
			## Validation / Saving
			if ($in{'amount'}>0){
				$pmts{'newamount_'.$in{'idx'}} = $in{'amount'};
				$va{'message'} = &trans_txt('apporders_pmtupdated');
				$va{'paymentsupdlist'} = &hidden_pmtdata;                  
				return &build_page('apporders/edit_pmt_msg.html');  
			}else{
				$error{'amount'} = &trans_txt('invalid');
				$va{'paymentsupdlist'} = &hidden_pmtdata;
				return &build_page('apporders/edit_pmt_cod.html');
			}
	
		}elsif ($in{'idpayment'}>0 and ($pmts{'type_'.$in{'idpayment'}} eq 'COD' or $pmts{'type_'.$in{'idpayment'}} eq 'COD')){
			## Validation / Saving
			if ($in{'amount'}>0){
				$pmts{'updamount_'.$in{'idpayment'}} = $in{'amount'};
				$va{'message'} = &trans_txt('apporders_pmtupdated');
				$va{'paymentsupdlist'} = &hidden_pmtdata;                  
				return &build_page('apporders/edit_pmt_msg.html');  
			}else{
				$error{'amount'} = &trans_txt('invalid');
				$va{'paymentsupdlist'} = &hidden_pmtdata;
				return &build_page('apporders/edit_pmt_cod.html');
			}
		}elsif ($in{'idx'}>0 and $pmts{'newpmttype_'.$in{'idx'}} eq 'Credit-Card'){
			## Validation
			$in{'pmtfield4'} = $in{'month'}.$in{'year'};
			my (@cols) = ('pmtfield1','pmtfield2','pmtfield3','pmtfield4','pmtfield5','pmtfield6','paymentdate','amount','pmtfield8');
			for (0..$#cols){
				if (!$in{$cols[$_]}	){
					$error{$cols[$_]} = &trans_txt('required');
					++$err;
				}
			}		
			if ($err>0){
				$va{'paymentsupdlist'} = &hidden_pmtdata;
				return &build_page('apporders/edit_pmt_newcard.html');
			}else{
				## Saving data to pmts
				$pmts{'newpmt_'.$in{'idx'}} = 1;
				$pmts{'newpmttype_'.$in{'idx'}} = 'Credit-Card';
				$pmts{'newamount_'.$in{'idx'}} = $in{'amount'};
				$pmts{'newpaymentdate_'.$in{'idx'}} = $in{'paymentdate'};
				$pmts{'newpmtstatus_'.$in{'idx'}} = 'Approved';
				# for (1..11){
				# 	$pmts{'newpmtfield'.$_.'_'.$in{'idx'}} = $in{'pmtfield'.$_.'_'.$in{'idorderspayments_'.$in{'idx'}}};
				# }
				$va{'message'} = &trans_txt('apporders_pmtupdated');
				$va{'paymentsupdlist'} = &hidden_pmtdata;                  
				return &build_page('apporders/edit_pmt_msg.html');  
			}  
		}else{
			## Saving data to pmts
			$pmts{'updamount_'.$in{'idpayment'}} = $in{'amount'};
			$pmts{'updpaymentdate_'.$in{'idpayment'}} = $in{'paymentdate'};
			$pmts{'updpmtstatus_'.$in{'idpayment'}} = 'Approved';
			$va{'message'} = &trans_txt('apporders_pmtupdated');
			$va{'paymentsupdlist'} = &hidden_pmtdata;                  
			return &build_page('apporders/edit_pmt_msg.html');  
		}
	}
	
	if ($in{'idx'} or $in{'idpayment'}){
		$va{'payment_type'} = ($pmts{'newpmttype_'.$in{'idx'}}) ? $pmts{'newpmttype_'.$in{'idx'}} : $pmts{'type_'.$in{'idpayment'}};

		if ($in{'idx'}>0 and ($pmts{'newpmttype_'.$in{'idx'}} eq 'COD' or $pmts{'newpmttype_'.$in{'idx'}} eq 'Deposit'  or $pmts{'newpmttype_'.$in{'idx'}} eq 'Referenced Deposit')){
			$in{'amount'} = $pmts{'newamount_'.$in{'idx'}};
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			return &build_page('apporders/edit_pmt_cod.html');
		}elsif ($in{'idpayment'}>0 and ($pmts{'type_'.$in{'idpayment'}} eq 'COD' or $pmts{'type_'.$in{'idpayment'}} eq 'Deposit' or $pmts{'type_'.$in{'idpayment'}} eq 'Referenced Deposit')){
			$in{'amount'} = $pmts{'amount_'.$in{'idpayment'}};
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			return &build_page('apporders/edit_pmt_cod.html');
		}elsif ($in{'idx'}>0 and $pmts{'newpmttype_'.$in{'idx'}} eq 'Credit-Card'){
			## Load Data to In
			$in{'amount'} = $pmts{'newamount_'.$in{'idx'}};
			$in{'paymentdate'} = $pmts{'newpaymentdate_'.$in{'idx'}};
			for (1..11){
				$in{'pmtfield'.$_}=$pmts{'newpmtfield'.$_.'_'.$in{'idx'}};
			}
			$in{'month'} = substr($in{'pmtfield4'},0,2);
			$in{'year'} = substr($in{'pmtfield4'},2,2);
			$va{'paymentsupdlist'} = &hidden_pmtdata;
			return &build_page('apporders/edit_pmt_newcard.html');
		}else{
			if( ($pmts{'capdate_'.$in{'idpayment'}} eq '0000-00-00' or !$pmts{'capdate_'.$in{'idpayment'}}) and ($pmts{'captured_'.$in{'idpayment'}} eq 'No' or !$pmts{'captured_'.$in{'idpayment'}}) and ($pmts{'authcode_'.$in{'idpayment'}} eq '' or !$pmts{'authcode_'.$in{'idpayment'}}) ){
				# Load Data to In
				$in{'amount'} = $pmts{'amount_'.$in{'idpayment'}};
				$in{'paymentdate'} = $pmts{'paymentdate_'.$in{'idpayment'}};
				for (1..11){
					$in{'pmtfield'.$_}=$pmts{'pmtfield'.$_.'_'.$in{'idpayment'}};
				}
				$in{'pmtfield3'} = "#### #### #### ".substr($in{'pmtfield3'},-4);
				$in{'pmtfield5'} = "## ".substr($in{'pmtfield3'},-1);
				$in{'month'} = substr($in{'pmtfield4'},0,2);
				$in{'year'} = substr($in{'pmtfield4'},2,2);
				$va{'paymentsupdlist'} = &hidden_pmtdata;
				return &build_page('apporders/edit_pmt_oldcard.html');
			}else{
				$va{'message'} = &trans_txt('apporders_noedit');
				$va{'paymentsupdlist'} = &hidden_pmtdata;                  
				return &build_page('apporders/edit_pmt_msg.html');  
			}
		}
	}else{
		$va{'paymentsupdlist'} = &hidden_pmtdata;
		$va{'message'} = &trans_txt('apporders_noedit');
		return &build_page('apporders/edit_pmt_msg.html');
	}

}


sub confirmation{
# --------------------------------------------------------			
	my ($rec,$id_products);
	my (@c) = split(/,/,$cfg{'srcolors'});

	###############
	###############
	###############
	## Order has exchange records?
	###############
	###############
	###############
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders = '$in{'id_orders'}' AND merAction = 'Exchange' AND Status = 'Resolved';");
	my ($exchange_on) = $sth->fetchrow();
	my $reasonpmt = !$exchange_on ? 'Sale' : 'Exchange';
	my ($log_edition);
	#### Ponemos en 0 no es necesario actualizar Lineas que no tienen cambios.
	$in{'force_calc'} = 0 if($cfg{'productos_create_newline'});
	###################################
	### Products
	###################################
	foreach my $key (keys %prods){
		$print_line = 0;


		if ($key =~ /idordersproducts_(\d+)/){

			### Existing Lines
			%rec = ();
			$rec{'id_orders_products'} = $prods{'idordersproducts_'.$1};
			$rec{'type'} = &trans_txt('apporders_origprod');
			$rec{'action'} = &trans_txt('apporders_actskipped');
			
			### Check Line Condition
			$rec{'linetype'} = &trans_txt('cond_original');
			my (@ary) = ('saleprice_','discount_','shipping_','quantity_','idprice_','status_');
			for my $i(0..$#ary){
				if ($ary[$i] ne 'idprice_' and ($in{'force_calc'} or ($prods{'new'.$ary[$i].$rec{'id_orders_products'}} ne $prods{$ary[$i].$rec{'id_orders_products'}}))){				
					$rec{'action'} = "<span style='Color:Red'>".&trans_txt('apporders_actupdate')."</span>";
					if ($i<=2){
						$rec{'changes'} .= substr($ary[$i],0,-1)." : ". &format_price($prods{$ary[$i].$rec{'id_orders_products'}}) ." -> ". &format_price($prods{'new'.$ary[$i].$rec{'id_orders_products'}})."<br>";
						if ($ary[$i] eq 'saleprice_'){
							my $saleprice = ($prods{'newsaleprice_'.$rec{'id_orders_products'}} * $prods{'newquantity_'.$rec{'id_orders_products'}});
							$saleprice = &round($saleprice, $sys{'fmt_curr_decimal_digits'});

							### Cero aritmético
							$saleprice = $cfg{'arithmetic_zero_amt'} if( $saleprice == 0 and $cfg{'arithmetic_zero'} == 1 );

							$rec{'query'}   .= substr($ary[$i],0,-1) . "='".$saleprice."',";
						}else{
							$rec{'query'}   .= substr($ary[$i],0,-1) . "='".&round($prods{'new'.$ary[$i].$rec{'id_orders_products'}},$sys{'fmt_curr_decimal_digits'})."',";
						}
					}else{
						$rec{'changes'} .= substr($ary[$i],0,-1)." : ". $prods{$ary[$i].$rec{'id_orders_products'}} ." -> ". $prods{'new'.$ary[$i].$rec{'id_orders_products'}}."<br>";
						$rec{'query'}   .= substr($ary[$i],0,-1) . "='".$prods{'new'.$ary[$i].$rec{'id_orders_products'}}."',";

						if (($prods{'newsaleprice_'.$rec{'id_orders_products'}} ne $prods{'saleprice_'.$rec{'id_orders_products'}} or $prods{'newquantity_'.$rec{'id_orders_products'}} ne $prods{'quantity_'.$rec{'id_orders_products'}})){
							my $saleprice = ($prods{'newsaleprice_'.$rec{'id_orders_products'}} * $prods{'newquantity_'.$rec{'id_orders_products'}});
							$saleprice = &round($saleprice, $sys{'fmt_curr_decimal_digits'});
							
							### Cero aritmético
							$saleprice = $cfg{'arithmetic_zero_amt'} if( $saleprice == 0 and $cfg{'arithmetic_zero'} == 1 );

							$rec{'query'}   .= "saleprice='".$saleprice."',";

							$in{'force_calc'} = 0 if($cfg{'productos_create_newline'});
						}
					}
				}
			}
			
			## Check taxes			
			if ($prods{'idrelated_'.$rec{'id_orders_products'}} > 400000000 and $prods{'idrelated_'.$rec{'id_orders_products'}} < 500000000){
				# is an SKU
				$id_products = $prods{'idrelated_'.$rec{'id_orders_products'}};
			}elsif($prods{'idproducts_'.$rec{'id_orders_products'}} > 600000000 and $prods{'idproducts_'.$rec{'id_orders_products'}} < 700000000){
				## is a Service
				$id_products = $prods{'idproducts_'.$rec{'id_orders_products'}};
			}else{
				## is a Product
				$id_products = $prods{'idproducts_'.$rec{'id_orders_products'}};
			}

			## Fix bug for Services
			if ($prods{'idrelated_'.$rec{'id_orders_products'}} > 600000000 and $prods{'idrelated_'.$rec{'id_orders_products'}} < 700000000){
				## is a Service
				$id_products = $prods{'idrelated_'.$rec{'id_orders_products'}};
			}
			
			my ($tax_prd) = &calc_taxprod($id_products);
			
			$currentTaxProduct = &round(&Do_SQL(qq|SELECT TAX FROM sl_orders_products WHERE ID_orders_products=$rec{'id_orders_products'}|)->fetchrow(), $sys{'fmt_curr_decimal_digits'});
			$newTaxProduct = &round($tax_prd * (($prods{'newquantity_'.$rec{'id_orders_products'}} * $prods{'newsaleprice_'.$rec{'id_orders_products'}}) - $prods{'newdiscount_'.$rec{'id_orders_products'}}),$sys{'fmt_curr_decimal_digits'});

			#cgierr(qq|$currentTaxProduct <> $newTaxProduct|);
			if ($in{'force_calc'} or ($currentTaxProduct != $newTaxProduct) ){
				$rec{'changes'} .= "Product Taxes : ". $currentTaxProduct." -> ".$newTaxProduct."<br>";
				$rec{'action'} = "<span style='Color:Red'>".&trans_txt('apporders_actupdate')."</span>";
				$rec{'query'} .= "Tax_percent='".$tax_prd."',Tax='".$newTaxProduct."',";
			}
			my ($tax_shp) = &calc_taxshp($id_products);
			if ($in{'force_calc'} or ($prods{'taxshp_'.$rec{'id_orders_products'}} != $tax_shp and $prods{'newshipping_'.$rec{'id_orders_products'}}>0)){
				$rec{'changes'} .= "Shipping Taxes : ". $prods{'taxshp_'.$rec{'id_orders_products'}}." -> ".$tax_shp."<br>";
				$rec{'action'} = "<span style='Color:Red'>".&trans_txt('apporders_actupdate')."</span>";
				$rec{'query'} .= "ShpTax_percent='".$tax_shp."',ShpTax='".&round($tax_shp*$prods{'newshipping_'.$rec{'id_orders_products'}},$sys{'fmt_curr_decimal_digits'})."',";
			}
			if ($rec{'query'}){
				chop($rec{'query'});
				if($cfg{'productos_create_newline'}){
					$query = qq|SELECT original FROM sl_orders_products WHERE ID_orders_products = '$rec{'id_orders_products'}'|;
					$_validate = &Do_SQL($query)->fetchrow();
					if($_validate == 1){
						$id_original = &Do_SQL(qq|select 
						IF(ID_related_original_orders_products > 1,  ID_related_original_orders_products, ID_orders_products)
							from sl_orders_products op
						where 1
							AND ID_orders_products = $rec{'id_orders_products'}|)->fetchrow();

						$va{'sql'} .="INSERT INTO sl_orders_products (`ID_products`, `ID_orders`, `ID_packinglist`, `Related_ID_products`, `ID_products_prices`, `Quantity`, `SalePrice`, `Shipping`, `Cost`, `Tax`, `Tax_percent`, `Discount`, `FP`, `SerialNumber`, `ShpDate`, `Tracking`, `ShpProvider`, `DeliveryDate`, `ShpTax`, `ShpTax_percent`, `PostedDate`, `Upsell`, `Status`,`original`, `ID_related_original_orders_products`, `Date`, `Time`, `ID_admin_users`)
						SELECT `ID_products`, `ID_orders`, `ID_packinglist`, `Related_ID_products`, `ID_products_prices`, `Quantity`, `SalePrice`, `Shipping`, `Cost`, `Tax`, `Tax_percent`, `Discount`, `FP`, `SerialNumber`, `ShpDate`, `Tracking`, `ShpProvider`, `DeliveryDate`, `ShpTax`, `ShpTax_percent`, `PostedDate`, `Upsell`, `Status`, 0, '$id_original', curdate() `Date`, curtime() `Time`,  $usr{'ID_admin_users'} `ID_admin_users` FROM sl_orders_products WHERE ID_orders_products=$rec{'id_orders_products'} LIMIT 1;";
						### Modificamos nuevo Registro
						$va{'sql'} .= "UPDATE sl_orders_products SET $rec{'query'} WHERE ID_orders_products=LAST_INSERT_ID();";
						### Inactivamos Registro Original
						$va{'sql'} .= "UPDATE sl_orders_products SET `Status`='Inactive' WHERE ID_orders_products=$rec{'id_orders_products'};";
					}else{
						$va{'sql'} .= "UPDATE sl_orders_products SET $rec{'query'} WHERE ID_orders_products=$rec{'id_orders_products'};";	
					}
				}else{
					$va{'sql'} .= "UPDATE sl_orders_products SET $rec{'query'} WHERE ID_orders_products=$rec{'id_orders_products'};";
				}
				### Clonamos Linea

				$va{'sql_debug'} .= "UPDATE sl_orders_products SET $rec{'query'} WHERE ID_orders_products=$rec{'id_orders_products'};<br>" if($cfg{'order_edition_debug'});
			}
			$print_line = 1;

			# Log in Notes
			my $tmp_taxes = &round($tax_prd * (($prods{'newquantity_'.$rec{'id_orders_products'}} * $prods{'newsaleprice_'.$rec{'id_orders_products'}}) - $prods{'discount_'.$rec{'id_orders_products'}}),$sys{'fmt_curr_decimal_digits'}) + &round($tax_shp * $prods{'shipping_'.$rec{'id_orders_products'}},$sys{'fmt_curr_decimal_digits'});
			my $tmp_saleprice = ($prods{'newquantity_'.$rec{'id_orders_products'}} * $prods{'newsaleprice_'.$rec{'id_orders_products'}});
			$tmp_saleprice = &round($tmp_saleprice, $sys{'fmt_curr_decimal_digits'});
			$log_edition .= "[M] ID=$rec{'id_orders_products'}, Prod=$id_products, Qty=$prods{'newquantity_'.$rec{'id_orders_products'}}, Net=$tmp_saleprice, Disc=$prods{'discount_'.$rec{'id_orders_products'}}, Shp=$prods{'shipping_'.$rec{'id_orders_products'}}, Tax=$tmp_taxes, Status=$prods{'newstatus_'.$rec{'id_orders_products'}}\n";

		}elsif($key =~ /newproduct_(\d+)/){

			### New Lines
			%rec = ();
			my ($idx) = $1;

			if ($prods{'newstatus_'.$idx} =~ /Active|Exchange/){

				$rec{'type'} = &trans_txt('apporders_newprod');
				$rec{'action'} = "<span style='Color:Red'>".&trans_txt('apporders_actinsert')."</span>";
				$rec{'linetype'} = &trans_txt('cond_new');

				if ($prods{'newidrelated_'.$idx} > 400000000 and $prods{'newidrelated_'.$idx} < 500000000){

					### Cero aritmético
					if( $prods{'newsaleprice_'.$idx} == 0 and $cfg{'arithmetic_zero'} == 1 ){
						$prods{'newsaleprice_'.$idx} = $cfg{'arithmetic_zero_amt'};
						$prods{'newdiscount_'.$idx} = $cfg{'arithmetic_zero_amt'};
					}

					# is an SKU
					my $changes = $prods{'newquantity_'.$idx} ." x (" . &format_sltvid($prods{'newidrelated_'.$idx}).") ". &load_name('sl_parts','ID_parts',substr($prods{'newidrelated_'.$idx},3,9),'Name');
					$rec{'changes'} .= $changes;
					$rec{'query'} = "ID_products='".(99+$idx)."000000',ID_orders=$in{'id_orders'},Related_ID_products='".$prods{'newidrelated_'.$idx}."',Quantity='".$prods{'newquantity_'.$idx}."',";
					$rec{'query'} .=  "SalePrice='".($prods{'newsaleprice_'.$idx} * $prods{'newquantity_'.$idx})."',";
					$id_products = $prods{'newidrelated_'.$idx};

				}elsif($prods{'newidproducts_'.$idx}<700000000 and $prods{'newidproducts_'.$idx}>600000000){

					## is a Service
					my $changes = $prods{'newquantity_'.$idx}." x (" . &format_sltvid($prods{'newidproducts_'.$idx}).") ". &load_name('sl_services','ID_services',substr($prods{'newidproducts_'.$idx},3,9),'Name');
					$rec{'changes'} .= $changes;
					
					# Insert Services as Related_ID_products
					if ($cfg{'e_orders_services_as_related'} and $cfg{'e_orders_services_as_related'} == 1){
						$rec{'query'} = "ID_products='".(99+$idx)."000000',ID_orders=$in{'id_orders'},Related_ID_products='".$prods{'newidrelated_'.$idx}."',Quantity='".$prods{'newquantity_'.$idx}."',";
					}else{
						$rec{'query'} = "ID_products='".$prods{'newidproducts_'.$idx}."',ID_orders=$in{'id_orders'},Related_ID_products=NULL,Quantity='".$prods{'newquantity_'.$idx}."',";
					}

					### Cero aritmético
					if( $prods{'newsaleprice_'.$idx} == 0 and $cfg{'arithmetic_zero'} == 1 ){
						$prods{'newsaleprice_'.$idx} = $cfg{'arithmetic_zero_amt'};
						$prods{'newdiscount_'.$idx} = $cfg{'arithmetic_zero_amt'};
					}

					$rec{'query'} .=  "SalePrice='".($prods{'newsaleprice_'.$idx} * $prods{'newquantity_'.$idx})."',";
					$id_products = $prods{'newidproducts_'.$idx};

				}else{
					### Cero aritmético
					if( $prods{'newsaleprice_'.$idx} == 0 and $cfg{'arithmetic_zero'} == 1 ){
						$prods{'newsaleprice_'.$idx} = $cfg{'arithmetic_zero_amt'};
						$prods{'newdiscount_'.$idx} = $cfg{'arithmetic_zero_amt'};
					}
					
					## is a Product
					my $changes = "1 x (" . &format_sltvid($prods{'newidproducts_'.$idx}).") ". &load_db_names('sl_products','ID_products',substr($prods{'newidproducts_'.$idx},3,9),'[Name] / [Model]');
					$rec{'changes'} .= $changes;
					$rec{'query'} = "ID_products='".$prods{'newidproducts_'.$idx}."',ID_orders=$in{'id_orders'},Quantity='1',ID_products_prices='".$prods{'newidprice_'.$idx}."',";
					$rec{'query'} .= "SalePrice='".$prods{'newsaleprice_'.$idx}."',";
					$rec{'query'} .= "Related_ID_products='".$prods{'newidrelated_'.$idx}."'," if (!$cfg{'e_orders_lock_promo'} and $prods{'newidpromo_'.$idx});
					
					## Upsell
					$rec{'query'} .=  "Upsell='No',";

					$id_products = $prods{'newidproducts_'.$idx};

				}

				my ($tax_shp) = &calc_taxshp($id_products);
				my ($tax_prd) = &calc_taxprod($id_products);
				$rec{'query'} .=  "Shipping='".$prods{'newshipping_'.$idx}."',Discount='".$prods{'newdiscount_'.$idx}."',"
				."Tax='".&round($tax_prd * (($prods{'newquantity_'.$idx} * $prods{'newsaleprice_'.$idx}) - $prods{'newdiscount_'.$idx}),$sys{'fmt_curr_decimal_digits'})."',"
				."Tax_percent='".$tax_prd ."',"
				."ShpTax='".&round($tax_shp * $prods{'newshipping_'.$idx},$sys{'fmt_curr_decimal_digits'})."',"
				."ShpTax_percent='".$tax_shp ."',"
				."Status='".$prods{'newstatus_'.$idx} ."',"
				."Date=CURDATE(),Time=CURTIME(),ID_admin_users='".$usr{'id_admin_users'} ."'";
						
				$va{'sql'} .= "INSERT INTO sl_orders_products SET $rec{'query'};";
				$va{'sql_debug'} .= "INSERT INTO sl_orders_products SET $rec{'query'};<br>" if($cfg{'order_edition_debug'});
				$print_line = 1;

				# Log in Notes
				my $tmp_taxes = &round($tax_prd * (($prods{'newquantity_'.$idx} * $prods{'newsaleprice_'.$idx}) - $prods{'newdiscount_'.$idx}),$sys{'fmt_curr_decimal_digits'}) + &round($tax_shp * $prods{'newshipping_'.$idx},$sys{'fmt_curr_decimal_digits'});
				my $tmp_saleprice = ($prods{'newquantity_'.$idx} * $prods{'newsaleprice_'.$idx});
				$log_edition .= "[N] Prod=$id_products, Qty=$prods{'newquantity_'.$idx}, Net=$tmp_saleprice, Disc=$prods{'newdiscount_'.$idx}, Shp=$prods{'newshipping_'.$idx}, Tax=$tmp_taxes, Status=$prods{'newstatus_'.$idx}\n";

			}

		}

		if ($print_line){
			$d = 1 - $d;
			++$va{'lines'};
			$va{'changeslist'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td valign="top">$va{'lines'}</td>
					<td valign="top">$rec{'type'}</td>
					<td valign="top">$rec{'changes'}</td>
					<td valign="top">$rec{'action'}</td>
				</tr>\n|;
		}
	}

	###################################
	### payments
	###################################
	my %cc_data;
	my $k = 0;	

	foreach my $key (keys %pmts){
		$print_line = 0;
		if ($key =~ /idorderspayments_(\d+)/){
			
			###################################
			### Building Existing Lines
			###################################
			%rec = ();
			$rec{'id_orders_payments'} = $pmts{'idorderspayments_'.$1};
			$rec{'type'} = &trans_txt('apporders_origpmt');
			$rec{'action'} = &trans_txt('apporders_actskipped');
			my (@ary) = ('updamount_','updpaymentdate_','updstatus_');
			for (0..$#ary){

				if ($pmts{$ary[$_].$rec{'id_orders_payments'}} and ($pmts{$ary[$_].$rec{'id_orders_payments'}} != $pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}} or $in{'force_calc'})){
					if ($_ <1){
						$rec{'changes'} .= substr($ary[$_],3,-1) . " : ". &format_price($pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}})." -> ".&format_price($pmts{$ary[$_].$rec{'id_orders_payments'}})."<br>";
					}else{
						$rec{'changes'} .= substr($ary[$_],3,-1) . " : ". $pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}}." -> ".$pmts{$ary[$_].$rec{'id_orders_payments'}}."<br>";
					}
					$rec{'query'} .= substr($ary[$_],3,-1) . "='".$pmts{$ary[$_].$rec{'id_orders_payments'}}."',";
					$rec{'action'} = "<span style='Color:Red'>".&trans_txt('apporders_actupdate')."</span>";
				}
				# el if de arriba no sirve porque esta comparando != numero en el estatus no funciona
				if ($ary[$_] eq 'updstatus_' and $pmts{$ary[$_].$rec{'id_orders_payments'}} ne '' and ($pmts{$ary[$_].$rec{'id_orders_payments'}} ne $pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}} or $in{'force_calc'})){
					$rec{'changes'} .= substr($ary[$_],3,-1) . " : ". $pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}}." -> ".$pmts{$ary[$_].$rec{'id_orders_payments'}}."<br>";
					$rec{'query'} .= substr($ary[$_],3,-1) . "='".$pmts{$ary[$_].$rec{'id_orders_payments'}}."',";

				}
				if ($ary[$_] eq 'updpaymentdate_' and $pmts{$ary[$_].$rec{'id_orders_payments'}} ne '' and ($pmts{$ary[$_].$rec{'id_orders_payments'}} ne $pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}} or $in{'force_calc'})){
					$rec{'changes'} .= substr($ary[$_],3,-1) . " : ". $pmts{ substr($ary[$_],3,-1).'_'.$rec{'id_orders_payments'}}." -> ".$pmts{$ary[$_].$rec{'id_orders_payments'}}."<br>";
					$rec{'query'} .= substr($ary[$_],3,-1) . "='".$pmts{$ary[$_].$rec{'id_orders_payments'}}."',";

				}
			}
			$print_line = 1;
			if ($rec{'query'}){
				chop($rec{'query'});
				$va{'sql'} .= "UPDATE sl_orders_payments SET $rec{'query'} WHERE ID_orders_payments=$rec{'id_orders_payments'};";
				$va{'sql_debug'} .= "UPDATE sl_orders_payments SET $rec{'query'} WHERE ID_orders_payments=$rec{'id_orders_payments'};<br>" if($cfg{'order_edition_debug'});

			}
			
		}elsif ($key =~ /newpmt_(\d+)/ ){

			%rec = ();
			my ($idx) = $1;
			$rec{'id_orders_payments'} = $idx;

			if ($pmts{'newpmtstatus_'.$idx} eq 'Approved'){


				$rec{'type'} = &trans_txt('apporders_newpmt');
				$rec{'action'} = &trans_txt('apporders_actinsert');
				$rec{'changes'} = $pmts{'newpmttype_'.$idx} ." : ". &format_price($pmts{'newamount_'.$idx});
				my($cc_number, $cc_date, $cc_cvn);
				for (1..11){
					if( $pmts{'newpmttype_'.$idx} eq 'Credit-Card' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1) ){
						if( $_ == 3 ){
							$cc_number = &filter_values($pmts{'newpmtfield'.$_.'_'.$idx});
							$rec{'query'} .= "PmtField3='".substr($cc_number, 0, 6)."xxxxxx".substr($cc_number, -4)."',";
						}elsif( $_ == 4 ){
							$cc_date = &filter_values($pmts{'newpmtfield'.$_.'_'.$idx});
							$rec{'query'} .= "PmtField4='xxxx',";
						}elsif( $_ == 5 ){
							$cc_cvn = &filter_values($pmts{'newpmtfield'.$_.'_'.$idx});
							$rec{'query'} .= (length($cc_cvn) == 4) ? "PmtField5='xxxx'," : "PmtField5='xxx',";
						}else{
							$rec{'query'} .= "pmtfield".$_."='".$pmts{'newpmtfield'.$_.'_'.$idx}."',";
						}
					}else{
						$rec{'query'} .= "pmtfield".$_."='".$pmts{'newpmtfield'.$_.'_'.$idx}."',";
					}
				}

				# Puntos Diestel 
				if($pmts{'newpmtpuntos_'.$idx} eq 'on' and $cfg{'use_points'}){
					$rec{'query'} =~ s/PmtField1='\w+'/PmtField1='Mastercard - Puntos'/gi;
				}

				$cc_data{'pmt'.$k}{'cc_type'}	=  $pmts{'newpmttype_'.$idx};
				$cc_data{'pmt'.$k}{'cc_number'}	=  $cc_number;
				$cc_data{'pmt'.$k}{'cc_date'}	=  $cc_date;
				$cc_data{'pmt'.$k}{'cc_cvn'}	=  $cc_cvn;
				++$k;

				$statuspmt = 'Approved';
				$reasonpmt = !$exchange_on ? 'Sale' : 'Exchange';
				### Pagos negativos
				if( $pmts{'newamount_'.$idx} < 0 ){
					$reasonpmt = 'Refund';
					$statuspmt = 'Credit';
				}

				$va{'sql'} .= "INSERT INTO sl_orders_payments SET Type='".$pmts{'newpmttype_'.$idx}."', ID_orders='$in{'id_orders'}'," 
				. $rec{'query'} 
				. "Reason='".$reasonpmt."',"
				. "Amount='".$pmts{'newamount_'.$idx}."',"
				. "Paymentdate='".$pmts{'newpaymentdate_'.$idx}."',"
				. "Status='".$statuspmt."',"
				. "Date=CURDATE(),"
				. "Time=CURTIME(),"
				. "ID_admin_users=$usr{'id_admin_users'};";				
				


				$va{'sql_debug'} .= "INSERT INTO sl_orders_payments SET Type='".$pmts{'newpmttype_'.$idx}."', ID_orders='$in{'id_orders'}'," 
				. $rec{'query'} 
				. "Reason='".$reasonpmt."',"
				. "Amount='".$pmts{'newamount_'.$idx}."',"
				. "Paymentdate='".$pmts{'newpaymentdate_'.$idx}."',"
				. "Status='".$statuspmt."',"
				. "Date=CURDATE(),"
				. "Time=CURTIME(),"
				. "ID_admin_users=$usr{'id_admin_users'};<br>" if($cfg{'order_edition_debug'});
				$print_line = 1;
			}
		}
		if ($print_line){
			$d = 1 - $d;
			++$va{'lines'};
			$va{'changeslist'} .= qq|
				<tr bgcolor='$c[$d]'>
					<td valign="top">$va{'lines'}</td>
					<td valign="top">$rec{'type'}</td>
					<td valign="top">$rec{'changes'}</td>
					<td valign="top">$rec{'action'}</td>
				</tr>\n|;
		}
	}
	if ($in{'runsave'}){
		# Log in Notes
		
		&add_order_notes_by_type($in{'id_orders'},$log_edition,"Low");			
		## todo
		## add JS to close the window in apporders/close.html para cerrar
		my @ary_qry = split(/\;/,$va{'sql'}); 
		$k = 0;
		for my $i(0..$#ary_qry){
			my $sth = &Do_SQL($ary_qry[$i]);

			if( $ary_qry[$i] =~ /INSERT/ and $ary_qry[$i] =~ /sl_orders_payments/ ){
				my $id_payments = $sth->{'mysql_insertid'};

				### Encrypt CC
				if( $cc_data{'pmt'.$k}{'cc_type'} eq 'Credit-Card' and ($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1) ){
					&encrypt_cc($in{'id_orders'}, $id_payments, $cc_data{'pmt'.$k}{'cc_number'}, $cc_data{'pmt'.$k}{'cc_date'}, $cc_data{'pmt'.$k}{'cc_cvn'});
				}
				++$k;
			}
		}
		
		# If Force recalculation
		&force_calc_payment() if ($in{'force_calc'});

		## Update sl_orders totals
		my $sth = &Do_SQL("SELECT 
			count(*) AS OrderQty
			, SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS OrderTotal 
			, SUM(SalePrice) AS OrderNet
			, SUM(Shipping)OrderShp
			, SUM(Discount)OrderDisc
			FROM sl_orders_products WHERE ID_orders = '$in{'id_orders'}' AND Status NOT IN ('Inactive','Order Cancelled');
			");
		my ($orderqty,$ordertotal,$ordernet,$ordershp,$orderdisc) = $sth->fetchrow_array();
		
		my $sth = &Do_SQL("UPDATE sl_orders SET OrderQty='$orderqty', OrderShp='$ordershp', OrderDisc='$orderdisc', OrderNet='$ordernet' WHERE ID_orders='$in{'id_orders'}';");

		## Logs
		
		&add_order_notes_by_type($in{'id_orders'},&trans_txt('opr_orders_order_edited'),"Low");
		$in{'db'} = "sl_orders";
		&auth_logging('opr_orders_order_edited',$in{'id_orders'});

		return &build_page('apporders/close.html');
	}else{
		$va{'paymentsupdlist'} = &hidden_pmtdata;
		return &build_page('apporders/confirmation.html');
	}
}

sub calc_taxprod{
# --------------------------------------------------------
	my ($id_products, $id_orders_products) = @_;

	my ($tax) = 0;
	if ($in{'taxmode'} eq 'on'){
		if ($id_products < 500000000 and $id_products > 400000000){

			# is an SKU
			$tax = &load_name('sl_parts','ID_parts',($id_products - 400000000),'Sale_Tax')/100;

		}elsif($id_products < 700000000 and $id_products > 600000000){

			## is a Service
			$tax = &load_name('sl_services','ID_services',($id_products - 600000000),'Tax')/100;

		}elsif($id_products < 900000000 and $id_products > 800000000){	

			## is a Credit Memo
			my ($sth) = &Do_SQL("SELECT `sl_creditmemos_products`.Tax_percent / 100 FROM sl_orders_products INNER JOIN sl_creditmemos_products ON Related_ID_products = ID_creditmemos WHERE ID_orders = '$in{'id_orders'}' AND sl_orders_products.ID_orders_products = '$id_orders_products' ORDER BY `sl_creditmemos_products`.Tax_percent DESC LIMIT 1;");
			$tax = $sth->fetchrow();
			(!$tax) and ($tax = 0);

		}else{
			## is a Product
			$tax = &load_name('sl_products','ID_products',substr($id_products, -6),'TaxAux')/100;
		}
	}
	return $tax;
	
}

sub calc_taxshp{
# --------------------------------------------------------
	my ($id_products) = @_;
	my ($tax) = 0;
	if ($in{'taxmode'} eq 'on'){
		if ($cfg{'shptax'} and $cfg{'taxp_default'}){
			$tax =$cfg{'taxp_default'};
		}
	}
	return $tax;
}

sub hidden_pmtdata{
# --------------------------------------------------------
	my ($idx, $output);
	foreach my $key (keys %pmts){
		if ($key =~ /idorderspayments_(\d+)/){
			## Existing Payments
			$id_payment =  $pmts{$key};
			$idx = $1;
			$output .= qq|<input type="hidden" name="idorderspayments_$idx" value="$id_payment">\n|;
			$output .= qq|<input type="hidden" name="updamount_$id_payment" value="$pmts{'updamount_'.$id_payment}">\n| if($pmts{'updamount_'.$id_payment});
			$output .= qq|<input type="hidden" name="updpaymentdate_$id_payment" value="$pmts{'updpaymentdate_'.$id_payment}">\n| if($pmts{'updpaymentdate_'.$id_payment});
			$output .= qq|<input type="hidden" name="updstatus_$id_payment" value="$pmts{'updstatus_'.$id_payment}">\n| if($pmts{'updstatus_'.$id_payment});
		}elsif($key =~ /newpmt_(\d+)/){
			my ($idx) = $1;
			$output .= qq|<input type="hidden" name="newpmt_$idx" value="1">\n|;
			$output .= qq|<input type="hidden" name="newpmttype_$idx" value="$pmts{'newpmttype_'.$idx}">\n|;
			$output .= qq|<input type="hidden" name="newamount_$idx" value="$pmts{'newamount_'.$idx}">\n|;
			$output .= qq|<input type="hidden" name="newpaymentdate_$idx" value="$pmts{'newpaymentdate_'.$idx}">\n|;
			$output .= qq|<input type="hidden" name="newpmtstatus_$idx" value="$pmts{'newpmtstatus_'.$idx}">\n|;
			$output .= qq|<input type="hidden" name="newpmtpuntos_$idx" value="$pmts{'newpmtpuntos_'.$idx}">\n|;
			for (1..11){
				$output .= qq|<input type="hidden" name="newpmtfield|.$_.qq|_$idx" value="$pmts{'newpmtfield'.$_.'_'.$idx}">\n|;
			}
		}
	}
	return $output;
}

sub availablepayments{
# --------------------------------------------------------
	my ($output);

	my $add_sql = ($cfg{'e_orders_fp_restricted'} and $cfg{'e_orders_fp_restricted'} ne'')? " AND FP NOT IN ($cfg{'e_orders_fp_restricted'}) ":"";


	## Build Available Payments
	delete($va{'availablepayments'});
	my $sth = &Do_SQL("SELECT FP FROM `sl_products_prices` WHERE `Status`='Active' $add_sql GROUP BY FP ORDER BY FP ASC");
	while (my $p = $sth->fetchrow){
		if ($in{'pmtfield8'} eq $p){
			$output .= "<option value='$p' selected>$p</option>\n";
		}else{
			$output .= "<option value='$p'>$p</option>\n";
		}
	}
	return $output;
}

sub force_calc_payment{
# --------------------------------------------------------
	my $sth = &Do_SQL("SELECT 
		(SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Status IN ('Pending','Approved'))
		, (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Status IN ('Pending','Approved'))
		, SUM(SalePrice - Discount + Shipping + Tax + ShpTax) AS OrderTotal 
		FROM sl_orders_products WHERE ID_orders = '$in{'id_orders'}' AND Status NOT IN ('Inactive','Order Cancelled');");
	my ($total_payments,$num_payments,$total_order) = $sth->fetchrow_array();

	$total_payments = &round($total_payments,$sys{'fmt_curr_decimal_digits'});
	$total_order = &round($total_order,$sys{'fmt_curr_decimal_digits'});
	my $difference = $total_order - $total_payments;
	$difference = &round($difference,$sys{'fmt_curr_decimal_digits'});

	if ($num_payments == 1 and ( $difference == 0.01 or $difference == -0.01)){
		my $sth = &Do_SQL("UPDATE sl_orders_payments SET Amount='$total_order' WHERE ID_orders='$in{'id_orders'}' AND Status IN ('Pending','Approved') LIMIT 1;");
	}
}

############################################################################################
############################################################################################
#	Function: customers_status
#   	Genera de forma dinamica el selector de estatus para customers
#
#	Created by:
#		01-05-2015::Ing. Gilberto Quirino
#
#	Modified By:
#		24-07-2015::Ing. Alejandro Diaz::https://github.com/adiaz-inova/dev2.direksys.com/commit/14bc611cf9717ae67c736827077021f3cf423625
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub postdate{
############################################################################################
############################################################################################

	print "Content-type: text/html\n\n";
	my ($err, $key, $idx, $rec);
	
	if (&check_permissions('edit_order_postdate','','')){

		$in{'id_orders'} = int($in{'id_orders'});	
		$va{'postdated_ok'} = 0;

		my $days = int($in{'days'});
		if( $in{'action'} and $days ){
			if( $days > 0 and $days <= $cfg{'postdateddays'} ){
				&Do_SQL("START TRANSACTION;");
				&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = DATE_ADD(CURDATE(), INTERVAL ".$in{'days'}." DAY)  WHERE ID_orders_payments=".$in{'id_orders_payments'}.";");
				&Do_SQL("UPDATE sl_orders SET Status='New', StatusPay='Post-Dated' WHERE ID_orders=".$in{'id_orders'}.";");
				&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders=".$in{'id_orders'}.", Notes = CONCAT('".&trans_txt('opr_orders_postdated')."\nLa nueva fecha de pago es: ',DATE_ADD(CURDATE(), INTERVAL ".$in{'days'}." DAY), ' y los ',CONVERT(convert('días' using binary) USING utf8),' elegidos para postfechada son: ".$in{'days'}."'), Type = 'Validada',ID_orders_notes_types=13 , Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$usr{'id_admin_users'}.";");
				&Do_SQL("COMMIT;");
				$va{'message'} = &trans_txt('opr_orders_postdated');
				$va{'btn_update'} = '';
				$va{'postdated_ok'} = 1;
			}else{
				++$err;
				$error{'days'} = &trans_txt('invalid').' (max: '.$cfg{'postdateddays'}.' days)';
			}
		}else{

			if( (!$in{'days'} or int($in{'days'}) <= 0 ) and $in{'action'} ){
				++$err;
				$error{'days'} = (!$in{'days'}) ? &trans_txt('required') : &trans_txt('invalid');
			}

		}	

		## Se obtiene el Paymentdate de la orden
		my $sth = &Do_SQL("SELECT ID_orders_payments, Paymentdate, CURDATE() AS hoy FROM sl_orders_payments WHERE ID_orders=".$in{'id_orders'}." AND Status IN('Approved','Pending');");
		$dat_pay = $sth->fetchrow_hashref();

		$in{'id_orders_payments'} = $dat_pay->{'ID_orders_payments'};	
		$in{'paymentdate'} = ($dat_pay->{'Paymentdate'}) ? $dat_pay->{'Paymentdate'} : '0000-00-00';
		$va{'curdate'} = $dat_pay->{'hoy'};

		print &build_page('apporders/postdate.html');
	}else{
		print &build_page('unauth_small.html');
	}
}

#### Services
#conf|taxp_default=0.16
#
### Tax charge in Shipping
#conf|shptax=1

## if shptax=1 this must be configured values net|gross
#conf|shptaxtype=net

1;
