

#############################################################################
#############################################################################
#	Function: packing_fadd_auto
#
#	Created on: 24/02/2015  18:20:10
#
#	Author: _RB_
#
#	Modifications: 
#
#	Parameters:
#
#	Returns: Assign Inventory | Marks Orders to In Fulfillment
#
#	See Also:
#
#		/cgi-bin/mod/wms/admin.html.cgi | fn: packing_fadd_auto
#
sub packing_fadd_auto {
#############################################################################
#############################################################################

	use Data::Dumper;
	use Encode;

	# use utf8;
	print "Content-type: text/html;\n\n";
	my $this_response = 'Error: Data Not Received';
	my %all_inventory;my %skus_applied; my @ary_lines; my @orders_applied; my @orders_ostock; my @orders_pending; my $query; my $this_log; my $torders=0; my $total_inventory_assigned=0;
	
	if($in{'ostock'}){

		##
		## Clean Out of Stock Orders
		my $modsql_ptype = $in{'cod'} ? q|AND Ptype = 'COD'| : q|AND Ptype <> 'COD'|;
		&Do_SQL("START TRANSACTION;");
		&Do_SQL("UPDATE sl_orders SET StatusPrd = 'None' WHERE Status = 'Processed' AND StatusPrd = 'Out of Stock' $modsql_ptype;");
		&Do_SQL("COMMIT;");
		$this_response = 'ok';
		sleep(2);

	}elsif($in{'infulfillment'}){

		##
		## Clean In Fulfillment Orders
		my $modsql_ptype = $in{'cod'} ? q|AND Ptype = 'COD'| : q|AND Ptype <> 'COD'|;
		&Do_SQL("START TRANSACTION;");
		&Do_SQL("UPDATE sl_orders INNER JOIN sl_orders_products USING(ID_orders)
				LEFT JOIN sl_warehouses_batches_orders
				ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
				SET StatusPrd = 'None' 
				WHERE 1 AND sl_orders.Status = 'Processed' AND StatusPrd = 'In Fulfillment' AND sl_orders_products.Status = 'Active' AND sl_warehouses_batches_orders.ID_orders_products IS NULL 
				AND (ISNULL(ShpDate) OR ShpDate='0000-00-00') AND sl_orders_products.ID_products > 1000000 AND LEFT(sl_orders_products.ID_products,1) < 4 $modsql_ptype
				AND 1 > (SELECT COUNT(*) FROM sl_orders_products INNER JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)	
						WHERE sl_orders_products.ID_orders = sl_orders.ID_orders AND sl_products.DropShipment = 'Yes');");
		&Do_SQL("COMMIT;");
		$this_response = 'ok';
		sleep(3);


	}elsif($in{'data_in'}){

		$this_response = '';
		my ($id_warehouses, $these_zones, $this_exclude, $this_orderby, $filter_cod, $filter_express, $set_ostock, $this_cmd) = split(/::/, $in{'data_in'});
		print "IDW:$id_warehouses, States: $these_zones, OB:$this_orderby, COD:$filter_cod, EX:$filter_express, OS:$set_ostock, CMD:$this_cmd";
		#return;

		if(!$these_zones and $this_exclude){

			## Validate State + Exlusion 
			print "Error: No State was selected but Exclude option used";
			return;

		}

		##
		### Zones in Warehouse
		##
		$these_zones =~ s/,$//; 
		#my @zones = split(/,/, $these_zones); ## Zones Received Specifically
		my $delivery_zones = ($these_zones and !$this_exclude) ? $these_zones : &load_name('sl_warehouses', 'ID_warehouses', $id_warehouses, 'DeliveryZones'); ## All zones in Warehouse

		#print "TZ: $these_zones and !this_exclude\nDZ:$delivery_zones\n";
		my $str_exclude = $this_exclude ? 'NOT IN' : 'IN';
		my $mod_sql_cod = $filter_cod ? "AND Ptype = 'COD' "  : "AND Ptype <> 'COD' ";
		my $mod_sql_express = $filter_express ? "AND sl_orders.shp_type = 2"  : " ";
		my $mod_sql_zones = $delivery_zones ? "AND sl_orders.ID_zones IN (". $delivery_zones .") " : '';
		my $mod_sql_exclude_zones = $this_exclude ? "AND sl_orders.ID_zones NOT IN (". $these_zones .") " : '';
		
		##
		### Loading Inventory
		##
		%all_inventory = &inventory_all_auto(0, $id_warehouses, 0, 0);


		my $this_time = time();
		&Do_SQL("START TRANSACTION;");
		$query = "SELECT
						sl_orders.ID_orders
						, sl_orders.Date
					FROM
						sl_orders	
					INNER JOIN
						sl_orders_products USING(ID_orders)
					LEFT JOIN  
						sl_warehouses_batches_orders
					ON 
						sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products 
						AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Shipped','In Transit')
					WHERE
						1
						AND sl_orders.Status = 'Processed'
						AND (StatusPrd = 'None' OR StatusPrd = '')
						AND sl_orders_products.Status = 'Active' 
						AND sl_warehouses_batches_orders.ID_orders_products IS NULL 
						AND 1 > (
							SELECT 
								COUNT(*) 
							FROM 
								sl_orders_products 
							INNER JOIN 
								sl_products
							ON
								sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6)	
							WHERE
								sl_orders_products.ID_orders = sl_orders.ID_orders
								AND sl_products.DropShipment = 'Yes' 
						) 
						AND (ISNULL(ShpDate) OR ShpDate='0000-00-00')
						$mod_sql_cod 
						$mod_sql_express 
						$mod_sql_zones 
						$mod_sql_exclude_zones
						AND sl_orders_products.ID_products > 1000000
						AND LEFT(sl_orders_products.ID_products,1) < 6
					GROUP BY
						sl_orders.ID_orders	 
					ORDER BY 
						FIELD(shp_type, 2,1,3)
						, sl_orders.ID_orders $this_orderby;";
		Encode::from_to($query, 'utf8', 'iso-8859-1');

		my ($sth) = &Do_SQL($query);
		ORDERS:while(my ($id_orders, $this_date) = $sth->fetchrow()){

			++$torders;
			my $this_parts; my @skutemp; my $empty_skus=0; my $tparts=0; my $temp_status;

			my $queryp = "SELECT 
							sl_skus_parts.ID_parts
							, 400000000 + sl_skus_parts.ID_parts
							,SUM(sl_orders_products.Quantity * sl_skus_parts.Qty) AS TQty
						FROM 
							sl_orders_products 
						INNER JOIN 
							sl_skus_parts 
						ON 
							sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
						WHERE 
							ID_orders = '" . $id_orders . "' 
							AND sl_orders_products.Status = 'Active'	
						GROUP BY sl_skus_parts.ID_parts 
						ORDER BY sl_skus_parts.ID_parts;";
			my ($sth) = &Do_SQL($queryp);
			while(my ($this_id_parts, $this_sku, $this_quantity) = $sth->fetchrow()){

				++$tparts;
				$all_inventory{$this_sku}{'inventory'} = 0 if !$all_inventory{$this_sku}{'inventory'};
				$all_inventory{$this_sku}{'infulfillment'} = 0 if !$all_inventory{$this_sku}{'infulfillment'};
				$all_inventory{$this_sku}{'freeinventory'} = 0 if !$all_inventory{$this_sku}{'freeinventory'};

				$temp_status = ($temp_status !~ /Out/ and $all_inventory{$this_sku}{'freeinventory'} > 0 and ($all_inventory{$this_sku}{'freeinventory'} - $this_quantity) >= 0 ) ? 'In fulfillment' : "Out of Stock($set_ostock)";
				push(@ary_lines, "$id_orders, $this_id_parts, $all_inventory{$this_sku}{'inventory'}, $all_inventory{$this_sku}{'infulfillment'}, $all_inventory{$this_sku}{'freeinventory'}, $this_quantity," . ($all_inventory{$this_sku}{'freeinventory'} - $this_quantity) .",'$temp_status',MD5('". $this_time ."')");
				$this_parts .= qq|ID Part: $this_id_parts ;; Inventory: $all_inventory{$this_sku}{'inventory'} ;; inFulfillment: $all_inventory{$this_sku}{'infulfillment'} ;; Free: $all_inventory{$this_sku}{'freeinventory'} ;; Needed: $this_quantity ;;| . ($all_inventory{$this_sku}{'freeinventory'} - $this_quantity) .",'$temp_status'";

				if( exists($all_inventory{$this_sku}{'freeinventory'}) and $all_inventory{$this_sku}{'freeinventory'} > 0 and $all_inventory{$this_sku}{'freeinventory'} >= $this_quantity ){

					## 1) Sku has inventory | Loaded into temp array
					push(@skutemp, "$this_sku;;$this_quantity");

				}else{

					## 2) Sku has no inventory or not enough | Next Order?
					#next ORDERS if !$set_ostock;
					## 2.1) If continue then flag to clean skus hash
					$empty_skus = 1;


				}

				$this_parts .= (scalar @skutemp > 0) ? qq|Final: | . ($all_inventory{$this_sku}{'freeinventory'} - $this_quantity) .qq|<br>| : qq|Final: | . $all_inventory{$this_sku}{'freeinventory'}  .qq|<br>|;
			}

			
			if(!$tparts){

				### No Parts Found in Order
				push (@ary_lines, "$id_orders,0,0,0,0,0,0,'Pending',MD5('". $this_time ."')");
				$this_response .= qq|<br>Order: $id_orders \| $this_date<br>$this_parts Status:Pending<br>|;
				push(@orders_pending, $id_orders);

			}else{

				### Order OK, Parts Found
				
				if($empty_skus){

					## Quantity Orders not Enough | Out of Stock
					$this_response .= qq|<br>Order: $id_orders \| $this_date<br>$this_parts Status:Out of Stock($set_ostock)<br>|;
					push(@orders_ostock, $id_orders) if $set_ostock;
					undef @skutemp;

				}else{
				
					my $ts;
					for(0..$#skutemp){

						## 3) Apply decrement skutemp parts to freeinventory
						my ($sku,$qty) = split(/;;/, $skutemp[$_]);
						$all_inventory{$sku}{'freeinventory'} -= $qty;
						$all_inventory{$sku}{'infulfillment'} += $qty;

						## 3.1) Save each part+qty
						$skus_applied{$sku} += $qty;
						$total_inventory_assigned += $qty;
						
					}

					## Quantity Orders in Fulfillment
					$this_response .= qq|<br>Order: $id_orders \| $this_date<br>$this_parts Status:In Fulfillment<br>$ts<br><br>|;
					push(@orders_applied, $id_orders);

				} # else empty_skus

			} # else tparts

		} # while ORDERS

		$this_response = qq|Total_orders: $torders<br><br>$this_response<br>|;


		if($torders){

			##
			### All Notes and Logs | In Fulfillment
			##
			if(scalar @orders_applied > 0){

				my $my_ip = &get_ip;
				my $values_logs; my $values_notes;
				for(0..$#orders_applied){

					my $id_orders = $orders_applied[$_];
					$values_logs .= "(CURDATE(), CURTIME(), 'orders_updated', '". $id_orders ."', 'Application', 'sl_orders', '". $this_cmd ."', $usr{'id_admin_users'}, '". $my_ip ."'),";
					$values_notes .= "('". $id_orders ."', 'The order has been marked to : Fullfill', 'Low', 1, CURDATE(), CURTIME(), $usr{'id_admin_users'}),";

				}
				chop($values_notes);chop($values_logs);

				if($values_notes and $values_logs){

					my $query_prdst = "UPDATE sl_orders SET StatusPrd = 'In Fulfillment' WHERE ID_orders IN(". join(',', @orders_applied) .");";
					my $query_log = "INSERT INTO admin_logs (LogDate, LogTime, Message, Action, Type, tbl_name, Logcmd, ID_admin_users, IP) VALUES $values_logs;";
					my $query_note = "INSERT INTO sl_orders_notes (ID_orders, Notes, Type, ID_orders_notes_types, Date, Time, ID_admin_users) VALUES $values_notes;";
					
					&Do_SQL($query_prdst); 
					&Do_SQL($query_log); 
					&Do_SQL($query_note);
					#&add_order_notes_by_type($id_orders,"The order has been marked to : Fullfill","Low");
				}

			}


			##
			### All Notes and Logs | Out of Stock
			##
			if(scalar @orders_ostock > 0 and $set_ostock){

				my $values_logs; my $values_notes;
				for(0..$#orders_ostock){

					my $id_orders = $orders_ostock[$_];
					$values_logs .= "(CURDATE(), CURTIME(), 'orders_updated', '". $id_orders ."', 'Application', 'sl_orders', '". $this_cmd ."', $usr{'id_admin_users'}, '". $my_ip ."'),";
					$values_notes .= "('". $id_orders ."', 'The order has been marked to : Back Order', 'Low', 1, CURDATE(), CURTIME(), $usr{'id_admin_users'}),";

				}
				chop($values_notes);chop($values_logs);

				if($values_notes and $values_logs){

					my $query_prdst = "UPDATE sl_orders SET StatusPrd = 'Out of Stock' WHERE ID_orders IN(". join(',', @orders_ostock) .");";
					my $query_log = "INSERT INTO admin_logs (LogDate, LogTime, Message, Action, Type, tbl_name, Logcmd, ID_admin_users, IP) VALUES $values_logs;";
					my $query_note = "INSERT INTO sl_orders_notes (ID_orders, Notes, Type, ID_orders_notes_types, Date, Time, ID_admin_users) VALUES $values_notes;";	
					&Do_SQL($query_prdst); 
					&Do_SQL($query_log); 
					&Do_SQL($query_note);
					#&add_order_notes_by_type($id_orders,"The order has been marked to : Back Order","Low");

				}

			}


			##
			### All Notes and Logs | Pending
			##
			if(scalar @orders_pending > 0){

				my $my_ip = &get_ip;
				my $values_logs; my $values_notes;
				for(0..$#orders_applied){

					my $id_orders = $orders_pending[$_];
					$values_logs .= "(CURDATE(), CURTIME(), 'orders_updated', '". $id_orders ."', 'Application', 'sl_orders', '". $this_cmd ."', $usr{'id_admin_users'}, '". $my_ip ."'),";
					$values_notes .= "('". $id_orders ."', 'The order has been marked to : Pending', 'Low', 1, CURDATE(), CURTIME(), $usr{'id_admin_users'}),";

				}
				chop($values_notes);chop($values_logs);

				if($values_notes and $values_logs){

					my $query_prdst = "UPDATE sl_orders SET StatusPrd = 'Pending' WHERE ID_orders IN(". join(',', @orders_pending) .");";
					my $query_log = "INSERT INTO admin_logs (LogDate, LogTime, Message, Action, Type, tbl_name, Logcmd, ID_admin_users, IP) VALUES $values_logs;";
					my $query_note = "INSERT INTO sl_orders_notes (ID_orders, Notes, Type, ID_orders_notes_types, Date, Time, ID_admin_users) VALUES $values_notes;";
					&Do_SQL($query_prdst); 
					&Do_SQL($query_log); 
					&Do_SQL($query_note);
					#&add_order_notes_by_type($id_orders,"The order has been marked to : Pending","Low");
				}

			}

		}

		#&Do_SQL("ROLLBACK;");
		&Do_SQL("COMMIT;");


		## Log	
		my $query = "INSERT INTO cu_autofulfill_log(ID_autofulfill_log, ID_warehouses, ID_orders, ID_parts, Inventory, Fulfill, Free, Quantity, Final, Decision, MD5Verification, Date, Time, ID_admin_users) VALUES ";
		for(0..$#ary_lines){

			$query .= "(0, ". $id_warehouses .", ". $ary_lines[$_] .", CURDATE(), CURTIME(), ". $usr{'id_admin_users'} ."),\n" ;
			$this_log .= $ary_lines[$_] . qq|<br>|;

		}
		chomp($query); chop($query);
		$query .= ";";
		# print $query;

		if(&table_exists('cu_autofulfill_log') and scalar @ary_lines > 0){

			&Do_SQL($query);
			&Do_SQL("UPDATE cu_autofulfill_log
					INNER JOIN
					(
						SELECT ID_orders, MAX(Decision)AS decisionf FROM cu_autofulfill_log WHERE 1 AND MD5Verification = MD5('". $this_time."') GROUP BY cu_autofulfill_log.ID_orders
					)tmp USING(ID_orders)
					SET cu_autofulfill_log.Decision = decisionf
					WHERE 1
					AND MD5Verification = MD5('". $this_time."');");

		}

		##
		### Resume
		##
		$this_response = qq|<div class="good">\n
								<font size="4">All Done</font></div>\n
							<br>\n
							<font face="century gothic, arial" size="3">Total orders : |. $torders .qq|</font><br>\n
							<font color="#64a113">In Fullfilment:</font> |. scalar @orders_applied .qq| <br>\n
							<font color="#c80000">Out of Stock:</font> |. scalar @orders_ostock .qq| <br>\n
							<font color="#c80000">Pending:</font> |. scalar @orders_pending .qq| <br><br><br>\n
							<font face="century gothic, arial">Unique SKUs : |. keys(%skus_applied) .qq|</font><br>\n
							<font face="century gothic, arial">Inventory Assigned  : |. $total_inventory_assigned .qq|</font><br>\n|;
							#$query\n|;

	}

	#print $this_log;
	print $this_response;

	return;
}

1;
