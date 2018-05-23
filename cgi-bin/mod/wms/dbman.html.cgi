#!/usr/bin/perl

##########################################################
##		ADJUSTMENT
##########################################################
sub view_adjustments {
# --------------------------------------------------------
# Created on: 07/17/08 @ 14:31:22
# Author: Roberto Barcenas
# Last Modified on: 07/17/08 @ 14:31:22
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
# Last Modified RB: 11/10/08  18:02:47  -- Drop rows insted balance	
# Last Modification by JRG : 03/13/2009 : Se agrega log
# Last Modified on: 03/11/09 15:18:06
# Last Modified by: MCC C. Gabriel Varela S: Se pone WHERE ID_adjustments='$in{'id_adjustments'}'; en el update de status Denied. Observación hecha por José.
# Last Modification by JRG : 03/11/2009 : Se agrega el log
# Last Modified on: 06/08/09 15:52:18
# Last Modified by: MCC C. Gabriel Varela S: Se valida que no existan sets.

	my ($diff,$diffgral);

	if ($in{'chg_status'} eq 'Denied'){
		my ($sth) = &Do_SQL("UPDATE sl_adjustments SET Status='Denied' WHERE ID_adjustments='$in{'id_adjustments'}';");
		&auth_logging('adjustments_updated',$in{'id_adjustments'});
		$in{'status'} = 'Denied';
	}elsif ($in{'status'} eq 'New' and $in{'chg_status'} eq 'Approved' and (&check_permissions($in{'cmd'},'',''))){
		
		#Verifica si hay sets en la lista:
		#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_adjustments_items WHERE ID_adjustments='$in{'id_adjustments'}';");
		my ($sth) = &Do_SQL("SELECT COUNT(*),sum(if(Isset='Y',1,0)) as SumY
					FROM sl_adjustments_items 
					INNER JOIN sl_skus on(sl_adjustments_items.ID_products=sl_skus.ID_sku_products)
					WHERE ID_adjustments='$in{'id_adjustments'}';");
		($count,$sumy)=$sth->fetchrow_array();
		if($count> 0 and $sumy==0){
		
			my ($sth) = &Do_SQL("UPDATE sl_adjustments SET AuthBy='$usr{'id_admin_users'}',AuthDate=CURDATE(),Status='Approved' WHERE ID_adjustments='$in{'id_adjustments'}'");
			&auth_logging('adjustments_updated',$in{'id_adjustments'});
			$in{'status'} = 'Approved';
			&Do_SQL("DELETE FROM sl_warehouses_location WHERE `Quantity`=0");
			#&Do_SQL("START TRANSACTION");
			
			my ($sth) = &Do_SQL("SELECT * FROM sl_adjustments_items WHERE ID_adjustments='$in{'id_adjustments'}';");
			while ($rec = $sth->fetchrow_hashref){
				$cost = 0;
				
				##################
				################## Only if we have more than one item on inventory, we modify sl_warehouse_location
				################## 
				my ($std) = &Do_SQL("DELETE FROM sl_warehouses_location WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}'"); 
				if($rec->{'Qty'} > 0){
					my ($sthin) = &Do_SQL("INSERT INTO sl_warehouses_location SET ID_warehouses = '$rec->{'ID_warehouses'}', ID_products='$rec->{'ID_products'}', Quantity = '$rec->{'Qty'}', Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
					&auth_logging('warehouses_location_added',$sthin->{'mysql_insertid'});
				}
				
				#############
				############# Don't drop sl_skus_cost, We need it to get the average cost for a product
				## Actual Cost
				my ($sth2) = &Do_SQL("SELECT SUM(Quantity) FROM sl_skus_cost WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}' AND Quantity > 0 ;");	
				$act_cost = $sth2->fetchrow;
			
				$diffgral	=	$act_cost - $rec->{'Qty'};
				$diff = abs($diffgral);
			
				## DB > file items ; We need to delete items from DB
				if ($act_cost > $rec->{'Qty'}){
					FINAL :while($diff > 0){	
						my ($sth2) = &Do_SQL("SELECT ID_skus_cost,Quantity,Cost FROM sl_skus_cost WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products = '$rec->{'ID_products'}' AND Quantity > 0 ORDER BY Date LIMIT 1");
						($idsc,$items_qty,$cost) = $sth2->fetchrow;
				
						if($diff > $items_qty){
							my ($sth2) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = 0 WHERE ID_skus_cost = '$idsc' ;");
							&auth_logging('sku_cost_updated',$idsc);
							$diff -= $items_qty;
						}else{
							my ($sth2) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = $items_qty - $diff  WHERE ID_skus_cost = '$idsc' ;");
							&auth_logging('sku_cost_updated',$idsc);
							last FINAL;
						}
					}
				
				## DB < file items ; We need to add items to DB
				}elsif($act_cost < $rec->{'Qty'}){
					$cost = load_sltvcost($rec->{'ID_products'});
					my ($sth2) = &Do_SQL("INSERT INTO sl_skus_cost SET ID_warehouses='$rec->{'ID_warehouses'}' ,ID_products='$rec->{'ID_products'}',ID_purchaseorders='$rec->{'ID_adjustments'}',Tblname='sl_adjustments',Quantity=$diff,Cost='$cost',Date=CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}' ;");
					&auth_logging('sku_cost_added',$sth2->{'mysql_insertid'});
				}
				my ($sth2) = &Do_SQL("UPDATE sl_skus_cost SET Quantity = 0 WHERE ID_warehouses='$rec->{'ID_warehouses'}' AND ID_products='$rec->{'ID_products'}' AND Quantity < 0 ;");
				my ($sth2) = &Do_SQL("UPDATE sl_adjustments_items SET Price = '$cost', Adj=$diffgral*-1 WHERE  ID_adjustments_items ='$rec->{'ID_adjustments_items'}'");
			}
		}else{
				$va{'message'} = 'You can not change the status to approve until update adjustment. Probably there are sets in the list too.';
		}
		&auth_logging('adjustment_done',$in{'id_adjustments'});
	}elsif($in{'status'} eq 'New' and $in{'chg_status'} eq 'Approved'){
		$va{'message'} = 'Only users with developer rights can execute the adjustment';
	}
	
	if ($in{'status'} eq 'New'){
		$va{'change_status'} = qq|&nbsp;&nbsp; 
			<a href="#"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Approve' alt='' border='0' onClick='if(confirm("Do you want to APPROVE these adjustment?")){trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_adjustments]&tab=1&chg_status=Approved")}'></a>
			&nbsp;&nbsp;
			<a href="#"><img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Deny' alt='' border='0' onClick='if(confirm("Do you want to DENY these adjustments?")){trjump("/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_adjustments]&tab=1&chg_status=Denied")}'></a>|;
	}
}


##########################################################
##		PRODUCTS	  ##
##########################################################
sub list_products {
# --------------------------------------------------------
	$in{'show_only_list'} = 1;
}

sub view_products {
# --------------------------------------------------------
	$va{'id_products'} = &format_sltvid($in{'id_products'});	
}


sub advsearch_products {
# --------------------------------------------------------
	if ($in{'upc'}){
		my ($sth) = &Do_SQL("SELECT ID_products FROM sl_skus WHERE UPC='$in{'upc'}'");
		$in{'id_products'} = $sth->fetchrow;
		if ($in{'id_products'}>0){
			$in{'tab'}=3;
			$in{'db'} = 'sl_parts';
			$in{'cmd'} = 'parts';
			$in{'id_parts'}=$in{'id_products'};
			$va{'id_parts'} = &format_sltvid(400000000+$in{'id_parts'});
			&load_cfg('sl_parts');
			return &query('sl_parts');
		}else{
			return ();
		}
	}elsif($in{'sl_products_categories.id_categories'}){
		###querydb2($db1,$db2,$jqry,$header_fields)
		my ($hfields);
		$in{'sl_products_categories.sx'}=1;
		$in{'st'} = 'AND';
		for (0..$#headerfields){
			$hfields .= "sl_products.$headerfields[$_],";
		} 
		chop($hfields);
		return &querydb2('sl_products','sl_products_categories','sl_products.ID_products=sl_products_categories.ID_products',$hfields);
	}else{
		my ($fname);
		for (0..$#db_cols){
			$fname = lc($db_cols[$_]);
			($in{'sl_products.'.$fname}) and ($in{$fname} = $in{'sl_products.'.$fname});
			delete($in{'sl_products.'.$fname});
		}
		return &query('sl_products');
	}	
}



#############################################################################
#############################################################################
# Function: view_warehouses_batches
#
# Es: manejo de acciones de la aplicacion warehouses_batches
# En: 
#
# Created on: 20/10/2012 9:45:00
#
# Author: Pablo Hdez.
#
# Modifications:
#
# Parameters:
#
# - id_warehouses_batches : ID_warehouses_batches
#
# Returns:
#
# - multiples valores dependiendo del caso
#
# See Also:
#
#  Todo:
#
sub view_warehouses_batches{
#############################################################################
#############################################################################	
	my $ordstatus = "'Processed'";
	my $prdstatus = "'In Fulfillment'";
	my (@c) = split(/,/,$cfg{'srcolors'});
	$va{'idcounts'} ="";	 
	if($in{'ordersselected'} eq ''){
		$in{'ordersselected'} = 0;
	}
	    
    if($in{'id_warehouses'}){
	    my $wname = &load_name('sl_warehouses','ID_warehouses',int($in{'id_warehouses'}),'Name');
	    $va{'warehouses_name'}=$wname;
    }
	
	###### Drop Order From Batch
	if($in{'drop'}) {
		my $id_orders = int($in{'drop'});
		my $id_warehouses_batches = int($in{'view'});
		my $query = "UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products 
					USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Cancelled' 
					WHERE ID_warehouses_batches = '$id_warehouses_batches' AND ID_orders = '$id_orders'
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');";

		my ($sth) = &Do_SQL($query);
		if ($sth->rows()) {

			my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchdropped')." $id_orders',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$id_warehouses_batches';");

			&auth_logging('order_batchdropped',$id_warehouses_batches);
			$va{'message'} = &trans_txt('order_batchdropped')." $id_orders ";

		}

	}

	##########################################
	############ Change Status
	##########################################
	if ($in{'chg_status'} and $in{'chg_status'} =~/Processed|Cancelled/ and $in{'status'} =~ /Assigned|New/ ){
		if(&check_permissions($in{'cmd'}.'chgstatus','','')){ 

			if ($in{'chg_status'} eq 'Processed'){
				my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Processed' WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'");
				$in{'status'} = 'Processed';
				my $sth = &Do_SQL("SELECT sl_orders.ID_orders, PType
						   FROM sl_warehouses_batches_orders
						   LEFT JOIN sl_orders_products
						   ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
						   LEFT JOIN sl_orders
						   ON sl_orders.ID_orders=sl_orders_products.ID_orders
						   WHERE /*sl_orders.Ptype='COD' AND*/ ID_warehouses_batches = '$in{'id_warehouses_batches'}'
						   AND sl_warehouses_batches_orders.Status='In Fulfillment'
						   GROUP BY sl_orders.ID_orders");
				while (my ($id_ord,$pt) = $sth->fetchrow){
					($pt eq 'COD') and ( &Do_SQL("UPDATE sl_orders SET ID_warehouses ='$in{'id_warehouses'}' WHERE ID_orders='$id_ord';") );
					## Agregar Nota??
					($pt eq 'COD') and (my $sth2 = &Do_SQL("INSERT IGNORE INTO sl_orders_datecod SET ID_orders='$id_ord', ID_warehouses=$in{'id_warehouses'}, DateCOD=CURDATE(),Status='Active',Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';") );
					my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_orders_notes SET Notes='".&trans_txt('order_batchadded')." $in{'id_warehouses_batches'} ',Type='High', ID_orders_notes_types=3,Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders = '$id_ord';");
					$in{'db'} = 'sl_orders';
					&auth_logging('order_batchadded', $id_ord);

				}
			}else{
				my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='New' WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'");
				$in{'status'} = 'New';
				my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status='Cancelled' WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'");	
			}
			$in{'db'} = 'sl_warehouses_batches';
			&auth_logging('status_changed_' . $in{'chg_status'},$in{'id_warehouses_batches'});
			$va{'message'} =  &trans_txt('status_changed_'.$in{'chg_status'});
		}else{
			$va{'message'} =  &trans_txt('not_authorized');
		}

	}
	

	if($in{'ordersselected'} eq ''){
		$in{'ordersselected'}= 0;
	}
	
	########################################
	####Change Status Button
	########################################
	$va{'changestatus'} = &trans_txt('change_status')." &nbsp; ";	
    if ($in{'status'} eq "Processed"){
	    $va{'changestatus'}='';
    }elsif($in{'status'} =~ /Assigned|New/){
    	$va{'changestatus'} .= qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_warehouses_batches]&chg_status=Processed">Processed</a>&nbsp;&nbsp; / &nbsp;&nbsp;
								<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_warehouses_batches]&chg_status=Cancelled">Cancelled</a>|;
	}else{
		$va{'changestatus'}='';
	}


	##########################################
	##########################################
	############
	############ Batch Actions
	############
	##########################################
	##########################################

	if($in{'action'}){


		if($in{'rx'} and &check_permissions('warehouses_batches_orders_reasign','','')){

			

			##########################################
			##########################################
			############
			############ Products in Batch Reasign
			############
			##########################################
			##########################################

			my $id_orders = int($in{'rx'});

			if($id_orders) {
				###
				### 1) Status / Date for this Order
				my ($sth1) = &Do_SQL("SELECT 
										sl_warehouses_batches_orders.ScanDate
										, sl_warehouses_batches_orders.Status
										, sl_warehouses_batches_orders.Date
										, sl_warehouses_batches_orders.Time 
									FROM sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products) 
									WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'
									AND ID_orders = '$id_orders' ORDER BY LEFT(ID_products,1) LIMIT 1;");
				my ($s_date, $r_st, $r_date, $r_time) = $sth1->fetchrow();


				###
				### 2) Deactivate othe batch products
				my ($sth2) = &Do_SQL("UPDATE `sl_orders_products` 
									INNER JOIN sl_warehouses_batches_orders
									USING ( ID_orders_products ) 
									SET sl_warehouses_batches_orders.Status = 'Cancelled'
									WHERE ID_orders = '$id_orders' 
									AND ID_warehouses_batches <> '$in{'id_warehouses_batches'}'
									AND sl_warehouses_batches_orders.Status NOT IN('Returned','Error');");
				my ($total) = $sth2->rows();

				###
				### 3) Reasign Products
				if($total > 0) {

					my ($sth3) = &Do_SQL("SELECT ID_orders_products,'$usr{'id_admin_users'}'
										FROM sl_orders_products
										WHERE ID_orders = '$id_orders' AND Status NOT IN ('Returned','Order Cancelled','Inactive','Exchange','ReShip');");
					while( my($a, $b) = $sth3->fetchrow()){

						&Do_SQL("INSERT IGNORE INTO sl_warehouses_batches_orders SET 
									ID_warehouses_batches	 = '$in{'id_warehouses_batches'}'
									, ID_orders_products = '$a'
									, Retries = 0
									, ScanDate = '$s_date'
									, Status = '$r_st'
									, Date = '$r_date'
									, Time = '$r_time'
									, ID_admin_users = '$b'
									;");
					
					}
					&auth_logging('order_batchreasigned', $in{'id_warehouses_batches'});

				}

			}

		}



		if( ($in{'c'} or $in{'rs'}) and &check_permissions('warehouses_batches_certify','','') ) {


			##########################################
			##########################################
			############
			############ Certify / ReShip Batch
			############
			##########################################
			##########################################

			my $x = 0;
			my $total_reshipped = 0;

			###
			### 1) Order Validation
			###
			my ($sth) = &Do_SQL("SELECT ID_orders, PType
				 				 FROM sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products)
				 				 INNER JOIN sl_orders USING(ID_orders)
				 				WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'
				 				GROUP BY ID_orders;");
			while(my ($id_orders, $ptype) = $sth->fetchrow()) {


				my $query = "SELECT 
								COUNT(tmp.ID_orders_products)
								, GROUP_CONCAT(ID_orders_products)AS IDS
								, SUM(ToReship)AS ToReship
							FROM 
							sl_warehouses_batches_orders INNER JOIN
							(
								SELECT 
									ID_orders_products
									, IF(sl_orders_products.Status = 'ReShip',1,0)AS ToReship
								FROM sl_orders_products INNER JOIN sl_orders_parts USING (ID_orders_products)
								WHERE ID_orders = '$id_orders'
								GROUP BY ID_orders_products
							)tmp
							USING(ID_orders_products)
							WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'
							AND Status IN('In Fulfillment','Shipped','In Transit','Returned');";
				my ($sth2) = &Do_SQL($query);
				my ($tprods, $id_orders_products_grouped, $treship) = $sth2->fetchrow();
				$x += $tprods;

				if($in{'c'}) {

					##########
					########## Certify
					##########

					if(!$tprods) {

						#### Agregar Nota a orden/remesa de desasignacion + Quitar In Fulfillment? \n".&filter_values($query)."
						my ($sth2) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchdropped')." $id_orders', Type='High', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}', ID_warehouses_batches = '$in{'id_warehouses_batches'}';");

						$in{'db'} = 'sl_orders';
						
						## 24042015-AD-Se omite nota y log porque causa confusion a la operacion
						## Nota orden eliminada del batch
						# my ($sth3) = &Do_SQL("INSERT INTO sl_orders_notes SET Notes='".&trans_txt('order_batchdropped')." $in{'id_warehouses_batches'} ',Type='High',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_orders = '$id_orders';");
						# &auth_logging('order_batchdropped', $id_orders);

						## Quitar In Fulfillment
						my ($sth4) = &Do_SQL("UPDATE sl_orders SET StatusPrd = 'None' WHERE ID_orders = '$id_orders';");

						## Aseguramos sacarla de remesa
						my ($sth5) = &Do_SQL("UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Cancelled' WHERE ID_orders = '$id_orders' AND ID_warehouses_batches = '$in{'id_warehouses_batches'}';");

					}else{

						## Aseguramos status de la linea
						&Do_SQL("UPDATE sl_orders_products INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = IF('$ptype' = 'COD', 'In Transit','Shipped') WHERE ID_orders = '$id_orders' AND sl_warehouses_batches_orders.Status = 'In Fulfillment';");

					}

				}elsif($in{'rs'} and $treship){

					##########
					########## ReShip
					##########

					### 1) ShpDate Update
					my ($sthrs) = &Do_SQL("UPDATE sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) SET sl_orders_products.ShpDate = CURDATE(), sl_orders_parts.ShpDate = CURDATE() WHERE ID_orders_products IN ($id_orders_products_grouped) AND sl_orders_products.Status = 'ReShip';");
					$total_reshipped += $sthrs->rows();

					### 2) Order Status / Order ShpDate Note
					&Do_SQL("UPDATE sl_orders SET Status = 'Shipped', StatusPrd = 'None' WHERE ID_orders = '$id_orders';");
					&add_order_notes_by_type($id_orders, &trans_txt('order_batchreshipped')." $in{'id_warehouses_batches'}" ,"Reenviada");
					&auth_logging('order_batchreshipped', $id_orders);

					### 3) Batch Line Sent
					&Do_SQL("UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Shipped' WHERE sl_orders_products.ID_orders_products IN ($id_orders_products_grouped) AND sl_orders_products.Status = 'ReShip' AND ID_warehouses_batches = '$in{'id_warehouses_batches'}';");

					### 4) Return PackingList Done / Return ShpDate Note
					my ($sth) = &Do_SQL("SELECT ID_returns FROM sl_returns WHERE ID_orders = '$id_orders' AND merAction = 'ReShip' AND Status = 'Resolved' AND PackingListStatus <> 'Done';");
					while(my ($id_returns) = $sth->fetchrow()){

						&Do_SQL("INSERT INTO sl_returns_notes SET ID_returns = '$id_returns', Notes='".&trans_txt('order_batchreshipped')." $in{'id_warehouses_batches'}',Type='High',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");
						&Do_SQL("UPDATE sl_returns SET PackingListStatus = 'Done' WHERE ID_returns = '$id_returns';");

					}

				}
			
			} # While order


			if($in{'c'}){

				###
				### 3) Batch To Void?
				###
				(!$x) and ($in{'status'} = 'Void') and &Do_SQL("UPDATE sl_warehouses_batches SET Status='Void' WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}';");


				###
				### 4) Batch Certified
				###
				my ($sth7) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('warehouses_batches_certified')."', Type='Certified', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}', ID_warehouses_batches = '$in{'id_warehouses_batches'}';");

			}elsif($in{'rs'} and $total_reshipped){

				###
				### 4) Batch ReShip
				###	
				my ($sth7) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('warehouses_batches_reship_done')."', Type='Medium', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}', ID_warehouses_batches = '$in{'id_warehouses_batches'}';");
				$va{'message'} = &trans_txt('done');

			}

		} # $in{c} or $in{rs}

	} # if action


	if($in{'status'} =~ /Processed|In Transit|Shipped/) {

		###
		### Certify Orders in Batch?
		###		
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches_notes WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}' AND Notes ='".&trans_txt('warehouses_batches_certified')."';");
		my ($t) = $sth->fetchrow();
		(!$t) and (&check_permissions('warehouses_batches_certify','','')) and ($va{'certifybatch'} = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_warehouses_batches]&action=1&c=1"><img src="[va_imgurl]/[ur_pref_style]/b_packinglist.gif" border="0"></a>|);

		###
		### ReShip Orders in Batch?
		###
		my $query = "SELECT 
						COUNT(*)
					FROM sl_orders_products
					 INNER JOIN
					(
						SELECT 
							ID_orders_products
						FROM sl_warehouses_batches_orders 
						WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}'
						AND Status IN('In Fulfillment','Shipped','In Transit')
						GROUP BY ID_orders_products
					)tmp
					USING(ID_orders_products)
					WHERE Status = 'ReShip';";
		my ($sth2) = &Do_SQL($query);
		my ($tr) = $sth2->fetchrow();
		my ($sth3) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches_notes WHERE ID_warehouses_batches = '$in{'id_warehouses_batches'}' AND Notes ='".&trans_txt('warehouses_batches_reship_done')."';");
		my ($tn) = $sth3->fetchrow();
		($tr and !$tn) and (&check_permissions('warehouses_batches_certify','','')) and ($va{'reshipbatch'} = qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_warehouses_batches]&action=1&rs=1"><img src="[va_imgurl]/[ur_pref_style]/b_reship.gif" border="0" title="ReShip Orders To Transit"></a>|);


		###
		### Conciliate Orders?
		###
		($in{'status'} eq 'In Transit') and (&check_permissions('warehouses_batches_conciliate','','')) and ($va{'conciliatebatch'} = qq|<a href="/cgi-bin/mod/$usr{'application'}/admin?cmd=[in_cmd]_conciliate&view=[in_id_warehouses_batches]"><img src="[va_imgurl]/[ur_pref_style]/b_toreview_payment.gif" border="0"></a>|);		
		
	}


    
    ###Warehouses string
    my $Query = "SELECT ID_warehouses, Name FROM sl_warehouses WHERE Type IN('Virtual','Outsource') AND Status='Active' AND ID_warehouses NOT IN(".$in{'id_warehouses'}.")";
    $sth = &Do_SQL($Query);
	while ($rec = $sth->fetchrow_hashref){
		$va{'wh_optionsdet'} .= qq|'$rec->{'ID_warehouses'}':'$rec->{'ID_warehouses'} -- $rec->{'Name'}',|;
	}
	chop($va{'wh_optionsdet'});
	$va{'wh_options'} = "options:{".$va{'wh_optionsdet'}."}";    
	
	####Change option
	if($so =~ /Assigned|New/){
		$va{'chg_remesa'} = qq|<span id="span_chg_wh">
					    		<img style="cursor:pointer;" title="Click to change warehouse" src="/sitimages/default/b_edit.png" id="btn_chg_wh">
					    	</span>|;
	}
	

	if($in{'id_warehouses'} eq '' && $in{'id_warehouses_batches'} ){
		my $sth = &Do_SQL("SELECT ID_warehouses  FROM sl_warehouses_batches WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'}));
		$in{'id_warehouses'} = $sth->fetchrow;
	}


	################################################
	################################################
	################################################
	################################################
	###########
	########### Impresion
	###########
	################################################
	################################################
	################################################
	################################################


	### Para formatos 5 y 6, mandamos llamar al print de orders
	warehouses_batches_rewrite_print_f5();
	warehouses_batches_rewrite_print_f6();
	warehouses_batches_rewrite_print_f7();
	warehouses_batches_rewrite_print_f9();

	my (%tmpord);
	if ($in{'toprint'}){

		my $fn = 'warehouses_batches_execute_print_f' . $in{'f'};
		#&cgierr($fn);
		if( defined &$fn ) {
			&$fn();
		}


	}


	################################################
	################################################
	################################################
	################################################
	###########
	########### Exportacion
	###########
	################################################
	################################################
	################################################
	################################################

	$va{'export_perm'} = &check_permissions('warehouses_batches','_export','');	
	if($in{'export'}){

		my $fn = 'warehouses_batches_export';
		#&cgierr($fn);
		if( defined &$fn ) {
			&$fn();
			exit;
		}

	}

	
	
}


