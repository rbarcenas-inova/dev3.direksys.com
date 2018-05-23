#!/usr/bin/perl
####################################################################
###
###        STOP !!!!!!!!!!!!!
###
###
###     NO MODIFICAR RUTINAS EN ESTA APLICACION
###
###
###    SOLO PARA PRUEBA AGREGAR 
###    &cgierr('P-Nombre:comments')  TEMPORALMENTE!!!!!!!!!
###
####################################################################


						##################################################################
						##################################################################
						##################################################################
						#
						#						Aciones Movimientos Contables
						#
						##################################################################
						##################################################################
						##################################################################


#############################################################################
#############################################################################
#   Function: order_refund
#
#       Es: Inserta el movimiento de contabilidad por el refund
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *09/21/09* by _Roberto Barcenas_ : Se separa la categoria en Sale|Refund para saber cuando es un Refund por pago mayor en una venta e incluir este rango en el apartado de Sales Facts del closebatch.
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_orders,$id_payments)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub order_refund_e8 {
#############################################################################
#############################################################################
 	
	my ($param_data) = @_;
	my ($id_orders,$id_payments);

	$id_orders = @{$param_data}[0];
	$id_payments = @{$param_data}[1];
	
	## Has Return Movements Already?
	my ($sth) = &Do_SQL("SELECT IF(COUNT(*) = 0, 'Sale', 'Refund')AS type FROM sl_movements WHERE ID_tableused = '$id_orders' AND Category = 'Return'; ");
	my ($rtype) = $sth->fetchrow();

	
	my $amount = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'Amount*-1');
	&general_deposits($id_payments,$id_orders,'orders','Refund',$rtype,'N/A','CURDATE','CURDATE',$amount);
	my ($sth) = &Do_SQL("UPDATE sl_movements SET Status = 'Active',EffDate=CURDATE() WHERE tableused='sl_orders' AND ID_tableused = '$id_orders' AND Status='Pending' ;");

	return;
}
	


###############
###############
############### Inventory
###############
###############



