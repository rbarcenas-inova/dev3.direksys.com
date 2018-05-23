#!/usr/bin/perl


## Use MD5Verification for sl_movements
$va{'md5verification_exists'} = $va{'md5verification_exists'} ? $va{'md5verification_exists'} : &table_field_exists('sl_movements','MD5Verification');

######################################################################################################
######################################################################################################
###
###       
###
###
###     			FUNCIONES ESPECIFICAS PARA MOVIMIENTOS CONTABLES
###
###			Commit your transactions immediately after making a set of related changes. 
###			Small transactions are less prone to collision. 
###			In particular, do not leave an interactive mysql session open for a long time with an uncommitted transaction.
###    
###    
###
######################################################################################################
######################################################################################################


#############################################################################
#############################################################################
#   Function: general_deposits
#
#       Es: Devuelve el tipo al que pertenece el pago
#       En: 
#
#
#    Created on: 06/15/09 12:27:10
#
#    Author: MCC C. Gabriel Varela S.
#
#    Modifications:
#
#        
#
#   Parameters:
#
#       - $id_payments: ID del pago si es que es un deposito
#		- $idtable: ID de la tabla por el concepto que se generara el movimiento contable,
#		- $tablename: Nombre de la tabla padre del movimiento contable,
#		- $keypoint: Keypoint a buscar en sl_keypoints_movements,
#		- $category: Categoria del movimiento contable,
#		- $cond1: Condicion 1,
#		- $cond2: Condicion 2,
#		- $cond3: Condicion 3,
#		- $amount: Monto del movimiento
#
#  Returns:
#
#      - 
#
#   See Also:
#
#			<load_accounts>
#
sub general_deposits {
#############################################################################
#############################################################################


	my ($id_payments,$idtable,$tablename,$keypoint,$category,$cond1,$cond2,$cond3,$amount) = @_;
	my @ary_debit_ids;
	my @ary_credit_ids;


	return (@ary_debit_ids, @ary_credit_ids) if $amount == 0;

	## Determinamos si es un tipo de pago y si se debe activar de inmediato o no el movimiento contable
	#!$id_payments or
	
	my $type = $id_payments == -1 ? 'N/A' : &get_deposit_type($id_payments,$keypoint);
	my $status = $id_payments == -1 ? 'Pending' : 'Active';
	
	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';	
	my @accountsc = &load_accounts($keypoint,$cond1,$cond2,$cond3,$type,'credit');
	
	for(0..$#accountsc){

		if ($accountsc[$_]){

			my ($sth) = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time, ID_admin_users )
								VALUES (". $accountsc[$_] .", ". $amount .", '', CURDATE(), 'sl_$tablename', '$idtable', '$category', 'Credit', ". $md5time_value ." '$status',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			my $this_movement = $sth->{'mysql_insertid'};
			push(@ary_credit_ids, $this_movement);
		}

	}

	my @accountsd = &load_accounts($keypoint,$cond1,$cond2,$cond3,$type,'debit');
	for(0..$#accountsd){

		if ($accountsd[$_]){

			my ($sth) = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused , ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time, ID_admin_users )
								VALUES (". $accountsd[$_] .", ". $amount .", '', CURDATE(), 'sl_$tablename', '$idtable', '$category', 'Debit', ". $md5time_value ." '$status', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			my $this_movement = $sth->{'mysql_insertid'};
			push(@ary_debit_ids, $this_movement);

		}

	}

	##### Segments?
	&accounting_set_segment($idtable, $tablename);

	##### Reference?
	($in{'acc_reference'}) and (&Do_SQL("UPDATE sl_movements SET Reference = '". $in{'acc_reference'} ."' WHERE ID_tableused = '". $idtable ."' AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0;") );

	#return ( join(':', @ary_debit_ids), join(':', @ary_credit_ids) );
	return ( \@ary_debit_ids, \@ary_credit_ids );

}


#############################################################################
#############################################################################
#   Function: load_accounts
#
#       Es: Devuelve las cuentas contables a las que cuales aplicar el movimiento contable
#       En: 
#
#
#    Created on: 06/15/09 15:37:44
#
#    Author: MCC C. Gabriel Varela S.
#
#    Modifications:
#
#
#   Parameters:
#
#		- $keypoint,
#		- $cond1,
#		- $cond2,
#		- $cond3,
#		- $type,
#		-$credebit
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<load_accounts>
#
#
sub load_accounts {
#############################################################################
#############################################################################

	my ($keypoint,$cond1,$cond2,$cond3,$type,$credebit) = @_;
	my ($cond1cad, $cond2cad, $cond3cad, $typecad);
	my @accounts;
	$cond1cad=" and cond1='$cond1' " if($cond1);
	$cond2cad=" and cond2='$cond2' " if($cond2);
	$cond3cad=" and cond3='$cond3' " if($cond3);
	my $modtype = $in{'ida_banks'} ? "AND ID_accounts_debit = '$in{'ida_banks'}'" : '';
	$typecad=" AND ( (LOWER(type) = LOWER('$type') $modtype) OR (not isnull(Suboperation) AND Suboperation!='N/A')) " if($type);

	my $credebitcad=" AND (ID_accounts_$credebit!=0 OR (NOT ISNULL(Suboperation) and Suboperation!='N/A'))";
	#&cgierr("SELECT * FROM sl_keypoints_movements WHERE keypoint LIKE '$keypoint' $cond1cad $cond2cad $cond3cad $typecad $credebitcad AND Status='Active'");
	my $sth=&Do_SQL("SELECT * FROM sl_keypoints_movements WHERE keypoint LIKE '$keypoint' $cond1cad $cond2cad $cond3cad $typecad $credebitcad AND Status='Active'");

	while(my $rec=$sth->fetchrow_hashref){
		push @accounts,$rec->{"ID_accounts_$credebit"} if($rec->{"ID_accounts_$credebit"});
		push @accounts,&load_accounts($rec->{'Suboperation'},$rec->{'Cond1'},$rec->{'Cond2'},$rec->{'Cond3'},$type,$credebit) if($rec->{'Suboperation'}ne'' and $rec->{'Suboperation'}ne'N/A');
	}


	return @accounts;
}


#############################################################################
#############################################################################
#   Function: retrieve_cond
#
#       Es: Devuelve cadena con condiciones
#       En: 
#
#
#    Created on: 06/15/09 15:37:44
#
#    Author: MCC C. Gabriel Varela S.
#
#    Modifications:
#
#
#   Parameters:
#
#		- $id,
#		- $tablename
#		- $productpayment
#		- $datetype
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<general_deposits>
#
#
sub retrieve_cond {
#############################################################################
#############################################################################

	($id,$tablename,$productpayment,$datetype)=@_;
	$cond=&load_name("sl_".$tablename."_$productpayment","ID_".$tablename."_$productpayment",$id,$datetype);
	$sth=&Do_SQL("SELECT IF('$cond'='' or '$cond'='0000-00-00','0000-00-00',
       IF('$cond'=curdate(),'CURDATE',
       IF('$cond'<=curdate(),'<=CURDATE',
       IF('$cond'<CURDATE(),'<CURDATE',
       '!=0000-00-00'))))AS Cond");

	return $sth->fetchrow;
}