#############################################################################
#############################################################################
# Function: validate_warehouses_batches
#
# Es: valida si existe el warehouse seleccionado
# En: 
#
# Created on: 21/10/2012 11:00:00
#
# Author: Pablo Hdez.
#
# Modifications:
#
# Parameters:
#
# - id_warehouses : ID_warehouses
#
# Returns:
#
# - err : $err, numero de errores encontrados
#
# See Also:
#
#  Todo:
#
sub validate_warehouses_batches{
#############################################################################
#############################################################################

	my ($err);

	if($in{'id_warehouses'}){
		my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses=".int($in{'id_warehouses'}));    
	    if ($sth->fetchrow == 0){	
			$va{'message'} = &trans_txt('invalid');
			$error{'id_warehouses'} = &trans_txt('required');
	    	++$err;
	    }

	    my $sth3 = &Do_SQL("SELECT ID_warehouses_batches FROM sl_warehouses_batches WHERE ID_warehouses=".int($in{'id_warehouses'})." AND Status != 'Sent' ORDER BY ID_warehouses_batches LIMIT 1;");    
	    $in{'id_warehouses_batches'} = $sth3->fetchrow();

	    if($in{'id_warehouses_batches'}) {
	    	++$err;
	    	$va{'towh'} = qq|<script language="javascript" type="text/javascript">self.location = '/cgi-bin/mod/[ur_application]/dbman?cmd=warehouses_batches&view=$in{'id_warehouses_batches'}';</script>|;
	    } 
	 $in{'status'} = 'New'; 

	}
	return $err;
}

