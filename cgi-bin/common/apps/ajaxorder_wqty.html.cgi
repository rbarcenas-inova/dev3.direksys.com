#!/usr/bin/perl

sub editing_order{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/18/08 12:27:06
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/19/08 11:27:23
# Last Modified by: MCC C. Gabriel Varela S: Se agrega parte de payments y se modifica la de productos
# Last Modified on: 11/20/08 09:00:29
# Last Modified by: MCC C. Gabriel Varela S: 
#		-Se implementan tablas temporales. 
#		-Se filtra por status de órdenes y pagos.
#		-Se incluyen acciones para pagos
# Last Modified on: 11/21/08 13:38:31
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a check_pretotals. Se corrige campo status de $cadtbpaymentstmp
#	&Do_SQL("drop table if exists $cadtbproductstmp;");
#	&Do_SQL("drop table if exists $cadtbpaymentstmp;");
# Last Modified on: 11/26/08 10:26:45
# Last Modified by: MCC C. Gabriel Varela S: Dependiendo del valor de in_finish se procesará o no la edición.
# Last Modified on: 12/05/08 10:57:28
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar primero a UPDATE_updatables.
# Last Modified on: 01/05/09 16:17:06
# Last Modified on: 03/18/09 18:03:50
# Last Modified by: MCC C. Gabriel Varela S: Se habilita que cuando se finalice la edición, se borren los registros. Y también todos los registros previos para ese usuario.
# Last Modified RB: 04/06/09  16:22:38 -- Se hace dinamico el prefijo opr_
# Last Modified on: 05/01/09 11:03:06
# Last Modified by: MCC C. Gabriel Varela S: Se cambia if relacionado con check_pretotals e in edit_finished
# Last Time Modified by RB on 04/15/2011 12:56:37 PM: Se agrega id_orders como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:18:08 PM : Se agrega City como parametro para calculate_taxes

#Last modified on 30 Jun 2011 16:06:05
#Last modified by: MCC C. Gabriel Varela S. :Function verify_credits_vs_debits is called


	print "Content-type: text/html\n\n";

	if(&check_permissions('edit_order_wholesale_ajaxmode','','')) {
		
		my $tot_ord,$tot_pay;
		my $cmdret = '';
		my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
		my $hasbothpayments=0;
		
		&Do_SQL("DELETE FROM sl_orders_paymentstmp WHERE ID_orders<>$in{$cadidorders} AND ID_admin_users=$usr{'id_admin_users'}");
		&Do_SQL("DELETE FROM sl_orders_productstmp WHERE ID_orders<>$in{$cadidorders} AND ID_admin_users=$usr{'id_admin_users'}");
		
		if(!&is_adm_order($in{$cadidorders})or 1) {

			&UPDATE_updatables();
			$hasbothpayments=&verify_credits_vs_debits();
			my $checkPretotalsBU=&check_pretotals;
			
			if(($in{'finish'} or $in{'edit_finished'}) and &check_pretotals==0 and ($hasbothpayments==0 or $in{'bothmovements_checkbox'} eq 'Yes')) {
				$cmdret ='opr_';
				&process_edition;
				$in{'dototemp'}="NO";
				$va{'javascriptvar'}="<script type='text/javascript'>
										//<![CDATA[
											onload = function(){
												top.location.href='[in_path]?cmd=".$cmdret."$in{'edit_type'}orders&view=$in{$cadidorders}&edit_finished=1#tabsl';
											}
										//]]>
										</script>";
				
			}else{
				#it verifies if there are both kind of editable payments
				if($hasbothpayments == 1){
					$va{'bothmovements_checkbox'}="<input type='checkbox' name='bothmovements_checkbox' value='Yes' class='checkbox'> I want to leave both credits and debits payments in the order";
				}else{
					$va{'bothmovements_checkbox'}='';
				}
				#cgierr("$hasbothpayments jiji".$va{'bothmovements_checkbox'});
				#$va{'script_url'}= $cfg{'pathcgi_ajaxorder_wqty'};
		
				#Se crea tabla temporal
				&Do_SQL("CREATE /*temporary*/ TABLE IF NOT EXISTS $cadtbproductstmp ($cadidorderproducts int(6),ID_products int(6),$cadidorders int(6),Related_ID_products int(6),Quantity int(2),SalePrice decimal(6,2),Shipping decimal(6,2),Tax decimal(6,3),Discount decimal(6,2),FP int(2),ShpDate date,Status enum('Active', 'Exchange', 'Returned', 'Undeliverable', 'Order Cancelled', 'Inactive', 'Lost', 'ReShip'),ID_admin_users varchar(6),Action enum('Original','Edited','Created'),comefrom enum('Original','Add','Dupl','Return','Drop'),returnid int(6));");
				&Do_SQL("CREATE /*temporary*/ TABLE IF NOT EXISTS $cadtbpaymentstmp ($cadidorderpayments int(6),$cadidorders int(6),Type enum('Credit-Card', 'Check', 'WesternUnion', 'Money Order', 'Flexipago'),PmtField1 varchar(60),PmtField2 varchar(30),PmtField3 varchar(30),PmtField4 varchar(30),PmtField5 varchar(20),PmtField6 varchar(30),PmtField7 varchar(30),PmtField8 varchar(30),PmtField9 varchar(10),Amount decimal(6,2),Reason enum('Sale', 'Refund', 'Exchange', 'Reship', 'Other'),Paymentdate date,AuthCode varchar(10),AuthDateTime varchar(30),Captured enum('Yes', 'No'),CapDate date,Status enum('Approved', 'Financed', 'Denied', 'Pending', 'Insufficient Funds', 'Credit', 'Credit by Monterey', 'ChargeBack', 'Counter Finance', 'Void', 'On Collection', 'Claim', 'Order Cancelled', 'Cancelled'),ID_admin_users int(6),Action enum('Original','Edited','Created'),comefrom enum('Original','Add','Dupl','Return','Drop'));");
				
				if($in{'dototemp'}eq"YES") {
					#Se borran los registros de la orden con el usuario en la temporal
					&Do_SQL("DELETE FROM $cadtbproductstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'};");
					&Do_SQL("DELETE FROM $cadtbpaymentstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'};");
					#Se pasan los registros de la orden a las temporales

					my ($tmp_sth) = &Do_SQL("SELECT $cadidorderproducts,ID_products,$cadidorders,Related_ID_products,Quantity,SalePrice/Quantity,SalePrice,Shipping,Tax,Tax_percent,Discount,FP,ShpDate,Status from $cadtbproducts where $cadidorders=$in{$cadidorders} ORDER BY $cadidorderproducts DESC;");
					while( my( $tmp_cadidorderproducts, $tmp_id_products, $tmp_cadidorders, $tmp_related_id_products, $tmp_quantity, $tmp_salePrice_qty, $tmp_salePrice, $tmp_shipping, $tmp_tax, $tmp_tax_percent, $tmp_discount, $tmp_fp, $tmp_shpdate, $tmp_status ) = $tmp_sth->fetchrow_array() )
					{
						&Do_SQL("INSERT INTO $cadtbproductstmp ($cadidorderproducts,ID_products,$cadidorders,Related_ID_products,Quantity,UnitPrice,SalePrice,Shipping,Tax,Tax_percent,Discount,FP,ShpDate,Status,ID_admin_users,Action,comefrom)
										VALUES( '$tmp_cadidorderproducts','$tmp_id_products','$tmp_cadidorders','$tmp_related_id_products','$tmp_quantity','$tmp_salePrice_qty','$tmp_salePrice','$tmp_shipping','$tmp_tax','$tmp_tax_percent','$tmp_discount','$tmp_fp','$tmp_shpdate','$tmp_status',$usr{'id_admin_users'},'Original','Original' );");
					}

				  	my ($tmp_sth) =  &Do_SQL("SELECT $cadidorderpayments,$cadidorders,Type,PmtField1,PmtField2,PmtField3,PmtField4,PmtField5,PmtField6,PmtField7,PmtField8,PmtField9,Amount,Reason,Paymentdate,AuthCode,AuthDateTime,Captured,CapDate,Status from $cadtbpayments where $cadidorders=$in{$cadidorders} ORDER BY $cadidorderpayments DESC;");
				  	while( my($tmp_cadidorderpayments,$tmp_cadidorders,$tmp_type,$tmp_pmtfield1,$tmp_pmtfield2,$tmp_pmtfield3,$tmp_pmtfield4,$tmp_pmtfield5,$tmp_pmtfield6,$tmp_pmtfield7,$tmp_pmtfield8,$tmp_pmtfield9,$tmp_amount,$tmp_reason,$tmp_paymentdate,$tmp_authcode,$tmp_authdatetime,$tmp_captured,$tmp_capdate,$tmp_status) = $tmp_sth->fetchrow_array() )
				  	{
				  		&Do_SQL("INSERT INTO $cadtbpaymentstmp ($cadidorderpayments,$cadidorders,Type,PmtField1,PmtField2,PmtField3,PmtField4,PmtField5,PmtField6,PmtField7,PmtField8,PmtField9,Amount,Reason,Paymentdate,AuthCode,AuthDateTime,Captured,CapDate,Status,ID_admin_users,Action,comefrom)
										VALUES ( $tmp_cadidorderpayments,$tmp_cadidorders,$tmp_type,$tmp_pmtfield1,$tmp_pmtfield2,$tmp_pmtfield3,$tmp_pmtfield4,$tmp_pmtfield5,$tmp_pmtfield6,$tmp_pmtfield7,$tmp_pmtfield8,$tmp_pmtfield9,$tmp_amount,$tmp_reason,$tmp_paymentdate,$tmp_authcode,$tmp_authdatetime, $tmp_captured, $tmp_capdate, $tmp_status, $usr{'id_admin_users'},'Original','Original' );");
					}

					#$in{'taxesapp'}=&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'OrderTax');
					$in{'taxesapp'}=&calculate_taxes(&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_Zip'),&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_State'),&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_City'),$in{$cadidorders});
				
				}else{
					#&taxes_actions();
				}
				
				if($in{'taxesapp'}!=0){
					#$va{'taxes'}=qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&taxesaction=off&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Inactivate Taxes' alt='' border='0'></a>|;
					$va{'taxeson'}="checked='checked'";
					$va{'taxesoff'}="";
				
				}else{
					#$va{'taxes'}=qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&taxesaction=on&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate Taxes' alt='' border='0'></a>|;
					$va{'taxesoff'}="checked='checked'";
					$va{'taxeson'}="";
				}
				
				if($in{'taxesaction'} eq 'off'){
					$va{'taxesoff'}="checked='checked'";
					$va{'taxeson'}="";
				}else{
					$va{'taxeson'}="checked='checked'";
					$va{'taxesoff'}="";	
				}
				
				if($va{'bandedition'}==1){
					&adjust_edition();
				}
				
				&payments_actions();
				&products_actions();
				$tot_ord=&show_products();
				$tot_pay=&show_payments();
				#$check_pretot=&check_pretotals;
				$check_pretot=$checkPretotalsBU;
				#&adjust_edition() if($check_pretot!=0);
				$check_pretot=round($check_pretot,2);
				$va{'diff'}=&format_price($check_pretot);
				
				if($check_pretot!=0 or $in{'dototemp'}eq"YES") {
					#$va{'btntxt'}="Calcular";
					$va{'finish'}="0";
					$va{'script_url'}= $cfg{'pathcgi_ajaxorder_wqty'};
					$va{'cmdtoapply'}="editing_order";
					$va{'btntxt'}="<input id='btnact' type='submit' align='center' value='Calcular' class='button'>";
				
				}else{
					#$va{'btntxt'}="Finalizar";
					$va{'finish'}="1";
			#		$va{'script_url'}= $in{'path'};
			#		$va{'cmdtoapply'}="opr_orders";
					#$va{'btntxt'}="<input type='button' align='center' value='Finalizar' class='button' onclick='top.location.href=\"$in{'path'}?cmd=opr_orders&view=$in{$cadidorders}&edit_finished=1#tabsl\"'>";
					$va{'script_url'}= $cfg{'pathcgi_ajaxorder_wqty'};
					$va{'cmdtoapply'}="editing_order";
					$va{'btntxt'}="<input id='btnact' type='submit' align='center' value='Finalizar' class='button'>";
				}
			}

			$va{'req'} = &trans_txt('required');
			$va{'view'}="<input type='hidden' name='view' value='$in{$cadidorders}'>";
			print &build_page('editing_order_wqty.html');
		}

	}else{

		##ToDo: Pagina de no autorizado
		print &build_page('unauth_small.html');
	}
}

sub products_actions{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/20/08 17:42:22
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/21/08 12:43:20
# Last Modified by: MCC C. Gabriel Varela S: Se agrega Duplicar producto
# Last Modified on: 11/26/08 09:54:11
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si se agrega un producto debido a un return por exchange se manifieste en el campo correspondiente
# Last Modified on: 12/01/08 13:09:44
# Last Modified by: MCC C. Gabriel Varela S: Se agrega parte de returntype
# Last Modified on: 12/02/08 13:31:55
# Last Modified by: MCC C. Gabriel Varela S: Se ve todo lo de servicios asociados
# Last Modified on: 12/03/08 15:37:17
# Last Modified by: MCC C. Gabriel Varela S: Se contemplan Supply
# Last Modified on: 12/15/08 16:26:49
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el restock fee se calcule en base a un producto y no a un servicio
# Last Modified on: 02/20/09 11:50:24
# Last Modified by: MCC C. Gabriel Varela S: Se limita la eliminación al usuario que lo está editando
# Last Modified on: 09/02/09 16:45:32
# Last Modified by: MCC C. Gabriel Varela S:Se pone ID=1 cuando no existen datos previos.
	my $sth,$rec,$bandextwar=0;
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	###############################################################################################################
	######ACCIONES PARA PRODUCTOS##########################################################################
	###############################################################################################################
	
	####Eliminar/Inactivar producto####
	if($in{'droppr'}) {

		$sth = &Do_SQL("SELECT * FROM $cadtbproductstmp WHERE $cadidorderproducts='$in{'droppr'}' and ID_admin_users=$usr{'id_admin_users'}");
		$rec=$sth->fetchrow_hashref;
		if($sth->rows>0) {
			if($rec->{'Status'}ne"Inactive") {
				if($rec->{'Action'}ne"Created") {
					#Se modifica el status
					&Do_SQL("UPDATE $cadtbproductstmp set Status='Inactive',Action='Edited' where $cadidorderproducts='$in{'droppr'}' and ID_admin_users=$usr{'id_admin_users'}");
					#Se toman en cuenta servicios asociados
					&Do_SQL("UPDATE $cadtbproductstmp set Status='Inactive',Action='Edited' where Related_ID_products=$rec->{'ID_products'} and comefrom='Original' and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'}");
				}else{ #Se elimina la fila
				
					&Do_SQL("DELETE FROM $cadtbproductstmp where $cadidorderproducts='$in{'droppr'}' and ID_admin_users=$usr{'id_admin_users'}");
					#Se toman en cuenta servicios asociados
					&Do_SQL("DELETE FROM $cadtbproductstmp where Related_ID_products=$rec->{'ID_products'} and comefrom!='Original' and ID_admin_users=$usr{'id_admin_users'}");
				}
			}
		}
		&adjust_edition();
	}
	
	####Activar producto####
	if($in{'activpr'}){

		$sth = &Do_SQL("SELECT * FROM $cadtbproductstmp WHERE $cadidorderproducts='$in{'activpr'}' and ID_admin_users=$usr{'id_admin_users'}");
		$rec=$sth->fetchrow_hashref;
		
		if($sth->rows>0) {
			if($rec->{'Status'}ne"Active") {
				&Do_SQL("UPDATE $cadtbproductstmp set Status='Active',Action='Edited' where $cadidorderproducts='$in{'activpr'}' and ID_admin_users=$usr{'id_admin_users'}");
				#Se toman en cuenta servicios asociados
				&Do_SQL("UPDATE $cadtbproductstmp set Status='Active',Action='Edited' where Related_ID_products=$rec->{'ID_products'} and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'}");
			}
		}

		&adjust_edition();
	}
	
	####Duplicar producto####
	if($in{'duplpr'}) {
		$sth = &Do_SQL("SELECT * FROM $cadtbproductstmp WHERE $cadidorderproducts='$in{'duplpr'}' and ID_admin_users=$usr{'id_admin_users'}");
		$rec=$sth->fetchrow_hashref;
		
		if($sth->rows>0) {
			#Obtener próximo ID
			$sth = &Do_SQL("SELECT max($cadidorderproducts)+1 FROM $cadtbproductstmp");
			$lastid=$sth->fetchrow;
			$lastid=1 if(!$lastid);
			&Do_SQL("INSERT INTO $cadtbproductstmp ($cadidorderproducts,ID_products,$cadidorders,Related_ID_products,Quantity,UnitPrice,SalePrice,Shipping,Tax,Tax_percent,Discount,FP,Status,ID_admin_users,Action,comefrom)
											SELECT $lastid,ID_products,$cadidorders,Related_ID_products,Quantity,UnitPrice,SalePrice,Shipping,Tax,Tax_percent,Discount,FP,Status,$usr{'id_admin_users'},'Created','Dupl' from $cadtbproductstmp where $cadidorderproducts=$in{'duplpr'} and ID_admin_users=$usr{'id_admin_users'};");
			#Se toman en cuenta servicios asociados
#			$lastid++;
#			&Do_SQL("INSERT INTO $cadtbproductstmp ($cadidorderproducts,ID_products,$cadidorders,Related_ID_products,Quantity,UnitPrice,SalePrice,Shipping,Tax,Discount,FP,Status,ID_admin_users,Action,comefrom)
#											SELECT $lastid,ID_products,$cadidorders,Related_ID_products,Quantity,UnitPrice,SalePrice,Shipping,Tax,Discount,FP,Status,$usr{'id_admin_users'},'Created','Dupl' from $cadtbproductstmp where Related_ID_products=$rec->{'ID_products'} and ID_admin_users=$usr{'id_admin_users'} and comefrom='Original';");
			&adjust_edition();
		}
	}

	if($in{'addpr'}) {
		####Add product####
		$sth = &Do_SQL("SELECT max($cadidorderproducts)+1 FROM $cadtbproductstmp");
		$lastid=$sth->fetchrow;
		$lastid=1 if(!$lastid);
		my ($sprice,$comefrom,$returnid);

		$comefrom="Add";
		$comefrom="Return"if($in{'exchange'}ne"");
		$returnid="";
		$returnid=",returnid=$in{'exchange'}"if($in{'exchange'}ne"");
		
		if($in{'prefix'}=~/^4/) {

			if($cfg{'customers_parts_use'}) {
				$in{'id_customers'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
				my ($sth) = &Do_SQL("SELECT SPrice FROM sl_customers_parts WHERE ID_customers = '$in{'id_customers'}' AND ID_parts = '$in{'addpr'}';");
				$sprice = $sth->fetchrow();
			}else{
				$sprice = 1;
			}

			$sku_id=$in{'prefix'}+$in{'addpr'};
		
		}else{
			
			my ($sth) = &Do_SQL("SELECT SPrice FROM sl_services WHERE ID_services='$in{'addpr'}' AND Status NOT IN (/*'Hidden',*/'Inactive') AND SPrice>=0");;
			$sprice = $sth->fetchrow;
			$sku_id=600000000+$in{'addpr'};
		}
		$sprice=1 if !$sprice;
		my $id_products_to_apply=&last_id_products()."000000";

		#my ($sth) = &Do_SQL("INSERT INTO $cadtbproductstmp SET $cadidorderproducts=$lastid,ID_products='$sku_id',$cadidorders='$in{$cadidorders}',Quantity=abs($sprice)/$sprice,UnitPrice=$sprice/(abs($sprice)/$sprice),SalePrice='$sprice',Shipping=0,Tax=0,Discount=0,Status='Active',ID_admin_users='$usr{'id_admin_users'}',Action='Created',comefrom='$comefrom'$returnid");
		my ($sth) = &Do_SQL("INSERT INTO $cadtbproductstmp SET $cadidorderproducts=$lastid,ID_products='$id_products_to_apply',$cadidorders='$in{$cadidorders}',Related_ID_products='$sku_id',Quantity=abs($sprice)/$sprice,UnitPrice=$sprice/(abs($sprice)/$sprice),SalePrice=$sprice,Shipping=0,Tax=0,Tax_percent=0,Discount=0,Status='Active',ID_admin_users='$usr{'id_admin_users'}',Action='Created',comefrom='$comefrom'$returnid");
		&calc_tmp_prod_fields($lastid,1)if($in{'prefix'}=~/^4/ or $in{'prefix'}=~/^6/);
		#Se toman en cuenta servicios asociados
		&adjust_edition();
	}

}

sub show_products{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/20/08 17:46:07
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/21/08 13:38:57
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se regrese el total de la suma de precios de los productos
# Last Modified on: 11/25/08 09:32:51
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar a exists_return
# Last Modified on: 11/26/08 12:26:03
# Last Modified by: MCC C. Gabriel Varela S: Se agrega path
# Last Modified on: 12/01/08 12:45:47
# Last Modified by: MCC C. Gabriel Varela S: se agrega &returntype=$in{'returntype'}
# Last Modified on: 12/02/08 11:26:24
# Last Modified by: MCC C. Gabriel Varela S: Se agrega validación para que se muestre el ícono de return sólo si el producto ya fue enviado. Sólo se pueden duplicar los originales.
# Last Modified on: 12/05/08 13:38:54
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se puedan editar los precios también.
# Last Modified on: 01/12/09 17:14:31
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si el producto tiene un return, no se muestre la opción de return.
# Last modified on 1 Jul 2011 18:18:17
# Last modified by: MCC C. Gabriel Varela S. :$shipped is conditioned
# Last time modified by RB on 01/09/2012: Se reviso que el producto no estuviera enviado para permitir edicion de cajas de texto $locked_record
	###############################################################################################################
	####Productos##################################################################################################
	###############################################################################################################
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my $tot_ord,$totqty,$totprice,$totdis,$totshp,$tottax,$cadtoshow;
	my $producttot=0,$i=0,$d,$sku_id_p,$decor;#,$tot_ord;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $cadtbproductstmp WHERE $cadidorders='$in{$cadidorders}'  and ID_admin_users=$usr{'id_admin_users'}/*and Status in ('Active','Exchange','Returned','ReShip')*/");
	$va{'matchespr'} = $sth->fetchrow;
	if ($va{'matchespr'}>0){
		my ($sth1) = &Do_SQL("SELECT *,$cadidorderproducts,$cadidorders FROM $cadtbproductstmp WHERE $cadidorders='$in{$cadidorders}' and ID_admin_users=$usr{'id_admin_users'}/*and Status in ('Active','Exchange','Returned','ReShip')*/order by $cadidorderproducts");
		my $gvcolor,$locked_record;
		while ($col = $sth1->fetchrow_hashref){

			if($col->{'Action'} eq "Original"){
				$gvcolor="green";
			}elsif($col->{'Action'} eq "Edited"){
				$gvcolor="blue";
			}elsif($col->{'Action'} eq "Created"){
				$gvcolor="red";
			}

			$i++;
			$d = 1 - $d;
			my $flag_services=0;
			my($status,%tmp);
			if($col->{'ID_products'} < 99999 or substr($col->{'Related_ID_products'},0,1) == 6){
				$producttot=$col->{'SalePrice'};
				my ($sth5) = &Do_SQL("SELECT name FROM sl_services WHERE ID_services = right($col->{'Related_ID_products'},4) ;");
				$serdata = $sth5->fetchrow_hashref;
				$cadtoshow=$serdata->{'name'};
				$flag_services=1;
			}else{
				$producttot=($col->{'SalePrice'}-$col->{'Discount'})+$col->{'Tax'}+$col->{'Shipping'};
				$sku_id_p=$col->{'Related_ID_products'}-400000000;
				$cadtoshow=&load_name('sl_parts','ID_parts',$sku_id_p,'Name');
			}

			if ($col->{'Status'} eq 'Inactive'){
				$decor = " style=' text-decoration: line-through'";
			}else{
				$totqty +=  $col->{'Quantity'};
				$totprice += $col->{'SalePrice'};
				$totdis += $col->{'Discount'};
				$totshp += $col->{'Shiping'};
				$tottax += $col->{'Tax'};
				$tot_ord += $producttot;
				$decor ='';
			}


			$va{'searchresultspr'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresultspr'} .= "  <td class='smalltext'>";
			$va{'searchresultspr'} .= "		<input type='checkbox' class='checkbox' name='changeproducts' value='$col->{$cadidorderproducts}'>\n\n"if($cfg{'chbox_orders_edition'});
			#if((!$col->{'ShpDate'} or $col->{'ShpDate'} eq '0000-00-00') and $col->{'Status'} ne 'Inactive')
			my $shipped=0;
			if($col->{'Status'} ne 'Inactive'){

				## Record Line locked?
				if($col->{'Action'} ne 'Created') {
					my($sth)=&Do_SQL("SELECT COUNT(*) FROM sl_orders_parts WHERE ID_orders_products='$col->{'ID_orders_products'}';");
					$locked_record=$sth->fetchrow();
				}

				if($col->{'Action'} eq 'Original'){
					my $sthshp=&Do_SQL("SELECT if(ShpDate!='0000-00-00' and ShpDate!='' and not isnull(ShpDate) and Tracking!='' and not isnull(Tracking),1,0)as Shipped 
					from $cadtbproducts 
					where $cadidorderproducts=$col->{$cadidorderproducts}
					and $cadidorders=$col->{$cadidorders};");
					$shipped=$sthshp->fetchrow;
				}
				$va{'searchresultspr'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&droppr=$col->{$cadidorderproducts}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>|if(!$shipped);
				$va{'searchresultspr'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&duplpr=$col->{$cadidorderproducts}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/duplicate.gif' title='Duplicate' alt='' border='0'></a>|;# if($col->{'comefrom'}eq"Original");
# 				my $sthshp=&Do_SQL("SELECT if(ShpDate!='0000-00-00' and ShpDate!='' and not isnull(ShpDate) and Tracking!='' and not isnull(Tracking),1,0)as Shipped from $cadtbproducts where $cadidorderproducts=$col->{$cadidorderproducts}");
# 				my $shipped=$sthshp->fetchrow;
				if(!&return_in_order($col->{$cadidorderproducts}) and $shipped and !&exists_return and $col->{'Action'}ne"Created" and $col->{'Quantity'}>0 and !($col->{'ID_products'} < 99999 or substr($col->{'ID_products'},0,1) == 6)){
					$in{'taxesapp'}="";
					$va{'searchresultspr'} .= "&nbsp;<a href='#prdmenu$i' onMouseOver=\"popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'prdmenu$i');loadDoc('/cgi-bin/common/apps/ajaxorder_wqty?cmdo=[in_cmd]&cmd=edit_actions&$cadidorders=[in_id_orders]&$cadidorderproducts=$col->{$cadidorderproducts}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}');\"><img src='$va{'imgurl'}/$usr{'pref_style'}/return_small.gif' title='Return' alt='' border='0'></a>";
					$va{'searchresultspr'} .= "&nbsp;<a name='prdmenu$i' id='prdmenu$i'>&nbsp;</a>";
				}
			}
			elsif($col->{'Status'} eq 'Inactive' or $col->{'Status'} eq ''){
				$va{'searchresultspr'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&activpr=$col->{$cadidorderproducts}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate' alt='' border='0'></a>|;
			}
			$va{'searchresultspr'} .= "</td>";
			$va{'searchresultspr'} .= " <td class='smalltext' valign='top'>";
			$va{'searchresultspr'} .= "<br>".&format_sltvid($col->{'Related_ID_products'});
			$va{'searchresultspr'} .= "</td>\n";
			$va{'searchresultspr'} .= "  <td class='smalltext' valign='top'>$tmp{'model'}<br>".substr($cadtoshow,0,30)."</td>\n";
# 			my $sthshp=&Do_SQL("SELECT if(ShpDate!='0000-00-00' and ShpDate!='' and not isnull(ShpDate) and Tracking!='' and not isnull(Tracking),1,0)as Shipped from $cadtbproducts where $cadidorderproducts=$col->{$cadidorderproducts}")if($col->{'Action'}ne'Original');
# 			my $shipped=$sthshp->fetchrow;
 			#&cgierr("$shipped or $locked_record or $col->{'Status'}");
			
			if(($shipped or $locked_record or $col->{'Status'} eq 'Inactive')) {
				#Se muestran textos
				$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'Quantity'})."</td>";
				$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'UnitPrice'})."</td>";
				$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'SalePrice'})."</td>";
				$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'Discount'})."</td>\n";
				$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'Shipping'})."</td>\n";
			
			}else{
				#Se muestran cajas de edición
				$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input type='hidden' name='upd_$col->{$cadidorderproducts}' value='$col->{$cadidorderproducts}'>
				                                                                                            <input $locked_record size=5 type='text' name='quantity_$col->{$cadidorderproducts}' value='$col->{'Quantity'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";				
				# Edit Price in Order
				if (&check_permissions('edit_order_edit_price','','') or $flag_services){
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input $locked_record size=5 type='text' name='unitprice_$col->{$cadidorderproducts}' value='".$col->{'UnitPrice'}."' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input $locked_record size=8 type='text' name='price_$col->{$cadidorderproducts}' value='".$col->{'SalePrice'}."' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
				}else{
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input type='hidden' name='unitprice_$col->{$cadidorderproducts}' value='".$col->{'UnitPrice'}."'>".&format_price($col->{'UnitPrice'})."</td>";
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input type='hidden' name='price_$col->{$cadidorderproducts}' value='".$col->{'SalePrice'}."'>".&format_price($col->{'SalePrice'})."</td>";
				}

				if ($col->{'ID_products'} < 99999 or substr($col->{'Related_ID_products'},0,1) == 6)
				{
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input type='hidden' name='disc_$col->{$cadidorderproducts}' value='$col->{'Discount'}'>".&format_price($col->{'Discount'})."</td>\n";
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input type='hidden' name='shp_$col->{$cadidorderproducts}' value='$col->{'Shipping'}'>".&format_price($col->{'Shipping'})."</td>\n";
				}
				else
				{
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input $locked_record size=5 type='text' name='disc_$col->{$cadidorderproducts}' value='$col->{'Discount'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>\n";
					$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap><input $locked_record size=5 type='text' name='shp_$col->{$cadidorderproducts}' value='$col->{'Shipping'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>\n";
				}
			}
			$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($col->{'Tax'})."</td>\n";
			$va{'searchresultspr'} .= "  <td class='smalltext' align='right' valign='top' $decor nowrap>".&format_price($producttot)."</td>\n";
			$va{'searchresultspr'} .= "  <td class='tbltextttl' align='right' valign='top' $decor nowrap><font color='$gvcolor'>$col->{'Action'}</font></td>\n";
			$va{'searchresultspr'} .= "</tr>\n";
		}
		$va{'searchresultspr'} .= qq|
			<tr>
				<td colspan='3' class='smalltext' align="center">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="left" class='smalltext' nowrap> $totqty </td>
				<td colspan='2' align="right" class='smalltext' nowrap>|.&format_price($totprice).qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($totdis).qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($totshp).qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($tottax).qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($tot_ord).qq|</td>
			</tr>\n|;
	}
	else
	{
		$va{'pageslist'} = 1;
		$va{'searchresultspr'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $tot_ord;
}

sub show_payments{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/20/08 17:48:16
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/21/08 15:35:05
# Last Modified by: MCC C. Gabriel Varela S: Se agrega columna Action. 
# Last Modified on: 11/26/08 12:25:50
# Last Modified by: MCC C. Gabriel Varela S: Se agrega path
# Last Modified on: 12/01/08 12:47:13
# Last Modified by: MCC C. Gabriel Varela S: Se agrega &returntype=$in{'returntype'}
# Last Modified on: 12/03/08 09:44:13
# Last Modified by: MCC C. Gabriel Varela S: Se condiciona que se pueda eliminar/cancelar un pago
# Last Modified on: 12/03/08 15:49:28
# Last Modified by: MCC C. Gabriel Varela S: Se incorporan cajas de texto
# Last Modified on: 01/07/09 13:45:13
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se puedan editar las cantidades y payment date de los pagos que son type "desconocido"
# Last Modified on: 03/11/09 13:41:25
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si el tipo de pago es "desconocido", se permita cancelar si el tipo de pago es Layaway y no está captured
# Last Modified on: 07/14/09 12:35:54
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se pueda borrar un pago "desconocido" si el action es Created.
# Last Modified on: 07/21/09 11:51:58
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se puedan eliminar pagos "desconocidos" cuando el pago no ha sido capturado.
	###############################################################################################################
	####Pagos##################################################################################################
	###############################################################################################################
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my $tot_pay;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $cadtbpaymentstmp WHERE $cadidorders='$in{$cadidorders}'  and ID_admin_users=$usr{'id_admin_users'}/*and Status not in ('Cancelled','Void','Order Cancelled')*/");
	$va{'matchespa'} = $sth->fetchrow;
	
	if ($va{'matchespa'}>0) {

		my ($sth1) = &Do_SQL("SELECT *,$cadidorderpayments FROM $cadtbpaymentstmp WHERE $cadidorders='$in{$cadidorders}' and ID_admin_users=$usr{'id_admin_users'} /*and Status not in ('Cancelled','Void','Order Cancelled')*/ order by $cadidorderpayments;");
		my $gvcolor;
		
		while ($rec = $sth1->fetchrow_hashref) {
			$d = 1 - $d;
			if($rec->{'Action'}eq"Original") {
				$gvcolor="green";
			}elsif($rec->{'Action'}eq"Edited") {
				$gvcolor="blue";
			}elsif($rec->{'Action'}eq"Created") {
				$gvcolor="red";
			}

			if ($rec->{'Type'} eq "Check"){

				$va{'searchresultspa'} .= "<tr>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Select</td>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Name on Check</td>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Payment Date<br>(YYYY-MM-DD)</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Action</td>\n";
				$va{'searchresultspa'} .= "</tr>\n";
				$va{'searchresultspa'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresultspa'} .= "  <td class='smalltext'>";
				$va{'searchresultspa'} .= "  	<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{$cadidorderpayments}'>\n\n"if($cfg{'chbox_orders_edition'});
				if($rec->{'Status'}ne"Cancelled" and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void")
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&droppa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>|if((($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'})));
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&duplpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/duplicate.gif' title='Duplicate' alt='' border='0'></a>|if($rec->{'comefrom'}eq"Original");
				}
				else
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&activpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate' alt='' border='0'></a>|;
				}
				$va{'searchresultspa'} .= "</td>";
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'};
				}
				$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField1'}</td>\n";
				$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor> $rec->{'PmtField2'}<br>$rec->{'PmtField3'}<br>$rec->{'PmtField4'}</td>\n";
				
				if( ($rec->{'Status'} eq 'Approved' and $rec->{'AuthCode'} and $rec->{'AuthCode'} ne '0000') or $rec->{'Status'}eq"Cancelled" or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'} eq "Void") {
				#Se muestran textos.
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>";
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> $rec->{'Paymentdate'}</td>";
				
				}else{
				#Se muestra caja	
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> <input type='hidden' name='updpa_$rec->{$cadidorderpayments}' value='$rec->{$cadidorderpayments}'><input size=8 type='text' name='amt_$rec->{$cadidorderpayments}' value='$rec->{'Amount'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> <input size=10 type='text' name='pdate_$rec->{$cadidorderpayments}' value='$rec->{'Paymentdate'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
				}
				$va{'searchresultspa'} .= "   <td class='tbltextttl' valign='top' $decor> <font color='$gvcolor'>$rec->{'Action'}</font></td>\n";
				$va{'searchresultspa'} .= "</tr>\n";					
			}elsif($rec->{'Type'} eq "WesternUnion"){
				$va{'searchresultspa'} .= "<tr>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>SELECT</td>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title' colspan='5'>WesterUnion Payment</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Payment Date<br>(YYYY-MM-DD)</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Action</td>\n";
				$va{'searchresultspa'} .= "</tr>\n";
				$va{'searchresultspa'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresultspa'} .= "  <td class='smalltext'>";
				$va{'searchresultspa'} .= "  	<input type='checkbox' class='checkbox' name='changepayments' value='$rec->{$cadidorderpayments}'>\n\n"if($cfg{'chbox_orders_edition'});
				if($rec->{'Status'}ne"Cancelled" and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void")
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&droppa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>|if($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000');
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&duplpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/duplicate.gif' title='Duplicate' alt='' border='0'></a>|if($rec->{'comefrom'}eq"Original");
				}
				else
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&activpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate' alt='' border='0'></a>|;
				}
				$va{'searchresultspa'} .= "</td>";
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'};
				}
				$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor colspan='4'> No Information Required For WU Payments</td>\n";
				if(($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000')or($rec->{'Status'}eq"Cancelled" or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"))
				{#Se muestran textos
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>\n";
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> $rec->{'Paymentdate'}</td>\n";
				}
				else
				{#Se muestra caja
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> <input type='hidden' name='updpa_$rec->{$cadidorderpayments}' value='$rec->{$cadidorderpayments}'><input size=8 type='text' name='amt_$rec->{$cadidorderpayments}' value='$rec->{'Amount'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>\n";
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> <input size=10 type='text' name='pdate_$rec->{$cadidorderpayments}' value='$rec->{'Paymentdate'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>\n";
				}
				$va{'searchresultspa'} .= "   <td class='tbltextttl' valign='top' $decor> <font color='$gvcolor'>$rec->{'Action'}</font></td>\n";
				$va{'searchresultspa'} .= "</tr>\n";	
			}elsif($rec->{'Type'} eq "Credit-Card"){
				$va{'searchresultspa'} .= "<tr>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>SELECT</td>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Payment Date<br>(YYYY-MM-DD)</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Action</td>\n";
				$va{'searchresultspa'} .= " </tr>\n";
				$va{'searchresultspa'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresultspa'} .= "  <td class='smalltext'>";
				$va{'searchresultspa'} .= "  <input type='checkbox' class='checkbox' name='changepayments' value='$rec->{$cadidorderpayments}'>\n\n"if($cfg{'chbox_orders_edition'});
				if($rec->{'Status'}ne"Cancelled" and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void")
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&droppa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>|if ((($rec->{'Amount'}<0 and $rec->{'Status'}ne'Credit by Monterey')or( $rec->{'Status'} ne 'Cancelled' and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void" and $rec->{'Status'}ne'Credit by Monterey' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))))and !($rec->{'Captured'} eq 'Yes' or $rec->{'Status'} eq 'Order Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void")and !($rec->{'AuthCode'}>0));
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&duplpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/duplicate.gif' title='Duplicate' alt='' border='0'></a>|if($rec->{'comefrom'}eq"Original");
				}
				else
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&activpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate' alt='' border='0'></a>|;
				}
				$va{'searchresultspa'} .= "</td>";
				
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'};
				}
				$va{'searchresultspa'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField1'}<br>$rec->{'PmtField7'}</td>\n";
				$rec->{'PmtField3'} = "XXXX-XXXX-XXXX-".substr($rec->{'PmtField3'},-4) unless ($usr{'usergroup'} eq '1' or $usr{'usergroup'} eq '2');
				if ($rec->{'AuthCode'}){
					$va{'searchresultspa'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}<br>Auth Code: $rec->{'AuthCode'} / Capt Date $rec->{'CapDate'}</td>\n";
				}else{
					$va{'searchresultspa'} .= "   <td class='smalltext' $decor valign='top'>$rec->{'PmtField2'}<br>$rec->{'PmtField3'}</td>\n";
				}
				if (!(((($rec->{'Amount'}<0 and $rec->{'Status'}ne'Credit by Monterey')or( $rec->{'Status'} ne 'Cancelled' and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void" and $rec->{'Status'}ne'Credit by Monterey' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))))and !($rec->{'Captured'} eq 'Yes' or $rec->{'Status'} eq 'Order Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void")and !($rec->{'AuthCode'}>0)))or ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"))
				{#Se muestran textos
					$va{'searchresultspa'} .= "   <td class='smalltext' $decor align='right' valign='top'> ".&format_price($rec->{'Amount'})."</td>\n";
					$va{'searchresultspa'} .= "   <td class='smalltext' $decor align='right' valign='top'> $rec->{'Paymentdate'}</td>\n";
				}
				else
				{#Se muestra caja
					$va{'searchresultspa'} .= "   <td class='smalltext' $decor align='right' valign='top'> <input type='hidden' name='updpa_$rec->{$cadidorderpayments}' value='$rec->{$cadidorderpayments}'><input size=8 type='text' name='amt_$rec->{$cadidorderpayments}' value='$rec->{'Amount'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>\n";
					$va{'searchresultspa'} .= "   <td class='smalltext' $decor align='right' valign='top'> <input size=10 type='text' name='pdate_$rec->{$cadidorderpayments}' value='$rec->{'Paymentdate'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>\n";
				}

				#$va{'searchresultspa'} .= "</td>\n";
				$va{'searchresultspa'} .= "   <td class='tbltextttl' valign='top' $decor><font color='$gvcolor'> $rec->{'Action'}</font></td>\n";
				$va{'searchresultspa'} .= "</tr>\n";
			}else{
				$va{'searchresultspa'} .= "<tr>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>SELECT</td>\n";
				$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Type</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Pay Form</td>\n";	
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Amount</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Payment Date<br>(YYYY-MM-DD)</td>\n";
				$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Action</td>\n";
				$va{'searchresultspa'} .= " </tr>\n";
				$va{'searchresultspa'} .= " <tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresultspa'} .= "  <td class='smalltext'>";
				$va{'searchresultspa'} .= "  <input type='checkbox' class='checkbox' name='changepayments' value='$rec->{$cadidorderpayments}'>\n\n"if($cfg{'chbox_orders_edition'});
				if ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"){
					$decor = " style=' text-decoration: line-through'";
				}else{
					$decor ='';
					$tot_pay += $rec->{'Amount'};
				}
				
				if($rec->{'Status'}ne"Cancelled" and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void")
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&droppa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>|if(($rec->{'Type'} eq "Layaway" and $rec->{'Captured'} ne 'Yes')or($rec->{'Action'}eq"Created")or($rec->{'Captured'} ne 'Yes'));
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&duplpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/duplicate.gif' title='Duplicate' alt='Duplicate' border='0'></a>|;#if($rec->{'comefrom'}eq"Original");
				}
				else
				{
					$va{'searchresultspa'} .= qq| <a href="$script_url?cmd=[in_cmd]&$cadidorders=$in{$cadidorders}&activpa=$rec->{$cadidorderpayments}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate' alt='Activate' border='0'></a>|;
				}
				
				$va{'searchresultspa'} .= "</td>";
				$va{'searchresultspa'} .= "   <td class='smalltext' nowrap>$rec->{'Type'}</td>";
				$va{'searchresultspa'} .= "   <td class='smalltext' nowrap>$rec->{'PmtField1'}</td>";
				if (!(((($rec->{'Amount'}<0 and $rec->{'Status'}ne'Credit by Monterey')or( $rec->{'Status'} ne 'Cancelled' and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void" and $rec->{'Status'}ne'Credit by Monterey' and (($rec->{'Status'} ne 'Approved' or $rec->{'AuthCode'} eq '0000') or ($rec->{'Status'} eq 'Approved' and !$rec->{'AuthCode'}))))and !($rec->{'Captured'} eq 'Yes' or $rec->{'Status'} eq 'Order Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void")and !($rec->{'AuthCode'}>0)))or ($rec->{'Status'} eq 'Cancelled' or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void"))
				{#Se muestran textos.
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> ".&format_price($rec->{'Amount'})."</td>";
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> $rec->{'Paymentdate'}</td>";
				}
				else
				{#Se muestra caja
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> <input type='hidden' name='updpa_$rec->{$cadidorderpayments}' value='$rec->{$cadidorderpayments}'><input size=8 type='text' name='amt_$rec->{$cadidorderpayments}' value='$rec->{'Amount'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
					$va{'searchresultspa'} .= "   <td class='smalltext' valign='top' $decor align='right'> <input size=10 type='text' name='pdate_$rec->{$cadidorderpayments}' value='$rec->{'Paymentdate'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
				}
#				$va{'searchresultspa'} .= "   <td class='smalltext' $decor align='right' valign='top'> ".&format_price($rec->{'Amount'});
#				$va{'searchresultspa'} .= "</td>\n";
#				$va{'searchresultspa'} .= "   <td class='smalltext' $decor align='right' valign='top'> $rec->{'Paymentdate'}</td>\n";
				$va{'searchresultspa'} .= "   <td class='tbltextttl' valign='top' $decor><font color='$gvcolor'> $rec->{'Action'}</font></td>\n";
				$va{'searchresultspa'} .= "</tr>\n";
			}
		}
		$va{'searchresultspa'} .= qq|
			<tr>
				<td colspan='3' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($tot_pay).qq|</td>
			</tr>\n|;
	}else{
		if($in{'type'}eq'Credit-Card'){
			$va{'searchresultspa'} .= "<tr>\n";
			$va{'searchresultspa'} .= "   <td class='menu_bar_title'>SELECT</td>\n";
			$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Type</td>\n";
			$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Name on Card<br>Card Number</td>\n";
			$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Amount</td>\n";
			$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Payment Date<br>(YYYY-MM-DD)</td>\n";
			$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Action</td>\n";
			$va{'searchresultspa'} .= " </tr>\n";			
		}else{
			$va{'searchresultspa'} .= "<tr>\n";
			$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Select</td>\n";
			$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Name on Check</td>\n";
			$va{'searchresultspa'} .= "   <td class='menu_bar_title'>Routing ABA/ Account/ Chk</td>\n";
			$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Amount</td>\n";
			$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Payment Date<br>(YYYY-MM-DD)</td>\n";
			$va{'searchresultspa'} .= "	<td class='menu_bar_title'>Action</td>\n";
			$va{'searchresultspa'} .= "</tr>\n";	
		}		
		
		$va{'pageslist'} = 1;
		$va{'searchresultspa'} .= qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $tot_pay;
}

sub payments_actions{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/20/08 17:49:01
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/26/08 16:44:52
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la validación de amount para aceptar pagos negativos
# Last Modified on: 12/11/08 13:17:00
# Last Modified by: MCC C. Gabriel Varela S: Nueva forma de agregar pagos.
# Last Modified on: 02/20/09 11:51:38
# Last Modified by: MCC C. Gabriel Varela S: Se limita la eliminación al usuario que lo está editando.
# Last Modified RB: 05/19/09  15:16:46 -- Se cambia el Reason a Other/Refund
# Last Modified on: 09/02/09 16:45:32
# Last Modified by: MCC C. Gabriel Varela S:Se pone ID=1 cuando no existen datos previos.


	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	###############################################################################################################
	######ACCIONES PARA PAGOS##########################################################################
	###############################################################################################################
	
	####Eliminar/Inactivar pagos####
	if($in{'droppa'})
	{
		$sth = &Do_SQL("SELECT * FROM $cadtbpaymentstmp WHERE $cadidorderpayments='$in{'droppa'}' and ID_admin_users=$usr{'id_admin_users'}");
		$rec=$sth->fetchrow_hashref;
		if($sth->rows>0)
		{
			if($rec->{'Status'}ne"Cancelled" and $rec->{'Status'}ne"Order Cancelled" and $rec->{'Status'}ne"Void")
			{
				if($rec->{'Action'}ne"Created")#Se modifica el status
				{
					&Do_SQL("UPDATE $cadtbpaymentstmp set Status='Cancelled',Action='Edited' where $cadidorderpayments='$in{'droppa'}' and ID_admin_users=$usr{'id_admin_users'}");
				}
				else #Se elimina la fila
				{
					&Do_SQL("DELETE FROM $cadtbpaymentstmp where $cadidorderpayments='$in{'droppa'}' and ID_admin_users=$usr{'id_admin_users'}");
				}
			}
		}
	}
	
#	####Activar pago####
	if($in{'activpa'})
	{
		$sth = &Do_SQL("SELECT * FROM $cadtbpaymentstmp WHERE $cadidorderpayments='$in{'activpa'}' and ID_admin_users=$usr{'id_admin_users'}");
		$rec=$sth->fetchrow_hashref;
		if($sth->rows>0)
		{
			if($rec->{'Status'}eq"Cancelled" or $rec->{'Status'}eq"Order Cancelled" or $rec->{'Status'}eq"Void")
			{
				&Do_SQL("UPDATE $cadtbpaymentstmp set Status='Approved',Action='Edited' where $cadidorderpayments='$in{'activpa'}' and ID_admin_users=$usr{'id_admin_users'}");
			}
		}
	}
	
#	####Duplicar pago####
	if($in{'duplpa'})
	{
		#Obtener próximo ID
		$sth = &Do_SQL("SELECT max($cadidorderpayments)+1 FROM $cadtbpaymentstmp");
		$lastid=$sth->fetchrow;
		$lastid=1 if(!$lastid);
		&Do_SQL("INSERT INTO $cadtbpaymentstmp ($cadidorderpayments,$cadidorders,Type,PmtField1,PmtField2,PmtField3,PmtField4,PmtField5,PmtField6,PmtField7,PmtField8,PmtField9,Amount,Reason,Paymentdate,Status,ID_admin_users,Action,comefrom)
										SELECT $lastid,$cadidorders,Type,PmtField1,PmtField2,PmtField3,PmtField4,PmtField5,PmtField6,PmtField7,PmtField8,PmtField9,Amount,Reason,Paymentdate,Status,$usr{'id_admin_users'},'Created','Dupl' from $cadtbpaymentstmp where $cadidorderpayments=$in{'duplpa'} and ID_admin_users=$usr{'id_admin_users'};");
	}

#	####Agregar pago####
	if($in{'addpa'}) {

		if($in{$cadidorderpayments} && $in{'amount'} && $in{$cadidorders} && $in{'paymentdate'}){
			if($in{'amount'} =~ m/^(-?[0-9]+)(\.[0-9]+)?$/){
				my ($sth) = &Do_SQL("SELECT COUNT(*) FROM $cadtbpaymentstmp WHERE $cadidorderpayments='$in{$cadidorderpayments}' and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'};");
				$va{'matches'} = $sth->fetchrow;
				if($va{'matches'}==1){
					$sth = &Do_SQL("SELECT max($cadidorderpayments)+1 FROM $cadtbpaymentstmp");
					$lastid=$sth->fetchrow;
					$lastid=1 if(!$lastid);
					my ($sth) = &Do_SQL("SELECT * FROM $cadtbpaymentstmp WHERE $cadidorderpayments='$in{$cadidorderpayments}' and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'};");
					$rec = $sth->fetchrow_hashref;
					for my $i(1..9){
						$query .= "PmtField$i='".&filter_values($rec->{'PmtField'.$i})."',";
					}
					chop($query);
					#$reason = 'Other' if $in{'amount'} < 0;
					$in{$cadidorderpayments}++;
					my ($sth) = &Do_SQL("INSERT INTO $cadtbpaymentstmp SET $cadidorderpayments=$lastid,$cadidorders='$in{$cadidorders}',Type='Credit-Card',$query ,Amount='$in{'amount'}',Reason=IF($in{'amount'}>0,'Sale','Other'),Paymentdate='$in{'paymentdate'}',Status='Approved', ID_admin_users='$usr{'id_admin_users'}',Action='Created',comefrom='Add'");
					if($in{'refundworeturn'}eq"1")
					{
						$in{'addpr'}=$cfg{'refund_wo_return'};
					}
				}
			} else {
				$error{'amount'} = &trans_txt('invalid');
				$va{'tabmessage'} = &trans_txt('reqfields');
			}
		} else{
			$va{'tabmessage'} = &trans_txt('reqfields');
		}
	}	
	
#	####Agregar pago####
	if($in{'addnpa'}){
		#El pago es tipo tdc
		if($in{'ptype'}eq"tdc"){
			if(($in{'amount'} and $in{$cadidorders} and $in{'paymentdate'}) or ($in{'pmtfield1'}ne"" and $in{'pmtfield2'}ne"" and $in{'pmtfield3'}ne"" and $in{'pmtfield5'}ne"" and $in{'pmtfield6'}ne"" and $in{'amount'} and $in{$cadidorders} and $in{'paymentdate'} and $in{'month'} and $in{'year'})){
				if($in{'amount'} =~ m/^(-?[0-9]+)(\.[0-9]+)?$/){				
					$sth = &Do_SQL("SELECT max($cadidorderpayments)+1 FROM $cadtbpaymentstmp");
					$lastid=$sth->fetchrow;
					$lastid=1 if(!$lastid);
					$count=9;
					$type="Credit-Card";
					$count=1 and $type="Money Order" if($in{'pmtfield1'}eq"Money Order");
					$in{'pmtfield4'}="$in{'month'}$in{'year'}"if($in{'pmtfield1'}ne"Money Order");
					for my $i(1..$count){
						$query .= "PmtField$i='".&filter_values($in{'pmtfield'.$i})."',";
					}
					my ($sth) = &Do_SQL("INSERT INTO $cadtbpaymentstmp SET $cadidorderpayments=$lastid,$cadidorders='$in{$cadidorders}',Type='$type',$query Amount='$in{'amount'}',Reason=IF($in{'amount'}>0,'Sale','Refund'),Paymentdate='$in{'paymentdate'}',Status='Approved', ID_admin_users='$usr{'id_admin_users'}',Action='Created',comefrom='Add'");
					
					if($in{'refundworeturn'}eq"1"){
						$in{'addpr'}=$cfg{'refund_wo_return'};
					}
				}else{
					$error{'amount'} = &trans_txt('invalid');
					$va{'tabmessage'} = &trans_txt('reqfields');
				}
			}
		#El pago es tipo check	
		}else{
			if($in{'amountc'} and $in{$cadidorders} and $in{'paymentdatec'}){
				$sth = &Do_SQL("SELECT max($cadidorderpayments)+1 FROM $cadtbpaymentstmp");
				$lastid=$sth->fetchrow;
				$lastid=1 if(!$lastid);
				$count=9;
				$type = $cfg{'payments_default_type'};
				my ($sth) = &Do_SQL("INSERT INTO $cadtbpaymentstmp SET $cadidorderpayments=$lastid,$cadidorders='$in{$cadidorders}',Type='$type',$query Amount='$in{'amountc'}',Reason=IF($in{'amountc'}>0,'Sale','Refund'),Paymentdate='$in{'paymentdatec'}',Status='Approved', ID_admin_users='$usr{'id_admin_users'}',Action='Created',comefrom='Add'");				
			}else{
				$error{'amountc'} = &trans_txt('invalid');
				$error{'paymentdatec'} = &trans_txt('invalid');
				$va{'tabmessage'} = &trans_txt('reqfields');
			}
		}
	}
	
}

sub check_pretotals{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/21/08 12:51:51
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 12/02/08 18:26:02
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta
# Last Modified on: 02/13/09 11:03:53
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se calculen a 0 los valores que son null en donde antes estaba:SalePrice-Discount+Tax+Shipping
# Last Modified on: 09/02/09 17:22:00
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se redondee check_pretotals a 2 decimales.
# Last Modified on: 09/14/09 15:00:31
# Last Modified by: MCC C. Gabriel Varela S: Se hace que si es menor el absoluto que .01, regrese 0.

	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	$sth=&Do_SQL("SELECT sum(amount)as SumPay from $cadtbpaymentstmp where $cadidorders=$in{$cadidorders} and Status not in ('Cancelled','Void','Order Cancelled') and ID_admin_users=$usr{'id_admin_users'} group by $cadidorders");
	$sumamount=$sth->fetchrow();
	$sumamount=0 if($sumamount eq'');
	
	$sth=&Do_SQL("SELECT (Sum(if(ID_products not like '6%' and $cadtbproductstmp.Status!='Inactive',if(not isnull(SalePrice),SalePrice,0)-if(not isnull(Discount),Discount,0)+if(not isnull(Tax),Tax,0)+if(not isnull(Shipping),Shipping,0),0)))+Sum(if(ID_products like '6%' and $cadtbproductstmp.Status!='Inactive',SalePrice,0))-if(not isnull(Sumpay),Sumpay,0) as Diff
FROM $cadtbproductstmp
left join (SELECT $cadidorders,sum(amount)as SumPay from $cadtbpaymentstmp where $cadidorders=$in{$cadidorders} and Status not in ('Cancelled','Void','Order Cancelled') and ID_admin_users=$usr{'id_admin_users'} group by $cadidorders)as tempo on (tempo.$cadidorders=$cadtbproductstmp.$cadidorders)
where ID_admin_users=$usr{'id_admin_users'} and $cadtbproductstmp.$cadidorders=$in{$cadidorders}
GROUP BY $cadtbproductstmp.$cadidorders");
	#return round($sth->fetchrow(),2);
	my $sthvalue=$sth->fetchrow();
	if($sthvalue < 0.01 and $sthvalue > -0.01){
		return 0.00;
	}else{
		return $sthvalue;
	}
}

sub adjust_edition {
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/21/08 15:47:52
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 09/02/09 16:45:32
# Last Modified by: MCC C. Gabriel Varela S:Se pone ID=1 cuando no existen datos previos.
# Last modified on 30 Jun 2011 15:39:24
# Last modified by: MCC C. Gabriel Varela S. :If the order type is COD, then the payment is edited instead of adding a new one.
# Last modified by RB on 03/12/2012: Se pide que el pago no este capturado para proceder con el UPDATE
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my $diff=&check_pretotals;
	my $reason,$comefrom;
	
	if($diff!=0) {
		
		if($in{'addpr'} or $in{'addpa'}) {
			$comefrom="Add";
		}elsif($in{'droppr'} or $in{'droppa'}){
			$comefrom="Drop";
		}elsif($in{'duplpr'} or $in{'duplpa'}){
			$comefrom="Dupl";
		}elsif($in{'refund'} or $in{'reship'} or $in{'exchange'}){
			$comefrom="Return";
		}
		
		$sth = &Do_SQL("SELECT max($cadidorderpayments)+1 FROM $cadtbpaymentstmp");
		$lastid=$sth->fetchrow;
		$lastid=1 if(!$lastid);
		
		my ($sth2) = &Do_SQL("SELECT *,$cadidorderpayments FROM $cadtbpaymentstmp WHERE $cadidorders =$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'}
							ORDER BY $cadidorderpayments LIMIT 1 ");
		my ($rec2) = $sth2->fetchrow_hashref;
		$queryPmt = '';
		for my $i(1..9){
				$queryPmt .= ",PmtField$i = '".$rec2->{'PmtField'.$i.''}."' ";
		}
		my $statuspayments='Approved';
		$statuspayments='Credit' if($diff<0);
		$reason="Reason='Sale',";
		$reason="Reason='Refund',"if($in{'refund'} or $diff<0);
		$reason="Reason='Reship',"if($in{'reship'});
		$reason="Reason='Exchange',"if($in{'exchange'});
		
		#If the order type is COD, then the payment is edited instead of adding a new one.
		#Get the orden type first
		my $order_type=&load_name("$cadtborders","$cadidorders",$in{"$cadidorders"},"Ptype");
		
		if($order_type eq 'COD' and $rec2->{'Captured'} ne 'Yes' and $rec2->{$cadidorderpayments}) {
			&Do_SQL("UPDATE $cadtbpaymentstmp SET Amount =Amount+$diff,Action='Edited',comefrom='$comefrom' where $cadidorderpayments=".$rec2->{$cadidorderpayments});
		}else{
			#Verifica si ya existe un pago Created
			$sthpc=&Do_SQL("SELECT $cadidorderpayments FROM $cadtbpaymentstmp WHERE $cadidorders =$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'} and Action='Created'");
			$id_orders_payments_created=$sthpc->fetchrow;
			
			if($id_orders_payments_created ne "" and $id_orders_payments_created>0) {
				&Do_SQL("UPDATE $cadtbpaymentstmp SET Amount=Amount+$diff WHERE $cadidorderpayments=$id_orders_payments_created");
			}else{
				$rec2->{'Type'} = $cfg{'payments_default_type'};
				&Do_SQL("INSERT INTO $cadtbpaymentstmp SET $cadidorderpayments=$lastid,$cadidorders=$in{$cadidorders},Type= '$rec2->{'Type'}' $queryPmt , Amount =$diff,$reason Paymentdate=CURDATE(),Status='$statuspayments',ID_admin_users=$usr{'id_admin_users'},Action='Created',comefrom='$comefrom'");
			}
		}
	}
}


sub exists_return{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/24/08 18:15:31
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/25/08 09:24:52
# Last Modified by: MCC C. Gabriel Varela S: Se modifica consulta.

	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();

	my $sth;
	$sth=&Do_SQL("SELECT sum(hasreturn)as hasreturn from
(SELECT if(isnull(sum(if(comefrom='Return',1,0))),0,sum(if(comefrom='Return',1,0)))as hasreturn from $cadtbproductstmp 
where comefrom='Return' and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'}
union
SELECT if(isnull(sum(if(comefrom='Return',1,0))),0,sum(if(comefrom='Return',1,0)))as hasreturn from $cadtbpaymentstmp 
where comefrom='Return' and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'}) as determ");
	return $sth->fetchrow;
}

sub edit_orders_additems{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/25/08 10:01:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 11/25/08 17:23:15
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se agregue el id del producto exchange
# Last Modified on: 11/26/08 09:39:38
# Last Modified by: MCC C. Gabriel Varela S: Se agrega variable get exchange para incluirla en la búsqueda al hacer el submit
# Last Modified on: 12/01/08 12:49:40
# Last Modified by: MCC C. Gabriel Varela S: Se agrega &returntype=$in{'returntype'}
# Last Modified on: 12/02/08 09:26:22
# Last Modified by: MCC C. Gabriel Varela S: Se cambia consulta para mostrar sólo los productos que sí tienen UPC cuando se hace por medio de un return.
# Last Modified on: 12/03/08 15:22:32
# Last Modified by: MCC C. Gabriel Varela S: Se contemplan servicios
# Last Modified on: 08/06/09 12:09:00
# Last Modified by: MCC C. Gabriel Varela S: Se modifica sólo para agregar partes.

	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	my ($query,$queryret,$querynon,$querytoapply,$str_id,$ctable,$ctable1,$cmod);

	$in{'id_customers'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
	

	if($cfg{'customers_parts_use'}) {
		(!$in{'allskus'}) ?
			($va{'this_link'} = '<a href="/cgi-bin/common/apps/ajaxorder_wqty?cmd=edit_orders_additems&id_orders='.$in{'id_orders'}.'&path='.$in{'path'}.'&exchange='.$in{'exchange'}.'&taxesapp='.$in{'taxesapp'}.'&edit_type='.$in{'edit_type'}.'&allskus=1" title="General List"> Show All SKUs</a>') :
			($va{'this_link'} = '<a href="/cgi-bin/common/apps/ajaxorder_wqty?cmd=edit_orders_additems&id_orders='.$in{'id_orders'}.'&path='.$in{'path'}.'&exchange='.$in{'exchange'}.'&taxesapp='.$in{'taxesapp'}.'&edit_type='.$in{'edit_type'}.'" title="Customer List"> Show  Customer\'s SKUs</a>');
	}

	my $cor = "OR sl_parts.ID_parts like '%$in{'keyword'}%'";
	my $cprice = "1";
	if($cfg{'customers_parts_use'} and !$in{'allskus'}){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers_parts WHERE ID_customers = '$in{'id_customers'}';");
		my($total) = $sth->fetchrow();

		($total > 0) and ($ctable = "INNER JOIN sl_customers_parts USING(ID_parts) ") and ($cor = " OR sl_customers_parts.ID_parts LIKE '%$in{'keyword'}%' OR sl_customers_parts.sku_customers LIKE '%$in{'keyword'}%' ") and ($cprice = "sl_customers_parts.SPrice") and  ($cmod = " AND ID_customers = '$in{'id_customers'}'") ;

	}

	$queryret="";
	$queryret=" and not isnull(UPC) and UPC!='' " if($in{'exchange'}ne"");
	$query=" and sl_parts.Status !='Inactive' ";
	$querynon=" and sl_services.Status NOT IN (/*'Hidden',*/'Inactive') AND SPrice>=0 ";

	if ($in{'keyword'}){
		$in{'keyword'}=&filter_values($in{'keyword'});
		$query .= " AND (Name like '%$in{'keyword'}%' OR Model like '%$in{'keyword'}%' ". $cor ." OR UPC = '$in{'keyword'}')";
		$querynon .= " AND (Name like '%$in{'keyword'}%' OR sl_services.ID_services like '%$in{'keyword'}%')";
	}

	$querytoapply="SELECT SUM(county) FROM (SELECT COUNT(DISTINCT(sl_parts.ID_parts))as county FROM sl_parts ".$ctable." INNER JOIN sl_skus on (sl_parts.ID_parts=sl_skus.ID_products) WHERE 1 $queryret $query $cmod";
	$querytoapply.=" UNION
					SELECT count(distinct(sl_services.ID_services))as county FROM sl_services /*INNER JOIN sl_skus on (sl_services.ID_services=sl_skus.ID_products)*/ WHERE SPrice>=0 $querynon"if($in{'exchange'}eq"");
	$querytoapply.=")as tempo";
	my ($sth) = &Do_SQL($querytoapply);
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/ajaxorder_wqty",$va{'matches'},$usr{'pref_maxh'});
		$querytoapply="SELECT sl_parts.ID_parts as ID_products,Model,Name,".$cprice." as SPrice,sl_parts.Status,'400000000'as prefix FROM sl_parts ".$ctable." INNER JOIN sl_skus on (sl_parts.ID_parts=sl_skus.ID_products) WHERE 1 $queryret $query $cmod GROUP BY sl_parts.ID_parts LIMIT $first,$usr{'pref_maxh'};";
		$querytoapply="SELECT ID_services as ID_products,'',Name,SPrice,sl_services.Status,'600000000'as prefix FROM sl_services INNER JOIN sl_skus on (sl_services.ID_services=sl_skus.ID_products) WHERE SPrice>=0 $querynon GROUP BY sl_services.ID_services
						UNION ".$querytoapply if($in{'exchange'}eq"");
		my ($sth) = &Do_SQL($querytoapply);
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;

			my $model_name = qq|$rec->{'Model'}|;
			$model_name .= qq|<br>| if ($model_name ne '');			
			$model_name = qq|$rec->{'Name'}|;
			$str_id = format_sltvid($rec->{'ID_products'}+$rec->{'prefix'});

			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/common/apps/ajaxorder_wqty?cmd=editing_order&$cadidorders=$in{$cadidorders}&addpr=$rec->{'ID_products'}&prefix=$rec->{'prefix'}&qty=1&exchange=$in{'exchange'}&path=$in{'path'}&taxesapp=$in{'taxesapp'}&edit_type=$in{'edit_type'}')">
				<td class="smalltext" valign="top">$str_id</td>
				<td class="smalltext" valign="top">$model_name</td>
				<td class="smalltext" valign="top" align="right">|.&format_price($rec->{'SPrice'}).qq|</td>
				<td class="smalltext" valign="top" align="right" nowrap>$rec->{'Status'}</td>
			</tr>\n|;
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='4' align="center">  |.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	
	$va{'header'} = qq|
		<tr>
		    <td class="menu_bar_title">ID</td>
		    <td class="menu_bar_title">Model/Name</td>
		    <td class="menu_bar_title">Price</td>
		    <td class="menu_bar_title">Status</td>
		 </tr>\n|;
	$in{'id_name'} = "$cadidorders";
	$in{'id_value'} = $in{$cadidorders};
	$in{'id_name2'} = "exchange";
	$in{'id_value2'} = $in{'exchange'};
	$in{'id_name3'} = "taxesapp";
	$in{'id_value3'} = $in{'taxesapp'};
	$in{'id_name4'} = "edit_type";
	$in{'id_value4'} = $in{'edit_type'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
}

sub calc_tmp_prod_fields{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/25/08 10:36:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 01/05/09 13:26:59
# Last Modified by: MCC C. Gabriel Varela S: Se cambia el criterio para saber si está bien calculado el tax.
# Last Modified on: 03/17/09 17:10:26
# Last Modified by: MCC C. Gabriel Varela S: Parámetros sltv_itemshipping
# Last Modified on: 03/24/09 15:21:27
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta envío de COD
# Last Modified on: 05/26/09 13:40:27
# Last Modified by: MCC C. Gabriel Varela S: Se optimiza consulta.
# Last Modified RB: 12/16/2010  16:45:44 -- Se agregan parametros para calculo de shipping

	my($id_orders_products,$shippingf,$discountf)=@_;
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my ($sth1,$sth,$rec,$idpacking,$edt,$sizeq,$sizeh,$sizel,$discflex,$size,$weight,$shptotal1,$shptotal2,$shptotal1pr,$shptotal2pr,$shptype,$comillitas,$totshpord,$ntax,$ndisc,$shippingb,$taxb,$discb,$fpb,$shippingcad,$fpago,$customer_tax,$sku_tax);
	
	if(!$id_orders_products){
		$sth1=&Do_SQL("SELECT last_insert_id($cadidorderproducts)as last from $cadtbproductstmp order by last desc limit 1");
		$id_orders_products=$sth1->fetchrow;
	}

	$sth=&Do_SQL("SELECT $cadtbproductstmp.$cadidorderproducts,$cadtbproductstmp.Related_ID_products as ID_products,$cadtbproductstmp.$cadidorders,$cadtborders.shp_type,if(($cadtbproductstmp.Discount=0 and $cadtborders.OrderDisc!=0 and not isnull(OrderDisc)),0,1) as DiscB,
	             if(($cadtbproductstmp.Tax=0 and OrderTax!=0 and not isnull(OrderTax) and SalePrice!=0)or((SalePrice-$cadtbproductstmp.Discount)*OrderTax!=Tax)or isnull(Tax),0,1) as TaxB,if($cadtbproductstmp.Shipping=0 and OrderShp!=0 and not isnull(OrderShp),0,1)as ShippingB, Products, if(not isnull(Payments),Payments,0)as Payments, 
	             OrderTax, SalePrice, OrderShp, OrderDisc,$cadtbproductstmp.Discount, 
	        	Tax,Shipping,Quantity,shp_Zip 
	from $cadtbproductstmp 
	INNER JOIN $cadtborders on($cadtbproductstmp.$cadidorders=$cadtborders.$cadidorders) 
	INNER JOIN sl_parts on (right($cadtbproductstmp.Related_ID_products,4)=sl_parts.ID_parts) 
	INNER JOIN(SELECT $cadtbproductstmp.$cadidorders, count($cadidorderproducts) as Products, Payments
	           from $cadtbproductstmp left join (SELECT $cadtbpaymentstmp.$cadidorders, count($cadidorderpayments) as Payments
	                                             from $cadtbpaymentstmp
	                                             where $cadtbpaymentstmp.$cadidorders=$in{$cadidorders}
	                                             group by $cadtbpaymentstmp.$cadidorders)as tempt on (tempt.$cadidorders=$cadtbproductstmp.$cadidorders)
	           where 1 /*Related_id_products not like '6%'*/
	           and $cadtbproductstmp.$cadidorders=$in{$cadidorders}
	           group by $cadtbproductstmp.$cadidorders)as tempo on(tempo.$cadidorders=$cadtborders.$cadidorders)
	where 1 /*$cadtbproductstmp.Related_ID_products not like '6%'*/ and $cadtbproductstmp.$cadidorderproducts=$id_orders_products");
	$rec=$sth->fetchrow_hashref;
	
	## Part Sale Tax
	my $sth = &Do_SQL("SELECT IF(Sale_Tax IS NULL,'no',Sale_Tax/100)AS Sale_Tax FROM sl_parts WHERE ID_parts = '". substr($rec->{'ID_products'},-4) ."';") ;
	my($ptax) = $sth->fetchrow();
	$in{'taxesapp'} = $ptax if $ptax ne 'no';


	$discb=$rec->{'Discount'};
	$taxb=$rec->{'Tax'};
	$shippingb=$rec->{'Shipping'};
	
	if($rec->{'ID_products'} ne '') {
		#########################
		#Se establece el Shipping
		#########################
		if($rec->{'ShippingB'}==0) {
			if($rec->{'Products'}==1) {
				$totshpord=$rec->{'OrderShp'};
			}else{
				$idpacking = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},-4),'ID_packingopts');
				$edt= $rec->{'edt'};
				$sizew=$rec->{'SizeW'};
				$sizeh=$rec->{'SizeH'};
				$sizel=$rec->{'SizeL'};
				$discflex=$rec->{'flexipago'};
				$size=$sizew*$sizeh*$sizel;
				$weight=$rec->{'Weight'};
				
				## Fixed/Variable/Table Shipping ? 
				my $shpcal  = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'shipping_table');
				my $shpmdis = &load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'shipping_discount');
				($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$weight,$idpacking,$shpcal,$shpmdis,substr($rec->{'ID_products'},3,6));
				$va{'shptotal1'}=$shptotal1;
				$va{'shptotal2'}=$shptotal2;
				$va{'shptotal3'}=$shptotal3;
				$va{'shptotal1pr'}=$shptotal1pr;
				$va{'shptotal2pr'}=$shptotal2pr;
				$va{'shptotal3pr'}=$shptotal3pr;
				$comillitas=$rec->{'shp_type'};
				$totshpord=$va{'shptotal'.$comillitas.''};
			}
			$shippingb=$totshpord;
		}
		##########################
		#Se establece el Descuento
		##########################
		if($rec->{'DiscB'}==0 and $discountf==1) {
			if($rec->{'ID_products'} =~ /$cfg{'disc40'}/){
				$discb=$rec->{'SalePrice'}*$rec->{'Quantity'}*(40/100);
			}elsif ($rec->{'ID_products'} =~ /$cfg{'disc30'}/){
				$discb=$rec->{'SalePrice'}*$rec->{'Quantity'}*(30/100);
			}else{
				$fpago=&load_name('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'flexipago');
				$discb=($rec->{'SalePrice'}*$cfg{'fpdiscount'.$fpago}/100);
			}
		}

		####################
		#Se establece el Tax
		####################
		$taxb=0;
		$taxb=$in{'taxesapp'}*($rec->{'SalePrice'}-$discb);
		$taxb = 0 if($in{'taxesaction'} eq 'off');
		################
		#Se establece FP
		################
		$fpb=1;
		$shippingcad="Shipping=$shippingb," if $shippingf;
		&Do_SQL("UPDATE $cadtbproductstmp SET $shippingcad Tax=$taxb, Tax_percent = '$in{'taxesapp'}', Discount=$discb, FP=$fpb where $cadidorderproducts=$rec->{$cadidorderproducts};");
	}
}

sub process_edition{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 11/26/08 10:22:19
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 12/05/08 17:07:09
# Last Modified by: MCC C. Gabriel Varela S: Se contempla edición de precio.
# Last Modified on: 02/02/09 10:28:05
# Last Modified by: MCC C. Gabriel Varela S: Se agrega tax
# Last Modified on: 03/18/09 18:09:38
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se borren todos los datos previos de ese usuario.
# Last Modified on: 05/01/09 09:56:16
# Last Modified by: MCC C. Gabriel Varela S: Se pone tablename para registrar bien los logs.
# Last Modified RB: 06/30/09  09:20:16 -- Se agrega a lista de accounting para revision
#Last modified on 1 Jul 2011 16:21:57
#Last modified by: MCC C. Gabriel Varela S. :Insert notes of edition


	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();

	my ($sth,$rec);
	#############################################
	##################Productos##################
	#############################################
	my $notes_to_insert='';
	$sth=&Do_SQL("SELECT *,$cadidorderproducts,$cadidorders from $cadtbproductstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'} and Action!='Original'/* and comefrom!='Original'*/;");
	
	while($rec=$sth->fetchrow_hashref) {
		##Editados##
		&Do_SQL("UPDATE $cadtbproducts SET Quantity=$rec->{'Quantity'},Shipping=$rec->{'Shipping'},Tax=$rec->{'Tax'},Tax_percent='$rec->{'Tax_percent'}',Discount=$rec->{'Discount'},SalePrice=$rec->{'SalePrice'},FP=1,Status='$rec->{'Status'}'/*,ID_admin_users=$rec->{'ID_admin_users'}*/ where $cadidorderproducts=$rec->{$cadidorderproducts}")if($rec->{'Action'}eq'Edited');
		##Creados##
		&Do_SQL("INSERT INTO $cadtbproducts (ID_products ,$cadidorders ,Related_ID_products,Quantity ,SalePrice ,Shipping ,Tax, Tax_percent, Discount ,FP ,Status ,Date ,Time ,ID_admin_users )
							VALUES ('$rec->{'ID_products'}','$rec->{$cadidorders}','$rec->{'Related_ID_products'}','$rec->{'Quantity'}','$rec->{'SalePrice'}','$rec->{'Shipping'}','$rec->{'Tax'}','$rec->{'Tax_percent'}','$rec->{'Discount'}','$rec->{'FP'}','$rec->{'Status'}',CURDATE(),Now(),'$rec->{'ID_admin_users'}');")if($rec->{'Action'}eq'Created');
		$notes_to_insert.="Action:$rec->{'Action'}, Shipping=$rec->{'Shipping'},Discount=$rec->{'Discount'},SalePrice=$rec->{'SalePrice'},Status=$rec->{'Status'}\n";
	}
	
	#############################################
	##################Pagos######################
	#############################################
	$sth=&Do_SQL("SELECT *,$cadidorderpayments,$cadidorders from $cadtbpaymentstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'} and Action!='Original'/* and comefrom!='Original'*/;");
	while($rec=$sth->fetchrow_hashref)
	{
		##Editados##
		&Do_SQL("UPDATE $cadtbpayments set Amount=$rec->{'Amount'},Paymentdate='$rec->{'Paymentdate'}',Status='$rec->{'Status'}' where $cadidorderpayments=$rec->{$cadidorderpayments}")if($rec->{'Action'}eq'Edited');
		##Creados##
		&Do_SQL("INSERT INTO $cadtbpayments ($cadidorders ,Type ,PmtField1 ,PmtField2 ,PmtField3 ,PmtField4 ,PmtField5 ,PmtField6 ,PmtField7 ,PmtField8 ,PmtField9 ,Amount ,Reason , Paymentdate, Status ,Date ,Time ,ID_admin_users )
							VALUES ('$rec->{$cadidorders}','$rec->{'Type'}','$rec->{'PmtField1'}','$rec->{'PmtField2'}','$rec->{'PmtField3'}','$rec->{'PmtField4'}','$rec->{'PmtField5'}','$rec->{'PmtField6'}','$rec->{'PmtField7'}','$rec->{'PmtField8'}','$rec->{'PmtField9'}','$rec->{'Amount'}','$rec->{'Reason'}','$rec->{'Paymentdate'}','$rec->{'Status'}',CURDATE(),Now(),'$rec->{'ID_admin_users'}');")if($rec->{'Action'}eq'Created');
		$notes_to_insert.="Action:$rec->{'Action'},Amount=$rec->{'Amount'},Paymentdate=$rec->{'Paymentdate'},Status=$rec->{'Status'}\n";
	}
	&Do_SQL("INSERT INTO ".$cadtborders."_notes set $cadidorders='$in{$cadidorders}',Notes='$notes_to_insert',Type='Medium',Date=CURDATE(),Time=curtime(),ID_admin_users='$usr{'id_admin_users'}'");
	####En caso de tener return se inserta####
	
	if(&exists_return) {
		&add_return;
	}

	$in{'db'}=$cadtborders;
	&recalc_totals($in{$cadidorders});
	
	#####Borrar datos de tablas temporales#######
	&Do_SQL("DELETE FROM $cadtbproductstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'};");
	&Do_SQL("DELETE FROM $cadtbpaymentstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'};");
	&auth_logging('opr_orders_order_edited',$in{$cadidorders});
	
	$ttable = $cadtborders;
	$ttable =~ s/sl_//; 
	my $pd_order = &load_name('sl_orders','ID_orders',$in{$cadidorders},'PostedDate');
	if($pd_order and $pd_order ne '0000-00-00' and $cfg{'accounting_edit_order'}){
		my @list = split(/,/,$cfg{'accounting_edit_order'});
		for (0..$#list){
			&write_to_list("Edit $ttable",$ttable,$list[$_],0,$in{$cadidorders},$cadtborders);
		}
	}
}

sub UPDATE_updatables{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 12/03/08 12:13:07
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	#Se recorren los ins
	# Last Modified on: 12/05/08 11:04:00
# Last Modified by: MCC C. Gabriel Varela S: Se quita la llamada a adjust_edition. Se hace que se puedan editar los precios también.
# Last Modified on: 01/20/09 12:20:51
# Last Modified by: MCC C. Gabriel Varela S: Se valida que la cantidad concuerde con los valores restantes.
# Last Time Modified by RB on 04/15/2011 12:54:07 PM: Se agrega id_orders como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:20:07 PM : Se agrega City como parametro para calculate_taxes 
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my $key,$shipping,$discount,$cadshp,$caddisc,$oldshp,$olddisc,$bandedition=0,$cadamt,$amount,$oldamt,$cadprice,$sprice,$oldsprice;
	
	my $cadquantity,$cadunitprice,$quantity,$unitprice,$oldquantity,$oldunitprice;
	
	my $tax,$oldtax;
	
	if($in{'taxesaction'}eq'on')
	{
		#$in{'taxesapp'}=&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'OrderTax');
		$in{'taxesapp'}=&calculate_taxes(&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_Zip'),&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_State'),&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_City'),$in{$cadidorders});
		$va{'bandedition'}=1;
		#&cgierr("$in{'taxesapp'}");
	}
	elsif($in{'taxesaction'}eq'off')
	{
		delete($in{'taxesapp'});
		$va{'bandedition'}=1;
	}
	
	$va{'bandedition'}=0;
	foreach $key (sort(keys %in)) 
	{
		if(($key =~/^(upd_)(\d+)/))
		{
			$cadshp="shp_$2";
			$caddisc="disc_$2";
			$cadprice="price_$2";
			$cadquantity="quantity_$2";
			$cadunitprice="unitprice_$2";
			
			$shipping=$in{$cadshp};
			$discount=$in{$caddisc};
			$sprice=$in{$cadprice};
			$quantity=$in{$cadquantity};
			$unitprice=$in{$cadunitprice};
			
			$tax=0;
			$tax=$in{'taxesapp'};
			
			$oldshp=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'Shipping');
			$olddisc=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'Discount');
			$oldsprice=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'SalePrice');
			$oldquantity=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'Quantity');
			$oldunitprice=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'UnitPrice');
			
			$oldtax=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'Tax');
			
			#$quantity=&load_name("$cadtbproductstmp","$cadidorderproducts",$2,'Quantity');
			
			$shipping=$oldshp if($shipping eq '');
			$discount=$olddisc if($discount eq '');
			$sprice=$oldsprice if($sprice eq '');
			$quantity=$oldquantity if($quantity eq'');
			$unitprice=$oldunitprice if($unitprice eq'');
			
			$tax=$old_tax if($tax eq'');
			
			#Valida cambios
			if($oldunitprice==$unitprice and $oldsprice!=$sprice)
			{
				$unitprice=$sprice/$quantity;
			}
			else
			{
				$sprice=$unitprice*$quantity;
			}
			#&cgierr("if(($oldtax!=$tax or $oldunitprice!=$unitprice or $oldshp!=$shipping or $discount!=$olddisc or $sprice!=$oldsprice)and(($quantity<0 and $shipping<=0 and $discount<=0 and $sprice<=0)or($quantity>0 and $shipping>=0 and $discount>=0 and $sprice>=0)))");
			if(($oldtax!=$tax or $oldunitprice!=$unitprice or $oldshp!=$shipping or $discount!=$olddisc or $sprice!=$oldsprice)and(($quantity<0 and $shipping<=0 and $discount<=0 and $sprice<=0)or($quantity>0 and $shipping>=0 and $discount>=0 and $sprice>=0)))
			{
				$bandedition=1;
				$va{'bandedition'}=1;
				&Do_SQL("UPDATE $cadtbproductstmp set Shipping='$shipping',Discount='$discount',Quantity='$quantity',UnitPrice='$unitprice',SalePrice='$sprice',Action=if(comefrom!='Original',Action,'Edited') where $cadidorderproducts=$2");
				&calc_tmp_prod_fields($2,0);
			}
		}
		if(($key =~/^(updpa_)(\d+)/))
		{
			$cadamt="amt_$2";
			$cadpdate="pdate_$2";
			$amount=$in{$cadamt};
			$paymentdate=$in{$cadpdate};
			$oldamt=&load_name("$cadtbpaymentstmp","$cadidorderpayments",$2,'Amount');
			$oldpdate=&load_name("$cadtbpaymentstmp","$cadidorderpayments",$2,'Paymentdate');
			$amount=$oldamt if($amount eq "");
			$paymentdate=$oldpdate if($paymentdate eq "");
			if(($oldamt ne $amount and $amount ne "") or ($oldpdate ne $paymentdate and $paymentdate ne ""))
			{
				&Do_SQL("UPDATE $cadtbpaymentstmp set Amount='$amount',Reason=IF($amount > 0,Reason,'Other'),Paymentdate='$paymentdate',Action=if(comefrom!='Original',Action,'Edited') where $cadidorderpayments=$2");
			}
		}
  }
}

sub return_in_order{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/12/09 16:42:23
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	return 0 if($in{'edit_type'}eq"pre");
	my($id_orders_products)=@_;
	$sth=&Do_SQL("SELECT count(*) FROM `sl_returns` WHERE ID_orders_products=$id_orders_products and Status!='Void'");
	return $sth->fetchrow;
}

sub check_values{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 01/20/09 10:39:27
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	$sth=&Do_SQL("SELECT count($cadidorders) from $cadtbproducts where ((Quantity>0 and (SalePrice<=0 or Shipping<=0 or Tax<=0 or Discount<=0))or(Quantity<0 and (SalePrice>=0 or Shipping>=0 or Tax>=0 or Discount>=0))) and Action!='Original' and $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'}");
	return $rec=$sth->fetchrow;
}

sub last_id_products{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/07/09 10:20:09
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	my $sth=&Do_SQL("SELECT left(ID_products,3)+1 from $cadtbproductstmp where $cadidorders=$in{$cadidorders} and ID_admin_users=$usr{'id_admin_users'} order by ID_orders_products desc limit 1");
	my $nextid=$sth->fetchrow();
	return 100 if(!$nextid);
	return $nextid;
}

sub taxes_actions{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 08/10/09 10:19:57
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Time Modified by RB on 04/15/2011 12:55:02 PM : Se agrega id_orders como parametro para funcion calculate_taxes
# Last Modified by RB on 06/07/2011 01:19:14 PM : Se agrega City como parametro para calculate_taxes

	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	if($in{'taxesaction'} eq 'on'){
		$in{'taxesapp'}=&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'OrderTax');
		$in{'taxesapp'}=&calculate_taxes(&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_Zip'),&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_State'),&load_name("$cadtborders","$cadidorders",$in{$cadidorders},'shp_City'),$in{$cadidorders});
		$va{'bandedition'}=1;
		#&cgierr("$in{'taxesapp'}");
	
	}elsif($in{'taxesaction'}eq'off'){
		delete($in{'taxesapp'});
		$va{'bandedition'}=1;
	}
}

sub verify_credits_vs_debits{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 30 Jun 2011 16:07:14
# Author: MCC C. Gabriel Varela S.
# Description :   It verifies if there are editable credits and debits at the same time.
# Parameters :
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	$sth=&Do_SQL("SELECT if(sum(if(Amount>0,1,0))>0 and sum(if(Amount<0,1,0))>0,1,0)as bothmovements
	from $cadtbpaymentstmp
	where $cadidorders=$in{$cadidorders} 
	and ID_admin_users=$usr{'id_admin_users'}
	/*and Action!='Original'*/
	and ((Type='Check'
				and not((((Status!='Approved'
									 or AuthCode='0000')
									or (Status='Approved'
											and (AuthCode='0000'
													 or AuthCode=''
													 or isnull(AuthCode)))))
								or Status='Cancelled'
								or Status='Order Cancelled'
								or Status='Void'))
				or (Type='credit-card'
						and not(not((((Amount<0
													 and Status!='Credit by Monterey')
													or( Status!='Cancelled'
															and Status!='Order Cancelled'
															and Status!='Void'
															and Status!='Credit by Monterey'
															and ((Status!='Approved'
																		or AuthCode='0000')
																	 or (Status='Approved'
																			 and (AuthCode='0000'
																						or AuthCode=''
																						or isnull(AuthCode))))))
												 and not((Captured!='No' and Captured!='' and not isnull(Captured))
																 or Status='Order Cancelled'
																 or Status='Order Cancelled'
																 or Status='Void')
												 and not(AuthCode!='' and AuthCode!='0000' and not isnull(AuthCode))))
										or (Status='Cancelled'
												or Status='Order Cancelled'
												or Status='Void')))
				or (Type='westernunion'
						and not((Status!='Approved'
										 or AuthCode='0000')
										or(Status='Cancelled'
											 or Status='Order Cancelled'
											 or Status='Void')))
				or (not(not((((Amount<0
											 and Status!='Credit by Monterey')
											or( Status!='Cancelled'
													and Status!='Order Cancelled'
													and Status!='Void'
													and Status!='Credit by Monterey'
													and ((Status!='Approved'
																or AuthCode='0000')
															 or (Status='Approved'
																	 and (AuthCode='0000'
																			  or AuthCode=''
																			  or isnull(AuthCode))))))
										 and not((Captured!='No' and Captured!='' and not isnull(Captured))
														 or Status='Order Cancelled'
														 or Status='Order Cancelled'
														 or Status='Void')
										 and not(AuthCode!='' and AuthCode!='0000' and not isnull(AuthCode))))
								or (Status='Cancelled'
										or Status='Order Cancelled'
										or Status='Void'))) )");
	return $sth->fetchrow;
}


1;
