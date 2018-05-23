#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 9           #################
##################################################################

# Last Modified on: 07/15/08 16:58:10
# Last Modified by: MCC C. Gabriel Varela S: Se valida si el pago de la orden tiene código de autorización para pasar por el riskmanager
# Last Modified on: 09/09/08 10:27:33
# Last Modified by: MCC C. Gabriel Varela S: Se agregan líneas para cuando se mandaba a llamar a sltvcyb_sale
# Last Modified on: 09/09/08 10:00:00
# Last Modified by: Jose Ramirez Garcia: Se a¤adieron las opciones que ceran la preeorden para layaway
# Last Modified on: 10/30/08 10:29:59
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no exista downpayment del 7% para pagos quincenales y semanales
# Last Modified on: 10/31/08 15:27:04
# Last Modified by: MCC C. Gabriel Varela S: Se modifica parte que muestra el mensaje de que no se permite pago de una sola exhibición para Lay-Away
# Last Modified on: 11/03/08 13:48:23
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si es un solo pago, y es lay away se haga orden y no preorden
# Last Modified on: 11/10/08 18:51:42
# Last Modified on: 11/17/08 11:54:31
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando se hace un insert a sl__payments sí se admita tipo de pago Layaway, y en otro caso no
# Last Modified RB: 12/30/08  17:52:56 - Se hizo una funcion en console.func.cgi para el traductor de codigos
# Last Modified on: 01/14/09 16:19:39
# Last Modified by: MCC C. Gabriel Varela S: Se agrega nueva traducción de código.
# Last Modified on: 02/03/09 10:00:00
# Last Modified by: JRG : Se agrega validacion de campos de direccion en cod
# Last Modified on: 02/12/09 18:01:22
# Last Modified by: MCC C. Gabriel Varela S: Se cambia USA por United States
# Last Modified on: 03/04/09 17:03:59
# Last Modified by: MCC C. Gabriel Varela S: Se cambia USA por United States
# Last Modified RB: 03/11/09  15:47:37 -- Se agrego traductor para shapecharger
# Last Modified RB: 04/14/09  17:26:29 -- Se comentaron las discriminaciones entre order/preorden en lo que respecta al customer
# Last Modified on: 04/21/09 10:26:20
# Last Modified by: MCC C. Gabriel Varela S: Se hace que la inclusión de dirección para customers COD se haga en los dos casos posibles (nuevo cliente, cliente existente).
# Last Modified on: 05/12/09 15:28:45
# Last Modified by: MCC C. Gabriel Varela S: Se hace que un cliente sea miembro sólo en caso de que compre la membresía, pero no sea preorden.
# Last Modified on: 05/12/09 15:42:32
# Last Modified by: MCC C. Gabriel Varela S: Se agrega variable para determinar si existe membresía en la orden
# Last Modified on: 07/10/09 11:31:33
# Last Modified by: MCC C. Gabriel Varela S. Lic. Roberto Bárcenas: Se hace que no se considere precio de flexipago cuando pnum=1
# Last Modified on: 07/14/09 13:51:05
# Last Modified by: MCC C. Gabriel Varela S: Se comenta la llamada a la función &cod_drivers_to_status
# Last Modified RB: 09/08/09  18:08:43 -- Se agrega nota para Downsale Price Authorization
# Last Modified RB: 02/24/10  12:56:43 -- Se permite cambiar tipo de orden de CC a COD 
# Last Modified RB: 08/09/2010  17:20:43 -- Se corrige problema en los pagos postfechados. Si el usuario usaba el boton back del navegador, se creaba un problema donde se mezclaban los datos de sl_orders con sl_orders_payments. La variable $query se inicilizo y se genero nuevamente.
# Last Modified RB: 03/14/2011  16:51 -- Se agrega idioma a la orden. Para el envio de correo de confirmacion y escaneo
# Last Modified by RB on 06/03/2011 07:02:19 PM : Se agrega procesamiento para Prepaid-Card 

	&pay_type_verification;