#############################################################################
#############################################################################
# Function: summary_warehouses_batches
#
# Es: Resumen del batch enviado
# En: 
#
# Created on: 18/02/2013
#
# Author: Enrqiue Pena
#
# Modifications:
#
# Parameters:
#
# - id_warehouses : ID_warehouses
#
# Returns:
#
# See Also:
#
#  Todo:
#
sub summary_warehouses_batches{
#############################################################################
#############################################################################
	#my ($query) = @_;
	my ($total_d,$total_dc,$total_p,$total_pc,$total_bck,$total_bckc,$total,$status,$total_order) ;	
	my ($sth2) = &Do_SQL("SELECT sl_orders_products.ID_orders, sl_orders.Status, sl_orders.Ptype, 
				sl_orders.OrderNet,sl_orders.OrderDisc,sl_orders.OrderShp,sl_orders.OrderTax
				FROM  sl_warehouses_batches_orders
				INNER JOIN sl_warehouses_batches ON  sl_warehouses_batches.ID_warehouses_batches = sl_warehouses_batches_orders.ID_warehouses_batches
				INNER JOIN sl_orders_products    ON  sl_orders_products.ID_orders_products = sl_warehouses_batches_orders.ID_orders_products
				INNER JOIN sl_orders 		 ON  sl_orders.ID_orders = sl_orders_products.ID_orders
				WHERE sl_warehouses_batches.ID_warehouses                = $in{'id_warehouses'}
				AND   sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}
				AND   sl_warehouses_batches.Status = 'Sent'
				GROUP BY sl_orders_products.ID_orders");
	while ($rec = $sth2->fetchrow_hashref){
		#$total_order =  (($rec->{'OrderNet'}+$rec->{'OrderShp'}) - ($rec->{'OrderDisc'}) )+($rec->{'OrderNet'}*$rec->{'OrderTax'});

		%tmpord = &get_record('ID_orders',$rec->{'ID_orders'},'sl_orders');
		$id_customer = &load_db_names('sl_orders','ID_orders',$rec->{'ID_orders'},"[ID_customers]");
		$customer    = &load_db_names('sl_customers','ID_customers',$id_customer,"[Lastname1] [FirstName]");

		my ($sth3) = &Do_SQL("SELECT IsSet,sl_orders_products.* 
					FROM sl_orders_products 
					INNER JOIN sl_warehouses_batches_orders 
						ON sl_warehouses_batches_orders.ID_orders_products = sl_orders_products.ID_orders_products
					LEFT JOIN sl_skus 
					       ON sl_orders_products.ID_products = sl_skus.ID_sku_products
					WHERE ID_orders = $rec->{'ID_orders'}
					  AND sl_warehouses_batches_orders.ID_warehouses_batches = $in{'id_warehouses_batches'}
					  AND sl_orders_products.Status='Active';");		
		while($rprod = $sth3->fetchrow_hashref()){
			$sumprod+=$rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)!= 6;
			$sumser+=$rprod->{'SalePrice'} if substr($rprod->{'ID_products'},0,1)== 6;
			$sumtax+=$rprod->{'Tax'};
			$sumdisc+= $rprod->{'Discount'}*-1;
			$sumshipp+= $rprod->{'Shipping'};
		
			$items++ if (substr($rprod->{'ID_products'},0,1) != 6 and $rprod->{'IsSet'}ne'Y');
			$item = load_name('sl_products','ID_products',substr($rprod->{'ID_products'},3),"Name") if substr($rprod->{'ID_products'},0,1)!= 6;
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
			
		$total_order = 	$sumprod+$sumtax+$sumser+$sumshipp+$sumdisc;	
				
		if($rec->{'Ptype'}eq'COD'){
			if($rec->{'Status'}eq'Processed'){
				$total_d += $total_order;
				$total_dc++; 
				$va{'status'} = qq| style='font-size:12px;font-weight:bold;color:red'> Pendiente|;
			}elsif($rec->{'Status'}eq'Shipped'){
				$total_p += $total_order;
				$total_pc++;
				$va{'status'}= qq| style='font-size:12px;font-weight:bold;color:green'> Pagada|;
			}elsif($rec->{'Status'}eq'Cancelled'){
				$total_bck += $total_order;
				$total_bckc++;
				$va{'status'}= qq| style='font-size:12px;font-weight:bold;color:blue'>  Devuelta|;
			}
		}elsif($rec->{'Ptype'}eq'Credit-Card'){
			$total_p += $total_order;
			$total_pc++;
			$va{'status'}= qq| style='font-size:12px;font-weight:bold;color:green'> Pagada|;
		}
		
		$total += $total_order;				
				
		$va{'searchresults2'} .= "<table border='0' width='100%' algin='center' style='border:1px solid;font-size:9px;'>
					<tr>
						<td align='left' style='font-size:10px;'><strong>Order</strong></td><td style='font-size:10px;'>$rec->{'ID_orders'}</td>
							<td align='right' colspan='4' $va{'status'}</td>
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
	
	my ($output) = qq| 
			<fieldset><legend>Resumen:</legend>
			<table border="0" cellspacing="0" cellpadding="2" width="100%">
				<tr class='menu_bar_title'>
					<td align='center' ></td>
					<td align='center' >No. Orders</td>
					<td align='center' >Total Orders</td>
				</tr>
				<tr style='font-size:12px;font-weight:bold;color:green'>
					<td >Pagados</td>
					<td align='center' >|.&format_number($total_pc).qq|</td>
					<td align='center' >|.format_price($total_p).qq|</td>
				</tr>
				<tr style='font-size:12px;font-weight:bold;color:blue'>
					<td >Devueltos</td>
					<td align='center' >|.&format_number($total_bckc).qq|</td>
					<td align='center' >|.format_price($total_bck).qq|</td>
				</tr>
				<tr style='font-size:12px;font-weight:bold;color:red'>
					<td>Pendientes</td>
					<td align='center' >|.&format_number($total_dc).qq|</td>
					<td align='center' >|.format_price($total_d).qq|</td>
				</tr>
				

				<tr class='menu_bar_title'>
					<td>Total</td>
					<td align='center' >|.&format_number($total_bckc+$total_dc+$total_pc).qq|</td>
					<td align='center' >|.format_price($total).qq|</td>
				</tr>				
			</table></fieldset> &nbsp; |;
	return $output.$va{'searchresults2'};
}


#############################################################################
#############################################################################
# Function: loaddefault_mer_parts_productions
#
# Es: Valida los datos de un registro de produccion de skus
# En: 
#
# Created on: 18/02/2013
#
# Author: RB
#
# Modifications:
# 
# 19/03/2015 ISC Alejandro Diaz se sustituye funcion validate_mer_parts_productions -> loaddefault_mer_parts_productions y se corrige filtro de busqueda por status
#
# Parameters:
#
# - %in hash
#
# Returns:
#
# See Also:
#
#  Todo:
#
sub loaddefault_mer_parts_productions{
#############################################################################
#############################################################################

	$in{'status'} = 'New' if $in{'add'};

}


#############################################################################
#############################################################################
# Function: view_mer_parts_productions
#
# Es: Operaciones de un registro de produccion de skus
# En: 
#
# Created on: 18/02/2013
#
# Author: _RB_
#
# Modifications:
#	-2013/07/18 _RB_: Se agrega validacion de al menos un elemento en In y uno en  Out
#	-2013/07/24 _RB_: Se agrega &filter_values() en los nombres de los skus
#
# Parameters:
#
# - %in hash
#
# Returns:
#
# See Also:
#
#  Todo:
#
sub view_mer_parts_productions{
#############################################################################
#############################################################################
	my $log = "DEBUG view_mer_parts_productions\n\n<br>";
	## Change Status
	if ($in{'chgstatus'} and &check_permissions('sl_parts_productions_apply','','')) {

		#&Do_SQL("START TRANSACTION");
		$log .= "START TRANSACTION\n\n<br>";
		
		delete($va{'message'});
		$sql = "SELECT COUNT(*) FROM sl_parts_productions WHERE ID_parts_productions = '$in{'id_parts_productions'}' AND Status != 'New';";
		$log .= $sql."\n\n<br>";
		my ($sth) = &Do_SQL($sql);
		my ($t) = $sth->fetchrow();

		if ($in{'chgstatus'} eq 'Void' and !$t) {

			###############################
			###############################
			######
			###### Cambio a VOID
			######
			###############################
			###############################
			&Do_SQL("UPDATE sl_parts_productions SET Status = 'Void' WHERE ID_parts_productions = '$in{'id_parts_productions'}';");
			&auth_logging('mer_parts_productions_void', $in{'id_parts_productions'});
			$in{'status'} = $in{'chgstatus'};

		}elsif ($in{'chgstatus'} eq 'Processed' and !$t) {

			### Se valida que no exista una transaccion activa sobre el mismo proceso
        	if( !&transaction_validate($in{'cmd'}, $in{'id_parts_productions'}, 'check') ){

        		### Se bloquea la transaccion para evitar duplicidad
        		my $id_transaction = &transaction_validate($in{'cmd'}, $in{'id_parts_productions'}, 'insert');

				###############################
				###############################
				######
				###### Cambio a Processed
				######
				###############################
				###############################
				&Do_SQL("START TRANSACTION");
				delete($va{'message'});
				my $ptype = $in{'type'};
				#my $tcost=0;

				###
				### Validation
				###
				$sql = "SELECT SUM(IF(In_out = 'in',1,0)), SUM(IF(In_out = 'out',1,0)), SUM(IF(In_out = 'in', Qty, 0)), SUM(IF(In_out = 'out', Qty, 0)) 
						FROM sl_parts_productions_items 
						WHERE ID_parts_productions = '$in{'id_parts_productions'}' ;";
				$log .= $sql."\n\n<br>";
				my ($sth) = &Do_SQL($sql);
				my ($tot_in, $tot_out, $total_qty_in, $total_qty_out) = $sth->fetchrow();
				$log .= "tot_in=".$tot_in."\n\n<br>";
				$log .= "tot_out=".$tot_out."\n\n<br>";

				if (!$tot_in or !$tot_out){
					$va{'message'} = &trans_txt('reqfields_short');
				}


				my $tpct = 0;
				my @ary_items_in;
				my @ary_items_out;
				if ($tot_in > 0 and $tot_out > 0){

					if ( lc($in{'type'}) eq 'implode'){

						############
						############
						### Implode Validation
						############
						############				
						
						$factor = ($total_qty_in % $total_qty_out);
						if( $factor != 0 ){
							$va{'message'} .= &trans_txt('mer_parts_productions_implode_qtyout_invalid');
						}

					}

					############
					############
					### Location Quantity
					############
					############
					$sql = "SELECT ID_products, Location, Qty, In_out, Pct / 100
	                FROM sl_parts_productions_items 
	                WHERE ID_parts_productions = '$in{'id_parts_productions'}' 
	                ORDER BY In_out,Pct,ID_parts_productions_items;";
					$log .= $sql."\n\n<br>";
					my ($sth) = &Do_SQL($sql);
					ITEMS:while (my($id_parts, $location, $qty, $type, $pct) = $sth->fetchrow()) {
				
						if($type eq 'in'){
							$sql = "SELECT GROUP_CONCAT(ID_warehouses_location), SUM(Quantity) Qty
									FROM sl_warehouses_location
									WHERE ID_warehouses = '$in{'id_warehouses'}'
										AND ID_products = '$id_parts' 
										AND Location = '$location' 
										AND Quantity > 0
									Group by ID_products, ID_warehouses, Location
									HAVING Qty >= '$qty'
									LIMIT 1;";
						}else{
							$sql = "SELECT ID_warehouses_location, Quantity
							        FROM sl_warehouses_location
							        WHERE ID_warehouses = '$in{'id_warehouses'}'
							        	AND ID_products = '$id_parts' 
							        	AND Location = '$location' 
							        	AND Quantity >= '$qty' 
							        ORDER BY Date LIMIT 1;";
						}
						$log .= $sql."\n\n<br>";
						my ($sth) = &Do_SQL($sql);

						my ($idwl, $wqty) = $sth->fetchrow();
						$idwl = 0 if !$idwl;

						if ($type eq 'in' and ($wqty < $qty or !$idwl) ) {
							$va{'message'} .= &trans_txt('mer_parts_productions_items_insufficient') . qq| $id_parts ($wqty < $qty)<br>|;
							next ITEMS;
						}elsif ($type eq 'out'){
							$tpct += $pct if $ptype eq 'Explode';
							$sql = "SELECT COUNT(*) FROM sl_locations WHERE ID_warehouses = '$in{id_warehouses}' AND Code = '$location';";
							$log .= $sql."\n\n<br>";
							my ($sth) = &Do_SQL($sql);
							my ($t) = $sth->fetchrow();
							if (!$t){
								$va{'message'} .= &trans_txt('opr_locations_unknown') . qq| $location<br>|;
								next ITEMS;
							}
						}

						#&cgierr("$id_parts:$location:$qty:$idwl:$pct");
						push(@ary_items_in, "$id_parts:$location:$qty:$idwl:$pct") if $type eq 'in';
						push(@ary_items_out, "$id_parts:$location:$qty:$idwl:$pct") if $type eq 'out';

					}

					# if ($ptype eq 'Explode' and $tpct ne '1'){
					# 	$va{'message'} .= &trans_txt('mer_parts_productions_explode_pct') . qq| <br>|;
					# }

				}
				
				if (!$va{'message'}) {

					### Metodo usado para la salida de inventario. FIFO: Primer entradas primeras salidas | LIFO: Ultimas entradas primeras salidas
					my $acc_method = $cfg{'acc_inventoryout_method'} ? $cfg{'acc_inventoryout_method'} : 'fifo';
					my $invout_order = $acc_method eq 'fifo' ? '' : 'DESC';
					$log .= "acc_method=".$acc_method."\n\n<br>";
					$log .= "inv           out_order=".$invout_order."\n\n<br>";

					my $tcost = 0; my $tcost_adj = 0; my $total_cost_add = 0; my $total_unit_cost = 0; my $total_unit_cost_adj = 0; my $id_custom_info_out;

					##########################################
					##########################################
					##########################################
					######### Array Items IN
					##########################################
					##########################################
					##########################################
					my $str_in_to_note = '';

					########################
					### Costo Promedio
					########################	
					if( $cfg{'acc_inventoryout_method_cost'} and $cfg{'acc_inventoryout_method_cost'} eq 'average' ){
						for (0..$#ary_items_in){

							my $data_line = $ary_items_in[$_];
							my ($id_parts, $location, $qty, $idwl, $wqty) = split(/:/, $data_line);

							$total_qty += $qty;
							### String to note record
							my $pname = &load_name('sl_parts','ID_parts',($id_parts - 400000000),'Name');
							$str_in_to_note .= qq|ID SKU: $id_parts\nName: $pname\nLocation: $location\n|;

							$log .= "#####################################################\n<br>";
							$log .= "##### Se procesa el SKU: $id_parts\n<br>";
							$log .= "#####################################################\n<br>";

							################################
							## Warehouses Location
							################################

							## En caso de que la existencia del SKU se encuentre en varios registros
							## se realiza el proceso de actualizacion/eliminacion por cada registro encontrado
							my @ary_idwl = split(/,/, $idwl);
							my $rest_qty = $qty;
							foreach(@ary_idwl){
								my $this_idwl = $_;

								$sql = "SELECT Quantity FROM sl_warehouses_location WHERE ID_warehouses_location='$this_idwl';";
								$log .= $sql."\n\n<br>";
								my $sth = &Do_SQL($sql);
								my $qty_wl = $sth->fetchrow();

								$log .= "diff_qty = qty_wl - rest_qty => $diff_qty = $qty_wl - $rest_qty \n<br>";
								my $diff_qty = $qty_wl - $rest_qty;
								if( $diff_qty > 0 ){
									$sql = "/* From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_warehouses_location SET Quantity = Quantity - $rest_qty WHERE ID_warehouses_location = '$this_idwl';";
								}else{
									$sql = "/* From sl_parts_productions ($in{'id_parts_productions'}) */ DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = '$this_idwl';";
								}
								$log .= $sql."\n\n<br>";
								&Do_SQL($sql);

								if( $diff_qty >= 0 ){
									last;
								}else{
									$rest_qty = abs($diff_qty);
								}
							}
							
							################################
							### Costos					
							################################
							my ($cost, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($id_parts);
							$log .= "Costo promedio: ($cost, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add)\n<br>";

							if( !$cost or $cost == 0 ){
								$va{'message'} .= &trans_txt('mer_parts_cost_invalid').' '.$id_parts;
							}

							### Validacion y actualizacion de existencias en skus_cost
							my $rest_qty = $qty;
							do{
								my $sql = "SELECT ID_skus_cost, Quantity FROM sl_skus_cost WHERE ID_warehouses = '$in{'id_warehouses'}' AND ID_products = '$id_parts' AND Quantity>0 AND Cost>0 ORDER BY Date $invout_order, Time $invout_order LIMIT 1;";
								$log .= $sql."\n\n<br>";
								my $sth_cost = &Do_SQL($sql);
								my $rec_cost = $sth_cost->fetchrow_hashref();

								$log .= "Rest. Qty: $rest_qty, SCost. Qty: ".$rec_cost->{'Quantity'}."\n<br>";
								if( $rec_cost->{'ID_skus_cost'} ){
									if( $rest_qty < $rec_cost->{'Quantity'} ){
										$sql = "/* $tcost += ($rest_qty * $cost) From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_skus_cost SET Quantity = Quantity - $rest_qty WHERE ID_skus_cost = '$rec_cost->{'ID_skus_cost'}';";
										$log .= $sql."\n\n<br>";
										my ($sth) = &Do_SQL($sql);

										$rest_qty = 0;
									}else{
										$sql = "/* $tcost += ($rest_qty * $cost) From sl_parts_productions ($in{'id_parts_productions'}) */ DELETE FROM sl_skus_cost WHERE ID_skus_cost = '$rec_cost->{'ID_skus_cost'}'";
										$log .= $sql."\n\n<br>";
										my ($sth) = &Do_SQL($sql);

										$rest_qty -= $rec_cost->{'Quantity'};
									}
								}else{
									$rest_qty = 0;
								}
								$log .= "Rest. Qty: $rest_qty\n<br>";
							}while( $rest_qty > 0 );

							&sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, $cost_adj, 'OUT', $id_custom_info, $cost_add);
							$log .= qq|sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, $cost_adj, 'OUT', $id_custom_info, $cost_add)|."\n\n<br>";

							$total_unit_cost += $cost;
							$total_unit_cost_adj += $cost_adj;
							$tcost += round($qty * $cost, 3);
							$tcost_adj += round($qty * $cost_adj, 3);
							#$total_cost_add += $cost_add;

							if( $_ == 0 or int($id_custom_info_out) == 0 ){
								$id_custom_info_out = $id_custom_info;
							}

							$str_in_to_note .= qq|$qty x $cost\n|;
							$str_in_to_note .= qq|Total Cost: $tcost\n\n|;

							$log .= "tcost=".$tcost."\n<br>";

						}# End for ary_items_in

					########################
					### Costo UEPS
					########################
					}else{

						for (0..$#ary_items_in){

							my $data_line = $ary_items_in[$_];
							my ($id_parts, $location, $qty, $idwl, $wqty) = split(/:/, $data_line);

							### String to note record
							my $pname = &load_name('sl_parts','ID_parts',($id_parts - 400000000),'Name');
							$str_in_to_note .= qq|ID SKU: $id_parts\nName: $pname\nLocation: $location\n|;

							## Warehouses Location
							$sql = "/* From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_warehouses_location SET Quantity = Quantity - $qty WHERE ID_warehouses_location = '$idwl';";
							$log .= $sql."\n\n<br>";

							#&Do_SQL("ROLLBACK");&cgierr($sql);
							&Do_SQL($sql);
							
							###
							### Custom Info
							###
							my $sql_info = "SELECT sl_warehouses_location.ID_customs_info 
											FROM sl_warehouses_location 
											WHERE sl_warehouses_location.ID_warehouses = '$in{'id_warehouses'}' 
												AND sl_warehouses_location.Location = '$location' 
												AND sl_warehouses_location.ID_products = '$id_parts'
											ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order
											LIMIT 1;";
							my $sth_info = &Do_SQL($sql_info);
							$id_custom_info = $sth_info->fetchrow();

							## SKUS COST
							do{

								$sql = "SELECT ID_skus_cost, Quantity, Cost, Cost_Adj FROM sl_skus_cost WHERE ID_warehouses = '$in{'id_warehouses'}' AND ID_products = '$id_parts' AND Quantity>0 ORDER BY Date $invout_order LIMIT 1;";
								#&Do_SQL("ROLLBACK");&cgierr($sql);
								$log .= $sql."\n\n<br>";
								my ($sth) = &Do_SQL($sql);
								my ($idsc, $wqty, $cost, $cost_adj) = $sth->fetchrow();
								$log .= "idsc=".$idsc."\n<br>";
								$log .= "wqty=".$wqty."\n<br>";
								$log .= "cost=".$cost."\n<br>";
								($cost, $cost_adj) = &load_sltvcost($id_parts) if !$cost;
								$log .= "cost=".$cost."\n<br>";
								if( $wqty > 0 ){
									if($wqty < $qty) {
										&sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $wqty, $cost, $cost_adj, 'OUT', $id_custom_info);
										$log .= qq|sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $wqty, $cost, $cost_adj, 'OUT', $id_custom_info)|."\n\n<br>";
									}else {
										&sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, $cost_adj, 'OUT', $id_custom_info);
										$log .= qq|sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, $cost_adj, 'OUT', $id_custom_info)|."\n\n<br>";
									}
								}
								#&Do_SQL("ROLLBACK");&cgierr($log);
								if (!$idsc) {
									# ToDo: Mandar notificacion de discrepancia entre wlocation / skus_cost

									$tcost  += ($qty * $cost);
									$qty = 0;
								
								}else{

									if ($wqty >= $qty){
										if($qty > 0) {
											$tcost += round($qty * $cost,3);
											$sql = "/* $tcost += ($qty * $cost) From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_skus_cost SET Quantity = Quantity - $qty WHERE ID_skus_cost = '$idsc';";
											$log .= $sql."\n\n<br>";
											my ($sth) = &Do_SQL($sql);
											$str_in_to_note .= qq|$qty x $cost\n|;
											$qty=0;
										}
									}else{
										if($qty > 0) {
											$tcost += round($wqty * $cost,3);
											$sql = "/* $tcost += ($qty * $cost) From sl_parts_productions ($in{'id_parts_productions'}) */ DELETE FROM sl_skus_cost WHERE ID_skus_cost = '$idsc'";
											$log .= $sql."\n\n<br>";
											my ($sth) = &Do_SQL($sql);
											$str_in_to_note .= qq|$wqty x $cost\n|;
											$qty -= $wqty;
										}
									}
								}


							}while ($qty);
							#&Do_SQL("ROLLBACK");&cgierr($log);
							$str_in_to_note .= qq|Total Cost: $tcost\n\n|;
							$log .= "tcost=".$tcost."\n<br>";

						}# End for ary_items_in

					}

					$sql = "INSERT INTO sl_parts_productions_notes SET ID_parts_productions = '$in{'id_parts_productions'}', Notes = '". &filter_values($str_in_to_note) ."', Type = 'In', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
					$log .= $sql."\n\n<br>";
					&Do_SQL($sql);
					my $diffcost = $tcost; ## Usado para llevar el saldo del costo y saber al final cual es el remanente por redondeo
					my $last_idsc = 0; ## Usado para saber el ID del ultimo registro ID_skus_cost, para aplicar la diferencia del redondeo al ultimo item

					##########################################
					##########################################
					##########################################
					######### Array Items Out
					##########################################
					##########################################
					##########################################				
					my $str_out_to_note;
					########################
					### Costo Promedio
					########################
					if( $cfg{'acc_inventoryout_method_cost'} and $cfg{'acc_inventoryout_method_cost'} eq 'average' ){

						for (0..$#ary_items_out){

							my $data_line = $ary_items_out[$_];
							my ($id_parts,$location,$qty,$idwl,$pct) = split(/:/, $data_line);

							### String to note record
							my $pname = &load_name('sl_parts','ID_parts',($id_parts - 400000000),'Name');
							$str_out_to_note .= qq|ID SKU: $id_parts\nName: $pname\nLocation: $location\n|;

							#########################
							### Warehouses Location
							#########################
							if ($idwl) {							
								my $sql = "/* From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_warehouses_location SET Quantity = Quantity + $qty WHERE ID_warehouses_location = '$idwl';";
								$log .= $sql."\n\n<br>";
								&Do_SQL($sql);
							}else{							
								my $sql = "/* From sl_parts_productions ($in{'id_parts_productions'}) */ INSERT INTO sl_warehouses_location SET ID_warehouses = '$in{'id_warehouses'}', ID_products = '$id_parts', Location = '$location', Quantity = '$qty', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
								$log .= $sql."\n\n<br>";
								&Do_SQL($sql);
							}

							#########################
							### Costos
							#########################
							### Implode Data
							if ($ptype eq 'Implode') {
									
								if( !$total_unit_cost or $total_unit_cost == 0 ){
									$va{'message'} .= &trans_txt('mer_parts_cost_invalid').' '.$id_parts;
								}

								### Se recalcula el costo para el SKU resultante
								$total_unit_cost = round($tcost / $qty, 3);
								$total_unit_cost_adj = round($tcost_adj / $qty, 3);

								## Se inserta el nuevo costo en skus_cost
								my $sql = "/*Implode :: $diffcost = $tcost - ($cost * $qty) From sl_parts_productions ($in{'id_parts_productions'}) */ 
											INSERT INTO sl_skus_cost SET ID_products= '$id_parts', ID_purchaseorders = '$in{'id_parts_productions'}', ID_warehouses = '$in{'id_warehouses'}', Tblname = 'sl_parts_productions', Quantity = '$qty', Cost = '$total_unit_cost', Cost_Adj = '$total_unit_cost_adj', Cost_Add = '$total_cost_add', Date=CURDATE(), Time=CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
								$log .= $sql."\n<br>";
								my ($sth) = &Do_SQL($sql);
								$idsc = $sth->{'mysql_insertid'};
								$log .= "New ID_skus_cost: ".$idsc."\n<br>";
								
								$str_out_to_note .= qq|$qty x $total_unit_cost\n|;				

								&sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $total_unit_cost, $total_unit_cost_adj, 'IN', $id_custom_info_out, $total_cost_add);
								$log .= qq|sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $total_unit_cost, $total_unit_cost_adj, 'IN', $id_custom_info_out, $total_cost_add)|."\n\n<br>";
							}
							### Explode Data
							if ($ptype eq 'Explode') {
								
								### Costo Promedio
								my ($cost, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add) = &get_average_cost($id_parts);
								$log .= "Costo promedio: ($cost, $total_cost_avg, $id_custom_info, $cost_adj, $cost_add)\n<br>";

								if( !$cost or $cost == 0 ){
									$va{'message'} .= &trans_txt('mer_parts_cost_invalid').' '.$id_parts;
								}

								## Se inserta el costo en skus_cost
								my $sql = "/* Explode :: $in{'id_parts_productions'} */ 
											INSERT INTO sl_skus_cost SET ID_products= '$id_parts', ID_purchaseorders = '$in{'id_parts_productions'}', ID_warehouses = '$in{'id_warehouses'}', Tblname = 'sl_parts_productions', Quantity = '$qty', Cost = '$cost', Cost_Adj = '$cost_adj', Cost_Add = '$cost_add', Date=CURDATE(), Time=CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
								$log .= $sql."\n<br>";
								my ($sth) = &Do_SQL($sql);
								$idsc = $sth->{'mysql_insertid'};
								$log .= "New ID_skus_cost: ".$idsc."\n<br>";

								&sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, $cost_adj, 'IN', $id_custom_info, $cost_add);
								$log .= qq|sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, $cost_adj, 'IN', $id_custom_info, $cost_add)|."\n\n<br>";

								$str_out_to_note .= qq|$qty x $cost\n\n|;
							}

						}

					########################
					### Costo UEPS
					########################
					}else{
						for (0..$#ary_items_out){

							my $data_line = $ary_items_out[$_];
							my ($id_parts,$location,$qty,$idwl,$pct) = split(/:/, $data_line);
							my $cost = 0;
							my $fcost = 0;
							my $qty_orig = 0;
							my $i;

							### String to note record
							my $pname = &load_name('sl_parts','ID_parts',($id_parts - 400000000),'Name');
							$str_out_to_note .= qq|ID SKU: $id_parts\nName: $pname\nLocation: $location\n|;

							#######
							####### Implode Data
							#######
							if ($ptype eq 'Implode') {
								$cost = round($tcost / $qty,3);
								$fcost = round($cost + ($tcost - ($qty * $cost)),3); ## Se determina perdida de centavos por redondeo

								$qty_orig = $qty;
								$qty -= 1 if $fcost > $cost; ## Si hubo perdida, se quita un elemento de qty
								$i = $fcost > $cost ? 1 : 0; ## $i se aumenta para agregar el ultimo elemento con la suma del redondeo

								#if($fcost > $cost){ &cgierr("$fcost > $cost $fcost = $cost + ($tcost - ($qty * $cost));"); }
							}

							#######
							####### Explode Data
							#######
							if ($ptype eq 'Explode') {
								$cost = round($pct * $tcost / $qty,3);
								$diffcost -= round($cost * $qty,3);
								$i = 0;
							}


							## Warehouses Location
							if ($idwl) {
								my $this_qty = $qty_orig ? $qty_orig : $qty;
								&Do_SQL("/* From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_warehouses_location SET Quantity = Quantity + $this_qty WHERE ID_warehouses_location = '$idwl';");
							}else{
								my $this_qty = $qty_orig ? $qty_orig : $qty;
								&Do_SQL("/* From sl_parts_productions ($in{'id_parts_productions'}) */ INSERT INTO sl_warehouses_location SET ID_warehouses = '$in{'id_warehouses'}', ID_products = '$id_parts', Location = '$location', Quantity = '$this_qty', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
							}

							###
							### Custom Info
							###
							my $sql_info = "SELECT sl_warehouses_location.ID_customs_info 
											FROM sl_warehouses_location 
											WHERE sl_warehouses_location.ID_warehouses = '$in{'id_warehouses'}' 
												AND sl_warehouses_location.Location = '$location' 
												AND sl_warehouses_location.ID_products = '$id_parts'
											ORDER BY sl_warehouses_location.Date $invout_order, sl_warehouses_location.Time $invout_order
											LIMIT 1;";
							my $sth_info = &Do_SQL($sql_info);
							$id_custom_info = $sth_info->fetchrow();

							for (0..$i) {

								($_ == 1 and $ptype eq 'Implode') and ($qty = 1) and ($cost = $fcost);

								# SKUs Cost. SUM(Cost)
								my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$in{'id_warehouses'}' 
									                 AND ID_products = '$id_parts' AND Cost = '$cost' AND Quantity>0 ORDER BY Date $invout_order LIMIT 1;");
								my ($idsc) = $sth->fetchrow();

								if (!$idsc) {
									my ($sth) = &Do_SQL("/* $diffcost = $tcost - ($cost * $qty) From sl_parts_productions ($in{'id_parts_productions'}) */ INSERT INTO sl_skus_cost SET ID_products= '$id_parts', ID_purchaseorders = '$in{'id_parts_productions'}', ID_warehouses = '$in{'id_warehouses'}',
											         	Tblname = 'sl_parts_productions', Quantity = '$qty', Cost = '$cost', Date=CURDATE(), Time=CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'; ");
									$idsc = $sth->{'mysql_insertid'};
								}else{
									my ($sth) = &Do_SQL("/* $diffcost = $tcost - ($cost * $qty)  From sl_parts_productions ($in{'id_parts_productions'}) */ UPDATE sl_skus_cost SET Quantity = Quantity + $qty WHERE ID_skus_cost = '$idsc';");
								}
								$str_out_to_note .= qq|$qty x $cost\n|;

								## Guardamos el id del ultimo registro tocado
								$last_idsc = $idsc;

								&sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, 0, 'IN', $id_custom_info);
								$log .= qq|sku_logging($id_parts, $in{'id_warehouses'}, $location, 'Production', $in{'id_parts_productions'}, 'sl_parts_productions', $qty, $cost, 0, 'IN', $id_custom_info)|."\n\n<br>";
								
							}

							$str_out_to_note .= qq|\n| if ($ptype eq 'Explode' and ($diffcost > 0 or $diffcost < 0) );

						} ## for ary_items_out
						$diffcost = round($diffcost,2);
						#&cgierr($log);
						#&cgierr($str_out_to_note);
						#############
						############# Explode Evaluate cost difference
						#############
						if ($ptype eq 'Explode' and ($diffcost > 0 or $diffcost < 0) ){

							if ($last_idsc) {

								my ($sth) = &Do_SQL("SELECT ID_products, Quantity, Cost, ROUND(Cost + $diffcost,2) FROM sl_skus_cost WHERE ID_skus_cost = '$last_idsc';");
								my ($idp,$qty,$cost,$fcost) = $sth->fetchrow();

								if ($qty == 1){
									my ($sth) = &Do_SQL(" /* Explode: $in{'id_parts_productions'} */ UPDATE sl_skus_cost SET Cost = '$fcost' WHERE ID_skus_cost = '$last_idsc';");
								}else{
									my ($sth) = &Do_SQL("/* Explode: $in{'id_parts_productions'} */ UPDATE sl_skus_cost SET Quantity = Quantity - 1 WHERE ID_skus_cost = '$last_idsc';");

									my ($sth) = &Do_SQL("SELECT ID_skus_cost FROM sl_skus_cost WHERE ID_warehouses = '$in{'id_warehouses'}' 
										                 AND ID_products = '$idp' AND Cost = '$fcost' ORDER BY Date $invout_order LIMIT 1;");
									my ($idsc) = $sth->fetchrow();

									if (!$idsc) {
										my ($sth) = &Do_SQL("/* $fcost <> $diffcost From sl_parts_productions ($in{'id_parts_productions'}) DiffCost */ INSERT INTO sl_skus_cost SET ID_products= '$idp', ID_purchaseorders = '$in{'id_parts_productions'}', ID_warehouses = '$in{'id_warehouses'}',
												         	Tblname = 'sl_parts_productions', Quantity = 1, Cost = '$fcost', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}'; ");
									}else{
										my ($sth) = &Do_SQL("/* $fcost <> $diffcost  From sl_parts_productions ($in{'id_parts_productions'}) DiffCost */ UPDATE sl_skus_cost SET Quantity = Quantity + 1 WHERE ID_skus_cost = '$idsc';");
									}
									$str_out_to_note .= qq|-1 x $cost\n1 x $fcost\n\n|;

								}

							}else{
								$va{'message'} = "$ptype - $diffcost";
							}

						}
					}

					#&cgierr($str_out_to_note);
					$sql = "INSERT INTO sl_parts_productions_notes SET ID_parts_productions = '$in{'id_parts_productions'}', Notes = '". &filter_values($str_out_to_note) ."', Type = 'Out', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';";
					$log .= $sql."\n\n<br>";
					&Do_SQL($sql);
					&auth_logging('mer_parts_productions_processed');
					
					$sql = "UPDATE sl_parts_productions SET Status = 'Processed' WHERE ID_parts_productions = '$in{'id_parts_productions'}';";
					$log .= $sql."\n\n<br>";
					&Do_SQL($sql);
					$in{'status'} = $in{'chgstatus'};

					if( !$va{'message'} ){
						&Do_SQL("COMMIT;");
						$va{'message'} = &trans_txt('mer_parts_completed');
					}else{
						&Do_SQL("ROLLBACK;");
					}

				} else {
					#ERROR, se regresa todo el proceso
					&Do_SQL("ROLLBACK;");
				}

				### Elimina el registro de la transaccion activa de este proceso
	            &transaction_validate($in{'cmd'}, $in{'id_parts_productions'}, 'delete');

			}else{
				$va{'message'} = &trans_txt('transaction_duplicate');
			}

		}elsif ($t){
			$va{'message'} &trans_txt('invalid');
		}

		# &send_text_mail($cfg{'to_email_debug'},$cfg{'to_email_debug'},"Debug parts_productions $in{'id_parts_productions'}","$log");

		# &Do_SQL("ROLLBACK");
		#&Do_SQL("COMMIT");

		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('parts_productions', '$in{'id_parts_productions'}', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	}


	$va{'div_height_in'} = 50;
	$va{'div_height_out'} = 50;
	if ($in{'status'} eq 'New') {

		$va{'ids_in'}='';
		$va{'ids_out'}='';
		my ($sth) =  &Do_SQL("SELECT ID_parts_productions_items, sl_parts_productions_items.ID_products, sl_parts.Name, Location,Qty, In_out, 
						IF('$in{'type'}' = 'Explode',Pct,'N/A'),  IF( UPC IS NOT NULL, UPC , 'N/A')
	                    FROM sl_parts INNER JOIN sl_parts_productions_items
	                    ON ID_parts = RIGHT(sl_parts_productions_items.ID_products,4) 
	                    LEFT JOIN sl_skus ON sl_parts_productions_items.ID_products = ID_sku_products
	                    WHERE ID_parts_productions = '$in{'id_parts_productions'}'
	                    ORDER BY In_out,ID_parts_productions_items;");
		while (my($idppi,$id_parts,$name,$location,$qty,$type,$pct,$upc) = $sth->fetchrow()){

			$va{'div_height_' . $type} += 22;
			$va{'ids_' . $type } .= qq|<tr id="row-$type-$idppi">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$type-$idppi" style="cursor:pointer" title="Drop $id_parts"></td>\n
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=|.($id_parts - 400000000).qq|">|.&format_sltvid($id_parts).qq|</a></td>\n
								<td>$name</td>\n
								<td>$upc</td>\n
								<td align="center">$location</td>\n 
								<td align="right">$qty</td>\n
								<td align="right">$pct</td>\n
							</tr>|;	
		}

		if ($va{'ids_in'}) {
			$va{'ids_in'} = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">ID</td>\n 
								<td align="center" class="menu_bar_title">Name</td>\n
								<td align="center" class="menu_bar_title">UPC</td>\n 
								<td align="center" class="menu_bar_title">Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n 
								<td align="center" class="menu_bar_title">Pct(%)</td>\n 
							</tr>\n
							$va{'ids_in'}
						</table>\n|;
		}

		if ($va{'ids_out'}) {
			$va{'ids_out'} = qq|<table id="tbl-id-out" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">ID</td>\n 
								<td align="center" class="menu_bar_title">Name</td>\n 
								<td align="center" class="menu_bar_title">UPC</td>\n 
								<td align="center" class="menu_bar_title">Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n
								<td align="center" class="menu_bar_title">Pct(%)</td>\n  
							</tr>\n
							$va{'ids_out'}
						</table>\n|;
		}


		## Cargado de datos autocomplete.

		########
		########
		######## In
		########
		########
		my $mod = $in{'type'} eq 'Implode' ? '' : qq| AND LENGTH(sl_skus.UPC) > 3 |; 
		#my ($sth) = &Do_SQL("SELECT sl_warehouses_location.ID_products, Name, Location, Quantity
		#                    FROM sl_warehouses_location 
		#                    INNER JOIN sl_parts ON ID_parts = RIGHT(sl_warehouses_location.ID_products,4) 
		#					INNER JOIN sl_skus ON  ID_parts = sl_skus.ID_products
		#                    WHERE ID_warehouses = '$in{'id_warehouses'}' $mod
		#                    AND Quantity >0 ORDER BY Name,Quantity DESC;");
		my ($sth) = &Do_SQL("SELECT sl_warehouses_location.ID_products, sl_skus.UPC, Name, Location, sum(Quantity)
		                    FROM sl_warehouses_location 
		                    INNER JOIN sl_parts ON ID_parts = RIGHT(sl_warehouses_location.ID_products,4) 
							INNER JOIN sl_skus ON  ID_parts = sl_skus.ID_products
							INNER JOIN sl_locations ON sl_warehouses_location.Location=sl_locations.Code AND sl_warehouses_location.ID_warehouses = sl_locations.ID_warehouses
		                    WHERE sl_warehouses_location.ID_warehouses = '$in{'id_warehouses'}' $mod
		                    AND Quantity > 0 AND sl_locations.`Status` = 'Active' AND sl_locations.`Locked` = 'Inactive'
		                    GROUP BY sl_warehouses_location.ID_products, UPC, Location
		                    ORDER BY Name,Quantity DESC;");
		#while (my($id_parts,$name,$location,$qty) = $sth->fetchrow()){
		while (my($id_parts,$str_upc,$name,$location,$qty) = $sth->fetchrow()){
				$va{'ids_autocomplete'} .= '"'.$id_parts.' @@ '.$str_upc.' @@ '.&filter_values($name).' @@ '.$location.' @@ '.$qty.'",';
				#$va{'ids_autocomplete'} .= '"'.$id_parts.' @@ '.$str_upc.' @@ '.&filter_values($name).' @@ '.$location.' @@ '.$qty.'",';
		}
		chop($va{'ids_autocomplete'});

		########
		########
		######## Out
		########
		########
		my $mod = $in{'type'} eq 'Implode' ? qq| AND LENGTH(UPC) > 0 | : qq| /*AND UPC IS NULL OR UPC = ''*/ |; 
		my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, UPC, Name FROM sl_parts INNER JOIN sl_skus ON (ID_parts = ID_products) WHERE 1 $mod ORDER BY Name;");
		#my ($sth) = &Do_SQL("SELECT 400000000 + ID_parts, Name FROM sl_parts INNER JOIN sl_skus ON (ID_parts = ID_products) WHERE 1 $mod ORDER BY Name;");

		#while (my($id_parts,$name) = $sth->fetchrow()){
		while (my($id_parts,$str_upc,$name) = $sth->fetchrow()){
				$va{'ids_autocomplete_out'} .= '"'.$id_parts.' @@ '.$str_upc.' @@ '.&filter_values($name).'",';
				#$va{'ids_autocomplete_out'} .= '"'.$id_parts.' @@ '.&filter_values($name).'",';
		}
		chop($va{'ids_autocomplete_out'});


		########
		########
		######## Location
		########
		########
		my ($sth) = &Do_SQL("SELECT Code FROM sl_locations WHERE ID_warehouses = '$in{'id_warehouses'}' AND `Status`='Active' AND sl_locations.`Locked` = 'Inactive' ORDER BY Code;");

		while (my($location) = $sth->fetchrow()){
				$va{'loc_out'} .= '"'.$location.'",';
		}
		chop($va{'loc_out'});

	}

	$va{'this_style'} = $in{'status'} eq 'New' ? '' : qq|style="display:none;" |;
	## ToDo: Hacer las operaciones para mostrar los links de cambio de Status 
	if ($in{'status'} eq 'New'){
		$va{'changestatus'} = qq| <a href="#"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Approve' alt='' border='0' onClick='if(confirm("Do you want to PROCESS this record?")){trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_parts_productions]&tab=1&chgstatus=Processed")}'></a>
									&nbsp;&nbsp;
									<a href="#"><img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Deny' alt='' border='0' onClick='if(confirm("Do you want to DENY this record?")){trjump("/cgi-bin/mod/[ur_application]/dbman?cmd=[in_cmd]&view=[in_id_parts_productions]&tab=1&chgstatus=Void")}'></a>|;
	}else {
		$va{'changestatus'} = " &nbsp; ---";
	}



}


#############################################################################
#############################################################################
# Function: view_warehouses_batches
#
# Es: manejo de acciones de la aplicacion warehouses_batches
# En: 
#
# Created on: 20/10/2012 9:45:00
#
# Author: Pablo Hdez.
#
# Modifications:
#
# Parameters:
#
# - id_warehouses_batches : ID_warehouses_batches
#
# Returns:
#
# - multiples valores dependiendo del caso
#
# See Also:
#
#  Todo:
#
sub OLDview_warehouses_batches{
#############################################################################
#############################################################################	
	my $ordstatus = "'Processed'";
	my $prdstatus = "'In Fulfillment'";
	my (@c) = split(/,/,$cfg{'srcolors'});
	$va{'idcounts'} ="";	 
	if($in{'ordersselected'} eq ''){
		$in{'ordersselected'} = 0;
	}
	
		
	    
    if($in{'id_warehouses'}){
	    my $wname = &load_name('sl_warehouses','ID_warehouses',int($in{'id_warehouses'}),'Name');
	    $va{'warehouses_name'}=$wname;
    }
	
	###### Drop Order From Batch
	if($in{'drop'}) {

		my $id_orders = int($in{'drop'});
		my $id_warehouses_batches = int($in{'view'});
		my $query = "UPDATE sl_warehouses_batches_orders INNER JOIN sl_orders_products 
					USING(ID_orders_products) SET sl_warehouses_batches_orders.Status = 'Cancelled' 
					WHERE ID_warehouses_batches = '$id_warehouses_batches' AND ID_orders = '$id_orders'
					AND sl_warehouses_batches_orders.Status IN ('In Fulfillment','Error');";

		my ($sth) = &Do_SQL($query);
		if($sth->rows()) {

			my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchdropped')." $id_orders',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$id_warehouses_batches';");

			&add_order_notes_by_type($id_orders,&trans_txt('order_batchdropped')." $id_warehouses_batches","Low");
			&auth_logging('order_batchdropped',$id_warehouses_batches);
			$va{'message'} = &trans_txt('order_batchdropped')." $id_orders ";

		}

	}

	###### Process batch
	if ($in{'chgsr'}){
				
		my (@ids_tdc);
		my (@ids_cod);
		
		$count_process = 0;
		my ($sthr) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches WHERE Status='Processed' AND ID_warehouses_batches=$in{'id_warehouses_batches'}");
	    
	    if ($sthr->fetchrow>0){	
			
			my $sthro = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_warehouses_batches=".int($in{'id_warehouses_batches'}));
		    if ($sthro->fetchrow>0){	
		    	
		    	
		    	my ($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight); 
				($sec, $min, $hour, $day, $mon, $year, $dweek, $dyear, $daylight) = localtime(time());
				my (@months, $output,$year_num,$mon_num);
				$year += 1900;
				++$mon;
				my $day = substr('00'.$day,-2,2);
				my $mon = substr('00'.$mon,-2,2);
			    my $file_date = "$day$mon".substr($year,2,2);
			  	my $ename = lc($cfg{'app_e'.$in{'e'}});
			  	$ename =~ s/\s//g; 

				my $fname   =	$ename. '.'. $in{'id_warehouses_batches'}.'-'.$file_date.'.csv';
				$fname = $cfg{'path_upfiles'} . 'batches/e'.$in{'e'}.'/' . $fname;
 				 		
 				use Cwd;
				my $dir = getcwd;
				my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
				my $home_dir = $b_cgibin.'cgi-bin/common/';

				####TDC Orders
				my ($sthtdc) = &Do_SQL("SELECT sl_orders.ID_orders 
										  FROM sl_orders 
										  INNER JOIN sl_orders_products
										  ON sl_orders_products.ID_orders=sl_orders.ID_orders
										  INNER JOIN sl_warehouses_batches_orders
										  ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
										  WHERE sl_warehouses_batches_orders.ID_warehouses_batches=".int($in{'id_warehouses_batches'})." 		 
										  AND sl_orders.Ptype != 'COD' 
										  AND sl_orders.Status IN ('Processed','Shipped')
										  AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive','Returned')
										  AND sl_warehouses_batches_orders.Status = 'In Fulfillment'
										  GROUP BY sl_orders.ID_orders
										  ORDER BY sl_orders.ID_orders;");
			
				TDC:while ($id_orders = $sthtdc->fetchrow()){ 

					### Revisar aqui si se debe/puede cobrar
					$sth=&Do_SQL("SELECT 
									if(sum(if(Captured='Yes' and CapDate!='0000-00-00' AND Amount > $cfg{'postdatedfesprice'},1,0)) > 0,
									sum(if(Captured='Yes' and CapDate!='0000-00-00' AND Amount > $cfg{'postdatedfesprice'},1,0)),0)  as Payments,
									if(not isnull(sum(if(not isnull(Amount),Amount,0))),sum(if(not isnull(Amount),Amount,0)),0)as SumPayments
									FROM sl_orders_payments
									WHERE ID_orders = '$id_orders'
									and Status NOT IN('Order Cancelled', 'Cancelled') 
									and Amount>0");

					my ($paymentscaptured,$sumpayments)=$sth->fetchrow_array;

					my $order_status='OK';
					if($sumpayments) {

						my ($sth) = &Do_SQL("SELECT ID_orders_payments,PmtField3,AuthCode FROM sl_orders_payments 
											WHERE ID_orders = '$id_orders' AND Status NOT IN ('Void','Cancelled','Order Cancelled') 
											AND (Captured != 'Yes' OR Captured IS NULL ) AND (CapDate IS NULL OR CapDate='0000-00-00') 
											AND ( (AuthCode IS NOT NULL AND AuthCode != '') OR Paymentdate <= CURDATE() )
											ORDER BY Paymentdate;");
				
						if($sth->rows() > 0) {

							TDCC:while(my($idp,$ptype,$authcode) = $sth->fetchrow()) {
	 						
	 							my ($status,$statmsg,$codemsg);
	 							my $fn_pay = $authcode ? 'sltvcyb_capture' : 'sltvcyb_sale';
								## ( PayPal | Google Checkout | Cybersource ) Payment
								if ($ptype !~ /paypal|google/i and $ptype ne ''){
									require $home_dir . "apps/cybersubs.cgi";
									($status,$statmsg,$codemsg) = &$fn_pay($id_orders,$idp);
								}elsif($ptype =~ /paypal/i){
									require $home_dir . "apps/paypalsubs.cgi";
									require $home_dir . "apps/cybersubs.cgi";
									($status,$statmsg,$codemsg) = &capture_paypal($id_orders,$idp);
								}elsif($ptype =~ /google/i){
									require $home_dir . "apps/googlesubs.cgi";
									($status,$statmsg,$codemsg) = &fn_pay($id_orders,$idp);
								}
								if ($status !~ m/ok/i) {
									$order_status = "Error:$status\n$statmsg";
									last TDCC;
								}

							}
						}
						#elsif($paymentscaptured) {
						#	$order_status='OK';
						#}

					}

					if($order_status !~ m/ok/i){ # or !$paymentscaptured
						my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchunpaid')." $id_orders\n+ $order_status',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
						$count_not_process++;
						next TDC;
					}

					push(@ids_tdc, $id_orders);
				}

				my (@tdc_layout);			
				$va{'tdc_layout'}='';
				$va{'all_idorders'}='';
				my $pay_method = 'IN';
				
				#### Shipvia 
				my $ship_via_tdc = 'PM';  #USPS	
								
				TDCL:for my $i(0..$#ids_tdc){

					my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(sl_orders_products.ID_orders_products) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$ids_tdc[$i]';");
					my ($id_orders_products_sent) = $sth->fetchrow();
					my $mod_sent = $id_orders_products_sent ? "AND ID_orders_products NOT IN($id_orders_products_sent) " : '';
					my ($sthf) = &Do_SQL("SELECT 
							sl_orders.ID_orders AS ID_orders,
							shp_name,
							shp_Address1,
							shp_Address2,
							shp_Address3,
							shp_Urbanization,
							shp_City,
							shp_State,
							shp_Zip,
							shp_Country,
							ID_pricelevels,
							DNIS,
							ID_salesorigins,
							shp_Notes,
							sl_orders.Status AS OrderStatus,
							sl_orders.Date AS OrderDate,
							sl_customers.FirstName,
							sl_customers.LastName1,
							sl_customers.LastName2,
							sl_customers.Phone1,
							sl_customers.Email,
							
							ID_orders_products,
							ID_products,
							Items,
							SumItem,
							SumService,
							SumTax,
							SumShipping,
							SumDiscount,
							tmpprod.OrderNet AS OrderNet,
							OrderTotal,
							NumItems,
							QtyItems,
							PayType,
							SumPayments,
							QtyPayments,
							OrderShp
					FROM sl_orders
					INNER JOIN
					sl_customers
					ON sl_orders.ID_customers = sl_customers.ID_customers 
					INNER JOIN
					(
					  SELECT 
					     ID_orders,
					     GROUP_CONCAT(ID_orders_products)AS ID_orders_products,
					     GROUP_CONCAT(RIGHT(ID_products,6)) AS ID_products,
					     GROUP_CONCAT(ID_products SEPARATOR '|') AS Items,
					     SUM(IF(LEFT(ID_products,1) <> '6',SalePrice,0))AS SumItem,
					     SUM(IF(LEFT(ID_products,1) = '6',SalePrice,0))AS SumService,
					     SUM(Tax)AS SumTax,
					     SUM(Shipping)AS SumShipping,
					     SUM(Discount)AS SumDiscount,
					     SUM(SalePrice-Discount)AS OrderNet,
					     SUM(SalePrice-Discount+Shipping+Tax)AS OrderTotal,
					     COUNT(ID_products) AS NumItems,
					     GROUP_CONCAT(Quantity SEPARATOR '|') AS QtyItems
					  FROM sl_orders_products 
					  WHERE ID_orders = '$ids_tdc[$i]' 
					  AND Status NOT IN('Order Cancelled','Inactive','Returned')
					  AND Cost = 0 AND SalePrice >= 0 AND (ShpDate IS NULL OR ShpDate = '0000-00-00')
					  $mod_sent
					  GROUP BY ID_orders
					)AS tmpprod
					ON tmpprod.ID_orders = sl_orders.ID_orders
					INNER JOIN
					(
					  SELECT 
					     ID_orders,
					     Type AS PayType,
					     SUM(IF(Captured <> 'Yes' OR Captured IS NULL,Amount,0))AS SumPayments,
					     COUNT(*)AS QtyPayments
					  FROM sl_orders_payments 
					  WHERE ID_orders  = '$ids_tdc[$i]' AND Status NOT IN('Order Cancelled', 'Cancelled')
					  GROUP BY ID_orders
					)AS tmppay
					ON tmppay.ID_orders = sl_orders.ID_orders
					WHERE sl_orders.ID_orders='$ids_tdc[$i]' limit 1 ");

					if(!$sthf->rows) {
						my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchempty')." $ids_tdc[$i]',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
						next TDCL;
					}

					while ($rec = $sthf->fetchrow_hashref()){
						
						####Filter
						$year = substr($rec->{'OrderDate'},2,4);
						$mon = substr($rec->{'OrderDate'},5,2);
						$day = substr($rec->{'OrderDate'},8,2);
						$order_date = "$mon/$day/$year"; 

						$va{'parts_producs'}=''; 
						$va{'price_producs'}='';
 						$cont_parts = 0;

 						my ($tprice) = $rec->{'SumPayments'} > 0 ?
 										$rec->{'OrderNet'} :
 										$rec->{'SumPayments'};
 										
						my ($sth_pr) = &Do_SQL("SELECT (400000000 + ID_parts) AS Parts, 
						                                SUM(Quantity * Qty) as Qty
						                          FROM sl_orders_products 
												 INNER JOIN sl_skus_parts 
												    ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
												 WHERE ID_orders_products IN (".$rec->{'ID_orders_products'}.") 
												 GROUP BY ID_parts;");
						$va{'matches_parts'} = $sth_pr->rows;						
						if($va{'matches_parts'} <= 5 ){
							
							while ($rec_pr = $sth_pr->fetchrow_hashref){
								$cont_parts++;

								my $price_per_part = $tprice;
								if($tprice > 0) {
									my ($sth_t) = &Do_SQL("SELECT  $tprice / SUM(Quantity * Qty) 
															FROM sl_orders_products 
															INNER JOIN sl_skus_parts 
															ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
															WHERE ID_orders = '$rec->{'ID_orders'}'
															AND sl_orders_products.Status='Active';");
									$price_per_part = $sth_t->fetchrow();
								}

								$va{'parts_producs'} .= '"'.$rec_pr->{'Parts'}.'",'.$rec_pr->{'Qty'}.',';
								$va{'price_producs'} .= '"'.$price_per_part.'",,';
								#$va{'price_producs'} .= '"'.round($price_per_part,2).'",,';
							}
							
							if($cont_parts < 5){
								my $iterator_part =  5 - $cont_parts;
								for my $i(1..$iterator_part){
									$va{'parts_producs'} .= '"",,';
									$va{'price_producs'} .= '"",,';
								}
							}
							
						}else{
							my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchskulimit')." $ids_tdc[$i]',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
							$count_not_process++;
							next TDCL;
						}
 						
						$va{'tdc_layout'}  = '';
						$va{'tdc_layout'} .= ',';                                                #1
						$va{'tdc_layout'} .= $rec->{'ID_orders'}.',';                            #2
						$va{'tdc_layout'} .= '"'.substr($rec->{'LastName1'}, 0, 20).'",';        #3
						$va{'tdc_layout'} .= '"'.substr($rec->{'FirstName'}, 0, 15).'",';        #4
						$va{'tdc_layout'} .= ',';                                                #5

						if(length($rec->{'shp_Address1'}) > 32){
							$va{'tdc_layout'} .= '"'.substr($rec->{'shp_Address1'}, 0, 31).'",'; #6
							$va{'tdc_layout'} .= '"'.substr($rec->{'shp_Address1'}, 31).' '.$rec->{'shp_Address2'}.'",';   #7	 	
						}else{
							$va{'tdc_layout'} .= '"'.$rec->{'shp_Address1'}.'",';     			 #6 
							$va{'tdc_layout'} .= '"'.substr($rec->{'shp_Address2'}, 0, 31).'",'; #7 
						} 

						$va{'tdc_layout'} .= '"'.substr($rec->{'shp_City'}, 0, 30).'",';         #8
						$va{'tdc_layout'} .= '"'.substr($rec->{'shp_State'}, 0, 2).'",';         #9
						$va{'tdc_layout'} .= '"'.substr($rec->{'shp_Zip'}, 0, 10).'",';          #10
						$va{'tdc_layout'} .= ',';                                                #11
						$va{'tdc_layout'} .= '"'.substr($rec->{'Phone1'}, 0, 18).'",';           #12
						$va{'tdc_layout'} .= ',';                                                #13
						$va{'tdc_layout'} .= ',';                                                #14
						$va{'tdc_layout'} .= ',';                                                #15
						$va{'tdc_layout'} .= ',';                                                #16
						$va{'tdc_layout'} .= ',';                                                #17
						$va{'tdc_layout'} .= ',';                                                #18
						$va{'tdc_layout'} .= ',';                                                #19
						$va{'tdc_layout'} .= ',';                                                #20
						$va{'tdc_layout'} .= ',';                                                #21
						$va{'tdc_layout'} .= ',';                                                #22
						$va{'tdc_layout'} .= ',';                                                #23
						$va{'tdc_layout'} .= ',';                                                #24
						$va{'tdc_layout'} .= ',';                                                #25
						$va{'tdc_layout'} .= ',';                                                #26
						$va{'tdc_layout'} .= '"'.$ship_via_tdc.'",';                             #27
						$va{'tdc_layout'} .= ',';                                                #28
						$va{'tdc_layout'} .= ',';                                                #29
						$va{'tdc_layout'} .= ',';                                                #30
						$va{'tdc_layout'} .= '"'.substr($order_date, 0, 8).'",';  		         #31
						$va{'tdc_layout'} .= ',';                                                #32
						$va{'tdc_layout'} .= $va{'parts_producs'};                               #33 .... 42
						$va{'tdc_layout'} .= ',';                                                #43
						$va{'tdc_layout'} .= ',';                                                #44
						$va{'tdc_layout'} .= ',';                                                #45
						$va{'tdc_layout'} .= ',';                                                #46
						$va{'tdc_layout'} .= ',';                                                #47
						$va{'tdc_layout'} .= ',';                                                #48
						$va{'tdc_layout'} .= ',';                                                #49
						$va{'tdc_layout'} .= ',';                                                #50
						$va{'tdc_layout'} .= ',';                                                #51
						$va{'tdc_layout'} .= '"'.$pay_method.'",';                               #52
						$va{'tdc_layout'} .= ',';                                                #53
						$va{'tdc_layout'} .= ',';                                                #54
						$va{'tdc_layout'} .= ',';                                                #55
						$va{'tdc_layout'} .= ',';                                                #56
						$va{'tdc_layout'} .= ',';                                                #57 
						$va{'tdc_layout'} .= ',';                                                #58
						$va{'tdc_layout'} .= ',';                                                #59 
						$va{'tdc_layout'} .= ',';                                                #60 
						$va{'tdc_layout'} .= ',';                                                #61 
						$va{'tdc_layout'} .= ',';                                                #62 
						$va{'tdc_layout'} .= ',';                                                #63 
						$va{'tdc_layout'} .= ',';                                                #64 
						$va{'tdc_layout'} .= ',';                                                #65 
						$va{'tdc_layout'} .= ',';                                                #66 
						$va{'tdc_layout'} .= ',';                                                #67
						$va{'tdc_layout'} .= ','; 										         #68
						$va{'tdc_layout'} .= '"'.substr($rec->{'Email'}, 0, 50).'",';            #69
						$va{'tdc_layout'} .= ',';                                                #70
						$va{'tdc_layout'} .= ',';                                                #71
						$va{'tdc_layout'} .= ',';                                                #72
						$va{'tdc_layout'} .= ',';                                                #73
						$va{'tdc_layout'} .= ',';                                                #74
						$va{'tdc_layout'} .= ',';                                                #75
						$va{'tdc_layout'} .= ',';                                                #76
						$va{'tdc_layout'} .= ',';                                                #77
						$va{'tdc_layout'} .= ',';                                                #78
						$va{'tdc_layout'} .= ',';                                                #79
						$va{'tdc_layout'} .= ',';                                                #80
						$va{'tdc_layout'} .= ',';                                                #81
						$va{'tdc_layout'} .= ',';                                                #82
						$va{'tdc_layout'} .= ',';                                                #83
						$va{'tdc_layout'} .= ',';                                                #84
						$va{'tdc_layout'} .= ',';                                                #85
						$va{'tdc_layout'} .= ',';                                                #86
						$va{'tdc_layout'} .= ',';                                                #87
						$va{'tdc_layout'} .= ',';                                                #88
						$va{'tdc_layout'} .= ',';                                                #89
						$va{'tdc_layout'} .= ',';                                                #90
						$va{'tdc_layout'} .= ',';                                                #91
						$va{'tdc_layout'} .= ',';                                                #92
						$va{'tdc_layout'} .= ',';                                                #93
						$va{'tdc_layout'} .= ',';                                                #94
						$va{'tdc_layout'} .= ',';                                                #95
						$va{'tdc_layout'} .= ',';                                                #96
						$va{'tdc_layout'} .= ',';                                                #97
						$va{'tdc_layout'} .= ',';                                                #98
						$va{'tdc_layout'} .= ',';                                                #99
						$va{'tdc_layout'} .= ',';                                                #100
						$va{'tdc_layout'} .= ',';                                                #101
						$va{'tdc_layout'} .= ',';                                                #102
						$va{'tdc_layout'} .= ',';                                                #103
						$va{'tdc_layout'} .= ',';                                                #104
						$va{'tdc_layout'} .= '"'.$rec->{'ID_orders'}.'",';        				 #105
						$va{'tdc_layout'} .= ',';                                                #106
						$va{'tdc_layout'} .= ',';                                                #107
						$va{'tdc_layout'} .= ',';                                                #108
						$va{'tdc_layout'} .= ',';                                                #109
						$va{'tdc_layout'} .= ',';                                                #110
						$va{'tdc_layout'} .= ',';                                                #111
						$va{'tdc_layout'} .= ',';                                                #112
						$va{'tdc_layout'} .= ',';                                                #113
						$va{'tdc_layout'} .= ',';                                                #114
						$va{'tdc_layout'} .= ',';                                                #115
						$va{'tdc_layout'} .= ',';                                                #116
						$va{'tdc_layout'} .= ',';                                                #117
						$va{'tdc_layout'} .= ',';                                                #118
						$va{'tdc_layout'} .= ',';                                                #119
						$va{'tdc_layout'} .= ',';                                                #120
						$va{'tdc_layout'} .= '"'.$rec->{'ID_orders'}.'",';        				 #121
						$va{'tdc_layout'} .= ',';									             #122
						$va{'tdc_layout'} .= ',';                                                #123
						$va{'tdc_layout'} .= ',';                                                #124
						$va{'tdc_layout'} .= ',';                                                #125
						$va{'tdc_layout'} .= ',';                                                #126
						$va{'tdc_layout'} .= ',';                                                #127
						$va{'tdc_layout'} .= ',';                                                #128
						$va{'tdc_layout'} .= ',';                                                #129
						$va{'tdc_layout'} .= ',';                                                #130
						$va{'tdc_layout'} .= ',';                                                #131
						$va{'tdc_layout'} .= ',';                                                #132
						$va{'tdc_layout'} .= ',';                                                #133
						$va{'tdc_layout'} .= ',';                                                #134
						$va{'tdc_layout'} .= ',';                                                #135
						$va{'tdc_layout'} .= ',';                                                #136
						$va{'tdc_layout'} .= ',';                                                #137
						$va{'tdc_layout'} .= ',';                                                #138
						$va{'tdc_layout'} .= ',';                                                #139
						$va{'tdc_layout'} .= ',';                                                #140
						$va{'tdc_layout'} .= ',';                                                #141
						$va{'tdc_layout'} .= ',';                                                #142
						$va{'tdc_layout'} .= ',';                                                #143
						$va{'tdc_layout'} .= ',';                                                #144
						$va{'tdc_layout'} .= ',';                                                #145
						$va{'tdc_layout'} .= ',';                                                #146
						$va{'tdc_layout'} .= ',';                                                #147
						$va{'tdc_layout'} .= ',';                                                #148
						$va{'tdc_layout'} .= ',';                                                #149
						$va{'tdc_layout'} .= ',';                                                #150
						$va{'tdc_layout'} .= ',';                                                #151
						$va{'tdc_layout'} .= ',';                                                #152
						$va{'tdc_layout'} .= ',';                                                #153
						$va{'tdc_layout'} .= ',';                                                #154
						$va{'tdc_layout'} .= ',';                                                #155
						$va{'tdc_layout'} .= ',';                                                #156
						$va{'tdc_layout'} .= ',';                                                #157
						$va{'tdc_layout'} .= ',';                                                #158
						$va{'tdc_layout'} .= ',';                                                #159
						$va{'tdc_layout'} .= ',';                                                #160
						$va{'tdc_layout'} .= ',';                                                #161
						$va{'tdc_layout'} .= ',';                                                #162
						$va{'tdc_layout'} .= ',';                                                #163
						$va{'tdc_layout'} .= ',';                                                #164
						$va{'tdc_layout'} .= ',';                                                #165
						$va{'tdc_layout'} .= ',';                                                #166
						$va{'tdc_layout'} .= ',';                                                #167
						$va{'tdc_layout'} .= ',';                                                #168
						$va{'tdc_layout'} .= ',';                                                #169
						$va{'tdc_layout'} .= '';                                                 #170			 
						$va{'tdc_layout'} .= "\r\n"; 
						
				
						####Global Layout TDC									
						push(@tdc_layout, $va{'tdc_layout'});
						$va{'all_idorders'} .="$rec->{'ID_orders'},";								 
						$count_process++; 
		
						## Nota orden enviada en batch		

						&add_order_notes_by_type($ids_tdc[$i],&trans_txt('order_batchsent'),"High");
						## Log
						&auth_logging('order_batchsent', $ids_tdc[$i]);


							
					}#end while	customers		
				}#end for ids
				
				####COD
				my $query = "SELECT sl_orders.ID_orders                  
				FROM sl_orders_products
				INNER JOIN sl_orders on(sl_orders_products.ID_orders=sl_orders.ID_orders)
				INNER JOIN (select ID_orders,sum(if(Type='COD',1,0))as PaymentsCOD,sum(if(Type!='COD',1,0))as PaymentsNotCOD
				FROM sl_orders_payments
				GROUP BY ID_orders
				HAVING PaymentsCOD>0)as tempo on (tempo.ID_orders=sl_orders.ID_orders)
				INNER JOIN sl_warehouses_batches_orders
				 ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
				WHERE sl_warehouses_batches_orders.ID_warehouses_batches=".int($in{'id_warehouses_batches'})." 
				AND sl_orders_products.ID_products not like '6%' 
				AND (isnull(ShpDate) or ShpDate='0000-00-00' or ShpDate='') 
				AND (isnull(Tracking) or Tracking='')
				AND (isnull(ShpProvider) or ShpProvider='')
				AND shp_type=3
				AND sl_orders.Status IN ('Shipped','Processed')
				AND Ptype='COD' 
				AND StatusPrd='In Fulfillment'
				AND sl_orders_products.Status NOT IN('Order Cancelled','Inactive','Returned')
				AND sl_warehouses_batches_orders.Status = 'In Fulfillment'
				AND sl_orders_products.SalePrice>0
				AND sl_orders_products.Quantity>0
				GROUP BY sl_orders_products.ID_orders";
	
				my ($sthtcod) = &Do_SQL($query);
				COD:while ($id_orders = $sthtcod->fetchrow()){

					## 0=Unshipped, 1=Shipped, 2=In Transit
					my $order_status = &delivery_status_order($id_orders);
					
					if($order_status > 1) {

						my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchintransit')." $id_orders',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
						&Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders = '$id_orders';");
						$count_not_process++;
						next COD;

					}

					push(@ids_cod, $id_orders)
					
				}
				
				my (@cod_layout);			
				$va{'cod_layout'}='';	
				$pay_method = 'CO';
				
				CODL:for my $i(0..$#ids_cod){

					my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(sl_orders_products.ID_orders_products) FROM sl_orders_products INNER JOIN sl_orders_parts USING(ID_orders_products) WHERE ID_orders = '$ids_cod[$i]';");
					my ($id_orders_products_sent) = $sth->fetchrow();
					my $mod_sent = $id_orders_products_sent ? "AND ID_orders_products NOT IN($id_orders_products_sent) " : '';
					my ($sth_cod) = &Do_SQL("SELECT 
							sl_orders.ID_orders AS ID_orders,
							shp_name,
							shp_Address1,
							shp_Address2,
							shp_Address3,
							shp_Urbanization,
							shp_City,
							shp_State,
							shp_Zip,
							shp_Country,
							ID_pricelevels,
							DNIS,
							ID_salesorigins,
							shp_Notes,
							sl_orders.Status AS OrderStatus,
							sl_orders.Date AS OrderDate,
							sl_customers.FirstName,
							sl_customers.LastName1,
							sl_customers.LastName2,
							sl_customers.Phone1,
							sl_customers.Email,
							ID_orders_products,
							ID_products,
							Items,
							SumItem,
							SumService,
							SumTax,
							SumShipping,
							SumDiscount,
							tmpprod.OrderNet AS OrderNet,
							OrderTotal,
							NumItems,
							QtyItems,
							PayType,
							SumPayments,
							QtyPayments,
							OrderShp
					FROM sl_orders
					INNER JOIN
					sl_customers
					ON sl_orders.ID_customers = sl_customers.ID_customers 
					INNER JOIN
					(
					  SELECT 
					     ID_orders,
					     GROUP_CONCAT(ID_orders_products)AS ID_orders_products,
					     GROUP_CONCAT(RIGHT(ID_products,6)) AS ID_products,
					     GROUP_CONCAT(ID_products SEPARATOR '|') AS Items,
					     SUM(IF(LEFT(ID_products,1) <> '6',SalePrice,0))AS SumItem,
					     SUM(IF(LEFT(ID_products,1) = '6',SalePrice,0))AS SumService,
					     SUM(Tax)AS SumTax,
					     SUM(Shipping)AS SumShipping,
					     SUM(Discount)AS SumDiscount,
					     SUM(SalePrice-Discount)AS OrderNet,
					     SUM(SalePrice-Discount+Shipping+Tax)AS OrderTotal,
					     COUNT(ID_products) AS NumItems,
					     GROUP_CONCAT(Quantity SEPARATOR '|') AS QtyItems
					  FROM sl_orders_products 
					  WHERE ID_orders = '$ids_cod[$i]' 
					  AND Status NOT IN('Order Cancelled','Inactive','Returned')
					  AND Cost = 0 AND SalePrice >= 0 AND (ShpDate IS NULL OR ShpDate = '0000-00-00')
					  $mod_sent
					  GROUP BY ID_orders
					)AS tmpprod
					ON tmpprod.ID_orders = sl_orders.ID_orders
					INNER JOIN
					(
					  SELECT 
					     ID_orders,
					     Type AS PayType,
					     SUM(IF(Captured <> 'Yes' OR Captured IS NULL,Amount,0))AS SumPayments,
					     COUNT(*)AS QtyPayments
					  FROM sl_orders_payments 
					  WHERE ID_orders  = '$ids_cod[$i]' AND Status NOT IN('Void','Order Cancelled', 'Cancelled')
					  GROUP BY ID_orders
					)AS tmppay
					ON tmppay.ID_orders = sl_orders.ID_orders
					WHERE sl_orders.ID_orders='$ids_cod[$i]' limit 1 ");
		 
					if(!$sth_cod->rows) {
						my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchempty')." $ids_cod[$i]',Type='Low',Date=CURDATE(),Time=CURDATE(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
						&Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders = '$ids_cod[$i]';");
						$count_not_process++;
						next CODL;
					}

					while ($rec = $sth_cod->fetchrow_hashref()){
												
						####Filter
						$year = substr($rec->{'OrderDate'},2,4);
						$mon = substr($rec->{'OrderDate'},5,2);
						$day = substr($rec->{'OrderDate'},8,2);

						$order_date = "$mon/$day/$year"; 
 						 
 						$va{'parts_producs'}='';
 						$va{'price_producs'}='';
 						$cont_parts = 0;

 						
 						my ($tprice) = $rec->{'SumPayments'} > 0 ?
 										$rec->{'OrderNet'} :
 										$rec->{'SumPayments'};

						my ($sth_pr) = &Do_SQL("SELECT (400000000 + ID_parts) as Parts, 
						                                SUM(Quantity * Qty) as Qty
						                          FROM sl_orders_products 
												 INNER JOIN sl_skus_parts 
												    ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
												 WHERE ID_orders_products IN (".$rec->{'ID_orders_products'}.") 
												 GROUP BY ID_parts");
						$va{'matches_parts'} = $sth_pr->rows;

						if($va{'matches_parts'} <= 5 ){
							
							while ($rec_pr = $sth_pr->fetchrow_hashref){
								$cont_parts++;

								my $price_per_part = $tprice;
								if($tprice > 0) {
									my ($sth_t) = &Do_SQL("SELECT  $tprice / SUM(Quantity * Qty) 
															FROM sl_orders_products 
															INNER JOIN sl_skus_parts 
															ON sl_orders_products.ID_products = sl_skus_parts.ID_sku_products 
															WHERE ID_orders = '$rec->{'ID_orders'}'
															AND sl_orders_products.Status='Active';");
									$price_per_part = $sth_t->fetchrow();
								}

								$va{'parts_producs'} .= '"'.$rec_pr->{'Parts'}.'",'.$rec_pr->{'Qty'}.',';
								$va{'price_producs'} .= '"'.$price_per_part.'",,';
								#$va{'price_producs'} .= '"'.round($price_per_part,2).'",,';
							}
							
							if($cont_parts < 5){
								my $iterator_part =  5 - $cont_parts;
								for my $i(1..$iterator_part){
									$va{'parts_producs'} .= '"",,';
									$va{'price_producs'} .= '"",,';
								}
							}
							
						}else{
							my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('order_batchskulimit')." $ids_cod[$i]',Type='Low',Date=CURDATE(),Time=CURDATE(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
							&Do_SQL("UPDATE sl_orders SET StatusPrd='None' WHERE ID_orders = '$ids_cod[$i]';");
							$count_not_process++;
							next CODL;
						}
												
						my $ship_via_cod = 'UPS'; #UPS
						if($rec->{'shp_State'} =~ /PR-Puerto Rico/) {
							$ship_via_cod = 'PM'; #USPS puerto rico
						}														
																		
						$va{'cod_layout'}  = '';
						$va{'cod_layout'} .= ',';                                                #1
						$va{'cod_layout'} .= $rec->{'ID_orders'}.',';                            #2
						$va{'cod_layout'} .= '"'.substr($rec->{'LastName1'}, 0, 20).'",';        #3
						$va{'cod_layout'} .= '"'.substr($rec->{'FirstName'}, 0, 15).'",';        #4
						$va{'cod_layout'} .= ',';                                                #5

						if(length($rec->{'shp_Address1'}) > 32){
							$va{'cod_layout'} .= '"'.substr($rec->{'shp_Address1'}, 0, 31).'",'; #6
							$va{'cod_layout'} .= '"'.substr($rec->{'shp_Address1'}, 31).' '.$rec->{'shp_Address2'}.'",';   #7	 	
						}else{
							$va{'cod_layout'} .= '"'.$rec->{'shp_Address1'}.'",';     			 #6 
							$va{'cod_layout'} .= '"'.substr($rec->{'shp_Address2'}, 0, 31).'",'; #7 
						} 

						$va{'cod_layout'} .= '"'.substr($rec->{'shp_City'}, 0, 30).'",';         #8
						$va{'cod_layout'} .= '"'.substr($rec->{'shp_State'}, 0, 2).'",';         #9
						$va{'cod_layout'} .= '"'.substr($rec->{'shp_Zip'}, 0, 10).'",';          #10
						$va{'cod_layout'} .= ',';                                                #11
						$va{'cod_layout'} .= '"'.substr($rec->{'Phone1'}, 0, 18).'",';           #12
						$va{'cod_layout'} .= ',';                                                #13
						$va{'cod_layout'} .= ',';                                                #14
						$va{'cod_layout'} .= ',';                                                #15
						$va{'cod_layout'} .= ',';                                                #16
						$va{'cod_layout'} .= ',';                                                #17
						$va{'cod_layout'} .= ',';                                                #18
						$va{'cod_layout'} .= ',';                                                #19
						$va{'cod_layout'} .= ',';                                                #20
						$va{'cod_layout'} .= ',';                                                #21
						$va{'cod_layout'} .= ',';                                                #22
						$va{'cod_layout'} .= ',';                                                #23
						$va{'cod_layout'} .= ',';                                                #24
						$va{'cod_layout'} .= ',';                                                #25
						$va{'cod_layout'} .= ',';                                                #26
						$va{'cod_layout'} .= '"'.$ship_via_cod.'",';                             #27
						$va{'cod_layout'} .= ',';                                                #28
						$va{'cod_layout'} .= ',';                                                #29
						$va{'cod_layout'} .= ',';                                                #30
						$va{'cod_layout'} .= '"'.substr($order_date, 0, 8).'",';                 #31
						$va{'cod_layout'} .= ',';                                                #32						
						$va{'cod_layout'} .= $va{'parts_producs'};                               #33 .... 42
						$va{'cod_layout'} .= ',';                                                #43
						$va{'cod_layout'} .= ',';                                                #44
						$va{'cod_layout'} .= ',';                                                #45
						$va{'cod_layout'} .= ',';                                                #46
						$va{'cod_layout'} .= ',';                                                #47
						$va{'cod_layout'} .= ',';                                                #48
						$va{'cod_layout'} .= ',';                                                #49
						$va{'cod_layout'} .= ',';                                                #50
						$va{'cod_layout'} .= ',';                                                #51
						$va{'cod_layout'} .= '"'.$pay_method.'",';                               #52
						$va{'cod_layout'} .= ',';                                                #53
						$va{'cod_layout'} .= ',';                                                #54
						$va{'cod_layout'} .= ',';                                                #55
						$va{'cod_layout'} .= '"Y",';                                             #56
						$va{'cod_layout'} .= $va{'price_producs'};                               #57 ... 66
						$va{'cod_layout'} .= '"Y",';                                             #67
						$va{'cod_layout'} .= '"'.round($rec->{'SumShipping'},2).'",';          #68
						$va{'cod_layout'} .= '"'.substr($rec->{'Email'}, 0, 50).'",';            #69
						$va{'cod_layout'} .= ',';                                                #70
						$va{'cod_layout'} .= ',';                                                #71
						$va{'cod_layout'} .= ',';                                                #72
						$va{'cod_layout'} .= ',';                                                #73
						$va{'cod_layout'} .= ',';                                                #74
						$va{'cod_layout'} .= ',';                                                #75
						$va{'cod_layout'} .= ',';                                                #76
						$va{'cod_layout'} .= ',';                                                #77
						$va{'cod_layout'} .= ',';                                                #78
						$va{'cod_layout'} .= ',';                                                #79
						$va{'cod_layout'} .= ',';                                                #80
						$va{'cod_layout'} .= ',';                                                #81
						$va{'cod_layout'} .= ',';                                                #82
						$va{'cod_layout'} .= ',';                                                #83
						$va{'cod_layout'} .= ',';                                                #84
						$va{'cod_layout'} .= ',';                                                #85
						$va{'cod_layout'} .= ',';                                                #86
						$va{'cod_layout'} .= ',';                                                #87
						$va{'cod_layout'} .= ',';                                                #88
						$va{'cod_layout'} .= ',';                                                #89
						$va{'cod_layout'} .= ',';                                                #90
						$va{'cod_layout'} .= ',';                                                #91
						$va{'cod_layout'} .= ',';                                                #92
						$va{'cod_layout'} .= ',';                                                #93
						$va{'cod_layout'} .= ',';                                                #94
						$va{'cod_layout'} .= ',';                                                #95
						$va{'cod_layout'} .= ',';                                                #96
						$va{'cod_layout'} .= ',';                                                #97
						$va{'cod_layout'} .= ',';                                                #98
						$va{'cod_layout'} .= ',';                                                #99
						$va{'cod_layout'} .= ',';                                                #100
						$va{'cod_layout'} .= ',';                                                #101
						$va{'cod_layout'} .= ',';                                                #102
						$va{'cod_layout'} .= ',';                                                #103
						$va{'cod_layout'} .= ',';                                                #104
						$va{'cod_layout'} .= '"'.$rec->{'ID_orders'}.'",';        				 #105
						$va{'cod_layout'} .= ',';                                                #106
						$va{'cod_layout'} .= ',';                                                #107
						$va{'cod_layout'} .= ',';                                                #108
						$va{'cod_layout'} .= ',';                                                #109
						$va{'cod_layout'} .= ',';                                                #110
						$va{'cod_layout'} .= ',';                                                #111
						$va{'cod_layout'} .= ',';                                                #112
						$va{'cod_layout'} .= ',';                                                #113
						$va{'cod_layout'} .= ',';                                                #114
						$va{'cod_layout'} .= ',';                                                #115
						$va{'cod_layout'} .= ',';                                                #116
						$va{'cod_layout'} .= ',';                                                #117
						$va{'cod_layout'} .= ',';                                                #118
						$va{'cod_layout'} .= ',';                                                #119
						$va{'cod_layout'} .= ',';                                                #120
						$va{'cod_layout'} .= '"'.$rec->{'ID_orders'}.'",';        				 #121
						$va{'cod_layout'} .= ',';									             #122
						$va{'cod_layout'} .= ',';                                                #123
						$va{'cod_layout'} .= ',';                                                #124
						$va{'cod_layout'} .= ',';                                                #125
						$va{'cod_layout'} .= ',';                                                #126
						$va{'cod_layout'} .= ',';                                                #127
						$va{'cod_layout'} .= ',';                                                #128
						$va{'cod_layout'} .= ',';                                                #129
						$va{'cod_layout'} .= ',';                                                #130
						$va{'cod_layout'} .= ',';                                                #131
						$va{'cod_layout'} .= ',';                                                #132
						$va{'cod_layout'} .= ',';                                                #133
						$va{'cod_layout'} .= ',';                                                #134
						$va{'cod_layout'} .= ',';                                                #135
						$va{'cod_layout'} .= ',';                                                #136
						$va{'cod_layout'} .= ',';                                                #137
						$va{'cod_layout'} .= ',';                                                #138
						$va{'cod_layout'} .= ',';                                                #139
						$va{'cod_layout'} .= ',';                                                #140
						$va{'cod_layout'} .= ',';                                                #141
						$va{'cod_layout'} .= ',';                                                #142
						$va{'cod_layout'} .= ',';                                                #143
						$va{'cod_layout'} .= ',';                                                #144
						$va{'cod_layout'} .= ',';                                                #145
						$va{'cod_layout'} .= ',';                                                #146
						$va{'cod_layout'} .= ',';                                                #147
						$va{'cod_layout'} .= ',';                                                #148
						$va{'cod_layout'} .= ',';                                                #149
						$va{'cod_layout'} .= ',';                                                #150
						$va{'cod_layout'} .= ',';                                                #151
						$va{'cod_layout'} .= ',';                                                #152
						$va{'cod_layout'} .= ',';                                                #153
						$va{'cod_layout'} .= ',';                                                #154
						$va{'cod_layout'} .= ',';                                                #155
						$va{'cod_layout'} .= ',';                                                #156
						$va{'cod_layout'} .= ',';                                                #157
						$va{'cod_layout'} .= ',';                                                #158
						$va{'cod_layout'} .= ',';                                                #159
						$va{'cod_layout'} .= ',';                                                #160
						$va{'cod_layout'} .= ',';                                                #161
						$va{'cod_layout'} .= ',';                                                #162
						$va{'cod_layout'} .= ',';                                                #163
						$va{'cod_layout'} .= ',';                                                #164
						$va{'cod_layout'} .= ',';                                                #165
						$va{'cod_layout'} .= ',';                                                #166
						$va{'cod_layout'} .= ',';                                                #167
						$va{'cod_layout'} .= ',';                                                #168
						$va{'cod_layout'} .= ',';                                                #169
						$va{'cod_layout'} .= '';                                                 #170			 
						$va{'cod_layout'} .= "\r\n"; 
															
						$count_process++; 	
						
						####Global Layout TDC									
				 		push(@cod_layout, $va{'cod_layout'});	 
				 		$va{'all_idorders'} .="$rec->{'ID_orders'},";

				 		## Nota orden enviada en batch		

						&add_order_notes_by_type($ids_cod[$i],&trans_txt('order_batchsent')." $in{'id_warehouses_batches'}","High");
						## Log
						&auth_logging('order_batchsent', $ids_cod[$i]);
					 
					}#end while			
				
				}#end for ids

				if($va{'all_idorders'} ne ''){
					chop($va{'all_idorders'});
					my ($sth_c3) = &Do_SQL("SELECT sl_orders_products.ID_orders_products 
											FROM sl_orders 
											INNER JOIN sl_orders_products
											ON sl_orders_products.ID_orders=sl_orders.ID_orders
											INNER JOIN sl_warehouses_batches_orders
											ON sl_orders_products.ID_orders_products=sl_warehouses_batches_orders.ID_orders_products
											WHERE sl_orders.ID_orders IN(".$va{'all_idorders'}.")
											GROUP BY sl_orders_products.ID_orders_products"); 

					while ($rec_all = $sth_c3->fetchrow_hashref()){
						$va{'wh_ordersproducts'} .= $rec_all->{'ID_orders_products'}.',';
					}
					chop($va{'wh_ordersproducts'});
					my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches_orders SET Status='Shipped' WHERE ID_orders_products IN($va{'wh_ordersproducts'})");
				}
				
				if( $count_process > 0) {
					##### Save to a File orders process
					if (open(my $auth, ">>",$fname)) {
						
						####tdc
						for my $i(0..$#tdc_layout) {
							print $auth $tdc_layout[$i];													
						}		
						####cod	
						for my $j(0..$#cod_layout) {
							print $auth $cod_layout[$j];													
						}			

					}else{
						&cgierr("Unable to open $fname");
					}
					chmod (0666, $fname);
				}
		    }
	    }
		
		if($count_process>0){
			my ($sth) = &Do_SQL("UPDATE sl_warehouses_batches SET Status='Sent' WHERE ID_warehouses_batches=$in{'id_warehouses_batches'};");
			my ($sth) = &Do_SQL("INSERT INTO sl_warehouses_batches_notes SET Notes='".&trans_txt('warehouses_batches_send')."',Type='Low',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}', ID_warehouses_batches='$in{'id_warehouses_batches'}';");
		    &auth_logging('batches_sent',$in{'id_warehouses_batches'});
		    $va{'message'} = &trans_txt('warehouses_batches_send');
			delete($in{'chgsr'});
		}elsif($count_process==0){
			$va{'message'} = &trans_txt('warehouses_batches_notorders');
		}
	 
	}
	
	if($in{'cancelr'}){
		
		my ($sthr) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches WHERE Status IN ('New','Assigned') AND ID_warehouses_batches=$in{'id_warehouses_batches'}");
	    if ($sthr->fetchrow>0){	

	    	my ($sthd) = &Do_SQL("SELECT ID_orders FROM sl_orders_products INNER JOIN sl_warehouses_batches_orders USING(ID_orders_products)  
	    						WHERE ID_warehouses_batches = '".&filter_values($in{'id_warehouses_batches'})."' 
	    						GROUP BY ID_orders;");
	    	while(my ($id_orders) = $sthd->fetchrow()){

				## Nota y Log para orden asignada
				$in{'db'} = 'sl_orders';
				## Nota orden enviada en batch		

				&add_order_notes_by_type($id_orders,&trans_txt('order_batchdropped')." $in{'id_warehouses_batches'}","High");
				&auth_logging('order_batchdropped', $id_orders);

	    	}					

	    	$Query = "DELETE FROM sl_warehouses_batches_orders  WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'});
			($sth_upd) = &Do_SQL($Query);
			my $wh_status = &load_name('sl_warehouses_batches','ID_warehouses_batches',int($in{'id_warehouses_batches'}),'Status');
			$Query = "UPDATE sl_warehouses_batches SET Status='New' WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'});
			($sth_up) = &Do_SQL($Query);
		    
		    $in{'db'} = 'sl_warehouses_batches';
		    &auth_logging('warehouses_batches_cancelled',&filter_values($in{'id_warehouses_batches'}));		    
	    }
	}
	
	if($in{'chg_process'}){
		my ($sthr) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses_batches WHERE Status IN ('Assigned') AND ID_warehouses_batches=$in{'id_warehouses_batches'}");
	    if ($sthr->fetchrow>0){	
			$Query = "UPDATE sl_warehouses_batches SET Status='Processed' WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'});
			($sth_up) = &Do_SQL($Query);
		    
		    $in{'db'} = 'sl_warehouses_batches';
		    &auth_logging('warehouses_batches_change_status',&filter_values($in{'id_warehouses_batches'}));		
		    $va{'message'} = &trans_txt('warehouses_batches_process');    
	    }
	}
	
	
	if ($in{'process'}){
     
		### Insert Remesas Orders 
		my $Query = "SELECT ID_orders, ID_orders_products FROM sl_orders_products WHERE ID_orders IN(".$in{'ordersselected'}.");";
		my ($sth) = &Do_SQL($Query);
		my ($ids);

		while ($rec = $sth->fetchrow_hashref){
			$Query = "SELECT COUNT(*) FROM sl_warehouses_batches_orders WHERE ID_orders_products = '$rec->{'ID_orders_products'}';";
			
			($sth2) = &Do_SQL($Query);
			($count)=$sth2->fetchrow_array();
			if($count == 0 ){
				$Query = "INSERT INTO sl_warehouses_batches_orders SET ID_warehouses_batches=".$in{'id_warehouses_batches'}.", ID_orders_products=".int($rec->{'ID_orders_products'}).", Status='In Fulfillment', Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'; ";
				($sth3) = &Do_SQL($Query);
			}


			if($rec->{'ID_orders_products'} !~ /$ids/) {

				## Nota y Log para orden asignada
				$in{'db'} = 'sl_orders';
				## Nota orden enviada en batch		

				&add_order_notes_by_type($id_orders,&trans_txt('order_batchadded')." $in{'id_warehouses_batches'}","High");
				&auth_logging('order_batchadded', $id_orders);

				$ids .= qq|$rec->{'ID_orders'}&|;

			}

		}

	}
	
	if($in{'ordersselected'} eq ''){
		$in{'ordersselected'}= 0;
	}
	
	####Process button
	my $so = &load_name('sl_warehouses_batches','ID_warehouses_batches',$in{'id_warehouses_batches'},'Status');
	$va{'change'}=''; 
	 
    if($so eq "Assigned"){
	    $va{'change'} .= qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_warehouses_batches]&chg_process=$in{'id_warehouses_batches'}">Processed</a>&nbsp;&nbsp;|; 
    }
    
    if($so eq "Processed"){
	    $va{'change'} .= qq|<a href="#" onClick="to_sent();return false;">Sent</a>&nbsp;&nbsp;|; 
    }
    
	if($so =~ /Assigned|New/){
		$va{'change'} .= qq|<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=[in_cmd]&view=[in_id_warehouses_batches]&cancelr=$in{'id_warehouses_batches'}">Cancelled</a>&nbsp;&nbsp;|;
	}
	
	$va{'message_status'} = 'Change Status to:';
	if($so eq "Sent"){
		$va{'message_status'}='';
	} 	
	$va{'status_remesas'} = qq|<tr>
		<td valign="top" width="30%" valign="top">Status: </td> 
		<td class="smalltext" valign="top">$so &nbsp;&nbsp;&nbsp; <span class='smalltext'>$va{'message_status'} |.$va{'change'}.qq|</span></td>
		</tr>|;
    
    ###Warehouses string
    my $Query = "SELECT ID_warehouses, Name FROM sl_warehouses WHERE Type IN('Virtual','Outsource') AND Status='Active' AND ID_warehouses NOT IN(".$in{'id_warehouses'}.")";
    $sth = &Do_SQL($Query);
	while ($rec = $sth->fetchrow_hashref){
		$va{'wh_optionsdet'} .= qq|'$rec->{'ID_warehouses'}':'$rec->{'ID_warehouses'} -- $rec->{'Name'}',|;
	}
	chop($va{'wh_optionsdet'});
	$va{'wh_options'} = "options:{".$va{'wh_optionsdet'}."}";    
	
	####Change option
	if($so =~ /Assigned|New/){
		$va{'chg_remesa'} = qq|<span id="span_chg_wh">
			    		<img style="cursor:pointer;" title="Click to change warehouse" src="/sitimages/default/b_edit.png" id="btn_chg_wh">
			    	</span>|;
	}
	

	if($in{'id_warehouses'} eq '' && $in{'id_warehouses_batches'} ){
		my $sth = &Do_SQL("SELECT ID_warehouses  FROM sl_warehouses_batches WHERE ID_warehouses_batches=".&filter_values($in{'id_warehouses_batches'}));
		$in{'id_warehouses'} = $sth->fetchrow;
	}


	################################################
	################################################
	################################################
	################################################
	###########
	########### Impresion
	###########
	################################################
	################################################
	################################################
	################################################


	### PAra formato 5, mandamos llamar al print de orders
	warehouses_batches_rewrite_print_f5();
	warehouses_batches_rewrite_print_f6();

	my (%tmpord);
	if ($in{'toprint'}){		
		
		my $fn = 'warehouses_batches_execute_print_f' . $in{'f'};
		#&cgierr($fn);
		if( defined &$fn ) {
			&$fn();
		}


	}


	################################################
	################################################
	################################################
	################################################
	###########
	########### Exportacion
	###########
	################################################
	################################################
	################################################
	################################################
	$va{'export_perm'} = &check_permissions('warehouses_batches','_export','');	
	if($in{'export'}){

		my $fn = 'warehouses_batches_export';
		#&cgierr($fn);
		if( defined &$fn ) {
			&$fn();
			exit;
		}

	}
	
	
}


##########################################################
##		CUSTOMS INFO
##########################################################
sub view_opr_customs_info {

	if( $in{'id_vendors'} ){
		my $sth = &Do_SQL("SELECT CompanyName, Currency FROM sl_vendors WHERE ID_vendors = ".$in{'id_vendors'})->fetchrow_hashref();
		$va{'company_name'} = $sth->{'CompanyName'};
		$va{'currency'} = $sth->{'Currency'};
	}

}

1;