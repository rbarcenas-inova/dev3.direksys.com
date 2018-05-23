#!/usr/bin/perl

sub entershipment {
# --------------------------------------------------------
# Created on: 3/jun/2008 04:26:18 PM GMT -05:00
# Last Modified on: 17/12/2015
# Last Modified by: Fabian Cañaveral
# Author: Carlos Haas
# Description : 
# Parameters :
# Last Modified on: 09/09/08 09:43:03
# Last Modified by: MCC C. Gabriel Varela S: Se agregan líneas de configuración para llamar a sltvcyb_capture
# Last Modified on: 09/19/08 10:30:29
# Last Modified by: MCC C. Gabriel Varela S: Se valida que si en la variable de sistema no se permite enviar producto que no existe para un warehouse
# Last Modified on: 10/24/08 17:31:20
# Last Modified by: MCC C. Gabriel Varela S: Se agrega tipo de tracking number para fedex
# Last Modified on: 01/12/09 10:24:39
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la consulta que estaba en ## Checking for SETs/Kits, ahora sólo se contemplan los que tienen status Active y que además no se ha enviado
# Last Modified on: 01/12/09 15:00:00
# Last Modified by: Jose Ramirez Garcia: Se adapto para que funcione enterlocaldelivery
# Last Modified RB: 02/25/09  16:01:08 -- Se agrego prevencion de envio para preordenes duplicadas
# Last Modified GV: 03/06/09  11:49:30 -- Se inicializa $id_orders = 0 
# Last Modification by JRG : 03/12/2009 : Se agrega log
# Last Modified RB: 03/17/09  16:30:34 -- Se activo la opcion de Status Exchange, Reship en envio de productos con Set
# Last Modified on: 05/13/09 16:53:38
# Last Modified by: MCC C. Gabriel Varela S: Se cambia SL por variable de sistema
# Last Modified on: 05/26/09 12:19:39
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar los items enviados.
# Last Modified on: 06/01/09 13:50:14
# Last Modified by: MCC C. Gabriel Varela S: Se evalúa lo que regrese cost_inventory
# Last Modified RB: 06/18/09  15:16:10 -- Si el escaneo es exitoso se manda llamar la funcion &accounting_keypoints($id_orders); que registra los movimientos de venta del modulo de contabilidad
# Last Modified on: 07/09/09 10:36:18
# Last Modified by: MCC C. Gabriel Varela S: Se habilita paquetería IW
# Last Modified RB: 07/21/09  12:09:45 -- Se incluye la carga de UPCs via funcion para Bulk shipping
# Last Modified RB: 07/23/09  11:22:46 -- Se modifica la llamada a la funcion &accounting_sale. Solamente se llama si el texto regresado es el resultado exitoso. Se verifica que el texto regresado no sea un error en payments
# Last Modified RB: 08/12/09  13:39:38 -- Se hacen modificaciones para permitir escaneo de ordenes de exportacion. Validadas por la variable $consolidated, su ejecucion esta al final de esta funcion.
# Last Modified on: 09/16/09 12:39:31
# Last Modified by: MCC C. Gabriel Varela S: Se habilita cookie multi compañía
# Last Modified RB: 09/21/09  18:02:32 -- userGroup(1,2,8) valido para errores en la orden. Se crea valor $in{'auth_admin'} y se borra el valor del campo en &cost_inventory
# Last Modified by RB on 05/17/2010  16:28:32 -- Se agrega envio de correo electronico al cliente cuando se escanea la orden
# Last Modified on: 04/14/11 10:25:42 AM
# Last Modified by: MCC C. Gabriel Varela S: Se generan reward points
# Last modified on 6 May 2011 13:46:24
# Last modified by: MCC C. Gabriel Varela S. :Se incluye sms notification
# Last modified on 9 May 2011 15:32:30
# Last modified by: MCC C. Gabriel Varela S. : Se condiciona sms notification
# Last modified on 26 May 2011 11:59:23
# Last modified by: MCC C. Gabriel Varela S. :Se hace que no se establezcan los puntos aquí
# Last Modified by RB on 06/23/2011 06:29:04 PM : Se agrega actualizacion sl_cod_sales para ordenes COD
# Last Modified by RB on 07/06/2011 04:39:43 PM : Se agrega nota en la orden para saber el warehouse de escaneo  
# Last Modified by RB on 04/19/2012 04:48:43 PM : Se modifica busqueda de productos sin enviar en la orden (Se valida >= 0)
# Last Modified by RB on 07/03/2013 12:00:00 PM : Se agrega validacion para Status Active de cliente
# Last Modified by Fabian Cañaveral on 17/12/2015 : Se modifica la forma de procesar ordenes en traking se procesa ahora producto.


	my ($status,$statmsg);
	my (@carriers);
	my $duplicated = 0;
	my $consolidated = 0;
	my $sumshipp = 0;
	my $str_shp;
	my $whvirtual=0;
	my $id_warehouses_batches;
	my $log_tracking;
	my $id_orders;
	$in{'shpdate'} = &get_sql_date();

	$cfg{'shipping_companies'} .= ",".join(',',&load_enum_toarray('sl_orders_products','ShpProvider'));

	if ($in{'action'}){

		if (!$in{'shpdate'} or !$in{'id_warehouses'} or (!$in{'tracking'} && !$in{'localdelivery'})){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}
		$log_tracking = $in{'tracking'};

		print "Set-Cookie: ck_warehouses$in{'e'}=$in{'id_warehouses'} ; expires=; path=/;\n";

		if($in{'id_packinglist'}){

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_packinglist='$in{'id_packinglist'}' AND ISNULL(Tracking);");
			if ($sth->fetchrow() == 0){
				$va{'message'} = &trans_txt('packinglist_updinvfld');
				++$err;
			}

		}

		if (!$err){
			my ($order_type, $ctype, $customer_status, $status, $msg, $tracking, $trktype, @id_products, %ids, $num);
			$id_orders=0;

			@ary = split(/\n|\s/,$in{'tracking'});

			##### Consolidated Shipment -- Si el envio es bulk
			if ($in{'bulk'}){ 

				LINES: for (0..$#ary){
					
					$ary[$_] =~ s/\n|\r|\s//g;
					if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){

						$id_orders = $1;
						if ($id_orders >0){

							$consolidated = 1 if &is_exportation_order($id_orders);
							$in{'tracking'} .= &get_bulk_products('orders',$id_orders) if !$consolidated;
							last LINES;

						}

					}

				}

			}
			

			if (!$consolidated){

				my $flag_zone = 0;
				@ary = split(/\n/,$in{'tracking'});
				LINE: for my $i(0..$#ary){

					$ary[$i] =~ s/\n|\r//g;

					if ($ary[$i] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){

						$id_orders = $1;
						$ary[$i] = '';
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders = ". $id_orders ." AND sl_orders.Status IN ('Processed','Shipped');");
						if ($sth->fetchrow==0){
							$id_orders = 0;
							$va{'message'} .= "<li>".trans_txt('scan_order_invalid_status')."</li>";
						}

						
						if(&table_field_exists('sl_warehouses','DeliveryZones')){

							###
							## Zone Validation
							###
							my $id_zones = &load_name('sl_orders', 'ID_orders', $id_orders, 'ID_zones');
							my @ary_zones = split(/,/, &load_name('sl_warehouses', 'ID_warehouses', $in{'id_warehouses'}, 'DeliveryZones'));
							#&cgierr("$id_zones vs " . scalar @ary_zones);
							if(scalar @ary_zones){

								## Warehouse with Delivery Zones Limited
								$flag_zone = 1;
								for(0..$#ary_zones){

									my $this_zone = $ary_zones[$_];
									if ($this_zone == $id_zones){
										$flag_zone = 0;
										last;
									}

								}

								if($flag_zone){

									## Warehouse doesn't serve the zone
									$va{'message'} .= "<li>".trans_txt('scan_order_invalid_warehouse_deliveryzone')."</li>";
								
								}
								
							}

						}
						

					}elsif($ary[$i]){

						if (!$tracking){

							@carriers = split(/,/, $cfg{'shipping_companies'}) if ($#carriers<0);
							for (0..$#carriers){
								if ($cfg{'shprov_'.$carriers[$_]}){
									my ($trknum) = $ary[$i];
									eval { "if ($cfg{'shprov_'.$carriers[$_]}){$tracking = $trknum; $ary[$i]=''; $trktype='$carriers[$_]'; next LINE;}"};
								}
							}

							if ($i == 1 and $ary[$i] =~ /^([A-Za-z0-9]+)/ and !$tracking){

								$tracking = $1;
								# Get shipping companies by REGEX
								if($ary[$i] =~ /\b(1Z ?[0-9A-Z]{3} ?[0-9A-Z]{3} ?[0-9A-Z]{2} ?[0-9A-Z]{4} ?[0-9A-Z]{3} ?[0-9A-Z]|[\dT]\d\d\d ?\d\d\d\d ?\d\d\d)\b/i){
									$trktype = 'UPS';
								}elsif($ary[$i] =~ /(\b\d{34}\b)/){
									$trktype = 'FEDEX';
								}elsif($ary[$i] =~ /(\b\d{22}\b)/){
									$trktype = 'ESTAFETA';
								}elsif($ary[$i] =~ /DRIVER/i){
									$trktype = 'DRIVER';
								}

								if ($cfg{'shipping_companies'} =~ /$trktype/i){
									$ary[$i] = '';
									next LINE;
								}else{
									$tracking = '';
									$trktype = '';
								}
							}elsif(!$tracking){
								($trktype,$tracking) = split(/\@/, $ary[$i]);
								if ($cfg{'shipping_companies'} =~ /$trktype/i){
									$ary[$i] = '';
									next LINE;
								}else{
									$tracking = '';
									$trktype = '';
								}
							}
						}
						my ($sth) = &Do_SQL("SELECT ID_sku_products, IsSet FROM sl_skus WHERE UPC='".&filter_values($ary[$i])."';");
						($id, $isset) = $sth->fetchrow_array;
						++$num;
						if ($id >0 and $isset ne 'Y'){
							my ($sthinv,$recinv);
							if (!$cfg{'allow_inv_negatives'}){
								$sthinv=&Do_SQL("SELECT IF(SUM(Quantity)>0,SUM(Quantity),0) AS Quantity FROM sl_warehouses_location WHERE ID_products = '$id' AND ID_warehouses = '$in{'id_warehouses'}' ");
								$recinv=$sthinv->fetchrow;
								if (!$recinv){
									$va{'message'} .= "<li>" . trans_txt('scan_no_stock') .  $ary[$i] ." ". trans_txt('warehouse') . ": $in{'id_warehouses'}</li>";
								}
							}
							push(@id_products,$id);
							push(@upcs,$ary[$i]);
							$ids{$num}[0] = $id;
							$ids{$num}[1] = $ary[$i];
						}elsif ($id >0 and $isset eq 'Y'){
							$ids{$num}[0] = '--';
							$ids{$num}[1] = $ary[$i];
							$ids{$num}[2] = 'ERROR';
							$ids{$num}[3] = "<li>UPC $ary[$i] ". trans_txt('upc_kit') . "(". &format_sltvid($id) .") </li>";
						}else{
							$ids{$num}[0] = '--';
							$ids{$num}[1] = $ary[$i];
							$ids{$num}[2] = 'ERROR';
							$ids{$num}[3] = "<li>". trans_txt('scan_upc_unknown')." $ary[$i]</li>";
						}
						#$sumshipp += substr($ary[$i],-5);
						$str_shp .= "$sumshipp + ".($id - 400000000)."\n";
						$sumshipp += ($id - 400000000);
					}
				}

				if (!$id_orders){
				    $va{'message'} .= "<li>". trans_txt('scan_order_unknown')."</li>";
				}else{

					my ($sth) = &Do_SQL("SELECT Ptype,sl_customers.Status FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
					($order_type,$customer_status) = $sth->fetchrow();

					($customer_status ne 'Active') and ($va{'message'} .= "<li>". trans_txt('scan_order_customer_' . lc($customer_status))."</li>");

				}

				## Validacion de remesa unica
				$sql = "SELECT COUNT(distinct sl_warehouses_batches_orders.ID_warehouses_batches)inbatches, sl_warehouses_batches_orders.ID_warehouses_batches
				FROM sl_warehouses_batches_orders 
				INNER JOIN sl_orders_products on sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products
				WHERE sl_orders_products.Status NOT IN ('Inactive')
				AND sl_orders_products.ID_orders='$id_orders'
				AND sl_warehouses_batches_orders.Status='In Fulfillment'
				ORDER BY sl_warehouses_batches_orders.ID_warehouses_batches desc, sl_warehouses_batches_orders.ID_orders_products asc";
				$sth_wbo = &Do_SQL($sql);
				my($unique_batch, $val_id_warehouses_batches) = $sth_wbo->fetchrow();
				
				if ($unique_batch > 1){
				    $va{'message'} .= "<li>". trans_txt('scan_order_wbo_fail')."</li>";
				}

				# my $val_status_batch = &load_name('sl_warehouses_batches','ID_warehouses_batches',$val_id_warehouses_batches,'Status');
				# if ($val_status_batch ne 'Processed'){
				#     $va{'message'} .= "<li>". trans_txt('batch_not_processed')."</li>";
				# }

				## Is New COD Shipping OR Exchange?
				my $is_exchange =  &delivery_status_order($id_orders);

				## Local COD /Local Delivery?
				if ($order_type eq 'COD' and !$is_exchange and !$va{'message'}){ 

				    $whvirtual = &load_name('sl_orders','ID_orders',$id_orders,'ID_warehouses');
				    $sthwv = &Do_SQL("SELECT ID_warehouses FROM sl_orders_datecod WHERE ID_orders = '$id_orders' AND Status = 'Active';");
				    my ($whvirtual2) = $sthwv->fetchrow();
				    (!$whvirtual) and ($whvirtual = $whvirtual2);

				    if ($id_orders and !$whvirtual){
					   $va{'message'} .= "<li>".trans_txt('scan_order_nocoverage')."</li>";
				    }

				    my $sumorder = &ordercomplete($id_orders);
				    #&cgierr("$sumorder != $sumshipp");
				    if ($sumorder != $sumshipp){
					    $va{'message'} .= "<li>".trans_txt('scan_order_codincomplete')."</li>";
				    }

				    if(!$tracking or !$trktype){
						$tracking = "Local COD";
						$trktype  = "Local COD";
				    }

				}elsif($in{'localdelivery'} and $is_exchange == 2){				     

					## COD in transit
					$va{'message'} .= "<li>".trans_txt('scan_order_codincomplete')."</li>";

				}elsif($in{'localdelivery'} and !$tracking){

				    $tracking = "Local";
				    $trktype = "Local";

				}

				if (!$tracking and !$in{'localdelivery'}){
				    $va{'message'} .= "<li>".trans_txt('scan_order_unknown_tracking')."</li>";
				}

				if (!$num){
				    $va{'message'} .= "<li>".trans_txt('scan_order_noupc')."</li>";
				}

				### Se valida que no exista una transaccion activa sobre el mismo proceso
				if( !&transaction_validate($in{'cmd'}, $id_orders, 'check') ){
					my $id_transaction = &transaction_validate($in{'cmd'},  $id_orders, 'insert');
				}else{
					print "Content-type: text/html\n\n";
					print &trans_txt('transaction_duplicate');
					exit;
		        }

				### Inicializa la transaccion
				&Do_SQL("START TRANSACTION;");

				my (@id_orders_products);
				if (!$va{'message'}){

					&Do_SQL("UPDATE sl_orders_products SET Status = IF(Status = 'Reship' OR Status = 'Active','Lost','Returned') WHERE ID_orders = '$id_orders' AND Saleprice < 0;");

					## Checking for Items in Order (Not Shipped)
					my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND SalePrice >= 0 AND (Status='Active' OR Status='Exchange' OR Status='ReShip') AND (ShpDate IS NULL OR ShpDate = '' OR ShpDate='0000-00-00');");
					LINE:while ($rec = $sth->fetchrow_hashref){
						for my $i(1..$num){
							if ($rec->{'ID_products'} eq $ids{$i}[0] and ($ids{$i}[2] ne 'OK' and $ids{$i}[2] ne 'ERROR') and (!$rec->{'ShpDate'} or $rec->{'ShpDate'} eq '0000-00-00')){
								$ids{$i}[2] = 'OK';
								$ids{$i}[3] = $rec->{'ID_orders_products'};
								next LINE;
							}
						}
					}

					## Checking for Items in Order (Shipped)
					my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status IN('Active','Exchange','ReShip') AND (ShpDate IS NULL OR ShpDate = '' OR ShpDate='0000-00-00');");
					LINE:while ($rec = $sth->fetchrow_hashref){

						for my $i(1..$num){ 

							if ($rec->{'ID_products'} eq $ids{$i}[0] and  $ids{$i}[2] ne 'OK' and $rec->{'ShpDate'}){ 
								$ids{$i}[2] = 'ERROR';
								$ids{$i}[3] =  "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0]). " ".trans_txt('scan_order_upcshipped')." $rec->{'ShpDate'}</li>";
								next LINE;

							} 

						} 

					}
					## Checking for SETs/Kits
					my ($sth) = &Do_SQL("SELECT ID_sku_products,IsSet,ID_orders_products
							  FROM sl_orders_products,sl_skus 
							  WHERE sl_orders_products.ID_products=sl_skus.ID_sku_products 
							  AND ID_orders='$id_orders' AND Saleprice >= 0
							  AND sl_orders_products.Status IN('Active','Exchange','ReShip')
							  And(isnull(ShpDate) or ShpDate='' or ShpDate='0000-00-00') 
							  GROUP BY ID_orders_products,sl_orders_products.ID_products");
					while (($id,$isset,$id_prod) = $sth->fetchrow_array()){ 

						## In Batch?
						my ($sth) = &Do_SQL("SELECT ID_warehouses_batches FROM sl_warehouses_batches_orders WHERE ID_orders_products = '$id_prod' AND Status IN('In Fulfillment','Shipped');");
						$id_warehouses_batches = $sth->fetchrow();

						if ($isset eq 'Y'){ 

							my ($sth) = &Do_SQL("SELECT ID_parts,SUM(Qty) FROM sl_skus_parts WHERE ID_sku_products='$id' GROUP BY ID_parts;");
							LINE:while (my ($id_part,$qty) = $sth->fetchrow_array){ 

								if ($qty>1){

									my ($sth2) = &Do_SQL("SELECT IF(SUM(Quantity) > 0,SUM(Quantity),0) AS totshp FROM sl_orders_parts WHERE ID_orders_products ='$id_prod' AND ID_parts='$id_part';");
									my $totshp = $qty-$sth2->fetchrow;
									for my $i(1..$num){ 

										if(!$id_warehouses_batches and (!$in{'fc_dropshipp_return'} and !$in{'skip_batch'}) ) {
											$ids{$i}[2] = 'ERROR';
											$ids{$i}[3] =  "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." " .trans_txt('prod_batchabsent')."</li>";

										}elsif (($id_part+400000000) eq $ids{$i}[0] and ($ids{$i}[2] ne 'OK' and $ids{$i}[2] ne 'ERROR')){
											if ($totshp>0){
												$ids{$i}[2] = 'OK';
												$ids{$i}[3] = "SET:$id_prod,$id_part";
												--$totshp;
											}	
										} 

									}

								}else{ 

									for my $i(1..$num){ 
										if (!$id_warehouses_batches and (!$in{'fc_dropshipp_return'} and !$in{'skip_batch'}) ) {
											$ids{$i}[2] = 'ERROR';
											$ids{$i}[3] =  "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." " .trans_txt('prod_batchsent')." $id_warehouses_batches </li>";

										}elsif (($id_part+400000000)  eq $ids{$i}[0] and ($ids{$i}[2] ne 'OK' and $ids{$i}[2] ne 'ERROR')){
											my ($sth2) = &Do_SQL("SELECT ShpDate FROM sl_orders_parts WHERE ID_orders_products='$id_prod' AND ID_parts='$id_part';");
											$ShpDate = $sth2->fetchrow;
											if ($ShpDate){
												$ids{$i}[2] = 'ERROR';
												$ids{$i}[3] =  "<li>The UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." has been shipped on $ShpDate $ids{$i}[3]</li>";
												next LINE;
											}else{
												$ids{$i}[2] = 'OK';
												$ids{$i}[3] = "SET:$id_prod,$id_part";
												next LINE;
											}
										} 

									} 

								} 

							} 

						} 

					}

					for my $i(1..$num){ 
					    if ($ids{$i}[2] eq 'ERROR'){
						    $va{'message'} .=  $ids{$i}[3];
					    }elsif (!$ids{$i}[2]){
						    $va{'message'} .= "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." ".trans_txt('scan_order_upcnorder')." </li>";
					    } 
					} 
				}

				if ($id_orders > 0){ 

					#################
					#################
					# Error en la orden ?
					#################
					#################

					# my ($status) = $order_type eq 'COD' ? 'OK' : &check_ord_totals($id_orders);
					my ($status) = &check_ord_totals($id_orders);
					my ($riskorder) = &check_rman($id_orders);
					## revisar si es OK

					#################
					#################
					# Si hay error en la orden se necesita authcode
					#################
					#################

					my ($sth3)=&Do_SQL("SELECT * FROM sl_vars WHERE VName='Auth Order' AND VValue LIKE '$id_orders,%'");
					my ($rec3) = $sth3->fetchrow_hashref;
					my (@parts) = split(/,/,$rec3->{'VValue'});
					$in{'authcode'} = $parts[2];


					if (($status ne 'OK' or $riskorder ne 'OK') and $in{'authcode'}){

						my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='Authorization Code' AND RIGHT(VValue,4)='".&filter_values($in{'authcode'})."'");
						my ($idadmin,$authorization) = split(/,/,$sth->fetchrow);
						if ($idadmin > 0){
							## 	Add a Shipment Authorization Note

							&add_order_notes_by_type($id_orders,&trans_txt('order_shpauthorized'),"Low");
							&auth_logging('orders_note_added',$id_orders);
							$in{'auth_admin'}=1;
						}else{
							#############
							## Revisar Si hay numero de autorizacion para la orden $id_orders
							#############
							# my ($sth2) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName = 'Auth Order' AND RIGHT(VValue,4) = '$in{'authcode'}'");
							my ($sth2) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName = 'Auth Order' AND VValue like('$id_orders,%,$in{'authcode'}')");

							my ($idorder,$idadmin,$authorization) = split(/,/,$sth2->fetchrow,3);
							if ($idorder eq $id_orders){

								&add_order_notes_by_type($id_orders,&trans_txt('order_shpauthorized'),"Low");
								&auth_logging('orders_note_added',$id_orders);
								$in{'auth_admin'}=1;
							}else{
								$va{'message'} .= "<li>".trans_txt('payments_invalid_authcode')."</li>";
							}
						}
					}elsif ($status ne 'OK' or $riskorder ne 'OK'){
						if ($status ne 'OK'){
							$va{'message'} .= $status;
						}
						if($riskorder ne 'OK' and $riskorder ne ''){
							$riskorder =~ s/Risk/<\/li><li>Risk/g;
							$riskorder =~ s/<\/li><\/li>/<\/li>/g;
							$va{'message'} .= "<li>".trans_txt('scan_order_riskerror')."</li>$riskorder";
						}
					}	
				}

				if ($va{'message'}){

					$va{'error'} = 'ERROR';

					&Do_SQL("ROLLBACK;");

					### Log Temporal
 					my $tt = $order_type eq 'COD' ? 'cod' : 'tdc';
 					## Get ID_warehouses_batches if exists
					my ($log_id_warehouses_batches) = &warehouses_batches_by_order($id_orders);
 					my ($add_sql) = ($log_id_warehouses_batches)? ", ID_warehouses_batches = '$log_id_warehouses_batches'":"";

 					&Do_SQL("INSERT INTO sl_entershipments SET ID_orders = '$id_orders' $add_sql, Type = '$tt', Input = '".&filter_values($log_tracking)."', Output = '".&filter_values($va{'message'})."', Status = 'error', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';"); 					

				}else{

					my $this_log;
					##############################################################################################
					##############################################################################################
					##############################################################################################
					######################														####################
					######################							ESCANEO DE LA ORDEN 		####################
					######################														####################
					##############################################################################################
					##############################################################################################
					##############################################################################################

					## COD Order?
					if ($order_type eq 'COD'  and !$is_exchange){
					    ($status, $msg) = &cod_tovirtual($in{'shpdate'},$tracking,$trktype,$id_orders,$in{'id_warehouses'},$num,1,$whvirtual,%ids);

					## Regular Order
					}else{
					    ($status, $msg, $log) = &cost_inventory($in{'shpdate'},$tracking,$trktype,$id_orders,$in{'id_warehouses'},$num,1,1,1,1,%ids);
					    $this_log .= $log .qq|<br>|;
					}

					if ($status eq 'ok'){

							#### Transfer Invoice
							if ($cfg{'scan_cod_with_transfer_invoice'} and $cfg{'scan_cod_with_transfer_invoice'} == 1 and $order_type eq 'COD'  and !$is_exchange){
									&export_info_for_transfer_invoice($id_orders);
							}

							#### Acounting Movements
							my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
							($order_type, $ctype) = $sth->fetchrow();

							my @params = ($id_orders);
							my $this_keypoint = !$is_exchange ? 'order_products_scanned_'. $ctype .'_'. $order_type : 'order_products_exchange_scanned';
							&accounting_keypoints($this_keypoint, \@params );

							##########
							########## Revision ShpDate
							##########
							&order_scan_check_shpdate($id_orders);

							my $whb;
							## Updating Batches
							my ($sth) = &Do_SQL("SELECT ShpDate, ID_warehouses_batches_orders, ID_warehouses_batches
										FROM `sl_orders_products` 
										LEFT JOIN sl_warehouses_batches_orders USING(ID_orders_products) 
										WHERE `ID_orders`= '$id_orders' 
										AND sl_warehouses_batches_orders.Status = 'In Fulfillment'
										ORDER BY ID_warehouses_batches DESC;");

							while ($rec = $sth->fetchrow_hashref){

								if ($rec->{'ShpDate'} and $rec->{'ID_warehouses_batches_orders'} > 0 and $order_type eq 'COD' and !$is_exchange){
									my ($sth2) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status='In Transit', ScanDate = IF(ScanDate IS NULL OR ScanDate = '' OR ScanDate = '0000-00-00', CURDATE(), ScanDate) WHERE ID_warehouses_batches_orders=$rec->{'ID_warehouses_batches_orders'}");
								}elsif($rec->{'ShpDate'} and $rec->{'ID_warehouses_batches_orders'} > 0 and ($order_type ne 'COD' or $is_exchange) ){
									my ($sth2) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status = 'Shipped', ScanDate = IF(ScanDate IS NULL OR ScanDate = '' OR ScanDate = '0000-00-00', CURDATE(), ScanDate) WHERE ID_warehouses_batches_orders=$rec->{'ID_warehouses_batches_orders'}");
								}
								my ($sth2) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='In Transit' WHERE Status = 'Processed' AND ID_warehouses_batches = $rec->{'ID_warehouses_batches'}");
								$whb = $rec->{'ID_warehouses_batches'};

							}

							## Updating Returns
							&Do_SQL("UPDATE sl_returns SET PackingListStatus = 'Done' WHERE ID_orders = '$id_orders';");

							my ($sth) = &Do_SQL("SELECT  sl_warehouses.ID_warehouses, sl_warehouses.Name FROM sl_warehouses INNER JOIN sl_warehouses_batches USING(ID_warehouses) WHERE ID_warehouses_batches = '$whb';");
							my ($idwh,$whn) = $sth->fetchrow();

						  	## Warehouse Note

						  	&add_order_notes_by_type($id_orders,&trans_txt('order_shipped')." From Warehouse: ".&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name')." ($in{'id_warehouses'})\n".trans_txt('scan_order_assignedto').": $whn ($idwh)","Low");
							## Email Notification
							my $status_email;
							if ($cfg{'email_confirmation'} and !$is_exchange){
								$status_email = &send_email_scanconfirmation($in{'shpdate'},$tracking,$trktype,$id_orders,$num,%ids) if ($trktype  !~ /^Local/);
							}

							## SMS Notificacion
							my $status_sms;
							if ($cfg{'sms_confirmation'} and !$is_exchange){
								$status_sms = &shipping_notification($in{'shpdate'},$tracking,$trktype,$id_orders,$num,%ids) if ($trktype !~ /^Local/);
							}

							#### Pieces Scanned
							$va{'message'} .= "|1|<br><span class=\"bigerrtext\">$num ".trans_txt('scan_order_pieces')."</span><!--scannedOK--><br>";
							$va{'message'} .= "<span class=\"bigerrtext\">".trans_txt('scan_order_assignedto')." ".&load_name('sl_warehouses','ID_warehouses',$whvirtual,'Name')."</span>" if $order_type eq 'COD';

							if ($status_email eq 'ok'){
								$va{'message'} .= "<br>".trans_txt('scan_order_cemail');
							}else{
								$va{'message'} .= "<br>Email: $status_email";
							}

							if ($status_sms == 1){
								$va{'message'} .= "<br>".trans_txt('scan_order_csms');
							}

							#Aqui genera los puntos de la orden
	 						#&set_reward_points($id_orders);

	 						my $full_scan = 1; my $this_scan_status = 0; my $this_scan_str;
	 						if ($cfg{'validate_full_scan'} and $cfg{'validate_full_scan'}==1){

	 							if(!$is_exchange){
	 								($this_scan_status, $this_scan_str, $vslog)  = &validate_scan_skus($id_orders);
	 								$this_log .= qq|($this_scan_status, $this_scan_str, $vslog)  = |."validate_scan_skus($id_orders)";
	 								$this_log .= $vslog .qq|<br>|;
	 							}
	 							($res_full_scan, $prods_full_scan) = &validate_scan($id_orders);
	 							$this_log .= $res_full_scan . " - " . $prods_full_scan .qq|<br>|;
	 							if ($res_full_scan > 0) {
	 								$full_scan = 0;
	 							}

	 						}

							## End Transaction
	 						if (!$full_scan or $this_scan_status ){

	 							## Escaneo incompleto
	 							&Do_SQL("ROLLBACK; /*scan_order_incomplete*/");
								$va{'error'} = 'ERROR';
								$va{'message'} = "<br>".&trans_txt("scan_order_incomplete") . ' ' . $this_scan_str."<br>1::".$res_full_scan."::".$prods_full_scan;
	 							$this_log .= "ROLLBACK -->> ".$va{'message'}."\n";

							}else{
			 					&Do_SQL("COMMIT;");
			 					$this_log .= "COMMIT";

			 					### Se limpian los input
			 					$in{'tracking'} = '';
			 					$in{'authcode'} = '';
	 						}
        				
					}else{
						&Do_SQL("ROLLBACK;");
						$va{'error'} = 'ERROR';
						$va{'message'} .= "<br>$msg";
						$this_log .= "ROLLBACK -->> ".$va{'message'}."\n";
					}

					delete($in{'authcode'});

					### Log Temporal
 					my $tt = $order_type eq 'COD' ? 'cod' : 'tdc';
 					$status = ($va{'error'} eq 'ERROR')? 'error':$status;
 					## Get ID_warehouses_batches if exists
					my ($log_id_warehouses_batches) = &warehouses_batches_by_order($id_orders);
 					my ($add_sql) = ($log_id_warehouses_batches)? ", ID_warehouses_batches = '$log_id_warehouses_batches'":"";
 					&Do_SQL("INSERT INTO sl_entershipments SET ID_orders = '$id_orders' $add_sql,  Type = '$tt', Input = '".&filter_values($log_tracking)."', Output = '".&filter_values($va{'message'})."', Status = '$status', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
 					### DEBUG
					&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('entershipment', '$id_orders', '".$va{'message'}."\n\n".&filter_values($this_log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

				}

				### Elimina el registro de la transaccion activa de este proceso
				&transaction_validate($in{'cmd'}, $id_orders, 'delete');

			#if !$consolidated	
			}elsif ($consolidated){ 

				### Se valida que no exista una transaccion activa sobre el mismo proceso
				if( !&transaction_validate($in{'cmd'}, $id_orders, 'check') ){
					my $id_transaction = &transaction_validate($in{'cmd'},  $id_orders, 'insert');
				}else{
					print "Content-type: text/html\n\n";
					print &trans_txt('transaction_duplicate');
					exit;
		        }

				### Inicializa la transaccion
				&Do_SQL("START TRANSACTION;");

				my ($status, $msg) = &enterexportation();

				if ($status eq 'ok'){ 

					#### Acounting Movements
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
					($order_type, $ctype) = $sth->fetchrow();

					my @params = ($id_orders);
					&accounting_keypoints('order_skus_scanned_'. $ctype .'_'. $order_type, \@params);

					#### Pieces Scanned
					$va{'message'} .= "<br><span class=\"bigerrtext\">$num ".trans_txt('scan_order_pieces')."</span><!--scannedOK--><br>";

					## Warehouse Note

					&add_order_notes_by_type($id_orders,&trans_txt('order_shipped')." From Warehouse: ".&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name')." ($in{'id_warehouses'})","Low");
	 				$full_scan = 1;
					if ($cfg{'validate_full_scan'} and $cfg{'validate_full_scan'}==1){
						($res_full_scan, $prods_full_scan) = &validate_scan($id_orders);
						$this_log .= $res_full_scan . " - " . $prods_full_scan .qq|<br>\n|;
						if ($res_full_scan > 0) {
							$full_scan = 0;
						}
					}

					## End Transaction
					if (!$full_scan){
						&Do_SQL("ROLLBACK; /*scan_order_incomplete*/");
						$this_log .= "ROLLBACK";
						$va{'error'} = 'ERROR';
						$va{'message'} = "<br>".&trans_txt("scan_order_incomplete")."<br>2::".$res_full_scan."::".$prods_full_scan;
						$this_log .= "ROLLBACK -->> ".$va{'message'}."\n";
					}else{
						&Do_SQL("COMMIT;");
						$this_log .= "COMMIT";
						# &Do_SQL("ROLLBACK;"); # Debug only
						### Se limpian los input
			 			$in{'tracking'} = '';
			 			$in{'authcode'} = '';
					}
				

					### Log Temporal
	 				my $tt = 'exportation';
	 				## Get ID_warehouses_batches if exists
					my ($log_id_warehouses_batches) = &warehouses_batches_by_order($id_orders);
	 				my ($add_sql) = ($log_id_warehouses_batches)? ", ID_warehouses_batches = '$log_id_warehouses_batches'":"";
	 				&Do_SQL("INSERT INTO sl_entershipments SET ID_orders = '$id_orders' $add_sql,  Type = '$tt', Input = '".&filter_values($log_tracking)."', Output = '".&filter_values($va{'message'})."', Status = '$status', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

	 				### Elimina el registro de la transaccion activa de este proceso
					&transaction_validate($in{'cmd'}, $id_orders, 'delete');

				}else{
					&Do_SQL("ROLLBACK;");
					$va{'error'} = 'ERROR';
					$va{'message'} .= "<br>$msg";
					$this_log .= "ROLLBACK -->> ".$va{'message'}."\n";

					### Elimina el registro de la transaccion activa de este proceso
					&transaction_validate($in{'cmd'}, $id_orders, 'delete');
				}
				delete($in{'authcode'});

			}

		}
		
	}else{
		$in{'shpdate'} = &get_sql_date(0);
	}
	
	## Return to function orders_dropshipp
	if ($in{'fc_dropshipp_return'} == 1){
		return;
	}

	if ($ENV{'REQUEST_URI'} =~ /apps\/entershipment/){
		$va{'cgiurl'} = '/cgi-bin/common/apps/entershipment';
	}else{
		$va{'cgiurl'} = '/cgi-bin/mod/wms/admin';
	}
	#$in{'id_warehouses'} = &GetCookies("ck_warehouses$in{'e'}");
	$in{'id_warehouses'} = ($cfg{'id_warehouses_def'} and !$in{'id_warehouses'}) ? $cfg{'id_warehouses_def'} : $in{'id_warehouses'};
	
	if ($in{'localdelivery'}){
		$va{'skip_line_2'} = 0;
		$va{'nameenter'} = 'Enter Local Delivery';
		$va{'descriptionenter'} = '(Invoice / Product Number)';

	}else{
		$va{'skip_line_2'} = 0;
		$va{'nameenter'} = 'Enter Shipment ';
		$va{'descriptionenter'} = '(Invoice / Tracking Number / Product Number) ';
	}

	$va{'entershipment_scan_order_noupc'} = trans_txt('entershipment_scan_order_noupc');
	$va{'entershipment_scan_upc_unknown'} = trans_txt('entershipment_scan_upc_unknown');
	$va{'submit_code'} = $cfg{'submit_code'};
	

	print "Content-type: text/html\n\n";

	if (!$in{'action'}){

		if ($in{'fix'} and &check_permissions('wms_fix_scans','','')){
			print &build_page('entershipment_fix.html');
		}else{
			print &build_page('entershipment.html');
		}

	}else{
		if (!$in{'ajax'}){
			if ($in{'fix'} and &check_permissions('wms_fix_scans','','')){
				print &build_page('entershipment_fix.html');
			}else{
				print &build_page('entershipment.html');
			}
		}else{
			print $va{'message'};
		}
	}
}


sub entershipment_pos {
	my ($status,$statmsg);
	my (@carriers);
	my $duplicated = 0;
	my $consolidated = 0;
	my $sumshipp = 0;
	my $str_shp;
	my $whvirtual=0;
	my $id_warehouses_batches;
	my $log_tracking;
	my $id_orders;
	$va{'this_pos_sale'} = 1;
	$in{'shpdate'} = &get_sql_date();
	$msg = '';
	$cfg{'shipping_companies'} .= ",".join(',',&load_enum_toarray('sl_orders_products','ShpProvider'));

	if ($in{'action'}){

		if (!$in{'shpdate'} or !$in{'id_warehouses'} or (!$in{'tracking'} && !$in{'localdelivery'})){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}
		$log_tracking = $in{'tracking'};


		print "Set-Cookie: ck_warehouses$in{'e'}=$in{'id_warehouses'} ; expires=; path=/;\n";

		if($in{'id_packinglist'}){

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_packinglist='$in{'id_packinglist'}' AND ISNULL(Tracking);");
			if ($sth->fetchrow() == 0){
				$va{'message'} = &trans_txt('packinglist_updinvfld');
				++$err;
			}

		}

		if (!$err){

			my ($order_type, $ctype, $customer_status, $status, $msg, $tracking, $trktype, @id_products, %ids, $num);
			$id_orders=0;

			@ary = split(/\n|\s/,$in{'tracking'});

			##### Consolidated Shipment -- Si el envio es bulk
			if ($in{'bulk'}){ 

				LINES: for (0..$#ary){
					
					$ary[$_] =~ s/\n|\r|\s//g;
					if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){

						$id_orders = $1;
						if ($id_orders >0){

							$consolidated = 1 if &is_exportation_order($id_orders);
							$in{'tracking'} .= &get_bulk_products('orders',$id_orders) if !$consolidated;
							last LINES;

						}

					}

				}

			}

			
			if (!$consolidated){

				@ary = split(/\n/,$in{'tracking'});
				LINE: for my $i(0..$#ary){

					$ary[$i] =~ s/\n|\r//g;

					if ($ary[$i] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){

						$id_orders = $1;
						$ary[$i] = '';
						my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$id_orders' AND Status IN ('Processed','Shipped');");
						if ($sth->fetchrow==0){
							$id_orders = 0;
							$va{'message'} .= "<li>".trans_txt('scan_order_invalid_status')."</li>";
						}						

					}elsif($ary[$i]){

						if (!$tracking){

							@carriers = split(/,/, $cfg{'shipping_companies'}) if ($#carriers<0);
							for (0..$#carriers){
								if ($cfg{'shprov_'.$carriers[$_]}){
									my ($trknum) = $ary[$i];
									eval { "if ($cfg{'shprov_'.$carriers[$_]}){$tracking = $trknum; $ary[$i]=''; $trktype='$carriers[$_]'; next LINE;}"};
								}
							}

							if ($i == 1 and $ary[$i] =~ /^([A-Za-z0-9]+)/ and !$tracking){

								$tracking = $1;
								# Get shipping companies by REGEX
								if($ary[$i] =~ /\b(1Z ?[0-9A-Z]{3} ?[0-9A-Z]{3} ?[0-9A-Z]{2} ?[0-9A-Z]{4} ?[0-9A-Z]{3} ?[0-9A-Z]|[\dT]\d\d\d ?\d\d\d\d ?\d\d\d)\b/i){
									$trktype = 'UPS';
								}elsif($ary[$i] =~ /(\b\d{34}\b)/){
									$trktype = 'FEDEX';
								}elsif($ary[$i] =~ /(\b\d{22}\b)/){
									$trktype = 'ESTAFETA';
								}elsif($ary[$i] =~ /DRIVER/i){
									$trktype = 'DRIVER';
								}elsif($ary[$i] =~ /(\b\d{9}\b)/i){
									$trktype = 'SERVIENTREGA';
								}

								if ($cfg{'shipping_companies'} =~ /$trktype/i){
									$ary[$i] = '';
									next LINE;
								}else{
									$tracking = '';
									$trktype = '';
								}
							}elsif(!$tracking){
								($trktype,$tracking) = split(/\@/, $ary[$i]);
								if ($cfg{'shipping_companies'} =~ /$trktype/i){
									$ary[$i] = '';
									next LINE;
								}else{
									$tracking = '';
									$trktype = '';
								}
							}
						}
						my ($sth) = &Do_SQL("SELECT ID_sku_products, IsSet FROM sl_skus WHERE UPC='$ary[$i]';");
						($id, $isset) = $sth->fetchrow_array;
						++$num;
						if ($id >0 and $isset ne 'Y'){
							my ($sthinv,$recinv);
							if (!$cfg{'allow_inv_negatives'}){
								$sthinv=&Do_SQL("SELECT IF(SUM(Quantity)>0,SUM(Quantity),0) AS Quantity FROM sl_warehouses_location WHERE ID_products = '$id' AND ID_warehouses = '$in{'id_warehouses'}' ");
								$recinv=$sthinv->fetchrow;
								if (!$recinv){
									$va{'message'} .= "<li>" . trans_txt('scan_no_stock') .  $ary[$i] ." ". trans_txt('warehouse') . ": $in{'id_warehouses'}</li>";
								}
							}
							push(@id_products,$id);
							push(@upcs,$ary[$i]);
							$ids{$num}[0] = $id;
							$ids{$num}[1] = $ary[$i];
						}elsif ($id >0 and $isset eq 'Y'){
							$ids{$num}[0] = '--';
							$ids{$num}[1] = $ary[$i];
							$ids{$num}[2] = 'ERROR';
							$ids{$num}[3] = "<li>UPC $ary[$i] ". trans_txt('upc_kit') . "(". &format_sltvid($id) .") </li>";
						}else{
							$ids{$num}[0] = '--';
							$ids{$num}[1] = $ary[$i];
							$ids{$num}[2] = 'ERROR';
							$ids{$num}[3] = "<li>". trans_txt('scan_upc_unknown')." $ary[$i]</li>";
						}
						#$sumshipp += substr($ary[$i],-5);
						$str_shp .= "$sumshipp + ".($id - 400000000)."\n";
						$sumshipp += ($id - 400000000);
					}
				}

				if (!$id_orders){
				    $va{'message'} .= "<li>". trans_txt('scan_order_unknown')."</li>";
				}else{

					my ($sth) = &Do_SQL("SELECT Ptype,sl_customers.Status FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
					($order_type,$customer_status) = $sth->fetchrow();

					($customer_status ne 'Active') and ($va{'message'} .= "<li>". trans_txt('scan_order_customer_' . lc($customer_status))."</li>");

				}


				## Validacion de remesa unica
				$sql = "SELECT COUNT(distinct sl_warehouses_batches_orders.ID_warehouses_batches)inbatches
						FROM sl_warehouses_batches_orders 
							INNER JOIN sl_orders_products on sl_warehouses_batches_orders.ID_orders_products=sl_orders_products.ID_orders_products
						WHERE sl_orders_products.Status NOT IN ('Inactive')
							AND sl_orders_products.ID_orders='$id_orders'
							AND sl_warehouses_batches_orders.Status='In Fulfillment'
						ORDER BY sl_warehouses_batches_orders.ID_warehouses_batches desc, sl_warehouses_batches_orders.ID_orders_products asc";
				$sth_wbo = &Do_SQL($sql);
				my($unique_batch) = $sth_wbo->fetchrow();
				
				if ($unique_batch > 1){
				    $va{'message'} .= "<li>". trans_txt('scan_order_wbo_fail')."</li>";
				}

				## Is New COD Shipping OR Exchange?
				my $is_exchange =  &delivery_status_order($id_orders);

				## Local COD /Local Delivery?
				## Se integra opcion para trabajar COD como venta normal
				if ($order_type eq 'COD' and !$cfg{'cod_normal_sale'} and !$is_exchange and !$va{'message'}){ 

				    $whvirtual = &load_name('sl_orders','ID_orders',$id_orders,'ID_warehouses');
				    $sthwv = &Do_SQL("SELECT ID_warehouses FROM sl_orders_datecod WHERE ID_orders = '$id_orders' AND Status = 'Active';");
				    my ($whvirtual2) = $sthwv->fetchrow();
				    (!$whvirtual) and ($whvirtual = $whvirtual2);

				    if ($id_orders and !$whvirtual){
					   $va{'message'} .= "<li>".trans_txt('scan_order_nocoverage')."</li>";
				    }

				    my $sumorder = &ordercomplete($id_orders);
				    #&cgierr("$sumorder != $sumshipp");
				    if ($sumorder != $sumshipp){
					    $va{'message'} .= "<li>".trans_txt('scan_order_codincomplete')."</li>";
				    }

				    if(!$tracking or !$trktype){
						$tracking = "Local COD";
						$trktype  = "Local COD";
				    } 

				}elsif($in{'localdelivery'} and !$tracking){
				    $tracking = "Local";
				    $trktype = "Local";
				}

				if (!$tracking and !$in{'localdelivery'}){
				    $va{'message'} .= "<li>".trans_txt('scan_order_unknown_tracking')."</li>";
				}

				if (!$num){
				    $va{'message'} .= "<li>".trans_txt('scan_order_noupc')."</li>";
				}

				### Se valida que no exista una transaccion activa sobre el mismo proceso
				

				### Inicializa la transaccion para escaneos NO consolidados
				# &Do_SQL("START TRANSACTION;");

				my (@id_orders_products);
				if (!$va{'message'}){

					&Do_SQL("UPDATE sl_orders_products SET Status = IF(Status = 'Reship' OR Status = 'Active','Lost','Returned') WHERE ID_orders = '$id_orders' AND Saleprice < 0;");

					## Checking for Items in Order (Not Shipped)
					my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND SalePrice >= 0 AND (Status='Active' OR Status='Exchange' OR Status='ReShip') AND (ShpDate IS NULL OR ShpDate = '' OR ShpDate='0000-00-00');");
					LINE:while ($rec = $sth->fetchrow_hashref){
						for my $i(1..$num){
							if ($rec->{'ID_products'} eq $ids{$i}[0] and ($ids{$i}[2] ne 'OK' and $ids{$i}[2] ne 'ERROR') and (!$rec->{'ShpDate'} or $rec->{'ShpDate'} eq '0000-00-00')){
								$ids{$i}[2] = 'OK';
								$ids{$i}[3] = $rec->{'ID_orders_products'};
								next LINE;
							}
						}
					}

					## Checking for Items in Order (Shipped)
					my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders='$id_orders' AND Status IN('Active','Exchange','ReShip') AND (ShpDate IS NULL OR ShpDate = '' OR ShpDate='0000-00-00');");
					LINE:while ($rec = $sth->fetchrow_hashref){

						for my $i(1..$num){ 

							if ($rec->{'ID_products'} eq $ids{$i}[0] and  $ids{$i}[2] ne 'OK' and $rec->{'ShpDate'}){ 
								$ids{$i}[2] = 'ERROR';
								$ids{$i}[3] =  "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0]). " ".trans_txt('scan_order_upcshipped')." $rec->{'ShpDate'}</li>";
								next LINE;

							} 

						} 

					}
					## Checking for SETs/Kits
					my ($sth) = &Do_SQL("SELECT ID_sku_products,IsSet,ID_orders_products
							  FROM sl_orders_products,sl_skus 
							  WHERE sl_orders_products.ID_products=sl_skus.ID_sku_products 
							  AND ID_orders='$id_orders' AND Saleprice >= 0
							  AND sl_orders_products.Status IN('Active','Exchange','ReShip')
							  And(isnull(ShpDate) or ShpDate='' or ShpDate='0000-00-00') 
							  GROUP BY ID_orders_products,sl_orders_products.ID_products");
					while (($id,$isset,$id_prod) = $sth->fetchrow_array()){ 

						## In Batch?
						my ($sth) = &Do_SQL("SELECT ID_warehouses_batches FROM sl_warehouses_batches_orders WHERE ID_orders_products = '$id_prod' AND Status IN('In Fulfillment','Shipped');");
						$id_warehouses_batches = $sth->fetchrow();

						if ($isset eq 'Y'){ 

							my ($sth) = &Do_SQL("SELECT ID_parts,SUM(Qty) FROM sl_skus_parts WHERE ID_sku_products='$id' GROUP BY ID_parts;");
							LINE:while (my ($id_part,$qty) = $sth->fetchrow_array){ 

								if ($qty>1){

									my ($sth2) = &Do_SQL("SELECT IF(SUM(Quantity) > 0,SUM(Quantity),0) AS totshp FROM sl_orders_parts WHERE ID_orders_products ='$id_prod' AND ID_parts='$id_part';");
									my $totshp = $qty-$sth2->fetchrow;
									for my $i(1..$num){ 

										if(!$id_warehouses_batches and (!$in{'fc_dropshipp_return'} and !$in{'skip_batch'}) ) {
											$ids{$i}[2] = 'ERROR';
											$ids{$i}[3] =  "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." " .trans_txt('prod_batchabsent')."</li>";

										}elsif (($id_part+400000000) eq $ids{$i}[0] and ($ids{$i}[2] ne 'OK' and $ids{$i}[2] ne 'ERROR')){
											if ($totshp>0){
												$ids{$i}[2] = 'OK';
												$ids{$i}[3] = "SET:$id_prod,$id_part";
												--$totshp;
											}	
										} 

									}

								}else{ 

									for my $i(1..$num){ 
										if (!$id_warehouses_batches and (!$in{'fc_dropshipp_return'} and !$in{'skip_batch'}) ) {
											$ids{$i}[2] = 'ERROR';
											$ids{$i}[3] =  "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." " .trans_txt('prod_batchsent')." $id_warehouses_batches </li>";

										}elsif (($id_part+400000000)  eq $ids{$i}[0] and ($ids{$i}[2] ne 'OK' and $ids{$i}[2] ne 'ERROR')){
											my ($sth2) = &Do_SQL("SELECT ShpDate FROM sl_orders_parts WHERE ID_orders_products='$id_prod' AND ID_parts='$id_part';");
											$ShpDate = $sth2->fetchrow;
											if ($ShpDate){
												$ids{$i}[2] = 'ERROR';
												$ids{$i}[3] =  "<li>The UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." has been shipped on $ShpDate $ids{$i}[3]</li>";
												next LINE;
											}else{
												$ids{$i}[2] = 'OK';
												$ids{$i}[3] = "SET:$id_prod,$id_part";
												next LINE;
											}
										} 

									} 

								} 

							} 

						} 

					}

					for my $i(1..$num){ 
					    if ($ids{$i}[2] eq 'ERROR'){
						    $va{'message'} .=  $ids{$i}[3];
					    }elsif (!$ids{$i}[2]){
						    $va{'message'} .= "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." ".trans_txt('scan_order_upcnorder')." </li>";
					    } 
					} 
				}

				if ($id_orders > 0){ 

					#################
					#################
					# Error en la orden ?
					#################
					#################

					# my ($status) = $order_type eq 'COD' ? 'OK' : &check_ord_totals($id_orders);
					my ($status) = &check_ord_totals($id_orders);
					my ($riskorder) = &check_rman($id_orders);
					## revisar si es OK

					#################
					#################
					# Si hay error en la orden se necesita authcode
					#################
					#################

					my ($sth3)=&Do_SQL("SELECT * FROM sl_vars WHERE VName='Auth Order' AND VValue LIKE '$id_orders,%'");
					my ($rec3) = $sth3->fetchrow_hashref;
					my (@parts) = split(/,/,$rec3->{'VValue'});
					$in{'authcode'} = $parts[2];


					if (($status ne 'OK' or $riskorder ne 'OK') and $in{'authcode'}){

						my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='Authorization Code' AND RIGHT(VValue,4)='".&filter_values($in{'authcode'})."'");
						my ($idadmin,$authorization) = split(/,/,$sth->fetchrow);
						if ($idadmin > 0){
							## 	Add a Shipment Authorization Note
							my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_shpauthorized')."',Type='Low',Date=Curdate(),Time=NOW(),ID_admin_users='$idadmin', ID_orders='$id_orders';");
							&auth_logging('orders_note_added',$id_orders);
							$in{'auth_admin'}=1;
						}else{
							#############
							## Revisar Si hay numero de autorizacion para la orden $id_orders
							#############
							# my ($sth2) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName = 'Auth Order' AND RIGHT(VValue,4) = '$in{'authcode'}'");
							my ($sth2) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName = 'Auth Order' AND VValue like('$id_orders,%,$in{'authcode'}')");

							my ($idorder,$idadmin,$authorization) = split(/,/,$sth2->fetchrow,3);
							if ($idorder eq $id_orders){
								my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_shpauthorized')."',Type='Low',Date=Curdate(),Time=NOW(),ID_admin_users='$idadmin', ID_orders='$id_orders';");
								&auth_logging('orders_note_added',$id_orders);
								$in{'auth_admin'}=1;
							}else{
								$va{'message'} .= "<li>".trans_txt('payments_invalid_authcode')."</li>";
							}
						}
					}elsif ($status ne 'OK' or $riskorder ne 'OK'){
						if ($status ne 'OK'){
							$va{'message'} .= $status;
						}
						if($riskorder ne 'OK' and $riskorder ne ''){
							$riskorder =~ s/Risk/<\/li><li>Risk/g;
							$riskorder =~ s/<\/li><\/li>/<\/li>/g;
							$va{'message'} .= "<li>".trans_txt('scan_order_riskerror')."</li>$riskorder";
						}
					}	
				}


				if ($va{'message'}){

					$va{'error'} = 'ERROR';

					### Log Temporal
 					my $tt = $order_type eq 'COD' ? 'cod' : 'tdc';
 					## Get ID_warehouses_batches if exists
					my ($log_id_warehouses_batches) = &warehouses_batches_by_order($id_orders);
 					my ($add_sql) = ($log_id_warehouses_batches)? ", ID_warehouses_batches = '$log_id_warehouses_batches'":"";
 					&Do_SQL("INSERT INTO sl_entershipments SET ID_orders = '$id_orders' $add_sql, Type = '$tt', Input = '".&filter_values($log_tracking)."', Output = '".&filter_values($va{'message'})."', Status = 'error', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

				}else{

					##############################################################################################
					##############################################################################################
					##############################################################################################
					######################														####################
					######################							ESCANEO DE LA ORDEN 		####################
					######################														####################
					##############################################################################################
					##############################################################################################
					##############################################################################################

					my ($validate_cod_sale, $cod_sale_msg, $cod_sale_log);
					if ( lc($order_type) eq 'cod' and !$cfg{'cod_normal_sale'} and !$is_exchange){

						###########
						########### COD In Transit
						###########
						
					    ($status, $msg) = &cod_tovirtual($in{'shpdate'},$tracking,$trktype,$id_orders,$in{'id_warehouses'},$num,1,$whvirtual,%ids);
						## 2) Venta COD - Si existe parametro de configuracion (Se valida en la funcion)
					    ($validate_cod_sale, $cod_sale_msg, $cod_sale_log) = &set_cod_automatic_sale($id_orders) if $status eq 'ok';

					}else{

						###########
						########### TDC/Referenced Deposit/ + COD As Regular Sale
						###########
						
						my $check_payment = ( lc($order_type) eq 'cod' and $cfg{'cod_normal_sale'}) ? 0 : 1;
					    ($status, $msg, $log) = &cost_inventory($in{'shpdate'},$tracking,$trktype,$id_orders,$in{'id_warehouses'},$num,1,$check_payment,1,1,%ids);
					}


					if ($status eq 'ok'){

						#########################
						#########################
						#### Acounting Movements
						#########################
						#########################
						
						## 1) Venta TDC/C.F.
						my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
						($order_type, $ctype) = $sth->fetchrow();

						my @params = ($id_orders);
						my $this_keypoint = !$is_exchange ? 'order_products_scanned_'. $ctype .'_'. $order_type : 'order_products_exchange_scanned';
						&accounting_keypoints($this_keypoint, \@params );


						##########
						########## Revision ShpDate
						##########
						&order_scan_check_shpdate($id_orders);

						my $whb;
						## Updating Batches
						my ($sth) = &Do_SQL("SELECT ShpDate, ID_warehouses_batches_orders, ID_warehouses_batches
									FROM `sl_orders_products` 
									LEFT JOIN sl_warehouses_batches_orders USING(ID_orders_products) 
									WHERE `ID_orders`= '$id_orders' 
									AND sl_warehouses_batches_orders.Status = 'In Fulfillment'
									ORDER BY ID_warehouses_batches DESC;");

						while ($rec = $sth->fetchrow_hashref){

							if ($rec->{'ShpDate'} and $rec->{'ID_warehouses_batches_orders'} > 0 and $order_type eq 'COD' and !$is_exchange){
								my ($sth2) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status='In Transit', ScanDate = IF(ScanDate IS NULL OR ScanDate = '' OR ScanDate = '0000-00-00', CURDATE(), ScanDate) WHERE ID_warehouses_batches_orders=$rec->{'ID_warehouses_batches_orders'}");
							}elsif($rec->{'ShpDate'} and $rec->{'ID_warehouses_batches_orders'} > 0 and ($order_type ne 'COD' or $is_exchange) ){
								my ($sth2) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status = 'Shipped', ScanDate = IF(ScanDate IS NULL OR ScanDate = '' OR ScanDate = '0000-00-00', CURDATE(), ScanDate) WHERE ID_warehouses_batches_orders=$rec->{'ID_warehouses_batches_orders'}");
							}
							my ($sth2) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='In Transit' WHERE Status = 'Processed' AND ID_warehouses_batches = $rec->{'ID_warehouses_batches'}");
							$whb = $rec->{'ID_warehouses_batches'};

						}

						## Updating Returns
						&Do_SQL("UPDATE sl_returns SET PackingListStatus = 'Done' WHERE ID_orders = '". $id_orders ."';");

						my ($sth) = &Do_SQL("SELECT  sl_warehouses.ID_warehouses, sl_warehouses.Name FROM sl_warehouses INNER JOIN sl_warehouses_batches USING(ID_warehouses) WHERE ID_warehouses_batches = '$whb';");
						my ($idwh,$whn) = $sth->fetchrow();

					  	## Warehouse Note
					  	my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_shipped')." From Warehouse: ".&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name')." ($in{'id_warehouses'})\n".trans_txt('scan_order_assignedto').": $whn ($idwh)',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders='$id_orders';");

						## Email Notification
						my $status_email;
						if ($cfg{'email_confirmation'} and !$is_exchange){
							$status_email = &send_email_scanconfirmation($in{'shpdate'},$tracking,$trktype,$id_orders,$num,%ids) if ($trktype  !~ /^Local/);
						}

						## SMS Notificacion
						my $status_sms;
						if ($cfg{'sms_confirmation'} and !$is_exchange){
							$status_sms = &shipping_notification($in{'shpdate'},$tracking,$trktype,$id_orders,$num,%ids) if ($trktype !~ /^Local/);
						}

						#### Pieces Scanned
						$va{'message'} .= "|1|<br><span class=\"bigerrtext\">$num ".trans_txt('scan_order_pieces')."</span><!--scannedOK--><br>";
						$va{'message'} .= "<span class=\"bigerrtext\">".trans_txt('scan_order_assignedto')." ".&load_name('sl_warehouses','ID_warehouses',$whvirtual,'Name')."</span>" if ( lc($order_type) eq 'cod' and !$cfg{'cod_normal_sale'} ) ;

						if ($status_email eq 'ok'){
							$va{'message'} .= "<br>".trans_txt('scan_order_cemail');
						}else{
							$va{'message'} .= "<br>Email: $status_email";
						}

						if ($status_sms == 1){
							$va{'message'} .= "<br>".trans_txt('scan_order_csms');
						}

						#Aqui genera los puntos de la orden
 						#&set_reward_points($id_orders);
 						$full_scan = 1;
 						if ($cfg{'validate_full_scan'} and $cfg{'validate_full_scan'}==1){
 							($res_full_scan, $prods_full_scan) = &validate_scan($id_orders);
 							if ($res_full_scan > 0) {
 								$full_scan = 0;
 							}
 						}

						## End Transaction
 						if (!$full_scan){

 							## Escaneo incompleto
 							&Do_SQL("ROLLBACK;");
							$va{'error'} = 'ERROR';
							$va{'message'} = "<br>".&trans_txt("scan_order_incomplete")."<br>3::".$res_full_scan."::".$prods_full_scan;

						}elsif( lc($order_type) eq 'cod' and !$is_exchange and !$cfg{'cod_normal_sale'} and !$validate_cod_sale){

							## Venta de COD no se completo
							&Do_SQL("ROLLBACK;");
							$va{'error'} = 'ERROR';
							$va{'message'} = "<br>".&trans_txt("scan_order_incomplete") . "<br>" . $cod_sale_msg;

 						}else{

			 				&Do_SQL("COMMIT;");
							# &Do_SQL("ROLLBACK;"); # Debug only

 						}


					}else{
						&Do_SQL("ROLLBACK;");
						$va{'error'} = 'ERROR';
						$va{'message'} .= "<br>$msg";
					}
					delete($in{'authcode'});

					### Log Temporal
 					my $tt = $order_type eq 'COD' ? 'cod' : 'tdc';
 					$status = ($va{'error'} eq 'ERROR')? 'error':$status;
 					## Get ID_warehouses_batches if exists
					my ($log_id_warehouses_batches) = &warehouses_batches_by_order($id_orders);
 					my ($add_sql) = ($log_id_warehouses_batches)? ", ID_warehouses_batches = '$log_id_warehouses_batches'":"";
 					&Do_SQL("INSERT INTO sl_entershipments SET ID_orders = '$id_orders' $add_sql,  Type = '$tt', Input = '".&filter_values($log_tracking)."', Output = '".&filter_values($va{'message'})."', Status = '$status', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

				}

			#if !$consolidated	
			}elsif ($consolidated){ 

				my ($status, $msg) = &enterexportation();
				if ($status eq 'ok'){ 
					#### Acounting Movements
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
					($order_type, $ctype) = $sth->fetchrow();

					my @params = ($id_orders);
					&accounting_keypoints('order_skus_scanned_'. $ctype .'_'. $order_type, \@params);

					#### Pieces Scanned
					$va{'message'} .= "<br><span class=\"bigerrtext\">$num ".trans_txt('scan_order_pieces')."</span><!--scannedOK--><br>";

					## Warehouse Note
					my ($sth) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_shipped')." From Warehouse: ".&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name')." ($in{'id_warehouses'}) ',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders='$id_orders';");

	 				$full_scan = 1;
					if ($cfg{'validate_full_scan'} and $cfg{'validate_full_scan'}==1){
						($res_full_scan, $prods_full_scan) = &validate_scan($id_orders);
						if ($res_full_scan > 0) {
							$full_scan = 0;
						}
					}

					## End Transaction
					if (!$full_scan){
						$va{'error'} = 'ERROR';
						$va{'message'} = "<br>".&trans_txt("scan_order_incomplete")."<br>4::".$res_full_scan."::".$prods_full_scan;
					}else{

						# &Do_SQL("ROLLBACK;"); # Debug only

					}

					### Log Temporal
	 				my $tt = 'exportation';
	 				## Get ID_warehouses_batches if exists
					my ($log_id_warehouses_batches) = &warehouses_batches_by_order($id_orders);
	 				my ($add_sql) = ($log_id_warehouses_batches)? ", ID_warehouses_batches = '$log_id_warehouses_batches'":"";
	 				&Do_SQL("INSERT INTO sl_entershipments SET ID_orders = '$id_orders' $add_sql,  Type = '$tt', Input = '".&filter_values($log_tracking)."', Output = '".&filter_values($va{'message'})."', Status = '$status', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

				}else{
					
					$va{'error'} = 'ERROR';
					$va{'message'} .= "<br>$msg";
				}
				delete($in{'authcode'});

			}
		}

	}else{
		$in{'shpdate'} = &get_sql_date(0);
	}

	delete($va{'this_pos_sale'});
	if($va{'error'} ne ''){
		print $msg;
		print $va{'message'};
		print $va{'error'};
		return 0;
	}
	if($va{'message'} ne ''){
		print 'HOLA';
		return 1;
	}

}



sub enterexportation{
#-----------------------------------------
# Created on: 08/11/09  12:21:36 By  Roberto Barcenas
# Forms Involved: 
# Description : Funcion que se encargará de sacar las exportaciones
# Parameters :
# Last Modified by RB on 07/03/2013 12:00:00 PM : Se agrega validacion para Status Active de cliente 	

	my(@ary,$message,$id_orders,$tracking,$trktype,%ids,$num,$st,$msg,$customer_status);
	$st = 'error';
	my $total_items=0;
		@ary = split(/\n/,$in{'tracking'});
		LINE: for my $i(0..$#ary){
			$ary[$i] =~ s/\n|\r//g;
			if ($ary[$i] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){
				$id_orders = $1;
				$ary[$i] = '';
				my ($sth) = &Do_SQL("SELECT IF(Status ='Processed' AND Ptype != 'COD',1,0)AS OrderStatus  FROM sl_orders WHERE ID_orders='$id_orders';");
				if ($sth->fetchrow==0){
					$message .= "<li>".trans_txt('scan_order_notws')."</li>";
				}
			}elsif(!$tracking){
				@carriers = split(/,/, $cfg{'shipping_companies'}) if ($#carriers<0);
				for (0..$#carriers){
					if ($cfg{'shprov_'.$carriers[$i]}){
						my ($trknum) = $ary[$i];
						eval { "if ($cfg{'shprov_'.$carriers[$i]}){$tracking = $trknum; $ary[$i]=''; $trktype='$carriers[$i]'; next LINE;}"};
					}
				}
				if ($ary[$i] =~ /^([A-Za-z]+)-([A-Za-z0-9]+)/ and !$tracking){
					$tracking = $2;
					$trktype = $1;
					if ($cfg{'shipping_companies'} =~ /$trktype/i){
						$ary[$i] = '';
						next LINE;
					}else{
						$tracking = '';
						$trktype = '';
					}
				}elsif(!$tracking){
					($trktype,$tracking) = split(/\@/, $ary[$i]);
					if ($cfg{'shipping_companies'} =~ /$trktype/i){
						$ary[$i] = '';
						next LINE;
					}else{
						$tracking = '';
						$trktype = '';
					}
				}
			}
		}
		my $bol_msg;
		if(!$in{'fc_dropshipp_return'}  and !$in{'skip_batch'}) {

			my ($sth_wh) = &Do_SQL("SELECT IF(sl_warehouses_batches.Status IS NULL,'ok',sl_warehouses_batches.Status)AS warning_batch,
									ID_warehouses_batches
									FROM sl_orders_products
									LEFT JOIN sl_warehouses_batches_orders
									USING(ID_orders_products)
									LEFT JOIN sl_warehouses_batches
									USING(ID_warehouses_batches)
									WHERE ID_orders = '$id_orders'
									GROUP BY ID_orders
									ORDER BY ID_orders;");

			my ($status_wh, $id_batch) = $sth_wh->fetchrow();
			$bol_msg = 1 if $status_wh eq 'Sent';
		}

		if($bol_msg){
			$message .= "<li>". trans_txt('order_batchsent')." $id_batch</li>";
		}elsif (!$id_orders){
			$err++;
			$message .= "<li>".trans_txt('scan_order_unknown')."</li>";
		}

		if($in{'localdelivery'}){
			$tracking = "Local";
			$trktype = "Local";				
		}

		if (!$tracking){
			$err++;
			$message .= "<li>".trans_txt('scan_order_unknown_tracking')."</li>";
		}

		my ($sth) = &Do_SQL("SELECT sl_customers.Status FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
		$customer_status = $sth->fetchrow();
		if($customer_status ne 'Active') {
			$err++;
			$message .= "<li>". trans_txt('scan_order_customer_' . lc($customer_status))."</li>";
		}


		if(!$err) {

			### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
			my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
			my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

			### Escanear orden del location Pack?
			my $mod_pack = $in{'scan_from_pack'} ? " AND UPPER(Location) = 'PACK' " : '';

			my ($sth) = &Do_SQL("SELECT ID_orders_products,Related_ID_products,Quantity,ShpDate FROM sl_orders_products WHERE ID_orders = $id_orders AND LEFT(Related_ID_products,1) != '6' AND Status='Active';");
			while(my($id_orders_products,$id,$qty,$shpDate) = $sth->fetchrow()){
				++$num;	
				if(!$cfg{'allow_inv_negatives'}){
					$sthinv=&Do_SQL("SELECT IF(SUM(Quantity)>0,SUM(Quantity),0)AS Stock, IF(SUM(Quantity) < $qty,0,1)AS ToSend FROM sl_warehouses_location WHERE ID_products = '$id' AND ID_warehouses = '$in{'id_warehouses'}' $mod_pack;");
					my($stock,$recinv)=$sthinv->fetchrow();
					if($stock == 0 or !$recinv){
						$message .= "<li>".trans_txt('scan_no_stock').":$id ($stock < $qty) ".trans_txt('warehouse')." $in{'id_warehouses'}</li>";
						&auth_logging('consolidated_order_no_stock',$id_orders);
					}
				}

				if($shpDate and $shpDate ne '0000-00-00'){
					$message .= "<li>$id ".trans_txt('scan_order_upcshipped')." $shpDate</li>";
					&auth_logging('product_already_sent',$id_orders);
				}
				$ids{$num}[0] = $id;
				$ids{$num}[1] = $qty;
				$ids{$num}[2] = $id_orders_products;
				$total_items+=$qty;
			}
		}

		if ($message){
			$msg = $message;

			&add_order_notes_by_type($id_orders,"Consolidated Order Failed. Order Not Sent\n$msg","Low");
		}else{
			($st,$msg) = &cost_inventory($in{'shpdate'},$tracking,$trktype,$id_orders,$in{'id_warehouses'},$num,0,1,2,1,%ids);
			if($st eq 'ok'){
				if($status_wh ne 'ok' and !$in{'fc_dropshipp_return'}){
					## La orden estaba en un batch?
					my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches_orders
					INNER JOIN sl_orders_products ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
					SET sl_warehouses_batches_orders.Status = 'Cancelled'
					WHERE sl_orders_products.ID_orders = $id_orders
					AND sl_warehouses_batches_orders.Status <> 'Shipped';");
				}
			}

		}

	return ($st, $msg)
}

#############################################################################
#############################################################################
#   Function: 
#
#       Es: Realiza el proceso de salida de inventario del almacen.       
#		En:  
#
#
#    Created on:  06/03/08
#
#    Author: _Carlos Haas_
#
#    Modifications:
#
# 		Last Modified RB: 06/18/2009 17:24:56 -- Se manda a ejecutar el movimiento de salida de inventario para el modulo de accountingd
# 		Last Modified RB: 07/23/2009 11:24:30 -- Se reparo el query que busca que se haya hecho por lo menos un payment para permitir el escaneo.
# 		Last Modified RB: 08/12/2009 13:41:48 -- Se separa la ejecucion del cost_inventory para exportaciones enviando la variable $doinventory=2. La ejecucion de este proceso al final de la funcion
# 		Last Modified RB: 09/21/2009 17:47:15 -- userGroup(1=Developers,8=Finance) validos para sacar mercancia sin pago capturado
# 		Last Modified RB: 09/22/2009 12:55:44 -- Se separa el chequeo de ordertotals del de pagos capturados y solamente se descarta el authcode cuando se ha completado el escaneo de la orden.
# 		Last Modified RB: 08/04/2010 17:55:44 -- Se agrega captura para PayPal
# 		Last Modified RB: 04/22/2013 11:00:00 -- Se agrega orden de escaneo por configuracion FIFO | LIFO
# 		Last Modified RB: 04/22/2013 11:00:00 -- Se agrega variable $in{'scan_from_pack'} para sacar inventario solamente desde el location Code 'pack'
#		Last Modified by Fabian Cañaveral on 17/12/2015 -- Se cambia la forma de procesar lineas del traking, se procesa ahora por producto, se elimino el llamado a ls_locations_trans por desuso ahora se usa sl_skus_trans, se elimino el calculo del costo promedio del proceso debido a que en salidas el costo promedio no es necesario calcularlo.
#		
#   Parameters:
#
#       - gvshpdate: Fecha de envio orden  
#       - gvtracking: Tracking Number  
#		- gvtrktype: Mesajeria
#		- gvid_orders: Listado de productos
#		- id_warehouses: ID Warehouses
#		- gvnum:
#		- doflexi:
#		- domiddle:
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub cost_inventory {
#############################################################################
#############################################################################
	my ($shpdate, $tracking, $trktype, $id_orders, $id_warehouses, $num, $doflexi, $domiddle, $doinventory, $domessag, %ids)=@_;

	my ($st, $message);
	$st = 'error';
	$tcost = 0;
	my $log2 = '';
	my $qty = 1;

	if($domiddle==1){

		my ($status, $statmsg, $codemsg);
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders=$id_orders AND (ShpDate IS NOT NULL AND ShpDate<>'0000-00-00') AND Status='Active';");
		if ($sth->fetchrow == 0){
			my ($sth) = &Do_SQL("SELECT ID_orders_payments,PmtField3 FROM sl_orders_payments WHERE ID_orders=$id_orders AND Status<>'Cancelled' AND AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000' AND (CapDate IS NULL OR CapDate='0000-00-00') ORDER BY Paymentdate ASC LIMIT 1");	
			my($idp,$ptype) = $sth->fetchrow();

			if ($idp){

				use Cwd;
				my ($dir) = getcwd;
				my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
				my $paym_dir = $b_cgibin.'cgi-bin/common/apps/';


				## ( PayPal | Google Checkout | Cybersource ) Payment
				if ($ptype !~ /paypal|google/i and $ptype ne ''){
					require ($paym_dir . 'cybersubs.cgi');
					($status,$statmsg,$codemsg) = &sltvcyb_capture($id_orders,$idp);
				}elsif($ptype =~ /paypal/i){
					require ($paym_dir . 'paypalsubs.cgi');
					require ($paym_dir . 'cybersubs.cgi');
					($status,$statmsg,$codemsg) = &capture_paypal($id_orders,$idp);
				}elsif($ptype =~ /google/i){
					require ($paym_dir . 'googlesubs.cgi');
					($status,$statmsg,$codemsg) = &google_capture($id_orders,$idp);
				}

			}else{
				$status = 'OK';
			}

			$message .= " $status-".$statmsg."- " if($domessage);
			#$vamsg.= " $status-".$statmsg."- ";
			if ($status ne 'OK'){
				my ($sth) = &Do_SQL("INSERT INTO cleanup_temp SET ID_orders='$id_orders',Message='Error in Capture : $statmsg'");	
				$message .= trans_txt('payments_check_paylogs') . " ($status)";
			}
		}else{
			my ($sth) = &Do_SQL("INSERT INTO cleanup_temp SET ID_orders='$id_orders',Message='Order Shipped but Not Captured because Items Already been Shipped'");	
		}

		################################################
		################################################
		# Verifica si tiene al menos un pago capturado.
		################################################
		################################################

		## We can skip the minimum amount verification
		## with wms_scan_skip_minimum_payment = 1 
		if(!$cfg{'wms_scan_skip_minimum_payment'}) {

			$sth=&Do_SQL("SELECT 
								IF(
									SUM(
										IF(
											Captured='Yes' and CapDate!='0000-00-00' AND Amount > ". $cfg{'postdatedfesprice'} ."
											,1,0
											)
										) > 0
									,SUM(
										IF(
											Captured='Yes' and CapDate!='0000-00-00' AND Amount > ". $cfg{'postdatedfesprice'} ."
											,1,0
											)
									),0
								)  as Payments
								, IF(NOT ISNULL(SUM(IF(NOT ISNULL(Amount),Amount,0))),sum(if(not isnull(Amount),Amount,0)),0)AS SumPayments
								, SUM(IF(Captured = 'Yes' AND CapDate > '0000-00-00', Amount, 0 ))AS SumPaid
							FROM 
								sl_orders_payments
							WHERE 
								ID_orders = ". $id_orders ."
								AND Status NOT IN('Order Cancelled', 'Cancelled') 
								AND Amount > 0;");
			($paymentscaptured, $sumpayments, $sumpaid)=$sth->fetchrow_array;

			$sth=&Do_SQL("SELECT 
							SUM(SalePrice)as SumSalePrice
						FROM 
							sl_orders_products
						WHERE 
							ID_orders = ". $id_orders ."
							AND Status NOT IN('Inactive','Order Cancelled')");
			$sumproducts=$sth->fetchrow;

			#################################################
			#################################################
			# Si no hay pago capturado se necesita authcode de Finanzas
			#################################################
			#################################################
			if(!$va{'this_pos_sale'}){
			
				if ( ($cfg{'wms_scan_total_paid'} and $doinventory == 2 ) or (!$cfg{'wms_scan_total_paid'} and ($paymentscaptured == 0 and $sumpayments > 0 and $sumproducts > 0) and $in{'authcode'})  ){
					
					# wms_scan_total_paid = Verifica pago completo
					# doinventory = 1 -> Escaneo de productos
					# doinventory = 2 -> Escaneo de skus

					my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='Authorization Code' AND RIGHT(VValue,4) = '".&filter_values($in{'authcode'})."'; ");
					my ($idadmin,$authorization) = split(/,/,$sth->fetchrow);

					if ($idadmin > 0) {
						## 	Add a Shipment Authorization Note

						&add_order_notes_by_type($id_orders,&trans_txt('order_shpauthorized')." Without Captured Payment","High");
						&auth_logging('orders_note_added',$id_orders);
						$in{'auth_finance'}=1;

					}else{

						#####################################
						## Revisar Si hay numero de autorizacion para la orden $id_orders
						#####################################
						my ($sth2) = &Do_SQL("SELECT ID_vars,VValue FROM sl_vars WHERE VName = 'Auth Order' AND RIGHT(VValue,4) = '$in{'authcode'}'");
						my ($idorder,$idadmin,$authorization) = split(/,/,$sth2->fetchrow,3);

						if ($idorder eq $id_orders) {

							&add_order_notes_by_type($id_orders,&trans_txt('order_shpauthorized')." Without Captured Payment","High");
							&auth_logging('orders_note_added',$id_orders);
							$in{'auth_finance'}=1;

						}else{

							return ($st, trans_txt('payments_invalid_authcode'));

						}

					}

				}elsif( &round($sumpayments - $sumpaid,2 ) > 1 and $cfg{'wms_scan_total_paid'} ){

					## All Payments must be Paid
					return ($st, trans_txt('payments_not_captured'));				

				}elsif($paymentscaptured==0 and $sumpayments>0 and $sumproducts>0 and ($sumpayments > $cfg{'risk_authnopayment'} or !$cfg{'risk_authnopayment'})){

					#return ($st, trans_txt('payments_zero_captured'));
				}
			}


		} ## Check for Minimum payment posted
	}


	##########################
	##########################
	# Si se utilizó el authcode, desocupamos el valor en DB
	##########################
	##########################
	if ($in{'auth_finance'} or $in{'auth_admin'}){
		my ($sth) = &Do_SQL("INSERT INTO cleanup_temp SET ID_orders='$id_orders',Message='Order Shipped but Not Captured due to error in Totals : $status'");
		## Reinitialize the Value
		my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Authorization Code'");
		my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName = 'Auth Order' AND RIGHT(VValue,4)='$in{'authcode'}';");
		delete($in{'auth_finance'})		if	$in{'auth_finance'};
		delete($in{'authcode_admin'})	if	$in{'authcode_admin'};
	}


	if ($cfg{'shprecaldate'}){		#JRG var to update
		$orderdate = &load_name('sl_orders','ID_orders',$id_orders,'Date');
		$today = &get_sql_date(0);
		my ($dth) = Do_SQL("SELECT DATEDIFF('$today','$orderdate');");
		if($dth->fetchrow() >= $cfg{'shprecaldate'} && $cfg{'shprecaldate'} >0){
			if($doflexi==1){
				&update_flexipago($id_orders,&get_sql_date(0));
			}
		}
	}

	my ($sth0,$rec0,$qrystr1,$sth1,$rec1);

	#####################
	#####################
	# Envio Regular
	#####################
	#####################
	if ($doinventory == 1){

		my ($query, $category, $prod_to_mov, @products_movements, $is_codsale);

		### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
		my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
		my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

		### Escanear orden del location Pack?
		my $mod_pack = $in{'scan_from_pack'} ? " AND Location = 'pack' " : '';

		
		%skus_products = fix_hash_for_entershipment(\%ids);

		while( my($sku, $value) = each %skus_products ){
			@order_products_array = split(/,/, $value->{'id_orders_products'});
			$value->{'id_orders_products'} = \@order_products_array;
			my ($sth,$pcost,$pcost_adj);
			my $id_orders_products = $value->{'id_orders_products'};
			my ($this_skucost, $this_skucost_adj, $this_skucost_add) = split(/:/, $value->{'cost'});
			my $add_sql_locations_locked = ($cfg{'validate_locations_locked'} and $cfg{'validate_locations_locked'}==1)? " AND sl_locations.Locked='Inactive'":"";
			my $add_sql_cost = $this_skucost > 0 ? " ABS(Cost - ". $this_skucost ."), " : " ";
			$add_sql_cost .= $this_skucost_adj > 0 ? " ABS(Cost_Adj - ". $this_skucost_adj ."), " : '';
			$add_sql_cost .= $this_skucost_add > 0 ? " ABS(Cost_Add - ". $this_skucost_add ."), " : '';
			$is_codsale = $value->{'codsale'}; ## Flag to indicate a cod sale (don't insert sl_orders_parts, only inventory out)

			$diff_wh = $value->{'qty'};
			my $id_products = $sku;

			$sql = "SELECT 
						sl_warehouses_location.ID_warehouses_location
						, sl_warehouses_location.Location
						, sl_warehouses_location.Quantity 
						, sl_locations.ID_locations
						, sl_warehouses_location.ID_customs_info
					FROM sl_warehouses_location
						INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses=sl_locations.ID_warehouses
						INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_locations.ID_warehouses
					WHERE sl_warehouses_location.ID_warehouses = '". $id_warehouses ."'
						AND sl_warehouses_location.ID_products = '". $id_products ."'
						AND sl_warehouses_location.Quantity > 0 
						AND sl_locations.Status='Active'
						$add_sql_locations_locked
						AND sl_warehouses.Status='Active'
					$mod_pack 
					ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order 
					;";
			$log .= $sql."<br>\n\n";
			my ($sth2) = &Do_SQL($sql);

			while (my $rec = $sth2->fetchrow_hashref){

				if ($diff_wh > 0){
					my $qty_processed=0;

					if ($rec->{'Quantity'} > $diff_wh){
						$sql = "UPDATE sl_warehouses_location SET Quantity = Quantity - $diff_wh WHERE ID_warehouses_location = '". $rec->{'ID_warehouses_location'} ."' LIMIT 1;";
						$log .= $sql."<br>\n\n";
						&Do_SQL($sql);
						$qty_processed = $diff_wh;
					}else{
						$sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '". $rec->{'ID_warehouses_location'} ."' LIMIT 1;";
						$log .= $sql."<br>\n\n";
						&Do_SQL($sql);
						$qty_processed = $rec->{'Quantity'};
					}
					$diff_wh -= $qty_processed;
					$diff_cost = $qty_processed;


					my $pname = &load_name('sl_parts','ID_parts',($id_products - 400000000),'Name');
					$sql = "INSERT INTO sl_locations_notes SET ID_locations = '". $rec->{'ID_locations'} ."', Notes = 'Order: ". $id_orders ."\nType: Scan\nItem: ($id_products) ". &filter_values($pname) ."\nQuantity: $qty_processed', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
					$log .= $sql."<br>\n\n";
					&Do_SQL($sql);

					###########################
					### sl_skus_cost
					###########################
					$sql = "SELECT 
								ID_skus_cost, Quantity, Cost, Cost_Adj, Cost_Add
							FROM sl_skus_cost
							WHERE ID_warehouses = '". $id_warehouses ."'
								AND ID_products = '". $id_products ."'
								AND Quantity > 0 
								AND Cost > 0
							ORDER BY $add_sql_cost Date $invout_order, Time $invout_order
							;";
					# cgierr($sql);
					$log .= $sql."<br>\n\n";

					my ($sth3) = &Do_SQL($sql);
					while (my $rec_cost = $sth3->fetchrow_hashref){

						if ($diff_cost > 0){
							###########################
		                    ### Costo Promedio
		                    ###########################
		                    if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
		                        my ($cost_avg, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($id_products);

		                        if ($cost_avg <= 0) {
		                            
		                            return ("ERROR", "AVG Cost Not Found");

		                        }

		                        $rec_cost->{'Cost'} = $cost_avg;
		                        $rec_cost->{'Cost_Adj'} = $cost_adj;
		                        $rec_cost->{'Cost_Add'} = $cost_add;
		                        $rec->{'ID_customs_info'} = $id_custom_info;

		                        $log .= "cost_avg=".$cost_avg."<br>\n";
		                        $log .= "cost_adj=".$cost_adj."<br>\n";
		                        $log .= "cost_add=".$cost_add."<br>\n";
		                        $log .= "id_custom_info=".$id_custom_info."<br>\n";
		                        $log .= "total_cost_avg=".$total_cost_avg."<br>\n";
		                    }
							$pcost += $rec_cost->{'Cost'};
							$log .= "pcost=".$pcost."<br>\n\n";
							$qty_processed = 0;

							if ($rec_cost->{'Quantity'} > $diff_cost){
								$sql = "UPDATE sl_skus_cost SET Quantity = Quantity - $diff_cost WHERE ID_skus_cost = '". $rec_cost->{'ID_skus_cost'} ."' LIMIT 1;";
								$log .= $sql."<br>\n\n";
								&Do_SQL($sql);
								$qty_processed = $diff_cost;
							}else{
								$sql = "DELETE FROM sl_skus_cost WHERE ID_skus_cost = '". $rec_cost->{'ID_skus_cost'} ."' LIMIT 1;";
								$log .= $sql."<br>\n\n";
								&Do_SQL($sql);
								$qty_processed = $rec_cost->{'Quantity'};
							}
							$diff_cost -= $qty_processed;
							
							###########################
							### sl_skus_trans
							###########################
							&sku_logging($id_products, $id_warehouses, $rec->{'Location'}, 'Sale', $id_orders, 'sl_orders', $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
							$log .= qq|sku_logging($id_products, $id_warehouses, $rec->{'Location'}, 'Sale', $id_orders, 'sl_orders', $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";
							
							###########################
							### sl_orders_parts
							###########################
							if(!$is_codsale){

								$sql = "INSERT INTO sl_orders_parts (Tracking, Cost, Cost_Adj, Cost_Add, ShpDate, ShpProvider, ID_orders_products, ID_parts, Status, Quantity, Date, Time, ID_admin_users) values ";
		                        @id_orders_p = split(/,/, $id_orders_products);

		                        for (1..$qty_processed){
		                        	$el = shift $value->{'id_orders_products'};
		                            $sql.=" ('$tracking', $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, $rec_cost->{'Cost_Add'}, '$shpdate', '$trktype', $el, ($id_products - 400000000), 'Shipped', 1, curdate(), curtime(), $usr{'id_admin_users'}),";
		                        }
		                        chop($sql);
								$log .= $sql."<br>\n\n";
								&Do_SQL($sql);

							}

						}else{
							last;
						}
					}
				}


			}

			if ($diff_wh>0 or $diff_cost>0){
				$log .= "ERROR, $id_warehouses;;$id_products;;$qty;;$in{'scan_from_pack'}";
				
				return ("ERROR", "$id_warehouses;;$id_products;;$qty;;$in{'scan_from_pack'}");
			}

		}
		
		####### Movimientos de contabilidad (2/2)
		my ($order_type, $ctype,@params);
		my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = $id_orders;");
		($order_type, $ctype) = $sth->fetchrow();

		$sql = "SELECT sl_orders_products.ID_orders_products
				FROM sl_orders_products 
				INNER JOIN sl_orders_parts ON sl_orders_products.ID_orders_products=sl_orders_parts.ID_orders_products
				WHERE sl_orders_products.ID_orders = '". $id_orders ."'
				GROUP BY sl_orders_products.ID_orders_products;";
		my $sth_orders_products = &Do_SQL($sql);

		while (my $rec_orders_products = $sth_orders_products->fetchrow_hashref()){
			@arr_id_orders_products = split(/,/,$id_orders_products);
			$sql = "UPDATE sl_orders_products
					INNER JOIN 
					(
					 	SELECT 
							ID_orders_products
							, SUM(sl_orders_parts.Cost * sl_orders_parts.Quantity) As ct
							, sl_orders_parts.Date AS sd
							, sl_orders_parts.Tracking tr
							, sl_orders_parts.ShpProvider pr
						FROM sl_orders_parts 
							INNER JOIN sl_orders_products USING(ID_orders_products)
						WHERE ID_orders_products = '". $rec_orders_products->{'ID_orders_products'} ."'
						GROUP BY ID_orders_products
					)tmp
					USING(ID_orders_products)
					SET Cost = ct, ShpDate = sd, Tracking = tr, ShpProvider = pr, PostedDate = sd
					WHERE ID_orders_products = '". $rec_orders_products->{'ID_orders_products'} ."' ;";
			$log .= $sql."<br>\n\n";

			&Do_SQL($sql);
			@params = ($id_orders, $rec_orders_products->{'ID_orders_products'});
			&accounting_keypoints('order_products_inventoryout_'. $ctype .'_'. $order_type, \@params );
			$log .= qq|accounting_keypoints('order_products_inventoryout_'. $ctype .'_'. $order_type, [$id_orders, $rec_orders_products->{'ID_orders_products'}] );|."<br>\n\n";
		}
		
		##### Inventory Out
		$st = 'ok';

		## Update Order Status & Add Note
		my ($shp_place) = &load_name('sl_orders','ID_orders',$id_orders,"CONCAT(shp_City,' , ',shp_State)");
		$sql = "UPDATE sl_orders SET Status='Shipped', StatusPrd='None' WHERE ID_orders='$id_orders';";
		$log .= $sql."<br>\n\n";
		my ($sth) = &Do_SQL($sql);

		$sql = "UPDATE sl_orders_payments SET PostedDate = CURDATE() WHERE ID_orders='$id_orders' AND (PostedDate IS NULL OR PostedDate = '0000-00-00') ";
		$log .= $sql."<br>\n\n";
		my ($sth) = &Do_SQL($sql);
		$sql = "UPDATE sl_orders SET PostedDate = CURDATE() WHERE ID_orders='$id_orders' AND (PostedDate IS NULL OR PostedDate = '0000-00-00' OR PostedDate = CURDATE()) ";
		$log .= $sql."<br>\n\n";
		my ($sth) = &Do_SQL($sql);


		if(!$is_codsale){

			my $datetoapply;
			$datetoapply = "CURDATE()";
			$datetoapply = "'$in{'datetoapplygv'}'" if ($in{'datetoapplygv'}=~/(\d{4})[-|\/](\d{1,2})[-|\/](\d{1,2})$/);

			&add_order_notes_by_type($id_orders,&trans_txt('order_shipped')." to:$shp_place","Low");
			$log .= $sql."<br>\n\n";
			my ($sth) = &Do_SQL($sql);
			$in{'db'} = "sl_orders";
			&auth_logging('opr_orders_stShipped', $id_orders);
			&status_logging($id_orders, 'Shipped');

		}


		## Clean Tracking Info
		$in{'tracking'} = '';

	}elsif($doinventory == 2){
		#####################
		#####################
		# Envio de exportacion
		#####################
		#####################
		($st, $message) = &do_inventory_exportation($shpdate,$tracking,$trktype,$id_orders,$id_warehouses,$num,%ids);
		$log .= qq|do_inventory_exportation($shpdate,$tracking,$trktype,$id_orders,$id_warehouses,$num,%ids)|."\n";
		$log .= "status=$st\n";
		$log .= "message=$message\n";
	}
	# &send_text_mail($cfg{'to_email_debug'},$cfg{'to_email_debug'},"Debug cost_inventory $id_orders","$log");
	# &cgierr($log.'<br><-------');
	return ($st,$message,$log);
}


#############################################################################
#############################################################################
#   Function: do_inventory_exportation
#
#       Es: Realiza la salida de inventario para ordenes de mayoreo
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on 12/24/2010 by _Roberto Barcenas_ : Se modifica el modo de escanear para sl_skus_cost, se toman valores por costo, y se agrega a sl_orders_parts. 
#
#   Parameters:
#
#      	- shpdate: Fecha en envio para la orden  
#      	- tracking: Tracking number para la orden
#		- trktype: Mensajeria.
#		- id_orders: ID orden
#		- id_warehouses: ID warehouses de salida
#		- num:
#		- ids: arreglo con los ids para salida   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <cost_inventory>
#
sub do_inventory_exportation{
#############################################################################
#############################################################################

	my ($shpdate,$tracking,$trktype,$id_orders,$id_warehouses,$num,%ids) = @_;
	my ($query, $category, $str_message);

	for my $i(1..$num){
		my ($sth,$id_products,$pcost,$actual_cost,$flag,$temp_qty,$qty,$diff_cost,$diff_wh);
		$id_products = $ids{$i}[0];
		$pcost = 0;
		$actual_cost = 0;
		$flag=0;
		$temp_qty=0;
		$qty = $ids{$i}[1];
		my $id_orders_products = $ids{$i}[2];

		# $sql = "SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders = $id_orders AND Related_ID_products = '$id_products' AND Status = 'Active' AND Quantity = $qty ORDER BY ID_orders_products LIMIT 1;";
		# $log .= $sql."<br>\n\n";
		# my ($sth) = &Do_SQL($sql);
		# my $id_orders_products = $sth->fetchrow();


		### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
		my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
		my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

		### Escanear orden del location Pack?
		my $mod_pack = ($in{'scan_from_pack'}) ? " AND UPPER(sl_warehouses_location.Location) = 'PACK' " : '';

		###########################
		### sl_warehouses_location
		###########################
		my $add_sql_locations_locked = ($cfg{'validate_locations_locked'} and $cfg{'validate_locations_locked'}==1)? " AND sl_locations.Locked='Inactive'":"";

		$diff_wh = $qty;
		$diff_cost = $qty;
		$sql = "SELECT 
		sl_warehouses_location.ID_warehouses_location
		, sl_warehouses_location.Location
		, sl_warehouses_location.Quantity 
		, sl_locations.ID_locations
		, ID_customs_info
		FROM sl_warehouses_location
		INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses=sl_locations.ID_warehouses
		INNER JOIN sl_warehouses ON sl_warehouses.ID_warehouses=sl_locations.ID_warehouses
		WHERE sl_warehouses_location.ID_warehouses = $id_warehouses 
		AND sl_warehouses_location.ID_products = $id_products 
		AND sl_warehouses_location.Quantity > 0 
		AND sl_locations.Status='Active'
		$add_sql_locations_locked
		AND sl_warehouses.Status='Active'
		$mod_pack 
		ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order;";
		$log .= $sql."<br>\n\n";
		my ($sth2) = &Do_SQL($sql);
		while (my $rec = $sth2->fetchrow_hashref){

			if ($diff_wh > 0){
				my $qty_processed=0;

				if ($rec->{'Quantity'} > $diff_wh){
					$sql = "UPDATE sl_warehouses_location SET Quantity = Quantity - $diff_wh WHERE ID_warehouses_location = $rec->{'ID_warehouses_location'} LIMIT 1;";
					$log .= $sql."<br>\n\n";
					&Do_SQL($sql);
					$qty_processed = $rec->{'Quantity'} - ($rec->{'Quantity'} - $diff_wh);
				}else{
					$sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = $rec->{'ID_warehouses_location'} LIMIT 1;";
					$log .= $sql."<br>\n\n";
					&Do_SQL($sql);
					$qty_processed = $rec->{'Quantity'};
				}
				$diff_wh -= $rec->{'Quantity'};
				$diff_cost = $qty_processed;

				my $pname = &load_name('sl_parts','ID_parts',($id_products - 400000000),'Name');
				$sql = "INSERT INTO sl_locations_notes SET ID_locations = '$rec->{'ID_locations'}', Notes = 'Order: $id_orders\nType: Scan\nItem: ($id_products) ". &filter_values($pname) ."\nQuantity: $qty_processed', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
				$log .= $sql."<br>\n\n";
				&Do_SQL($sql);

				###########################
				### sl_skus_cost
				###########################
				$sql = "SELECT 
				ID_skus_cost, Quantity, Cost, Cost_Adj, Cost_Add
				FROM sl_skus_cost
				WHERE ID_warehouses = $id_warehouses 
				AND ID_products = $id_products 
				AND Quantity > 0 
				AND Cost > 0 
				ORDER BY Date $invout_order, Time $invout_order;";
				$log .= $sql."<br>\n\n";
				my ($sth3) = &Do_SQL($sql);
				while (my $rec_cost = $sth3->fetchrow_hashref){

					if ($diff_cost > 0){
						###########################
	                    ### Costo Promedio
	                    ###########################
	                    if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
	                        my ($cost_avg, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($id_products);

	                        if ($cost_avg <= 0) {
	                            
	                            return ("ERROR", "AVG Cost Not Found");

	                        }

	                        $rec_cost->{'Cost'} = $cost_avg;
	                        $rec_cost->{'Cost_Adj'} = $cost_adj;
	                        $rec_cost->{'Cost_Add'} = $cost_add;
	                        $rec->{'ID_customs_info'} = $id_custom_info;

	                        $log .= "cost_avg=".$cost_avg."<br>\n";
	                        $log .= "cost_adj=".$cost_adj."<br>\n";
	                        $log .= "cost_add=".$cost_add."<br>\n";
	                        $log .= "id_custom_info=".$id_custom_info."<br>\n";
	                        $log .= "total_cost_avg=".$total_cost_avg."<br>\n";
	                    }

						$pcost += $rec_cost->{'Cost'};
						$log .= "pcost=".$pcost."<br>\n\n";
						$qty_processed = 0;

						if ($rec_cost->{'Quantity'} > $diff_cost){
							$sql = "UPDATE sl_skus_cost SET Quantity = Quantity - $diff_cost WHERE ID_skus_cost = $rec_cost->{'ID_skus_cost'} LIMIT 1;";
							$log .= $sql."<br>\n\n";
							&Do_SQL($sql);
							$qty_processed = $rec_cost->{'Quantity'} - ($rec_cost->{'Quantity'} - $diff_cost);
						}else{
							$sql = "DELETE FROM sl_skus_cost WHERE ID_skus_cost = $rec_cost->{'ID_skus_cost'} LIMIT 1;";
							$log .= $sql."<br>\n\n";
							&Do_SQL($sql);
							$qty_processed = $rec_cost->{'Quantity'};
						}
						$diff_cost -= $rec_cost->{'Quantity'};
						
						###########################
						### sl_skus_trans
						###########################
						&sku_logging($id_products, $id_warehouses, $rec->{'Location'}, 'Sale', $id_orders, 'sl_orders', $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'});
						$log .= qq|sku_logging($id_products, $id_warehouses, $rec->{'Location'}, 'Sale', $id_orders, 'sl_orders', $qty_processed, $rec_cost->{'Cost'}, $rec_cost->{'Cost_Adj'}, "OUT", $rec->{'ID_customs_info'}, $rec_cost->{'Cost_Add'})|."<br>\n\n";
						
						###########################
						### sl_orders_parts
						###########################
						$sql = "INSERT INTO sl_orders_parts SET Tracking='$tracking', Cost='$rec_cost->{'Cost'}', Cost_Adj='$rec_cost->{'Cost_Adj'}', Cost_Add='$rec_cost->{'Cost_Add'}', ShpDate='$shpdate', ShpProvider='$trktype', ID_orders_products='$id_orders_products', ID_parts=($id_products - 400000000), Status='Shipped', Quantity=$qty_processed, Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
						$log .= $sql."<br>\n\n";
						&Do_SQL($sql);
					}
				}
			}
		}

		if ($diff_wh>0 or $diff_cost>0){

			$str_message .= "Invalid Inventory $id_warehouses -> $id_products x $qty <br>";
		}

		$sql = "UPDATE sl_orders_products
		INNER JOIN 
		(
		 	SELECT 
				ID_orders_products
				, SUM(sl_orders_parts.Cost * sl_orders_parts.Quantity) As ct
				, sl_orders_parts.Date AS sd
				, sl_orders_parts.Tracking tr
				, sl_orders_parts.ShpProvider pr
		 FROM sl_orders_parts INNER JOIN sl_orders_products
		 USING(ID_orders_products)
		 WHERE ID_orders_products = '$id_orders_products'
		 GROUP BY ID_orders_products
		)tmp
		USING(ID_orders_products)
		SET Cost = ct, ShpDate = sd, Tracking = tr, ShpProvider = pr, PostedDate = sd
		WHERE ID_orders_products = $id_orders_products;";
		$log .= $sql."<br>\n\n";
		&Do_SQL($sql);

		####### Movimientos de contabilidad
		#######
		my ($order_type, $ctype, $ptype,@params);
		$sql = "SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = $id_orders;";
		$log .= $sql."<br>\n\n";
		my ($sth) = &Do_SQL($sql);
		($order_type, $ctype) = $sth->fetchrow();

		@params = ($id_orders, $id_orders_products);
		&accounting_keypoints('order_skus_inventoryout_'. $ctype .'_'. $order_type, \@params );

	}


	## Update Order Status & Add Note
	$sql = "UPDATE sl_orders SET Status='Shipped', StatusPrd = 'None', PostedDate = '$shpdate' WHERE ID_orders=$id_orders AND (PostedDate IS NULL OR PostedDate = '0000-00-00') ;";
	$log .= $sql."<br>\n\n";
	$sth = &Do_SQL($sql);

	$sql = "UPDATE sl_orders_products SET PostedDate = '$shpdate' WHERE ID_orders=$id_orders AND (PostedDate IS NULL OR PostedDate = '0000-00-00');";
	$log .= $sql."<br>\n\n";
	$sth = &Do_SQL($sql);

	$sql = "UPDATE sl_orders_payments SET PostedDate = '$shpdate' WHERE ID_orders=$id_orders AND (PostedDate IS NULL OR PostedDate = '0000-00-00');";
	$log .= $sql."<br>\n\n";
	$sth = &Do_SQL($sql);

	# Update paymentdate in sl_orders_payment
	&update_paymentdate($id_orders);

	my ($shp_place) = &load_name('sl_orders','ID_orders',$id_orders,"CONCAT(shp_City,' , ',shp_State)");
	$sql = "INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_shipped')." to:$shp_place ',ID_orders_notes_types=1,Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders='$id_orders';";
	$log .= $sql."<br>\n\n";
	
	my ($sth) = &Do_SQL($sql);
	
	
	my $flag = $sth->rows();

	$in{'db'} = "sl_orders";
	&auth_logging('opr_orders_stShipped',$id_orders);
	&status_logging($id_orders,'Shipped');

	&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('cost_inventory', '$id_orders', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	if ($str_message ne ''){
		return ("ERROR", $str_message);
	}else{
		return ('ok', 'ok');
	}

}

sub enterlocaldelivery {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/22/2008
# Last Modified on: 01/12/2009
# Last Modified by: Channged to be used as entershipment
# Description : 
# Forms Involved: 
# Parameters : 
# Notes: Based on entershipment

	$in{'localdelivery'} = 1;
	&entershipment;

}

sub _old_ordercomplete{
#-----------------------------------------
# Created on: 02/10/09  11:31:20 By  Roberto Barcenas
# Forms Involved: &entershipment_cod
# Description : Return sum=products/parts in order to compare with ship products
# Parameters : 	

	my ($id_orders) = @_;
	my $suma =0;

	my ($sth) = &Do_SQL("SELECT ID_sku_products,RIGHT(UPC,5),ID_orders_products AS UPC,IsSet 
				FROM sl_orders_products 
				INNER JOIN sl_skus ON sl_orders_products.ID_products = sl_skus.ID_sku_products
				WHERE ID_orders = $id_orders 
				AND LEFT(sl_orders_products.ID_products,1) <> 6
				/* AND sl_skus.Status = 'Active' */
				AND sl_orders_products.Status='Active' 
				AND(isnull(ShpDate) or ShpDate='' or ShpDate='0000-00-00') ;");




	while($rec = $sth->fetchrow_hashref()){

		if($rec->{'IsSet'}eq'Y'){
			my ($sth) = &Do_SQL("SELECT ID_parts,Qty FROM sl_skus_parts WHERE ID_sku_products = '$rec->{'ID_sku_products'}';");
			while(my($idp,$qty) = $sth->fetchrow()){
				my ($sth2) = &Do_SQL("SELECT SUM(Quantity) FROM sl_orders_parts WHERE ID_orders_products='$rec->{'ID_orders_products'}' AND ID_parts='$idp';");
				$totshp = $sth2->fetchrow();
				if($totshp == 0){
				        my ($sth) = &Do_SQL("SELECT RIGHT(UPC,5)*$qty FROM sl_skus WHERE ID_products = '$idp'");
				        my($upc) = $sth->fetchrow();
				        $suma+= $upc;
				}
			}
		}else{
			$suma+=$rec->{'UPC'};
		}
	}
	return $suma;
}


sub ordercomplete{
#-----------------------------------------
# Created on: 02/10/09  11:31:20 By  Roberto Barcenas
# Forms Involved: &entershipment_cod
# Description : Return sum=products/parts in order to compare with ship products
# Parameters : 	

	my ($id_orders) = @_;
	my $suma =0;
	my $str;

	my ($sthv) = &Do_SQL("SELECT (ID_parts * sl_skus_parts.Qty)
							FROM sl_orders_products INNER JOIN sl_skus ON ID_sku_products = sl_orders_products.ID_products
							INNER JOIN sl_skus_parts USING(ID_sku_products) 
							WHERE ID_orders = '$id_orders' 
							AND sl_orders_products.Status = 'Active'
							AND (sl_orders_products.Cost IS NULL OR sl_orders_products.Cost = '' OR sl_orders_products.Cost = 0)
							AND 1 > (SELECT COUNT(*) FROM sl_orders_parts WHERE ID_orders_products = sl_orders_products.ID_orders_products)
							ORDER BY ID_parts;");


	while(my($id) = $sthv->fetchrow()){	
		$str .= "$suma + $id\n";
		$suma += $id;
	}

	#return $str;
	return $suma;
}	






sub get_bulk_products{
#-----------------------------------------
# Created on: 07/20/09  17:46:33 By  Roberto Barcenas
# Forms Involved: 
# Description : Regresa el arreglo con los productos y upcs de una orden para poderse escanear
# Parameters : 	prefix(orders,preorders), id_tabla

	my($prefix,$id_table) = @_;
	my $upcs ='';
	$id_table = int($id_table);

	##### La orden es valida, se procede a carga de id_products y upcs
	my ($sth) = &Do_SQL("SELECT ID_products,Quantity FROM sl_".$prefix."_products WHERE ID_".$prefix." = '$id_table' AND Status='Active' AND LEFT(ID_products,1) != 6 AND (ShpDate IS NULL OR ShpDate = '' OR ShpDate ='0000-00-00');");
	while(my($id,$pqty) = $sth->fetchrow()){
		my ($sth) = &Do_SQL("SELECT IsSet,UPC FROM sl_skus WHERE ID_sku_products='$id';");
		my ($isset,$upc) = $sth->fetchrow();

		#### Producto?
		if ($isset ne 'Y'){
			$upcs .="\r\n$upc" x $pqty;
		}else{
		#### Parte ?	
			my ($sth) = &Do_SQL("SELECT ID_parts,Qty FROM sl_skus_parts WHERE ID_sku_products='$id';");
			while(my($idp,$paqty) = $sth->fetchrow()){
				my ($sth) = &Do_SQL("SELECT UPC FROM sl_skus WHERE ID_products='$idp';");
				my ($upc) = $sth->fetchrow();
				$upcs .="\r\n$upc" x ($pqty * $paqty);
			}
		}
	}
	return $upcs;
}


#########################################################################################################
#########################################################################################################
#
#	Function: enterwreturn
#   		
#		sp: Recibe items para devolucion wholesale
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub enterwreturn {
#########################################################################################################
#########################################################################################################

	my ($status,$statmsg);
	my $consolidated = 0;
	my ($id_customers, $order_type, $ctype, $status, $msg, @id_products, %ids, $num);
	($va{'message'}) and (delete($va{'message'}));

	if ($in{'action'}){
		if (!$in{'tracking'}){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}

		my $id_orders=0;

		@ary = split(/\n/,$in{'tracking'});

		LINES: for (0..$#ary){
			$ary[$_] =~ s/\n|\r//g;
			if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){
				$id_orders = $1;				
				$consolidated = 1 if &is_exportation_order($id_orders);
				last LINES;
			}
		}
		(!$consolidated) and ($va{'message'} = &trans_txt('scan_not_wholesale'));

		if($consolidated) {
			@ary = split(/\n/,$in{'tracking'});
			LINE: for my $i(0..$#ary){

				$ary[$i] =~ s/\n|\r//g;
				if ($ary[$i] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders) {

					$id_orders = $1;
					$ary[$i] = '';
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$id_orders' AND Status IN ('Processed','Shipped');");

					if ($sth->fetchrow==0){
						$id_orders = 0;
						$va{'message'} .= "<li>".trans_txt('scan_order_invalid_status')."</li>";
					}
				}
				if ($id_orders>0){
					if ($ary[$i] !~ /\@/i ){
						next LINE;
					}elsif($ary[$i] =~ /^$cfg{'prefixentershipment'}(.*)/i and $1 and $i == 0){
						$ary[$i] = $1;
					}else{
						$ary[$i] = $id_orders . '/'.$ary[$i];
					}
					my ($order,$loc,$sku,$this_qty) = split(/\/|\@|x/,$ary[$i]);
					if ($order ne $id_orders){
						$va{'message'} .= "<li>".trans_txt('scan_order_onlyone')."</li>";
					}else{
						$this_loc = &load_name( 'sl_locations','UPC', $loc, 'Code' );
						my ($sth) = &Do_SQL("SELECT ID_sku_products, IsSet FROM sl_skus WHERE ID_sku_products = '$sku' OR UPC='$sku';");
						my ( $this_upc , $isset ) = $sth->fetchrow();
						++$num;
						if ($this_upc > 0 and $isset ne 'Y' and $this_loc){
							push(@id_products,$this_upc);
							push(@upcs,$this_upc);
							$ids{$num}[0] = $this_upc;
							$ids{$num}[1] = $this_upc;
							$ids{$num}[2] = $this_loc;
							$ids{$num}[3] = $this_qty;
						}elsif($this_upc > 0 and $isset ne 'Y' and !$this_loc){
							$ids{$num}[0] = '--';
							$ids{$num}[1] = $this_upc;
							$ids{$num}[2] = 'ERROR';
							$ids{$num}[3] = "<li>Invalid Locatin $loc </li>";
						}else{
							$ids{$num}[0] = '--';
							$ids{$num}[1] = $this_upc;
							$ids{$num}[2] = 'ERROR';
							$ids{$num}[3] = "<li>UPC $ary[$i] ". trans_txt('upc_kit') . "(". &format_sltvid($id) .") </li>";
						}



					}


#				}elsif($ary[$i] and $ary[$i] =~ /^(.+)@(4\d{8})x(\d{1,})$/){
#
#					my $this_loc = $1;
#					my $this_id_prod = int($2);
#					my $this_qty = int($3);
#		
#					my ($sth) = &Do_SQL("SELECT ID_sku_products, IsSet FROM sl_skus WHERE ID_sku_products = '$this_id_prod' ;");
#					my ( $id , $isset ) = $sth->fetchrow();
#					++$num;
#
#					if ($id > 0 and $isset ne 'Y'){
#						push(@id_products,$id);
#						push(@upcs,$this_upc);
#						$ids{$num}[0] = $id;
#						$ids{$num}[1] = $this_upc;
#						$ids{$num}[2] = $this_loc;
#						$ids{$num}[3] = $this_qty;
#					}else{
#						$ids{$num}[0] = '--';
#						$ids{$num}[1] = $this_upc;
#						$ids{$num}[2] = 'ERROR';
#						$ids{$num}[3] = "<li>!!UPC $ary[$i] ". trans_txt('upc_kit') . "(". &format_sltvid($id) .") SELECT ID_sku_products, IsSet FROM sl_skus WHERE UPC = '$this_upc'</li>";
#
#					}

				}else{
					$ids{$num}[0] = '--';
					$ids{$num}[1] = $this_upc;
					$ids{$num}[2] = 'ERROR';
					$ids{$num}[3] = "<li>". trans_txt('scan_upc_unknown')." $ary[$i]</li>";
				}

			} ## LINE

			if (!$id_orders){
				$va{'message'} .= "<li>". trans_txt('scan_order_unknown')."</li>";
			}else{
				$id_customers = &load_name('sl_orders', 'ID_orders', $id_orders, 'ID_customers');
				(!$id_customers) and ($va{'message'} .= "<li>". trans_txt('scan_order_customer_unknown')."</li>");
			}
			if (!$num){
				$va{'message'} .= "<li>". trans_txt('scan_order_noupc')."</li>";
			}

			if(!$va{'message'}) {
				my ($order_type, $ctype);
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
				my ($order_type, $ctype) = $sth->fetchrow();

				## Checking for Items in Order (Shipped) vs Items Returned
				my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, ID_orders_products, sl_orders_parts.Quantity FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' GROUP BY ID_parts;");
				XLINE: while (my($id_sku, $idop, $qty) = $sth->fetchrow_array){
					for my $i(1..$num){ 
						if ($id_sku eq $ids{$i}[0] and $ids{$i}[2] > $qty){ 
							$ids{$i}[2] = 'ERROR';
							$ids{$i}[3] = "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0]). " ".trans_txt('scan_order_wreturn_qtylesser')."</li>";
							next XLINE;

						}elsif($id_sku eq $ids{$i}[0]) {
							$ids{$i}[4] = $idop;
							next XLINE;
						} 

					} ## for num
				} ## while LINE

				## Last check for Errors
				my $okskus = 0;
				for my $i(1..$num) {

				    if ($ids{$i}[2] eq 'ERROR'){
					    $va{'message'} .=  $ids{$i}[3];
				    }elsif (!$ids{$i}[2]){
					    $va{'message'} .= "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." ".trans_txt('scan_order_upcnorder')." </li>";
				    }else{
				    	$okskus++;
				    } 

				}

				######################################  
				######################################
				############### Return Process
				######################################  
				######################################
				if(!$va{'message'} or ($okskus and $cfg{'wreturn_partial_errors'}) ) {

					my($totqty,$sumatoria);
					######################################
					############### 1) Return Record
					###################################### 
					$in{'meraction'} = 'Refund'; ## necessary for orderbalance operation
					my ($sth) = &Do_SQL("INSERT INTO sl_returns SET ID_orders = '$id_orders', ID_customers = '$id_customers', Type='Returned for Refund', generalpckgcondition='Unknown', itemsqty = '1', merAction = '$in{'meraction'}', Status = 'Resolved', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
					my ($id_returns) = $sth->{'mysql_insertid'};

					if($id_returns) {

						### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
						my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
						my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

						######################################
						############### 1) Items Record
						###################################### 

						for my $i(1..$num) {

					    	if ($ids{$i}[2] ne 'ERROR'){

						    	#### 0 id, 1 upc, 2 upc_loc, 3 qty, 4 id_orders_products
						    	my $id_product = $ids{$i}[0];
						    	my $id_orders_products = $ids{$i}[4];
						    	my $quantity = $ids{$i}[3];
								my $code = $ids{$i}[2];
						    	my $id_warehouses = &load_name( 'sl_locations','CODE', $code, 'ID_warehouses' );


						    	$totqty += $quantity;
						    	#&cgierr("IDP: $id_product / IDOP: $id_orders_products / QTY:$quantity / IDWH: $id_warehouses / LU: $loc_code /  C:$code");

						    	## 1) sl_returns_upcs insert
						    	my ($sth) = &Do_SQL("INSERT INTO sl_returns_upcs SET ID_returns = '$id_returns', ID_parts = '$ids{$i}[0]', UPC = '$ids{$i}[1]', ID_warehouses = '$id_warehouses', InOrder = 'yes', Quantity = '$ids{$i}[3]', Status = 'TBD', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

          						
						    #   Modificación de para obtener Costo de Aterrizaje = Cost_Adj // HCeja 21-Mayo-2014
				        	#	## 2) Price + Cost + PCost
				        	#	my ($sthd) = &Do_SQL("SELECT SalePrice / Quantity AS SalePrice, Cost / Quantity AS Cost, Cost AS TCost FROM sl_orders_products WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products';");
				         	#	my ($saleprice,$cost,$pcost) = $sthd->fetchrow();
				            #
				          	#	# No Cost?
							#	if(!$pcost or $pcost < 0){
							#		$sthcost = &Do_SQL("SELECT IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0, sl_orders_parts.Cost,IF(sl_orders_products.Cost IS NULL,0,sl_orders_products.Cost )) FROM sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) WHERE sl_orders_products.ID_orders_products = '$id_orders_products';");
				            #		$cost = $sthcost->fetchrow();
				            #		$pcost = $cost * $quantity;
				          	#	}
				          	#	$cost=0 if !$cost;


				        		## 2) Price + Cost + PCost + Cost_Adj
				        		my ($sthd) = &Do_SQL("SELECT sl_orders_products.SalePrice / sl_orders_products.Quantity AS SalePrice, IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0, sl_orders_parts.Cost, IF( sl_orders_products.Cost IS NULL, 0, sl_orders_products.Cost / sl_orders_products.Quantity )) AS Cost, sl_orders_products.Cost AS TCost, sl_orders_parts.Cost_Adj FROM sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products';");
				         		my ($saleprice,$cost,$pcost,$cost_adj) = $sthd->fetchrow();
				          		$cost=0 if !$cost;
				          		$cost_adj=0 if !$cost_adj;


								## warehouses_location
								my($sthinv);
								my ($sthwl) = &Do_SQL("/* returns_exportartion */ SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = '$id_warehouses' AND ID_products = '$id_product' AND Location = '$code' AND Quantity > 0 ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
								my ($idwl) = $sthwl->fetchrow();

								if($idwl) {
									$sthinv = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity + $quantity WHERE ID_warehouses_location = '$idwl' AND ID_warehouses = '$id_warehouses' AND ID_products = '$id_product';");
								}else{
									$sthinv = &Do_SQL("/* returns_exportartion */ INSERT INTO sl_warehouses_location SET ID_warehouses = '$id_warehouses', ID_products = '$id_product', Location = '$code', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
									&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
								}
								&sku_logging($id_product,$id_warehouses,$code,'Return',$id_returns,'sl_returns',$quantity);

								## skus_cost	
								my ($sths1) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$id_warehouses' AND ID_products = $id_product AND Quantity > 0 AND Cost = '$cost' AND Date=CURDATE() LIMIT 1;");
								my ($idsc) = $sths1->fetchrow();

								if($idsc){
									## Is there a record same day / same cost ?
									&Do_SQL("/* 1 returns_exportartion */ UPDATE sl_skus_cost SET Quantity = Quantity + $quantity WHERE ID_skus_cost = $idsc;");
								}else{									
									my $sthsku = &Do_SQL("/* returns_exportartion */ INSERT INTO sl_skus_cost SET ID_products = '$id_product', ID_purchaseorders = '$in{'id_returns'}', Tblname = 'sl_returns', Cost = '$cost', Cost_Adj = '$cost_adj', ID_warehouses = '$id_warehouses', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'");
								 	 &auth_logging('sku_cost_added',$sthsku->{'mysql_insertid'});
								}

								## Add negative orders_products
								my $tprice = $saleprice * $quantity * -1;
								my $tcost = $cost * $quantity * -1;
								my $tquantity = $quantity * -1;
								my (%tmp) = ('id_products'=>"CONCAT(LEFT(ID_products,3)+1,'000000')",'related_id_products'=>$id_product,'quantity'=>$tquantity,
										'saleprice'=>$tprice,'cost'=>$tcost,'shpdate'=>'CURDATE()','posteddate'=>'CURDATE()','upsell'=>'No','status'=>'Returned',
										'date'=>'CURDATE()','time'=>'CURTIME()', 'id_admin_users'=>$usr{'id_admin_users'});

								my $lastidp = &Do_selectinsert('sl_orders_products',"ID_orders_products = '$id_orders_products'","ORDER BY ID_orders_products DESC","LIMIT 1",%tmp);
								&Do_SQL("UPDATE sl_orders_products SET Tracking = '', ShpProvider = '',Tax = SalePrice * Tax_percent WHERE ID_orders_products = '$lastidp';");


								## Movimientos Contables
								my @params = ($id_orders,$id_product,$pcost);
								&accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, \@params );

								my($sth)=&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns='$id_returns', Notes='Return Processed: $quantity pieces of $idproduct Returned to ".&load_name('sl_warehouses','ID_warehouses',$id_warehouses,'Name')."($id_warehouses) Warehouse ',Type='ATC',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
				          		my($sth)=&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns='$id_returns', Notes='".&filter_values($in{'note'})."',Type='Reception',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';") if ($in{'note'});

				          		&add_order_notes_by_type($id_orders,&filter_values($in{'note'}),"Low");


							} ## end if

						} ## for

						## Sumatoria final
						$sumatoria = &orderbalance($id_orders);

						## Movimientos Contables
						my @params = ($id_orders);
						&accounting_keypoints('order_skus_returned_'. $ctype .'_'. $order_type, \@params );

						my $amount_toreturn = $sumatoria > 0 ? 0 : $sumatoria;
						@params = ($id_orders,$in{'meraction'},0,$amount_toreturn);
						&accounting_keypoints('order_skus_returnsolved_'. $ctype .'_'. $order_type, \@params );
 
						### Last Payment Done
			        	my ($sth2) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Status = 'Approved' 
					    					ORDER BY Captured = 'Yes', LENGTH(AuthCode) DESC, ID_orders_payments DESC LIMIT 1;");
			        	my ($idp) = $sth2->fetchrow();


			        	### Cancel All Pending Payments
			       	 	&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = '$id_orders' AND (Captured='No' OR Captured IS NULL OR Captured='') AND (CapDate IS NULL OR CapDate='0000-00-00'); ");

			        	## Products + Tax + Shipping vs Payments already done
			        	my $posteddate = "";
			        	my $statuspayments = 'Approved';
			        	$statuspayments = 'Credit' if($sumatoria<0);

			        	if($sumatoria < 0.99 * -1 or $sumatoria > 0.99){

			     			my $querypay = !$idp ? "ID_orders = '$id_orders'" : "ID_orders_payments = '$idp'";
			        		my (%tmp) = ('reason'=>$meraction,'amount'=>$sumatoria,'paymentdate'=>'CURDATE()','posteddate'=>'CURDATE()','status'=>$statuspayments,'date'=>'CURDATE()','time'=>'CURTIME()', 'id_admin_users'=>$usr{'id_admin_users'});		
							my $lastidp = &Do_selectinsert('sl_orders_payments',$querypay,"ORDER BY ID_orders_payments DESC","LIMIT 1",%tmp);
						    &auth_logging('orders_payments_added', $id_orders);
						    $in{'amount'} = $amount_toreturn;

			        	}else{
				        	$sumatoria = 0;
			       	 	}

			      		&recalc_totals($id_orders);
						my($sthrt)=&Do_SQL("UPDATE sl_returns SET Amount = '$sumatoria', itemsqty = '$totqty', Status = IF($sumatoria > 0,'Pending Payments','Pending Refunds') WHERE ID_returns = '$id_returns'");			  
						delete($in{'done'});
						$va{'message'} .= "\n Return Resolved ($in{'amount'} to Refund).<!--return OK-->";

					}else{
						$va{'message'} .= "<li>".trans_txt('scan_order_wreturn_noidreturn')." </li>";
					}


				} ## message + okskus

			} ## message

		}## !Error

	} ## Action
	if ($ENV{'REQUEST_URI'} =~ /apps\/entershipment/){
		$va{'cgiurl'} = '/cgi-bin/common/apps/entershipment';
	}else{
		$va{'cgiurl'} = '/cgi-bin/mod/wms/admin';
	}
	print "Content-type: text/html\n\n";
	print &build_page('enterwreturn.html');
}


#########################################################################################################
#########################################################################################################
#
#	Function: entercmreturn
#   		
#		sp: Recibe items para devolucion wholesale
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub entercmreturn {
#########################################################################################################
#########################################################################################################

	my ($status,$statmsg);
	my $consolidated = 0;
	my ($id_customers, $order_type, $ctype, $status, $msg, @id_products, %ids, $num);
	my $log = "Debug cmd=entercmreturn\n\n";

	($va{'message'}) and (delete($va{'message'}));

	if ($in{'action'}){

		if (!$in{'tracking'}){
			$error{'tracking'} = &trans_txt('required');
			++$err;
		}

		if (!$in{'retdate'}){
			$error{'retdate'} = &trans_txt('required');
			++$err;
		}

		my $id_creditmemos=0;
		@ary = split(/\n/,$in{'tracking'});
		LINES: for (0..$#ary){
			$ary[$_] =~ s/\n|\r//g;
			if ($ary[$_] =~ /(\d+)/i and !$id_creditmemos){
				$id_creditmemos = $1;
			}elsif($ary[$_] =~ /(\d+)\/(.*)/i and !$id_creditmemos){
				$id_creditmemos = $1;
				$ary[$_] = $2;
			}
		}

		$log .= "in{'tracking'}=".$in{'tracking'}."\n";
		$log .= "in{'retdate'}=".$in{'retdate'}."\n";
		$log .= "id_creditmemos=".$id_creditmemos."\n";

		@ary = split(/\n/,$in{'tracking'});
		LINE: for my $i(0..$#ary){
			$ary[$i] =~ s/\n|\r//g;
			++$num;
			if ($ary[$i] =~ /(\d+)/i and !$id_creditmemos) {
				$id_creditmemos = $1;
				$ary[$i] = '';
				$sql .= "SELECT COUNT(*) FROM sl_creditmemos WHERE ID_creditmemos='$id_creditmemos' AND Status IN ('Approved','Applied');";
				$log .= $sql."\n";
				my ($sth) = &Do_SQL($sql);
				if ($sth->fetchrow==0){
					$id_creditmemos = 0;
					++$err;
					$va{'message'} .= "<li>".trans_txt('scan_cm_invalid_status')."</li>";
				}
			}

			if ($id_creditmemos>0){
				if ($ary[$i] !~ /\@/i ){
					$ids{$num}[0] = ''; 
					$ids{$num}[1] = 'ok';
					next LINE;
				}elsif($ary[$i] !~ /\//i ){
					$ary[$i] = $id_creditmemos . '/'.$ary[$i];
				}

				my ($cm,$loc,$sku,$this_qty) = split(/\/|\@|x/,$ary[$i]);
				$log .= "cm=".$cm."\n";
				$log .= "loc=".$loc."\n";
				$log .= "sku=".$sku."\n";
				$log .= "this_qty=".$this_qty."\n\n";
				
				if ($cm ne $id_creditmemos){
					$va{'message'} .= "<li>".trans_txt('scan_cm_onlyone')."</li>";
					++$err;
					$log .= "$cm ne $id_creditmemos\n\n";
					last LINE;
				}else{
					$sql = "SELECT Code,ID_warehouses FROM sl_locations WHERE UPC='".&filter_values($loc)."'";
					$log .= $sql."\n";
					my ($sth) = &Do_SQL($sql);
					my ($this_loc,$this_wh) = $sth->fetchrow_array();
					
					if ($this_loc eq '' or !$this_wh){
						++$err;
						$va{'message'} .= "UPC Location Unknown $loc<br>";
					}

					$log .= "this_loc=".$this_loc."\n";
					$log .= "this_wh=".$this_wh."\n\n";

					$sql = "SELECT ID_sku_products FROM sl_creditmemos_products LEFT JOIN sl_skus ON ID_sku_products=sl_creditmemos_products.ID_products WHERE (ID_sku_products = '$sku' OR UPC='$sku') AND ID_creditmemos = '$id_creditmemos' AND ShpDate IS NULL;";
					$log .= $sql."\n";
					my ($sth) = &Do_SQL($sql);
					my ($this_sku) = $sth->fetchrow();
					
					if (!$this_sku){
						++$err;
						$va{'message'} .= "Product Unknown $sku<br>";
					}

					$log .= "this_sku=".$this_sku."\n\n";

					if ($this_sku and $this_loc and $this_wh){
						$ids{$this_sku}[0] += $this_qty;
						$ids{$this_sku}[1] .= "$this_loc|$this_wh|$this_qty|";
						push(@id_products,$this_sku);
						push(@upcs,$this_sku);
						$ids{$num}[0] = $this_sku; 
						$ids{$num}[1] = 'ok';
					}else{
						$ids{$num}[0] = '';
						$ids{$num}[1] = 'ERROR';
						$ids{$num}[2] = "<li>$ary[$i] ". trans_txt('invalid') ."</li>";
					}
				}
			}else{
				$ids{$num}[0] = '';
				$ids{$num}[1] = 'ERROR';
				$ids{$num}[2] = "<li>". &trans_txt('scan_upc_unknown')." $ary[$i]</li>";
			}

		} ## LINE

		if (!$id_creditmemos){
			++$err;
			$va{'message'} .= "<li>". trans_txt('scan_cm_unknown')."</li>";
		}else{
			$id_customers = &load_name('sl_creditmemos', 'ID_creditmemos', $id_creditmemos, 'ID_customers');
			
			if (!$id_customers){
				++$err;
				$va{'message'} .= "<li>". trans_txt('scan_cm_customer_unknown')."</li>";
			}
		}

		if ($num < 2){
			$va{'message'} .= "<li>". trans_txt('scan_order_noupc')."</li>";
		}

		if (!$va{'message'} and !$err) {
			my ($ctype) = &load_name('sl_customers', 'ID_customers', $id_customers, 'Type');

			## Checking for Items in Order (Shipped) vs Items Returned
			$sql = "SELECT ID_products, ID_creditmemos_products, Quantity, ShpDate FROM sl_creditmemos_products WHERE ID_creditmemos = '$id_creditmemos'";
			$log .= $sql."\n";
			my ($sth) = &Do_SQL($sql);
			XLINE: while (my($id_sku, $idcmp, $qty, $shpdate) = $sth->fetchrow_array){
				$log .= "id_sku=".$id_sku."\n";
				$log .= "idcmp=".$idcmp."\n";
				$log .= "qty=".$qty."\n\n";
				for my $i(1..$num){ 
					if ($id_sku eq $ids{$i}[0] and $ids{$id_sku}[0] ne $qty){ 
						$log .= qq|$id_sku eq $ids{$i}[0] and $ids{$id_sku}[0] ne $qty|."\n";
						$ids{$i}[1] = 'ERROR';
						$ids{$i}[2] = "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0]). " x ".$ids{$id_sku}[0]." : ".trans_txt('scan_cm_wreturn_qty')."</li>";
						$va{'message'} .=  $ids{$i}[2];
						next XLINE;
					}

					if ($shpdate ne ''){
						$va{'message'} .= "Previously returned product $sku<br>";
					}
				} ## for num
			} ## while LINE

			######################################  
			######################################
			############### Return Process
			######################################  
			######################################
			if (!$va{'message'}) {
				&Do_SQL("START TRANSACTION");
				$log .= "START TRANSACTION\n\n";

				my ($return_note);
				my $cost_not_found=0;

				######################################
				############### 1) Items Record
				###################################### 
				$sql = "SELECT * FROM sl_creditmemos_products WHERE ID_creditmemos = '$id_creditmemos' AND ShpDate IS NULL;";
				$log .= $sql."\n";
				my ($sth) = &Do_SQL($sql);
				while (my $rec = $sth->fetchrow_hashref){
					$log .= "ids{$rec->{'ID_products'}}[0]=".$ids{$rec->{'ID_products'}}[0]."\n";
					$log .= "ids{$rec->{'ID_products'}}[1]=".$ids{$rec->{'ID_products'}}[1]."\n";
					$log .= "rec->{'Quantity'}=".$rec->{'Quantity'}."\n\n";
					
					if ($ids{$rec->{'ID_products'}}[0] eq $rec->{'Quantity'}){
						chop($ids{$rec->{'ID_products'}}[1]);
						## Warehouse Location Add Items
						$log .= "->".$ids{$rec->{'ID_products'}}[1]."\n\n";
						my (@ary)= split(/\|/,$ids{$rec->{'ID_products'}}[1]);

						my ($cost, $to_dump, $id_customs_info, $cost_adj, $cost_add);
						my $idx = 0;
						while( $idx < $#ary ){
							my $location = $ary[$idx];
							my $id_warehouses = $ary[$idx+1];
							my $quantity = $ary[$idx+2];

							###########################
							### Costo Promedio
							###########################
							if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
								($cost, $to_dump, $id_customs_info, $cost_adj, $cost_add) = &get_average_cost($rec->{'ID_products'});
								$log .= "($cost, $to_dump, $id_customs_info, $cost_adj, $cost_add) = get_average_cost($rec->{'ID_products'}) \n\n";

								## Sino se encuentra el Costo Promedio se intenta con el ultimo Costo de Compra
								if ( !$cost or $cost == 0 or $cost eq ''){
									 ($cost, $cost_adj, $cost_add, $cost_add) = &load_last_purchase_cost($rec->{'ID_products'});
								}

							}else{
								($cost, $cost_adj, $id_customs_info, $cost_add) = &load_sltvcost($rec->{'ID_products'});
								$log .= "($cost, $cost_adj, $id_customs_info, $cost_add)=load_sltvcost($rec->{'ID_products'}) \n\n";
							}
							
							## CreditMemo to Shipped
							$sql = "UPDATE sl_creditmemos_products SET ShpDate='$in{'retdate'}', Cost='$cost', Cost_Adj='$cost_adj', Cost_Add='$cost_add' WHERE ID_creditmemos_products='$rec->{'ID_creditmemos_products'}'";
							$log .= $sql."\n";
							my ($sth2) = &Do_SQL($sql);

							if (!$cost or $cost == 0 or $cost eq ''){
								$cost_not_found++;
								$cost_not_found_msg .= &trans_txt('enternewcmreturn_cost_not_found')." $rec->{'ID_products'}<br>";
								$log .= &trans_txt('enternewcmreturn_cost_not_found')." $rec->{'ID_products'}<br>";
							}else{
								my $add_sql_custom_info='';
								$add_sql_custom_info .= ($id_customs_info and $id_customs_info ne '')? ", ID_customs_info='$id_customs_info' ":"";

								### Se valida si ya existe un registro en sl_warehouses_location
								my $sel_sql_custom_info = (!$id_customs_info) ? "AND ID_customs_info IS NULL" : "AND ID_customs_info = $id_customs_info";
					            $sql = "SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = $id_warehouses AND ID_products = $rec->{'ID_products'} AND Location = '$location' $sel_sql_custom_info ORDER BY Date DESC LIMIT 1;";
					            my $sth_exist = &Do_SQL($sql);
					            my $id_wl = $sth_exist->fetchrow();
					            if( int($id_wl) > 0 ){
					                $sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $quantity WHERE ID_warehouses_location = $id_wl;";
					            }else{
									$sql = "INSERT INTO sl_warehouses_location SET ID_warehouses='$id_warehouses', ID_products='$rec->{'ID_products'}', Location='$location', Quantity='$quantity' $add_sql_custom_info, Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
								}
								$log .= $sql."\n";
								$sthinv = &Do_SQL($sql);
								&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});

								&sku_logging($rec->{'ID_products'}, $id_warehouses, $location, 'Return', $id_creditmemos, 'sl_creditmemos', $quantity, $cost, $cost_adj, "IN", $id_customs_info, $cost_add);
								$log .= qq|sku_logging($rec->{'ID_products'}, $id_warehouses, $location, 'Return', $id_creditmemos, 'sl_creditmemos', $quantity, $cost, $cost_adj, "IN", $id_customs_info, $cost_add)|."\n\n";

								$return_note .= "$id_warehouses:$location \@ $rec->{'ID_products'} x $quantity\n";
								
								$sql = "INSERT INTO sl_skus_cost SET ID_products='$rec->{'ID_products'}', ID_purchaseorders='$id_creditmemos', ID_warehouses='$id_warehouses', Tblname='sl_creditmemos', Cost='$cost', Cost_Adj='$cost_adj', Quantity='$quantity', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'";
								$log .= $sql."\n";
								my $sthsku = &Do_SQL($sql);
							 	&auth_logging('sku_cost_added',$sthsku->{'mysql_insertid'});

							}

							$idx += 3;
						} ## for @ary

						############
						############ Mov. Contables
						############
						## ToDo: No se puede saber cuanto le toca a cada orden. Evaluar sacar porcentaje en base a sl_creditmemos_payments. Por el momento contabilidad de la devolucion se queda en creditmemos
						my $pcost =round($rec->{'Quantity'} * $cost,2);
						my @params = ($id_creditmemos,$rec->{'ID_products'},$rec->{'Quantity'},$pcost);
						&accounting_keypoints('cm_skus_backtoinventory_'. $ctype, \@params );
						$log .= qq|accounting_keypoints('cm_skus_backtoinventory_'. $ctype, [$id_creditmemos,$rec->{'ID_products'},$rec->{'Quantity'},$pcost] )|."\n\n";
						
					}

				} ## for num

				if ($cost_not_found > 0){
					&Do_SQL("ROLLBACK");
					$va{'message'} = $cost_not_found_msg;
				}else{
	          		$sql = "INSERT INTO sl_creditmemos_notes SET ID_creditmemos='$id_creditmemos', Notes='".&filter_values($in{'note'})."',Type='Reception',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';";
	          		$log .= $sql."\n" if ($in{'note'});
	          		my($sth)=&Do_SQL($sql) if ($in{'note'});
	          		
	          		$sql = "INSERT INTO sl_creditmemos_notes SET ID_creditmemos='$id_creditmemos', Notes='".&trans_txt('scan_cm_processed')." $return_note ',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';";
	          		$log .= $sql."\n";
	          		my($sth)=&Do_SQL($sql);

					delete($in{'done'});
					$va{'message'} .= "\n".&trans_txt('scan_cm_processed')."<!--return OK-->";

					&Do_SQL("COMMIT");
					# &Do_SQL("ROLLBACK"); ## Debug only
				}

			} ## message + okskus

		} ## message


		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('entercmreturn', '$id_creditmemos', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	} ## Action
	if ($ENV{'REQUEST_URI'} =~ /apps\/entershipment/){
		$va{'cgiurl'} = '/cgi-bin/common/apps/entershipment';
	}else{
		$va{'cgiurl'} = '/cgi-bin/mod/wms/admin';
	}
	print "Content-type: text/html\n\n";
	print &build_page('entercmreturn.html');
}

#########################################################################################################
#########################################################################################################
#
#	Function: enternewcmreturn
#   		
#		sp: Recibe items para devolucion wholesale
#
#	Created by:
#		@ivanmiranda
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub enternewcmreturn {
#########################################################################################################
#########################################################################################################

	my ($status,$statmsg);
	my $consolidated = 0;
	my ($id_customers, $order_type, $ctype, $status, $msg, @id_products, %ids, $num);
	$err = 0;
	($va{'message'}) and (delete($va{'message'}));
	if ($in{'action'}){
		if (!$in{'tracking'}){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}
		if (!$in{'customer'}){
			$error{'customer'} = &trans_txt('required');
			++$err;
		}else{
			my ($sth) = &Do_SQL("SELECT ID_customers, `Type` FROM sl_customers WHERE ID_customers=".&filter_values($in{'customer'}).";");
			($id_customers, $ctype) = $sth->fetchrow_array();
			$id_customers = int($id_customers);
			if($id_customers < 1){
				$error{'customer'} = "Customer not found";
				++$err;
			}else{
				#Primero se valida que el folio de la devolucion no se hubiera capturado previamente
				$captured = 0;
				my ($sth) = &Do_SQL("SELECT id_creditmemos FROM sl_creditmemos WHERE ID_customers=".$id_customers." AND Reference='".&filter_values($in{'note'})."';");
				my ($captured,) = $sth->fetchrow_array();
				if($captured > 0){
					$va{'message'} .= &trans_txt('previous_creditmemo').$captured;
					++$err;
				}
			}
		}
		if (!$in{'retdate'}){
			$error{'retdate'} .= &trans_txt('required');
			++$err;
		}
		if (!$in{'note'}){
			$error{'note'} .= &trans_txt('required');
			++$err;
		}

		my $id_creditmemos=0;
		my $qry_customers = '';

		@ary = split(/\n/,$in{'tracking'});
		LINE: for my $i(0..$#ary){
			$ary[$i] =~ s/\n|\r//g;
			++$num;
			if ($ary[$i] !~ /\@/i ){
				$ids{$num}[0] = ''; 
				$ids{$num}[1] = 'ok';
				next LINE;
			}
			
			my ($loc,$sku,$this_qty) = split(/\@|x|\/|\//i,$ary[$i]);
			$this_qty = int($this_qty);

			if (!$this_qty){
				++$err;
				$va{'message'} .= "\<br>".&trans_txt('scan_cm_wreturn_qty');
			}

			#&cgierr( $ary[$i]." ::: ".$loc.' -> '.$sku.' -> '.$this_qty );
			my ($sth) = &Do_SQL("SELECT Code,ID_warehouses FROM sl_locations WHERE UPC='".&filter_values($loc)."'");
			my ($this_loc,$this_wh) = $sth->fetchrow_array();
			my ($sth) = &Do_SQL("SELECT ID_sku_products FROM sl_skus where ID_sku_products = '$sku' OR UPC='$sku';");
			my ($this_sku) = $sth->fetchrow();
			if ($this_sku and $this_loc and $this_wh){
				$ids{$this_sku}[0] += $this_qty;
				$ids{$this_sku}[1] .= "$this_loc|$this_wh|$this_qty|";
				push(@id_products,$this_sku);
				push(@upcs,$this_sku);
				$ids{$num}[0] = $this_sku; 
				$ids{$num}[1] = 'ok';
			}
			
			###-------------------------------------------
			### Se valida la existencia del Precio y Tax del SKU
			###-------------------------------------------			
			if( $this_sku ne '' ){				
				if($cfg{'use_rfc'}){
					my $ids = &Do_SQL("SELECT 
											GROUP_CONCAT(c2.ID_customers) ids
										FROM sl_customers c1
										INNER JOIN sl_customers c2 on c2.RFC = c1.RFC
										WHERE 1
											AND c1.ID_customers = ".$id_customers."
										GROUP BY c2.RFC;")->fetchrow();
					$qry_customers = ($ids) ? " AND sl_customers_parts.ID_customers IN ($ids) " : " AND sl_customers_parts.ID_customers = '$id_customers' ";
				}else{
					$qry_customers = " AND sl_customers_parts.ID_customers = '$id_customers' ";
				}

				my $sql = "SELECT sPrice
							FROM sl_customers_parts
							WHERE 1
								".$qry_customers."
								AND sl_customers_parts.ID_parts = RIGHT(".$this_sku.", 4)
							LIMIT 1;";
				my ($sth) = &Do_SQL($sql);
				my $this_price = $sth->fetchrow();
				if( !$this_price and $id_customers ){
					++$err;
					$va{'message'} .= "\<br>$sku :: ".&trans_txt('returns_creditmemo_without_price');
				}

				my $sql = "SELECT ID_parts, Sale_Tax
							FROM sl_parts
							WHERE ID_parts = RIGHT(".$this_sku.", 4);";
				my ($sth) = &Do_SQL($sql);
				my ($this_part, $this_tax) = $sth->fetchrow_array();
				if( !$this_part and !$this_tax ){
					++$err;
					$va{'message'} .= "\n<br>$sku :: ".&trans_txt('returns_creditmemo_without_tax');
				}
			}else{
				++$err;
				$va{'message'} .= "\n<br>$sku :: ".&trans_txt('returns_creditmemo_sku_notfound');
			}
		} ## LINE

		if (!$num){
			$va{'message'} .= "<li>". trans_txt('scan_order_noupc')."</li>";
		}

		if(!$va{'message'} and $err == 0) {			

			######################################  
			######################################
			############### Return Process
			######################################  
			######################################
			&Do_SQL("START TRANSACTION;");
			$id_creditmemos = 0;
			$cost_not_found = 0;
			$cost_not_found_msg = '<br>';
			if(!$va{'message'}) {
				$log .= "in{'tracking'}=".$in{'tracking'}."\n\n";

				#Crear el CM, que almacenara los productos que se estan escaneando...
				if($id_creditmemos == 0){
					$sql = "INSERT INTO sl_creditmemos SET ID_customers = ".$id_customers.", Reference = '".$in{'note'}."', Description = '".$in{'note'}."',Status = 'New', Date=CURDATE(),Time=CURTIME(),ID_admin_users=".$usr{'id_admin_users'}.";";
					$log .= $sql."\n\n";
					my ($sth_cm) = &Do_SQL($sql);
					$id_creditmemos = $sth_cm->{'mysql_insertid'};
				}
				#...e insertar los productos solicitados
				@ary = split(/\n/,$in{'tracking'});
				LINE: for my $i(0..$#ary){
					$ary[$i] =~ s/\n|\r//g;
					++$num;
					if ($ary[$i] !~ /\@/i ){
						$ids{$num}[0] = ''; 
						$ids{$num}[1] = 'ok';
						next LINE;
					}
					# }elsif($ary[$i] !~ /\//i ){
					# 	$ary[$i] = $id_creditmemos . '/'.$ary[$i];
					# }

					my ($loc, $sku, $this_qty) = split(/\@|x|\/|\//i,$ary[$i]);

					# my ($sthLocation) = &Do_SQL("SELECT Code,ID_warehouses FROM sl_locations WHERE UPC='".&filter_values($loc)."';");
					# my ($Code,$ID_warehouses) = $sthLocation->fetchrow_array();

					my ($sthProds) = &Do_SQL("SELECT ID_sku_products,ID_products from sl_skus WHERE ID_sku_products = '$sku' OR UPC='$sku';");
					my ($ID_sku_products,$ID_products) = $sthProds->fetchrow_array();
					
					####
					#### Se obtinen el precio y tax del SKU
					####
					my $this_price = 0;
					my $this_tax = 0;
					my $sql = "SELECT sl_customers_parts.sPrice, sl_parts.Sale_Tax
								FROM sl_customers_parts
									INNER JOIN sl_parts ON sl_customers_parts.ID_parts = sl_parts.ID_parts
								WHERE 1
									".$qry_customers." 
									AND sl_customers_parts.ID_parts = RIGHT(".$ID_sku_products.", 4)
								GROUP BY sl_customers_parts.ID_customers, sl_customers_parts.ID_parts
								LIMIT 1;";
					my $sth_price = &Do_SQL($sql);
					($this_price, $this_tax) = $sth_price->fetchrow_array();


					if ($this_tax > 0){
						$this_price_tax = ($this_price * ($this_tax/100)) * $this_qty; #($this_price - ($this_price * (100 / ($this_tax + 100))) * $this_qty);
					}else{
						$this_price_tax = 0;
					}
					
					$sql = "SELECT Code,ID_warehouses FROM sl_locations WHERE UPC='".&filter_values($loc)."';";
					$log .= $sql."\n\n";
					my ($sthLocation) = &Do_SQL($sql);
					my ($Code, $ID_warehouses) = $sthLocation->fetchrow_array();
					$log .= "Code=".$Code."\n\n";
					$log .= "ID_warehouses=".$ID_warehouses."\n\n";

					if (!$ID_warehouses or !$Code){
						$cost_not_found++;
						$cost_not_found_msg .= "UPC Location Unknown $loc<br>";
					}

					$sql = "SELECT ID_sku_products,ID_products from sl_skus WHERE ID_sku_products = '$sku' OR UPC='$sku';";
					$log .= $sql."\n\n";

					my ($sthProds) = &Do_SQL($sql);
					my ($ID_sku_products, $ID_products) = $sthProds->fetchrow_array();
					$log .= "ID_sku_products=".$ID_sku_products."\n\n";
					$log .= "ID_products=".$ID_products."\n\n";

					if (!$ID_sku_products or !$ID_products){
						$cost_not_found++;
						$cost_not_found_msg .= "Product Unknown $sku<br>";
					}
					
					if ($this_tax > 0){
						$this_price_tax = ($this_price * ($this_tax/100)) * $this_qty;
						# ($this_price - ($this_price * (100 / ($this_tax + 100))) * $this_qty);
						$log .= "this_price_tax=($this_price * ($this_tax/100)) * $this_qty \n\n";
					}else{
						$this_price_tax = 0;
						$log .= "this_price_tax=0 \n\n";
					}

					if (!$cost_not_found){
					
						###------------------------------------------------------
						### Costo de producto
						###------------------------------------------------------
						my ($this_cost,$to_dump, $id_customs_info, $this_cost_adj, $this_cost_add);

						if ($cfg{'acc_inventoryout_method_cost'} and lc($cfg{'acc_inventoryout_method_cost'}) eq 'average'){
							
							($this_cost,$to_dump, $id_customs_info, $this_cost_adj, $cost_add) = &get_average_cost($ID_sku_products);
							$log .= "($this_cost, $to_dump, $id_customs_info, $this_cost_adj, $cost_add)=get_average_cost($ID_sku_products) \n\n";
							
							if( !$this_cost or $this_cost == 0 or $this_cost eq ''){
								($this_cost, $this_cost_adj, $this_cost_add) = &load_last_purchase_cost($ID_sku_products);
							}

						}else{
							($this_cost, $this_cost_adj, $id_customs_info) = &load_sltvcost($ID_sku_products);
							$log .= "($this_cost, $this_cost_adj, $id_customs_info)=load_sltvcost($ID_sku_products) \n\n";
						}
						### Valida que el costo sea mayor que 0
						if (!$this_cost or $this_cost == 0 or $this_cost eq ''){
							++$err;
							$va{'message'} .= &trans_txt('enternewcmreturn_cost_not_found')." $ID_sku_products<br>";
						}

						$sql = "INSERT INTO sl_creditmemos_products SET 
									ID_products = ".$ID_sku_products."
									, Location = '".$loc."'
									, ID_creditmemos = ".$id_creditmemos."
									, Quantity = ".$this_qty."
									, SalePrice = ".$this_price."
									, Cost='".$this_cost."'
									, Cost_Adj='".$this_cost_adj."'
									, Tax = round(".$this_price_tax.",2)
									, Tax_percent = ".$this_tax."
									, ShpDate = '".$in{'retdate'}."'
									, Status = 'Active'
									, Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$usr{'id_admin_users'}.";";
						$log .= $sql."\n\n";
						my ($sth_cmprd) = &Do_SQL($sql);
						$ID_creditmemos_products = $sth_cmprd->{'mysql_insertid'};
						
						###------------------------------------------------------
						### Inventario
						###------------------------------------------------------
						# my $add_sql_custom_info='';
						# $add_sql_custom_info .= ($id_customs_info and $id_customs_info ne '')? ", ID_customs_info='$id_customs_info' ":"";
						# if (!$this_cost or $this_cost == 0 or $this_cost eq ''){
						# 	$cost_not_found++;
						# 	$cost_not_found_msg .= &trans_txt('enternewcmreturn_cost_not_found')." $ID_sku_products<br>";
						# }else{
						# 	&sku_logging($ID_sku_products,$ID_warehouses, $Code, 'Return', $id_creditmemos, 'sl_creditmemos', $this_qty, $this_cost, $this_cost_adj, 'IN', $id_customs_info, $cost_add);
						# 	$log .= "sku_logging($ID_sku_products,$ID_warehouses, $Code, 'Return', $id_creditmemos, 'sl_creditmemos', $this_qty, $this_cost, $this_cost_adj, 'IN', $id_customs_info, $cost_add) \n\n";
						# }
						# my ($sthinv) =  &Do_SQL("SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = ".$ID_warehouses." AND Location = '".$Code."' and ID_products=".$ID_sku_products.";");
						# my ($ID_warehouses_location) = $sthinv->fetchrow();
						
						# my $sel_sql_custom_info = (!$id_customs_info) ? "AND ID_customs_info IS NULL" : "AND ID_customs_info = $id_customs_info";
			   			# $sql = "SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = $ID_warehouses AND ID_products = $ID_sku_products AND Location = '$Code' $sel_sql_custom_info ORDER BY Date DESC LIMIT 1;";
			    		# my $sth_exist = &Do_SQL($sql);
			   			# my $id_wl = $sth_exist->fetchrow();
			   			# if( int($id_wl) > 0 ){
			   			# 	$sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $this_qty WHERE ID_warehouses_location = $id_wl;";
			   			# }else{
						# 	$sql = "INSERT INTO sl_warehouses_location SET ID_warehouses=".$ID_warehouses.", ID_products=".$ID_sku_products.", Location='".$Code."', Quantity=".$this_qty." $add_sql_custom_info, Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
						# }
						# $log .= $sql."\n\n";
						# $sthinv = &Do_SQL($sql);
						# &auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
						
						# $sql = "INSERT INTO sl_skus_cost SET ID_products = '".$ID_sku_products."',ID_purchaseorders='".$id_creditmemos."',ID_warehouses='".$ID_warehouses."',Tblname='sl_creditmemos',Quantity='".$this_qty."',Cost='".$this_cost."', Cost_Adj='".$this_cost_adj."', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}';";
						# $log .= $sql."\n\n";
						# &Do_SQL($sql);
						
						###------------------------------------------------------
						### Contailidad
						###------------------------------------------------------
						# my $sku_cost = round($this_qty * $this_cost,2);
						# my $sku_price = ($this_price * $this_qty);# + $this_price_tax;
						# my @params = ($id_creditmemos, $id_customers, $sku_cost, $sku_price, $this_price_tax, $in{'retdate'});
						# &accounting_keypoints('skus_backtoinventory_wo_cm_'. $ctype, \@params);
						# $log .= "accounting_keypoints('skus_backtoinventory_wo_cm_'. $ctype, [$id_creditmemos, $id_customers, $sku_cost, $sku_price, $in{'retdate'}]) \n\n";
						###------------------------------------------------------
					}
				}
				my($return_note);
				
          		my($sth)=&Do_SQL("INSERT INTO sl_creditmemos_notes SET ID_creditmemos='$id_creditmemos', Notes='".&filter_values($in{'note'})."',Type='Reception',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';") if ($in{'note'});
          		my($sth)=&Do_SQL("INSERT INTO sl_creditmemos_notes SET ID_creditmemos='$id_creditmemos', Notes='".&trans_txt('scan_cm_processed')." $return_note ',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

          		###------------------------------------------------------
          		### Aprobación del nuevo CreditMemo
          		###------------------------------------------------------
          		## Se cambia el status del CreditMemo
				# my ($sth) = &Do_SQL("UPDATE sl_creditmemos SET `Status` = 'Approved' WHERE ID_creditmemos = ". $id_creditmemos .";");				
				# $log .= "Aprobacion del nuevo CreditMemo\n";
				# $log .= "UPDATE sl_creditmemos SET `Status` = 'Approved' WHERE ID_creditmemos = ". $id_creditmemos .";\n\n";

          		# Generate Credit Note
				# ($va{'tabmessages'}, $status) = &export_info_for_credits_notes($id_creditmemos);
				# if ($status =~ /OK/i){
				if (int($err) <= 0){

					delete($in{'done'});
					$va{'message'} .= "\n<br>".&trans_txt('scan_cm_processed')." :: ID Created ".$id_creditmemos."<!--return OK-->";
					$log .= $va{'message'}."\n\n";
				}
				# }else{
				# 	++$err;
				# 	$va{'message'} .= "Invoice Response :: ".$va{'tabmessages'};
				# 	$log .= $va{'message'}."\n\n";
				# }
          		###------------------------------------------------------

			} ## message + okskus

			if ($cost_not_found > 0 or int($err) > 0){
				&Do_SQL("ROLLBACK");
				$va{'message'} .= $cost_not_found_msg;
				$log .= $va{'message'}."\n\n";
				$log .= "ROLLBACK\n\n";
			}else{
				&Do_SQL("COMMIT");
				# &Do_SQL("ROLLBACK"); ## Debug only
				$log .= "COMMIT\n\n";

				### Se limpian los input
				$in{'tracking'} = '';
				$in{'note'} = '';
			}

			&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('enternewcmreturn', '$in{'customer'}', '".$va{'message'}."\n\n-->\n\n".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		} ## message



	} ## Action
	if ($ENV{'REQUEST_URI'} =~ /apps\/entershipment/){
		$va{'cgiurl'} = '/cgi-bin/common/apps/entershipment';
	}else{
		$va{'cgiurl'} = '/cgi-bin/mod/wms/admin';
	}
	print "Content-type: text/html\n\n";
	print &build_page('enternewcmreturn.html');
}

#####################################################################
#####################################################################
#######################
####################### Sub Funciones
#######################
#####################################################################
#####################################################################


sub orderbalance {
# --------------------------------------------------------	
# Acci?n: Creaci?n
# Comentarios:
# Created on: unknown
# Author: Roberto B?rcenas Uribe
# Description :  
# Parameters :
# Last Modified on: 07/17/08 15:41:20
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la forma en la que se contemplar?n los pagos. Se toman s?lo para hacer la equivalencia entre productos y payments

# Description30jun2008 :  Se agregan validaciones para resultados de suma/diferencia y se agrega descripci?n de funci?n

#GV Termina modificaci?n 13jun2008: Se cambia orderBalance por orderbalance
# Last Modified on: 09/02/08 15:59:36
# Last Modified by: MCC C. Gabriel Varela S: Se cambian las condiciones para sumar los pagos
# Last Modified on: 09/26/08 15:59:36
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la forma en que se suma lo pagado

	my ($idorder) = @_;

	if(!$idorder) {

		if($in{'id_orders_products'}) {
			$idorder=&load_name('sl_orders_products','ID_orders_products',$in{'id_orders_products'},'ID_orders');
		}elsif($in{'id_orders'}){
			$idorder=$in{'id_orders'};
		}else{
			return "Invalid order";
		}
	}

	my ($sumatoryOrder,$sumatorypayments);

	my ($sth1) = &Do_SQL("SELECT COUNT(*)
							FROM sl_orders, sl_orders_products
							WHERE sl_orders.ID_orders = '$idorder'
							AND sl_orders.ID_orders = sl_orders_products.ID_orders
							AND sl_orders_products.Status NOT
							IN ('Order Cancelled', 'Inactive')");

	$sumatoryOrder = $sth1->fetchrow;

	### SUM PRODUCTS IN ORDER
	if($sumatoryOrder) {
		my ($sth1) = &Do_SQL("SELECT SUM((SalePrice-Discount)+Tax+Shipping+ShpTax) FROM sl_orders_products
								WHERE ID_orders = '$idorder'
								AND sl_orders_products.Status NOT IN ('Order Cancelled', 'Inactive');");

		$sumatoryOrder = $sth1->fetchrow;
	}


	my $cond=" STATUS NOT IN ('Order Cancelled', 'Cancelled') ";
	$cond = " STATUS IN ('Approved') AND ((CapDate!='0000-00-00') or (NOT ISNULL(AuthCode) AND AuthCode!='')) " if($in{'meraction'} eq "Refund");
	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '$idorder' AND $cond");

	$sumatorypayments = $sth2->fetchrow;

	if($sumatorypayments){

		my ($sth2) = &Do_SQL("SELECT IF(SUM(Amount) IS NULL,0,SUM(Amount)) FROM sl_orders_payments WHERE ID_orders = '$idorder' AND $cond");
		$sumatorypayments = $sth2->fetchrow;
	}

	#&cgierr("$idorder $sumatoryOrder - $sumatorypayments");
	#$va{'message'}.="Return amount: ".&format_price($sumatoryOrder - $sumatorypayments);
	return $sumatoryOrder - $sumatorypayments;

}


#########################################################################################################
#########################################################################################################
#
#	Function: enterwreturn
#   		
#		sp: Recibe items para devolucion wholesale / retail
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub enterwreturn2 {
#########################################################################################################
#########################################################################################################

	my ($status,$statmsg);
	my $consolidated = 0;
	my $st_type = 'New'; ## Si se ingresa por Retail, se deja en new porque el proceso del usuario tiene que determinar el camino a seguir
	my ($id_customers, $order_type, $ctype, $status, $msg, @id_products, %ids, $num);
	($va{'message'}) and (delete($va{'message'}));

	if ($in{'action'}){
		if (!$in{'tracking'}){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}

		my $id_orders=0;

		@ary = split(/\n/,$in{'tracking'});

		LINES: for (0..$#ary){
			$ary[$_] =~ s/\n|\r//g;
			if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){
				$id_orders = $1;
				$consolidated = 1 if &is_exportation_order($id_orders);
				last LINES;
			}
		}
		#(!$consolidated) and ($va{'message'} = &trans_txt('scan_not_wholesale'));
		(!$consolidated) and ($fast_back_to_inventory = 1) and ($st_type = 'Resolved');

		#if($consolidated) {
		if(1) {

			@ary = split(/\n/,$in{'tracking'});
			######1
			LINE: for my $i(0..$#ary){

				$ary[$i] =~ s/\n|\r//g;
				if ($ary[$i] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders) {

					###########################
					###########################
					###########################
					## 1) ID_orders
					###########################
					###########################
					###########################
					$id_orders = $1;
					$ary[$i] = '';
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$id_orders' AND Status IN ('Processed','Shipped');");

					if ($sth->fetchrow==0){

						#########
						######### 1.1) No exista la orden o no tiene el status correcto
						#########
						$id_orders = 0;
						$va{'message'} .= "<li>".trans_txt('scan_order_invalid_status')."</li>";

					}

				}elsif($cfg{'return_one_by_order'}){

					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders = '$id_orders' AND Status <> 'Void';");
					my ($tr) = $sth->fetchrow();

					#########
					######### 1.2) Ya existe un proceso de Devolucion para la orden y solo se permite uno por orden
					#########
					($tr) and ($va{'message'} .= "<li>".trans_txt('scan_order_duplicated_return')."</li>");

				}


				###########################
				###########################
				###########################
				## Cargamos ahora los datos en memoria
				###########################
				###########################
				###########################
				if ($id_orders > 0){

					if ($ary[$i] !~ /\@/i ){
						next LINE;
					}

					my ($loc,$sku,$this_qty) = split(/\/|\@|x/,$ary[$i]);
					$this_loc = &load_name( 'sl_locations','UPC', $loc, 'Code' );

					my ($sth) = &Do_SQL("SELECT ID_sku_products, UPC, IsSet FROM sl_skus WHERE ID_sku_products = '$sku' OR UPC='$sku';");
					my ( $this_part, $this_upc , $isset ) = $sth->fetchrow();
					++$num;

					if ($this_part > 0 and $isset ne 'Y' and $this_loc){

						push(@id_products,$this_part);
						push(@upcs,$this_upc);
						$ids{$num}[0] = $this_part;
						$ids{$num}[1] = $this_upc;
						$ids{$num}[2] = $this_loc;
						$ids{$num}[3] = $this_qty;
						$ids{$num}[5] = $loc;

					}elsif($this_part > 0 and $isset ne 'Y' and !$this_loc){

						$ids{$num}[0] = '--';
						$ids{$num}[1] = $this_upc;
						$ids{$num}[2] = 'ERROR';
						$ids{$num}[3] = "<li>Invalid Locatin $loc </li>";

					}elsif($this_part > 0 and $isset eq 'Y'){

						$ids{$num}[0] = '--';
						$ids{$num}[1] = $this_upc;
						$ids{$num}[2] = 'ERROR';
						$ids{$num}[3] = "<li>UPC $ary[$i] ". trans_txt('upc_kit') . "(". &format_sltvid($this_part) .") </li>";

					}else{

						$ids{$num}[0] = '--';
						$ids{$num}[1] = $this_upc;
						$ids{$num}[2] = 'ERROR';
						$ids{$num}[3] = "<li>UPC $sku Not Found in $ary[$i]</li>";

					}						

				}else{

					$ids{$num}[0] = '--';
					$ids{$num}[1] = $this_upc;
					$ids{$num}[2] = 'ERROR';
					$ids{$num}[3] = "<li>". trans_txt('scan_upc_unknown')." $ary[$i]</li>";

				}

			} ## LINE

			if (!$id_orders){
				$va{'message'} .= "<li>". trans_txt('scan_order_unknown')."</li>";
			}else{
				$id_customers = &load_name('sl_orders', 'ID_orders', $id_orders, 'ID_customers');
				$this_status = &load_name('sl_orders', 'ID_orders', $id_orders, 'Status');
				(!$id_customers) and ($va{'message'} .= "<li>". trans_txt('scan_order_customer_unknown')."</li>");
				($this_status ne 'Shipped') and ($va{'message'} .= "<li>". trans_txt('returns_order_notshipped')."</li>");

				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' GROUP BY sl_orders_parts.ID_orders_products");
				my ($tp) = $sth->fetchrow();
				(!$tp and $this_status eq 'Shipped') and ($va{'message'} .= "<li>". trans_txt('returns_order_skusnotshipped')."</li>");

			}

			if (!$num){
				$va{'message'} .= "<li>". trans_txt('scan_order_noupc')."</li>";
			}
			######2


			if(!$va{'message'}) {

				my ($order_type, $ctype);
				my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
				my ($order_type, $ctype) = $sth->fetchrow();

				## Checking for Items in Order (Shipped) vs Items Returned
				my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, ID_orders_products, sl_orders_parts.Quantity FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' GROUP BY ID_parts;");
				#my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, ID_orders_products, sl_orders_parts.Quantity FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders';");
				XLINE: while (my($id_sku, $idop, $qty) = $sth->fetchrow_array){
					for my $i(1..$num){ 
						if ($id_sku eq $ids{$i}[0] and $ids{$i}[2] > $qty){ 
							$ids{$i}[2] = 'ERROR';
							$ids{$i}[3] = "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0]). " ".trans_txt('scan_order_wreturn_qtylesser')."</li>";
							next XLINE;

						}elsif($id_sku eq $ids{$i}[0]) {
							$ids{$i}[4] = $idop;
							next XLINE;
						} 

					} ## for num
				} ## while LINE

				## Last check for Errors
				my $okskus = 0;
				for my $i(1..$num) {

				    if ($ids{$i}[2] eq 'ERROR'){
					    $va{'message'} .=  $ids{$i}[3];
				    }elsif (!$ids{$i}[2]){
					    $va{'message'} .= "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." ".trans_txt('scan_order_upcnorder')." </li>";
				    }else{
				    	$okskus++;
				    } 

				}

				######################################  
				######################################
				############### Return Process
				######################################  
				######################################
				if(!$va{'message'} or ($okskus and $cfg{'wreturn_partial_errors'}) ) {

					my($totqty,$sumatoria);
					######################################
					############### 1) Return Record
					###################################### 
					$in{'meraction'} = 'Refund'; ## necessary for orderbalance operation
					my ($sth) = &Do_SQL("INSERT INTO sl_returns SET ID_orders = '$id_orders', ID_customers = '$id_customers', Type='Returned for Refund', generalpckgcondition='Unknown', itemsqty = '1', merAction = '$in{'meraction'}', Status = '$st_type', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
					my ($id_returns) = $sth->{'mysql_insertid'};

					if($id_returns) {

						### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
						my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
						my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

						######################################
						############### 1) Items Record
						###################################### 

						for my $i(1..$num) {

					    	if ($ids{$i}[2] ne 'ERROR'){

						    	#### 0 id, 1 upc, 2 upc_loc, 3 qty, 4 id_orders_products
						    	my $id_product = $ids{$i}[0];
						    	my $id_orders_products = $ids{$i}[4];
						    	my $quantity = $ids{$i}[3];
								my $code = $ids{$i}[2];
								my $upc_location = $ids{$i}[5];

								my ($sth) = &Do_SQL("SELECT ID_warehouses FROM sl_locations WHERE 1 AND sl_locations.UPC='$upc_location' AND Status='Active';");
						    	my ($id_warehouses) = $sth->fetchrow_array;

						    	$totqty += $quantity;
						    	#&cgierr("IDP: $id_product / IDOP: $id_orders_products / QTY:$quantity / IDWH: $id_warehouses / LU: $loc_code /  C:$code");

						    	## 1) sl_returns_upcs insert
						    	my ($sth) = &Do_SQL("INSERT INTO sl_returns_upcs SET ID_returns = '$id_returns', ID_parts = '$ids{$i}[0]', UPC = '$ids{$i}[1]', ID_warehouses = '$id_warehouses', InOrder = 'yes', Quantity = '$ids{$i}[3]', Status = 'TBD', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

						    	my $saleprice; my $cost = 0; my $pcost = 0; my $cost_adj = 0;
          
				        		## 2) Price + Cost + PCost
								if($fast_back_to_inventory) {

									#######################
									#######################
									####### Retail W/FBI
									#######################
									#######################


									#my ($sthd) = &Do_SQL("SELECT SUM(Cost) AS Cost, SUM(Cost) * $quantity AS TCost FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) INNER JOIN sl_skus ON ID_parts = ID_products WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products' AND ID_parts;");										
									my ($sthd) = &Do_SQL("SELECT sku_cost.Cost AS Cost, (sku_cost.Cost * $quantity) AS TCost, sku_cost.Cost_Adj
															FROM sl_orders_products 
															LEFT JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products = sl_orders_products.ID_products 
															LEFT JOIN (SELECT ID_products, Cost, Cost_Adj FROM (SELECT * FROM sl_skus_cost ORDER BY date DESC, time DESC) a GROUP BY ID_products) sku_cost ON sku_cost.ID_products=(sl_skus_parts.ID_parts+400000000)
	 														WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products' AND ID_parts;");										
									($cost, $pcost, $cost_adj) = $sthd->fetchrow()	;

								}else{

									#######################
									#######################
									####### Wholesale
									#######################
									#######################

				        			my ($sthd) = &Do_SQL("SELECT sl_orders_products.SalePrice / sl_orders_products.Quantity AS SalePrice, IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0, sl_orders_parts.Cost, IF( sl_orders_products.Cost IS NULL, 0, sl_orders_products.Cost / sl_orders_products.Quantity )) AS Cost, sl_orders_products.Cost AS TCost, sl_orders_parts.Cost_Adj FROM sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products';");
				         			($saleprice,$cost,$pcost,$cost_adj) = $sthd->fetchrow();

				          		}


				          		# # No Cost?
								# if(!$pcost or $pcost < 0){
								#	$sthcost = &Do_SQL("SELECT IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0, sl_orders_parts.Cost,IF(sl_orders_products.Cost IS NULL,0,sl_orders_products.Cost )) FROM sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) WHERE sl_orders_products.ID_orders_products = '$id_orders_products';");
				            	#	$cost = $sthcost->fetchrow();
				            	#	$pcost = $cost * $quantity;
				          		#}

				          		$cost=0 if !$cost;
				          		$cost_adj=0 if !$cost_adj;

								## warehouses_location
								my($sthinv);
								my ($sthwl) = &Do_SQL("/* returns_exportartion */ SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = '$id_warehouses' AND ID_products = '$id_product' AND Location = '$code' AND Quantity > 0 ORDER BY Date $invout_order, Time $invout_order LIMIT 1;");
								my ($idwl) = $sthwl->fetchrow();

								if($idwl) {
									$sthinv = &Do_SQL("UPDATE sl_warehouses_location SET Quantity = Quantity + $quantity WHERE ID_warehouses_location = '$idwl' AND ID_warehouses = '$id_warehouses' AND ID_products = '$id_product';");
								}else{
									$sthinv = &Do_SQL("/* returns_exportartion */ INSERT INTO sl_warehouses_location SET ID_warehouses = '$id_warehouses', ID_products = '$id_product', Location = '$code', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
									&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
								}
								&sku_logging($id_product,$id_warehouses,$code,'Return',$id_returns,'sl_returns',$quantity, $cost, $cost_adj);

								## skus_cost	
								my ($sths1) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$id_warehouses' AND ID_products = $id_product AND Quantity > 0 AND Cost = '$cost' AND Date=CURDATE() LIMIT 1;");
								my ($idsc) = $sths1->fetchrow();

								if($idsc){
									## Is there a record same day / same cost ?
									&Do_SQL("/* 1 returns_exportartion */ UPDATE sl_skus_cost SET Quantity = Quantity + $quantity WHERE ID_skus_cost = $idsc;");
								}else{									
									my $sthsku = &Do_SQL("/* returns_exportartion */ INSERT INTO sl_skus_cost SET ID_products = '$id_product', ID_purchaseorders = '$in{'id_returns'}', Tblname = 'sl_returns', Cost = '$cost', Cost_Adj = '$cost_adj' , ID_warehouses = '$id_warehouses', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'");
								 	 &auth_logging('sku_cost_added',$sthsku->{'mysql_insertid'});
								}

								## Add negative orders_products

								#######################
								#######################
								####### Only Wholesale
								#######################
								#######################

								if($consolidated) {

									my $tprice = $saleprice * $quantity * -1;
									my $tcost = $cost * $quantity * -1;
									my $tquantity = $quantity * -1;
									my (%tmp) = ('id_products'=>"CONCAT(LEFT(ID_products,3)+1,'000000')",'related_id_products'=>$id_product,'quantity'=>$tquantity,
											'saleprice'=>$tprice,'cost'=>$tcost,'shpdate'=>'CURDATE()','posteddate'=>'CURDATE()','upsell'=>'No','status'=>'Returned',
											'date'=>'CURDATE()','time'=>'CURTIME()', 'id_admin_users'=>$usr{'id_admin_users'});

									my $lastidp = &Do_selectinsert('sl_orders_products',"ID_orders_products = '$id_orders_products'","ORDER BY ID_orders_products DESC","LIMIT 1",%tmp);
									&Do_SQL("UPDATE sl_orders_products SET Tracking = '', ShpProvider = '',Tax = SalePrice * Tax_percent WHERE ID_orders_products = '$lastidp';");

								}

								## Movimientos Contables
								my @params = ($id_orders,$id_product,$pcost);
								&accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, \@params );

								my($sth)=&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns='$id_returns', Notes='Return Processed: $quantity pieces of $idproduct Returned to ".&load_name('sl_warehouses','ID_warehouses',$id_warehouses,'Name')."($id_warehouses) Warehouse ',Type='ATC',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
				          		my($sth)=&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns='$id_returns', Notes='".&filter_values($in{'note'})."',Type='Reception',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';") if ($in{'note'});

				          		&add_order_notes_by_type($id_orders,"Return Processed: $quantity pieces of $idproduct Returned to ".&load_name('sl_warehouses','ID_warehouses',$id_warehouses,'Name')."($id_warehouses) Warehouse","Low");


							} ## end if

						} ## for


						if($consolidated) {

							#######################
							#######################
							####### Only Wholesale
							#######################
							#######################

							## Sumatoria final
							$sumatoria = &orderbalance($id_orders);

							## Movimientos Contables
							my @params = ($id_orders);
							&accounting_keypoints('order_skus_returned_'. $ctype .'_'. $order_type, \@params );

							my $amount_toreturn = $sumatoria > 0 ? 0 : $sumatoria;
							@params = ($id_orders,$in{'meraction'},0,$amount_toreturn);
							&accounting_keypoints('order_skus_returnsolved_'. $ctype .'_'. $order_type, \@params );

							### Last Payment Done
				        	my ($sth2) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Status = 'Approved' 
						    					ORDER BY Captured = 'Yes', LENGTH(AuthCode) DESC, ID_orders_payments DESC LIMIT 1;");
				        	my ($idp) = $sth2->fetchrow();


				        	### Cancel All Pending Payments
				       	 	&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = '$id_orders' AND (Captured='No' OR Captured IS NULL OR Captured='') AND (CapDate IS NULL OR CapDate='0000-00-00'); ");

				        	## Products + Tax + Shipping vs Payments already done
				        	my $posteddate = "";
				        	my $statuspayments = 'Approved';
				        	$statuspayments = 'Credit' if($sumatoria<0);

				        	if($sumatoria < 0.99 * -1 or $sumatoria > 0.99){

				     			my $querypay = !$idp ? "ID_orders = '$id_orders'" : "ID_orders_payments = '$idp'";
				        		my (%tmp) = ('reason'=>$meraction,'amount'=>$sumatoria,'paymentdate'=>'CURDATE()','posteddate'=>'CURDATE()','status'=>$statuspayments,'date'=>'CURDATE()','time'=>'CURTIME()', 'id_admin_users'=>$usr{'id_admin_users'});		
								my $lastidp = &Do_selectinsert('sl_orders_payments',$querypay,"ORDER BY ID_orders_payments DESC","LIMIT 1",%tmp);
							    &auth_logging('orders_payments_added', $id_orders);
							    $in{'amount'} = $amount_toreturn;

				        	}else{
					        	$sumatoria = 0;
				       	 	}

				      		&recalc_totals($id_orders);
							my($sthrt)=&Do_SQL("UPDATE sl_returns SET Amount = '$sumatoria', itemsqty = '$totqty', Status = IF($sumatoria > 0,'Pending Payments','Pending Refunds') WHERE ID_returns = '$id_returns'");			  
							delete($in{'done'});
							$va{'message'} .= "\n Return Resolved ($in{'amount'} to Refund).<!--return OK-->";

						}else{
							$va{'message'} .= qq|\n Return Process with Fast Back to Inventory Started (<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_returns&view=$id_returns">$id_returns</a>)|;
						}


					}else{
						$va{'message'} .= "<li>".trans_txt('scan_order_wreturn_noidreturn')." </li>";
					}


				} ## message + okskus

			} ## message

		}## !Error

	} ## Action
	&Do_SQL("update sl_skus_cost a left join (select * from (select ID_products, Cost, Date, Time from sl_skus_cost where Cost>0 order by Date DESC, Time DESC) a group by ID_products) b using (ID_products) set a.Cost=b.Cost where a.Cost=0");
	if ($ENV{'REQUEST_URI'} =~ /apps\/entershipment/){
		$va{'cgiurl'} = '/cgi-bin/common/apps/entershipment';
	}else{
		$va{'cgiurl'} = '/cgi-bin/mod/wms/admin';
	}
	print "Content-type: text/html\n\n";
	print &build_page('enterwreturn2.html');
}



#########################################################################################################
#########################################################################################################
#
#	Function: enterwreturn
#   		
#		sp: Recibe items para devolucion wholesale / retail
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub enter_return {
#########################################################################################################
#########################################################################################################

	my ($status,$statmsg);
	my $id_orders=0;
	my $consolidated = 0;
	my $rtype = $in{'type'} ? $in{'type'} : 'Unknown'; ## Retail
	my $st_type = 'New'; ## Si se ingresa por Retail, se deja en new porque el proceso del usuario tiene que determinar el camino a seguir
	my ($id_customers, $order_type, $ctype, $status, $msg, @id_products, %ids, $num);
	my $fast_back_to_inventory = 0; #$cfg{'fastbackinventory'} ? 1 : 0;
	my $log = "Debug cmd=enter_return\n\n";
	$in{'meraction'} = 'To Be Determined by CR';
	($va{'message'}) and (delete($va{'message'}));

	if ($in{'action'}){

		&Do_SQL("START TRANSACTION;");
		$log .= "START TRANSACTION\n\n";

		if (!$in{'tracking'}){
			$va{'message'} = &trans_txt('reqfields');
			++$err;
		}
		@ary = split(/\n/,$in{'tracking'});

		$log .= "in{'tracking'}=".$in{'tracking'}."\n";

		###########################
		###########################
		###########################
		## Se determina si es una orden tipo sku (mayoreo)
		###########################
		###########################
		###########################
		LINES: for (0..$#ary){
			$ary[$_] =~ s/\n|\r//g;
			if ($ary[$_] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders){
				$id_orders = $1;
				$consolidated = 1 if &is_exportation_order($id_orders);
				last LINES;
			}
		}
		($consolidated and $cfg{'fastbackinventory'}) and ($fast_back_to_inventory = 1) and ($st_type = 'Resolved') and ($rtype = 'Returned for Refund') and ($in{'meraction'} = 'Refund');

		$log .= "consolidated=".$consolidated."\n";
		$log .= "cfg{'fastbackinventory'}=".$cfg{'fastbackinventory'}."\n";
		$log .= "is_exportation_order=".&is_exportation_order($id_orders)."\n";
		$log .= "st_type=".$st_type."\n";
		$log .= "rtype=".$rtype."\n";
		$log .= "id_orders=".$id_orders."\n";


		###########################
		###########################
		###########################
		## Se procesan las lineas para extraer los datos
		###########################
		###########################
		###########################
		@ary = split(/\n/,$in{'tracking'});
		LINE: for my $i(0..$#ary){

			$ary[$i] =~ s/\n|\r//g;

			###########################
			###########################
			###########################
			## Cargamos los datos en memoria
			###########################
			###########################
			###########################
			if ($ary[$i] =~ /^(.+)\@(.+)x(\d{1,})$/){

				#if ($ary[$i] !~ /\@/ ){
				#	next LINE;
				#}

				my ($loc,$sku,$this_qty);# = split(/\/|\@|x/,$ary[$i]);
				$loc = $1; $sku = $2; $this_qty = int($3);
				$this_loc = &load_name( 'sl_locations','UPC', $loc, 'Code' );

				my $queryupc = "SELECT ID_products, UPC, IsSet FROM sl_skus WHERE ( ID_sku_products = '$sku' AND LENGTH(ID_sku_products) > 3 ) OR ( UPC = '$sku' AND LENGTH(UPC) > 0 );";
				$log .= $queryupc."\n";
				my ($sth) = &Do_SQL($queryupc);
				my ( $this_part, $this_upc , $isset ) = $sth->fetchrow();
				$log .= "this_part=".$this_part."\n";
				$log .= "this_upc=".$this_upc."\n";
				$log .= "isset=".$isset."\n";

				if ($this_part > 0 and $isset ne 'Y' and $this_loc){

					push(@id_products,$this_part);
					push(@upcs,$this_upc);
					++$num;
					$ids{$num}[0] = $this_part;
					$ids{$num}[1] = $this_upc;
					$ids{$num}[2] = $this_loc;
					$ids{$num}[3] = $this_qty;
					$ids{$num}[5] = $loc;
					

				}elsif($this_part > 0 and $isset ne 'Y' and !$this_loc){

					$ids{$num}[0] = '--';
					$ids{$num}[1] = $this_upc;
					$ids{$num}[2] = 'ERROR';
					$ids{$num}[3] = "<li>Invalid Locatin $loc </li>";

				}elsif($this_part > 0 and $isset eq 'Y'){

					$ids{$num}[0] = '--';
					$ids{$num}[1] = $this_upc;
					$ids{$num}[2] = 'ERROR';
					$ids{$num}[3] = "<li>UPC $ary[$i] ". trans_txt('upc_kit') . "(". &format_sltvid($this_part) .") </li>";

				}else{

					$ids{$num}[0] = '--';
					$ids{$num}[1] = $this_upc;
					$ids{$num}[2] = 'ERROR';
					$ids{$num}[3] = "<li>UPC $sku Not Found in $ary[$i]</li>";

				}						

			}elsif ($ary[$i] =~ /^$cfg{'prefixentershipment'}(\d+)/i and !$id_orders) {

				###########################
				###########################
				###########################
				## 1) ID_orders
				###########################
				###########################
				###########################
				$id_orders = $1;
				$ary[$i] = '';
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_orders='$id_orders' AND Status IN ('Processed','Shipped');");

				if ($sth->fetchrow==0){

					#########
					######### 1.1) No exista la orden o no tiene el status correcto
					#########
					$id_orders = 0;
					$va{'message'} .= "<li>".trans_txt('scan_order_invalid_status')."</li>";

				}

			}else{

				$ids{$num}[0] = '--';
				$ids{$num}[1] = $this_upc;
				$ids{$num}[2] = 'ERROR';
				$ids{$num}[3] = "<li>". trans_txt('scan_upc_unknown')." $ary[$i]</li>";

			}

		} ## LINE

		if (!$id_orders){

			$va{'message'} .= "<li>". trans_txt('scan_order_unknown')."</li>";

		}else{

			#&cgierr($str);
			####
			#### Validacion Orden
			####
			my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT ID_orders_products)
								FROM
								(
									SELECT ID_orders_parts, sl_orders_products.ID_orders_products 
									FROM sl_orders_products LEFT JOIN sl_orders_parts USING(ID_orders_products) 
									WHERE ID_orders = '$id_orders'
									AND sl_orders_products.Status IN('Active','ReShip','Exchange')
									AND IF($consolidated = 1,
											LENGTH(Related_ID_products) = 9 AND LEFT(Related_ID_products,1) = 4,
											RIGHT(ID_products,6) >= 100000
										)
									AND SalePrice >= 0		 
									HAVING ID_orders_parts IS NULL
								)tmp;");
			my ($pactive) = $sth->fetchrow();
			
			if($pactive){

				####
				#### b) Orden tiene productos activos sin enviar (Orden consolidada solo permite 1 devolucion total)
				####
				$va{'message'} .= "<li>".trans_txt('scan_order_pactive_return')."</li>";

			}else{

				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns 
									WHERE ID_orders = '$id_orders' 
									AND IF($consolidated = 1,
											Status NOT IN ('Void'),	
											Status NOT IN ('Void','Resolved')
										);");
				my ($tr) = $sth->fetchrow();

				#########
				######### c) Ya existe un proceso de Devolucion para la orden y solo se permite uno por orden activo
				#########
				($tr) and ($va{'message'} .= "<li>".trans_txt('scan_order_duplicated_return')."</li>");

			}	


			$id_customers = &load_name('sl_orders', 'ID_orders', $id_orders, 'ID_customers');
			$this_status = &load_name('sl_orders', 'ID_orders', $id_orders, 'Status');
			(!$id_customers) and ($va{'message'} .= "<li>". trans_txt('scan_order_customer_unknown')."</li>");
			($this_status ne 'Shipped') and ($va{'message'} .= "<li>". trans_txt('returns_order_notshipped')."</li>");

			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' GROUP BY sl_orders_parts.ID_orders_products");
			my ($tp) = $sth->fetchrow();
			(!$tp and $this_status eq 'Shipped') and ($va{'message'} .= "<li>". trans_txt('returns_order_skusnotshipped')."</li>");

		}

		if (!$num){
			$va{'message'} .= "<li>". trans_txt('scan_order_noupc')."</li>";
		}



		if(!$va{'message'}) {

			###########################
			###########################
			###########################
			## Evaluamos los datos
			###########################
			###########################
			###########################

			my ($order_type, $ctype);
			my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
			my ($order_type, $ctype) = $sth->fetchrow();

			## Checking for Items in Order (Shipped) vs Items Returned
			my ($sth) = &Do_SQL("SELECT ID_parts, ID_orders_products, sl_orders_parts.Quantity FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' GROUP BY ID_parts;");
			#my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, ID_orders_products, sl_orders_parts.Quantity FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders';");
			XLINE: while (my($id_parts, $idop, $qty) = $sth->fetchrow_array){

				for my $i(1..$num){ 

					if($id_parts eq $ids{$i}[0] and $ids{$i}[2] <= $qty) {

						$ids{$i}[4] = $idop;
						#next XLINE;

					}elsif($id_parts eq $ids{$i}[0] and $ids{$i}[2] > $qty){ 

						$ids{$i}[2] = 'ERROR';
						$ids{$i}[3] = "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0]). " ".trans_txt('scan_order_wreturn_qtylesser')."</li>";

					}

				} ## for num
			} ## while LINE

			## Last check for Errors
			my $okskus = 0;
			for my $i(1..$num) {

			    if ($ids{$i}[2] eq 'ERROR'){
				    $va{'message'} .=  $ids{$i}[3];
			    }elsif (!$ids{$i}[2]){
				    $va{'message'} .= "<li>UPC $ids{$i}[1] ID ".&format_sltvid($ids{$i}[0])." ".trans_txt('scan_order_upcnorder')." </li>";
			    }else{
			    	$okskus++;
			    } 

			}


			if (!$va{'message'} or ($okskus and $cfg{'wreturn_partial_errors'}) ) {


				######################################  
				######################################
				############### Return Process
				######################################  
				######################################

				my ($totqty, $sumatoria);

				######################################
				############### 1) Return Record
				###################################### 
				$sql = "INSERT INTO sl_returns SET ID_orders = '$id_orders', ID_customers = '$id_customers', Type='$rtype', generalpckgcondition='Unknown', itemsqty = '1', merAction = '$in{'meraction'}', Status = '$st_type', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
				$log .= $sql."<br>\n\n";
				my ($sth) = &Do_SQL($sql);
				my ($id_returns) = $sth->{'mysql_insertid'};
				$log .= "id_returns=".$id_returns."<br>\n";

				if ($id_returns) {

					### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
					my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
					my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';

					$log .= "acc_method=".$acc_method."<br>\n";
					$log .= "invout_order=".$invout_order."<br>\n\n";

					######################################
					############### 2) Items Record
					###################################### 

					my $str_debug; my $str_note_order;
					UPCS:for my $i(1..$num) {

				    	if ($ids{$i}[2] ne 'ERROR'){

					    	#### 0 id, 1 upc, 2 upc_loc, 3 qty, 4 id_orders_products
					    	my $id_parts = $ids{$i}[0];
					    	my $id_product = ($id_parts + 400000000);
					    	my $upc = $ids{$i}[1];
					    	my $code = $ids{$i}[2];
					    	my $quantity = $ids{$i}[3];
					    	my $id_orders_products = $ids{$i}[4];
							my $upc_location = $ids{$i}[5];
							next UPCS if (!$upc or !$id_parts or !$quantity or !$upc_location);

							my $saleprice; 
							my $cost = 0;
							my $cost_adj = 0; 
							my $pcost = 0;

							$sql = "SELECT ID_warehouses FROM sl_locations WHERE 1 AND sl_locations.UPC='$upc_location' AND Status='Active';";
							$log .= $sql."<br>\n\n";
							my ($sth) = &Do_SQL($sql);
					    	my ($id_warehouses) = $sth->fetchrow_array;

					    	$totqty += $quantity;


					      	###############################
			          		###############################
			          		###############################
			        		## 2.1) Price + Cost + PCost
							############################### tk9139055
			          		############################### re-dev@7502233301471x1
			          		############################### 9139055,9155248,9142772,9202796
							$log .= "if (!consolidated) ".$consolidated."<br>\n\n";
							
							if (!$consolidated) {

								#######################
								#######################
								####### 2.1.1) Retail W/FBI
								#######################
								#######################

								$sql = "SELECT sl_orders_parts.Cost AS Cost, SUM(sl_orders_parts.Cost) * $quantity AS TCost, sl_orders_parts.Cost_Adj FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$id_orders' AND sl_orders_products.ID_orders_products = '$id_orders_products' AND ID_parts = '$id_parts' GROUP BY ID_orders_products;";
								my ($sthd1) = &Do_SQL($sql);
								($cost, $pcost, $cost_adj) = $sthd1->fetchrow();
								$log .= "cost=".$cost."<br>\n";
			         			$log .= "pcost=".$pcost."<br>\n";
			         			$log .= "cost_adj=".$cost_adj."<br>\n\n";

								if (!$cost){

									$sql = "SELECT sku_cost.Cost AS Cost, (sku_cost.Cost * $quantity) AS TCost, sku_cost.Cost_Adj
											FROM sl_orders_products 
											LEFT JOIN sl_skus_parts ON sl_skus_parts.ID_sku_products = sl_orders_products.ID_products 
											LEFT JOIN (SELECT ID_products, Cost, Cost_Adj FROM (SELECT * FROM sl_skus_cost ORDER BY date DESC, time DESC) a GROUP BY ID_products) sku_cost ON sku_cost.ID_products=(sl_skus_parts.ID_parts+400000000)
											WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products' AND ID_parts;";
									$log .= $sql."<br>\n\n";
									my ($sthd) = &Do_SQL($sql);
									($cost, $pcost, $cost_adj) = $sthd->fetchrow();
									$log .= "cost=".$cost."<br>\n";
				         			$log .= "pcost=".$pcost."<br>\n";
				         			$log .= "cost_adj=".$cost_adj."<br>\n\n";

								}

							}else{

								#######################
								#######################
								####### 2.1.2) Wholesale
								#######################
								#######################


								# &Do_SQL("SELECT SalePrice / Quantity AS SalePrice, Cost / Quantity AS Cost, Cost AS TCost FROM sl_orders_products WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products';");
			        			$sql = "SELECT sl_orders_products.SalePrice / sl_orders_products.Quantity AS SalePrice, IF(sl_orders_parts.Cost IS NOT NULL AND sl_orders_parts.Cost > 0, sl_orders_parts.Cost, IF( sl_orders_products.Cost IS NULL, 0, sl_orders_products.Cost / sl_orders_products.Quantity )) AS Cost, sl_orders_products.Cost AS TCost, sl_orders_parts.Cost_Adj FROM sl_orders_parts INNER JOIN sl_orders_products USING(ID_orders_products) WHERE ID_orders = '$id_orders' AND ID_orders_products = '$id_orders_products';";
			        			$log .= $sql."<br>\n\n";
			        			my ($sthd) = &Do_SQL($sql);
			         			($saleprice, $cost, $pcost, $cost_adj) = $sthd->fetchrow();
			         			$log .= "saleprice=".$saleprice."<br>\n";
			         			$log .= "cost=".$cost."<br>\n";
			         			$log .= "pcost=".$pcost."<br>\n";
			         			$log .= "cost_adj=".$cost_adj."<br>\n\n";

			          		}

			          		#######################
							#######################
			          		## 2.1.3) No Cost?
							#######################
							#######################
							if (!$pcost or $pcost < 0){
			            		($cost, $cost_adj) = &load_sltvcost($id_product);
			            		$pcost = $cost * $quantity;

		            			$log .= "cost=".$cost." -> load_sltvcost($id_product)<br>\n";
			            		$log .= "pcost=".$pcost."<br>\n\n";
			          		}
			          		$cost=0 if !$cost;
			          		$cost_adj=0 if !$cost_adj;

			          		$str_note_order .= "$quantity x $id_product\n";
			          		$str_debug .= "IDO:$id_orders / IDP: $id_product / IDOP: $id_orders_products / COST: $cost / QTY:$quantity / TCOST: ".($cost * $quantity)." / IDWH: $id_warehouses / LU: $upc_location /  C:$code\n";
			          		$log .= "str_debug=".$str_debug."<br>\n\n";

			          		###############################
			          		###############################
			          		###############################
			          		## 2.2) sl_returns_upcs insert
							###############################
			          		###############################
			          		###############################
					    	$sql = "INSERT INTO sl_returns_upcs SET ID_returns = '$id_returns', ID_parts = '$id_parts', UPC = '$upc', ID_warehouses = '$id_warehouses', Location = '$code', Cost = '$cost', Cost_Adj='$cost_adj', InOrder = 'yes', Quantity = '$ids{$i}[3]', Status = 'TBD', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
					    	$log .= $sql."<br>\n\n";
					    	my ($sth) = &Do_SQL($sql);

					    	###############################
			          		###############################
			          		###############################
					    	## 2.3) Devolucion de Inventario
							###############################
			          		###############################
			          		###############################
							if ($fast_back_to_inventory) {
								$log .= "if (fast_back_to_inventory) ".$fast_back_to_inventory."<br>\n\n";

								#######################
								#######################
				          		## 2.3.1) sl_warehouses_location
								#######################
								#######################
								my($sthinv);
								$sql = "/* returns_exportartion */ SELECT ID_warehouses_location FROM sl_warehouses_location WHERE ID_warehouses = '$id_warehouses' AND ID_products = '$id_product' AND Location = '$code' AND Quantity > 0 ORDER BY Date $invout_order, Time $invout_order LIMIT 1;";
								$log .= $sql."<br>\n\n";
								my ($sthwl) = &Do_SQL($sql);
								my ($idwl) = $sthwl->fetchrow();

								if($idwl) {
									$sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + $quantity WHERE ID_warehouses_location = '$idwl' AND ID_warehouses = '$id_warehouses' AND ID_products = '$id_product';";
									$log .= $sql."<br>\n\n";
									$sthinv = &Do_SQL($sql);
								}else{
									$sql = "/* returns_exportartion */ INSERT INTO sl_warehouses_location SET ID_warehouses = '$id_warehouses', ID_products = '$id_product', Location = '$code', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users='$usr{'id_admin_users'}'";
									$log .= $sql."<br>\n\n";
									$sthinv = &Do_SQL($sql);
									&auth_logging('warehouses_location_added',$sthinv->{'mysql_insertid'});
								}
								
								&sku_logging($id_product,$id_warehouses,$code,'Return',$id_returns,'sl_returns',$quantity,$cost,$cost_adj);
								$log .= "sku_logging($id_product,$id_warehouses,$code,'Return',$id_returns,'sl_returns',$quantity)"."<br>\n\n";

								#######################
								#######################
				          		## 2.3.2) sl_skus_cost
								#######################
								#######################	
								$sql = "SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$id_warehouses' AND ID_products = $id_product AND Quantity > 0 AND Cost = '$cost' AND Date=CURDATE() LIMIT 1;";
								$log .= $sql."<br>\n\n";
								my ($sths1) = &Do_SQL($sql);
								my ($idsc) = $sths1->fetchrow();

								if($idsc){
									## Is there a record same day / same cost ?
									$sql = "/* 1 returns_exportartion */ UPDATE sl_skus_cost SET Quantity = Quantity + $quantity WHERE ID_skus_cost = $idsc;";
									$log .= $sql."<br>\n\n";
									&Do_SQL($sql);
								}else{									
									$sql = "/* returns_exportartion */ INSERT INTO sl_skus_cost SET ID_products = '$id_product', ID_purchaseorders = '$in{'id_returns'}', Tblname = 'sl_returns', Cost = '$cost', Cost_Adj = '$cost_adj', ID_warehouses = '$id_warehouses', Quantity = '$quantity', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'";
									$log .= $sql."<br>\n\n";
									my $sthsku = &Do_SQL($sql);
								 	&auth_logging('sku_cost_added',$sthsku->{'mysql_insertid'});
								}

								#######################
								#######################
				          		## 2.3.3) Movimientos Contables
								#######################
								#######################
								my @params = ($id_orders,$id_product,$pcost);
								&accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, \@params );
								$log .= "accounting_keypoints('order_skus_backtoinventory_'. $ctype .'_'. $order_type, [$id_orders,$id_product,$pcost] )"."<br>\n\n";

							}



							###############################
			          		###############################
			          		###############################
							####### 3) ## Add negative orders_products (Only Wholesale)
							###############################
			          		###############################
			          		###############################
							if ($consolidated) {

								my $tprice = $saleprice * $quantity * -1;
								my $tcost = $cost * $quantity * -1;
								my $tquantity = $quantity * -1;
								my (%tmp) = ('id_products'=>"CONCAT(LEFT(ID_products,3)+1,'000000')",'related_id_products'=>$id_product,'quantity'=>$tquantity,
										'saleprice'=>$tprice,'cost'=>$tcost,'shpdate'=>'CURDATE()','posteddate'=>'CURDATE()','upsell'=>'No','status'=>'Returned',
										'date'=>'CURDATE()','time'=>'CURTIME()', 'id_admin_users'=>$usr{'id_admin_users'});

								my $lastidp = &Do_selectinsert('sl_orders_products',"ID_orders_products = '$id_orders_products'","ORDER BY ID_orders_products DESC","LIMIT 1",%tmp);
								$log .= "lastidp=".$lastidp.qq|Do_selectinsert('sl_orders_products',"ID_orders_products = '$id_orders_products'","ORDER BY ID_orders_products DESC","LIMIT 1",tmp)|."<br>\n\n";

								$sql = "UPDATE sl_orders_products SET Tracking = '', ShpProvider = '',Tax = SalePrice * Tax_percent WHERE ID_orders_products = '$lastidp';";
								$log .= $sql."<br>\n\n";
								&Do_SQL($sql);

							}

						} ## end if  Returned to ".&load_name('sl_warehouses','ID_warehouses',$id_warehouses,'Name')."($id_warehouses) Warehouse

					} ## for
					

					###############################
	          		###############################
	          		###############################
					####### 3.1) Validar registros de upcs
					###############################
	          		###############################
	          		###############################		
	          		$sql = "SELECT COUNT(*) FROM sl_returns_upcs WHERE ID_returns = '$id_returns';";
	          		$log .= $sql."<br>\n\n";
	          		my ($sth) = &Do_SQL($sql);
	          		my ($tupcs) = $sth->fetchrow();

		          	if(!$tupcs){

		          		$va{'message'} .= "<li>". trans_txt('scan_order_noupc')."</li>";

		          	}else{


						###############################
		          		###############################
		          		###############################
						####### 4) Cerrar Return ONLY WHOLESALE (Sumatoria de lo devuelto para aplicar descuentos)
						###############################
		          		###############################
		          		###############################

						if ($consolidated) {
							$log .= "if (consolidated) ".$consolidated."<br>\n\n";

							## Sumatoria final
							$sumatoria = &orderbalance($id_orders);

							#######################
							#######################
			          		## 4.1) Movimientos Contables
							#######################
							#######################
							my @params = ($id_orders);
							&accounting_keypoints('order_skus_returned_'. $ctype .'_'. $order_type, \@params );
							$log .= "accounting_keypoints('order_skus_returned_'. $ctype .'_'. $order_type, [$id_orders] )<br>\n\n";

							my $amount_toreturn = $sumatoria > 0 ? 0 : $sumatoria;
							$log .= "amount_toreturn=".$amount_toreturn."<br>\n";
							$log .= "sumatoria=".$sumatoria."<br>\n\n";

							@params = ($id_orders,$in{'meraction'},0,$amount_toreturn);
							&accounting_keypoints('order_skus_returnsolved_'. $ctype .'_'. $order_type, \@params );
							$log .= "accounting_keypoints('order_skus_returnsolved_'. $ctype .'_'. $order_type, [$id_orders, $in{'meraction'}, 0, $amount_toreturn] )<br>\n\n";

							### Last Payment Done
				        	$sql = "SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Status = 'Approved' ORDER BY Captured = 'Yes', LENGTH(AuthCode) DESC, ID_orders_payments DESC LIMIT 1;";
				        	$log .= $sql."<br>\n\n";
				        	my ($sth2) = &Do_SQL($sql);
				        	my ($idp) = $sth2->fetchrow();


				        	#######################
							#######################
			          		## 4.2) Cancel All Pending Payments
							#######################
							#######################
				       	 	$sql = "UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = '$id_orders' AND (Captured='No' OR Captured IS NULL OR Captured='') AND (CapDate IS NULL OR CapDate='0000-00-00'); ";
				       	 	$log .= $sql."<br>\n\n";
				       	 	&Do_SQL($sql);

				        	## Products + Tax + Shipping vs Payments already done
				        	my $posteddate = "";
				        	my $statuspayments = 'Approved';
				        	$statuspayments = 'Credit' if($sumatoria<0);


				        	#######################
							#######################
			          		## 4.3) Issue a Refund?
							#######################
							#######################
				        	if($sumatoria < 0.99 * -1 or $sumatoria > 0.99){

				     			my $querypay = !$idp ? "ID_orders = '$id_orders'" : "ID_orders_payments = '$idp'";
				        		my (%tmp) = ('reason'=>$meraction,'amount'=>$sumatoria,'paymentdate'=>'CURDATE()','posteddate'=>'CURDATE()','status'=>$statuspayments,'date'=>'CURDATE()','time'=>'CURTIME()', 'id_admin_users'=>$usr{'id_admin_users'});		
								my $lastidp = &Do_selectinsert('sl_orders_payments',$querypay,"ORDER BY ID_orders_payments DESC","LIMIT 1",%tmp);
							    &auth_logging('orders_payments_added', $id_orders);
							    $in{'amount'} = $amount_toreturn;

				        	}else{
					        	$sumatoria = 0;
				       	 	}

				      		&recalc_totals($id_orders);
				      		$log .= "recalc_totals($id_orders) <br>\n\n";


							$sql = "UPDATE sl_returns SET Amount = '$sumatoria', itemsqty = '$totqty', Status = IF($sumatoria > 0,'Pending Payments','Pending Refunds') WHERE ID_returns = '$id_returns'";
							$log .= $sql."<br>\n\n";
							&Do_SQL($sql);

							delete($in{'done'});
							$va{'message'} .= "\n Return Resolved ($in{'amount'} to Refund).<!--return OK-->";

						}else{
							my $mod = $fast_back_to_inventory ? qq|with Fast Back to Inventory| : '';
							$va{'message'} .= qq|\n Return Process $mod Started (<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_returns&view=$id_returns">$id_returns</a>)|;
						}


						###############################
		          		###############################
		          		###############################
						####### 5) Nota en Return / Order
						###############################
		          		###############################
		          		###############################

						if ($str_note_order){

							$sql = "INSERT INTO sl_returns_notes SET ID_returns='$id_returns', Notes='".&filter_values($in{'note'})."',Type='Reception',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';";
							$log .= $sql."<br>\n\n";
							&Do_SQL($sql) if ($in{'note'});
				          	
				          	$sql = "INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='Return Process Started\nType:$rtype\nStatus:$st_type\n\nSKUs Returned\n$str_note_order',Type='Medium',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';";
				          	$log .= $sql."<br>\n\n";
				          	&add_order_notes_by_type($id_orders,"Return Process Started\nType:".$rtype."\nStatus:".$st_type."\n\nSKUs Returned\n".$str_note_order,"Medium");
						}

						# &Do_SQL("ROLLBACK;"); #Only Debug
						&Do_SQL("COMMIT;");

					}  ##  upcs > 0

				}else{
					$va{'message'} .= "<li>".trans_txt('scan_order_wreturn_noidreturn')." </li>";

					&Do_SQL("ROLLBACK;");
					$log .= "Errores detectados:\n";
				}

			} ## message + okskus

		}else{
			&Do_SQL("ROLLBACK;");
			$log .= "Errores detectados:\n";
		}
		
		$log .= "va{'message'}=".$va{'message'}."\n";

		## Debug only 24042015-AD
		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('enter_return', '$id_orders', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");


	} ## Action

	#&Do_SQL("update sl_skus_cost a left join (select * from (select ID_products, Cost, Date, Time from sl_skus_cost where Cost>0 order by Date DESC, Time DESC) a group by ID_products) b using (ID_products) set a.Cost=b.Cost where a.Cost=0");
	if ($ENV{'REQUEST_URI'} =~ /apps\/entershipment/){
		$va{'cgiurl'} = '/cgi-bin/common/apps/entershipment';
	}else{
		$va{'cgiurl'} = '/cgi-bin/mod/wms/admin';
	}
	
	print "Content-type: text/html\n\n";
	print &build_page('enter_return.html');
}

1;