#######delete($cses{'id_orders'}); #for tests only
	my $pd_price = 0;
	if($cses{'postdated'} or $in{'postdated'}){

		## ToDo: Manejar diferente precio por monto en orden
		my $this_origin = lc(&load_name('sl_salesorigins', 'ID_salesorigins', $cses{'id_salesorigins'}, 'Channel'));
		$pd_price = ($this_origin and $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}} and $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}} >= 0) ? $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}} : $cfg{'postdatedfesprice'};

	}
	
	#$cses{'pay_type'} = 'cc' if ($cses{'pay_type'} eq 'lay' and $cses{'fppayments'} == 1);
	
	if (!$cses{'id_orders'}){
		
		########################################################
		########################################################
		########################################################
		########################################################
		#### Firs Try Order (No order created yet)
		########################################################
		########################################################
		########################################################
		########################################################


		if($cses{'dayspay'}){
			$in{'dayspay'} = $cses{'dayspay'};
		}
		
		# if($cses{'pay_type'} eq 'lay' && $cses{'fppayments'} <= 1){
		# 	$va{'shippingtype'} = &trans_txt('shp_type_'.$cses{'shp_type'});
		# 	$va{'paytype'} = &trans_txt('pay_type_'.$cses{'pay_type'});
		# 	&save_callsession();
		# 	$url = "/cgi-bin/mod/sales/admin?cmd=console_order&step=8&errmes=".&trans_txt('no_layaway');
		# 	print "Location: $url\n\n";
		# 	exit;
		# }
		
		&load_cfg('sl_customers');
		
		##############################################################################################
		#### Falta poder cargar los datos independiente si es cliente antiguo de  o orders
		##############################################################################################
		if($cses{'pay_type'} eq 'cod' or $cses{'pay_type'} eq 'rd'){
			if($cses{'address1'} eq ''){
				$cses{'address1'} = $cses{'shp_address1'};
			}
			if($cses{'address2'} eq ''){
				$cses{'address2'} = $cses{'shp_address2'};
			}
			if($cses{'address3'} eq ''){
				$cses{'address3'} = $cses{'shp_address3'};
			}
			if($cses{'urbanization'} eq ''){
				$cses{'urbanization'} = $cses{'shp_urbanization'};
			}					
			if($cses{'city'} eq ''){
				$cses{'city'} = $cses{'shp_city'};
			}
			if($cses{'state'} eq ''){
				$cses{'state'} = $cses{'shp_state'};
			}
			if($cses{'zip'} eq ''){
				$cses{'zip'} = $cses{'shp_zip'};
			}										
			if($cses{'country'} eq ''){
				$cses{'country'} = $cses{'shp_country'};
				($cses{'shp_country'}eq 'USA') and ($cses{'country'}='United States');
				($cses{'shp_country'}eq 'USA') and ($cses{'shp_country'}='United States');
			}
		}
		#ADG-->
		#Se agregan datos de Mexico
		if(uc($cfg{'country'}) eq 'MX')  {
			$cses{'country'} = 'Mexico';
			$cses{'shp_country'} = 'MX';
		}
		#ADG<--
		
		$cses{'type'} = "Retail" if (($cses{'membershipinorder'}==1) and($cses{'pay_type'} eq 'wu' or $cses{'pay_type'} eq 'mo' or $cses{'laytype'} eq 'mo' or $cses{'pay_type'} eq 'cod' or ($cses{'laytype'} eq 'cc'  and $cses{'fppayments'}!=1)));

		
		if ($cses{'id_customers'}>0){
			## Returneed customer
			for my $i(2..$#db_cols-3){
				$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
			}
			
			chop($query);
			my ($sth) = &Do_SQL("UPDATE sl_customers SET $query WHERE ID_customers='$cses{'id_customers'}'");
		}else{
			#### Creating New customer
			$query = '';
			for my $i(1..$#db_cols-3){
				$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
			}
			
			my ($sth) = &Do_SQL("INSERT INTO sl_customers SET $query Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
			$cses{'id_customers'} =  $sth->{'mysql_insertid'};

		}
		&save_callsession();
		
		#### Creating New Order
		if($cfg{'orderstype'}==1){
			&newregisterorders();
			## Actualizacion del ID_zones de la orden
			## common/susb/libs/lib.orders.pl			
			if ($cses{'id_orders'}){
				&update_order_zone($cses{'id_orders'});
			}
		}else{
			#&pay_type_verification;
			$query = '';
			$cses{'pay_type'}	=	'mo'	if	($cses{'laytype'} eq 'mo' and  $cses{'fppayments'}==1);
			
			if ($cses{'pay_type'} eq 'wu' or $cses{'pay_type'} eq 'mo' or $cses{'laytype'} eq 'mo' or $cses{'pay_type'} eq 'cod' or $cses{'pay_type'} eq 'rd' or ($cses{'laytype'} eq 'cc'  and $cses{'fppayments'}!=1)){
				&load_cfg('sl_orders');
				if($cses{'pay_type'} eq 'lay' and $cses{'fppayments'}!=1){
					if($cses{'laytype'} eq 'cc'){
						$cses{'status'}='Void';
						$cses{'statuspay'}='None';
					}else{
						## Refenced Deposit New|None|Pending Payment
						if ($cses{'pay_type'} eq 'rd'){
							$cses{'status'}='New';
							$cses{'statuspay'}='Pending Payment';
							$cses{'statusprd'}='None';
						}else{
							$cses{'status'}='Pending';
							$cses{'statuspay'}='None';
						}
					}
					for my $i(1..$#db_cols-5){
						$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
					}
				} else {
					## Refenced Deposit New|None|Pending Payment
					if ($cses{'pay_type'} eq 'rd'){
						$cses{'status'}='New';
						$cses{'statuspay'}='Pending Payment';
						$cses{'statusprd'}='None';
					}else{
						$cses{'statusprd'}='None';
						$cses{'statuspay'}='None';
					}
					for my $i(1..$#db_cols-4){
						$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
					}
				}
				
				## Ptype
				$query =~  s/Ptype=''/Ptype='Referenced Deposit'/ if ($cses{'pay_type'} eq 'rd');
				$query =~  s/Ptype=''/Ptype='COD'/  if  !$cses{'laytype'};
				$query =~  s/Ptype=''/Ptype='Layaway'/  if $cses{'laytype'};
				$query =~  s/Ptype=''/Ptype='Prepaid-Card'/  if $cses{'pay_type'} eq 'ppc';
				
				## Language
				$query =~  s/language=''/language='$cfg{'order_language'}'/;
				$query =~  s/language=''/language='spanish'/;

				
				my ($sth) = &Do_SQL("INSERT INTO sl_orders SET $query $add_query Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				$cses{'id_orders'} =  $sth->{'mysql_insertid'};
				
				if ($cses{'updates7'} and $cses{'id_orders'}>0){
					#&Do_SQL("UPDATE sl_cdr SET Calification='Contestada - Venta', ID_orders='$cses{'id_orders'}' WHERE ID_admin_users=$usr{'id_admin_users'} AND src='$cses{'cid'}'");
				}
			}else{
				&load_cfg('sl_orders');
				for my $i(1..$#db_cols-6){
					$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
				}
				
				## Ptype
				$query =~  s/Ptype=''/Ptype='Credit-Card'/;
				## Language
				$query =~  s/language=''/language='$cfg{'order_language'}'/;
				$query =~  s/language=''/language='spanish'/;
				
				my ($sth) = &Do_SQL("INSERT INTO sl_orders SET $query StatusPrd='None',StatusPay='None',Status='".$cfg{'statuscreateorder'}."',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				$cses{'id_orders'} =  $sth->{'mysql_insertid'};
				
				for my $i(1..$cses{'items_in_basket'}){
					if ($in{"fpago$i".$cses{'items_'.$i.'_id'}} > 1 && $cses{'fppayments'}<$in{"fpago$i".$cses{'items_'.$i.'_id'}}){
						$cses{'fppayments'} = $in{"fpago$i".$cses{'items_'.$i.'_id'}};
					}
				}
				
				
				if($cses{'fppayments'} > 1){
					$in{'dayspay'} = $cses{'dayspay'};
				} else {
					$in{'dayspay'} = 1;
				}
				
				my ($updday) = &Do_SQL("UPDATE sl_orders SET dayspay='".$in{'dayspay'}."' WHERE id_orders=$cses{'id_orders'}");
				
				### Update CDR S7
				if ($cses{'updates7'} and $cses{'id_orders'}>0){
					#&Do_SQL("UPDATE sl_cdr SET Calification='Contestada - Venta', ID_orders='$cses{'id_orders'}' WHERE ID_admin_users=$usr{'id_admin_users'} AND src='$cses{'cid'}'");
				}
			}
			
			&save_callsession;
			$buy_order=$cses{'id_orders'};
			
			##### Si hubo authcode para Downsale
			if($cses{'authcode_downsale'}){
				#&Do_SQL("INSERT INTO sl_orders_notes SET Notes='Downsale Price Authorization', ID_orders = $cses{'id_orders'},Type='Low',Date=Curdate(),Time=NOW(),ID_admin_users='$cses{'authcode_downsale'}'");
				$usr{'id_admin_users'}=$cses{'authcode_downsale'};
				&add_order_notes_by_type($cses{'id_orders'},"Downsale Price Authorization","Low");
			}
			

			########################################################
			########################################################
			########################################################
			########################################################
			#### Payment Creation Section
			########################################################
			########################################################
			########################################################
			########################################################

			%paytype = ('cc'=>'Credit-Card', 'check'=>'Check','wu' => 'WesternUnion','mo'=> 'Money Order','fp'=> 'Fexipago','lay'=>'Credit-Card','cod'=>'COD','ppc'=>'Prepaid-Card','rd'=>'Referenced Deposit');

			if ($cses{'pay_type'} eq 'cc' and $cses{'fppayments'}>1){

				######################
				######################
				#### Flex Pays
				#######################
				#######################

				for ($p = $cses{'fppayments'}; $p >= 1; $p--){
					$query = '';
					for my $i(1..9){
						$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
					}

					($p == 1) and ($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($cses{'fppayment'.$p} -= $pd_price);
					($p == 1) and ($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($cses{'fppayment'.$p} -= $pd_price);

					chop($query);
					my ($sth) = &Do_SQL("X2_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$cses{'fppayment'.$p}',Paymentdate='$cses{'fpdate'.$p}', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				}

			}else{


				######################
				######################
				#### No TDC or One Payment
				#######################
				#######################
				
				$query = '';

				## Refenced Deposit
				if ($cses{'pay_type'} eq 'rd'){
					my $ref = &ref_banco_azteca($cses{'id_orders'});
					$cses{'pmtfield3'} = $ref;
					$va{'ref_banco_azteca'} = $ref;
					$query .= "Paymentdate=CURDATE(),"
				}

				for my $i(1..9){
					$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
				}
				chop($query);
				
				if ($cses{'pay_type'} eq 'wu' or $cses{'pay_type'} eq 'mo' or $cses{'laytype'} eq 'mo' or $cses{'pay_type'} eq 'cod' or ($cses{'laytype'} eq 'cc'  and $cses{'fppayments'}!=1)){
					%paytype = ('cc'=>'Credit-Card', 'check'=>'Check','wu' => 'WesternUnion','mo'=> 'Money Order','fp'=> 'Fexipago','lay'=>'Layaway','cod'=>'COD');
				
					######################
					######################
					#### Not TDC
					#######################
					#######################

					if($cses{'pay_type'} eq 'lay' and $cses{'fppayments'}!=1){

						######################
						######################
						#### Layaway
						#######################
						#######################

						my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$cses{'id_orders'}'");
						for ($p = $cses{'fppayments'}; $p >= 1; $p--){

							$query = '';
							for my $i(1..9){
								$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
							}
							#$query .= ($cses{'laytype'} eq 'cc') ? "Status='None'"	:	"Status='Pending'";
							$query .= ($cses{'laytype'} eq 'cc') ? "Status='Approved'"	:	"Status='Pending'";
							($p == 1) and ($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($cses{'fppayment'.$p} -= $pd_price);
							($p == 1) and ($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($cses{'fppayment'.$p} -= $pd_price);
							#chop($query);
							my ($sth) = &Do_SQL("X3_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$cses{'fppayment'.$p}',Paymentdate='$cses{'fpdate'.$p}',Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");

						}

					} else {

						######################
						######################
						#### One Payment
						#######################
						#######################
						my ($sth) = &Do_SQL("X4_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$cses{'total_order'}',Status='Pending', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					}
				
				}else{

					######################
					######################
					#### TDC One Payment or Refenced Deposit
					#######################
					#######################

					($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($cses{'total_order'} -= $pd_price);
					($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($cses{'total_order'} -= $pd_price);

					my ($sth) = &Do_SQL("X5_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$cses{'total_order'}', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				}
			}
			
			#### Creating Products
			my ($tot_qty,$total,$tot_tax,$price);
			my $upsell ='No';
			my $mqry ='';
			
			for my $i(1..$cses{'items_in_basket'}){
				if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
					$tot_qty += $cses{'items_'.$i.'_qty'};
					if ($cses{'items_'.$i.'_fpprice'}>0 and $cses{'items_'.$i.'_payments'}>1){
						$total += $cses{'items_'.$i.'_fpprice'}*$cses{'items_'.$i.'_qty'};
						$sale_price = $cses{'items_'.$i.'_fpprice'};
					}elsif($cses{'items_'.$i.'_fpprice'}>0 and ($cses{'items_'.$i.'_payments'}==1 or $cses{'items_'.$i.'_payments'}eq '3c')and $cses{'items_'.$i.'_pnum'}==1){
						$total += $cses{'items_'.$i.'_fpprice'}*$cses{'items_'.$i.'_qty'};
						$sale_price = $cses{'items_'.$i.'_fpprice'};
					}else{
						$total += $cses{'items_'.$i.'_price'}*$cses{'items_'.$i.'_qty'};
						$sale_price = $cses{'items_'.$i.'_price'};
					}
					if($cses{'items_'.$i.'_relid'}){
						$relid = " Related_ID_products=".$cses{'items_'.$i.'_relid'}.", ";
					} else {
						$relid = "";
					}
					
					($cfg{'upsell2ndproduct'}) and ($mqry = "Upsell='$upsell',");
					
					
					$cses{'items_'.$i.'_payments'}  =  1  if ($cses{'pay_type'} eq 'wu' or $cses{'pay_type'} eq 'mo' or $cses{'laytype'} eq 'mo' or $cses{'pay_type'} eq 'cod' or ($cses{'laytype'} eq 'cc'  and $cses{'fppayments'}!=1));
					
					## Si el costo de shipping es mas impuestos
					#if($cfg{'shptax'} and (lc($cfg{'shptaxtype'}) eq 'net' or lc($cfg{'shptaxtype'}) eq 'gross')) {
					#	my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'items_'.$i.'_id'}', ".$relid." Quantity='$cses{'items_'.$i.'_qty'}',SalePrice='$sale_price',Shipping='$cses{'items_'.$i.'_newshipping'}',Tax='$cses{'items_'.$i.'_tax'}', Tax_percent='$cses{'items_'.$i.'_tax_percent'}', ShpTax='$cses{'items_'.$i.'_shptax'}', ShpTax_percent='$cses{'items_'.$i.'_shptax_percent'}', Discount='$cses{'items_'.$i.'_discount'}',FP='$cses{'items_'.$i.'_payments'}', $mqry Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					#}else {
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'items_'.$i.'_id'}', ID_products_prices='$cses{'items_'.$i.'_pnum'}', ".$relid." Quantity='$cses{'items_'.$i.'_qty'}',SalePrice='$sale_price',Shipping='$cses{'items_'.$i.'_shp'.$cses{'shp_type'}.''}',Tax='$cses{'items_'.$i.'_tax'}', Tax_percent='$cses{'items_'.$i.'_tax_percent'}', ShpTax='$cses{'items_'.$i.'_shptax'}', ShpTax_percent='$cses{'items_'.$i.'_shptax_percent'}', Discount='$cses{'items_'.$i.'_discount'}',FP='$cses{'items_'.$i.'_payments'}', $mqry Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					#}

					$upsell='Yes';
				}
			}
			
			$mqry='';
			$mqry = "Upsell='Yes',"	if $cfg{'upsell2ndproduct'};
			#### Creating Services as Products
			for my $i(1..$cses{'servis_in_basket'}){
				if ($cses{'servis_'.$i.'_qty'}>0 and $cses{'servis_'.$i.'_id'}>0){
					$tot_qty += $cses{'servis_'.$i.'_qty'};
					$total += $cses{'servis_'.$i.'_price'}*$cses{'servis_'.$i.'_qty'};
					#JRG start 11-06-2008
					if($cses{'servis_'.$i.'_relid'}){
						$related_id_products = $cses{'servis_'.$i.'_relid'};
					} else {
						$related_id_products = "";
					}

					## 08102013:AD::Tax in Services
					if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'servis_'.$i.'_id'}', Related_ID_products='$related_id_products', Quantity='$cses{'servis_'.$i.'_qty'}',SalePrice='$cses{'servis_'.$i.'_price'}',Shipping='0.00',Tax='$cses{'servis_'.$i.'_tax'}',Tax_percent='$cses{'servis_'.$i.'_tax_percent'}',Discount='0.00',FP=1, $mqry Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");						
					}else{
						my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'servis_'.$i.'_id'}', Related_ID_products='$related_id_products', Quantity='$cses{'servis_'.$i.'_qty'}',SalePrice='$cses{'servis_'.$i.'_price'}',Shipping='0.00',Tax='0.00',Discount='0.00',FP=1, $mqry Date=Curdate(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					}
				}				
			}
			## Update Totals
			my ($sth) = &Do_SQL("UPDATE sl_orders SET OrderDisc='$cses{'total_disc'}',OrderQty='$tot_qty',OrderShp='$cses{'shipping_total'}',OrderTax='$cses{'tax_total'}',OrderNet='$total' WHERE ID_orders='$cses{'id_orders'}'");
			#&cod_drivers_to_status($cses{'id_orders'});

			## Match Totales Order VS Payments
			$va{'payment'} = &format_price(&match_totals($cses{'id_orders'}));
			
			## Logs
			$in{'db'} = 'sl_orders';
			&auth_logging('opr_orders_added',$cses{'id_orders'});

			## Actualizacion del ID_zones de la orden
			## common/susb/libs/lib.orders.pl			
			if ($cses{'id_orders'}){
				&update_order_zone($cses{'id_orders'});
			}
			
		}
		#GV Inicia Modificación 21abr2008 Se comenta 1128-1230
		

	}elsif(!$in{'check_payment'}){
		


		########################################################
		########################################################
		########################################################
		########################################################
		#### Check Payment
		########################################################
		########################################################
		########################################################
		########################################################



	 	### Update Order Info
		##############################
		### UPDATE INFO ##############
		### UPDATE CUSTOMER RECORD ###
		##############################
		&load_cfg('sl_customers');
		$query ='';
		for my $i(2..$#db_cols-3){
			$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";
		}
		chop($query);
		my ($sth) = &Do_SQL("UPDATE sl_customers SET $query WHERE ID_customers='$cses{'id_customers'}'");

		#### Creating Products

		my ($sth) = &Do_SQL("DELETE FROM sl_orders_products WHERE ID_orders='$cses{'id_orders'}'");
		
		my ($tot_qty,$total,$tot_tax);
		my $upsell ='No';
		my $mqry='';
		
		($cfg{'upsell2ndproduct'}) and ($mqry = " Upsell='$upsell', ");
		for my $i(1..$cses{'items_in_basket'}){
			if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
				$tot_qty += $cses{'items_'.$i.'_qty'};
				if ($cses{'items_'.$i.'_fpprice'}>0 and $cses{'items_'.$i.'_payments'}>1){
					$total += $cses{'items_'.$i.'_fpprice'}*$cses{'items_'.$i.'_qty'};
					$sale_price = $cses{'items_'.$i.'_fpprice'};
				}elsif($cses{'items_'.$i.'_fpprice'}>0 and ($cses{'items_'.$i.'_payments'}==1 or $cses{'items_'.$i.'_payments'}eq '3c')){
					$total += $cses{'items_'.$i.'_fpprice'}*$cses{'items_'.$i.'_qty'};
					$sale_price = $cses{'items_'.$i.'_fpprice'};
				}else{
					$total += $cses{'items_'.$i.'_price'}*$cses{'items_'.$i.'_qty'};
					$sale_price = $cses{'items_'.$i.'_price'};
				}
				if($cses{'items_'.$i.'_relid'}){
					$relid = " Related_ID_products=".$cses{'items_'.$i.'_relid'}.", ";
				} else {
					$relid = "";
				}
				
				$cses{'items_'.$i.'_payments'}  =  1  if ($cses{'pay_type'} eq 'wu' or $cses{'pay_type'} eq 'mo' or $cses{'laytype'} eq 'mo' or $cses{'pay_type'} eq 'cod' or ($cses{'laytype'} eq 'cc'  and $cses{'fppayments'}!=1));
				
				## Si el costo de shipping es mas impuestos
				#if($cfg{'shptax'} and (lc($cfg{'shptaxtype'}) eq 'net' or lc($cfg{'shptaxtype'}) eq 'gross')) {
				#	my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'items_'.$i.'_id'}', ".$relid." Quantity='$cses{'items_'.$i.'_qty'}',SalePrice='$sale_price',Shipping='$cses{'items_'.$i.'_newshipping'}',Tax='$cses{'items_'.$i.'_tax'}', Tax_percent='$cses{'items_'.$i.'_tax_percent'}', ShpTax='$cses{'items_'.$i.'_shptax'}', ShpTax_percent='$cses{'items_'.$i.'_shptax_percent'}', Discount='$cses{'items_'.$i.'_discount'}',FP='$cses{'items_'.$i.'_payments'}', $mqry Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'"); 
				#}else {
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'items_'.$i.'_id'}', ID_products_prices='$cses{'items_'.$i.'_pnum'}', ".$relid." Quantity='$cses{'items_'.$i.'_qty'}',SalePrice='$sale_price',Shipping='$cses{'items_'.$i.'_shp'.$cses{'shp_type'}.''}',Tax='$cses{'items_'.$i.'_tax'}', Tax_percent='$cses{'items_'.$i.'_tax_percent'}', ShpTax='$cses{'items_'.$i.'_shptax'}', ShpTax_percent='$cses{'items_'.$i.'_shptax_percent'}', Discount='$cses{'items_'.$i.'_discount'}',FP='$cses{'items_'.$i.'_payments'}', $mqry Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'"); 
				#}
				$mqry = "Upsell='Yes',"	if $cfg{'upsell2ndproduct'};
			}
		}
		
		$mqry='';
		$mqry = "Upsell='Yes',"	if $cfg{'upsell2ndproduct'};
		my $total_tax_serv = 0;
		
		#### Creating Services as Products
		for my $i(1..$cses{'servis_in_basket'}){
			if ($cses{'servis_'.$i.'_qty'}>0 and $cses{'servis_'.$i.'_id'}>0){
				$tot_qty += $cses{'servis_'.$i.'_qty'};
				
				## 08102013:AD::Tax in Services
				if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
					$total += $cses{'servis_'.$i.'_price'} * $cses{'servis_'.$i.'_qty'};
					$total_tax_serv += $cses{'servis_'.$i.'_tax'};
					$cses{'tax_total'} += $cses{'servis_'.$i.'_tax'};
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'servis_'.$i.'_id'}', Quantity='$cses{'servis_'.$i.'_qty'}',SalePrice='$cses{'servis_'.$i.'_price'}',Shipping='0.00',Tax='$cses{'servis_'.$i.'_tax'}',Tax_percent='$cses{'servis_'.$i.'_tax_percent'}',Discount='0.00',FP=1, $mqry Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				}else{
					$total += $cses{'servis_'.$i.'_price'} * $cses{'servis_'.$i.'_qty'};
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders='$cses{'id_orders'}',ID_products='$cses{'servis_'.$i.'_id'}', Quantity='$cses{'servis_'.$i.'_qty'}',SalePrice='$cses{'servis_'.$i.'_price'}',Shipping='0.00',Tax='0.00',Discount='0.00',FP=1, $mqry Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
				}
			}
		}
		
		$cses{'orderqty'} = $tot_qty;
		$cses{'ordershp'} = $cses{'shipping_total'};
		$cses{'ordernet'} = $total;
		$cses{'orderdisc'} = $cses{'total_disc'};
		$cses{'ordertax'} = $cses{'tax_total'};
		
		%paytype = ('cc'=>'Credit-Card', 'check'=>'Check','wu' => 'Wester Union','mo'=> 'Money Order','fp'=> 'Fexipago', 'lay'=>'Credit-Card','cod'=>'COD','rd'=>'Referenced Deposit');
		

		########################################################
		########################################################
		########################################################
		########################################################
		#### Payment Creation Section
		########################################################
		########################################################
		########################################################
		########################################################

		if($cses{'pay_type'} eq 'cc'){

			#######################
			#######################
			##### TDC
			#######################
			#######################

			my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$cses{'id_orders'}'");
			
			for ($p = $cses{'fppayments'}; $p >= 1; $p--){
				$query = '';
				for my $i(1..9){
					$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
				}
				
				($p == 1) and ($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} <= 350) and ($cses{'fppayment'.$p} -= $pd_price);
				($p == 1) and ($pd_price > 0) and ($in{'postdated'} or $cses{'postdated'}) and ($cses{'total_order'}-$cses{'shipping_total'}-$cses{'tax_total'} >  350) and ($cses{'fppayment'.$p} -= $pd_price);
				chop($query);
				my ($sth) = &Do_SQL("X6_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query ,Amount='$cses{'fppayment'.$p}',Paymentdate='$cses{'fpdate'.$p}', Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
			}
		}else{

			#######################
			#######################
			##### COD
			#######################
			#######################

			my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders='$cses{'id_orders'}'");
			$query = '';
			for my $i(1..8){
				$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',"	if	$cses{'pay_type'} ne 'cod';
				$query .= "PmtField$i='',"	if	$cses{'pay_type'} eq 'cod';
				
			}				
			my ($sth) = &Do_SQL("X7_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}', $query Amount='$cses{'total_order'}',Paymentdate=DATE_ADD(CURDATE(),INTERVAL 1 DAY), Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
		}
		
		
		#### UPDATE Order
		$query = '';
		&load_cfg('sl_orders');
		if($cses{'fppayments'} > 1){
			$in{'dayspay'} = $cses{'dayspay'};
		} else {
			$in{'dayspay'} = 1;
		}
		for my $i(1..$#db_cols-6){
			$query .= "$db_cols[$i]='".uc(&filter_values($cses{lc($db_cols[$i])}))."',";					
		}
		chop($query);
		
		$query =~  s/Ptype=''/Ptype='Layaway'/  if $cses{'laytype'};
		$query =~  s/Ptype=''/Ptype='Credit-Card'/  if $cses{'pay_type'} eq 'cc';
		$query =~  s/Ptype=''/Ptype='COD'/  if  $cses{'pay_type'} eq 'cod';
		$query .= " , Status='New' "	if $cses{'pay_type'} ne 'cc';
		my ($sth) = &Do_SQL("UPDATE sl_orders SET $query WHERE ID_orders='$cses{'id_orders'}'");
		
	}


	## Double checking for Ptype Value
	my ($sth) = &Do_SQL("SELECT Type FROM sl_orders_payments WHERE ID_orders = $cses{'id_orders'} AND Status NOT IN('Void','System Error') ORDER BY ID_orders_payments DESC LIMIT 1;");
	my $nptype = $sth->fetchrow();
	my $modst = $nptype ne 'Credit-Card' ? ",Status='New'" : '';
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Ptype ='$nptype' $modst WHERE ID_orders= $cses{'id_orders'};");
	my ($sth_updt_cust) = &Do_SQL("UPDATE sl_customers SET Type=IF(Type IS NULL OR Type='','$cfg{'customer_type_default'}',Type) WHERE ID_customers='$cses{'id_customers'}'");	
	
	
	##### Code Translator
	&code_translate('prodchg') if $cfg{'prodchg'};
	&code_translate('bsilver') if $cfg{'bsilver'};
	&code_translate('bgold') if $cfg{'bgold'};
	&code_translate('parterr') if $cfg{'parterr'};
	&code_translate('parterr') if $cfg{'parterr'};
	&code_translate('redugrass') if $cfg{'redugrass'};
	&code_translate('redugrass2') if $cfg{'redugrass2'};
	&code_translate('shapecharge') if $cfg{'shapecharge'};
	&code_translate('everex') if $cfg{'everex'};
	
	## Print ID Order / ID Customer
	if ($cses{'pay_type'} eq 'wu'){
		$cses{'ordert'} = 'W';
		$va{'id_orders'} = 'W'.$cses{'id_orders'};
		$va{'id_customers'} = 'W'.$cses{'id_customers'};
	}elsif($cses{'pay_type'} eq 'mo'){
		$cses{'ordert'} = 'M';
		$va{'id_orders'} = 'M'.$cses{'id_orders'};
		$va{'id_customers'} = 'M'.$cses{'id_customers'};
	}elsif($cses{'laytype'} eq 'mo' or ($cses{'laytype'} eq 'cc' and $cses{'fppayments'}!=1)){		
		$cses{'ordert'} = 'L';
		$va{'id_orders'} = 'L'.$cses{'id_orders'};
		$va{'id_customers'} = 'L'.$cses{'id_customers'};
	}elsif($cses{'pay_type'} eq 'cod'){
		$va{'id_orders'} = 'C'.$cses{'id_orders'};
		$va{'id_customers'} = 'C'.$cses{'id_customers'};
	}else{
		$cses{'ordert'} = '';
		$va{'id_orders'} = $cses{'id_orders'};
		$va{'id_customers'} = $cses{'id_customers'};	
		#RB Start - &check_rman -apr2908;
		if($cses{'pay_type'} eq 'cc'){
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$cses{'id_orders'}' AND AuthCode<>'0000' AND AuthCode IS NOT NULL AND AuthCode<>''");
			if ($sth->fetchrow>0){
				$riskorder = &check_rman($cses{'id_orders'});
				if ($riskorder ne 'OK'){
					&Do_SQL("UPDATE sl_orders SET Status = 'Pending',StatusPay='Review Order' WHERE ID_orders = $cses{'id_orders'}");


					&add_order_notes_by_type($cses{'id_orders'},"Risk Order\n$riskorder","High");

					$va{'riskorder'} = &trans_txt('riskorder_pending');
				}else{
					$va{'riskorder'} = '...';
				}
			}
		}
		#RB End				
	}
	
	## Prepaid-Card Data
	if($cses{'pay_type'} eq 'ppc'){
		my($query);
		#my %ppcdata = ('ppc_customer_name'=>'Name', 'ppc_id_type'=>'ID Type','ppc_id_number'=>'ID Number','ppc_cellphone'=> 'Cellphone','ppc_this_address1'=> 'Address1','ppc_this_address2'=> 'Address2','ppc_this_address3'=> 'Address3','ppc_this_city'=> 'City','ppc_this_state'=> 'State','ppc_this_zip'=> 'Zipcode','ppc_postal_address1'=> 'Postal Address1','ppc_postal_address2'=> 'Postal Address2','ppc_postal_address3'=> 'Postal Address3','ppc_postal_city'=> 'Postal City','ppc_postal_state'=> 'Postal State','ppc_postal_zip'=> 'Postal Zipcode');
		foreach my $key (keys %cses){
			if($key =~ /^ppc_(.*)/){
				$fieldname = $1;
				if($key =~ /this/ or !$cses{'ppc_same_dir'}){
					# skip this
				}else{
					$query .= ucfirst($fieldname). "=". &filter_values($cses{$key})."\n";
					#$query .= " $ppcdata{$key}=$cses{$key}\n";
				}
			}
		}
		my($sth)=&Do_SQL("INSERT INTO sl_customers_notes SET ID_customers='$cses{'id_customers'}', Type='Low', Notes='Prepaid-Card Info\n$query',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
		my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='New' WHERE ID_orders='$cses{'id_orders'}'");
	}
	
	
			#####################################################################
			#####################################################################
			#####################################################################
			#####################################################################
			###############
			###############    All To One Payments
			###############
			#####################################################################
			#####################################################################
			#####################################################################
			#####################################################################


	if($cfg{'allorders_onepayment'} and ($cses{'pay_type'} eq 'cc' or $cses{'laytype'} eq 'cc') ) {

		##########
		########## SUM All Payments
		##########

		for my $i(1..$cses{'items_in_basket'}){
			if ($in{"fpago$i".$cses{'items_'.$i.'_id'}} > 1 && $cses{'fppayments'}<$in{"fpago$i".$cses{'items_'.$i.'_id'}}){
				$cses{'fppayments'} = $in{"fpago$i".$cses{'items_'.$i.'_id'}};
			}
		}

		my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders = '$cses{'id_orders'}';");
		my ($amount) = $sth->fetchrow();

		my ($sth1) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders  = '$cses{'id_orders'}' ORDER BY ID_orders_payments LIMIT 1;");
		my ($idop) = $sth1->fetchrow();

		#&cgierr("$amount > 0 and $idop");
		if($amount > 0 and $idop){

			&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = CURDATE(), Amount = '$amount', PmtField8 = '$cses{'fppayments'}', PmtField10 = '$cfg{'allorders_onepayment_cond1'}' WHERE ID_orders_payments  = '$idop';");
			&Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders = '$cses{'id_orders'}' AND ID_orders_payments  > '$idop';");

		}

		## Match Totales Order VS Payments
		$va{'payment'} = &format_price(&match_totals($cses{'id_orders'}));

	}	 



			#####################################################################
			#####################################################################
			#####################################################################
			#####################################################################
			###############
			###############    Check Payment / Post Dated Section
			###############
			#####################################################################
			#####################################################################
			#####################################################################
			#####################################################################

	$va{'id_salesorigins'} = $cses{'id_salesorigins'};
	if ($in{'check_payment'} or $in{'postdated'} or $cses{'postdated'}){

		my (%tmp,$cdata);
		my ($status,$msg,$code);

		if($cses{'pay_type'} eq 'cc' or $cses{'laytype'} eq 'cc'){

			$va{'speechname'}= 'ccinbound:8a- Order Number Credit Card Approved';
			
			if (($in{'postdated'} or $cses{'postdated'}) && $cfg{'postdatedbutton'}){

				######################
				######################
				##### Post Dated
				######################
				######################
			#@ivanmiranda :: Ticket 2015050710000361
				if(0 == $in{'days'}) {
					$in{'days'} = 1;
				}
				$datetosend = &sqldate_plus(&get_sql_date(),$in{'days'}+1);
							
				if( $cfg{'allorders_onepayment'} ) {

					####################
					####################
					##### All To One Payments
					####################
					####################

					&Do_SQL("UPDATE sl_orders_payments SET Amount = Amount + $pd_price, Paymentdate = DATE_ADD(CURDATE(), INTERVAL $in{'days'} DAY)  WHERE ID_orders  = '$cses{'id_orders'}' ORDER BY ID_orders_payments LIMIT 1;");
					$status = 'OK';


				}else{
					&update_flexipago($va{'id_orders'},$datetosend);

					$query = '';
					for my $i(1..9){
						$query .= "PmtField$i='".&filter_values($cses{'pmtfield'.$i})."',";
					}
					chop($query);
					$query =~ s/PmtField8=''/PmtField8='Post-Dated Fee'/;

					&Do_SQL("X8_INSERT INTO sl_orders_payments SET ID_orders='$cses{'id_orders'}',Type='$paytype{$cses{'pay_type'}}',$query,Amount='$pd_price',Paymentdate=CURDATE(), Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
					my ($stlid) = &Do_SQL("SELECT LAST_INSERT_ID()");
					$idordpay = $stlid->fetchrow;
					
					######################
					######################
					##### Post Dated Cybersource
					######################
					######################

					my ($num_of_retriespd) = 2;
					do{
						require ("../../common/apps/cybersubs.cgi");
						($status,$msg,$code) = &sltvcyb_sale($cses{'id_orders'}, $idordpay);
						$cses{'retriespd'} +=1;
					}while($status ne 'OK' and $cses{'retriespd'}<=$num_of_retriespd);	

				}


				if ($status eq 'OK'){

					&Do_SQL("UPDATE sl_orders SET Status='New', StatusPay='Post-Dated' WHERE ID_orders= $va{'id_orders'}");
					my ($sth)=&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$va{'id_orders'}', Notes=concat('La fecha de hoy es: ',Curdate(),' y los días elegidos para postfechada son: $in{'days'}'), Type='Low',ID_orders_notes_types=1, Date=Curdate(), Time=Now(), ID_admin_users='$usr{'id_admin_users'}'");

					#&status_logging($va{'id_orders'},'New');

				}elsif ($cses{'retriespd'}>2){

					# do nothing
					&Do_SQL("UPDATE sl_orders SET Status='Void' WHERE ID_orders= $va{'id_orders'}");
					#&status_logging($va{'id_orders'},'Void');

					&add_order_notes_by_type($va{'id_orders'},"La orden se pasa a Void por fallo en el cobro del posdated fee","Low");
					
				}else{
						&save_callsession();
						$url = "/cgi-bin/mod/sales/admin?cmd=console_order&step=7&check_payment=1&reasoncode=$code&dayspay=$cses{'dayspay'}";
						print "Location: $url\n\n";
						exit;
				}


			}

		}else{

			if (!$sys{'ck_verification_inb'}){
				my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='New' WHERE ID_orders='$va{'id_orders'}'");
				#&status_logging($va{'id_orders'},'New');
			}


			###############################################
			###############################################
			#############
			############# Posfecha COD
			#############
			###############################################
			###############################################

			if ($cses{'pay_type'} eq 'cod' and ($in{'postdated'} or $cses{'postdated'}) and $cfg{'postdatedbutton'}){

				######################
				######################d
				##### Post Dated
				######################
				######################

				###
				### COD ya tiene el pago agregado, si se requiere tener mas de un pago, se debe revisar desde la creacion del pago y aqui sumarlo al monto
				#@ivanmiranda
				if($in{'days'} == 0 or $in{'days'} eq '' or !$in{'days'}) {
					$in{'days'} = 1;
				}
				&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = DATE_ADD(CURDATE(), INTERVAL $in{'days'} DAY)  WHERE ID_orders  = '$cses{'id_orders'}' ORDER BY ID_orders_payments LIMIT 1;");
				&Do_SQL("UPDATE sl_orders SET Status='New', StatusPay='Post-Dated' WHERE ID_orders = '$cses{'id_orders'}';");
				&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$cses{'id_orders'}', Notes = CONCAT('La fecha de hoy es: ',CURDATE(),' y los días elegidos para postfechada son: $in{'days'}'), Type='Low',ID_orders_notes_types=1, Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");

				$in{'step'} = '10';
				$in{'sid'} = $sid;

			}			

			$va{'speechname'}= 'ccinbound:8b- Order Number Check Approved';
		}
		#&save_callsession('delete');


	}elsif($cses{'pay_type'} eq 'cc' or ($cses{'laytype'} eq 'cc' and $cses{'fppayments'}==1)){
		$in{'step'} = '9cc';
		$in{'sid'} = $sid;
	}elsif($cses{'pay_type'} eq 'check'){
		$in{'step'} = '9ck';
		$in{'sid'} = $sid;	
	}elsif($cses{'pay_type'} eq 'lay' and $cses{'laytype'} eq 'cc'){
		$in{'step'} = '9lay';
		$in{'sid'} = $sid;	
	}elsif($cses{'pay_type'} =~ /cod|ppc/){
		$in{'step'} = '10';
		$in{'sid'} = $sid;
	}else{
		$va{'speechname'}= 'ccinbound:8b- Order Number';
	}


	#####
	##### Status Logging
	#####
	&status_logging($cses{'id_orders'},'New') if int($cses{'id_orders'}) > 0;

	# This block the advanced bar
	$cses{'session_closed'} = 1 if ($cses{'id_orders'} and $cses{'id_customers'} and $cses{'pay_type'} eq "rd");

	&cod_redir;

1;