#############################################################################
#############################################################################
#   Function: accounting_wreceipt_inventory_in
#
#       Es: Recibe la mercancia de un PO vs AP o Prepaid segun sea el caso
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos (id_po, $qty, $cost)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_wreceipt_inventory_in_e8 {
#############################################################################
#############################################################################


	my ($param_data) = @_;
	my ($id_po,$qty,$cost,$amt);

	$id_po = @{$param_data}[0];
	$qty = @{$param_data}[1];
	$cost = @{$param_data}[2];
	$amt = $qty*$cost;
	
	my ($sth) = &Do_SQL("SELECT 
					IF(WPay IS NULL,0,WPay) AS WPay,
					/*IF(Payments IS NULL,0,Payments)AS Paid*/
					0 AS Paid
					FROM sl_purchaseorders
					LEFT JOIN
					(
						SELECT ID_purchaseorders, SUM( Received * Price ) AS Wpay
						FROM sl_purchaseorders_items
						WHERE ID_purchaseorders = $id_po
						GROUP BY ID_purchaseorders
					)AS tmp_po
					ON sl_purchaseorders.ID_purchaseorders = tmp_po.ID_purchaseorders
					/*
					LEFT JOIN
					(
						SELECT ID_purchaseorders, SUM( Amount ) AS Payments
						FROM sl_vendors_payments
						WHERE ID_purchaseorders = $id_po
						GROUP BY ID_purchaseorders
					)AS tmp_pay
					ON sl_purchaseorders.ID_purchaseorders = tmp_pay.ID_purchaseorders
					*/
					WHERE sl_purchaseorders.ID_purchaseorders = $id_po");
																	
	my($received,$paid) = $sth->fetchrow();
	
	####### Si no se ha hecho ningun prepago o lo pagado es menor que lo recibido todo va a accounts payable
	if($paid == 0 or $paid <= $received){
		&general_deposits(0,$id_po,'purchaseorders','Inventory Payable',"Inventory",'N/A','N/A','N/A',$amt);
	####### Si no se habia recibido nada hasta ahora	
	}else{
		### Si se tiene a favor prepaid y cubre por completo lo recibido todo va vs Prepaid
		if($paid - $received >= $amt){
			&general_deposits(0,$id_po,'purchaseorders','Inventory Prepaid',"Inventory",'N/A','N/A','N/A',$amt);
		### Se tiene prepaid pero no cubre por completo lo recibido, se tiene que hacer un mix entre prepaid y payable
		}else{
			&general_deposits(0,$id_po,'purchaseorders','Inventory Prepaid',"Inventory",'N/A','N/A','N/A',$paid - $received);
			$amt = $amt - ($paid - $received);
			&general_deposits(0,$id_po,'purchaseorders','Inventory Payable',"Inventory",'N/A','N/A','N/A',$amt);
		}
	}

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_adjustment
#
#       Es: Genera los movimientos contables cuando se realiza un ajuste de inventario
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($wrong_inventory,$real_inventory,$id_adjustments,$amt)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_adjustment_e8 {
#############################################################################
#############################################################################

	my ($param_data) = @_;
	my ($id_adjustments,$adjustment,$amt);

	$id_adjustments = @{$param_data}[0];
	$adjustment = @{$param_data}[1];
	$amt = @{$param_data}[2];

	
	($adjustment < 0) ?
		#### Si el inventario en sistema era mayor que el real, se hace entrada Inventory Adjustment(201) vs  Inventory Assets(89)
		&general_deposits(0,$id_adjustments,'adjustments','LA Main Negative Adj','Expense','N/A','N/A','N/A',$amt) :
		#### Si el inventario en sistema era menor que el real, se hace entrada Inventory Assets(89) vs Inventory Adjustment(201)
		&general_deposits(0,$id_adjustments,'adjustments','LA Main Positive Adj','Income','N/A','N/A','N/A',$amt);

	return;	
}


#############################################################################
#############################################################################
#   Function: accounting_adjustment
#
#       Es: Genera los Movimientos contables cuando se devuelve mercancia al vendedor.
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_warehouses, $wrong_inventory,$real_inventory,$id_adjustments,$amt)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_return_vendor_e8 {
#############################################################################
#############################################################################

	my ($param_data) = @_;
	my $idpo = @{$param_data}[0];

	my $id_vendors = &load_name('sl_purchaseorders','ID_purchaseorders',$id_po,'ID_vendors');
	my $inv_p = get_account('Prepaid Inventory');
	my $acc_p = get_account('Accounts Payable Trade'); 
	
	my ($sth) = &Do_SQL("SELECT SUM(Qty*Price)AS total FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$id_po';");
	my ($returned) = $sth->fetchrow();
	
	my ($sth) = &Do_SQL("SELECT 
					SUM(IF(Credebit='Debit',Amount,0)) AS Debits,
					SUM(IF(Credebit='Credit',Amount,0)) AS Credits
					FROM `sl_movements`
					INNER JOIN sl_purchaseorders ON sl_purchaseorders.ID_purchaseorders = sl_movements.`ID_tableused`
					WHERE `ID_accounts`
					IN ( $inv_p,$acc_p)
					AND `tableused` = 'sl_purchaseorders'
					AND ID_vendors = $id_vendors
					AND sl_movements.Status != 'Inactive'
					GROUP BY ID_vendors;");
	my ($debits,$credits) = $sth->fetchrow();
	
	### Si la cantidad de credits - debits es masyor o igual que el amount del return, entonces debemos decrecer el AP del vendor
	if($credits - $debits >= $returned){
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Payable','Income','N/A','N/A','N/A',$returned);
	### Si la cantidad de credits es mayor que debits pero la resta no es mayor o igual que el amount del return, entonces debemos hacer entrada en ambas cuentas
	}elsif($credits > $debits){
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Payable','Income','N/A','N/A','N/A',$credits-$debits);
		$returned = $returned - ($credits-$debits);
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Prepaid','Income','N/A','N/A','N/A',$returned);
	### Si debits es mayor que credits hacemos una entrada en Prepaid Inventory
	}else{
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Prepaid','Income','N/A','N/A','N/A',$returned);
	}											
}


1;