#############################################################################
#############################################################################
#   Function: get_iomovement_category
#
#       Es: Devuelve la categoria de un inventory out basado en el postedDate de la orden
#       En: 
#
#
#    Created on: 06/17/09  10:08:34
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#		- $id_orders_products
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<general_deposits>
#
#
sub get_iomovement_category {
#############################################################################
#############################################################################

	my ($id_orders_products) =	@_;
	
	my $sth = &Do_SQL("SELECT 
						IF(sl_orders.PostedDate >= sl_orders_products.PostedDate OR sl_orders.PostedDate = '0000-00-00','Ventas','Cambios Fisicos') AS category 
				FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders WHERE ID_orders_products = '$id_orders_products';");
	
	return $sth->fetchrow();
}


#############################################################################
#############################################################################
#   Function: sale_today
#
#       Es: Devuelve 1,0 dependiendo de si la operacion de venta para (product, service, discount, shipping,tax) ya se registro o no.
#       En: 
#
#
#    Created on: 06/18/09  11:21:46
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#		- $id_orders_products
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<accounting_sale>
#
#
sub sale_today {
#############################################################################
#############################################################################
	
	my ($id_account,$amount,$id_orders,$credebit) = @_;
	my $sth = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_accounts = '$id_account' AND Amount='$amount' AND tableused = 'sl_orders' AND ID_tableused = '$id_orders' AND Credebit = '$credebit' AND Status='Active' AND Date = CURDATE();");
	
	return $sth->fetchrow();

}


sub get_account{
#-----------------------------------------
# Created on: 06/30/09  11:47:47 By  Roberto Barcenas
# Forms Involved: 
# Description : Devuelve el id de una cuenta
# Parameters : 	Nombre de la cuenta
## ToDo: Agregar en un campo el tipo de Movimiento. Ejemplo - Customer Deposit y ahi buscar los que sean de ese tipo
## Devolver los ID's en un GROUP_CONCAT()
	
	my ($account) = @_;
	
	my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_accounts WHERE Name='$account';");
	return $sth->fetchrow();
}


#############################################################################
#############################################################################
#   Function: accounting_group_amounts
#
#       Es: Agrupa montos por cuenta contable
#       En: 
#
#
#    Created on: 06/01/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - tableused: 
#		- id_tableused
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_group_amounts{
#############################################################################
#############################################################################

	my ($tableused, $id_tableused) = @_;

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) <= 1|;

	my ($sth) = &Do_SQL("SELECT ID_accounts,Credebit,Amount,movs,ID_movs FROM
						(
							SELECT 
								ID_accounts
								, Credebit
								, IFNULL(Reference, 'NA')as Reference
								, COUNT(*)AS movs
								, SUM(Amount)AS Amount
								, GROUP_CONCAT(ID_movements)AS ID_movs 
							FROM sl_movements 
							WHERE 
								tableused = '". $tableused ."' 
								AND ID_tableused = '". $id_tableused ."' 
								AND Status = 'Active' 
								AND (ID_journalentries IS NULL OR ID_journalentries = 0) 
								AND ". $sqlmod_update_records ."
							GROUP BY 
								ID_accounts
								, ID_tablerelated
								, tablerelated
								, Credebit
								, Reference 
								, EffDate
								, Category
								, ID_segments
						)tmp
						HAVING movs > 1 ORDER BY Credebit,ID_accounts;");
	while(my ($id_accounts, $credebit, $amount, $movs, $ids) = $sth->fetchrow() ){

		my @ary = split(/,/, $ids);
		my $i=0;

		for (0..$#ary){

			my $id_movements = int($ary[$i]);
			if($i == 0){
				&Do_SQL("UPDATE sl_movements SET Amount = '". $amount ."' WHERE ID_movements = '". $id_movements ."';");
			}else{
				&Do_SQL("DELETE FROM sl_movements WHERE ID_movements = '". $id_movements ."';");
			}

			$i++;
		}

	}

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_set_segment
#
#       Es: Marca el segmento en la operacion
#       En: 
#
#
#    Created on: 06/01/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - tableused: 
#		- id_tableused
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_set_segment{
#############################################################################
#############################################################################

	my ($idtable, $tablename) = @_;


	if($cfg{'accounting_use_segments'}) {

		my ($id_segments);

		if($tablename eq 'orders') {

			my $id_salesorigins = &load_name('sl_orders','ID_orders',$idtable,'ID_salesorigins');
			(!$id_salesorigins) and ($id_salesorigins = $cfg{'default_origin'});
			my ($sth) = &Do_SQL("SELECT ID_accounts_segments FROM sl_salesorigins WHERE ID_salesorigins = '$id_salesorigins' LIMIT 1;");
			$id_segments = $sth->fetchrow();
		
		}elsif($in{'id_segments'}) {
			$id_segments = int($in{'id_segments'});
		}
		
		if($id_segments) {

			&Do_SQL("SET group_concat_max_len = 204800;");
			my ($stha) = &Do_SQL("SELECT GROUP_CONCAT(ID_accounts) FROM sl_accounts WHERE Segment =  'Yes';");
			my ($id_accounts_grouped) = $stha->fetchrow();

			if($id_accounts_grouped){
				my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_segments = '$id_segments' WHERE ID_tableused = '$idtable' AND ID_segments = 0 AND ID_accounts IN($id_accounts_grouped) AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0 ;");
			}

		}

	}

}


#############################################################################
#############################################################################
#   Function: accounting_set_automatic_journal
#
#       Es: Agrega un ID_journalentries automatico a los movimientos contables de cierta categoria de acuerdo a configuracion
#       En: 
#
#
#    Created on: 01/22/2015
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - id_tableused: ID tabla principal
#      - tableused: tabla principal
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_set_automatic_journal {
#############################################################################
#############################################################################

	my ($id_tableused, $tableused) = @_;

	if($cfg{'acc_journalauto'}){

		my @ary_cat = split(/\|/, $cfg{'acc_journalauto_categories'});
		for(0..$#ary_cat){

			## Extraemos ID_journal
			my $category = &filter_values($ary_cat[$_]);
			my $id_journalentries = create_journalentries($category);

			## Movimientos por asignar
			my ($sth) = &Do_SQL("UPDATE sl_movements SET ID_journalentries = '$id_journalentries' WHERE ID_tableused = '$id_tableused' AND tableused = '$tableused' AND Category = '$category' AND Status = 'Active' AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',TIME),NOW()) BETWEEN 0 AND 1 AND (ID_journalentries IS NULL OR ID_journalentries = 0);");

		}

	}

	return;
}


######################################################################################################
######################################################################################################
###
###       
###
###
###     			FUNCIONES ESPECIFICAS PARA MOVIMIENTOS CONTABLES
###
###
###    
###    
###
######################################################################################################
######################################################################################################


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
#   Function: order_deposit_americanexpress
#
#       Es: Genera movimientos contables derivados de depositos Capturados American Express. Se revisa descuento de comision cobrada por el banco por la transaccion
#       En: 
#
#
#    Created on: 02/16/013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#   Parameters:
#
#      - param_data: arreglo con id_orders, $id_payments
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_keypoints>
#      <accounting_order_deposit>
#
sub order_deposit_americanexpress{
#############################################################################
#############################################################################

	my (@param_data) = @_;
	my ($id_orders,$id_payments,$amount,$exchange_rate);

	$id_orders = int($param_data[0]);  
	$id_payments = int($param_data[1]);
	$amount = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'Amount');
	$amount = &round($amount * $exchange_rate,3);

	if($amount > 0) {
		
		## ToDo: Donde ponemos el numero de pagos?
		my ($sth) = &Do_SQL("SELECT IF(MAX(FP) < 1,1,MAX(FP)) FROM sl_orders_products WHERE ID_orders = '$id_orders';");
		my($fp) = $sth->fetchrow();

		my ($sth) = &Do_SQL("SELECT VValue/100 FROM sl_vars WHERE VName = 'comision_americanexpress' AND Subcode <= $fp ORDER BY Subcode DESC LIMIT 1;");
		my ($feepct) = $sth->fetchrow();

		if($feepct) {

			my $famount = round($amount - ($amount * $feepct),2); #1001.69 +
			my $aefee = round($amount - $famount,2); #25.68
			my $faefee = round($aefee - ($aefee * $cfg{'taxp_default'}),2); #21.58 +
			my $ftaxfee = $aefee - $faefee; #4.1
			my $id_products = 600000000 + $cfg{'bankfeesid'};

			#&cgierr("$famount - ($aefee)$faefee - $ftaxfee");
			## 1)Movimientos de descuento por comision 2685778.88 - (68866.12)57847.54 - 11018.58
			## New Service negative
			#&Do_SQL("_INSERT INTO sl_orders_products SET ID_products='$id_products',ID_orders='$id_orders',ID_packinglist='0',Quantity='1',SalePrice='-$aefee',Shipping='0',Cost='0',Tax='0',Discount='0',Status='Active',PostedDate='0000-00-00',Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");

			## 2) Payment adjustment
			&Do_SQL("UPDATE sl_orders_payments SET Amount = '$famount' WHERE ID_orders_payments = '$id_payments' AND Amount = '$amount' /*AND Captured = 'Yes' AND CapDate = CURDATE()*/;");
			## 3)Accounting movements for captured deposit
			&order_deposit(@param_data);
			&Do_SQL("UPDATE sl_orders_payments SET Amount = '$amount' WHERE ID_orders_payments = '$id_payments' AND Amount = '$amount' AND Captured = 'Yes' AND CapDate = CURDATE();");
			&Do_SQL("UPDATE sl_movements SET Amount = '$amount' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND Date=CURDATE() AND Amount = '$famount';");

			## ToDo: Donde estan estos movimientos?
			## 4)Accounting Movements
			&general_deposits(0,$id_orders,'orders','Customer Deposit Bank Fees','Anticipo Clientes','N/A','N/A','N/A',$faefee) if $faefee > 0;
			&general_deposits(0,$id_orders,'orders','Customer Deposit Bank Fees Tax','Anticipo Clientes','N/A','N/A','N/A',$ftaxfee)	if $ftaxfee > 0;

		}

	}

	return;
}


#############################################################################
#############################################################################
#   Function: order_deposit
#
#       Es: Genera movimientos contables derivados de depositos de dinero para una orden.
#       En: 
#
#
#    Created on: 06/15/09 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *06/30/09* by _Roberto Barcenas_ : El primer deposito siempre crea bank vs customer deposit
#        - Modified on *09/21/09* by _Roberto Barcenas_ : El pago de exchange o deposito de flexipago se mandan a buscar al keypoint y no se envian directo a TC
#        - Modified on *11/08/12* by _Roberto Barcenas_ : Los parametros de entrada vienen en un arreglo debido a que la funcion ya no es llamada directamente sino por medio de accounting_keypoints
#        - Modified on *07/01/13* by _Roberto Barcenas_ : Se agrega el valor de $in{'bankdate'}, que indica la fecha de aplicacion. Se utiliza para la busqueda y para hacer un update de los registros al final 
#		 - Modified on *08/04/13* by _Roberto Barcenas_ : Se vuelve a poner fecha efectiva de banco como el CURDATE()
#		 - Modified on *02/03/15* by _Roberto Barcenas_ : Se cambia categoria en Cambios Fisicos por Anticipo Clientes Lizbeth Parada
#		 - Modified on *05/29/15* by _Roberto Barcenas_ : Se modifica elsif por $pd_order == 1 or $sale_movements
#		 - Modified on *06/11/15* by _Roberto Barcenas_ : Se agrega parametro $exchange_rate pasado por funcion como 3er parametro
#
#
#   Parameters:
#
#      - param_data: arreglo con id_orders, $id_payments
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_keypoints>
#      <accounting_order_deposit>
#
sub order_deposit {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $this_rounded_amount = 0;
	($in{'ida_banks'}) and (delete($in{'ida_banks'})); #$id_banks_movements -- order_deposit_Distribuidores_Wire Transfer_deposit --- 721, 702 ,604

	## Parametros pasados por funcion
	my $id_orders = int($param_data[0]);
	my $id_payments = int($param_data[1]);
	$in{'ida_banks'} = int($param_data[2]) if scalar (@param_data) == 13; ## Se usa cuando se paga con un banco. Si el dato es cero, se buscara de acuerdo a la configuracion
	if($in{'ida_banks'} == -1){ $this_rounded_amount = 1; delete($in{'ida_banks'}); }
	my $exchange_rate = scalar (@param_data) == 13 ? &filter_values($param_data[3]) : &filter_values($param_data[2]);
	## Parametros pasados por configuracion
	my $ida_sale = scalar (@param_data) == 13 ? &filter_values($param_data[4]) : &filter_values($param_data[3]);
	my $ida_taxes = scalar (@param_data) == 13 ? &filter_values($param_data[5]) : &filter_values($param_data[4]);
	my $ida_banks = scalar (@param_data) == 13 ? &filter_values($param_data[6]) : &filter_values($param_data[5]);
	my $ida_deposits = scalar (@param_data) == 13 ? &filter_values($param_data[7]) : &filter_values($param_data[6]);
	my $ida_bank_debit_credit = scalar (@param_data) == 13 ? &filter_values($param_data[8]) : &filter_values($param_data[7]);
	my $ida_customer = scalar (@param_data) == 13 ? &filter_values($param_data[9]) : &filter_values($param_data[8]);
	my $ida_profit = scalar (@param_data) == 13 ? int($param_data[10]) : int($param_data[9]);
	my $ida_lost = scalar (@param_data) == 13 ? int($param_data[11]) : int($param_data[10]);
	my $ida_difference = scalar (@param_data) == 13 ? int($param_data[12]) : int($param_data[11]);

	my $str_params = join("\n", @param_data);
	
	my $str_log = "-----------------------------------------------------------\n";
	$str_log .= "==> Log Order Deposit : $id_orders\n";
	$str_log .= "-----------------------------------------------------------\n";
	$str_log .= "str_params: ".$str_params."\n";

	my $this_acc = 0;
	my $this_acc_str;
	my $this_acc_action;

	#my $ida_customer_refund = scalar (@param_data) == 9 ? &filter_values($param_data[8]) : &filter_values($param_data[7]);
	(!$ida_bank_debit_credit) and ($ida_bank_debit_credit = 0);
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;
	$str_log .= "sqlmod_update_records: ".$sqlmod_update_records."\n";

	#my $moddate = $in{'bankdate'} ? "'$in{'bankdate'}'" : 'CURDATE()';
	my $moddate = 'CURDATE()';
	my $category = '';
	my $keypoint;
	
	### PostedDate Order
	my ($sth) = &Do_SQL("SELECT IF(PostedDate='0000-00-00' OR PostedDate IS NULL,0,IF(PostedDate <= ". $moddate ." ,1,2)) AS PDOrder FROM sl_orders WHERE ID_orders = '$id_orders' ");
	my ($pd_order) = $sth->fetchrow();
	$str_log .= "pd_order: ".$pd_order."\n";

	### La orden tiene movimientos de venta?
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND ID_accounts IN(".$ida_sale.") AND  tableused = 'sl_orders' AND Credebit = 'Credit' AND status= 'Active';");
	my($sale_movements) = $sth->fetchrow();
	$str_log .= "sale_movements: ".$sale_movements."\n";

	my $amount = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'Amount');
	my $amount_original = $amount;
	$str_log .= "amount_original: ".$amount_original."\n";

	### Parche del Exchangerate
	$exchange_rate = 1 if( $exchange_rate == 0 );
	
	$amount = round($amount * $exchange_rate,3);
	$str_log .= "amount: ".$amount."\n";

	#######
	####### Customer Country 
	#######
	my ($sth) = &Do_SQL("SELECT IF(sl_customers.Currency <> '' AND '". $cfg{'acc_default_currency'} ."' <> '' AND sl_customers.Currency <> '". $cfg{'acc_default_currency'} ."',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $id_orders ."' ;");
	my ($tcustomer) = $sth->fetchrow();
	$str_log .= "tcustomer: ".$tcustomer."\n";
	
	my $apply_profit_lost = 0;

	if(!$sale_movements){
	
		$this_acc_action = 'Sale';

		### Pagos en la orden?
		my ($sth) = &Do_SQL("SELECT Total,PrePaid,Paid,IF(Total-Paid = 0,0,Total-Paid) AS AR
						FROM sl_orders_payments INNER JOIN
						(SELECT ID_orders,
						SUM(Amount)AS Total,
						SUM(IF(CapDate IS NOT NULL AND CapDate !='0000-00-00' AND CapDate < $moddate,Amount,0)) AS Prepaid,
						SUM(IF(Captured = 'Yes' AND (CapDate IS NOT NULL AND CapDate !='0000-00-00'),Amount,0)) AS Paid
						FROM sl_orders_payments
						WHERE  ID_orders = '". $id_orders ."'
						AND Status NOT IN ('Void','Order Cancelled','Cancelled')
						GROUP BY ID_orders) AS tmpPaid
						ON tmpPaid.ID_orders = sl_orders_payments.ID_orders
						GROUP BY sl_orders_payments.ID_orders; ");

		my ($total,$prepaid,$paid,$ar) = $sth->fetchrow();
		$str_log .= "$total, $prepaid, $paid, $ar\n";

		#######################################
		#######################################
		##################
		################## CUSTOMER DEPOSIT / VENTA ORIGINAL
		##################
		#######################################
		#######################################
		$category = 'Anticipo Clientes';
		$keypoint = 'Customer Deposit';

		&general_deposits($id_payments,$id_orders,'orders',$keypoint,$category,'','','CURDATE',$amount);
		$str_log .= "general_deposits($id_payments,$id_orders,'orders',$keypoint,$category,'','','CURDATE',$amount)";

		####### Tax
		&order_deposit_separate_tax($id_orders,$id_payments,$category,$ida_taxes);
		$str_log .= "order_deposit_separate_tax($id_orders,$id_payments,$category,$ida_taxes)";

	}elsif($pd_order == 1 or $sale_movements){
		
		$str_log .= "Con Movimientos o PostFechado --->>> \n";
		$category = 'Anticipo Clientes';
		$this_acc_action = 'PostDate';

		$pd_order = &load_name('sl_orders','ID_orders',$id_orders,'PostedDate');
		$pd_payment = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'PostedDate');
		$pd_payment = 0 if !$pd_payment;
		
		$date_return = &load_name('sl_returns','ID_orders',$id_orders,' UNIX_TIMESTAMP(Date) ');
		$date_return = 0 if !$date_return;
		$date_payment = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,' UNIX_TIMESTAMP(Date) ');
		
		#&cgierr("$pd_order - $sale_movements - $tcustomer - $pd_order vs $pd_payment");
		if($pd_order ne $pd_payment and $date_return > 0 and $date_return <= $date_payment){
			
			#######################################
			#######################################
			##################
			################## CAMBIO FISICO
			##################
			#######################################
			#######################################
			$keypoint = $tcustomer == 1 ? 'Sale TC 1 Payment Local' : 'Sale TC 1 Payment Foreign';

			&general_deposits($id_payments,$id_orders,'orders',$keypoint,$category,'N/A','<= CURDATE','CURDATE',$amount);
			####### Tax
			&order_deposit_separate_tax($id_orders,$id_payments,$category,$ida_taxes); 


		}else{
			
			$this_acc_action = 'FlexPay';
			#######################################
			#######################################
			##################
			################## PAGOS POSTERIORES A LA VENTA
			##################
			#######################################
			#######################################
			$keypoint = $tcustomer == 1 ? 'Flexpay Deposit Local' : 'Flexpay Deposit Foreign';
			#if($keypoint eq 'Flexpay Deposit Local'){ $amount = $amount * (100/116); } #En pagos posterires a venta, para clientes locales, lo pagado invluye IVA (que ahora se desglosa)
			&general_deposits($id_payments,$id_orders,'orders',$keypoint,'Cobranza','N/A','<= CURDATE','CURDATE',$amount);
			####### Tax
			&order_deposit_separate_tax($id_orders,$id_payments,'Cobranza',$ida_taxes);

			###
			### Fluctuacion Cambiaria
			###
			if( $tcustomer != 1 ){
				$apply_profit_lost = 1;
			}

		}
	}else{
		##### Deposito de Cliente
		$category = 'Anticipo Clientes';
	}


	########
	######## Cuenta especifica para la operacion?
	########
	if($ida_bank_debit_credit and $ida_bank_debit_credit ne '' and !$in{'ida_banks'}) {
		$str_log .= "Cuenta especifica para la operacion --->>> \n";

		my ($ida_bank_debit, $ida_bank_credit) = split(/:/,$ida_bank_debit_credit);

		$ida_bank_debit = int($ida_bank_debit); $ida_bank_credit = int($ida_bank_credit);
		($ida_bank_debit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_debit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND ID_accounts IN($ida_banks) AND Amount = '$amount' AND ". $sqlmod_update_records .";") );
		($ida_bank_credit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_credit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND ID_accounts IN($ida_deposits) AND Amount = '$amount' AND ". $sqlmod_update_records .";") );

	}elsif($in{'ida_banks'}){
		$str_log .= "Cuenta de Banco: $in{'ida_banks'} --->>> \n";

		my ($sth) = &Do_SQL("SELECT CONCAT(ID_accounts_debit,':',ID_accounts_credit) FROM sl_keypoints_movements WHERE Keypoint = '$keypoint' AND ID_accounts_debit = '$in{'ida_banks'}';");
		my ($ida_bank_debit_credit) = $sth->fetchrow();

		if($ida_bank_debit_credit){

			my ($ida_bank_debit, $ida_bank_credit) = split(/:/,$ida_bank_debit_credit);

			$ida_bank_debit = int($ida_bank_debit); $ida_bank_credit = int($ida_bank_credit);
			($ida_bank_debit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_debit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND ID_accounts IN($ida_banks) AND Amount = '$amount' AND ". $sqlmod_update_records .";") );
			($ida_bank_credit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_credit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND ID_accounts IN($ida_deposits) AND Amount = '$amount' AND ". $sqlmod_update_records .";") );

		}

	}

	
	if($this_rounded_amount){

		## Amount Difference	
		&Do_SQL("UPDATE sl_movements SET ID_accounts = ". $ida_difference ." WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND Status IN ('Active','Pending') AND ". $sqlmod_update_records ." LIMIT 1;");

	}


	if( $apply_profit_lost == 1 ){

		my @params = ($id_orders, $id_payments, $amount_original, $exchange_rate, $ida_customer, $in{'ida_banks'}, $ida_profit, $ida_lost, "Cobranza");
		my ($this_res, $this_res_str) = &order_deposit_profit_lost(@params);
		if($this_res){ $this_acc++; $this_acc_str .= $this_res_str; }

	}

	if($in{'bankdate'}){

		#&Do_SQL("UPDATE sl_movements SET EffDate = '$in{'bankdate'}' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50 ;");

	}

	### Se guarda el ID_orders_payments
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_orders_payments', ID_tablerelated = '". $id_payments ."' WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND ". $sqlmod_update_records .";");
	delete($in{'ida_banks'});

	##
	### Validations
	##
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();
	$str_log .= "Validacion de mov. contables: $total_records\n";

	if( !$total_records or ($total_records == 1 and $apply_profit_lost) ){

		$this_acc = 1;
		$this_acc_str .= " Action: " . $this_acc_action . " TR: " . $total_records . " PL: " . $apply_profit_lost; 

	}
	$str_log .= "this_acc: $this_acc, this_acc_str: $this_acc_str\n";

	### --------------------------------------------------
	### Se guarda el archivo
	### --------------------------------------------------
	my $file_path = $cfg{'path_upfiles'}.'e'.$in{'e'}.'/';
	my $file_name = 'debug_order_deposit_'.$id_orders.'.txt';

	#open(logs_file,"> ".$file_path . $file_name) || die "No se puede abrir el archivo\n";
	#print logs_file $str_log;
	#close(logs_file);
	### --------------------------------------------------

	return ($this_acc, $this_acc_str);
}


#########################################################################################################
#########################################################################################################
#
#	Function: order_deposit_profit_lost
#   		
#		es: Se calcula posible perdida/ganancia cambiaria
#		en: Possible Profit/Lost
#
#	Created by:
#		_Gilberto Quirino_
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#		None
#
#   	See Also:
#
sub order_deposit_profit_lost {
#########################################################################################################
#########################################################################################################
	my (@param_data) = @_;

	my $this_acc = 0; my $this_acc_str = 'OK';
	## Pasados a traves de la funcion que lo llama
	my $id_orders = int($param_data[0]);
	my $id_payment = int($param_data[1]);
	my $amount = &filter_values($param_data[2]);
	my $exchange_rate = &filter_values($param_data[3]);
	my $ida_customer = &filter_values($param_data[4]);
	my $ida_banks = int($param_data[5]);
	my $ida_profit = int($param_data[6]);
	my $ida_lost = int($param_data[7]);
	my $category = &filter_values($param_data[8]);
	
	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);

	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';	
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0|;

	####################
	####################
	####### 1) Buscamos currency_exchange del pasivo(Ultima)
	####################
	####################

	###
	### 1.1 Se obtiene la fecha de la venta
	###	

	my ($sth) = &Do_SQL("SELECT EffDate FROM sl_movements WHERE ID_tableused = ". $id_orders ." AND tableused = 'sl_orders' AND ID_accounts IN(". $ida_customer .") AND Category = 'Ventas' AND Credebit = 'Debit' AND Status = 'Active' LIMIT 1;");
	my($date_sale) = $sth->fetchrow();

	my ($sth) = &Do_SQL("SELECT exchange_rate FROM sl_exchangerates WHERE Date_exchange_rate <= '". $date_sale ."' ORDER BY Date_exchange_rate DESC LIMIT 1;");
	my ($last_exchange_rate) = $sth->fetchrow();
	
	###
	### 1.2 No se encuentra currency_exchange
	###
	return (1, 'No Original Sale Exchange Rate Found') if !$last_exchange_rate;

	####################
	####################
	####### 2) Calculamos ganacia/perdida
	####################
	####################

	###
	### 2.1) Monto basado en tipo de cambio de la venta.
	###
	my $amount_then = round($amount * $last_exchange_rate,2);

	###
	### 2.2) Monto basado en tipo de cambio de aplicacion actual
	###
	my $amount_now = round($amount * $exchange_rate,2);

	###
	### 2.3) Calculamos ganancia/perdida
	###
	my $amount_difference = round($amount_now - $amount_then,2);
	my $flag_exchange_rate = $amount_difference > 0 ? 1 : 0;
	#&cgierr("AD($amount_difference) = AT: $amount_then vs AN: $amount_now");
	my $category_mvs = ($category) ? $category : "Aplicacion Anticipos AP";
	###
	### 2.4) Ganancia / Perdida
	###
	if($amount_difference > 0){

		###
		### 2.4.1) Ejecutamos Ganancia
		###
		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status,Date,Time  ,ID_admin_users )
				VALUES (". $ida_profit .",'".abs($amount_difference)."', '', CURDATE(), 'sl_orders', ". $id_orders .", '". $category_mvs ."', 'Credit', ". $md5time_value ." 'Active',CURDATE(), CURTIME(), '". $usr{'id_admin_users'} ."');");
		sleep(1);
		&Do_SQL("UPDATE sl_movements SET Amount = Amount - ". abs($amount_difference) ." WHERE tableused = 'sl_orders' AND ID_tableused = '". $id_orders ."' AND Category='". $category_mvs ."' AND ID_accounts IN(". $ida_customer .") AND Credebit='Credit' AND Status='Active' AND ". $sqlmod_update_records ." ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");		

	}elsif($amount_difference < 0){

		###
		### 2.4.2) Ejecutamos Perdida
		###
		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time  ,ID_admin_users )
				VALUES (". $ida_lost .",'". abs($amount_difference) ."', '', CURDATE(), 'sl_orders', ". $id_orders .", '". $category_mvs ."', 'Debit', ". $md5time_value ." 'Active',CURDATE(), CURTIME(), '". $usr{'id_admin_users'} ."');");
		sleep(1);
		&Do_SQL("UPDATE sl_movements SET Amount = Amount + ". abs($amount_difference) ." WHERE tableused = 'sl_orders' AND ID_tableused='$id_orders' AND Category = '". $category_mvs ."' AND ID_accounts IN (". $ida_customer .") AND Credebit = 'Credit' And Status = 'Active' AND ". $sqlmod_update_records ." ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");
		
	}

	##
	### Validations
	##
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status = 'Active' AND Category = '". $category_mvs ."' AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();

	if($flag_exchange_rate and $total_records < 3){

		## 7.1) Exchange Rate Win/Lose Failed
		$this_acc = 1;
		$this_acc_str = &trans_txt('acc_winlose');

	}

	return ($this_acc, $this_acc_str);
}


###############
###############
############### Sales
###############
###############

#########################################################################################################
#########################################################################################################
#
#	Function: accounting_exchange
#   		
#		es: Pasa los datos a la funcion de venta para su procesamiento
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
sub accounting_exchange {
#########################################################################################################
#########################################################################################################

	my (@param_data) = @_;

	&accounting_sale(@param_data);
	return;

}


#########################################################################################################
#########################################################################################################
#
#	Function: accounting_sale
#   		Ingresa a las cuentas de Sale los productos, Servicios, Discounts, Shipping, Tax de productos que se escanean y que no han sido cargados a las cuentas.
#
#	Created by:
#		_Roberto Barcenas_
#
#	Modified By:
#		- Roberto Barcenas on 06/30/2009: Se revisa si lo depositado es el mismo dia y entonces se elimina la entrada en customer deposits para que la operacion quede como venta.
#		- Roberto Barcenas on 09/21/2009: Antes de procesar los movimientos de exchange, se eliminan todos los del mismo dia para no duplicar informacion.
#		- Roberto Barcenas on 03/23/2012: En movimientos posteriores, se revisa el PostedDate de las lineas antes de realizar la suma
#		- Roberto Barcenas on 07/31/2014: Se llama funcion de invoice en general para venta/cf
#		- Modified on *15/09/14* by _Roberto Barcenas_ : Se filtra solo productos basados en sl_orders.Date/Time para evitar duplicidad en escaneos parciales en el mismo dia
#		- Modified on *29/09/14* by _Roberto Barcenas_ : Se corrige query de Exchange para sumar agrupado por producto.
#
#   	Parameters:
#		id_orders: ID_orders
#
#   	Returns:
#		None
#
#   	See Also:
#
sub accounting_sale {
#########################################################################################################
#########################################################################################################

## ToDo: accounting_apply_deposits

	## Pasados por funcion
	my (@param_data) = @_;
	my ($id_orders) = int($param_data[0]);
	## Pasados por parametro
	my ($ida_product) = int($param_data[1]);
	my ($ida_service) = int($param_data[2]);
	my ($ida_discount) = int($param_data[3]);
	my ($ida_shipping) = int($param_data[4]);
	my ($ida_tax) = int($param_data[5]);
	my ($ida_cdeposit) = &filter_values($param_data[6]);
	my ($ida_bankfees) = &filter_values($param_data[7]);
	my ($ida_banks) = &filter_values($param_data[8]);
	my ($ida_septax) = int($param_data[9]);
	my ($ida_ar_difference) = &filter_values($param_data[10]);
	my ($ida_customer_refund) = scalar @param_data == 14 ? &filter_values($param_data[11]) : '76,238,1182';
	## Pasados para COD (accounting_cod_delivered)
	my ($ida_paylost) = scalar @param_data == 14 ? &filter_values($param_data[12]) : 0;
	my ($ida_fake_delivery) = scalar @param_data == 14 ? &filter_values($param_data[13]) : 0;
	
	# my $str_params = join("\n", @param_data);
	# &cgierr($str_params);
	 
	my $this_acc_flag; my $this_acc_str;
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0|;
	
	my ($sth) = &Do_SQL("SELECT IF(PostedDate IS NULL,'0000-00-00',PostedDate) AS PostedDate,IF(sl_orders.PostedDate = CURDATE() OR PostedDate IS NULL OR PostedDate ='0000-00-00','Sale','Exchange')AS type FROM sl_orders WHERE ID_orders = '$id_orders' ");
	my ($pd_order,$type) = $sth->fetchrow();

	## Has Return Movements Already?
	my ($sth) = &Do_SQL("SELECT IF(COUNT(*) = 0, 'Sale', 'Exchange')AS type FROM sl_movements WHERE ID_tableused = '$id_orders' AND Category = 'Devoluciones'; ");
	$type = $sth->fetchrow();
	
	($in{'set_sale_movements'}) and ($type = $in{'set_sale_movements'});

	if($type eq 'Sale'){

		###########
		########### 1) VENTA
		###########

		my ($sth) = &Do_SQL("SELECT
						SUM(IF(LEFT(ID_products,1) <> 6,SalePrice,0)) AS SaleP,
						SUM(IF(LEFT(ID_products,1) =  6,SalePrice,0)) AS SaleS,
						SUM(Discount) AS Discount,
						SUM(Shipping) AS Shipping,
						SUM(Tax+ShpTax) AS Tax
						FROM sl_orders_products 
						WHERE ID_orders = '$id_orders' AND Status='Active' 
						AND (PostedDate='$pd_order' OR PostedDate IS NULL); ");
	

		my ($sale,$service,$discount,$shipping,$tax) = $sth->fetchrow();
	
		#######
		####### Customer Country
		#######
		my ($sth) = &Do_SQL("SELECT sl_customers.Currency,IF(sl_customers.Currency <> '' AND '$cfg{'acc_default_currency'}' <> '' AND sl_customers.Currency <> '$cfg{'acc_default_currency'}',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders' ;");
		my ($currency,$tcustomer) = $sth->fetchrow();
		
		if($tcustomer != 1){
			$exchange_rate = get_intl_exchange($pd_order,$currency);
			$sale = round($sale * $exchange_rate,3);
			$service = round($service * $exchange_rate,3);
			$discount = round($discount * $exchange_rate,3);
			$shipping = round($shipping * $exchange_rate,3);
			$tax = round($tax * $exchange_rate,3);
		}
	
		&general_deposits(0,$id_orders,'orders','Sale Product','Ventas','N/A','N/A','N/A',$sale) if ($sale > 0 and &sale_today($ida_product,$sale,$id_orders,'Credit') == 0);
		&general_deposits(0,$id_orders,'orders','Sale Service','Ventas','N/A','N/A','N/A',$service) if ($service > 0 and &sale_today($ida_service,$service,$id_orders,'Credit') == 0);
		&general_deposits(0,$id_orders,'orders','Sale Discount','Ventas','N/A','N/A','N/A',$discount) if ($discount > 0 and &sale_today($ida_discount,$discount,$id_orders,'Debit') == 0);
		&general_deposits(0,$id_orders,'orders','Sale Shipping','Ventas','N/A','N/A','N/A',$shipping) if ($shipping > 0 and &sale_today($ida_shipping,$shipping,$id_orders,'Credit') == 0);

		
		if($tax > 0 and &sale_today($ida_tax,$tax,$id_orders,'Credit') == 0){

			if($tax > 0 and $ida_septax == 1) {
				## Tax must be separated
				my @params  = ("$id_orders","$ida_banks","$ida_discount","$pd_order","$tax");
				#&accounting_sale_separate_tax($id_orders,$ida_banks,$ida_discount,$pd_order,$tax);
				my ($this_st, $this_st_str) = &accounting_sale_separate_tax(@params);
				if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_separate_tax"); }
				
			} else {
				## Tax in one line
				&general_deposits(0,$id_orders,'orders','Sale Tax','Ventas','N/A','N/A','N/A',$tax)	if ($tax > 0 and &sale_today($ida_tax,$tax,$id_orders,'Credit') == 0);
				
			}

		}
		
		
		#### Change Customer Deposit to Sale?
		my ($this_st, $this_st_str) = &accounting_change_cd_to_sale($id_orders,$ida_cdeposit);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_cdtosale"); }
		#### Preorder Deposits?
		my ($this_st, $this_st_str) = &accounting_apply_deposits($id_orders,$ida_cdeposit);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_deposits"); }
		#### Activamos los movimientos que esten pendientes
		my ($sth) = &Do_SQL("UPDATE sl_movements SET Status = 'Active', EffDate = CURDATE() WHERE tableused = 'sl_orders' AND ID_tableused = '". $id_orders ."' AND Status = 'Pending' ;");
		#### La orden tiene Flexipagos?
		my ($this_st, $this_st_str) = &accounting_set_ar($id_orders,$ida_bankfees);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_flexpayments"); }
		#### La orden tiene Refunds?
		my ($this_st, $this_st_str) = &accounting_sale_refund($id_orders,$ida_banks,$ida_customer_refund);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_refund"); }


		####
		#### Suma Final, diferencia que aplicar?
		####
		my ($this_st, $this_st_str) = &accounting_sale_difference($id_orders, $ida_ar_difference, $ida_bankfees, $ida_banks,'Ventas');
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_difference"); }

		#### Cambiamos la fecha de la aplicacion
		my ($sth) = &Do_SQL("UPDATE sl_movements SET EffDate = '". $pd_order ."' WHERE tableused='sl_orders' 
							AND ID_tableused = '". $id_orders ."' AND ". $sqlmod_update_records .";") if $pd_order ne '0000-00-00';

		
	}else{

		#############
		############# 2) CAMBIO FISICO / ENVIO PARCIAL
		#############

		##### Movimiento Posterior (Posible Exchange o bien partial shipment que no registraron movimiento alguno)
		(!$cfg{'restockingfeeid'}) and ($cfg{'restockingfeeid'} = 0);
		(!$cfg{'returnfeeid'}) and ($cfg{'returnfeeid'} = 0);

		######
		###### Escaneo viene de Outsorcing (siempre es en pasado)
		my $modquery = $in{'shpdate'} ? "AND sl_orders_products.PostedDate = '$in{'shpdate'}'" : " AND sl_orders_products.PostedDate = CURDATE() ";

		##1) Verificacion de PostedDate correcto en lineas.
		my ($sth) = &Do_SQL("UPDATE sl_orders_products SET PostedDate=IF(ShpDate <> '0000-00-00' AND ShpDate <= '". $pd_order ."','". $pd_order ."',PostedDate)
					WHERE ID_Orders = '". $id_orders ."' AND Status NOT IN ('Order Cancelled','Inactive') AND SalePrice > 0 AND PostedDate > '". $pd_order ."';");

		my ($sth) = &Do_SQL("SELECT
								SUM(IF(LEFT(ID_products,1) <> 6,SalePrice,0)) AS SaleP,
								SUM(IF(LEFT(ID_products,1) =  6 AND ID_products NOT IN(600000000+".$cfg{'restockingfeeid'}.",600000000+".$cfg{'returnfeeid'}."),SalePrice,0)) AS SaleS,
								SUM(Discount) AS Discount,
								SUM(Shipping) AS Shipping,
								SUM(Tax+ShpTax) AS Tax
							FROM 
								sl_orders_products 
							INNER JOIN
							(
								SELECT
									sl_orders_products.ID_orders_products
								FROM
									sl_orders_products
								INNER JOIN	
									sl_orders_parts
								USING(ID_orders_products)
								WHERE 
									ID_orders = '$id_orders' 
									AND sl_orders_products.PostedDate >= '$pd_order' 
									AND sl_orders_products.PostedDate != '0000-00-00' 
									$modquery 
									AND (SalePrice > 0 OR Shipping > 0) 
									AND sl_orders_products.Status IN ('Exchange')
									AND TIMESTAMPDIFF(SECOND,CONCAT(sl_orders_parts.Date,' ',sl_orders_parts.TIME),NOW()) BETWEEN 0 AND 50
									/*AND (IF(LEFT(ID_products,1) != 6,ShpDate = PostedDate,LEFT(ID_products,1) = 6))*/ 
								GROUP BY 
									sl_orders_products.ID_orders_products
								ORDER BY 
									sl_orders_products.ID_orders_products	
							)tmp
							USING
								(ID_orders_products);");
	
		my ($sale,$service,$discount,$shipping,$tax) = $sth->fetchrow();
		my $amount = round($sale + $service - $discount + $shipping + $tax,3);

		my ($sth) = &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = $id_orders AND tableused='sl_orders' AND Category='Cambios Fisicos' AND ID_accounts IN(152,170,180,185,187) AND Credebit = 'Credit' AND EffDate=CURDATE(); ");
		&general_deposits(0,$id_orders,'orders','Sale Product','Cambios Fisicos','N/A','N/A','N/A',$sale) if $sale > 0;
		&general_deposits(0,$id_orders,'orders','Sale Service','Cambios Fisicos','N/A','N/A','N/A',$service) if $service > 0;
		&general_deposits(0,$id_orders,'orders','Sale Discount','Cambios Fisicos','N/A','N/A','N/A',$discount) if $discount > 0;
		&general_deposits(0,$id_orders,'orders','Sale Shipping','Cambios Fisicos','N/A','N/A','N/A',$shipping) if $shipping > 0;
		&general_deposits(0,$id_orders,'orders','Sale Tax','Cambios Fisicos','N/A','N/A','N/A',$tax) if $tax > 0;


		#### Change CD to Sale?
		my ($this_st, $this_st_str) = &accounting_change_cd_to_sale($id_orders,$ida_cdeposit);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_cdtosale"); }
		#### CD
		my ($this_st, $this_st_str) = &accounting_apply_deposits($id_orders,$ida_cdeposit);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_deposits"); }

		if($amount > 0){

			#########
			######### 2.1) C.F c/ C.Refund?
			#########
			my ($sthc) = &Do_SQL("SELECT Category FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Status = 'Active' ORDER BY ID_movements DESC LIMIT 1;");
			my ($this_ex_category) = $sthc->fetchrow();

			my ($sth) =  &Do_SQL("SELECT ID_movements, ID_accounts, Amount FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND ID_accounts IN($ida_customer_refund) AND Credebit = 'Debit' AND Status = 'Pending' ORDER BY EffDate, ID_movements;");
			REFUNDS:while(my ($id_refund, $ida_customer_refund, $amount_refund) = $sth->fetchrow()){

				if($amount >= $amount_refund){

					########
					######## 2.1.1) Exchange Amount > Refund?
					########
					&Do_SQL("UPDATE sl_movements SET Status = 'Active', Category = '$this_ex_category', EffDate = CURDATE(), Reference='Amount > Refund', Date = CURDATE(), Time = CURTIME() WHERE ID_movements = '$id_refund';");
					$amount -= $amount_refund;

				}else{

					########
					######## 2.1.1) Refund > Exchange Amount
					########
					&Do_SQL("UPDATE sl_movements SET Amount = Amount - $amount, Category = '$this_ex_category', Reference='Refund > Amount' WHERE ID_movements = '$id_refund';");

					my (%overwrite) = ('amount' => $amount, 'status' => 'Active');
					my $applied_movement = &Do_selectinsert('sl_movements', "ID_movements = '$id_refund'", "", "", %overwrite);
					&Do_SQL("UPDATE sl_movements SET EffDate = CURDATE(),Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_movements = '$applied_movement';");

					$amount = 0;

				}

				last REFUNDS if !$amount;

			}

		}

		#### La orden tiene AR
		my ($this_st, $this_st_str) = &accounting_set_ar($id_orders,$ida_bankfees);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_flexpayments"); }
		#### La orden tiene CR
		my ($this_st, $this_st_str) = &accounting_sale_refund($id_orders,$ida_banks,$ida_customer_refund);
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_refund"); }
		#### Suma Final, diferencia que aplicar?
		my ($this_st, $this_st_str) = &accounting_sale_difference($id_orders, $ida_ar_difference, $ida_bankfees, $ida_banks,'Cambios Fisicos');
		if ($this_st){ ++$this_flag_acc; $this_str_acc.= "<br>".&trans_txt("acc_keypoints_sale_difference"); }
		#### Aseguramos Categoria y EffDate
		&Do_SQL("UPDATE sl_movements SET Category = 'Cambios Fisicos', EffDate = CURDATE() WHERE ID_tableused = '". $id_orders ."' AND Category <> 'Costos' AND tableused = 'sl_orders' AND Status = 'Active' AND ". $sqlmod_update_records .";");

	}

	##
	### Payment Exceptions
	##
	if($in{'set_charging_carrier'} or $in{'set_payment_lost'} or $in{'set_fake_delivery'}){

		my $ida_payment_exception = 0;
		if($in{'set_payment_lost'}){ $ida_payment_exception = $ida_paylost; 
		}elsif($in{'set_charging_carrier'}){ $ida_payment_exception = $in{'set_charging_carrier'};
		}elsif($in{'set_fake_delivery'}){ $ida_payment_exception = $ida_fake_delivery;	}

		if($ida_payment_exception){

			## Update Debit Account
			&Do_SQL("UPDATE sl_movements SET ID_accounts = '". $ida_payment_exception ."' WHERE ID_tableused = '". $id_orders. "' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND ID_accounts IN(". $ida_cdeposit .",". $ida_banks .") AND Status = 'Active' AND Category = 'Ventas' AND ". $sqlmod_update_records .";");
			## Delete Deposit Movements
			&Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status = 'Active' AND Category = 'Anticipo Clientes' AND ". $sqlmod_update_records .";");

		}else{

			## Problem finding Exception Account
			return (1, &trans_txt('acc_accounting_sale_payment_exception'));

		}

	}

	#############
	############# Automatic Journal
	#############
	&accounting_set_automatic_journal($id_orders,'sl_orders');

	#############
	############# Invoice
	#############
	my ($str_invoices, $inv_status, $id_invoices) = &export_info_for_invoices($id_orders);
	if( lc($inv_status) ne 'ok'){ ++$this_flag_acc; $this_str_acc .= "<br>" . &trans_txt('invoicing') . $str_invoices; }
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'cu_invoices', ID_tablerelated = '". $id_invoices ."' WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status = 'Active' AND (tablerelated IS NULL OR tablerelated = '')  AND ". $sqlmod_update_records .";") if ($id_invoices);

	##
	### Validations
	##
	my ($sth) = &Do_SQL("SELECT 
							COUNT(*) 
						FROM 
							sl_movements 
						WHERE 
							ID_tableused = '". $id_orders ."' 
							AND tableused = 'sl_orders' 
							AND Status IN ('Active','Pending') 
							AND Category = 'Ventas' 
							AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();

	if( !$total_records ){

		++$this_flag_acc;
		$this_str_acc .= "<br>" . &trans_txt('acc_general');

	}


	return ($this_flag_acc, $this_str_acc);
}


#############################################################################
#############################################################################
#   Function: accounting_change_cd_to_sale
#
#       Es: Si la venta es el mismo dia que el deposito, se cambia el customer deposit por sale
#       En: 
#
#
#    Created on: 06/30/09  11:28:58
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - $id_orders
#		- $id_cd
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_sale>
#
#
sub accounting_change_cd_to_sale{
#############################################################################
#############################################################################

	if($cfg{'acc_cd_to_sale'}) {

		my ($id_orders,$id_cd) = @_;
		$id_cd = &get_account('Customer Deposit') if !$id_cd;
		$id_cd = 0 if !$id_cd;
		my $this_acc = 0; my $this_acc_str;
		
		my ($sth) = &Do_SQL("SELECT IF(EffDate = tmp.PostedDate ,1,0) AS SaleDeposit,COUNT(*) AS Payments, tmp.PostedDate 
							FROM sl_movements 
							INNER JOIN(SELECT ID_orders,PostedDate FROM sl_orders WHERE ID_orders = '$id_orders')tmp
							ON ID_orders = ID_tableused
							WHERE ID_tableused = '$id_orders' AND ID_accounts IN($id_cd) 
							AND Credebit='Credit' AND tableused='sl_orders' 
							GROUP BY Date ORDER BY Date DESC LIMIT 1;");
		my($sale,$npay,$pdate) = $sth->fetchrow();

		if($sale){

			#### Eliminamos los Customer Deposit que tenga la orden
			my ($sth) = &Do_SQL("DELETE FROM sl_movements WHERE ID_tableused = '$id_orders' AND ID_accounts IN($id_cd) AND Credebit='Credit' AND tableused='sl_orders' AND EffDate = '$pdate';");
			#### Cambiamos el primer registro a categoria 'Sale'
			my ($sth) = &Do_SQL("UPDATE sl_movements SET Category='Ventas' WHERE ID_tableused = '$id_orders' AND Category='Anticipo Clientes' AND Credebit='Debit' AND tableused='sl_orders' AND EffDate = '$pdate';");
			
		}

	}

	return($this_acc, $this_acc_str);

}


#############################################################################
#############################################################################
#   Function: accounting_apply_deposits
#
#       Es: Aplica los customer deposits a la venta
#       En: 
#
#
#    Created on: 06/18/09  15:52:35
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#    	- 08/21/2014: :a busqueda del anticipo aplicado se hace >= en lugar de > (para casos Cambio Fisico)
#    
#
#   Parameters:
#
#       - $id_orders
#		- $id_cd
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_sale>
#
#
sub accounting_apply_deposits{
#############################################################################
#############################################################################

	my ($id_orders,$id_cd) = @_;
	$id_cd = &get_account('Customer Deposit') if !$id_cd;
	(!$id_cd and $cfg{'ida_bankscd'}) and ($id_cd = $cfg{'ida_bankscd'});
	my $this_acc = 0; my $this_acc_str; my $i = 0;

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;

	my $sqlmod_update_newrecord = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|, MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								'';


	my ($sth) = &Do_SQL("SELECT 
							ID_movements
							, Amount
							, EffDate 
						FROM 
							sl_movements 
						WHERE 
							tableused = 'sl_orders' 
							AND ID_tableused = ". $id_orders ." 
							AND ID_accounts IN (". $id_cd .") 
							AND Credebit = 'Credit' 
							AND Status = 'Active';");
	while( my($id, $amount, $effdate) = $sth->fetchrow() ){

		my ($sth2) = &Do_SQL("SELECT 
								COUNT(*) 
							FROM 
								sl_movements 
							WHERE 
								tableused = 'sl_orders' 
								AND ID_tableused = ". $id_orders ."
								AND ID_accounts IN (". $id_cd .") 
								AND Credebit = 'Debit' 
								AND Amount = '". $amount ."' 
								AND EffDate >= '". $effdate ."';");
		my ($is_applied) = $sth2->fetchrow();


		if(!$is_applied){

			++$i;
			my (%overwrite) = ('credebit' => 'Debit', 'category' => 'Ventas', 'id_journalentries' => '0', 'tablerelated' => '', 'id_tablerelated' => '0');
			my $new_movement = &Do_selectinsert('sl_movements', "ID_movements = '$id'", "", "", %overwrite);
			&Do_SQL("UPDATE sl_movements SET EffDate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."' ". $sqlmod_update_newrecord ." WHERE ID_movements = ". $new_movement .";");

		}

	}

	##
	### Validations
	##
	if($i){

		my ($sth) = &Do_SQL("SELECT 
								COUNT(*) 
							FROM 
								sl_movements 
							WHERE 
								ID_tableused = '". $id_orders ."' 
								AND tableused = 'sl_orders' 
								AND Status IN ('Active','Pending') 
								AND Category = 'Ventas' 
								AND Credebit = 'Debit' 
								AND ID_accounts IN (". $id_cd .") 
								AND ". $sqlmod_update_records .";");
		my ($total_records) = $sth->fetchrow();

		if( abs($total_records - $i) ){

			$this_acc = 1;
			$this_acc_str .= " " . &trans_txt('acc_general');

		}

	}

	return ($this_acc, $this_acc_str);	
}	


#############################################################################
#############################################################################
#   Function: accounting_set_ar
#
#       Es: Registra movimientos de A/R en la orden
#       En: 
#
#
#    Created on: 07/13/09  17:47:37
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - $id_orders
#		- $id_bankfees
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_sale>
#
#
sub accounting_set_ar{
#############################################################################
############################################################################# 	
	
	my ($id_orders,$id_bankfees) = @_;
	
	my $this_acc = 0; my $this_acc_str;
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;
	
	my ($sth) = &Do_SQL("SELECT Total,PrePaid,Paid,IF(Total-Paid = 0,0,Total-Paid) AS AR
					FROM sl_orders_payments INNER JOIN
					(SELECT ID_orders,
					SUM(Amount)AS Total,
					SUM(IF(CapDate IS NOT NULL AND CapDate !='0000-00-00' AND CapDate < CURDATE(),Amount,0)) AS Prepaid,
					SUM(IF(Captured='Yes' AND (CapDate IS NOT NULL AND CapDate !='0000-00-00'),Amount,0)) AS Paid
					FROM sl_orders_payments
					WHERE  ID_orders = '$id_orders'
					AND Status NOT IN ('Void','Order Cancelled','Cancelled')
					GROUP BY ID_orders) AS tmpPaid
					ON tmpPaid.ID_orders = sl_orders_payments.ID_orders
					GROUP BY sl_orders_payments.ID_orders; ");
												
	my ($total,$prepaid,$paid,$ar) = $sth->fetchrow();

	#######
	####### Customer Country
	#######
	my ($sth) = &Do_SQL("SELECT IF(sl_customers.Currency <> '' AND '$cfg{'acc_default_currency'}' <> '' AND sl_customers.Currency <> '$cfg{'acc_default_currency'}',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders' ;");
	my ($tcustomer) = $sth->fetchrow();
	my $keypoint = $tcustomer == 1 ? 'Sale Flexpay Local' : 'Sale Flexpay Foreign';

	if ($ar > 0) {

		## Bank Fees
		if($id_bankfees){
			my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_movements WHERE ID_tableused = '$id_orders' AND Credebit = 'Debit' AND ID_accounts IN($id_bankfees) AND Status='Active';");
			my ($bankfees) = $sth->fetchrow();
			$ar -= $bankfees;
		}

		if ($ar > 0){

			&general_deposits(0,$id_orders,'orders',$keypoint,'Ventas','N/A','0000-00-00','0000-00-00',$ar);

			##
			### Validations
			##
			my ($sth) = &Do_SQL("SELECT 
									COUNT(*) 
								FROM 
									sl_movements 
								WHERE 
									ID_tableused = '". $id_orders ."' 
									AND tableused = 'sl_orders' 
									AND Status IN ('Active','Pending') 
									AND Category = 'Ventas' 
									AND Amount = '". $ar ."'
									AND ". $sqlmod_update_records .";");
			my ($total_records) = $sth->fetchrow();

			if( !$total_records ){

				$this_acc = 1;
				$this_acc_str .= " " . &trans_txt('acc_general');

			}

		}

	}

	return ($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: accounting_sale_refund
#
#       Es: Agrega movimientos contables de devolucion en la orden al procesar la venta
#       En: 
#
#
#    Created on: 07/28/09  11:39:34
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - $id_orders
#		- $id_banks
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_sale>
#
#
sub accounting_sale_refund{
#############################################################################
#############################################################################	
	return;
	## ToDo: Agregar sl_orders_payments con el pago negativo por la devolucion
	
	my ($id_orders,$id_banks,$ida_customer_refund) = @_;
	(!$cfg{'porcerror'}) and ($cfg{'porcerror'} = 0);

	my $this_acc = 0; my $this_acc_str; my $i = 0;
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;

	$id_orders = int($id_orders);
	my ($sth) = &Do_SQL("SELECT ROUND(Items,2),ROUND(Payments,2)
					FROM sl_orders
					INNER JOIN
						(SELECT ID_orders,SUM(SalePrice-Discount+Shipping+ShpTax+Tax)AS Items
						FROM sl_orders_products
						WHERE ID_orders = ". $id_orders ." AND Status IN('Active','Returned','ReShip','Exchange')
						GROUP BY ID_orders)as tmpi
					ON tmpi.ID_orders  = sl_orders.ID_orders
					INNER JOIN
						(SELECT ID_orders,SUM(Amount)AS Payments
						FROM sl_orders_payments
						WHERE ID_orders = ". $id_orders ." AND Status IN('Approved','Credit')
						AND IF(Amount < 0,0 <
						(
							SELECT COUNT(*) FROM sl_movements
							WHERE tableused='sl_orders'
							AND ID_tableused = ". $id_orders ."
							AND ABS( Amount - ABS(sl_orders_payments.Amount) ) BETWEEN 0 AND 1
							AND 
							(
								(ID_accounts IN(". $id_banks .") AND Credebit = 'Credit')
								OR
								(ID_accounts IN($ida_customer_refund) AND Credebit = 'Debit')	
							)
						),Amount != 0)
						GROUP BY ID_orders) AS tmpp
					ON tmpp.ID_orders  = sl_orders.ID_orders
					WHERE sl_orders.ID_orders = ". $id_orders ." /*AND Status='Shipped'*/;");
	
	my($pitem,$ppay) = $sth->fetchrow();

	#######
	####### Customer Country
	#######
	my ($sth) = &Do_SQL("SELECT IF(sl_customers.Currency <> '' AND '". $cfg{'acc_default_currency'} ."' <> '' AND sl_customers.Currency <> '$cfg{'acc_default_currency'}',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders' ;");
	my ($tcustomer) = $sth->fetchrow();
	my $keypoint = $tcustomer == 1 ? 'Customer Refund Local' : 'Customer Refund Foreign';


	my $diff_allowed = round( $ppay - ($ppay * (1 - $cfg{'porcerror'} / 100)),3);
	my $diff = round($ppay - $pitem,3);

	if($pitem < $ppay and $diff > $diff_allowed)  {

		my $this_amount = round($ppay - $pitem, 2);
		&general_deposits(0,$id_orders,'orders',$keypoint,'Ventas','N/A','< CURDATE','<= CURDATE',$this_amount);
		&general_deposits(-1,$id_orders,'orders',$keypoint,'Ventas','N/A','0000-00-00','0000-00-00',$this_amount);

		##
		### Validations
		##
		my ($sth) = &Do_SQL("SELECT 
								COUNT(*) 
							FROM 
								sl_movements 
							WHERE 
								ID_tableused = '". $id_orders ."' 
								AND tableused = 'sl_orders' 
								AND Status IN ('Active','Pending') 
								AND Category = 'Ventas' 
								AND Amount = '". $this_amount ."' 
								AND ". $sqlmod_update_records .";");
		my ($total_records) = $sth->fetchrow();

		if( !$total_records ){

			$this_acc = 1;
			$this_acc_str .= " " . &trans_txt('acc_general');

		}

	}

	return ($this_acc, $this_acc_str);												
}



#############################################################################
#############################################################################
#   Function: accounting_sale_difference
#
#       Es: Agrega movimientos contables por diferencia en contabilidad
#       En: 
#
#
#    Created on: 10/02/13  15:39:34
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - $id_orders
#		- $ida_difference
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_sale>
#
#
sub accounting_sale_difference{
#############################################################################
#############################################################################	

	## ToDo: Agregar sl_orders_payments con el pago negativo por la devolucion
	
	my ($id_orders,$ida_difference,$ida_bankfees,$ida_banks,$category) = @_;
	
	my $this_acc = 0; my $this_acc_str; my $i = 0;
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;
	
	$id_orders = int($id_orders);
	my $credebit = '';
	my $amount = 0;
	(!$ida_difference) and ($ida_difference = 0);
	(!$cfg{'porcerror'}) and ($cfg{'porcerror'} = 0);

	my ($sth) = &Do_SQL("SELECT 
						SUM(IF(Credebit = 'Debit',Amount,0)) AS Debits,
						SUM(IF(Credebit = 'Credit',Amount,0)) AS Credits
						FROM sl_movements
						WHERE ID_tableused = ". $id_orders ."
						AND tableused = 'sl_orders' 
						AND Status IN ('Active'/*,'Pending'*/)
						AND Amount > 0;");
	my($debits,$credits) = $sth->fetchrow();

	if(abs($debits - $credits) > 0) {

		my $diff_allowed = $debits > $credits ?
							round( $debits - ($debits * (1 - $cfg{'porcerror'} / 100)),2) :
							round( $credits - ($credits * (1 - $cfg{'porcerror'} / 100)) ,2);
		$amount = $credits > $debits ?round($credits - $debits,2) : round($debits - $credits,2);

		#&cgierr("$credits > $debits and $amount <= $diff_allowed <br> $id_orders,$ida_difference,$category");


		if($debits > $credits){
			# and $amount <= $diff_allowed 
			$credebit = 'Credit';
		}elsif($credits > $debits){
			# and $amount <= $diff_allowed 
			$credebit = 'Debit';
		}

		if($amount >= 0.01 and ($amount <= $diff_allowed or $amount < 1) ){

			
			if(int($ida_difference) > 0) {

				###
				### Insercion de diferencia
				###				
				&Do_SQL("/* $amount  */ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
							VALUES ($ida_difference,'".$amount."', '', CURDATE(), 'sl_orders', $id_orders, '$category', '$credebit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");


				if($cfg{'ser_roundamt'}){

					###
					### Se agrega servicio a la orden para compensar sobrante/taltante
					###
					&Do_SQL("INSERT INTO sl_orders_products SET ID_orders = '$id_orders', ID_products = 600000000 + $cfg{'ser_roundamt'}, Quantity = 1, ID_packinglist = 0, 
							SalePrice = IF('$credebit' = 'Credit',$amount,$amount * -1), Tax_percent = 0, ShpTax = 0, ShpTax_percent = 0, PostedDate = CURDATE(),
							Upsell = 'Yes', Status = IF('$category' = 'Sale','Active','Exchange'), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

				}

			}

			&accounting_set_segment($id_orders, 'orders');
			####
			#### ToDo: Funcion para manejar las diferencias?
			####


		}elsif($amount >= 0.01){

			#######
			####### Customer Country
			#######
			my ($sth) = &Do_SQL("SELECT IF(sl_customers.Currency <> '' AND '$cfg{'acc_default_currency'}' <> '' AND sl_customers.Currency <> '$cfg{'acc_default_currency'}',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders' ;");
			my ($tcustomer) = $sth->fetchrow();
			my $keypoint_debit = $tcustomer == 1 ? 'Sale Flexpay Local' : 'Sale Flexpay Foreign';
			my $keypoint_credit = $tcustomer == 1 ? 'Customer Refund Local' : 'Customer Refund Foreign';

			if($credebit eq 'Debit') {

				####
				#### 1) Cliente nos debe dinero
				####
				if($id_bankfees){
					my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_movements WHERE ID_tableused = '$id_orders' AND Credebit = 'Debit' AND ID_accounts IN($id_bankfees) AND Status='Active';");
					my ($bankfees) = $sth->fetchrow();
					$amount -= $bankfees;
				}

				&general_deposits(0,$id_orders,'orders',$keypoint_debit,'Ventas','N/A','0000-00-00','0000-00-00',$amount) if $amount > 0;

			}else{

				####
				#### 2) Cliente Tiene saldo a favor
				####
				&general_deposits(0,$id_orders,'orders',$keypoint_credit,'Ventas','N/A','< CURDATE','<= CURDATE',$amount) if $amount > 0;
				&general_deposits(-1,$id_orders,'orders',$keypoint_credit,'Ventas','N/A','0000-00-00','0000-00-00',$amount) if $amount > 0;

			}		


		}

		##
		### Validations
		##
		if($i){

			my ($sth) = &Do_SQL("SELECT 
									COUNT(*) 
								FROM 
									sl_movements 
								WHERE 
									ID_tableused = '". $id_orders ."' 
									AND tableused = 'sl_orders' 
									AND Status IN ('Active','Pending') 
									AND Category = 'Ventas' 
									AND Amount = ". $amount ." 
									AND ". $sqlmod_update_records .";");
			my ($total_records) = $sth->fetchrow();

			if( !$total_records ){

				$this_acc = 1;
				$this_acc_str .= " " . &trans_txt('acc_general');

			}

		}

	}

	return ($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: accounting_cod_delivered
#
#       Es: Ejecuta movimientos contables cuando una orden cod es entregada.
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
#      - param_data : ID Order in array form
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_order_cod_paid>
#      <accounting_inventory_out>
#
sub accounting_cod_delivered {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	$va{'no_time_sensitive'} = 1; ## Esta variable se ocupa en la funcion accounting_inventory_out
	my $flag_acc; my $str_acc;

	my ($acc_status_inventory, $acc_string_inventory) = &accounting_inventory_out(@param_data); ## salida de inventario
	if ($acc_status_inventory){ ++$flag_acc; $str_acc .= "<br>". &trans_txt("acc_keypoints_inventoryout") . "<br>" . $acc_string_inventory; }

	my ($acc_status_sale, $acc_string_sale) = &accounting_sale(@param_data); ## venta
	if ($acc_status_sale){ ++$flag_acc; $str_acc.= "<br>". &trans_txt("acc_keypoints_sale") . "<br>" . $acc_string_sale; }

	return ($flag_acc, $str_acc);
}


#############################################################################
#############################################################################
#   Function: accounting_inventory_out_cod
#
#       Es: Funcion puente, sirve para evaluar cuando se debe ejecutar contabibilid(Exchange) y cuando no (Venta)
#       En: 
#
#
#    Created on: 2014/10/03
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_orders : ID Order
#      - id_orders_products : ID Products . Solo viene cuando es llamada por linea de producto  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_inventory_out>
#
sub accounting_inventory_out_cod {
#############################################################################
#############################################################################	
	
	my (@param_data) = @_;

	my $id_orders = int($param_data[0]);
	my $id_orders_products = int($param_data[1]) if scalar (@param_data) == 3;
	my $ida_sale = scalar (@param_data) == 3 ? &filter_values($param_data[2]) : &filter_values($param_data[1]);
	return if !$id_orders;

	###
	### 1) Determinamos si es Exchange. Contamos cuantos registros de devolucion existen
	###
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND ID_accounts IN($ida_sale);");
	my ($tret) = $sth->fetchrow();

	if($tret){

		### 2) Si existen devoluciones, se debe procesar la contabilidad por CF.
		#$va{'no_time_sensitive'} = 1; ## Esta variable se ocupa en la funcion accounting_inventory_out
		&accounting_inventory_out(@param_data);

	}

}


#############################################################################
#############################################################################
#   Function: accounting_inventory_out
#
#       Es: Registra los movimientos de salida de inventario
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *11/12/12* by _Roberto Barcenas_ : La funcion puede ser llamada para todos los productos de la orden, o bien para un solo producto. Ahora es llamada tambien cuando se escanean los productos de las ordenes de CC
#		 - Modified on *15/09/14* by _Roberto Barcenas_ : Se filtra solo productos basados en sl_orders.Date/Time para evitar duplicidad en escaneos parciales en el mismo dia
#		 - Modified on *27/01/15* by _Roberto Barcenas_ : Se cambia Categoria Ventas -> Costos por peticion Lizbeth Torres Parada
#
#   Parameters:
#
#      - id_orders : ID Order
#      - id_orders_products : ID Products . Solo viene cuando es llamada por linea de producto  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_order_inventory_out>
#
sub accounting_inventory_out {
#############################################################################
#############################################################################	
	

	my (@param_data) = @_;

	my $id_orders = int($param_data[0]);
	my $id_orders_products = int($param_data[1]) if scalar (@param_data) == 3;
	my $ida_sale = 0; 
	(scalar (@param_data) == 2) and ($ida_sale = &filter_values($param_data[1])); 
	(scalar (@param_data) == 3) and ($ida_sale = &filter_values($param_data[2]));
	return if !$id_orders;
	
	my $category = 'Ventas';
	$category = 'Costos';

	my $this_acc = 0;
	my $this_acc_str;
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0|;

	###
	### 1) Determinamos si es Exchange. Contamos cuantos registros de devolucion existen
	###
	#if($ida_sale){
	#
	#	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Debit' AND ID_accounts IN($ida_sale);");
	#	my ($tret) = $sth->fetchrow();
	#	($tret) and ($category = 'Cambios Fisicos');
	#	
	#}


	my $modquery = $id_orders_products ? " AND sl_orders_products.ID_orders_products = '$id_orders_products' " : '';
	($in{'shpdate'}) and ($modquery .= " AND sl_orders_products.PostedDate = '$in{'shpdate'}' ");
	my $modtime = $va{'no_time_sensitive'} ? '' : "AND TIMESTAMPDIFF(MINUTE,CONCAT(sl_orders_parts.Date,' ',sl_orders_parts.TIME),NOW()) BETWEEN 0 AND 5";

	my $sth = &Do_SQL("SELECT 
							ID_orders_products
							, IF(sl_orders_products.Cost IS NULL OR sl_orders_products.Cost = '',0,sl_orders_products.Cost)AS Cost
							, isSet 
						FROM 
							sl_orders_products 
						INNER JOIN 
							sl_skus 
						ON 
							IF(RIGHT(sl_orders_products.ID_products,6) > 0,sl_orders_products.ID_products,Related_ID_products) = sl_skus.ID_sku_products 
						INNER JOIN
								sl_orders_parts
							USING(ID_orders_products)	
						WHERE 
							ID_orders = '$id_orders' 
							$modquery 
							AND SalePrice >= 0
							AND LEFT(sl_orders_products.ID_products,1) != 6 
							AND sl_orders_products.Status IN('Active','Exchange'/*,'ReShip'*/)
							$modtime
							GROUP BY sl_orders_products.ID_orders_products;");

	while(my ($idop,$cost,$isSet) = $sth->fetchrow()){
		
		if($isSet eq 'Y'){
			my $sth = &Do_SQL("SELECT 
									IF(Cost IS NULL OR Cost = '',0,Cost)AS Cost 
								FROM 
									sl_orders_parts 
								WHERE 
									ID_orders_products = '$idop' 
									AND ShpDate IS NOT NULL AND ShpDate !='' AND ShpDate !='0000-00-00'
									$modtime
									AND Status='Shipped';");
			while (my ($cost) = $sth->fetchrow()){

				if(!$cost) {
					##TODO: Llamado a notif cuando no se encuetre costo de la parte

				}

				##### Ejecutamos los movements para cada salida
				&general_deposits(0,$id_orders,'orders','Inventory Out',$category,'N/A','N/A','N/A',$cost);

			}
		}else{

			##### Ejecutamos los movements para cada salida
			&general_deposits(0,$id_orders,'orders','Inventory Out',$category,'N/A','N/A','N/A',$cost);

		}
	}


	##
	### Validations
	##
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND Category = '". $category ."' AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();

	if($total_records < 2){

		$this_acc = 1;
		$this_acc_str .= " " . &trans_txt('acc_general');

	}

	delete($va{'no_time_sensitive'}) if $va{'no_time_sensitive'};
	return ($this_acc, $this_acc_str);

}



###############
###############
############### Returns . Nota: Verificiar llamados a devoluciones de mayoreo
###############
###############


#############################################################################
#############################################################################
#   Function: accounting_sale_return
#
#       Es: Ingresa los movimientos contables que representan la devolucion de un producto. En este caso el return ya se genero por lo que solamente necesitamos pedir el ultimo registro ingresado para orders_products y sobre ese ejecutar los movimientos.
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
#      - id_orders: ID order  
#      - y  
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub accounting_sale_return {
#############################################################################
#############################################################################

	## ToDo: No hay llamado para order_skus_returned de ningun tipo. Revisar al finalizar las devoluciones de mayoreo 

	my (@param_data) = @_;
	## Datos pasados por sistema
	my ($id_orders) = $param_data[0];
	## Datos pasados por configuracion
	my ($ida_septax) = scalar @param_data == 4 ? int($param_data[1]) : 0;
	my ($ida_tax_payable) = scalar @param_data == 4 ? &filter_values($param_data[2]) : 0;
	my ($ida_tax_paid) = scalar @param_data == 4 ? &filter_values($param_data[3]) : 0;
	my $str_params = join('::', @param_data);
	my $this_acc = 0; my $this_acc_str = '';
	#&cgierr($str_params);

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0|;
	
	
	my ($sth) = &Do_SQL("SELECT
				SUM(IF(LEFT(ID_products,1) <> 6,ABS(SalePrice),0)) AS SaleP,
				SUM(IF(LEFT(ID_products,1) =  6,ABS(SalePrice),0)) AS SaleS,
				SUM(ABS(Discount)) AS Discount,
				SUM(ABS(Shipping)) AS Shipping,
				SUM(ABS(Tax+ShpTax)) AS Tax
				FROM sl_orders_products WHERE ID_orders = ". $id_orders ." 
				AND SalePrice < 0 AND Status = 'Returned' AND PostedDate = CURDATE() 
				AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',TIME),NOW()) BETWEEN 0 AND 2 
				GROUP BY ID_orders;");
	
	my ($sale,$service,$discount,$shipping,$tax) = $sth->fetchrow();
	
	&general_deposits(0,$id_orders,'orders','Return Product','Devoluciones','N/A','N/A','N/A',$sale) if $sale > 0;
	&general_deposits(0,$id_orders,'orders','Return Service','Devoluciones','N/A','N/A','N/A',$service)	if $service > 0;
	&general_deposits(0,$id_orders,'orders','Return Discount','Devoluciones','N/A','N/A','N/A',$discount) if $discount > 0;
	&general_deposits(0,$id_orders,'orders','Return Shipping','Devoluciones','N/A','N/A','N/A',$shipping) if $shipping > 0;
	
	if($tax > 0 and $ida_septax == 1) {

		## Tax must be separated
		my @params  = ("$id_orders","$ida_tax_payable","$ida_tax_paid","$tax");
		&accounting_return_separate_tax(@params);
		
	} else {

		## Tax in one line
		&general_deposits(0,$id_orders,'orders','Return Tax','Devoluciones','N/A','N/A','N/A',$tax)	if $tax > 0;
		
	}

	##
	### Validations
	##
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();

	if(!$total_records){

		$this_acc = 1;
		$this_acc_str .= " <br> " . &trans_txt('acc_general');

	}

	return ($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: accounting_sale_return_fees
#
#       Es: Ingresa los movimientos contables por concepto de penalizaciones al cliente por la devolucion
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
#      - @param_data: Arreglo con datos (id_orders, $id_orders_products)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_sale_return>
#
sub accounting_sale_return_fees {
#############################################################################
#############################################################################

	## ToDo: Revisar si el llamado del tag PType debe ser listado como esta en el order_deposit y no enum de sl_orders_payments
	## ToDo: No hay llamado para order_skus_returned de ningun tipo. Revisar al finalizar las devoluciones de mayoreo
	## ToDo: Recibir los conceptos de fee por parametro?
	## ToDo: Revisar sl_keypoints_

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_return_solved
#
#       Es: Ejecuta movimientos contables cuando una devolucion es completada (No movimientos de reversa de venta sino de CR)
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
#      - param_data : Arreglo con id order, 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_keypoints>
#      <accounting_aux_return>
#      <accounting_return_finalmovements>
#
sub accounting_return_solved {
#############################################################################
#############################################################################

	## ToDo: Revisar si el llamado del tag PType debe ser listado como esta en el order_deposit y no enum de sl_orders_payments

	my (@param_data) = @_;
	my $id_orders = int($param_data[0]);

	#### Movimientos de Contabilidad para Customer Refund y A/R(este ultimo solo en caso que el cliente aun tenga pagos pendientes)
	&accounting_aux_return(@param_data);
	#### Movimientos de accouting para definir que se hace con el customer refund.	
	&accounting_return_finalmovements(@param_data);
	############# Credit Memo (Nota Credito Fiscal)
	#&export_info_for_creditmemos($id_orders);

	return;
}


sub accounting_aux_return{
#-----------------------------------------
# Created on: 06/22/09  10:27:11 By  Roberto Barcenas
# Forms Involved: 
# Description : Se encarga de hacer el customer refund y la cancelacion del A/R si es el caso.
# Parameters :
# Last Modified RB: 09/14/09  15:21:53 -- Se hace la suma completa sin importar el PostedDate
# Last Modified RB: 11/04/2010  13:18:53 -- Solo se ejecutan los movimientos si el monto devuelto es mayor a cero
 	
	my (@param_data) = @_;

	my $id_orders = int($param_data[0]);
	my $meraction = &filter_values($param_data[1]);
	my $fees = &filter_values($param_data[2]);
	my $amount = &filter_values($param_data[3]); ## Este parametro no se usa, se calcula dentro de la funcion
	my $ida_customer_refund = scalar @param_data == 5 ? int($param_data[4]) : 0;
	my $str_params = join('::', @param_data);
	#&cgierr($str_params);
	
	############
	############ 1) Total | Paid | AR -> From sl_orders_payments
	############
	my ($sth) = &Do_SQL("SELECT 
							SUM(Amount)AS Total
							, SUM(IF(Captured='Yes' AND (CapDate IS NOT NULL AND CapDate !='0000-00-00'),Amount,0)) AS Paid
							, SUM(Amount) - SUM(IF(Captured='Yes' AND (CapDate IS NOT NULL AND CapDate !='0000-00-00'),Amount,0)) AS AR
						FROM sl_orders_payments
						WHERE ID_orders = '$id_orders'
						AND Status NOT IN ('Order Cancelled','Cancelled','Void','Credit')
						AND Amount >= 0 
						GROUP BY ID_orders");
												
	my ($total,$paid,$ar) = $sth->fetchrow();
	

	############
	############ 2) Returned -> From sl_orders_products
	############
	my ($sth) = &Do_SQL("SELECT 
							SUM(ABS(SalePrice)+ABS(Shipping)+ABS(Tax)+ABS(ShpTax)-ABS(Discount)) AS Returned 
						FROM sl_orders_products 
						WHERE ID_orders = '$id_orders' 
							AND SalePrice <= 0 AND Status='Returned' 
							AND PostedDate = CURDATE() 
							AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',TIME),NOW()) BETWEEN 0 AND 50 
						GROUP BY ID_orders;");
	my ($returned) = $sth->fetchrow();
	$returned=0 if !$returned;
	
	############
	############ 3) Customer Country
	############
	my ($sth) = &Do_SQL("SELECT IF(sl_customers.Currency <> '' AND '$cfg{'acc_default_currency'}' <> '' AND sl_customers.Currency <> '$cfg{'acc_default_currency'}',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders' ;");
	my ($tcustomer) = $sth->fetchrow();
	my $keypoint1 = $tcustomer == 1 ? 'Account Receivable Local' : 'Account Receivable Foreign';
	my $keypoint2 = $tcustomer == 1 ? 'Customer Refund Local' : 'Customer Refund Foreign';

	#&cgierr("$returned - $ar - $keypoint");
	

	############
	############ 4) Evaluation
	############
	if($returned > 0){

		if($meraction ne 'Refund'){

			#####
			##### 4.1) Exchange
			#####
			&general_deposits(0,$id_orders,'orders',$keypoint2,'Devoluciones','N/A','< CURDATE','<= CURDATE',$returned);

		}else{

			#####
			##### 4.2) AR
			#####
			if($ar > 0){

				if($ar >= $returned){

					######
					###### 4.2.1) AR is Greater than Returned
					######
					&general_deposits(0,$id_orders,'orders',$keypoint1,'Devoluciones','N/A','< CURDATE','0000-00-00',$returned);
					$returned = 0;

				}else{

					######
					###### 4.2.2) AR is Lesser than Returned
					######
					&general_deposits(0,$id_orders,'orders',$keypoint1,'Devoluciones','N/A','< CURDATE','0000-00-00',$ar);
					$returned -= $ar;

				}
			}

			#####
			##### 4.3) Customer Refund
			#####
			&general_deposits(0,$id_orders,'orders',$keypoint2,'Devoluciones','N/A','< CURDATE','<= CURDATE',$returned) if $returned > 0;
			
		}

		#####
		##### 4.4) Special Customer Refund Account?
		#####
		if($ida_customer_refund){

			&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_customer_refund' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND (ID_journalentries = 0 OR ID_journalentries IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50 ORDER BY ID_movements DESC LIMIT 1;");

		}

		#####
		##### 4.5) Grouping Amounts
		#####
		&accounting_group_amounts('sl_orders',$id_orders);

		#####
		##### 4.6) Automatic Journal
		#####
		&accounting_set_automatic_journal($id_orders,'sl_orders');


	}

	return;
}
	

sub accounting_return_finalmovements{
#-----------------------------------------
# Created on: 06/22/09  15:23:59 By  Roberto Barcenas
# Forms Involved: 
# Description : Movimientos pending de customer refund 
# Parameters : 	
	
	my (@param_data) = @_;

	my $id_orders = $param_data[0];
	my $meraction = $param_data[1];
	my $fees = $param_data[2];
	my $amount = $param_data[3];
	my $ida_customer_refund = scalar @param_data == 5 ? int($param_data[4]) : 0;
	my $str_params = join('::', @param_data);
	#&cgierr($str_params);


	########
	######## 1) Customer Refund Amount + Account
	########
	my ($sth) = &Do_SQL("SELECT 
							ID_accounts
							, Amount 
						FROM sl_movements 
						WHERE ID_tableused = '$id_orders' 
							AND tableused ='sl_orders' 
							AND Credebit = 'Credit' 
							AND (ID_journalentries = 0 OR ID_journalentries IS NULL) 
							AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50 
						ORDER BY ID_movements DESC 
						LIMIT 1;");
	my ($this_ida_customer_refund, $crefund) = $sth->fetchrow();

	if($this_ida_customer_refund and $crefund > 0) {

		########
		######## 2) Customer Country
		########
		my ($sth) = &Do_SQL("SELECT IF(sl_customers.Currency <> '' AND '$cfg{'acc_default_currency'}' <> '' AND sl_customers.Currency <> '$cfg{'acc_default_currency'}',2,1)AS Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders' ;");
		my ($tcustomer) = $sth->fetchrow();
		my $keypoint = $tcustomer == 1 ? 'Customer Refund Local' : 'Customer Refund Foreign';
	
		if($meraction eq 'Refund'){

			########
			######## 3) Refund
			########
			if($fees > 0){

				########
				######## 3.1) Refund Fees
				########
				$crefund -= $fees;
				&general_deposits(-1,$id_orders,'orders',$keypoint,'Reembolsos','N/A','< CURDATE','<= CURDATE',$fees);

			}

			########
			######## 3.2) Refund Amount
			########
			&general_deposits(-1,$id_orders,'orders',$keypoint,'Reembolsos','N/A','< CURDATE','<= CURDATE',$crefund) if $crefund > 0;

		}else{

			########
			######## 4) Exchange / Chargeback
			########
			my $category = $meraction eq 'Chargeback' ? 'Contracargos' : 'Cambios Fisicos';
			&general_deposits(-1,$id_orders,'orders',$keypoint,$category,'N/A','< CURDATE','<= CURDATE',$crefund)	if $crefund > 0;

		}

		########
		######## 2.1) UPDATE To $this_ida_customer_refund
		########
		&Do_SQL("UPDATE sl_movements SET ID_accounts = '$this_ida_customer_refund', Credebit = 'Debit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND Status = 'Pending' AND (ID_journalentries = 0 OR ID_journalentries IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50 ORDER BY ID_movements DESC LIMIT 1;");

		#####
		##### 2.2) Grouping Amounts
		#####
		&accounting_group_amounts('sl_orders',$id_orders);
	}

	return;
}


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
#		 - Modified on *06/13/14* by _Roberto Barcenas_ : La categoria del movimiento se extrae del movimiento mas reciente quie exista en la orden.
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
sub order_refund {
#############################################################################
#############################################################################
 	
	my (@param_data) = @_;

	## Datos pasados por funcion
	my $id_orders = int($param_data[0]);
	my $id_payments = int($param_data[1]);
	## Datos pasados por configuracion
	my $ida_customer_refund = &filter_values($param_data[2]);
	my $ida_bank_debit_credit = &filter_values($param_data[3]);
	(!$ida_bank_debit_credit) and ($ida_bank_debit_credit = 0);
	my $str_params = join('::', @param_data);
	#&cgierr($str_params);

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;


	## Amount
	my $amount = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'ABS(Amount)');
	## Has Return Movements Already?
	#my ($sth) = &Do_SQL("SELECT IF(COUNT(*) = 0, 'Ventas', 'Reembolsos')AS type FROM sl_movements WHERE ID_tableused = '$id_orders' AND Category = 'Devoluciones'; ");
	my ($sth) = &Do_SQL("SELECT Category FROM sl_movements WHERE ID_tableused = '$id_orders' AND Status <> 'Inactive' ORDER BY FIELD(Status, 'Pending', 'Active'), ID_movements DESC LIMIT 1; ");
	my ($rtype) = $sth->fetchrow();
	$rtype = 'Reembolsos';

	
	#########
	######### 1) Bank Refund Record
	#########
	&general_deposits($id_payments,$id_orders,'orders','Refund',$rtype,'N/A','CURDATE','CURDATE',$amount);


	#########
	######### 2) CR Record Decrement
	#########
	my @ids; my $tmp_amount = $amount;
	my ($sth) = &Do_SQL("SELECT ID_movements, Amount FROM sl_movements WHERE tableused = 'sl_orders' AND ID_tableused = '$id_orders' AND ID_accounts IN(". $ida_customer_refund .") AND Status = 'Pending' ORDER BY ID_movements;");
	REFUNDS:while(my ($this_id, $this_amount) = $sth->fetchrow()){

		if($tmp_amount >= $this_amount){

			#########
			######### 2.1) Amount Refunded Greater than Record
			#########
			my ($sth) = &Do_SQL("UPDATE sl_movements SET Status = 'Active',Category = '$rtype', EffDate = CURDATE(), Date = CURDATE(), Time = CURTIME() WHERE ID_movements = '$this_id';");
			$tmp_amount -= $this_amount;

		}else{

			#########
			######### 2.1) Amount Refunded Lesser than Record
			#########

			#########
			######### 2.1.1) New Record Containing Amount Refunded
			#########			
			my (%overwrite) = ('amount' => $tmp_amount, 'status' => 'Active');
			my $applied_movement = &Do_selectinsert('sl_movements', "ID_movements = '$this_id'", "", "", %overwrite);
			&Do_SQL("UPDATE sl_movements SET EffDate = CURDATE(), Date = CURDATE(), Time = CURTIME(), Category = '$rtype', ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_movements = '$applied_movement';");

			#########
			######### 2.1.2) Old Record Amount Updated
			#########
			my ($sth) = &Do_SQL("UPDATE sl_movements SET Amount = Amount - $tmp_amount WHERE ID_movements = '$this_id';");
			$tmp_amount = 0;

		}

		push(@ids, $this_id);
		last REFUNDS if !$amount;

	}

	######### ToDo: Revisar y confirmar funcionamiento.
	######### 3) Activacion de registros de Reembolso|Contracargo. (Que no sean de cuenta contable de reembolso con nota de credito)
	#########
	my ($sth) = &Do_SQL("UPDATE sl_movements SET Status = 'Active', Category = '$rtype', EffDate = CURDATE(), Date = CURDATE(), Time = CURTIME() WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Status = 'Pending' AND Category IN('Reembolsos','Contracargos','Cambios Fisicos') AND ID_accounts NOT IN(". $ida_customer_refund .");");

	if($ida_bank_debit_credit){

		my ($ida_bank_debit, $ida_bank_credit) = split(/:/,$ida_bank_debit_credit);

		$ida_bank_debit = int($ida_bank_debit); $ida_bank_credit = int($ida_bank_credit);
		($ida_bank_debit > 0 and scalar @ids > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_debit' WHERE ID_movements IN(". join(',', @ids) .");") );
		($ida_bank_credit > 0) and (&Do_SQL("UPDATE sl_movements SET ID_accounts = '$ida_bank_credit' WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND Amount = '$amount' AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50 LIMIT 1;") );

	}

	### Se guarda el ID_orders_payments
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_orders_payments', ID_tablerelated = '". $id_payments ."' WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND ". $sqlmod_update_records .";");

	&accounting_group_amounts('sl_orders', $id_orders);

	return;
}
	

#############################################################################
#############################################################################
#   Function: order_credit_memos
#
#       Es: Inserta el movimiento de contabilidad por la aplicacion de un credit memo
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#		- Se agrega nuevo parametro para saber si el cm es de productos o servicios. Con esto se podria cambiar la categoria entre uno y otro para mayor detalle
#		- En el update de ida_customers, se elimina la busqueda de alguna de las cuentas de ida_customers pasadas por keypoint y solamente se apunta a la ultima generada.
#		- Se regresa version anterior. No se puede actualizar la cuenta de Credito porque dejan de funcionar los tipos 1 y 2
#
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_orders,$amount,$tax,$currency_exchange)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub order_credit_memos {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	## Parametros pasados por funcion
	my $id_orders = int($param_data[0]);
	my $amount = &filter_values($param_data[1]);
	my $tax = &filter_values($param_data[2]);
	my $exchange_rate = &filter_values($param_data[3]);
	my $cm_type = &filter_values($param_data[4]);
	my $cm = &filter_values($param_data[5]);
	my $devol_type = &filter_values($param_data[6]);
	## Parametros pasados por configuracion
	my $ida_profit = int($param_data[7]);
	my $ida_lost = int($param_data[8]);
	my $ida_customers = $param_data[9] ? &filter_values($param_data[9]) : 0;
	my $str_params = join('::', @param_data);

	my $cm_category = $cm_type eq 'prod' ? 'Devoluciones' : 'Devoluciones';
	$devol_type = 'N/A' if(&filter_values($param_data[6]) eq '');
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	my $amount_original = $amount;
	$amount = round($amount * $exchange_rate,3);
	$tax = round($tax * $exchange_rate,3);
	#&cgierr($str_params . qq|\nC: $va{'currency'}|);


	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;

	
	###
	### 1) Buscamos cuenta de cliente
	###
	my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status = 'Active' AND ID_accounts IN(". $ida_customers .") ORDER BY ID_movements LIMIT 1;");
	my ($this_ida_customers) = $sth->fetchrow();

	###
	### 2) Aplicamos contabilidad Normalmente
	###
	&general_deposits(0,$id_orders,'orders','Credit Memo',$cm_category,$devol_type,'N/A','N/A',$amount) if $amount > 0;
	&general_deposits(0,$id_orders,'orders','Credit Memo Net',$cm_category,$devol_type,'N/A','N/A',($amount + $tax)) if $amount > 0;
	&general_deposits(0,$id_orders,'orders','Credit Memo Tax',$cm_category,$devol_type,'N/A','N/A',$tax) if $tax > 0;

	###
	### 3) Fluctuacion Cambiaria
	###
	if( $cfg{'acc_default_currency'} ne '' and uc($va{'currency'}) ne uc($cfg{'acc_default_currency'})){

		my $id_payments = 0; $in{'ida_banks'} = 0;
		my @params = ($id_orders, $id_payments, $amount_original, $exchange_rate, $ida_customers, $in{'ida_banks'}, $ida_profit, $ida_lost, "Devoluciones");
		my ($this_res, $this_res_str) = &order_deposit_profit_lost(@params);
		if($this_res){ $this_acc++; $this_acc_str .= $this_res_str; }

	}
	
	###
	### 4) Cambiamos cuenta de abono por original
	###
	if($this_ida_customers){	
		&Do_SQL("UPDATE sl_movements SET ID_accounts = '". $this_ida_customers ."' WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND ID_accounts IN(". $ida_customers .") AND Category = 'Devoluciones' AND Status = 'Active' AND ". $sqlmod_update_records ." ORDER BY ID_movements DESC LIMIT 1;");
	}

	###
	### 5) Actualizacion de tablerelated
	###	
	if($cm > 0) {
		&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_creditmemos', ID_tablerelated = '". $cm ."' WHERE tableused = 'sl_orders' AND id_tableused = '". $id_orders ."' AND ID_tablerelated = 0 AND Category = 'Devoluciones' AND Status = 'Active' AND ". $sqlmod_update_records .";");
	}

	###
	### 6) Agrupamos montos
	###	
	&accounting_group_amounts('sl_orders', $id_orders);

	return;
}


#############################################################################
#############################################################################
#   Function: order_credit_memos_return
#
#       Es: Crea la contabilidad al aprobarse o aplicarse un CM de devolución de mercancía
#
#    Created on: 2015-06-08
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
#
#
#   Parameters:
#     
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub order_credit_memos_return {
#############################################################################
#############################################################################
	my (@param_data) = @_;

	my $id_orders		= int($param_data[0]);	
	my $amount			= &filter_values($param_data[1]); 
	my $tax				= &filter_values($param_data[2]);
	my $exchange_rate	= &filter_values($param_data[3]);
	my $id_cm			= int($param_data[4]);
	$exchange_rate = 1 if(!$exchange_rate or $exchange_rate == 0);
	
	#my $str_params = join('::', @param_data);
	#&cgierr($str_params);

	$amount = round($amount * $exchange_rate, 3);

	###
	### Contabilidad
	###
	if( $amount > 0 ){
		&general_deposits(0,$id_orders,'orders','Credit Memo Charge','Cobranza','N/A','N/A','N/A',($amount+$tax));
		&general_deposits(0,$id_orders,'orders','Credit Memo Charge Net','Cobranza','N/A','N/A','N/A',($amount+$tax));
	}
	# if( $tax > 0 ){
	# 	$tax = round($tax * $exchange_rate, 3);
	# 	&general_deposits(0,$id_orders,'orders','Credit Memo Charge Tax','Cobranza','N/A','N/A','N/A',$tax);
	# }
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_creditmemos', ID_tablerelated = '$id_cm', ID_journalentries = 0 WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND tablerelated IS NULL AND ID_tablerelated = 0 AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 10;");
	
	return;
}


#############################################################################
#############################################################################
#   Function: chargeback_open
#
#       Es: Genera movimientos de contabilidad por proceso de contracagro
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_orders,$id_payments, exchange_rate)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub chargeback_open {
#############################################################################
#############################################################################
 	
	my (@param_data) = @_;

	## Datos pasados por funcion
	my $id_orders = int($param_data[0]);
	my $id_payments = int($param_data[1]);
	my $exchange_rate = &filter_values($param_data[2]);
	my $this_event = &filter_values($param_data[3]);
	my $this_isshipped = &filter_values($param_data[4]);
	## Datos pasados por configuracion
	my $ida_banks = &filter_values($param_data[5]);
	my $ida_deposits = &filter_values($param_data[6]);
	my $ida_customer_refund = &filter_values($param_data[7]);
	my $ida_lost = &filter_values($param_data[8]);
	my $ida_tax_paid = &filter_values($param_data[9]);
	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);


	###
	### 1) Sacamos el monto
	###
	my $amount = &load_name('sl_orders_payments','ID_orders_payments',$id_payments,'ABS(Amount)');
	$amount = &round($amount * $exchange_rate,2);


	###
	### 2) Existe Custome Refund? Si es asi, es un contracargo que ya tiene una devolucion (Orden Shipped)
	###
	my ($sth) = &Do_SQL("SELECT 
							ID_movements
						FROM
							sl_movements
						WHERE
							ID_tableused = '". $id_orders ."'
							AND tableused = 'sl_orders'
							AND Category = 'Reembolsos'
							AND ID_accounts IN(". $ida_customer_refund .")
							AND ABS(Amount - ". $amount .") < 1
							AND Status = 'Pending'
							AND Credebit = 'Debit'
						ORDER BY 
							EffDate DESC,
							ID_movements DESC 
						LIMIT 1;");
	my ($this_ida_refund) = $sth->fetchrow();
	$this_ida_refund = 0 if !$this_ida_refund;
	my $this_ida_debit = 0; my $this_ida_credit; my $this_ida_taxpaid; my $this_amount_taxpaid = 0;

	###
	### 3) Buscamos anticipo anterior debit/credit
	###
	
	## 3.1 Cargo(Banco)	
	my ($sth) = &Do_SQL("SELECT 
							ID_movements
						FROM
							sl_movements
						WHERE
							ID_tableused = '". $id_orders ."'
							AND tableused = 'sl_orders'
							AND Category = 'Anticipo Clientes'
							#AND ID_accounts IN(". $ida_banks .")
							AND Status = 'Active'
							AND Credebit = 'Debit'
						ORDER BY 
							EffDate DESC,
							ID_movements DESC 
						LIMIT 1;");
	$this_ida_debit = $sth->fetchrow();


	if(!$this_ida_refund){

		## 3.2 Solamente se busca Abono si no se encontro customer refund (Orden Unshipped)
		my ($sth2) = &Do_SQL("SELECT 
								ID_movements
							FROM
								sl_movements
							WHERE
								ID_tableused = '". $id_orders ."'
								AND tableused = 'sl_orders'
								AND Category = 'Anticipo Clientes'
								AND ID_accounts IN(". $ida_deposits .")
								AND Status = 'Active'
								AND Credebit = 'Credit'
							ORDER BY 
								EffDate DESC,
								ID_movements DESC 
							LIMIT 1;");
		$this_ida_credit = $sth2->fetchrow();

		## 3.3 Solamente se busca Tax si no hay Refund y si existe la variable isshipped (Contracargo de Envios NO Recuperados)
		if($this_isshipped){

			my ($sth) = &Do_SQL("SELECT 
									ID_movements
									, Amount 
								FROM 
									sl_movements 
								WHERE 
									tableused = 'sl_orders' 
									AND ID_tableused = '". $id_orders ."' 
									AND ID_accounts IN(". $ida_tax_paid .")
									AND Credebit = 'Credit'
									AND Status = 'Active' 
								ORDER BY 
									EffDate DESC, 
									ID_movements DESC 
								LIMIT 1;");
			($this_ida_taxpaid, $this_amount_taxpaid) = $sth->fetchrow();
			$this_ida_taxpaid = 0 if !$this_ida_taxpaid;
			$this_amount_taxpaid = 0 if !$this_amount_taxpaid;

		}

	}

	###
	### 3) Validacion
	###
	if(!$this_ida_debit or (!$this_ida_credit and !$this_ida_refund) ){
		return (1,'Original Movements not Found');
	}

	###
	### 4) Aplicamos reversa de los movimientos. Si es refund solamente se hace la reversa del anticipo, no del banco y ademas se deja en Pending en espera de que se haga la devolucion del dinero para activarse
	###
	my $this_category = lc($this_event) eq 'chargeback' ? 'Contracargos' : 'Reembolsos';
	my (%overwrite) = ('category' => $this_category, 'date' => 'CURDATE()', 'time' => 'CURTIME()');
	my $applied_movement_credit = $this_ida_refund ? $this_ida_refund : &Do_selectinsert('sl_movements', "ID_movements = '". $this_ida_credit ."'", "", "", %overwrite);
	my $applied_movement_tax = ($this_ida_refund and !$this_ida_taxpaid) ? -1 : &Do_selectinsert('sl_movements', "ID_movements = '". $this_ida_taxpaid ."'", "", "", %overwrite);
	$applied_movement_tax = -1 if !$applied_movement_tax;
	my $applied_movement_debit = lc($this_event) eq 'chargeback' ? &Do_selectinsert('sl_movements', "ID_movements = '$this_ida_debit'", "", "", %overwrite) : $applied_movement_credit;
	&Do_SQL("UPDATE 
				sl_movements 
			SET 
				Credebit = IF(
								ID_movements = '". $this_ida_refund ."', Credebit,
								IF(
									ID_movements IN ('". $applied_movement_credit ."', '". $applied_movement_tax ."'),'Debit',
									'Credit'
								)
							)
				, Amount = IF(". $this_isshipped ." = 1 AND '". lc($this_event) ."' = 'chargeback' AND ID_accounts IN(". $ida_deposits .") AND ID_movements = '". $applied_movement_credit ."' AND $this_amount_taxpaid > 0, Amount - ". $this_amount_taxpaid ." , Amount)
				, ID_accounts = IF(". $this_isshipped ." = 1 AND '". lc($this_event) ."' = 'chargeback' AND ID_accounts IN(". $ida_deposits .") AND ID_movements = '". $applied_movement_credit ."', ". $ida_lost ." , ID_accounts)			
				, Status = IF('". lc($this_event) ."' = 'chargeback', 'Active', 'Pending')
				, Category = IF('". lc($this_event) ."' = 'chargeback', 'Contracargos', 'Reembolsos')
				, EffDate = CURDATE()
				, tablerelated = NULL
				, ID_tablerelated = '0'
				, ID_journalentries = '0'
				, Date = CURDATE()
				, Time = CURTIME()
				, ID_admin_users = '". $usr{'id_admin_users'} ."' 
			WHERE 
				ID_movements IN (". $applied_movement_debit .",". $applied_movement_credit .",". $applied_movement_tax .")
				AND ID_movements > 0;");
	
	if($applied_movement_debit and $applied_movement_credit){
		return (0,'done');
	}else{
		return (1,'Reverse Movements Problem');
	}


}


###############
###############
############### Inventory
###############
###############


#############################################################################
#############################################################################
#   Function: accounting_vendor_deposit
#
#       Es: Ejecucion de contabilidad para anticipo a proveedores
#       En: Accouting movements when Vendor deposit is made
#
#
#    Created on: 05/09/2013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *06/26/2013* by _Roberto Barcenas_ : Se toma la cuenta contable proveniente del Bill
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_vendors,$ida_banks,$amount,$currency_exchange, $ida_vendor_deposit, $type)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_po_payment>
#   	<accounting_po_paid>
#
#
#
#  ToDO: #1 Se agrega la toma de cuenta deudora del proveedor. Se comenta mientras hay aprobacion
#  ToDO: #2 Se descomenta para pruebas en pp, con finalidad de pasar a produccion
#
sub accounting_vendor_deposit  {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	###### Pasadas por parametros
	my $id_vendors = int($param_data[0]);
	my $id_bills = int($param_data[1]);
	my $ida_banks = int($param_data[2]);
	my $bankdate = &filter_values($param_data[3]);
	my $amount = &filter_values($param_data[4]);
	my $exchange_rate = &filter_values($param_data[5]);
	###### Pasadas por configutacion
	my $ida_vendor_deposit = &filter_values($param_data[6]);
	my $category = int($param_data[7]);
	my $str = "$id_vendors - $id_bills - $ida_banks - $bankdate - $amount - $exchange_rate - $ida_vendor_deposit - $category";

	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	$amount = round($amount * $exchange_rate,3) ;

	if($amount > 0) {

		###
		### El Bill tenia una cuenta diferente?
		###
		my $id_segments = 0;
		my ($sth) = &Do_SQL("SELECT IF(ID_accounts > 0,ID_accounts,0) FROM sl_bills WHERE ID_bills = '$id_bills' AND Type = 'Deposit';");
		my ($this_ida_deposit) = $sth->fetchrow();
		if(!$this_ida_deposit) {
			my ($sth) = &Do_SQL("SELECT sl_bills_expenses.ID_accounts, sl_bills_expenses.ID_segments FROM sl_bills INNER JOIN sl_bills_expenses USING(ID_bills) WHERE sl_bills.ID_bills = '$id_bills' AND Type = 'Deposit';");
			($this_ida_deposit, $id_segments) = $sth->fetchrow();
		}
		(!$this_ida_deposit) and ($this_ida_deposit = $ida_vendor_deposit);
		(!$id_segments) and ($id_segments = 0);

		my $acc_deposit = 'Vendor Deposit '.$type;

		#&cgierr("$acc_deposit -- $id_vendors : $amount : $ida_vendor_deposit");

		&general_deposits(0,$id_vendors,'vendors',$acc_deposit,"Pagos",'N/A','N/A','N/A',$amount);
		&Do_SQL("/* $acc_deposit: $amount  */ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($ida_banks,'".$amount."', '', CURDATE(), 'sl_vendors', $id_vendors, 'Pagos', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_bills', ID_tablerelated = '$id_bills', ID_segments = '$id_segments',EffDate = '$bankdate' WHERE ID_tableused = '$id_vendors' AND tableused = 'sl_vendors' AND (ID_tablerelated = 0 OR ID_tableused IS NULL) AND (ID_journalentries = 0 OR ID_journalentries IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50 ORDER BY ID_movements DESC LIMIT 2;");


		###
		## Buscamos cuenta Deudora en Proveedor
		### 
		my $query = "SELECT 
						ID_accounts_debit 
					FROM 
						sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors 
					WHERE 
						sl_bills.ID_bills = ". $id_bills .";";
		my ($sth) = &Do_SQL($query);
		my ($this_ida_vendor_debit) = $sth->fetchrow();
		$this_ida_deposit = $this_ida_vendor_debit if $this_ida_vendor_debit;

		&Do_SQL("UPDATE sl_movements SET ID_accounts = ". $this_ida_deposit ." WHERE ID_tableused = ". $id_vendors ." AND tableused = 'sl_vendors' AND Credebit = 'Debit' AND ID_accounts IN(". $ida_vendor_deposit .") AND (ID_journalentries = 0 OR ID_journalentries IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50;"); 

	}

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_po_apply_deposit
#
#       Es: Ejecucion de contabilidad para aplicacion de anticipo a proveedores
#       En: Accouting movements when Vendor deposit is applied to a PO
#
#
#    Created on: 05/14/2013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *07/09/2013* by _Roberto Barcenas_ : Se busca la cuenta contable del proveedor para afectarla, antes se tomaba directamente proveedores de mercancia, pero puede ser proveedor de servicios
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_po,$ida_banks,$this_amount,$currency_exchange, $ida_vendor_deposit, $ida_vendor, $ida_tax_payable, $ida_tax_paid, $type)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#   	<accounting_po_payment>
#   	<accounting_pod_paid>
#
#
sub accounting_po_apply_deposit  {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	## Pasados via parametros en la funcion que lo manda llamar
	my $id_po = int($param_data[0]);
	my $id_bills = int($param_data[1]);
	my $ida_banks = int($param_data[2]);
	my $amount = &filter_values($param_data[3]);
	my $exchange_rate = &filter_values($param_data[4]);
	## Pasados via parametros en el setup de la funcion
	my $ida_vendor_deposit = filter_values($param_data[5]);
	my $ida_vendor = filter_values($param_data[6]);
	my $ida_tax_payable = int($param_data[7]);
	my $ida_tax_paid = int($param_data[8]);
	my $category = int($param_data[9]);
	my $ida_profit = int($param_data[10]);
	my $ida_lost = int($param_data[11]);
	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);
	
	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);


	##
	### Buscamos Cuenta de Proveedor y Anticipo
	##
	my $this_ida_vendor = 0; my $this_ida_vendor_deposit = 0;
	my $id_vendors = &load_name('sl_bills','ID_bills',$id_bills,'ID_vendors');
	my ($sth) = &Do_SQL("SELECT ID_accounts_debit, ID_accounts_credit FROM sl_vendors WHERE ID_vendors = ". $id_vendors .";");
	($this_ida_vendor_deposit, $this_ida_vendor) = $sth->fetchrow();


	###
	##  Cuenta De Proveedor
	###
	if(!$this_ida_vendor){

		#1.1. En el PO 
		my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND Credebit = 'Credit' AND ID_accounts IN($ida_vendor) AND Status = 'Active' ORDER BY EffDate LIMIT 1;");
		$this_ida_vendor = $sth->fetchrow();

	}

	if(!$this_ida_vendor){

		#1.2. En las cuentas parametrizadas
		my @ary = split(/,/, $ida_vendor);
		$this_ida_vendor = int($ary[0]);

	}
	(!$this_ida_vendor) and ($this_ida_vendor = 1);


	##
	### Cuenta de Anticipo
	##
	
	if(!$this_ida_vendor_deposit){

		#2.1. En el Anticipo
		my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tablerelated = ". $id_bills ." AND tablerelated = 'sl_bills' AND Credebit = 'Debit' AND Category = 'Pagos' AND Status = 'Active' ORDER BY EffDate LIMIT 1;");
		my ($this_ida_bills_deposit) = $sth->fetchrow();
		$this_ida_vendor_deposit = $this_ida_bills_deposit if $this_ida_bills_deposit;

	}

	if(!$this_ida_vendor_deposit){

		#2.2 En las cuentas parametrizadas
		my @ary = split(/,/, $ida_vendor);
		my @ary2 = split(/,/, $ida_vendor_deposit);
		for (0..$#ary) {
			$this_ida_vendor_deposit = $ary2[$_] if $ary[$_] eq $this_ida_vendor;
		}

	}
	(!$this_ida_vendor_deposit) and ($this_ida_vendor_deposit = 1);

	####################
	####################
	####### 1) Buscamos Total del PO debido y taxes si es que se tienen
	####################
	####################
	my ($sth) = &Do_SQL("/* amt: $amount */ SELECT 
						ROUND( SUM(Received * Price * (1+Tax_percent)), 2)AS Total_Received, 
						ROUND( SUM(Received * Price * Tax_percent), 2) AS Tax_Received
						FROM sl_purchaseorders_items WHERE ID_purchaseorders = '$id_po'
						AND Received > 0;");
	my ($sum_total, $sum_tax) = $sth->fetchrow();
	my $sum_cost = $sum_total - $sum_tax;

	#######
	####### Factor pagado
	#######
	if($sum_tax > 0) {
		$pct = $amount / $sum_total;
		$amount_tax = round($sum_tax * $pct,2);
		#$amount -= $amount_tax;
	}

	#######
	####### Currency Exchange (Convert to Default Currency)
	#######
	my $amount_original = $amount;
	my $tax_original = $amount_tax;
	$amount *= $exchange_rate;
	$amount_tax *= $exchange_rate if $amount_tax;


	if($amount > 0 and $this_ida_vendor){

		####################
		####################
		####### 2) Aplicamos el pago de acuerdo a los datos
		####################
		####################
		my $acc_payments = 'Purchase Order Apply Deposit '.$type;
		my $acc_tax = 'Purchase Order Payment Tax '.$type;

		#&general_deposits(0,$id_po,'purchaseorders',$acc_payments,"Aplicacion Anticipos AP",'N/A','N/A','N/A',$amount);
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($this_ida_vendor,'".$amount."', '', CURDATE(), 'sl_purchaseorders', $id_po, 'Aplicacion Anticipos AP', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Aplicacion Anticipos AP','N/A','N/A','N/A',$amount_tax) if $amount_tax > 0;
		&Do_SQL("/*$amount_tax - $sum_tax * $pct*/ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($this_ida_vendor_deposit,'".$amount."', '', CURDATE(), 'sl_purchaseorders', $id_po, 'Aplicacion Anticipos AP', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		
		####################
		####################
		####### 3) Fluctuacion cambiaria
		####################
		####################
		my @params = ($id_po, $id_bills, $amount_original, $tax_original, $exchange_rate, $this_ida_vendor, $ida_tax_payable, $ida_tax_paid, $ida_profit, $ida_lost);
		&bills_po_exchange_profit_lost(@params);

		####################
		####################
		####### 4) Aplicamos Related Table
		####################
		####################
		if($id_bills){
			&Do_SQL("UPDATE sl_movements SET ID_journalentries = 0,tablerelated = 'sl_bills', ID_tablerelated = '$id_bills' WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND (ID_tablerelated = 0 OR ID_tablerelated IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 30 AND ID_admin_users = '$usr{'id_admin_users'}';");
		}

		############
		############ Check for Paid Bill
		############
		my @params = ($id_po, $ida_vendor, $ida_profit, $ida_lost);
		&bills_po_check_paid(@params);

		&accounting_group_amounts('sl_purchaseorders', $id_po);

	}

}


#############################################################################
#############################################################################
#   Function: accounting_po_payment 
#
#       Es: Ejecucion de contabilidad cuando se realiza un pago del PO
#       En: Accouting movements when PO payment is posted
#
#
#    Created on: 05/09/2013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on *07/09/2013* by _Roberto Barcenas_ : Se busca la cuenta contable del proveedor para afectarla, antes se tomaba directamente proveedores de mercancia, pero puede ser proveedor de servicios#
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_po,$id_banks,$amount,$amount_d$vendor_type,$ida_tax_payabla,$ida_tax_paid)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#   	<accounting_pod_paid>
#
#
sub accounting_po_payment  {
#############################################################################
#############################################################################

	my (@param_data) = @_;
	my ($pct,$amount_tax,$amount_cost,$this_acc,$this_acc_str);


	## Pasados a traves de la funcion que lo llama
	my $id_po = int($param_data[0]);
	my $id_bills = int($param_data[1]);
	my $ida_banks = int($param_data[2]);
	my $amount = &filter_values($param_data[3]);
	my $exchange_rate = &filter_values($param_data[4]);
	my $id_po_adj = int($param_data[5]);
	## Pasados a traves de parametros en el setup de la funcion
	my $category = int($param_data[6]);
	my $ida_tax_payable = &filter_values($param_data[7]);
	my $ida_tax_paid = &filter_values($param_data[8]);
	my $ida_vendor = &filter_values($param_data[9]);
	my $ida_profit = int($param_data[10]);
	my $ida_lost = int($param_data[11]);
	#my $str_params = join('||', @param_data);
	#&cgierr($str_params);

	my $type = $category == 2 ? 'Foreign' : 'Local';
	my $amount_cost = $amount;
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	my $pct;

	####################
	####################
	####### 1) Buscamos movimientos de deuda al proveedor para comprobar pago vs anticipo
	####################
	####################
	my $qry_adj = ""; my $this_ida_vendor = 0;
	if($id_po_adj){

		my $id_vendor_po_adj = &load_name('sl_purchaseorders_adj', 'ID_purchaseorders_adj', $id_po_adj, 'ID_vendors');
		$this_ida_vendor = &load_name('sl_vendors', 'ID_vendors', $id_vendor_po_adj, 'ID_accounts_credit');
		my $ida_iva_ret = ($cfg{'ida_iva_retention'}) ? $cfg{'ida_iva_retention'} : 0;
		$qry_adj = "AND (tablerelated='sl_bills' AND ID_tablerelated='$id_bills' AND Reference Like 'Vendor GA: ".int($id_vendor_po_adj)."%' AND ID_accounts != $ida_iva_ret)";
		## 1201 = IVA RETENIDO POR TRANSPORTISTAS
	
	}else{

		my ($sth) = &Do_SQL("SELECT ID_accounts_credit FROM sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors WHERE sl_bills.ID_bills = ". $id_bills .";");
		$this_ida_vendor = $sth->fetchrow();

	}

	if(!$this_ida_vendor){

		my $qv = "SELECT ID_accounts FROM sl_movements WHERE ID_tableused = ". $id_po ." AND tableused = 'sl_purchaseorders' AND Credebit = 'Credit' $qry_adj AND Status = 'Active' ORDER BY Amount DESC, ID_movements LIMIT 1;";
		my ($sth) = &Do_SQL($qv);
		$this_ida_vendor = $sth->fetchrow();

	}

	if(!$this_ida_vendor){
		@ary = split(/,/, $ida_vendor);
		$this_ida_vendor = int($ary[0]);
	}


	####################
	####################
	####### 2) Buscamos Total del PO debido y taxes si es que se tienen
	####################
	####################
	my $qd = "SELECT 
				SUM(
					IF(ID_accounts IN(". $ida_vendor .") AND Credebit = 'Credit', Amount, 0)
					- 
					IF(ID_accounts IN(". $ida_vendor .") AND Credebit = 'Debit', Amount, 0)
				)
				, SUM(
					IF(ID_accounts IN(". $ida_tax_payable .") AND Credebit = 'Debit', Amount, 0)
					- 
					IF(ID_accounts IN(". $ida_tax_payable .") AND Credebit = 'credit', Amount, 0)
				)
				, IF(Credebit = 'Credit',ID_accounts,0) 
			FROM 
				sl_movements 
			WHERE 
				ID_tableused = ". $id_po ."
				AND tableused = 'sl_purchaseorders' 
				$qry_adj  
				AND Status = 'Active';";

	my ($sth) = &Do_SQL($qd);
	my ($amount_due, $tax_due) = $sth->fetchrow();

	if(!$amount_due) {

		### No tiene deuda, debe ser un anticipo al vendor
		### ToDo RB: Teoricamente esto no sucede, pero si sucediera esto tendria que revisarse desde la aplicacion de pago en CxP
		my $id_vendors = &load_name('sl_purchaseorders','ID_purchaseorders',$id_po,'ID_vendors');

	}

	my $qt = "/* amt: $amount , $exchange_rate */ SELECT 
						SUM(Received * Price * (1+Tax_percent))AS Total_Received, 
						SUM(Received * Price * Tax_percent) AS Tax_Received
						FROM sl_purchaseorders_items WHERE ID_purchaseorders = ". $id_po ."
						AND Received > 0;";
	my ($sth) = &Do_SQL($qt);
	my ($sum_total, $sum_tax) = $sth->fetchrow();
	$sum_total = round($sum_total,2); $sum_tax = round($sum_tax, 2);

	### PO Services
	my $po_type = &load_name('sl_purchaseorders','ID_purchaseorders',$id_po,'Type');

	if($id_po_adj){

		## 2.1. Si es GA, se toman los datos de la contabilidad
		$sum_total = round($amount_due,2);
		$sum_tax = round($tax_due,2);

	} elsif( $po_type eq 'PO Services' ){

		## Si es una OC de servicios se toma el tax due de la contabilidad
		$sum_tax = round($tax_due,2);
		$sum_total = round($amount,2);

	}
	my $sum_cost = $sum_total - $sum_tax;


	#######
	####### Factor  
	#######
	if($sum_tax > 0){

		$pct = ($sum_total > 0) ? round($amount / $sum_total,2) : 0;
		$amount_tax = round($sum_tax * $pct,2);
		$amount_cost -= $amount_tax;

	}
	$this_acc_str .= qq|QD: $qd\nQV: $qv\nQT: $qt\nAmountDue: $amount_due\nTax Due: $tax_due\nIDAVendor: $this_ida_vendor\nStotal: $sum_total\nSTax: $sum_tax\nSCost: $sum_cost\nPct: $pct\nAmt: $amount\nATax: $amount_tax\nAcost: $amount_cost|;

	#######
	####### Currency Exchange (Convert to Default Currency)
	#######
	my $amount_original = $amount;
	my $tax_original = $amount_tax;
	$amount *= $exchange_rate;
	$amount_cost *= $exchange_rate;
	$amount_tax *= $exchange_rate if $amount_tax;

	####################
	####################
	####### 3) Aplicamos el pago de acuerdo a los datos
	####################
	####################
	my $acc_payments = 'Purchase Order Payment '.$type;
	my $acc_tax = 'Purchase Order Payment Tax '.$type;

	#&general_deposits(0,$id_po,'purchaseorders',$acc_payments,"Pagos",'N/A','N/A','N/A',$amount);
	&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($this_ida_vendor,'".$amount."', '', CURDATE(), 'sl_purchaseorders', $id_po, 'Pagos', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Pagos','N/A','N/A','N/A',$amount_tax) if $amount_tax > 0;
	&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($ida_banks,'".$amount."', '', CURDATE(), 'sl_purchaseorders', $id_po, 'Pagos', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	####################
	####################
	####### 4) Fluctuacion cambiaria
	####################
	####################
	my @params = ($id_po, $id_bills, $amount_original, $tax_original, $exchange_rate, $this_ida_vendor, $ida_tax_payable, $ida_tax_paid, $ida_profit, $ida_lost, "Pagos");
	my ($this_st, $this_st_str) = &bills_po_exchange_profit_lost(@params);
	$this_acc++ if $this_st; $this_acc_str .= $this_st_str;

	## Actualizacion de tablerelated asignando el id_bills
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_bills', ID_tablerelated = '$id_bills' WHERE tableused = 'sl_purchaseorders' AND ID_tableused = '$id_po' AND Category = 'Pagos' AND ( ID_tablerelated IS NULL OR ID_tablerelated = 0 ) AND (ID_journalentries IS NULL OR ID_journalentries = 0) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50;")

	&accounting_group_amounts('sl_purchaseorders', $id_po);

	return($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: accounting_po_paid 
#
#       Es: Ejecucion de contabilidad cuando se termina de pagar un PO
#       En: Accouting movements when PO is paid
#
#
#    Created on: 05/09/2013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_po,$amount_due,$vendor_type)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#   	<accounting_po_payment>
#
sub accounting_po_paid {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $id_po = int($param_data[0]);
	my $amount_due = &filter_values($param_data[1]);
	my $exchange_rate = &filter_values($param_data[2]);
	my $category = int($param_data[3]);
	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	my $pct;


	####################
	####################
	####### Si el PO esta pagado completo, sacamos la perdida o ganancia 
	####### Nota: Solo aplica en P.O.s con currency diferente al default de la empresa
	####################
	####################
	if($cfg{'acc_default_currency'} and !$amount_due) {

		my ($sth) = &Do_SQL("SELECT Currency FROM sl_purchaseorders INNER JOIN sl_vendors USING(ID_vendors) WHERE ID_purchaseorders = '$id_po';");
		my($vendor_currency) = $sth->fetchrow();

		if ($vendor_currency and $vendor_currency ne $cfg{'acc_default_currency'}) {

			my ($sth) = &Do_SQL("SELECT SUM(IF(Credebit = 'Debit',Amount,0))AS Debits, SUM(IF(Credebit = 'Credit',Amount,0))AS Credits FROM sl_movements WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND EffDate <= CURDATE() AND Status = 'Active';");
			my ($sum_debits, $sum_credits) = $sth->fetchrow();
			my $amount_difference = $sum_debits - $sum_credits;

			my $acc_debit = 'Purchase Order Currency Exchange Lost ' . $type;
			my $acc_credit = 'Purchase Order Currency Exchange Gain ' . $type;

			if($amount_difference > 0){
				## Ganancia Cambiaria
				&general_deposits(0,$id_po,'purchaseorders',$acc_credit,"Pagos",'N/A','N/A','N/A',$amount_difference);
			}elsif($amount_difference < 0){
				## Perdida Cambiaria
				&general_deposits(0,$id_po,'purchaseorders',$acc_debit,"Pagos",'N/A','N/A','N/A',$amount_difference * -1);
			}

		}

	}

}


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
#        - Modified on *04/11/2016* by _Roberto Barcenas_ : Se agrega $this_ida_vendor_credit y se deja en cero en espera de validacion por parte del area contable para activar.
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
sub accounting_wreceipt_inventory_in {
#############################################################################
#############################################################################

	my (@param_data) = @_;
	my ($taxpc,$tax,$taxp);

	my $id_po = int($param_data[0]);
	my $id_poi = int($param_data[1]); ## Linea de PO Items Recibida
	my $qty = int($param_data[2]);
	my $cost = $param_data[3];
	my $proportional_adj = &filter_values($param_data[4]); ## ajuste monto proporcional
	my $proportional_adjt = &filter_values($param_data[5]); ## ajuste tax proporcional
	my $id_sku = int($param_data[6]);
	my $exchange_rate = &filter_values($param_data[7]); ## This is the exchange rate value,if it's not eq 1 then it's international
	my $category = int($param_data[8]);
	my $type = $category == 2 ? 'Foreign' : 'Local';

	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);
	my ($ids_debit, $ids_credit);

	#my $imported_merchandise = $exchange_rate == 1 ? 0 : 1;
	
	#&cgierr("$id_po, $qty, $cost, $id_sku, $imported_merchandise");

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;

	my $amt = $qty * $cost;
	my $amt_adj = $proportional_adj ? $proportional_adj * $qty : 0;
	my $tax_adj = $proportional_adjt ? $proportional_adjt * $qty : 0;

	$taxpc = &load_name('sl_purchaseorders_items','ID_purchaseorders_items',$id_poi,'Tax_percent');
	$taxpc = !$taxpc ? 0 : $taxpc * 100;
	
	my ($sth) = &Do_SQL("SELECT
					/* Sumanos lo recibido + tax + monto_ajuste + tax_ajuste*/ 
					IF(ToPayNet IS NULL,0,ToPayNet) +
					IF(ToPayTax IS NULL,0,ToPayTax) +
					". $amt_adj ." + ". $tax_adj ." AS Received,
					/*IF(Payments IS NULL,0,Payments)AS Paid*/
					0 AS Paid
					FROM sl_purchaseorders
					LEFT JOIN
					(
						SELECT ID_purchaseorders, 
						SUM( Received * Price * ". $exchange_rate ." ) AS ToPayNet,
						SUM( Tax / Received) AS ToPayTax
						FROM sl_purchaseorders_items
						WHERE ID_purchaseorders = ". $id_po ."
						GROUP BY ID_purchaseorders
					)AS tmp_po
					USING(ID_purchaseorders)
					/*LEFT JOIN
					(
						SELECT ID_purchaseorders, 
						SUM( Total ) AS ToPayAdj,
						ID_accounts
						FROM sl_purchaseorders_adj
						WHERE ID_purchaseorders = ". $id_po ."
						AND InCOGS = 'Yes'
						AND Status = 'Active'
						GROUP BY ID_purchaseorders
					)AS tmp_adj
					USING(ID_purchaseorders)
					LEFT JOIN
					(
						SELECT ID_purchaseorders, SUM( Amount ) AS Payments
						FROM sl_vendors_payments
						WHERE ID_purchaseorders = ". $id_po ."
						GROUP BY ID_purchaseorders
					)AS tmp_pay
					USING(ID_purchaseorders)
					*/
					WHERE sl_purchaseorders.ID_purchaseorders = ". $id_po .";");
																	
	my($received,$paid) = $sth->fetchrow();#$total_adj,$ida_adj,
	
	## Propocional de Ajuste se inserta en cualquier opcion?
	#($proportional_adj) and (&Do_SQL("INSERT INTO sl_movements SET ID_accounts = '$ida_adj', Amount = $proportional_adj, EffDate = CURDATE(), tableused = 'sl_purchaseorders', ID_tableused = '$id_po', Category = 'Compras', Credebit = 'Credit', Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';"));

	####### Si no se ha hecho ningun prepago o lo pagado es menor que lo recibido todo va a accounts payable
	if($paid == 0 or $paid <= $received){

		## Calculo de Impuesto
		($taxpc) and ($tax = $amt  * ($taxpc/100) );
		#$tax += $tax_adj;
		#$amt += $amt_adj;
		#($proportional_adj) and ($amt += $proportional_adj);

		my $acc_debit = 'Inventory '.$type.' Payable Debit';
		my $acc_tax = 'Inventory '.$type.' Payable Tax';
		my $acc_credit = 'Inventory '.$type.' Payable Credit';

		&general_deposits(0,$id_po,'purchaseorders',$acc_debit,"Compras",'N/A','N/A','N/A',$amt);
		&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Compras','N/A','N/A','N/A',$tax) if $tax > 0;
		## Guardamos la respuesta sobre la que ligaremos registros en sl_movements_auxiliary
		($ids_debit, $ids_credit) = &general_deposits(0,$id_po,'purchaseorders',$acc_credit,"Compras",'N/A','N/A','N/A',$amt + $tax);
		
	####### Si no se habia recibido nada hasta ahora	
	}else{
		
		#$amt += $amt_adj;
		
		if($paid - $received >= $amt){

			###
			## Si se tiene a favor prepaid y cubre por completo lo recibido todo va vs Prepaid
			###

			## Calculo de Impuesto
			($taxpc) and ($tax = $amt * ($taxpc/100) );
			#$tax += $tax_adj;
			#($proportional_adj) and ($amt += $proportional_adj);

			my $acc_debit = 'Inventory '.$type.' PrePaid Debit';
			my $acc_tax = 'Inventory '.$type.' Prepaid Tax';
			my $acc_credit = 'Inventory '.$type.' Prepaid Credit';

			&general_deposits(0,$id_po,'purchaseorders',$acc_debit,"Compras",'N/A','N/A','N/A',$amt);
			&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Compras','N/A','N/A','N/A',$tax) if $tax > 0;
			## Guardamos la respuesta sobre la que ligaremos registros en sl_movements_auxiliary
			($ids_debit, $ids_credit) = &general_deposits(0,$id_po,'purchaseorders',$acc_credit,"Compras",'N/A','N/A','N/A',$amt + $tax);
		

		}else{

			###
			## Se tiene prepaid pero no cubre por completo lo recibido, se tiene que hacer un mix entre prepaid y payable
			###

			## Paso 1, Amount + Tax sobre lo pagado
			my $amtp = $paid - $received;
			## Calculo de Impuesto
			($taxpc) and ($taxp = $amtp * ($taxpc/100) );
			$tax += $tax_adj;

			my $acc_debit = 'Inventory '.$type.' PrePaid Debit';
			my $acc_tax = 'Inventory '.$type.' Prepaid Tax';
			my $acc_credit = 'Inventory '.$type.' Prepaid Credit';

			&general_deposits(0,$id_po,'purchaseorders',$acc_debit,"Compras",'N/A','N/A','N/A',$amtp);
			&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Compras','N/A','N/A','N/A',$taxp) if $taxp > 0;
			&general_deposits(0,$id_po,'purchaseorders',$acc_credit,'Compras','N/A','N/A','N/A',$amtp + $taxp);

			## Paso 2, Amount + Tax sobre lo que se debe
			$amt = $amt - ($paid - $received);
			## Calculo de Impuesto
			($taxpc) and ($tax = $amt  * ($taxpc/100) );


			$acc_debit = 'Inventory '.$type.' Payable Debit';
			$acc_tax = 'Inventory '.$type.' Payable Tax';
			$acc_credit = 'Inventory '.$type.' Payable Credit';

			&general_deposits(0,$id_po,'purchaseorders',$acc_debit,"Compras",'N/A','N/A','N/A',$amt);
			&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Compras','N/A','N/A','N/A',$tax) if $tax > 0;
			## Guardamos la respuesta sobre la que ligaremos registros en sl_movements_auxiliary
			($ids_debit, $ids_credit) = &general_deposits(0,$id_po,'purchaseorders',$acc_credit,"Compras",'N/A','N/A','N/A',$amt + $tax);
		
		}

	}
	
	if(&table_exists('sl_movements_auxiliary') or $va{'movs_auxiliary'}){

		## Buscamos el ultimo registro del arreglo de credit
		$va{'movs_auxiliary'} = 1;
		my $this_id_movements_credit = @$ids_credit[-1];
		if($this_id_movements_credit){

			## Registramos ID_vendors, Type de cada gasto
			&Do_SQL("INSERT INTO sl_movements_auxiliary (ID_movements, FieldName, FieldValue)
				 	VALUES 
				 		(". $this_id_movements_credit .", 'sl_vendors.ID_vendors', ". $in{'id_vendors'} .")
				 		, (". $this_id_movements_credit .", 'sl_purchaseorders_items.ID_purchaseorders_items', ". $id_poi .")
				 	;");

		}

	}


	###
	## Buscamos cuenta Acreedora
	### 
	my $this_ida_vendor_credit = 0;
	my $query = "SELECT 
					ID_accounts_credit 
				FROM 
					sl_purchaseorders INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors = sl_vendors.ID_vendors 
				WHERE 
					sl_purchaseorders.ID_purchaseorders = ". $id_po .";";
	my ($sth) = &Do_SQL($query);
	$this_ida_vendor_credit = $sth->fetchrow();
	my $modupdate = $this_ida_vendor_credit ?
					" , ID_accounts = IF(Credebit = 'Credit', ". $this_ida_vendor_credit .", ID_accounts) " :
					'';

	##-------------------------------------------------
	## Se liga la contabilidad del PO con la recepción
	##-------------------------------------------------
	&Do_SQL("UPDATE 
				sl_movements 
			SET 
				Reference = 'Vendor: ". $in{'id_vendors'} ."'
				, tablerelated = 'sl_wreceipts'
				, ID_tablerelated = ". $in{'id_wreceipts'} ."
				". $modupdate ."
			 WHERE
			 	1 
			 	AND tableused = 'sl_purchaseorders' 
				AND ID_tableused = '". $id_po ."' 
				AND Category = 'Compras' 
				AND (ID_journalentries IS NULL OR ID_journalentries = 0) 
				AND ". $sqlmod_update_records ."
				AND (Reference IS NULL OR Reference = '');");
	##-------------------------------------------------

	##-------------------------------------------------
	## Se liga la contabilidad del PO con la recepción
	##-------------------------------------------------
	# &Do_SQL("UPDATE sl_movements SET Reference = 'Vendor: $in{'id_vendors'}', tablerelated = 'sl_wreceipts', ID_tablerelated = '$in{'id_wreceipts'}' 
	# 		 WHERE tableused = 'sl_purchaseorders' 
	# 			AND ID_tableused = '$id_po' 
	# 			AND Category = 'Compras' 
	# 			AND (ID_journalentries IS NULL OR ID_journalentries = 0) 
	# 			AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 15
	# 			AND (Reference IS NULL OR Reference = '');");
	##-------------------------------------------------

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_wreceipt_noninventory_in
#
#       Es: Recibe la mercancia de un PO No Inventariable
#       En: 
#
#
#    Created on: 07/09/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos (id_po, $id_products, $qty, $cost)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_wreceipt_noninventory_in {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	### Datos recibidos en funcion
	my $id_po = int($param_data[0]);
	my $id_poi = int($param_data[1]);
	my $id_products = int($param_data[2]);	
	my $ida_debit = int($param_data[3]);
	my $amount = &filter_values($param_data[4]);
	my $tax = &filter_values($param_data[5]);
	### Datos recibidos por configuracion
	#my $exchange_rate = &filter_values($param_data[5]); ## This is the exchange rate value,if it's not eq 1 then it's international
	my $category = int($param_data[6]);
	my $type = $category == 2 ? 'Foreign' : 'Local';

	####################
	####################
	####### 1) Aplicamos el pago de acuerdo a los datos
	####################
	####################
	my $acc_credit = 'Non Inventoy Wreceipt '.$type;
	my $acc_tax = 'Non Inventoy Wreceipt Tax '.$type;

	&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($ida_debit,'".$amount."', '', CURDATE(), 'sl_purchaseorders', $id_po, 'Compras', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	&general_deposits(0,$id_po,'purchaseorders',$acc_tax,'Compras','N/A','N/A','N/A',$tax) if $tax > 0;
	&general_deposits(0,$id_po,'purchaseorders',$acc_credit,"Compras",'N/A','N/A','N/A',$amount + $tax);
	
	&accounting_group_amounts('sl_purchaseorders', $id_po);

	return;

}


#############################################################################
#############################################################################
#   Function: accounting_wreceipt_adjustment_inventory_in
#
#       Es: Genera movimientos de ajustes como entrada de inventario ya que el costo se eligio ser parte deCOGS
#       En: 
#
#
#    Created on: 2013/06/05
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#        - Modified on 18-02-2015 by ISC Alejandro Diaz : Se agrega ID_wreceipts a sl_movements
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
sub accounting_wreceipt_adjustments_inventory_in {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $idpo_adj = int($param_data[0]);
	my $idpo = int($param_data[1]);
	my $id_vendors = int($param_data[2]);
	my $id_wreceipts = int($param_data[3]);
	my $adj_type = &filter_values($param_data[4]);
	my $amt = &filter_values($param_data[5]);
	my $tax = &filter_values($param_data[6]);
	my $exchange_rate = &filter_values($param_data[7]); ## This is the exchange rate value,if it's not eq 1 then it's international
	my $this_id_accounts = int($param_data[8]);
	my $in_cogs = int($param_data[9]);
	### Datos recibidos por configuracion
	my $category = int($param_data[10]);
	my $ida_tax_specific = int($param_data[11]); ## Genera contabilidad diferente
	my $ida_tax_ret = &filter_values($param_data[12]); ##Cuentas de IVA con retención(cuenta:porcentaje)

	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);
	
	$ida_tax_specific = 0 if(!$ida_tax_specific);
	my $type = $category == 2 ? 'Foreign' : 'Local';

	## How to update
	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';	
	my $sqlmod_update_records = ($md5time_field_exists and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;
	
	########
	######## To Default currency
	########
	my $this_amt = $amt * $exchange_rate;
	$tax *= $exchange_rate;

	###----------------------------
	### Retencion 4%
	###----------------------------	
	my $tax_ret = 0;
	my $amt_ret = 0;
	my @ary_tax_ret = split(/,/, $ida_tax_ret);
	for(0..$#ary_tax_ret){
		my ($ida_retx, $tax_retx) = split(/:/, $ary_tax_ret[$_]);		
		if( $ida_retx eq $this_id_accounts ){
			$tax_ret = $tax_retx;
			last;
		}
	}	
	if( $tax_ret > 0 ){
		$amt_ret = $amt *($tax_ret / 100);
		$amt_ret *= $exchange_rate;
		$tax -=	$amt_ret;
	}
	###----------------------------

	$acc_debit = 'Inventory Adjustments '.$type.' Payable Debit';
	$acc_tax = 'Inventory Adjustments '.$type.' Payable Tax';
	$acc_credit = 'Inventory Adjustments '.$type.' Payable Credit';
	$acc_ret_tax = 'Inventory Adjustments '.$type.' Retention Tax';
	
	if( !$in_cogs ){
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
				 VALUES (". $this_id_accounts .",'".$this_amt."', '', CURDATE(), 'sl_purchaseorders', $idpo, 'Compras', 'Debit',". $md5time_value ." 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	}else{
		&general_deposits(0,$idpo,'purchaseorders',$acc_debit,"Compras",'N/A','N/A','N/A',$this_amt);		
	}	
	&general_deposits(0,$idpo,'purchaseorders',$acc_tax,'Compras','N/A','N/A','N/A',$tax) if $tax > 0;
	my ($ids_ret_debit, $ids_ret_credit) = &general_deposits(0,$idpo,'purchaseorders',$acc_ret_tax,'Compras','N/A','N/A','N/A',$amt_ret) if $amt_ret > 0;
	my $this_ida_retx = @$ids_ret_credit[0] ? @$ids_ret_credit[0] : 0;
	## Guardamos la respuesta sobre la que ligaremos registros en sl_movements_auxiliary
	my ($ids_debit, $ids_credit) = &general_deposits(0,$idpo,'purchaseorders',$acc_credit,"Compras",'N/A','N/A','N/A',$this_amt + $tax);

	#&cgierr(scalar @$ids_credit);
	if(&table_exists('sl_movements_auxiliary') or $va{'movs_auxiliary'}){

		## Buscamos el ultimo registro del arreglo de credit
		$va{'movs_auxiliary'} = 1;
		my $this_id_movements_credit = @$ids_credit[-1];
		if($this_id_movements_credit){

			## Registramos ID_vendors, Type de cada gasto
			&Do_SQL("INSERT INTO sl_movements_auxiliary (ID_movements, FieldName, FieldValue)
				 	VALUES 
				 		(". $this_id_movements_credit .", 'sl_vendors.ID_vendors', ". $id_vendors .")
				 		, (". $this_id_movements_credit .", 'sl_purchaseorders_adj.ID_purchaseorders_adj', ". $idpo_adj .")
				 		, (". $this_id_movements_credit .", 'Type', '". &filter_values($adj_type) ."')
				 	;");

		}

	}

	###
	## Buscamos cuenta Acreedora
	### 
	my $this_ida_vendor_credit = 0;
	my $query = "SELECT 
					ID_accounts_credit 
				FROM 
					sl_vendors 
				WHERE 
					sl_vendors.ID_vendors = ". $id_vendors .";";
	my ($sth) = &Do_SQL($query);
	$this_ida_vendor_credit = $sth->fetchrow();
	my $modupdate = $this_ida_vendor_credit ?
					" , ID_accounts = IF(Credebit = 'Credit' AND ". $this_ida_retx ." = 0, ". $this_ida_vendor_credit .", ID_accounts)    " :
					'';

	#&Do_SQL("UPDATE sl_movements SET Reference = 'Vendor: $id_vendors', tablerelated = 'sl_wreceipts', ID_tablerelated = '$id_wreceipts' WHERE tableused = 'sl_purchaseorders' AND ID_tableused = '$idpo' AND Category = 'Compras' AND (ID_journalentries IS NULL OR ID_journalentries = 0) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50;");
	&Do_SQL("UPDATE 
				sl_movements
			SET 
				Reference = 'Vendor GA: ". $id_vendors ."|ID:".$idpo_adj."'
				, tablerelated = 'sl_wreceipts'
				, ID_tablerelated = ". $id_wreceipts ."
				". $modupdate ."
			 WHERE tableused = 'sl_purchaseorders' 
				AND ID_tableused = ". $idpo ." 
				AND Category = 'Compras' 
				AND (ID_journalentries IS NULL OR ID_journalentries = 0) 
				AND ". $sqlmod_update_records ."
				AND (Reference IS NULL OR Reference = '');");
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
sub accounting_adjustment {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $id_adjustments = int($param_data[0]);
	my $adjustment = $param_data[1];
	my $amt = $param_data[2];
	my $ida_deductible = &filter_values($param_data[3]);
	
	($adjustment < 0) ?
		#### Si el inventario en sistema era mayor que el real, se hace entrada Inventory Adjustment(201) vs  Inventory Assets(89)
		#&general_deposits(0,$id_adjustments,'adjustments','Negative Adj','Gastos','N/A','N/A','N/A',$amt) :
		&general_deposits(0,$id_adjustments,'adjustments','Negative Adj','Inventario','N/A','N/A','N/A',$amt) :
		#### Si el inventario en sistema era menor que el real, se hace entrada Inventory Assets(89) vs Inventory Adjustment(201)
		#&general_deposits(0,$id_adjustments,'adjustments','Positive Adj','Cobranza','N/A','N/A','N/A',$amt);
		&general_deposits(0,$id_adjustments,'adjustments','Positive Adj','Inventario','N/A','N/A','N/A',$amt);

	if($ida_deductible) {
		## Deductible
		my ($sth) = &Do_SQL("UPDATE sl_movements SET Reference = 'Deductible' WHERE ID_tableused = '$id_adjustments' AND ID_accounts IN($ida_deductible);");
	}

	return;	
}


#############################################################################
#############################################################################
#   Function: accounting_return_to_vendor
#
#       Es: Genera los Movimientos contables cuando se devuelve mercancia al proveedor
#       En: 
#
#
#	 Created on *2014/12/10* : Se agrega funcion que sera el paso1. Solo aplicara la salida de la mercancia vs la cuenta puente.En paso 2 se aplicara vs el saldo en una factura
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#		 - Modified on *2014/08/22* by _Roberto Barcenas_ : Se agrega el id_po original como campos related y se corrige el problema de IVA
#
#   Parameters:
#
#      - @param_data: Arreglo con datos (ID_po, Cost, Tax,ID_accounts for Vendor, ID_accounts tax payable, ID_accounts tax paid)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#		<accounting_po_apply_credit>
#
#
#
#  ToDO: #1 Se agrega la toma de cuenta deudora del proveedor. Se comenta mientras hay aprobacion
#  ToDO: #2 Se descomenta para pruebas en pp, con finalidad de pasar a produccion
#
sub accounting_return_to_vendor {
#############################################################################
#############################################################################

	my (@param_data) = @_;
	## Pasados por funcion que la llama
	my $id_po = int($param_data[0]);
	my $id_po_rvendor = int($param_data[1]);
	my $cost = &round($param_data[2],3);
	my $tax = &round($param_data[3],3);
	my $currency_exchange = &round($param_data[4],4);
	## Pasados por parametros DB
	my $category = int($param_data[5]);
	my $ida_rvendor = int($param_data[6]);

	my $str_params = join('::', @param_data);
	#&cgierr($str_params);

	###
	### 1) Monto basado en tipo de cambio
	###
	$cost = round($cost * $currency_exchange,2);
	$tax = round($tax * $currency_exchange,2);

	my $type = $category == 2 ? 'Foreign' : 'Local';
	my $amount = round($cost + $tax,2);

	###
	### 2) Aplicacion de Cuenta Temporal + Tax . Nota. Siempre aplicamos al tax por pagar debido a que en CxP siempre se aplicara el Credito a una factura por pagar..
	###
	&general_deposits(0,$id_po_rvendor,'purchaseorders','Return to Vendor Taxes Payable ' . $type,'Compras','N/A','N/A','N/A',$tax) if $tax;
	&general_deposits(0,$id_po_rvendor,'purchaseorders','Return to Vendor S1 ' . $type,'Compras','N/A','N/A','N/A',$cost);
	
	### Sum Tax to Debit Amount
	&Do_SQL("UPDATE sl_movements SET Amount = Amount + $tax WHERE ID_tableused = '$id_po_rvendor' AND tableused = 'sl_purchaseorders' AND Credebit = 'Debit' AND Amount = '$cost' AND Status = 'Active' ORDER BY ID_movements DESC LIMIT 1;") if $tax;	

	###
	### 3) Buscamos cuenta Abono Original
	###
	my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = ". $id_po ." AND tableused = 'sl_purchaseorders' AND Category = 'Compras' AND Credebit = 'Credit' ORDER BY ID_movements LIMIT 1;");
	my ($this_ida_debit) = $sth->fetchrow();

	###
	## 4) Buscamos cuenta Acreedora en Proveedor
	### 
	my $query = "SELECT 
					ID_accounts_credit 
				FROM 
					sl_purchaseorders INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors = sl_vendors.ID_vendors 
				WHERE 
					sl_purchaseorders.ID_purchaseorders = ". $id_po .";";
	my ($sth) = &Do_SQL($query);
	my ($this_ida_vendor_credit) = $sth->fetchrow();
	$this_ida_debit = $this_ida_vendor_credit if $this_ida_vendor_credit;

	if($this_ida_debit){

		## 3.1. Actualizacion cuenta Cargo
		&Do_SQL("UPDATE sl_movements SET ID_accounts = ". $this_ida_debit ." WHERE ID_tableused = '$id_po_rvendor' AND tableused = 'sl_purchaseorders' AND Credebit = 'Debit' AND ABS( Amount - ". ($cost + $tax) .") < 1 AND Status = 'Active' ORDER BY ID_movements DESC LIMIT 1;");

	}

	return;

}


#############################################################################
#############################################################################
#   Function: accounting_wreceipt_services_in
#
#       Es: Genera la contabilidad para POs de Servicios en el proceso de la recepcion
#       En: 
#
#
#    Created on: 09/01/2017
#
#    Author: ISC Gilberto QC
#
#    Modifications:
#
#        - Modified on ** by 
#
#   Parameters:
#
#      - @param_data: 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_wreceipt_services_in {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	### Datos recibidos en funcion
	my $id_po = int($param_data[0]);
	my $id_poi = int($param_data[1]);
	my $id_wr = int($param_data[2]);
	my $deductible = &filter_values($param_data[3]);
	my $invoice_in = int($param_data[4]);
	### Datos pasados por config. del keypoint
	my $ida_debit_tax = int($param_data[5]);
	my $ida_prov_vendor = int($param_data[6]);
	
	my $category = 'Gastos';

	my $sth = &Do_SQL("SELECT ID_accounts_credit 
						FROM sl_vendors 
							INNER JOIN sl_purchaseorders ON sl_vendors.ID_vendors = sl_purchaseorders.ID_vendors
						WHERE ID_purchaseorders = ".int($id_po).";");
	my $ida_credit = $sth->fetchrow();
	### Se sustituye la cuenta de proveedores por la de provision(cuando no se cuenta con la factura)
	$ida_credit = $ida_prov_vendor if( $invoice_in != 1 );

	my $sth = &Do_SQL("SELECT sl_purchaseorders_items.ID_products
							, sl_purchaseorders_items.Price
							, sl_purchaseorders_items.Tax
							, sl_purchaseorders_items.Qty
							, sl_purchaseorders_items.Tax_percent
							, sl_services.PurchaseID_accounts
							, sl_purchaseorders_items.ID_segments
						FROM sl_services
							INNER JOIN sl_purchaseorders_items ON sl_services.ID_services = RIGHT(sl_purchaseorders_items.ID_products, 4)							
						WHERE sl_purchaseorders_items.ID_purchaseorders = ".int($id_po)." 
							AND sl_purchaseorders_items.ID_purchaseorders_items = ".int($id_poi).";");
	my $po_item = $sth->fetchrow_hashref();	
	my $id_services = substr($po_item->{'ID_products'}, -4);
	my $price = $po_item->{'Price'};
	my $tax = $po_item->{'Tax'};
	my $qty = $po_item->{'Qty'};
	my $ida_debit = $po_item->{'PurchaseID_accounts'};
	my $id_segments = $po_item->{'ID_segments'};

	my $amount = round($price * $qty, 2);
	my $tax_pct = $po_item->{'Tax_percent'};
	my $tax_amt = round($amount * $tax_pct, 2);

	###
	### Cálculo de retenciones
	###
	my $pct_ret_debit = 0;
	my $pct_ret_credit = 0;
	my $amt_extra_credit = 0;
	my @querys_ret;
	my $sth_ret = &Do_SQL("SELECT Code AS id_accounts
								, Subcode AS percent
								, Largecode AS credebit
								, Description AS extra_account
							FROM sl_vars_config
							WHERE Command = 'service_account_retention' 
								AND IDValue = ".int($id_services).";");
	my $i = 0;
	while( my $rec = $sth_ret->fetchrow_hashref() ){
				
		my $this_id_accounts = $rec->{'id_accounts'};
		my $this_percent = (!$rec->{'percent'}) ? 0 : round(($rec->{'percent'} / 100), 4);
		my $this_amount = ($this_percent > 0) ? round(($this_percent * $amount), 2) : 0;
		my $this_credebit = $rec->{'credebit'};
		my $this_id_segments = 0;


		if( $rec->{'credebit'} eq 'debit' ){
			if( $rec->{'extra_account'} eq 'no' ){
				$pct_ret_debit += $this_percent;
			}
			$this_id_segments = $id_segments;
		} else {
			if( $rec->{'extra_account'} eq 'no' ){
				$pct_ret_credit += $this_percent;
			} else {
				$amt_extra_credit += $this_amount;
			}
		}

		### Se genera el query para ejecutarlos posteriormente
		$querys_ret[$i] = "INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
			 				VALUES (".$this_id_accounts.",'".$this_amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_wreceipts', ".$id_wr.", '".$category."', '".$this_credebit."', ".int($this_id_segments).", 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");";
		$i++;
	}
	### Se recalcula el IVA
	if( $pct_ret_debit > 0 ){
		if( $tax_pct >= $pct_ret_debit ){
			my $new_tax_pct = $tax_pct - $pct_ret_debit;
			$tax_amt = round($amount * $new_tax_pct, 2);
		} else {
			$tax_amt = 0;
		}
	}

	### Debits
	my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
						VALUES (".$ida_debit.",'".$amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_wreceipts', ".$id_wr.", '".$category."', 'Debit', ".int($id_segments).", 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	my $id_movs = $sth->{'mysql_insertid'};
	&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'ID_wreceipts', FieldValue='".$id_wr."';");
	&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'Deductible', FieldValue='Yes';") if( $deductible eq 'Yes' );

	if( $tax_amt > 0 ){
		my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
				 			VALUES (".$ida_debit_tax.",'".$tax_amt."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_wreceipts', ".$id_wr.", '".$category."', 'Debit', ".int($id_segments).", 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");
		my $id_movs = $sth->{'mysql_insertid'};
		&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'ID_wreceipts', FieldValue='".$id_wr."';");
		&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'Deductible', FieldValue='Yes';") if( $deductible eq 'Yes' );
	}

	### Se ejecutan los querys obtenidos en el proceso de retención
	foreach my $i (0 .. $#querys_ret){
		if( length($querys_ret[$i]) > 0 ){
			my $sth = &Do_SQL($querys_ret[$i]);
			my $id_movs = $sth->{'mysql_insertid'};
			&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'ID_wreceipts', FieldValue='".$id_wr."';");
			&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'Deductible', FieldValue='Yes';") if( $deductible eq 'Yes' );
		}
	}

	### Credits
	my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, Status, Date, Time, ID_admin_users)
			 			VALUES (".$ida_credit.",'".(($amount - $amt_extra_credit) + $tax_amt)."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_wreceipts', ".$id_wr.", '".$category."', 'Credit','Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	my $id_movs = $sth->{'mysql_insertid'};
	&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'ID_wreceipts', FieldValue='".$id_wr."';");
	&Do_SQL("INSERT INTO sl_movements_auxiliary SET ID_movements = '".$id_movs."', FieldName = 'Deductible', FieldValue='Yes';") if( $deductible eq 'Yes' );
	
	
	return;

}

#############################################################################
#############################################################################
#   Function: accounting_po_services_auth
#
#       Es: Genera la contabilidad para POs de Servicios en el proceso de autorizacion
#       En: 
#
#
#    Created on: 16/03/2017
#
#    Author: ISC Gilberto QC
#
#    Modifications:
#
#        - Modified on ** by 
#
#   Parameters:
#
#      - @param_data: 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_po_services_auth {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	### Datos recibidos en funcion
	my $id_po = int($param_data[0]);	
	### Datos pasados por config. del keypoint
	my $ida_debit = int($param_data[1]);
	my $ida_credit = int($param_data[2]);

	my $category = 'Cuentas de Orden';

	### Se obtiene el monto de la provisión
	my $sth = &Do_SQL("SELECT SUM(sl_purchaseorders_items.Price * sl_purchaseorders_items.Qty) TotalNet
							, SUM(sl_purchaseorders_items.Tax) TotalTax
							, SUM(sl_purchaseorders_items.Qty) TotalQty	
						FROM sl_purchaseorders_items 
						WHERE sl_purchaseorders_items.ID_purchaseorders = ".int($id_po).";");
	my $po_item = $sth->fetchrow_hashref();	
	my $amount = round($po_item->{'TotalNet'}, 2);

	### Revisa si ya existe contabilidad de una autorización previa
	my $sth_movs = &Do_SQL("SELECT SUM(Amount)
							FROM sl_movements
							WHERE tableused = 'sl_purchaseorders' 
								AND ID_tableused = ".$id_po." 
								AND Category = 'Cuentas de Orden' 
								AND `Status` = 'Active' 
								AND ID_accounts = ".$ida_debit." 
								AND Credebit = 'Debit';");
	my $amt_debit = $sth_movs->fetchrow();
	$amt_debit = 0 if( !$amt_debit );
	my $diff_amt_movs = 0;
	if( $amt_debit > 0 ){
		$diff_amt_movs = ($amount - $amt_debit);
	}

	### Si ya existe contabilidad previa de provisiones
	if( $diff_amt_movs > 0 ){

		$amount = $diff_amt_movs;

	}elsif( $diff_amt_movs < 0 ){

		my $ida_debit_aux = $ida_debit;
		$ida_debit = $ida_credit;
		$ida_credit = $ida_debit_aux;

		$amount = abs($diff_amt_movs);

	}
	
	### Debits
	my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
						VALUES (".$ida_debit.",'".$amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", NULL, 0, '".$category."', 'Debit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	### Credits
	my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
						VALUES (".$ida_credit.",'".$amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", NULL, 0, '".$category."', 'Credit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	
	
	return;

}

#############################################################################
#############################################################################
#   Function: accounting_po_services_cancell_prov
#
#       Es: Cancela la contabilidad de provisiones para POs de Servicios
#       En: 
#
#
#    Created on: 17/03/2017
#
#    Author: ISC Gilberto QC
#
#    Modifications:
#
#        - Modified on ** by 
#
#   Parameters:
#
#      - @param_data: 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_po_services_cancell_prov {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	### Datos recibidos en funcion
	my $id_po = int($param_data[0]);
	my $id_wr = int($param_data[1]);
	### Datos pasados por config. del keypoint
	my $ida_debit = &filter_values($param_data[2]);
	my $ida_credit = &filter_values($param_data[3]);
	### Parámetros por defecto
	my $category = 'Cuentas de Orden';
	
	### Se cancela la contabilidad de provisiones
	# my $sth = &Do_SQL("SELECT sl_movements.ID_accounts, sl_movements.Credebit, sl_movements.Amount, sl_movements.Category
	# 					FROM sl_movements
	# 					WHERE sl_movements.tableused = 'sl_purchaseorders' 
	# 						AND sl_movements.ID_tableused = ".int($id_po)." 
	# 						AND sl_movements.`Status` = 'Active'
	# 						AND sl_movements.ID_accounts In(".$ida_debit.",".$ida_credit.");");
	# while( my $rec = $sth->fetchrow_hashref() ){

	# 	if( ($rec->{'ID_accounts'} == $ida_debit and $rec->{'Credebit'} eq 'Debit') or ($rec->{'ID_accounts'} == $ida_credit and $rec->{'Credebit'} eq 'Credit') ){
	# 		my $id_accounts = $rec->{'ID_accounts'};
	# 		my $amount = $rec->{'Amount'};
	# 		my $category = $rec->{'Category'};
	# 		my $credebit = ($rec->{'Credebit'} eq 'Debit') ? 'Credit' : 'Debit';

	# 		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
	# 				 VALUES (".$id_accounts.",'".$amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", NULL, 0, '".$category."', '".$credebit."', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	# 	}
		
	# }
	my $sth = &Do_SQL("SELECT SUM(sl_purchaseorders_items.Price * sl_purchaseorders_items.Qty) TotalNet
							, SUM(sl_purchaseorders_items.Tax) TotalTax
							, SUM(sl_purchaseorders_items.Qty) TotalQty	
						FROM sl_purchaseorders_items 
						WHERE sl_purchaseorders_items.ID_purchaseorders = ".int($id_po).";");
	my $po_item = $sth->fetchrow_hashref();	
	my $amount = round($po_item->{'TotalNet'}, 2);
	
	### Debits
	my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
						VALUES (".$ida_debit.",'".$amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", NULL, 0, '".$category."', 'Credit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	### Credits
	my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
						VALUES (".$ida_credit.",'".$amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", NULL, 0, '".$category."', 'Debit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	
	
	return;

}

#############################################################################
#############################################################################
#   Function: accounting_po_services_topay
#
#       Es: Genera la contabilidad para los casos en que haya variacion entre el monto del PO
#			original y la factura cargada en los PO de Servicios
#       En: 
#
#
#    Created on: 21/03/2017
#
#    Author: ISC Gilberto QC
#
#    Modifications:
#
#        - Modified on ** by 
#
#   Parameters:
#
#      - @param_data: 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_po_services_topay {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	### Datos recibidos en funcion
	my $id_po = int($param_data[0]);
	my $id_bill = int($param_data[1]);
	my $amount = &filter_values($param_data[2]);
	my $tax_pct = &filter_values($param_data[3]);
	my $id_services = int($param_data[4]); 
	my $ida_services = int($param_data[5]); 
	my $ida_vendors = int($param_data[6]); #Proveedores Nacionales
	my $diff_amt = &filter_values($param_data[7]);
	my $diff_type = &filter_values($param_data[8]); 
	### Datos pasados por config. del keypoint
	my $ida_prov_vendor = &filter_values($param_data[9]); #Provisión(cancelar)
	my $ida_tax = &filter_values($param_data[10]); #Provisión(cancelar)
	### Parámetros por defecto
	my $category = 'Gastos';
	my $reference = 'PO Services - Cancell Provision';

	my $sth = &Do_SQL("SELECT COUNT(*) exists_prov
						FROM sl_movements
						WHERE sl_movements.tableused = 'sl_purchaseorders' 
							AND sl_movements.ID_tableused = ".int($id_po)." 
							AND sl_movements.`Status` = 'Active'
							AND sl_movements.Category = '".$category."'
							AND sl_movements.ID_accounts In(".$ida_prov_vendor.")
							AND sl_movements.Credebit = 'Credit';");
	my $exists_prov = $sth->fetchrow();
	### Si existe contabilidad de provisiones, entonces la cancela
	if( int($exists_prov) > 0 ){
		### Cancela la contabilidad de provisiones
		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
				 VALUES (".$ida_prov_vendor.",'".$amount."', '".$reference."', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', 'Debit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	

		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
				 VALUES (".$ida_vendors.",'".$amount."', '".$reference."', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', 'Credit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");	
	}

	### Genera la contabilidad por la posible diferencia
	if( $diff_amt > 0 and $diff_type ne '' ){
		my $this_tax_pct = ($tax_pct > 1) ? round($tax_pct / 100, 4) : $tax_pct;
		my $net_amt = round($diff_amt / (1 + $this_tax_pct), 3);
		my $tax_amt = $diff_amt - $net_amt;

		my $credebit = $diff_type;
		if( $diff_type eq 'Debit' ){
			&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
					 VALUES (".$ida_vendors.",'".$diff_amt."', '".$reference."', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', 'Credit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");
		} else {
			&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
					 VALUES (".$ida_vendors.",'".$diff_amt."', '".$reference."', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', 'Debit', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");
		}

		####---------------------------------------------------------------------------
		### Cálculo de retenciones
		####---------------------------------------------------------------------------
		my $sth_ret_count = &Do_SQL("SELECT COUNT(*) ret_exits
									FROM sl_vars_config
									WHERE Command = 'service_account_retention' 
										AND IDValue = ".int($id_services)."
										AND LOWER(Largecode) = 'credit';");
		my $ret_exits = $sth_ret_count->fetchrow();
	
		if( int($ret_exits) == 2 ){
			$net_amt = round($diff_amt * &filter_values($cfg{'factor_ret_pmt'}), 3) if($cfg{'factor_ret_pmt'});
		} elsif( int($ret_exits) == 1 ){
			$net_amt = round($diff_amt * &filter_values($cfg{'factor_ret_fght'}), 3) if($cfg{'factor_ret_fght'});				
		}

		### Segmento del servicio
		$item_seg = &Do_SQL("SELECT ID_segments FROM sl_purchaseorders_items WHERE ID_purchaseorders = ".$id_po." AND ID_products = 60000".$id_services." LIMIT 1;");
		my $id_segments = $item_seg->fetchrow();

		my $pct_ret_debit = 0;
		my $pct_ret_credit = 0;
		my $amt_extra_credit = 0;
		my @querys_ret;

		my $sth_ret = &Do_SQL("SELECT Code AS id_accounts
									, Subcode AS percent
									, Largecode AS credebit
									, Description AS extra_account
								FROM sl_vars_config
								WHERE Command = 'service_account_retention' 
									AND IDValue = ".int($id_services).";");
		my $i = 0;
		while( my $rec = $sth_ret->fetchrow_hashref() ){
					
			my $this_id_accounts = $rec->{'id_accounts'};
			my $this_percent = (!$rec->{'percent'}) ? 0 : round(($rec->{'percent'} / 100), 4);
			my $this_amount = ($this_percent > 0) ? round(($this_percent * $net_amt), 3) : 0;
			my $this_credebit = $rec->{'credebit'};
			my $this_id_segments = 0;

			if( $rec->{'credebit'} eq 'debit' ){
				if( $rec->{'extra_account'} eq 'no' ){
					$pct_ret_debit += $this_percent;
				}
				$this_id_segments = $id_segments;
			} else {
				if( $rec->{'extra_account'} eq 'no' ){
					$pct_ret_credit += $this_percent;
				} else {
					$amt_extra_credit += $this_amount;
				}
			}
			if( $diff_type eq 'Credit' ){
				$this_credebit = ($this_credebit eq 'debit') ? 'Credit' : 'Debit';
			}

			### Se genera el query para ejecutarlos posteriormente
			$querys_ret[$i] = "INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
				 				VALUES (".$this_id_accounts.",'".$this_amount."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', '".$this_credebit."', ".int($this_id_segments).", 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");";
			$i++;
		}
		### Se recalcula el IVA
		my $new_tax_pct = $tax_pct;
		if( $pct_ret_debit > 0 ){
			if( $tax_pct >= $pct_ret_debit ){
				$new_tax_pct = $tax_pct - $pct_ret_debit;
				$tax_amt = round($net_amt * $new_tax_pct, 3);
			} else {
				$tax_amt = 0;
			}
		}

		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
				 VALUES (".$ida_services.",'".$net_amt."', '".$reference."', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', '".$diff_type."', 0, 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");

		if( $tax_amt > 0 ){
			my $sth = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users)
					 			VALUES (".$ida_tax.",'".$tax_amt."', '', CURDATE(), 'sl_purchaseorders', ".$id_po.", 'sl_bills', ".$id_bill.", '".$category."', '".$credebit."', ".int($id_segments).", 'Active', CURDATE(), CURTIME(), ".int($usr{'id_admin_users'}).");");
		}

		### Se ejecutan los querys obtenidos en el proceso de retención
		foreach my $i (0 .. $#querys_ret){
			if( length($querys_ret[$i]) > 0 ){
				my $sth = &Do_SQL($querys_ret[$i]);
			}
		}

	}
	
	return;

}

#############################################################################
#############################################################################
#   Function: accounting_po_apply_credit
#
#       Es: Genera los Movimientos contables cuando se aplica un Bill tipo Credit para el pago de un PO
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#		 - Modified on *2014/08/22* by _Roberto Barcenas_ : Se agrega el id_po original como campos related y se corrige el problema de IVA
#		 - Modified on *2014/12/10* by _Roberto Barcenas_ : Se agrega el ida_rvendor, que es la cuenta puente generada en el paso 1.
#
#   Parameters:
#
#      - @param_data: Arreglo con datos (ID_po, Cost, Tax,ID_accounts for Vendor, ID_accounts tax payable, ID_accounts tax paid)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   
#   		<accounting_return_to_vendor>
#
#
sub accounting_po_apply_credit {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	## Pasados via parametros en la funcion que lo manda llamar
	my $id_po = int($param_data[0]);
	my $id_bills = int($param_data[1]);
	my $ida_banks = int($param_data[2]);
	my $amount = &filter_values($param_data[3]);
	my $exchange_rate = &filter_values($param_data[4]);
	## Pasados por parametros DB
	my $ida_vendor = &filter_values($param_data[5]);
	my $ida_tax_payable = &filter_values($param_data[6]);
	my $ida_tax_paid = &filter_values($param_data[7]);
	my $category = int($param_data[8]);
	my $ida_rvendor = int($param_data[9]);
	my $ida_profit = int($param_data[10]);
	my $ida_lost = int($param_data[11]);
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);

	my $str_params = join('::', @param_data);
	#&cgierr($str_params);

	if($amount > 0){


		my $type = $category == 2 ? 'Foreign' : 'Local';

		#######
		####### Currency Exchange (Convert to Default Currency)
		#######
		my $amount_original = $amount;
		$amount *= $exchange_rate;

		####################
		####################
		####### 1) Aplicamos Credito
		####################
		####################
		&general_deposits(0,$id_po,'purchaseorders','Purchase Order Apply Credit ' . $type,'Compras','N/A','N/A','N/A',$amount);

		####################
		####################
		####### 2) Fluctuacion cambiaria
		####################
		####################
		my @params = ($id_po, $id_bills, $amount_original, $amount_tax, $exchange_rate, $this_ida_vendor, $ida_tax_payable, $ida_tax_paid, $ida_profit, $ida_lost);
		&bills_po_exchange_profit_lost(@params);

		####################
		####################
		####### 3) Aplicamos Related Table
		####################
		####################
		if($id_bills){
			&Do_SQL("UPDATE sl_movements SET ID_journalentries = 0,tablerelated = 'sl_bills', ID_tablerelated = '$id_bills' WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND (ID_tablerelated = 0 OR ID_tablerelated IS NULL) AND TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 30 AND ID_admin_users = '$usr{'id_admin_users'}';");
		}

		############
		############ Check for Paid Bill
		############
		my @params = ($id_po, $ida_vendor, $ida_profit, $ida_lost);
		&bills_po_check_paid(@params);

		&accounting_group_amounts('sl_purchaseorders', $id_po);

	}

	return;
}


#############################################################################
#############################################################################
#   Function: _old_accounting_po_apply_credit
#
#       Es: Genera los Movimientos contables cuando se aplica un Bill tipo Credit para el pago de un PO
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#		 - Modified on *2014/08/22* by _Roberto Barcenas_ : Se agrega el id_po original como campos related y se corrige el problema de IVA
#		 - Modified on *2014/12/10* by _Roberto Barcenas_ : Se agrega el ida_rvendor, que es la cuenta puente generada en el paso 1.
#
#   Parameters:
#
#      - @param_data: Arreglo con datos (ID_po, Cost, Tax,ID_accounts for Vendor, ID_accounts tax payable, ID_accounts tax paid)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   
#   		<accounting_return_to_vendor>
#
#
sub _old_accounting_po_apply_credit {
#############################################################################
#############################################################################

	# NOTA: Esta funcion esta en desuso, confirmar despues de puesta en produccion de la aplicacion del credito por la devolucion al proveedor
	
	return;

	my (@param_data) = @_;

	## Pasados via pargrametros en la funcion que lo manda llamar
	my $id_po = int($param_data[0]);
	my $id_bills = int($param_data[1]);
	my $ida_banks = int($param_data[2]);
	my $amount = &filter_values($param_data[3]);
	my $exchange_rate = &filter_values($param_data[4]);
	## Pasados por parametros DB
	my $ida_vendor = &filter_values($param_data[5]);
	my $ida_tax_payable = &filter_values($param_data[6]);
	my $ida_tax_paid = &filter_values($param_data[7]);
	my $category = int($param_data[8]);
	my $ida_rvendor = int($param_data[9]);
	my $ida_profit = int($param_data[10]);
	my $ida_lost = int($param_data[11]);

	my $str_params = join('::', @param_data);
	#&cgierr($str_params);

	my $type = $category == 2 ? 'Foreign' : 'Local';

	my $id_vendors = &load_name('sl_purchaseorders','ID_purchaseorders',$id_po,'ID_vendors');
	my $returned = $cost + $tax;
	my $type = $category == 1 ? 'Local' : 'Foreign';

	my ($sth) = &Do_SQL("/*Returned = $cost + $tax */ 
					SELECT 
					SUM(IF(Credebit='Debit',Amount,0)) AS Debits,
					SUM(IF(Credebit='Credit',Amount,0)) AS Credits
					FROM `sl_movements`
					WHERE ID_tableused = '$id_po'
					AND `ID_accounts`IN ( $ida_vendor )
					AND `tableused` = 'sl_purchaseorders'
					AND sl_movements.Status != 'Inactive'
					GROUP BY ID_tableused;");
	my ($debits,$credits) = $sth->fetchrow();
	

	if($credits - $debits >= $returned){

		#################
		#################
		#### 1) Inventory Payable All 
		#################
		#################
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Payable ' . $type,'Compras','N/A','N/A','N/A',$cost);
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Taxes Payable ' . $type,'Compras','N/A','N/A','N/A',$tax) if $tax;
		### Sum Tax to Debit Amount
		&Do_SQL("UPDATE sl_movements SET Amount = Amount + $tax WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND Credebit = 'Debit' AND Amount = '$cost' ORDER BY ID_movements DESC LIMIT 1;") if $tax;

	}elsif($credits > $debits){

		#################
		#################
		#### 2) Inventory Payable + Inventory Paid
		#################
		#################
		my ($tax_payable,$tax_paid);
		my $to_return = $credits-$debits;
		my $pct = round($to_return * 100 / $returned,2);

		### Payable Data
		my $cost_payable = round($cost * $pct,2);
		$tax_payable = round($tax * $pct,2) if $tax;
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Payable ' . $type,'Compras','N/A','N/A','N/A',$cost_payable);
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Taxes Payable ' . $type,'Compras','N/A','N/A','N/A',$tax_payable) if $tax_payable;
		### Sum Tax to Debit Amount
		&Do_SQL("UPDATE sl_movements SET Amount = Amount + $tax_payable WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND Credebit = 'Debit' AND Amount = '$cost_payable' ORDER BY ID_movements DESC LIMIT 1;") if $tax_payable;

		### Paid Data
		my $cost_paid = $cost - $cost_payable;
		$tax_paid = $tax - $tax_payable;
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Paid ' . $type,'Compras','N/A','N/A','N/A',$cost_paid);
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Taxes Paid ' . $type,'Compras','N/A','N/A','N/A',$tax_paid) if $tax_paid;
		### Sum Tax to Debit Amount
		&Do_SQL("UPDATE sl_movements SET Amount = Amount + $tax_paid WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND Credebit = 'Debit' AND Amount = '$cost_paid' ORDER BY ID_movements DESC LIMIT 1;") if $tax_paid;
	
	}else{

		#################
		#################
		#### 3) Inventory Paid All
		#################
		#################
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Paid ' . $type,'Compras','N/A','N/A','N/A',$cost);
		&general_deposits(0,$id_po,'purchaseorders','Return to Vendor Taxes Paid ' . $type,'Compras','N/A','N/A','N/A',$tax) if $tax;
		### Sum Tax to Debit Amount
		&Do_SQL("UPDATE sl_movements SET Amount = Amount + $tax WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND Credebit = 'Debit' AND Amount = '$cost' ORDER BY ID_movements DESC LIMIT 1;") if $tax;

	}

	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_purchaseorders', ID_tablerelated = '$id_po_rvendor' WHERE ID_tableused = '$id_po' AND tableused = 'sl_purchaseorders' AND (tablerelated IS NULL OR tablerelated = '') AND (ID_tablerelated IS NULL OR ID_tablerelated = 0) AND TIMESTAMPDIFF(SECOND, CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 30;");


	return;
}




#############################################################################
#############################################################################
#   Function: upc_inventory_in
#
#       Es: Registra los movimientos de entrada de inventario provenientes de una orden. Esta funcion es llamada por cada UPC devuelto
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#    
#		 - Modified on *27/01/15* by _Roberto Barcenas_ : Se cambia Categoria Ventas -> Costos por peticion Lizbeth Torres Parada
#
#   Parameters:
#
#      - id_orders : ID Order
#      - cost: SKU Cost
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <order_fastbacktoinventory>
#
sub upc_inventory_in {
#############################################################################
#############################################################################	

	my (@param_data) = @_;

	my $id_orders = $param_data[0];
	my $sku = $param_data[1]; 
	my $cost = $param_data[2] if scalar (@param_data) == 3;
	my $category = 'Devoluciones';
	$category = 'Costos';

	if(!$cost){

		$cost = load_sltvcost($sku);
		##TODO: Llamado a notif cuando no se reciba costo de la parte

	}
	
	#### Movimientos de Contabilidad(Inventory In)
	&general_deposits(0,$id_orders,'orders','Inventory In',$category,'N/A','N/A','N/A',$cost);

	#####
	##### Grouping Amounts
	#####
	&accounting_group_amounts('sl_orders',$id_orders);

	return;
}


#############################################################################
#############################################################################
#   Function: credit_memo_skus_in
#
#       Es: Registra los movimientos de entrada de inventario provenientes de un credit memo
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_creditmemo : ID Credit Memo
#      - id_products : 9 digits version ID Products
#      - cost: SKU Cost
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <order_fastbacktoinventory>
#      <upc_inventory_in>
#
sub credit_memo_skus_in {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $id_creditmemos = int($param_data[0]);
	#my $id_orders = int($param_data[1]);
	my $sku = int($param_data[1]); 
	my $qty = int($param_data[2]);
	my $cost = &filter_values($param_data[3]);
	#$category = 'Devoluciones';
	$category = 'Costos';

	if(!$cost){

		$cost = load_sltvcost($sku) * $qty;
		##TODO: Llamado a notif cuando no se reciba costo de la parte

	}
	
	#### Movimientos de Contabilidad(Inventory In)
	&general_deposits(0,$id_creditmemos,'creditmemos','Inventory In',$category,'N/A','N/A','N/A',$cost);

	return;
}

#############################################################################
#############################################################################
#   Function: skus_in_without_cm
#
#       Es: Crea la contabilidad en las devoluciones sin CMs de la opción(Returns w/o CreditMemo)
#
#    Created on: 2015-06-05
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
#
#
#   Parameters:
#     
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub skus_in_without_cm {
#############################################################################
#############################################################################
	my (@param_data) = @_;

	my $id_creditmemos	= int($param_data[0]);	
	my $id_customers	= int($param_data[1]); 
	my $cost_amt		= &filter_values($param_data[2]);
	my $price_amt		= &filter_values($param_data[3]);
	my $tax_amt			= &filter_values($param_data[4]);
	my $date			= &filter_values($param_data[5]);
	### Pasados por parámetro
	my $ida_inventory	= int($param_data[6]);
	my $ida_cost		= int($param_data[7]);
	my $ida_return		= int($param_data[8]);
	my $ida_customer	= int($param_data[9]);
	my $ida_return_tax	= int($param_data[10]);

	#my $str_params = join('::', @param_data);
	#&cgierr($str_params);

	###
	### Inventory
	###
	&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused , tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users )
			 VALUES ($ida_inventory, $cost_amt, '$id_creditmemos', '$date', 'sl_creditmemos', $id_creditmemos, 'sl_customers', $id_customers, 'Costos', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	###
	### Cost
	###
	&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused , tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users )
			 VALUES ($ida_cost, $cost_amt, '$id_creditmemos', '$date', 'sl_creditmemos', $id_creditmemos, 'sl_customers', $id_customers, 'Costos', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	###
	### Return
	###
	&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused , tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users )
			 VALUES ($ida_return, $price_amt, '$id_creditmemos', '$date', 'sl_creditmemos', $id_creditmemos, 'sl_customers', $id_customers, 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	###
	### Return Tax
	###
	if( $tax_amt > 0 ){
		&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused , tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users )
				 VALUES ($ida_return_tax, $tax_amt, '$id_creditmemos', '$date', 'sl_creditmemos', $id_creditmemos, 'sl_customers', $id_customers, 'Devoluciones', 'Debit', 0, 0, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	}
	###
	### Customer
	###
	$price_amt += $tax_amt;
	&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused , tablerelated, ID_tablerelated, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users )
			 VALUES ($ida_customer, $price_amt, '$id_creditmemos', '$date', 'sl_creditmemos', $id_creditmemos, 'sl_customers', $id_customers, 'Devoluciones', 'Credit', 0, 0, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	return;
}

#############################################################################
#############################################################################
#   Function: accounting_sale_separate_tax
#
#       Es: Ingresa a las cuentas de Sale Tax de productos que se escanean, diferenciando el tax causado del tax pagado y que no han sido cargados a las cuentas.
#       En: 
#
#
#    Created on:
#
#    Author: Erik Osornio
#
#    Modifications:
#		- 08/21/2014: Si el tax es entre 0.01 - .99 se manda a IVA cobrado
#
#
#   Parameters:
#
#      - id_orders: ID_orders
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <accounting_sale>
#
sub accounting_sale_separate_tax {
#############################################################################
#############################################################################	
	#my ($id_orders,$ida_banks,$ida_discount,$pd_order,$tax) = @_;
	my (@param_data) = @_;
	my ($id_orders) = int($param_data[0]);
	##### Pasados por parametro
	my ($ida_banks) = &filter_values($param_data[1]);
	my ($ida_discount) = int($param_data[2]);
	my ($pd_order) = &filter_values($param_data[3]);
	my ($tax) = &filter_values($param_data[4]);
	my $str_params = join('::', @param_data);
	my $this_acc = 0; my $this_acc_str;

	#&cgierr($str_params);
	
	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;


	##############
	##############
	###### Credits (Cuanto me ha pagado)
	##############
	##############
	my ($sth2) = &Do_SQL("SELECT Amount FROM sl_movements WHERE ID_tableused = '$id_orders' 
						AND Credebit = 'Debit' AND Category IN ('Anticipo Clientes','Ventas') 
						AND ID_accounts IN ($ida_banks,$ida_discount)
						AND Status = 'Active';");
	my ($total_paid) = $sth2->fetchrow();


	##############
	##############
	###### Debits (Cuanto me debe pagar)
	##############
	##############	
	my ($sth4) = &Do_SQL("SELECT Amount
					FROM sl_orders_payments 
					WHERE ID_orders = '$id_orders' 
					AND Reason <> 'Refund' 
					AND Amount >= 0
					AND Status NOT IN('Void','Order Cancelled','Cancelled')
					/*AND Captured = 'Yes' AND CapDate <= CURDATE()*/;");
	my ($to_pay) = $sth4->fetchrow();
	
	$total_paid = round($total_paid,3);
	$to_pay = round($to_pay,3);
	#&cgierr("$total_paid vs $to_pay");

	##############
	##############
	###### Total Amount
	##############
	##############
	#my ($total_paid) = $credit_amount; #+ $tax;
	
	if($to_pay > 0){

		if( ($total_paid == $to_pay and $total_paid > 0) or $tax < 1 ) {
			## Payment Completed
			&general_deposits(0,$id_orders,'orders','Sale Tax','Ventas','N/A','N/A','N/A',$tax) if $tax > 0;
			
		} elsif($total_paid == 0 or $to_pay == 0) {
			## Zero Payments (A/R)
			&general_deposits(0,$id_orders,'orders','Sale Tax AR','Ventas','N/A','N/A','N/A',$tax) if $tax > 0;
			
		} else {
			## Payments + AR
			my ($percent) = $total_paid / $to_pay;
			my $tax1 = round($tax * $percent,2); ## Tax Pagado
			my $tax2 = $tax - $tax1; ## Tax Pendiente
			
			&general_deposits(0,$id_orders,'orders','Sale Tax','Ventas','N/A','N/A','N/A',$tax1) if $tax1 > 0;
			&general_deposits(0,$id_orders,'orders','Sale Tax AR','Ventas','N/A','N/A','N/A',$tax2) if $tax2 > 0;
		}


		##
		### Validations
		##
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status IN ('Active','Pending') AND Category = 'Ventas' AND ". $sqlmod_update_records .";");
		my ($total_records) = $sth->fetchrow();

		if($total_records < 2){

			$this_acc = 1;
			$this_acc_str .= " " . &trans_txt('acc_general');

		}

	}
	
	##########################
	return($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: accounting_return_separate_tax
#
#       Es: Ingresa a las cuentas de Tax de productos Devueltos
#       En: 
#
#
#    Created on: 
#
#    Author: _RB_
#
#    Modifications:
#    	- 2014/08/28: Se hace la suma sin distncion entre Debit|Credit para tomar en cuenta devoluciones
#
#
#   Parameters:
#
#      - id_orders: ID_orders
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <accounting_return>
#
sub accounting_return_separate_tax {
#############################################################################
#############################################################################	
	#my ($id_orders,$ida_banks,$ida_discount,$pd_order,$tax) = @_;
	my (@param_data) = @_;
	my ($id_orders) = int($param_data[0]);
	##### Pasados por parametro
	my ($ida_tax_payable) = &filter_values($param_data[1]);
	my ($ida_tax_paid) = &filter_values($param_data[2]);
	my ($tax) = &filter_values($param_data[3]);
	my $str_params = join('::', @param_data);
	#&cgierr($str_params);
	
	if(!$tax){ &cgierr($str_params);return; }

	##############
	##############
	###### 1) SUM(Pagado) | SUM(Pagable)
	##############
	##############
	my ($sth2) = &Do_SQL("SELECT 
							SUM(IF(ID_accounts IN ($ida_tax_paid) /*AND Credebit = 'Credit'*/,Amount,0))AS Paid 
							, SUM(IF(ID_accounts IN ($ida_tax_payable) /*AND Credebit = 'Credit'*/,Amount,0)) - SUM(IF(ID_accounts = '$ida_tax_payable' AND Credebit = 'Debit',Amount,0)) AS Payable
						FROM sl_movements WHERE ID_tableused = '$id_orders' 
						AND  tableused = 'sl_orders'
						AND ID_accounts IN ($ida_tax_payable, $ida_tax_paid)
						AND Status = 'Active';");
	my ($tax_paid, $tax_payable) = $sth2->fetchrow();

	##############
	##############
	###### 2) Evaluacion
	##############
	##############
	
	if($tax_payable >= $tax){

		####
		#### 2.1) 100% Tax Payable
		####
		&general_deposits(0,$id_orders,'orders','Return Tax Payable','Devoluciones','N/A','N/A','N/A',$tax);
		#&cgierr("1 $tax_paid, $tax_payable");
	}elsif($tax_payable == 0 and $tax_paid > 0){

		####
		#### 2.2) 100% Tax Paid
		####
		if($tax_paid >= $tax){
			&general_deposits(0,$id_orders,'orders','Return Tax Paid','Devoluciones','N/A','N/A','N/A',$tax);
			#&cgierr("2 $tax_paid, $tax_payable");
		}else{
			&general_deposits(0,$id_orders,'orders','Return Tax Paid','Devoluciones','N/A','N/A','N/A',$tax_paid);
			#&cgierr("3 $tax_paid, $tax_payable");
		}

	}elsif($tax_payable > 0 and $tax_paid > 0){

		my $tax_tmp = $tax;
		####
		#### 2.3) Mix Payable + Paid
		####

		####
		#### 2.3.1) Tax Payable
		####
		&general_deposits(0,$id_orders,'orders','Return Tax Payable','Devoluciones','N/A','N/A','N/A',$tax_payable);
		$tax -=	$tax_payable;

		####
		#### 2.3.2) Tax Paid
		####
		&general_deposits(0,$id_orders,'orders','Return Tax Paid','Devoluciones','N/A','N/A','N/A',$tax);
		#&cgierr("4 $tax_paid, $tax_payable");
	}	
	#&cgierr("5 $tax_paid, $tax_payable");

	return;
}


#############################################################################
#############################################################################
#   Function: order_deposit_separate_tax
#
#       Es: Separa el tax pagado de un deposito cobrado en una orden de venta
#       En: 
#
#
#    Created on: 07/15/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#		- Modified by _RB_ on 07/23/2013: Se corrige problema de calculo, se hacen pruebas con el script fix_sales.pl y se comprueba funcionamiento normal
#                     _IM_ on 08/01/2014: Corrige traspaso y desglose de IVA en pagos (también aplica para Journal Entries)
#
#
#   Parameters:
#
#      - id_orders: ID_orders
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <accounting_sale>
#
sub order_deposit_separate_tax {
#############################################################################
#############################################################################	
	my ($id_orders,$id_payments,$category,$ida_taxes) = @_;

	###################
	###################
	################### Traspaso de IVA
	###################
	###################
	my ($tax_pcts, $ida_tax_credits, $ida_tax_debits) = split(/,/,$ida_taxes);

	## How to update
	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';	


	
	########
	######## 1) Sacamos el porcentaje de lo pagado
	########
	#@ivanmiranda Se edito el query para tomar el Saldo de la Venta y no el saldo en línea
	#bkp: SUM(IF( ( (Captured <> 'Yes' OR Captured IS NULL) AND (CapDate IS NULL OR CapDate = '0000-00-00') ) OR ID_orders_payments = '$id_payments',Amount,0))AS Total 
	my ($sth2) = &Do_SQL("SELECT Amount / Total FROM sl_orders_payments INNER JOIN
						(
							SELECT ID_orders,
							SUM(Amount)AS Total 
							FROM sl_orders_payments WHERE ID_orders = '$id_orders'
							AND Status NOT IN('Void','Order Cancelled','Cancelled')
						)tmp USING(ID_orders)
						WHERE ID_orders_payments = '$id_payments';");
	my ($pct_paid) = $sth2->fetchrow();


	if($pct_paid > 0) {

		########
		######## 2) Buscamos Tax
		########

		my ($sth) = &Do_SQL("SELECT ID_accounts, SUM(Amount) AS Tax FROM sl_movements WHERE ID_tableused = '$id_orders' AND tableused = 'sl_orders' AND Credebit = 'Credit' AND Status = 'Active' GROUP BY ID_accounts;");
		my $x = $sth->rows();

		if($x > 0 and $pct_paid > 0){

			while(my ($id_accounts, $this_tax) = $sth->fetchrow()) {


				my @ary_c = split(/:/, $ida_tax_credits);
				my @ary_d = split(/:/, $ida_tax_debits);

				for(0..$#ary_c){

					#######
					####### 3) Buscamos el tax y aplicamos el movimiento de traspaso
					#######
					if($id_accounts == $ary_c[$_]){

						#&cgierr("$id_accounts == $ary_c[$_] ::: $amount_tax = round($this_tax * $pct_paid,3)");
						my $this_ida_debit = $ary_c[$_];
						my $this_ida_credit = $ary_d[$_];
						my $amount_tax = round($this_tax * $pct_paid,3);

						if($amount_tax >= 0.01){

							&Do_SQL("/* Tax Traspaso  */ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
							VALUES ($this_ida_debit,'".$amount_tax."', '', CURDATE(), 'sl_orders', $id_orders, '$category', 'Debit',". $md5time_value ." 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

							&Do_SQL("/* Tax Traspaso  */ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
							VALUES ($this_ida_credit,'".$amount_tax."', '', CURDATE(), 'sl_orders', $id_orders, '$category', 'Credit',". $md5time_value ." 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

						}

					}

				}

			}

		}

	}

	return;

}



######################################################
######################################################
######################################################
######
###### BILLS
######
######################################################
######################################################
######################################################



#############################################################################
#############################################################################
#   Function: bills_expenses_record
#
#       Es: Reconoce Deuda de Bill Expenses / Tambien genera contabilidad con cargo-abono inverso para casos de Creditos
#       En: 
#
#
#    Created on: 2013-05-25 
#
#    Author: _RB_
#
#    Modifications:
#		- 2014-05-27: Se utiliza misma funcion para generar contabilidad en notas de credito de proveedores simplemente volteando Debito/Credito respecto a Expenses. Valor se recibe en un parametro
#
#
#   Parameters:
#
#      - id_orders: ID_orders
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <shipping_tax_holding>
#
#
#  ToDO: #1 Se agrega la toma de cuenta deudora del proveedor. Se comenta mientras hay aprobacion
#  ToDO: #2 Se descomenta para pruebas en pp, con finalidad de pasar a produccion
#
sub bills_expenses_record {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	### Datos recibidos
	my $id_bills = int($param_data[0]);
	my $id_segments = int($param_data[1]);
	my $deductible = &filter_values($param_data[2]);
	my $id_accounts = int($param_data[3]);
	my $amount = &filter_values($param_data[4]);
	my $exchange_rate = &filter_values($param_data[5]);
	my $flip_credebit = &filter_values($param_data[6]);
	### Dataos pasados por parametro de la funcion
	my $category = int($param_data[7]);
	my $ida_vendor = int($param_data[8]);
	my ($ida_holding, $id_accounts_holding, $pct_holding, $fn_holding) = split( /:/, &filter_values($param_data[9]) );
	$ida_holding = int($ida_holding);
	$ida_accounts_holding = int($ida_accounts_holding);


	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	$amount *= $exchange_rate;
	(lc($deductible) eq 'yes') and ($deductible = 'deductible');
	

	#####
	##### Cuando se recibe un expense, se hace debit-credit, cuando se recibe credit se hace credit-debit
	#####
	my $credebit_debit = !$flip_credebit ? 'Debit' : 'Credit';
	my $credebit_credit = !$flip_credebit ? 'Credit' : 'Debit';


	if($amount > 0) {

		###
		## Buscamos cuenta Acreedora en Proveedor
		### 
		my $query = "SELECT 
						ID_accounts_credit
					FROM 
						sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors 
					WHERE 
						sl_bills.ID_bills = ". $id_bills .";";
		my ($sth) = &Do_SQL($query);
		my ($this_ida_vendor_credit) = $sth->fetchrow();
		$ida_vendor = $this_ida_vendor_credit if $this_ida_vendor_credit;

		#######
		####### Debit
		#######
		my ($sthd) = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused ,Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users )
							VALUES ($id_accounts, $amount, '$deductible', CURDATE(), 'sl_bills', $id_bills, 'Gastos', '$credebit_debit', '$id_segments', 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		my ($idm_debit) = $sthd->{'mysql_insertid'};

		#######
		####### Credit
		#######
		my ($sthc) = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused ,Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users )
							VALUES ($ida_vendor, $amount, '$deductible', CURDATE(), 'sl_bills', $id_bills, 'Gastos', '$credebit_credit', '$id_segments', 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		my ($idm_credit) = $sthc->{'mysql_insertid'};

	}elsif($amount < 0){

		#######
		####### Credit
		#######
		my ($sthc) = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused ,Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users )
							VALUES ($id_accounts, ABS($amount), '$deductible', CURDATE(), 'sl_bills', $id_bills, 'Gastos', '$credebit_credit', '$id_segments', 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");


		my ($sth) = &Do_SQL("SELECT ID_movements FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND ID_accounts = '$ida_vendor' AND Credebit = '$credebit_credit' AND Date = CURDATE() AND Amount > Amount - ABS($amount);");
		my ($this_idmovs) = $sth->fetchrow();

		my $modquery = $this_idmovs ? "ID_movements = '$this_idmovs' " : "1 AND Credebit = '$credebit_credit' AND Date = CURDATE() ORDER BY Amount DESC LIMIT 1 ";
		&Do_SQL("UPDATE sl_movements SET Amount = Amount - ABS($amount) WHERE $modquery");

	}
	&accounting_group_amounts('sl_bills', $id_bills);

	#################
	################# Extra Events
	#################
	#if($id_accounts == $ida_holding and $fn_holding) {
	#	
	#	if(defined &$fn_holding ) {
	#		&$fn_holding($idm_debit, $idm_credit, @param_data);
	#	}
	#
	#}


	return;
}


#############################################################################
#############################################################################
#   Function: accounting_expense_apply_deposit
#
#       Es: Ejecucion de contabilidad para aplicacion de anticipo a Expense
#       En: Accouting movements when Vendor deposit is applied to a PO
#
#
#    Created on: 06/26/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_expenses,$ida_banks,$ida_deposit,$this_amount,$currency_exchange,$pct, $ida_vendor_deposit, $ida_vendor, $ida_tax_payable, $ida_tax_paid, $type)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#   	<bills_expenses_payment>
#
#
sub accounting_expense_apply_deposit  {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	## Pasados via parametros en la funcion que lo manda llamar 6338,0,88,53353.66,13.1200,1.0000000
	my $id_bills = int($param_data[0]);
	my $id_bills_original = int($param_data[1]); # Este es el Bill del Deposit/Credit
	my $ida_banks = int($param_data[2]);
	my $ida_deposit = int($param_data[3]);
	my $amount = &filter_values($param_data[4]);
	my $exchange_rate = &filter_values($param_data[5]); # Del Bill del Deposit/Credit
	my $pct_paid = round(&filter_values($param_data[6]), 2);
	## Pasados via parametros en el setup de la funcion
	my $ida_vendor_deposit = &filter_values($param_data[7]);
	my $ida_vendor = &filter_values($param_data[8]);
	my $ida_tax_payable = &filter_values($param_data[9]);
	my $ida_tax_paid = &filter_values($param_data[10]);
	my $category = int($param_data[11]);
	
	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);

	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	my $this_acc = 0; my $this_acc_str = 'OK'; my $flag_tax = 0;

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;

	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';

	#######
	####### Currency Exchange (Convert to Default Currency)
	#######
	$amount *= $exchange_rate;#round($exchange_rate,3); 
	my $tmp_amount = $amount;

	##
	### Buscamos Cuenta de Proveedor y Anticipo
	##
	my $this_ida_vendor = 0; my $this_ida_vendor_deposit = 0;
	my $id_vendors = &load_name('sl_bills','ID_bills',$id_bills,'ID_vendors');
	my ($sth) = &Do_SQL("SELECT ID_accounts_debit, ID_accounts_credit FROM sl_vendors WHERE ID_vendors = ". $id_vendors .";");
	($this_ida_vendor_deposit, $this_ida_vendor) = $sth->fetchrow();

	###
	## Cuenta Acreedora
	###
	if(!$this_ida_vendor){

		#1.1. En el Bill
		my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = ". $id_bills ." AND tableused = 'sl_bills' AND Credebit = 'Credit' AND ID_accounts IN(". $ida_vendor .") AND Status = 'Active' ORDER BY EffDate LIMIT 1;");
		$this_ida_vendor = $sth->fetchrow();

	}

	if(!$this_ida_vendor){

		#1.2. En las cuentas parametrizadas
		my @ary = split(/,/, $ida_vendor);
		$this_ida_vendor = int($ary[0]);

	}


	##
	### Cuenta de Anticipo
	##
	if(!$this_ida_vendor_deposit){

		#2.1 En el Anticipo
		my $modthis = $id_bills_original > 0 ? " AND ID_tablerelated = '$id_bills_original' " : '';
		my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = ". $id_vendors ." ". $modthis ." AND tableused = 'sl_vendors' AND Credebit = 'Debit' /*AND ID_accounts IN(". $ida_vendor_deposit .") AND ROUND(Amount) >= ROUND(". $amount .")*/ LIMIT 1;");
		my ($this_ida_bills_deposit) = $sth->fetchrow();
		$this_ida_vendor_deposit = $this_ida_bills_deposit if $this_ida_bills_deposit;

	}

	#3. En las cuentas parametrizadas
	if(!$this_ida_vendor_deposit){

		my @ary = split(/,/, $ida_vendor);
		my @ary2 = split(/,/, $ida_vendor_deposit);
		for (0..$#ary) {
			$this_ida_vendor_deposit = $ary2[$_] if $ary[$_] eq $this_ida_vendor;
		}

	}
	(!$this_ida_vendor_deposit) and ($this_ida_vendor_deposit = 1);


	if($amount > 0 and $this_ida_vendor and $this_ida_vendor_deposit){

		my ($sth) = &Do_SQL("/*Apply Deposit Debit*/
							INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
							VALUES ($this_ida_vendor,'".$amount."', '', CURDATE(), 'sl_bills', $id_bills, 'Aplicacion Anticipos AP', 'Debit',". $md5time_value ." 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");


		if(int($this_ida_vendor_deposit)) {

			&Do_SQL("/* Apply Deposit Credit - $this_ida_vendor - $ida_vendor - $ida_vendor_deposit*/ 
						INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time,ID_admin_users )
						VALUES ($this_ida_vendor_deposit,'".$amount."', '', CURDATE(), 'sl_bills', $id_bills, 'Aplicacion Anticipos AP', 'Credit',". $md5time_value ." 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		
		}

		####################
		####################
		####### 3) Buscamos Cuenta de IVA para aplicar
		####################
		####################
		my ($sth) = &Do_SQL("SELECT ID_accounts, SUM(Amount) FROM sl_movements WHERE ID_tableused = ". $id_bills ." AND ID_accounts IN(". $ida_tax_payable .") AND tableused = 'sl_bills' AND Credebit = 'Debit' AND Status = 'Active' GROUP BY ID_accounts;");
		while( my ($this_ida_tax_payable,$tax_payable) = $sth->fetchrow() ) {

			if($tax_payable > 0) {

				++$flag_tax;
				my $this_ida_tax_paid = 0;
				my @ary = split(/,/, $ida_tax_payable);
				my @ary2 = split(/,/, $ida_tax_paid);
				for (0..$#ary) {
					$this_ida_tax_paid = $ary2[$_] if $ary[$_] eq $this_ida_tax_payable;
				}

				#######
				####### Currency Exchange (Convert to Default Currency)
				#######
				my $amount_tax = round($tax_payable * $pct_paid,3);

				#########
				######### Decremento IVA Original
				#########
				#print "$amount: $tax_payable * $pct_paid\n";
				my ($sth) = &Do_SQL("/*Tax Paid - $tax_payable * $pct_paid */ 
							INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
							VALUES ($this_ida_tax_payable, '".$amount_tax."', '', CURDATE(), 'sl_bills', $id_bills, 'Aplicacion Anticipos AP', 'Credit',". $md5time_value ."'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
				
				#########
				######### Traspaso IVA Pagado
				#########
				if($this_ida_tax_paid) {
					my ($sth) = &Do_SQL("/*Tax Paid - $tax_payable * $pct_paid */ 
								INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
								VALUES ($this_ida_tax_paid, '".$amount_tax."', '', CURDATE(), 'sl_bills', $id_bills, 'Aplicacion Anticipos AP', 'Debit',". $md5time_value ." 'Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
				}			

			}

		}


		## 4) Final Validation
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_bills ."' AND tableused = 'sl_bills' AND Status = 'Active' AND Category = 'Aplicacion Anticipos AP' AND ". $sqlmod_update_records .";");
		my ($total_records) = $sth->fetchrow();

		#&cgierr('TR: ' . $total_records . "\nFT: " . $flag_tax);
		if( ($flag_tax and $total_records < 4) or (!$flag_tax and $total_records < 2) ){

			## Record Validation Failed
			$this_acc = 1;
			$this_acc_str = &trans_txt('acc_accountig_record_count_failed');

		}else{

			&accounting_group_amounts('sl_bills', $id_bills);

		}

	}else{

		## Some variables needed not found
		$this_acc = 1;
		$this_acc_str = &trans_txt('acc_accountig_fn_failed');

	}
	
	#&cgierr('ACC: ' . $this_acc . "\nACCS: " . $this_acc_str);
	return ($this_acc, $this_acc_str);

}



#############################################################################
#############################################################################
#   Function: bills_expenses_payment 
#
#       Es: Ejecucion de contabilidad cuando se realiza un pago de Expenses
#       En: Accouting movements when Expenses payment is posted
#
#
#    Created on: 06/07/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on *2014/12/17* by _Roberto Barcenas_ : Se cancela llamado a accounting_group_amounts por peticion equipo contabilidad.
#        - Modified on *2014/12/17* by _Roberto Barcenas_ : Se agrega Category='Gastos' en la suma del IVA por pagar para no sumar el IVA de cancelaciones de pagos.
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_bills,$id_banks,$amount,$amount_c,$vendor_type,$ida_tax_payabla,$ida_tax_paid)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#
#
sub bills_expenses_payment  {
#############################################################################
#############################################################################

	my (@param_data) = @_;
	my ($pct,$amount_tax,$amount_cost);

	
	## Pasados a traves de la funcion que lo llama
	my $id_bills = int($param_data[0]);
	my $ida_banks = int($param_data[1]);
	my $amount = &filter_values($param_data[2]);
	my $pct_paid = &filter_values($param_data[3]);
	my $exchange_rate = &filter_values($param_data[4]);
	## Pasados a traves de parametros en el setup de la funcion
	my $category = int($param_data[5]);
	my $ida_tax_payable = &filter_values($param_data[6]);
	my $ida_tax_paid = &filter_values($param_data[7]);
	my $ida_vendor = &filter_values($param_data[8]);
	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);

	####################
	####################
	####### 1) Buscamos la suma de deuda al proveedor y el porcentaje que representa en los creditos
	####################
	####################
	#my ($sth) = &Do_SQL("SELECT SUM(IF(ID_accounts IN($ida_vendor),Amount,0)) / SUM(Amount) FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND Credebit = 'Credit' AND Status = 'Active' AND TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0;");
	#my ($credit_pct) = $sth->fetchrow();
	#$credit_pct = 1 if !$credit_pct;

	#######
	####### Currency Exchange (Convert to Default Currency)
	#######
	#$amount *= round($exchange_rate,3); #* $credit_pct;
	$amount *= $exchange_rate;

	####################
	####################
	####### 2) Aplicamos el pago de acuerdo a los datos
	####################
	####################
	my $acc_payments = 'Bills Expenses Payment '.$type;

	###
	## Buscamos cuenta Acreedora en Proveedor (Para cancelar deuda)
	### 
	my $query = "SELECT 
					ID_accounts_credit
				FROM 
					sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors 
				WHERE 
					sl_bills.ID_bills = ". $id_bills .";";
	my ($sth) = &Do_SQL($query);
	my ($this_ida_vendor_credit) = $sth->fetchrow();

	## Debit
	if(!$this_ida_vendor_credit){

		&general_deposits(0,$id_bills,'bills',$acc_payments,"Pagos",'N/A','N/A','N/A',$amount);		

	}else{

		&Do_SQL("/* 1 */INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($this_ida_vendor_credit,'".$amount."', '', CURDATE(), 'sl_bills', '$id_bills', 'Pagos', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	}

	
	## Credit
	&Do_SQL("/* 2 */INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($ida_banks,'".$amount."', '', CURDATE(), 'sl_bills', '$id_bills', 'Pagos', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	
	####################
	####################
	####### 3) Buscamos Cuenta de IVA para aplicar
	####################
	####################
	my ($sth) = &Do_SQL("SELECT ID_accounts,SUM(Amount) FROM sl_movements WHERE ID_tableused = '$id_bills' AND ID_accounts IN($ida_tax_payable) AND tableused = 'sl_bills' AND Credebit = 'Debit' AND Status = 'Active' AND Category = 'Gastos' GROUP BY ID_accounts;");
	while( my ($this_ida_tax_payable,$tax_payable) = $sth->fetchrow() ) {

		if($tax_payable > 0) {

			my $this_ida_tax_paid = 0;
			my @ary = split(/,/, $ida_tax_payable);
			my @ary2 = split(/,/, $ida_tax_paid);
			for (0..$#ary) {
				$this_ida_tax_paid = $ary2[$_] if $ary[$_] eq $this_ida_tax_payable;
			}

			#######
			####### Currency Exchange (Convert to Default Currency)
			#######
			my $amount_tax = round($tax_payable * $pct_paid,3);

			#########
			######### Decremento IVA Original
			#########
			#print "$amount: $tax_payable * $pct_paid\n";
			my ($sth) = &Do_SQL("/*Tax Paid - $tax_payable * $pct_paid */ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
						VALUES ($this_ida_tax_payable, '".$amount_tax."', '', CURDATE(), 'sl_bills', $id_bills, 'Pagos', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			
			#########
			######### Traspaso IVA Pagado
			#########
			if($this_ida_tax_paid) {
				my ($sth) = &Do_SQL("/*Tax Paid - $tax_payable * $pct_paid */ INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
							VALUES ($this_ida_tax_paid, '".$amount_tax."', '', CURDATE(), 'sl_bills', $id_bills, 'Pagos', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			}			

		}

	}

	&accounting_group_amounts('sl_bills', $id_bills);
	#&cgierr(2);
	
	return;
}


#############################################################################
#############################################################################
#   Function: bills_expenses_check_paid 
#
#       Es: Ejecucion de contabilidad despues que se realiza un pago/deposito de Expenses
#       En: Accouting movements after Expenses payment/deposit is posted
#
#
#    Created on: 07/11/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_bills,$id_profit,$ida_lost)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#
#
sub bills_expenses_paid  {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	## Pasados a traves de la funcion que lo llama
	my $id_bills = int($param_data[0]);
	## Pasados por configuracion
	my $ida_vendor = &filter_values($param_data[1]);
	my $ida_profit = int($param_data[2]);
	my $ida_lost = int($param_data[3]);

	my $this_acc = 0; my $this_acc_str = 'OK'; my $flag_amount = 0;

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(SECOND,CONCAT(Date,' ',Time) , NOW()) BETWEEN 0 AND 50|;

	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';
	my $this_amount_due = round(&bills_amount_due($id_bills), 2);

	if($cfg{'acc_default_currency'} and $this_amount_due <= 0) {

		## No debt
		my ($sth) = &Do_SQL("SELECT 
								sl_bills.Currency 
							FROM 
								sl_bills 
							WHERE 
								ID_bills = ". $id_bills .";");
		my($vendor_currency) = $sth->fetchrow();

		if ($vendor_currency and $vendor_currency ne $cfg{'acc_default_currency'}) {

			##########
			##########  Monto completo. Buscamos perdida o ganancia
			##########

			## Buscamos la cuenta utilizada
			my ($sth2) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = ". $id_bills ." AND tableused = 'sl_bills' AND ID_accounts IN(". $ida_vendor .") AND Credebit = 'Credit' AND Status = 'Active' ORDER BY EffDate LIMIT 1;");
			my ($this_ida_vendor) = $sth2->fetchrow();

			if(!$this_ida_vendor){

				my ($sth) = &Do_SQL("SELECT ID_accounts_credit FROM sl_bills INNER JOIN sl_vendors ON sl_bills.ID_vendors = sl_vendors.ID_vendors WHERE sl_bills.ID_bills = ". $id_bills .";");
				$this_ida_vendor = $sth->fetchrow();

			}

			
			## Buscamos la fecha del ultimo pago
			my ($sth3) = &Do_SQL("SELECT 
									EffDate
									, Date
									, Time
									, IF(ID_segments IS NULL,0,ID_segments)AS ID_segments 
								FROM 
									sl_movements 
								WHERE 
									ID_tableused = ". $id_bills ." 
									AND tableused = 'sl_bills' 
									AND ID_accounts IN(SELECT DISTINCT sl_vendors.ID_accounts_credit FROM sl_vendors WHERE sl_vendors.ID_accounts_credit > 0) 
									AND Credebit = 'Debit' 
									AND Status = 'Active' 
								ORDER BY 
									EffDate DESC LIMIT 1;");
			my ($effdate, $d, $t, $ids) = $sth3->fetchrow();
			$ids = 0 if !$ids;

			## Cargos y Abonos
			my ($sth) = &Do_SQL("SELECT 
									SUM(IF(ID_accounts = ". $this_ida_vendor ." AND Credebit = 'Debit',Amount,0)) AS Debits,
									SUM(IF(ID_accounts = ". $this_ida_vendor ." AND Credebit = 'Credit',Amount,0)) AS Credits
								FROM 
									sl_movements 
								WHERE 
									ID_tableused = ". $id_bills ." 
									AND tableused = 'sl_bills'
									AND Status = 'Active';");
			my ($debits,$credits) = $sth->fetchrow();
			$debits = &round($debits,2); $credits = &round($credits, 2);
			my $amount = abs(round($debits - $credits,2));
			$flag_amount++ if $amount;
			#&cgierr("$debits,$credits,$amount");

			if($debits > $credits){

				##########
				##########  Perdida Cambiaria
				##########
				&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
						VALUES (". $ida_lost .",'".$amount."', '', '". $effdate ."', 'sl_bills', '". $id_bills ."', 'Pagos', 'Debit',". $ids .",". $md5time_value ." 'Active','". $d ."', '". $t ."', '". $usr{'id_admin_users'} ."');");
				&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
						VALUES (". $this_ida_vendor .",'".$amount."', '', '". $effdate ."', 'sl_bills', '". $id_bills ."', 'Pagos', 'Credit',". $ids .",". $md5time_value ." 'Active','". $d ."', '". $t ."', '". $usr{'id_admin_users'} ."');");
				#&cgierr("Se termino de pagar: $id_bills y tuvo perdida");
			
			}elsif($debits < $credits) {

				##########
				##########  Ganancia Cambiaria
				##########
				&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
						VALUES (". $this_ida_vendor .",'".$amount."', '', '". $effdate ."', 'sl_bills', '". $id_bills ."', 'Pagos', 'Debit',". $ids .",". $md5time_value ." 'Active','". $d ."', '". $t ."', '". $usr{'id_admin_users'} ."');");
				&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,". $md5time_field ." Status,Date,Time  ,ID_admin_users )
						VALUES (". $ida_profit .",'".$amount."', '', '". $effdate ."', 'sl_bills', '". $id_bills ."', 'Pagos', 'Credit',". $ids .",". $md5time_value ." 'Active','". $d ."', '". $t ."', '". $usr{'id_admin_users'} ."');");
				#&cgierr("Se termino de pagar: $id_bills y tuvo ganancia");
			
			}

			($in{'id_segments'}) and ( &Do_SQL("UPDATE sl_movements INNER JOIN sl_accounts USING(ID_accounts) SET ID_segments = '".$in{'id_segments'}."' WHERE ID_tableused = ". $id_bills ." AND ID_segments = 0 AND Segment = 'Yes' AND ". $sqlmod_update_records ." ;") );

		}

	}


	## Final Validation
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_bills ."' AND tableused = 'sl_bills' AND Status = 'Active' AND Category = 'Pagos' AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();

	#&cgierr("$flag_amount and $total_records");
	if( $flag_amount and $total_records < 2 ){

		## Record Validation Failed
		$this_acc = 1;
		$this_acc_str = &trans_txt('acc_accountig_record_count_failed');

	}


	return;
}


#############################################################################
#############################################################################
#   Function: bills_po_exchange_profit_lost 
#
#       Es: Se calcula posible perdida/ganancia cambiaria
#       En: Possible Profit/Lost
#
#
#    Created on: 11/25/2014
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_po, $id_bills, $amount, $exchange_rate, $ida_profit, $ida_lost)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<bills_po_apply_deposit>
#
#
sub bills_po_exchange_profit_lost  {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	## Pasados a traves de la funcion que lo llama
	my $id_po = int($param_data[0]);
	my $id_bills = int($param_data[1]);
	my $amount = &filter_values($param_data[2]);
	my $tax = &filter_values($param_data[3]);
	my $exchange_rate = &filter_values($param_data[4]);
	my $ida_vendor = int($param_data[5]);
	my $ida_tax_payable = &filter_values($param_data[6]);
	my $ida_tax_paid = &filter_values($param_data[7]);
	my $ida_profit = int($param_data[8]);
	my $ida_lost = int($param_data[9]);
	my $category = &filter_values($param_data[10]);
	my $str_params = join('||', @param_data);
	my ($this_id_wreceipts_notes,$this_acc,$this_acc_str);

	####################
	####################
	####### 1) Comparamos monedas (Empresa vs Pago/Anticipo)
	####################
	####################
	
	####
	#### 1.1) Buscamos moneda en expense
	####
	my ($sth) = &Do_SQL("SELECT Currency, BankDate FROM sl_bills INNER JOIN sl_banks_movrel ON ID_bills = tableid INNER JOIN sl_banks_movements USING(ID_banks_movements) WHERE ID_bills = '$id_bills' AND tablename = 'bills' AND sl_banks_movements.Status = 'Active' AND sl_banks_movements.Type = 'Credits' LIMIT 1;");
	my ($this_currency, $this_date) = $sth->fetchrow();

	if(!$this_currency){

		####
		#### 1.2) Buscamos moneda en vendor
		####
		my ($sth) = &Do_SQL("SELECT IF(LENGTH(sl_vendors.Currency) > 0, sl_vendors.Currency, sl_bills.Currency), CURDATE() FROM sl_bills INNER JOIN sl_vendors USING(ID_vendors) WHERE ID_bills = '$ID_bills';");
		($this_currency, $this_date) = $sth->fetchrow();

	}

	###
	### 1.1 Misma moneda que la empresa?
	###
	return if ($this_currency eq $cfg{'acc_default_currency'} or !$this_currency);

	####################
	####################
	####### 2) Buscamos currency_exchange del pasivo(Ultima)
	####################
	####################
	my $q2;
	my $q1 = "SELECT ID_wreceipts FROM sl_wreceipts WHERE ID_purchaseorders = ". $id_po ." AND Status = 'Processed' /*AND Date >= '$this_date'*/ ORDER BY Date DESC, TIME DESC LIMIT 1;";
	my ($sth) = &Do_SQL($q1);
	my ($id_wreceipts) = $sth->fetchrow();

	if(!$id_wreceipts){

		## 2.1 Buscamos en Notas (WReceipt No Inventariable)
		$q2 = "SELECT 0, Notes FROM sl_purchaseorders_notes WHERE sl_purchaseorders_notes.ID_purchaseorders = ". $id_po ." AND sl_purchaseorders_notes.Notes LIKE 'Warehouse Receipt%';";
		my ($sth) = &Do_SQL($q2);
		($id_wreceipts, $this_id_wreceipts_notes) = $sth->fetchrow();

		if($this_id_wreceipts_notes){

			## 2.1.1 Buscamos last_exchange_rate
			my @ary = split(/\n/, $this_id_wreceipts_notes);
			for(0..$#ary){

				if($ary[$_] =~ /Exchange Rate: \$ (.+)/){

					$last_exchange_rate = round($1,2);

				}

			}


		}

	}
	$this_acc_str .= qq|\nQ1: $q1\nQ2: $q2|;

	###
	### 2.2 No se encuentra wreceipt
	###
	return (1, $this_acc_str) if (!$id_wreceipts and !$last_exchange_rate);


	if(!$last_exchange_rate){

		## ToDo: Agregar currency_exchange en la tabla sl_wreceipts para poder sacar el tipo de cambio sin buscar por texto en notas.
		my $q4;
		my $q3 = "SELECT exchange_rate FROM sl_wreceipts INNER JOIN sl_exchangerates USING(ID_exchangerates) WHERE ID_wreceipts = ". $id_wreceipts .";";
		my ($sth) = &Do_SQL($q3);
		$last_exchange_rate = $sth->fetchrow();

		if(!$last_exchange_rate){
			$q4 = "SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(Notes, 'Currency Exchange: ', -1), 'Unit Cost:',1)) FROM sl_wreceipts_notes WHERE ID_wreceipts = ". $id_wreceipts ." AND Notes LIKE '%Currency Exchange:%' LIMIT 1;";
			my ($sth) = &Do_SQL($q4);
			$last_exchange_rate = $sth->fetchrow();
		}
		$this_acc_str .= qq|\nQ3: $q3\nQ4: $q4|;

	}
	$this_acc_str .= qq|\nLEXR: $last_exchange_rate|;

	###
	### 2.2 No se encuentra currency_exchange
	###
	return (1, $this_acc_str) if !last_exchange_rate;
	###
	### 2.3 Mismo tipo de cambio
	###
	return (0,'')if abs($exchange_rate - $last_exchange_rate) == 0;

	####################
	####################
	####### 3) Calculamos ganacia/perdida
	####################
	####################
	
	###
	### 3.1) Monto basado en tipo de cambio de ultima recepcion.
	###
	my $amount_then = round($amount * $last_exchange_rate,2);
	my $tax_then = round($tax * $last_exchange_rate,2);

	###
	### 3.2) Monto basado en tipo de cambio de aplicacion actual
	###
	my $amount_now = round($amount * $exchange_rate,2);
	my $tax_now = round($tax * $exchange_rate,2);

	###
	### 3.3) Calculamos ganancia/perdida
	###
	my $amount_difference = round($amount_then - $amount_now,2);
	my $tax_difference = round($tax_then - $tax_now,2);

	#&cgierr("\nAMT:$amount\nERT: $last_exchange_rate\nERN:$exchange_rate\nAMTT: $amount_then\nAMTN:$amount_now\nAMTD:$amount_difference");
	$this_acc_str .= qq|\nAmtThen: $amount_then\nAmtNow: $amount_now\nAmtDiff: $amount_difference|;
	$this_acc_str .= qq|\nTaxThen: $tax_then\nTaxNow: $tax_now\nTaxDiff: $tax_difference|;


	my $category_mvs = ($category) ? $category : "Aplicacion Anticipos AP";

	###
	### 3.4) Ganancia / Perdida
	###
	if($amount_difference > 0){

		###
		### 3.4.1) Ejecutamos Ganancia
		###
		#&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
		#		VALUES ($ida_vendor,'".abs($amount_difference)."', '', CURDATE(), 'sl_purchaseorders', $id_po, '$category_mvs', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($ida_profit,'".abs($amount_difference)."', '', CURDATE(), 'sl_purchaseorders', $id_po, '$category_mvs', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		sleep(1);
		&Do_SQL("UPDATE sl_movements SET Amount=Amount+".abs($amount_difference)." WHERE tableused='sl_purchaseorders' AND ID_tableused='$id_po' AND Category='$category_mvs' AND ID_accounts='$ida_vendor' AND Credebit='Debit' AND ID_admin_users='$usr{'id_admin_users'}' ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");		

	}elsif($amount_difference < 0){

		###
		### 3.4.2) Ejecutamos Perdida
		###
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
				VALUES ($ida_lost,'".abs($amount_difference)."', '', CURDATE(), 'sl_purchaseorders', $id_po, '$category_mvs', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

		sleep(1);
		&Do_SQL("UPDATE sl_movements SET Amount=Amount-".abs($amount_difference)." WHERE tableused='sl_purchaseorders' AND ID_tableused='$id_po' AND Category='$category_mvs' AND ID_accounts='$ida_vendor' AND Credebit='Debit' AND ID_admin_users='$usr{'id_admin_users'}' ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 1;");
		#&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
		#		VALUES ($ida_vendor,'".abs($amount_difference)."', '', CURDATE(), 'sl_purchaseorders', $id_po, '$category_mvs', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

	}

	###
	### 3.5) Actualizacion Tax
	###
	if($tax){
	
		&Do_SQL("UPDATE sl_movements SET Amount = ". $tax_then ." WHERE tableused = 'sl_purchaseorders' AND ID_tableused = ". $id_po ." AND Category = '". $category_mvs ."' AND ID_accounts IN (". $ida_tax_payable .",". $ida_tax_paid .") AND ID_admin_users = ". $usr{'id_admin_users'} ." ORDER BY CONCAT(Date,' ',Time) DESC LIMIT 2;");

	}


	return ($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: bills_po_check_paid 
#
#       Es: Ejecucion de contabilidad despues que se realiza un pago/deposito de PO
#       En: Accouting movements after PO payment/deposit is posted
#
#
#    Created on: 07/11/2013
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - @param_data: Arreglo con datos ($id_po,$ida_vendor,$id_profit,$ida_lost)
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#   	
#   	<accounting_vendor_deposit>
#
#
sub bills_po_check_paid  {
#############################################################################
#############################################################################

	return;


	########################################
	########################################
	######################################## TODO: Como se calcula si se ha pagado el PO (Ajustes)
	########################################
	######################################## Modificar esta funcion (esta es copia de la de expenses)
	########################################
	######################################## Nota: Sumar po_items.Amount + (po_adjustments.Amount del InCOGS)
	########################################



	my (@param_data) = @_;

	## Pasados a traves de la funcion que lo llama
	my $id_bills = int($param_data[0]);
	my $ida_vendor = &filter_values($param_data[1]);
	my $ida_profit = int($param_data[2]);
	my $ida_lost = int($param_data[3]);

	##################
	################## 1) Buscamos el monto adeudado
	##################


	##################
	################## 1) Buscamos los bills donde hay pagos para el Bill especifico (Se buscan otros bills por aplicacion de anticipos/creditos)
	##################
	my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_bills) FROM sl_bills_applies WHERE ID_bills_applied = '$id_bills' AND Amount > 0;");
	my ($id_deposits) = $sth->fetchrow();
	my $modquery = $id_deposits ne '' ? "`tableid` IN ($id_deposits) OR " : '';

	##################
	################## 2) Comparamos Monto Bill vs Monto Pagado
	##################
	my ($sth) = &Do_SQL("SELECT IF(Amount = Paid,1,0) FROM sl_bills INNER JOIN 
						(
							SELECT $id_bills AS ID_bills, SUM(AmountPaid) AS Paid
							FROM `sl_banks_movrel` WHERE tablename =  'bills'
							AND ($modquery `tableid` = '$id_bills')
						)tmp USING (ID_bills);");
	my ($bill_paid) = $sth->fetchrow();

	
	if($bill_paid){

		#DELETE FROM `sl_movements` WHERE `ID_tableused` = 2374 AND `tableused` = 'sl_bills'# MySQL returned an empty result set (i.e. zero rows).

		##########
		########## 2.1) Buscamos la cuenta utilizada
		##########
		my ($sth2) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills' AND ID_accounts IN($ida_vendor) AND Credebit = 'Credit' AND Status = 'Active' ORDER BY EffDate LIMIT 1;");
		my ($this_ida_vendor) = $sth2->fetchrow();

		##########
		########## 3) Monto completo. Buscamos perdida o ganancia
		##########	
		my ($sth) = &Do_SQL("SELECT 
							SUM(IF(ID_accounts = '$this_ida_vendor' AND Credebit = 'Debit',Amount,0)) AS Debits,
							SUM(IF(ID_accounts = '$this_ida_vendor' AND Credebit = 'Credit',Amount,0)) AS Credits
							FROM sl_movements WHERE ID_tableused = '$id_bills' AND tableused = 'sl_bills'
							AND Status = 'Active';");
		my ($debits,$credits) = $sth->fetchrow();

		my $amount = abs(round($debits - $credits,2));
		if($debits > $credits){
			##########
			########## 3.1) Perdida Cambiaria
			##########
			&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($ida_lost,'".$amount."', '', CURDATE(), 'sl_bills', '$id_bills', 'Pagos', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($this_ida_vendor,'".$amount."', '', CURDATE(), 'sl_bills', '$id_bills', 'Pagos', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

		}elsif($debits < $credits) {
			##########
			########## 3.2) Ganancia Cambiaria
			##########
			&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($this_ida_vendor,'".$amount."', '', CURDATE(), 'sl_bills', '$id_bills', 'Pagos', 'Debit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");			
			&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,Status,Date,Time  ,ID_admin_users )
			VALUES ($ida_profit,'".$amount."', '', CURDATE(), 'sl_bills', '$id_bills', 'Pagos', 'Credit','Active',CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");

		}

	}

	return;
}



#############################################################################
#############################################################################
#   Function: shipping_tax_holding
#
#       Es: Funcion especial para retencion de IVA en Pagos de Fletes
#       En: 
#
#
#    Created on: 2013-06-01
#
#    Author: _RB_
#
#    Modifications:
#
#
#   Parameters:
#
#       - id_bills: ID_bills
#		- id_debit: ID_movements
#		- id_credit: ID_movements
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#      <bills_expenses_record>
#
sub shipping_tax_holding {
#############################################################################
#############################################################################

	my ($id_debit, $id_credit, @param_data) = @_;

	$id_debit = int(id_debit);
	$id_credit = int($id_credit);

	my $id_bills = int($param_data[0]);
	my $id_segments = int($param_data[1]);
	my $deductible = &filter_values($param_data[2]);
	my $id_accounts = int($param_data[3]);
	my $amount = &filter_values($param_data[4]);
	my $exchange_rate = &filter_values($param_data[5]);
	my $category = int($param_data[6]);
	my $ida_vendor = int($param_data[7]);
	my ($ida_holding, $id_accounts_holding, $pct_holding, $fn_holding) = split( /:/, &filter_values($param_data[8]) );	$ida_holding = int($ida_holding);
	$ida_accounts_holding = int($ida_accounts_holding);

	my $type = $category == 2 ? 'Foreign' : 'Local';
	$exchange_rate = 1 if (!$exchange_rate or $exchange_rate == 0);
	$amount *= $exchange_rate;
	(lc($deductible) eq 'yes') and ($deductible = 'deductible');

	my $amount_holding = round($amount * $pct_holding / 100,3);

	#######
	####### Credit
	#######
	my ($sthc) = &Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused ,Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users )
						VALUES ($id_accounts_holding, $amount_holding, '$deductible', CURDATE(), 'sl_bills', $id_bills, 'Gastos', 'Credit', '$id_segments', 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
	my ($idm_credit) = $sthc->{'mysql_insertid'};

	#######
	####### Vendor Decrement
	#######
	my ($sthp) = &Do_SQL("UPDATE sl_movements SET Amount = Amount - $amount_holding WHERE ID_movements = '$id_credit' AND tableused = 'sl_bills' AND ID_tableused = '$id_bills';");

	return;
}

#############################################################################
#############################################################################
#   Function: bills_expenses_record
#
#       Es: Elimina o reversa la contabilidad de un Bill
#       En: Eliminates or accounting reverses of a Bill
#
#
#    Created on: 2013-07-09 
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_bills: ID_bills
#      
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub bills_to_void {
#############################################################################
#############################################################################

	my ($id_bills) = @_;
	my $id_vendors = &load_name('sl_bills','ID_bills',$id_bills,'ID_vendors');
	my $status = &load_name('sl_bills','ID_bills',$id_bills,'Status');

	if ($status eq 'Partly Paid' or $status eq 'Paid'){

	}elsif($status eq 'Pending' or $status eq 'Processed'){
		my ($sth) = &Do_SQL("SELECT ID_movements, ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ID_segments, ID_journalentries, Status, Date, Time, ID_admin_users
			FROM sl_movements WHERE tableused='sl_bills' AND ID_tableused='$id_bills';");
		while (my $rec = $sth->fetchrow_hashref){
			if ($rec->{'ID_journalentries'} > 0){

				if ($rec->{'Credebit'} eq 'Credit'){
					# Debit required for reverse
					my ($sthd) = &Do_SQL("INSERT INTO sl_movements SET
						ID_accounts='".$rec->{'ID_accounts'}."'
						, Amount='".$rec->{'Amount'}."'
						, Reference='".$rec->{'Reference'}."'
						, EffDate='".$rec->{'EffDate'}."'
						, tableused='".$rec->{'tableused'}."'
						, ID_tableused='".$rec->{'ID_tableused'}."'
						, Category='".$rec->{'Category'}."'
						, Credebit='Debit'
						, ID_segments='".$rec->{'ID_segments'}."'
						, ID_journalentries=NULL
						, Status=Active
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users='$usr{'id_admin_users'}';");
					my ($idm_debit) = $sthd->{'mysql_insertid'};
				}elsif ($rec->{'Credebit'} eq 'Debit'){
					# Credit required for reverse
					my ($sthd) = &Do_SQL("INSERT INTO sl_movements SET
						ID_accounts='".$rec->{'ID_accounts'}."'
						, Amount='".$rec->{'Amount'}."'
						, Reference='".$rec->{'Reference'}."'
						, EffDate='".$rec->{'EffDate'}."'
						, tableused='".$rec->{'tableused'}."'
						, ID_tableused='".$rec->{'ID_tableused'}."'
						, Category='".$rec->{'Category'}."'
						, Credebit='Credit'
						, ID_segments='".$rec->{'ID_segments'}."'
						, ID_journalentries=NULL
						, Status=Active
						, Date=CURDATE()
						, Time=CURTIME()
						, ID_admin_users='$usr{'id_admin_users'}';");
					my ($idm_credit) = $sthc->{'mysql_insertid'};
				}
			}else{
				# Delete records
				my ($sthd) = &Do_SQL("DELETE FROM sl_movements WHERE ID_movements='".$rec->{'ID_movements'}."' LIMIT 1;");
			}
		}
	}

	return;
}

#############################################################################
#############################################################################
#   Function: get_intl_exchange
#
#       Es: Aplica la conversión de tipo de cambio, si la orden lo amerita
#
#
#    Created on: 2014-03-10 
#
#    Author: Ivan Miranda
#
#    Modifications:
#
#
#   Parameters:
#     
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub get_intl_exchange {
#############################################################################
#############################################################################
#$pd_order,$sale,$service,$discount,$shipping,$tax
	my (@param_data) = @_;
	my ($pd_order) = $param_data[0];
	my ($currency) = $param_data[1];

	#&cgierr("select exchange_rate from sl_exchangerates where date_exchange_rate='$pd_order' and currency = '$currency';");
	my ($sth) = &Do_SQL("select exchange_rate from sl_exchangerates where date_exchange_rate='$pd_order' and currency = '$currency';");
	my ($exchange_rate) = $sth->fetchrow();
	$exchange_rate = int($exchange_rate) == 0 ? 1 : $exchange_rate;
	#&cgierr($exchange_rate);
	return $exchange_rate;
}


#############################################################################
#############################################################################
#   Function: accounting_po_adj_process
#
#       Es: Modifica la contabilidad correspondiente a los gastos de aterrizaje 
#			de un proveedor para ligarlo con el Bill
#
#    Created on: 2015-04-14
#
#    Author: ISC Gilberto Quirino
#
#    Modifications:
#
#
#   Parameters:
#     
#
#  Returns:
#
#      - None
#
#   See Also:
#
#
sub accounting_po_adj_process {
#############################################################################
#############################################################################
	my (@param_data) = @_;

	### Pasados por funcion	
	my $id_bills = int($param_data[0]);	
	### Pasados por parámetro 	
	my $ida_variation = &filter_values($param_data[1]);
	my $ida_vendor = &filter_values($param_data[2]);
	my $id_vendors = 0;

	my $qMov = "SELECT DISTINCT 
					sl_movements.ID_movements
					, sl_movements.ID_tablerelated 
					, sl_movements.Reference
					, sl_purchaseorders_adj.ID_vendors
				FROM 
					sl_purchaseorders_adj
					INNER JOIN sl_bills_pos ON sl_purchaseorders_adj.ID_purchaseorders_adj = sl_bills_pos.ID_purchaseorders_adj					
					INNER JOIN sl_movements ON sl_purchaseorders_adj.ID_purchaseorders = sl_movements.ID_tableused
				WHERE 
				  	sl_bills_pos.ID_bills = $id_bills	
					AND sl_movements.ID_tableused = sl_purchaseorders_adj.ID_purchaseorders 
					AND sl_movements.tableused = 'sl_purchaseorders' 
					AND sl_movements.ID_tablerelated = sl_purchaseorders_adj.ID_wreceipts 
					AND sl_movements.tablerelated = 'sl_wreceipts' 
					AND (sl_movements.Reference LIKE CONCAT('Vendor GA: ', sl_purchaseorders_adj.ID_vendors, '%') OR sl_movements.Reference LIKE CONCAT('Vendor: ', sl_purchaseorders_adj.ID_vendors, '%'))
					AND sl_movements.`Status`='Active';";
	$sthMov = &Do_SQL($qMov);
	
	### Se obtienen los ID_purchaseorders_adj relacionados con el Bill actual
 	my $sql_ids_adj = "SELECT GROUP_CONCAT(ID_purchaseorders_adj SEPARATOR '|') FROM sl_bills_pos WHERE ID_bills = ".$id_bills.";";
 	my $sth_ids_adj = &Do_SQL($sql_ids_adj);
 	my $ids_po_adj = $sth_ids_adj->fetchrow();

	my @id_movs;
	while ( $recMov = $sthMov->fetchrow_hashref ) {
		my $this_id_po_adj = 0;
 		my $this_match = 0;
 
 		### Se extrae el ID_purchaseorders_adj del campo Reference
 		my @this_aref = split(/\|/, $recMov->{'Reference'});
 		### Se valida que la contabilidad sea del GA correspondiente
 		if( $this_aref[1] ){
 			$this_id_po_adj = substr($this_aref[1], 3);
 
 			$this_match = 1 if( $this_id_po_adj =~ /$ids_po_adj/ );
 		} elsif( $recMov->{'Reference'} !~ /\|/ ) {
 			$this_match = 1;
 		}
 
 		if( $this_match == 1 ){
		 	&Do_SQL("UPDATE sl_movements
		 			 SET 
		 			 	tablerelated = 'sl_bills',
		 			 	ID_tablerelated = $id_bills, 
		 			 	Reference = CONCAT(Reference, ' - WReceipts: ',".$recMov->{'ID_tablerelated'}.")
		 			 WHERE
		 			 	ID_movements = ".$recMov->{'ID_movements'}.";");
		 	push(@id_movs, $recMov->{'ID_movements'});
		}

		$id_vendors = $recMov->{'ID_vendors'} if( !$id_vendors );
	}
	
	###--------------------------------------------------------
	### Procesa la variacion en costos
	###--------------------------------------------------------
	my $ids_movs = join(',', @id_movs);

	if( $ids_movs ){
		### Se obtiene la cuenta contable del proveedor del GA
		my $this_ida_vendor = &load_name('sl_vendors', 'ID_vendors', $id_vendors, 'ID_accounts_credit');
		$ida_vendor = $this_ida_vendor if( int($this_ida_vendor) > 0 );

		### Se obtiene el monto total de la contabilidad ligada a este bill-adj
		my $sth = &Do_SQL("SELECT ID_tableused, /*SUM(IF(Credebit='Debit', Amount, 0)) TotalDebit,*/ SUM(IF(Credebit='Credit', Amount, 0)) TotalCredit
							FROM sl_movements 
							WHERE ID_movements IN($ids_movs) AND ID_accounts = ".$ida_vendor.";");
		my ($id_po, $amount_bill_movs) = $sth->fetchrow_array();

		### Se obtiene el monto total del bill
		my $sth = &Do_SQL("SELECT SUM(Amount) FROM sl_bills_pos WHERE ID_bills=$id_bills;");
		my ($amount_bill) = $sth->fetchrow_array();

		### Se obtiene el Currency del Vendor del Bill
		my $curr_vendor = &load_db_names('sl_bills','ID_bills',$id_bills,'[Currency]');

		my $amount_adj_bill = 0;
		if( $curr_vendor eq 'US$' ){
			## Se obtiene el tipo de cambio de la recepcion
			my $sth = &Do_SQL("SELECT ex.exchange_rate
								FROM sl_exchangerates ex
									INNER JOIN sl_wreceipts wr ON ex.ID_exchangerates=wr.ID_exchangerates
									INNER JOIN sl_purchaseorders_adj po_adj ON wr.ID_purchaseorders=po_adj.ID_purchaseorders
									INNER JOIN sl_bills_pos bp ON po_adj.ID_purchaseorders_adj=bp.ID_purchaseorders_adj
								WHERE bp.ID_bills=$id_bills
								LIMIT 1;");
			my ($exchange_rate) = $sth->fetchrow_array();

			### Se hace la conversión
			$amount_adj_bill = round($amount_bill * $exchange_rate, 2);
		}else{
			$amount_adj_bill = round($amount_bill, 2);
		}
		
		### Si existe variación en costo estimado
		if( $amount_adj_bill > $amount_bill_movs ){
			my $amount_var = $amount_adj_bill - $amount_bill_movs;

			if( !$ida_vendor ){
				### Se obtien el ID_accounts del Credit
				$sth = &Do_SQL("SELECT ID_accounts
								FROM sl_movements
								WHERE ID_movements IN($ids_movs) And Credebit='Credit' 
								LIMIT 1;");
				$ida_vendor = $sth->fetchrow_array();
			}

			&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, Status, Date, Time, ID_admin_users )
					 VALUES ($ida_variation, $amount_var, 'VCE', CURDATE(), 'sl_purchaseorders', '$id_po', 'sl_bills', $id_bills, 'Compras', 'Debit','Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
			&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, tablerelated, ID_tablerelated, Category, Credebit, Status, Date, Time, ID_admin_users )
					 VALUES ($ida_vendor, $amount_var, 'VCE', CURDATE(), 'sl_purchaseorders', '$id_po', 'sl_bills', $id_bills, 'Compras', 'Credit','Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		}
	}
	###--------------------------------------------------------
}


#############################################################################
#############################################################################
#   Function: accounting_customer_deposit 
#
#       Es: Genera movimientos contables derivados de anticipos de dinero para una orden(customers_advances).
#       En: 
#
#
#    Created on: 03/15/2015
#
#    Author: 
#
#    Modifications:
#
#        - 
#
#
#   Parameters:
#
#      - param_data: id_customers_advances, id_banks, id_banks_movements , amount, exchange_rate
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub accounting_customer_deposit {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $id_customers_advances = int($param_data[0]);
	my $id_banks = int($param_data[1]);
	my $id_banks_movements = int($param_data[2]);
	my $amount = round($param_data[3],3);
	my $exchange_rate = round($param_data[4],4);
	$amount = round($amount * $exchange_rate,3);
	$in{'ida_banks'} = $id_banks;

	## How to update
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0|;

	$category = 'Anticipo Clientes';
	$keypoint = 'Customer Advances';

	&general_deposits($id_banks_movements,$id_customers_advances,'customers_advances',$keypoint,$category,'','','CURDATE',$amount);
	### Se guarda el ID_orders_payments
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_banks_movements', ID_tablerelated = '". $id_banks_movements ."' WHERE ID_tableused = '". $id_customers_advances ."' AND tableused = 'sl_customers_advances' AND Status = 'Active' AND Category = '". $category ."' AND ". $sqlmod_update_records .";");

	return;
}


#############################################################################
#############################################################################
#   Function: accounting_customer_deposit_apply 
#
#       Es: Genera movimientos contables derivados de aplicacion de anticipos de clientes a una orden
#       En: 
#
#
#    Created on: 03/24/2016
#
#    Author: 
#
#    Modifications:
#
#        - 
#
#
#   Parameters:
#
#      - param_data: id_customers_advances, id_banks, id_banks_movements , amount, exchange_rate
#
#
#  Returns: 1074, 1078 | 1405 | 1398
#
#      - 
#
#   See Also: 
#
#
sub accounting_customer_deposit_apply {
#############################################################################
#############################################################################

	my (@param_data) = @_;

	my $this_acc = 0; my $this_acc_str = 'OK'; my $flag_exchange_rate = 0;
	### Pasados por funcion
	my $id_customers_advances = int($param_data[0]);
	my $id_orders = int($param_data[1]);
	my $id_payments = int($param_data[2]);
	my $amount = round($param_data[3],3);
	my $exchange_rate_customer_advance = round($param_data[4],4);
	my $exchange_rate_order = round($param_data[5],4);
	### Pasados por parametro
	my $ida_taxes = &filter_values($param_data[6]);
	my $ida_customer = &filter_values($param_data[7]);
	my $ida_profit = int($param_data[8]);
	my $ida_lost = int($param_data[9]);

	my $amount_now = round($amount * $exchange_rate_customer_advance,2);
	my $amount_then = round($amount * $exchange_rate_order,2);
	$amount = $amount_now;

	my $str_params = join("\n", @param_data);
	#&cgierr($str_params);
	
	## How to update
	my $md5time_field_exists = $va{'md5verification_exists'};
	my $md5time_field = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5Verification,| : '';
	my $md5time_value = ($md5time_field_exists and $va{'this_accounting_time'}) ? qq|MD5('|. $va{'this_accounting_time'} .qq|'),| : '';	
	my $sqlmod_update_records = ($va{'md5verification_exists'} and $va{'this_accounting_time'}) ?
								qq|MD5Verification = MD5('|. $va{'this_accounting_time'} .qq|')| :
								qq|TIMESTAMPDIFF(MINUTE,CONCAT(Date,' ',Time) , NOW()) = 0|;

	$category = 'Cobranza';
	$keypoint = 'Customer Advances Apply';

	## 1) Search  Customer Account
	my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Category = 'Ventas' AND Credebit = 'Debit' AND Status = 'Active' ORDER BY Amount DESC LIMIT 1;");
	my ($this_ida_customers) = $sth->fetchrow();

	## 2) Search Customer Advance Account
	my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_movements WHERE ID_tableused = '". $id_customers_advances ."' AND tableused = 'sl_customers_advances' AND Category = 'Anticipo Clientes' AND Credebit = 'Credit' AND Status = 'Active' ORDER BY Amount DESC LIMIT 1;");
	my ($this_ida_customers_advances) = $sth->fetchrow();

	## 3) Accounts Error?
	return (1, "Accounts Not Found: $this_ida_customers vs $this_ida_customers_advances") if (!$this_ida_customers or !$this_ida_customers_advances);

	## 4.1) Debit
	&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time, ID_admin_users )
			VALUES (". $this_ida_customers_advances .", ". $amount .", 'IDP-". $id_payments ."', CURDATE(), 'sl_orders', '". $id_orders ."', '". $category ."', 'Debit', ". $md5time_value ." 'Active',CURDATE(), CURTIME(), '". $usr{'id_admin_users'} ."');");

	## 4.2) Credit
	&Do_SQL("INSERT INTO sl_movements (ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time, ID_admin_users )
			VALUES (". $this_ida_customers .", ". $amount .", 'IDP-". $id_payments ."', CURDATE(), 'sl_orders', '". $id_orders ."', '". $category ."', 'Credit', ". $md5time_value ." 'Active',CURDATE(), CURTIME(), '". $usr{'id_admin_users'} ."');");

	## 4.3) Tax
	&order_deposit_separate_tax($id_orders,$id_payments,'Cobranza',$ida_taxes);


	## 5) Exchange Rate difference
	my $amount_difference = round($amount_now - $amount_then,2);
	$flag_exchange_rate = 1 if $amount_difference;
	
	if($amount_difference > 0){

		###
		### 2.4.1) Ejecutamos Ganancia
		###
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time  ,ID_admin_users )
				VALUES (". $ida_profit .",". abs($amount_difference) .", '', CURDATE(), 'sl_orders', ". $id_orders .", '". $category ."', 'Credit', ". $md5time_value ." 'Active',CURDATE(), CURTIME(), '". $usr{'id_admin_users'} ."');");
		sleep(1);
		&Do_SQL("UPDATE sl_movements SET Amount = Amount - ".abs($amount_difference)." WHERE tableused='sl_orders' AND ID_tableused=". $id_orders ." AND Category='". $category ."' AND ID_accounts IN(". $ida_customer .") AND Credebit = 'Credit' AND Status = 'Active' AND ". $sqlmod_update_records .";");

	}elsif($amount_difference < 0){

		###
		### 2.4.2) Ejecutamos Perdida
		###
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ". $md5time_field ." Status, Date, Time, ID_admin_users )
				VALUES (". $ida_lost .",". abs($amount_difference) .", '', CURDATE(), 'sl_orders', ". $id_orders .", '". $category ."', 'Debit', ". $md5time_value ." 'Active',CURDATE(), CURTIME(), '". $usr{'id_admin_users'} ."');");
		sleep(1);
		&Do_SQL("UPDATE sl_movements SET Amount = Amount + ". abs($amount_difference) ." WHERE tableused = 'sl_orders' AND ID_tableused = ". $id_orders ." AND Category = '". $category ."' AND ID_accounts IN (". $ida_customer .") AND Credebit = 'Credit' And Status = 'Active' AND ". $sqlmod_update_records .";");
		
	}


	## 6) tablerelated
	&Do_SQL("UPDATE sl_movements SET tablerelated = 'sl_customers_advances', ID_tablerelated = '". $id_customers_advances ."' WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status = 'Active' AND Category = '". $category ."' AND ". $sqlmod_update_records .";");


	## 7) Final Validation
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_movements WHERE ID_tableused = '". $id_orders ."' AND tableused = 'sl_orders' AND Status = 'Active' AND Category = '". $category ."' AND ". $sqlmod_update_records .";");
	my ($total_records) = $sth->fetchrow();

	if($flag_exchange_rate and $total_records < 3){

		## 7.1) Exchange Rate Win/Lose Failed
		$this_acc = 1;
		$this_acc_str = &trans_txt('acc_winlose');

	}elsif($total_records < 2){

		## 7.2) General Records Failed
		$this_acc = 1;
		$this_acc_str = &trans_txt('acc_general');

	}

	return ($this_acc, $this_acc_str);
}


#############################################################################
#############################################################################
#   Function: accounting_customers_apply_balance 
#
#       Es: Genera movimientos para ajuste por perdida de efectivo en entregas COD
#       En: 
#
#
#    Created on: 30/06/2016
#
#    Author: 
#
#    Modifications:
#
#        - 
#
#
#   Parameters:
#
#      - param_data: $id_customer_account,$id_bank_account,$amount,$id_orders,$id_banks_movements
#
#
#  Returns: 
#
#      - 
#
#   See Also: 
#


sub accounting_customers_apply_balance{
	# use Data::Dumper;
	# cgierr(Dumper \%@_);
	my ($id_customer_account,$id_bank_account,$amount,$id_orders,$id_banks_movements) = @_;
	my $sthMovement='';

	$sthMovement=&Do_SQL('INSERT INTO sl_movements
						      SET
						      ID_accounts='.$id_customer_account.',
						      Amount='.$amount.',
						      EffDate=CURDATE(),
						      tableused="sl_orders",
						      ID_tableused='.$id_orders.',
						      tablerelated="sl_banks_movements",
						      ID_tablerelated='.$id_banks_movements.',
						      Category="Cobranza",
						      Credebit="Credit",
						      Date=CURDATE(), Time=CURTIME(), ID_admin_users='.$usr{'id_admin_users'});
	
	$va{'id_movements'} = $sthMovement->{'mysql_insertid'};	

	$sthMovement=&Do_SQL('INSERT INTO sl_movements
						      SET
						      ID_accounts='.$id_bank_account.',
						      Amount='.$amount.',
						      EffDate=CURDATE(),
						      tableused="sl_orders",
						      ID_tableused='.$id_orders.',
						      tablerelated="sl_banks_movements",
						      ID_tablerelated='.$id_banks_movements.',
						      Category="Cobranza",
						      Credebit="Debit",
						      Date=CURDATE(), Time=CURTIME(), ID_admin_users='.$usr{'id_admin_users'});

}



1;
