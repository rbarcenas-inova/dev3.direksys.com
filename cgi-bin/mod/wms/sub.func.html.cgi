#!/usr/bin/perl
####################################################################
########              Home Page                     ########
####################################################################

sub wreceipt_itemlist {
# --------------------------------------------------------
	my ($output);
	(!$in{'totallines'}) and ($in{'totallines'}=1);
	
	for $i(1..$in{'totallines'}){
		$va{'line'} = $i;
		$in{'id_products'} = $in{'id_products'.$i};
		$in{'serial'} = $in{'serial'.$i};
		$in{'qty'} = $in{'qty'.$i};
		$error{'iderror'} = $error{'iderror'.$i} ."<br>";
		$error{'qtyerror'} = $error{'qtyerror'.$i} ."<br>";
		$output .= &build_page('wreceipt_itemlist.html');
	}
	return $output;
}

#GV Inicia
sub warehouseadjsmain{
# --------------------------------------------------------
	#MCC C Gabriel Varela S 
	#4/Apr/2008 10:10
	
	my ($line,$dif,$returnw);
	my ($OIdprod,$OQty,$OPrice);
	my ($WQty,$adjsuccess);
	open(WHA,"./adjfiles/inventory.csv");
	while(<WHA>)
	{
		$adjsuccess=0;
		$line = $_;
		$line =~ s/\r|\n//g;
		($OIdprod,$OQty,$OPrice)=split(/,/,$line);
		if(length($OIdprod)==6)
		{
			$OIdprod="100".$OIdprod;
			#$OIdprod=~/(\d+)-(\d+)-(\d+)/g;
			#$OIdprod=$1.$2.$3;
		}
#		elsif(length($OIdprod)==7)
#		{
#			$OIdprod=~/(\d+)-(\d+)/g;
#			$OIdprod='100'.$1.$2;
#		}
		$WQty=&getinfoware($OIdprod);
		$dif=$OQty-$WQty;
		if($dif>0)
		{
			$adjsuccess=&adj_pos($OIdprod,abs($dif),$OPrice);
		}
		elsif($dif<0)
		{
			$adjsuccess=&adj_adjustments($OIdprod,abs($dif));
		}
		if($adjsuccess==1)
		{
			$adjsuccess="Adjusted";
		}
		else
		{
			$adjsuccess="Not Adjusted:".$adjsuccess;
		}
		$returnw.="<tr>
								<td>".$OIdprod.'</td>
								<td>'.$OQty.'</td>
								<td>'.$OPrice."</td>
								<td>".$dif."</td>
								<td>".$adjsuccess."</td>
							</tr>";
	}
	return $returnw;
}

sub getinfoware{
# --------------------------------------------------------
	#MCC C Gabriel Varela S 
	#4/Apr/2008 11:46
	my ($OIdprod)=@_;
	my ($numhits);
	$cons=$DBH->prepare('SELECT sum(sl_warehouses_location.Quantity) as Qty
												FROM sl_warehouses_location
												WHERE sl_warehouses_location.ID_products ='.$OIdprod.'
												group by sl_warehouses_location.ID_products');
	$cons->execute;
	$numhits = $cons->rows();
	if(!$numhits)
	{
		return $numhits;
	}
	my $row_rsRmatypes=$cons->fetchrow_hashref();
	return $row_rsRmatypes->{"Qty"};
}

#sub adj_pos{
## --------------------------------------------------------
#	#MCC C Gabriel Varela S 
#	#4/Apr/2008 12:49
#	# Last Modification by JRG : 03/13/2009 : Se agrega log
#	# Last Modified on: 06/08/09 17:05:57
## Last Modified by: MCC C. Gabriel Varela S: Se comenta.
#	my ($IDW_product,$difabs,$OPrice)=@_;
#	my ($str1,$str2,$str3,$str4);
#	&Do_SQL("START TRANSACTION");
#	$str3 = &Do_SQL("INSERT INTO sl_adjustments
#												(Title,Comments,Status,Date,Time,ID_admin_users) values 
#												('".$IDW_product."','Ajuste para incrementar inventario','New',Curdate(),NOW(),".$usr{'id_admin_users'}.")");
#	my ($strli) = &Do_SQL("SELECT LAST_INSERT_ID()");
#	my ($idadj) = $strli->fetchrow;
#	$str4 = &Do_SQL("INSERT INTO sl_adjustments_items
#												(ID_adjustments,ID_products,Qty,Price,Date,Time,ID_admin_users) values 
#												(".$idadj.",".$IDW_product.",".$difabs.",".$OPrice.",Curdate(),NOW(),".$usr{'id_admin_users'}.")");
#	$str1 = &Do_SQL("INSERT INTO sl_warehouses_location 
#												(ID_warehouses,ID_products,Location,Quantity,Date,Time,ID_admin_users) values 
#												(1003,".$IDW_product.",'A00A',".$difabs.",Curdate(),NOW(),".$usr{'id_admin_users'}.")");
#	$str2 = &Do_SQL("INSERT INTO sl_skus_cost
#												(ID_products,ID_purchaseorders,ID_warehouses,Tblname,Quantity,Cost,Date,Time,ID_admin_users) values 
#												(".$IDW_product.",".$idadj.",'1003','sl_adjustments',".$difabs.",".$OPrice.",Curdate(),NOW(),".$usr{'id_admin_users'}.")");
# 	if($str1 ne '' and $str2 ne '' and $str3 ne '' and $str4 ne '')
# 	{
# 		&auth_logging('adjustment_added',$idadj);
# 		&auth_logging('sl_adjustments_itemasdded',$str4->{'mysql_insertid'});
# 		&auth_logging('warehouses_location_added',$str1->{'mysql_insertid'});
# 		&auth_logging('sku_cost_added',$str2->{'mysql_insertid'});
#		return 1;
#	}
#	else
#	{
#		return 0;
#	}
#}




#JRG start#

sub customerdata {
# --------------------------------------------------------
# Created by: Jose Ramirez Garcia
# Created on: 30abr2008
# Description : It shows the customer data
# Notes : (Modified on : Modified by :)

	if(!$in{'id_customers'} && $in{'id_returns'}){
		my ($sth0) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_returns='$in{'id_returns'}'");
		if ($sth0->fetchrow() >0){
			my ($sth0) = &Do_SQL("SELECT ID_orders FROM sl_returns,sl_orders_products WHERE sl_orders_products.ID_orders_products=sl_returns.ID_orders_products AND ID_returns='$in{'id_returns'}'");
			$in{'id_orders'} = $sth0->fetchrow();
			$in{'id_customers'} = &load_name('sl_orders','ID_orders',$in{'id_orders'},'ID_customers');
		}
	}
	
	if ($in{'id_customers'} ){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
		if ($sth->fetchrow() >0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
			my ($tmp) = $sth->fetchrow_hashref();
			foreach $key (keys %{$tmp}){
				$in{"customers.".lc($key)} = $tmp->{$key};
			}
			return &build_page("customerdata.html");
		}
	}
}



  sub updateinventory {
# --------------------------------------------------------	
#Accion: Creacian
#Comentarios:
# Forms Involved: \cgi-bin\templates\en\forms\retwarehouse_view.html
# Created on: 05/may/2008 08:22AM GMT -0600
# Last Modified on: 16jun2008
# Last Modified by: MCC C. Gabriel Varela S.
# Author: MCC C. Gabriel Varela S.
# Description :  Hara los ajustes de inventario segan los registros de returns
# Parameters :
# Description16jun2008 :  Se cambia Damaged por NC Damaged
# Last Modified on: 27/jun/2008
# Last Modified by: MCC C Gabriel Varela S
#Obtiene la informacian del registro de return
# Last Modified on: 30/jun/2008
# Last Modified by: MCC C Gabriel Varela S
#Se corrigen consultas para obtener totales correctos y reales.
# Last Modified on: 07/01/2008
# Last Modified by: MCC C Gabriel Varela S
# Se corrige opcian de exchange, cuando el merAction sea exchange tambian, entonces se va a considerar el cambio
# Last Modified on: 07/09/2008
# Last Modified by: MCC C Gabriel Varela S
# Se corrige la consulta SQL
# Last Modified on: 07/17/08 15:42:36
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la consulta SQL para contemplar salo el producto de sl_orders_products al que hace referencia el return
# Last Modified on: 08/11/08 11:22:36
# Last Modified by: MCC C. Gabriel Varela S: Cuando se hagan nuevos pagos, se pondra el campo PostedDate en now() o curdate()
# Last Modified on: 08/26/08 13:22:35
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se ponga en 0 o en 1 el valor que tiene el return dependiendo de si los campos ATCReturnFees y ATCRestockFees son Applicables o no. Tambian se cambia que ahora se va a mandar llamar la funcian actionsfunction dependiendo del campo merAction y no del tipo de return
# Last Modified on: 08/27/08 10:32:42
# Last Modified by: MCC C. Gabriel Varela S: Se quita la parte de cuando el producto IsFinal y que no se inserten pagos cuando la cantidad es cero
# Last Modified on: 09/02/08 09:47:01
# Last Modified by: MCC C. Gabriel Varela S: Se incluyen los campos OldShpReturn y NewShp de sl_returns para determinar las acciones que se haran
# Last Modified on: 09/02/08 09:57:11
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la forma en que se llama a actionsfunction, ya que no existe mas el parametro addprshippingnew
# Last Modified on: 09/04/08 13:00:06
# Last Modified by: MCC C. Gabriel Varela S: Se tomara en cuenta la aplicacian del nuevo envao siempre que la accian de return sea exchange o reship
# Last Modified on: 09/08/08 10:56:50
# Last Modified by: MCC C. Gabriel Varela S: Se graba la cantidad del return en el nuevo campo de sl_returns: Amount
# Last Modified on: 09/10/08 09:30:10
# Last Modified by: MCC C. Gabriel Varela S: Se ve la forma en que se calculara el descuento
# Last Modified on: 09/29/08 11:04:48
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el posteddate se establezca salo si el tipo de return es refund al insertar el pago
# Last Modified on: 09/30/08 16:50:54
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta el nuevo campo Reason de sl_orders_payments
# Last Modified on: 12/15/08 13:02:18
# Last Modified by: MCC C. Gabriel Varela S: No se estaba tomando en cuenta UPC de ningan lado
# Last Modification by JRG : 03/13/2009 : Se agrega log
# Last Modified on: 03/17/09 17:05:55
# Last Modified by: MCC C. Gabriel Varela S: Parametros sltv_itemshipping
# Last Modified RB: 06/22/09  10:10:03 -- Se genera el movimiento contable transitorio que devuelve virtualmente el dinero al cliente &accounting_aux_return($idorders). La funcion esta en sub.finance_2.html.cgi
# Last Modified RB: 09/01/09  11:38:14 -- Se corrigio el problema del shipping positivo en los returns. Tambien en los refund, cuando se procesa mas de un producto, los refunds anteriores no cobrados se cancelan para dejar activo el amount que agrupa todos los refuns.
# Last Modified RB: 09/14/09  12:25:04 -- Se cambio la linea de cancelacion de pagos/creditos pendientes para refund despues de haber hecho los movimientos contables.
# Last Modified RB: 09/21/09  17:28:54 -- Se toman en cuenta valores a 0.99 para sumatoria.
# Last Modified RB: 098/06/2010  17:55:54 -- Se corrige la extraccion de datos de la TDC a donde hacer el cargo/refund resultante, se estaba extrayendo la primer tarjeta que no estuvera capturada, debe ser la TDC mas recientemente con captura/authcode.
# Last Modified By RB on 12/16/2010 : Se agregan parametros para calculo con shipping_table
# Last Modified by RB on 06/07/2011 12:57:59 PM : Se cambian los valores de State y Zip por shp_State y shp_Zip y se agrega shp_City

	
	$id_orders_products=&load_name('sl_returns','ID_returns',$in{'id_returns'},'ID_orders_products');
	$id_products=&load_name('sl_orders_products','ID_orders_products',$id_orders_products,'ID_products');

	my($sth)=&Do_SQL("SELECT UPC,id_sku_products as ID_products, sl_returns.ID_returns, sl_orders_products.Saleprice, sl_products.SPrice, 
					sl_returns.Type, sl_products.Isfinal, sl_orders_products.Shipping, sl_orders_products.Cost, 
					sl_orders_products.SerialNumber, sl_orders_products.Tracking, sl_orders_products.ShpProvider, 
					sl_orders_products.Status, sl_orders_products.ID_packinglist, sl_returns.ID_products_exchange, 
					sl_orders.OrderNet, sl_orders.shp_type, sl_orders_products.ID_orders, sl_products.flexipago, 
					sl_orders.shp_State, sl_orders.shp_Zip, sl_orders.shp_City, sl_returns.merAction, 
					if(ATCReturnFees='Applicable',1,0)as ATCReturnFees,if(ATCRestockFees='Applicable',1,0)as ATCRestockFees,
					if(OldShpReturn='Applicable',1,0)as OldShpReturn,if(NewShp='Applicable',1,0)as NewShp, 
					sl_orders_products.Discount
					FROM sl_returns
					LEFT JOIN sl_skus ON ( $id_products = sl_skus.id_sku_products ) 
					LEFT JOIN sl_orders_products ON ( sl_orders_products.ID_orders_products = sl_returns.ID_orders_products ) 
					LEFT JOIN sl_products ON (sl_products.id_products=right($id_products,6) )
					LEFT JOIN sl_orders ON ( sl_orders_products.ID_orders = sl_orders.ID_orders ) 
					WHERE sl_returns.ID_returns =$in{'id_returns'} AND not isnull(sl_products.ID_products)
					");
	my $adddone=0;
	my $addshpdone=0;
	my $shippingdone=0;
	my $restockdone=0;
	my $flexivoiddone=0;
	my $sumatoria=0;
	my $shippingamount=0;
	my $fees=0;
	my $idorders=0;
	my $diff;

	while($rec=$sth->fetchrow_hashref()){

		$idorders = $rec->{'ID_orders'};
		#Exchange or Undeliverable wrong address Re-ship
		
		if($rec->{'merAction'}eq'Exchange' or $rec->{'merAction'}eq'ReShip')#($rec->{'Type'}eq'Exchange' or $rec->{'Type'}eq'Undeliverable Wrong Address')
		{
			#$rec->{'ID_products_exchange'}=$rec->{'ID_products'} if($rec->{'merAction'}eq'ReShip');
			($adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$fees)=&actionsfunction($rec,1,1,0,1,1,1,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$rec->{'ID_returns'});
		
		}elsif($rec->{'merAction'}eq'Refund') { #($rec->{'Type'}eq'Returned for Refund' or $rec->{'Type'}eq'Undeliverable Intercepted')
			#Return/Refund or #Undeliverable Intercepted no Re-ship
			#&cgierr("1,0,1,1,1,0,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$rec->{'ID_returns'}");
			($adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$fees)=&actionsfunction($rec,1,0,1,1,1,0,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$rec->{'ID_returns'});
			&auth_logging('orders_products_updated',$rec->{'ID_orders'});
		}

		#Return Final Sale
#		elsif($rec->{'Isfinal'}eq'Yes')
#		{
#			if($rec->{'sl_returns_upcs.Status'}eq'NC Damaged')
#			{
#				($adddone,$addshpdone,$shippingdone,$fees)=&actionsfunction($rec,1,0,0,1,1,1,0,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$rec->{'ID_returns'});
#			}
#			else
#			{
#				($adddone,$addshpdone,$shippingdone,$fees)=&actionsfunction($rec,0,0,0,1,1,1,0,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$rec->{'ID_returns'});
#			}
#		}
		#Undeliverable refused Re-ship or Undeliverable 3 attempts Re-ship
#		elsif($rec->{'Type'}eq'Undeliverable Refused by Cust' or $rec->{'Type'}eq'Undeliverable Not Delivery 3 Attempt')
#		{
#			($adddone,$addshpdone,$shippingdone,$fees)=&actionsfunction($rec,1,1,1,0,1,1,0,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$rec->{'ID_returns'});
#		}
		if($in{"upc_$rec->{'UPC'}"}){

			#Actualiza Location de UPC
			$lu=&Do_SQL("Update sl_returns_upcs set ID_warehouses='".$in{"upc_$rec->{'UPC'}"}."' where ID_returns =$in{'id_returns'}");#if($in{'status'}eq'Resolved');
			&auth_logging('returns_upcs_updated',$in{'id_returns'});
		
		}

		#Se calcula el monto de envao por si la accian es Exchange
		$totshpord=0;
		if($rec->{'NewShp'} and ($rec->{'merAction'}eq"Exchange" or $rec->{'merAction'}eq"ReShip")){ 

			($rec->{'ID_products_exchange'} eq '') and ($rec->{'ID_products_exchange'} = $rec->{'ID_products'});
			#$in{'ID_products_exchange'}=$rec->{'ID_products_exchange'} if (!$in{'ID_products_exchange'});
			#$in{'ID_products_exchangea'}=$in{'ID_products_exchange'};
			$idpacking = &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'ID_packingopts');
			$edt= &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'edt');
			$sizew=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SizeW');
			$sizeh=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SizeH');
			$sizel=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SizeL');
			$discflex=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'flexipago');
			$size=$sizew*$sizeh*$sizel;
			$weight=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'Weight');
			
			## Fixed/Variable/Table Shipping ? 
			my $shpcal  = &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'shipping_table');
			my $shpmdis = &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'shipping_discount');
			($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$weight,$idpacking,$shpcal,$shpmdis,substr($rec->{'ID_products_exchange'},3,6));
			$cad="$shptotal".$rec->{'shp_type'};
			$va{'shptotal1'}=$shptotal1;
			$va{'shptotal2'}=$shptotal2;
			$va{'shptotal1pr'}=$shptotal1pr;
			$va{'shptotal2pr'}=$shptotal2pr;
			$comillitas=$rec->{'shp_type'};
			$totshpord=$va{'shptotal'.$comillitas.''};#$cad;#$shptotal.$rec->{'shp_type'};
		}
		$totshpord-=$rec->{'Shipping'} if($rec->{'OldShpReturn'});
		$shipping=", Shipping=$totshpord" if ($totshpord);
		$shippingamount=$totshpord if ($totshpord);

	}
	
	## Movimientos Contables
	my ($order_type, $ctype, $ptype,@params);
	my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$idorders';");
	($order_type, $ctype) = $sth->fetchrow();
	@params = ($idorders,$in{'meraction'},$fees);
	&accounting_keypoints('order_products_returnsolved_'. $ctype .'_'. $order_type, \@params );

	
	#Pendiente Actualizar total de ordenes, ya sea aqua o en la funcion actionsfunction
	#Nota Importante: Tomar en cuenta todo: Discounts, Taxes, Envaos, Cantidades, y todo mas
	#Pendiente por hacer: La sumatoria de los productos quizas se deba calcular aqua, despuas de haber recorrido todos los UPCs del return
	#Pendiente Calcular el monto de payments aprobados y asignarlos a $paymentsaprobados
	
	if($in{'meraction'} eq "Refund"){
		&Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders =  $idorders AND (Captured='No' OR Captured IS NULL) AND (CapDate IS NULL OR CapDate='0000-00-00'); ");
	}

	my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders = $idorders
			AND Status = 'Approved' AND 
			(Captured='Yes' OR (AuthCode IS NOT NULL AND AuthCode != '' AND AuthCode != '0000'))
			ORDER BY ID_orders_payments DESC LIMIT 1;");
	my ($rec2) = $sth2->fetchrow_hashref;

	$queryPmt = '';
	for my $i(1..9){
		$queryPmt .= ",PmtField$i = '".$rec2->{'PmtField'.$i.''}."' ";
	}
	
	## Products + Tax + Shipping vs Payments already done
	$sumatoria = &orderbalance($idorders);#+$shippingamount;
	my $posteddate = "";
	my $statuspayments='Approved';
	$statuspayments='Credit' if($sumatoria<0);
	
	if($sumatoria < 0.99*-1 or $sumatoria > 0.99){
	
		&Do_SQL("INSERT INTO sl_orders_payments SET ID_orders = $rec2->{'ID_orders'}, Reason='$in{'meraction'}',
							Type= '$rec2->{'Type'}' $queryPmt , Amount = '$sumatoria' , PaymentDate = CURDATE()  $posteddate,Status='$statuspayments',
							Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
				&auth_logging('orders_payments_added',$rec2->{'ID_orders'});
				my ($sthliid)=&Do_SQL("SELECT last_insert_id(ID_orders_payments)as last from sl_orders_payments order by last desc limit 1");
				$lastid=$sthliid->fetchrow();
				#$lli=&Do_SQL("Update sl_returns set Amount='$sumatoria' where ID_returns=$in{'id_returns'};");
				$in{'amount'}=$sumatoria;
				&proccessamount($sumatoria,$rec2->{'ID_orders'},$lastid);
	}else{
		$sumatoria=0;
	}
	&payments_financed($idorders) if($in{'meraction'}eq"Refund");
	&recalc_totals($idorders);
}


sub payments_financed{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/29/08 13:49:20
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified on: 09/30/08 16:50:54
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta el nuevo campo Reason de sl_orders_payments
# Last Modified on: 10/02/08 12:51:37
# Last Modified by: MCC C. Gabriel Varela S: Se pone el mismo posteddate que el registro de devolucian al cliente en caso de que exista posteddate
# Last Modification by JRG : 03/13/2009 : Se agrega log
	my ($idorder) = @_;
	my ($sth,$rec);
	$sth=&Do_SQL("SELECT IF(SUM(Amount) IS NULL,0,SUM(Amount)) FROM sl_orders_payments WHERE ID_orders =$idorder AND STATUS IN ('Financed') and ((CapDate!='0000-00-00') or (not isnull(AuthCode) and AuthCode!=''))");
	$rec=$sth->fetchrow;
	if($rec)
	{
		my $posteddate;
		$posteddate="";
		#$posteddate=",PostedDate = CURDATE() " if ($in{'meraction'}eq"Refund");
		my ($sth2) = &Do_SQL("SELECT * FROM sl_orders_payments WHERE ID_orders =$idorder
													AND (Status NOT IN ('Approved', 'Chargeback')
													OR (AuthCode IS NULL OR AuthCode = '' OR AuthCode != '0000'))
													ORDER BY ID_orders_payments LIMIT 1 ");
		my ($rec2) = $sth2->fetchrow_hashref;
		my $queryPmt = '';
		for my $i(1..9){
				$queryPmt .= ",PmtField$i = '".$rec2->{'PmtField'.$i.''}."' ";
		}
		my($sthg)=&Do_SQL("SELECT posteddate FROM `sl_orders_payments` WHERE id_orders =70546 AND date = Curdate() AND NOT isnull( posteddate )");
		my($recg)=$sthg->fetchrow();
		$posteddate=",Posteddate='$recg'"if($recg);
		&Do_SQL("INSERT INTO sl_orders_payments SET ID_orders = $rec2->{'ID_orders'}, Reason='Refund',
							Type= '$rec2->{'Type'}' $queryPmt , Amount = -1*$rec , PaymentDate = CURDATE()  $posteddate, Status='Credit by Monterey',
							Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");
		&auth_logging('orders_payments_added',$rec2->{'ID_orders'});
	}
}

#GV Termina 05may2008
#GV Inicia 13jun2008
sub proccessamount {

	# Created on: 13/jun/2008 01:08:29 AM
	# Last Modified on: 130/jun/2008
	# Last Modified by: MCC C Gabriel Varela S
	# Author: MCC C Gabriel Varela S
	# Description : Evaluara qua tipo de movimiento se hara (cobro o cradito) y si se hara o no
	# Parameters : 
	#								$diff:Es el amount del return
	#								$id_order: El id de la orden
	#								$id_payment:Id del pago
	# Description18jun2008 : Se verificara si la orden tenaa malos totales. De ser asa, no se hara ningan movimiento
	# Last Modified on: 09/10/08 15:50:11
	# Last Modified by: MCC C. Gabriel Varela S: Se muestra el status de las funciones.
	# Last Modified on: 09/25/08 18:03:14
	# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando sea un tipo de return con action igual a Refund, se establezca el posteddate a now()
	# Last Modified on: 09/29/08 16:38:31
# Last Modified by: MCC C. Gabriel Varela S: Se hace que la cantidad sea negativa al llamar a sltvcyb_credit
# Last Modified on: 10/02/08 12:27:08
# Last Modified by: MCC C. Gabriel Varela S: Al procesar el refund con autorizacian se hara la actualizacian de todos los pagos para la orden en posteddate que cumplan las condiciones, anteriormente salo era para el pago referido en el parametro
# Last Modified on: 10/21/08 10:44:03
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el status del return dependa de ciertas acciones
# Last Modified by RB on 11/18/08 at 10:18:10 - Se agrego el Status Pending Refunds para devolucion de dinero y el parametro limite se puso a "0", por lo que los returns siempre se van a algun status de Pending
# Last Modification by JRG : 03/13/2009 : Se agrega log
# Last Modified RB: 04/01/09  12:25:51 -- Se agrega lista para diff=0



	 require ("../../common/apps/cybersubs.cgi");

	# Last Modified on: 09/10/08 15:11:26
	# Last Modified by: MCC C. Gabriel Varela S: Se muestra el error cuando hay error en los totales
	($diff,$id_order,$id_payment)=@_;
	$va{'message'}.=" Return amount: ".&format_price($diff);
	if(abs($diff)>$cfg{'returnamountlimit'})
	{
		my $sthdenied=&Do_SQL("insert into cleanup_temp set ID_orders=$id_order,Message='The return amount ($diff) is greater than $cfg{'returnamountlimit'}'");
		$in{'status'}="Pending Payments" if $diff > 0;
		$in{'status'}="Pending Refunds"  if $diff < 0;
		$va{'message'}.=" The sale/credit movement has not been done. The Return's amount is greater than the permited USD\$".$cfg{'returnamountlimit'}." limit.<br>
											The Return Status has changed to $in{'status'}.";
	}
	elsif($in{'badtotals'}==1)
	{
		my $sthdenied=&Do_SQL("insert into cleanup_temp set ID_orders=$idorder,Message='Error with order totals.'");
		$va{'message'}.=" Error with order totals: $in{'checkmsg'} The sale/credit movement has not been done.";
		$in{'status'}="Pending Payments";
	}
	else
	{
		if($diff>0)
		{
			($status,$statmsg) = &sltvcyb_sale($id_order,$id_payment) ;#if($in{'status'}eq'Resolved');
			$va{'message'}.=" Sale/Credit movement status: $status,$statmsg";
		}
		elsif($diff<0)
		{
			($status,$statmsg) = &sltvcyb_credit($id_order,$id_payment) ;#if($in{'status'}eq'Resolved');
			$va{'message'}.=" Sale/Credit movement status: $status,$statmsg";
		}
		else
		{
			#La diferencia es 0
			$status="OK";
			&autolist_returnspl($id_order)	if	$cfg{'returnspl'}==1;
		}
		
		
		if($status eq"OK")
		{
			$in{'status'}="Resolved";
		}
		else
		{
			$in{'status'}="Pending Payments" if $diff > 0;
			$in{'status'}="Pending Refunds"  if $diff < 0;
		}
		if($in{'meraction'}eq"Refund")# and $status eq "OK")Pendiente: Descomentar
		{
			#Entonces se hara la actualizacian de posteddate
			&Do_SQL("Update sl_orders_payments set PostedDate=Curdate() where ID_orders=$id_order and isnull(PostedDate)");
			&auth_logging('orders_payments_updated',$id_order);
			&Do_SQL("Update sl_orders_products set PostedDate=Curdate() where (isnull(PostedDate) and (Quantity=-1 or ID_products like '6%$cfg{'returnfeeid'}' or ID_products like '6%$cfg{'restockfeeid'}' or ID_products like '6%$cfg{'extwarrid'}') and ID_orders=$id_order)");
			&auth_logging('orders_products_updated',$id_order);
		}
	}
}
#GV Termina 13jun2008

sub actionsfunction {
	#Accian: Creacion
	#Comentarios:
	# --------------------------------------------------------
	# Forms Involved: \cgi-bin\templates\en\forms\retwarehouse_view.html
	# Created on: 06/may/2008 10:58AM GMT -0600
	# Last Modified on: 27/jun/2008
	# Last Modified by: MCC C. Gabriel Varela S.
	# Author: MCC C. Gabriel Varela S.
	# Description :  Hara las acciones que se seleccionen segan el tipo de return
	# Parameters :$rec=registro de tabla
	#							$addprnegativeproduct=Interruptor que determina si se agregara un producto con valores negativos
	#							$addprexchangeproduct=Interruptor que determina si se agregara un producto deseado
	#							$addprreturnfee=Interruptor que determina si se cargara un servicio Return Fee
	#							$addprshippingnew=Interruptor que determina si se sumara una cuota de envao por el nuevo producto
	#							$addprrestockfee=Interruptor que determina si se agregara un servicio Restock Fee
	#							$payflexvoid=Interruptor que determina si se actualizaran los flexipagos 'Pending' en 'Void' para la orden
	#							$paysum=Interruptor que determina si se Actualizaran los pagos o los craditos
	#							$notfinance=Interruptor que determina si se Notificara Finance
	#							$notreship=Interruptor que determina si se aNotificara No Re-Ship
	#							$adddone=Bandera que determina si ya se agrega un producto deseado
	#							$addshpdone=Bandera que determina si ya se agrega el monto del servicio Return Fee para un producto deseado
	#							$shippingdone=Bandera que determina si ya se agrega el monto de envao para un producto deseado
	#							$restockdoneBandera que determina si ya se agrega el monto del servicio Restock Fee para un producto deseado
	#							$flexivoiddone=Bandera que determina si ya se actualizaron los pagos
	#							$sumatoria=contendra la suma de los productos quitados o agregados
	#							$id_returns=Es el ID del return
# Last Modified on: 27/jun/2008
# Last Modified by: MCC C Gabriel Varela S	
# Last Modified on: 08/26/08 11:32:42
# Last Modified by: MCC C. Gabriel Varela S: Se hace que se tome en cuenta el precio de un producto en exchange en base a su ID. Tambian se toman en cuenta ahora los campos ATCReturnFees y ATCRestockFees para determinar si los servicios aplican o no, por lo tanto, se quitan tales parametros. Tambian se hace que se aplique el monto del nuevo envao para el cliente segan el diagrama de returns
# Last Modified on: 09/02/08 09:50:43
# Last Modified by: MCC C. Gabriel Varela S: Se quita parametro $addprshippingnew, ya que se determinara por medio del campo NewShp de sl_returns
# Last Modified on: 09/03/08 09:25:57
# Last Modified by: MCC C. Gabriel Varela S: Cuando el tipo de return es ReShip, se debe conservar el (los) precio(s) original(es) de(l) producto(s)
# Last Modified on: 09/04/08 10:56:23
# Last Modified by: MCC C. Gabriel Varela S: Se hace que cuando el tipo de returns es Exchange, pero se cumple que es el mismo id de producto, los precios se mantengan igual
# Last Modified on: 09/04/08 16:48:18
# Last Modified by: MCC C. Gabriel Varela S: Se agrega funcian &calc_tax_disc_shp
# Last Modified on: 09/09/08 09:29:42
# Last Modified by: MCC C. Gabriel Varela S: Se ve la forma de calcular el descuento en los productos que se agregan
# Last Modified on: 09/10/08 12:24:53
# Last Modified by: MCC C. Gabriel Varela S: Cuando es ReShip, se hace que los campos sean iguales en todo.
# Last Modified on: 09/29/08 13:43:25
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el posteddate sea dependiente de la variable
# Last Modified on: 10/02/08 16:06:23
# Last Modified by: MCC C. Gabriel Varela S: Se hace que no se modifiquen a void ciertos status para los payments
# Last Modified on: 10/14/08 12:23:42
# Last Modified by: MCC C. Gabriel Varela S: Se hace que el status de los productos negativo y positivo agregados sea igual al meraction de return
# Last Modified RB: 12/02/08  19:00:02 - Se cobra el mismo precio cuando sltvid (6 digitos) sea el mismo
# Last Modified on: 12/11/08 11:49:06
# Last Modified by: MCC C. Gabriel Varela S: Se hace que ya no se ponga el shipdate en el negativo
# Last Modified on: 12/15/08 17:52:37
# Last Modified by: MCC C. Gabriel Varela S: Se modifica calculo de restocking fee
# Last Modified on: 03/06/09 16:02:04
# Last Modified by: MCC C. Gabriel Varela S: Se pone el porcentaje del restocking fee en base a la variable de sistema.
# Last Modification by JRG : 03/13/2009 : Se agrega el log
# Last Modified on: 03/17/09 17:07:31
# Last Modified by: MCC C. Gabriel Varela S: Parametros sltv_itemshipping
# Last Modified By RB on 12/16/2010 : Parametros sltv_itemshipping
# Last Modified by RB on 04/15/2011 12:23:22 PM : Se agrega id_orders como parametro para funcion calculate_taxes 
#Last modified on 25 Apr 2011 17:08:34
#Last modified by: MCC C. Gabriel Varela S. :Se hace que el producto sea 000000000 si no existe
# Last Modified by RB on 06/07/2011 01:01:07 PM : Se agrega City como parametro para calculate_taxes
	
	
	my ($rec,$addprnegativeproduct,$addprexchangeproduct,$payflexvoid,$paysum,$notfinance,$notreship,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$id_returns) = @_;
	my ($discount,$posteddate,$sumfees,$order_type,$ctype);
	my $idorders = $rec->{'ID_orders'};
	my $idprod_returned;

	#cgierr("$rec->{'ID_orders'},$addprnegativeproduct,$addprexchangeproduct,$payflexvoid,$paysum,$notfinance,$notreship,$adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumatoria,$id_returns");
	
	my $bandextendw=0;
	my $pricerestocking=0;
	my $price=0;
	
	if($rec->{'Saleprice'} ne ''){
		$price=$rec->{'Saleprice'}*-1;
		$pricerestocking=$rec->{'Saleprice'}*$cfg{'restockfeeporc'}/100;
	}else{
		$price=$rec->{'SPrice'}*-1;
		$pricerestocking=$rec->{'SPrice'}*$cfg{'restockfeeporc'}/100;
	}

	my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$idorders';");
	($order_type, $ctype) = $sth->fetchrow();


	# Inicia Products
	if($addprnegativeproduct) {

		$shipping="";
		$cost="";
		$serialnumber="";
		$tracking="";
		$shpprovider="";
		#$status="";
		$posteddate=", PostedDate=CURDATE()";
		#$rec->{'Shipping'}=0 if($rec->{'OldShpReturn'});
		$shipping=", Shipping=$rec->{'Shipping'}*-1" if ($rec->{'Shipping'});
		$shipping=", Shipping=0" if(!$rec->{'OldShpReturn'});
		$cost=", Cost=$rec->{'Cost'}*-1" if ($rec->{'Cost'});
		$serialnumber=", SerialNumber=$rec->{'SerialNumber'}" if ($rec->{'SerialNumber'});
		$tracking=", Tracking='".$rec->{'Tracking'}."'" if ($rec->{'Tracking'});
		$shpprovider=", ShpProvider='$rec->{'ShpProvider'}'" if ($rec->{'ShpProvider'});

		$tracking=", Tracking='NULL'";

		$shpdate="";
		#&cgierr("Mes: $id_returns, $shpdate");

		$status=", Status='Returned'";

		#Agrega un producto con nameros negativos para dejar la cuenta en 0
		#Se busca servicio relacionado al producto
		if($rec->{'merAction'}eq'Exchange'){

			my $sthl=&Do_SQL("SELECT * FROM sl_orders_products WHERE Related_ID_products=$rec->{'ID_products'} and ID_orders=$rec->{'ID_orders'}");
			while (my $recl=$sthl->fetchrow_hashref){

				if($recl->{'ID_products'} =~ /$cfg{'extwarrid'}$/){

					#Se quita garantaa anterior
					my $idorders = $recl->{'ID_orders'};
					my $sprice = $recl->{'SalePrice'}*-1;
					$bandextendw=1;
					$recl->{'ID_products'}='000000000'if($recl->{'ID_products'}eq'' or $recl->{'ID_products'}==0);
					&Do_SQL("INSERT INTO sl_orders_products SET ID_products='$recl->{'ID_products'}',ID_orders=$recl->{'ID_orders'}, ID_packinglist=$recl->{'ID_packinglist'}, Related_ID_products=$recl->{'Related_ID_products'},Quantity=-1, SalePrice=$recl->{'SalePrice'}*-1 $status $posteddate,Date = CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");#if($in{'status'}eq'Resolved');
					&accounting_return_processed($idorders);
					&auth_logging('orders_products_added',$recl->{'ID_orders'});

				}

			} 

		}

		if($rec->{'Discount'}!=0){
			$discount=" ,Discount=$rec->{'Discount'}*-1 ";
		
		}else{
			$discount="";
		}

		$rec->{'ID_products'}='000000000'if($rec->{'ID_products'}eq'' or $rec->{'ID_products'}==0);
		my ($fi) = &Do_SQL("INSERT INTO sl_orders_products SET ID_products='$rec->{'ID_products'}',ID_orders='$idorders', ID_packinglist=$rec->{'ID_packinglist'}, Quantity=-1, SalePrice=$price $shipping $cost $serialnumber $tracking $discount $status $shpdate $posteddate,Date = CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}';");#if($in{'status'}eq'Resolved');
		$idprod_returned = $fi->{'mysql_insertid'};

		&auth_logging('orders_products_added',$idorders);

		if($rec->{'Discount'}==0){
			&calc_tax_disc_shp(0,0);
		}else{
			&calc_tax_disc_shp(0,0,1);
		}

		
		#Se calcula el descuento que tenia el producto
		#Se determina el numero de pagos para el producto
		my $paym=&Do_SQL("SELECT count(*) FROM `sl_orders_payments` WHERE ID_orders=$rec->{'ID_orders'}");
		$recpay=$paym->fetchrow;
		$discupdate=0;

		if($recpay eq 1 and $cfg{'fpdiscount'.$rec->{'flexipago'}}){
			#Inicia Actualiza el descuento de sl_orders
			$discupdate=$price * $cfg{'fpdiscount'.$rec->{'flexipago'}}/100;
		}
	
		# PendienteIgnorar calcular tax por producto en base al monto $price y asignarla a $tax 
		$tax=&calculate_taxes($rec->{'shp_Zip'},$rec->{'shp_State'},$rec->{'shp_City'},$rec->{'ID_orders'});
		$tax=($price-$discupdate)*$tax;
		#GV Termina 09may2008
		($price < 0) and ($sumatoria+=($price+$tax+$rec->{'Shipping'}-$discounts)*-1);
		#Termina Agrega un producto con numeros negativos para dejar la cuenta en 0
	
		### Movimiento de accounting para el return de la venta
		## ToDo: Donde se aplican los movimientos de las ordenes mayoreo?
		my @params = ($idorders);
		&accounting_keypoints('order_products_returned_'. $ctype .'_'. $order_type, \@params );


	}



						#################################################################################
						#################################################################################
						#################################################################################
						#################################################################################

						#								RETURN FEES

						#################################################################################
						#################################################################################
						#################################################################################
						#################################################################################




	# Agrega servicio Return fee
	if($rec->{'ATCReturnFees'}) {

		if(!$addshpdone) {

			$price=$cfg{'minorfee'};
			$price=$cfg{'greaterfee'} if ($weight>$cfg{'limitweight'});
			#GV Inicia modificacian 12jun2008
			$ti=&Do_SQL("INSERT INTO sl_orders_products SET ID_products = CONCAT('60000',$cfg{'returnfeeid'}),ID_orders = '$idorders', Related_ID_products = '$idprod_returned', Quantity=1, SalePrice=$price,Status='Active' $posteddate,Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");#if($in{'status'}eq'Resolved');
			&auth_logging('orders_products_added',$rec->{'ID_orders'});
			#PendienteIgnorar calcular tax por services en base al monto $price y si el servicio esta apto para aplicar tax y asignarla a $tax 
			$sumatoria+=($price+$tax);
			$addshpdone=1;
			$sumfees += $price;

		}
		
	}
	

	#Restock fee
	if($rec->{'ATCRestockFees'}) {

		if(!$restockdone) {

			$price=$cfg{'restockfeeporc'}/100*$rec->{'OrderNet'};
			$fi=&Do_SQL("INSERT INTO sl_orders_products SET ID_products = CONCAT('60000', $cfg{'restockfeeid'}),ID_orders = '$idorders', Related_ID_products = '$idprod_returned', Quantity=1, SalePrice=$pricerestocking ,Status='Active' $posteddate, Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");#if($in{'status'}eq'Resolved');
			&auth_logging('orders_products_added',$rec->{'ID_orders'});
			#PendienteIgnorar calcular tax por services en base al monto $price y si el servicio esta apto para aplicar tax y asignarla a $tax 
			$sumatoria+=($price+$tax);
			$restockdone=1;
			$sumfees += $pricerestocking;
		
		}
	
	}

	#### Acounting Movements
	my @params = ($idorders, $idprod_returned);
	&accounting_keypoints('order_products_returnfees_'. $ctype .'_'. $order_type, \@params );


	#Actualiza el envio
	if($rec->{'NewShp'}){

		if(!$shippingdone){		
			$shippingdone=1;
		}

	}



	if($addprexchangeproduct){
		$shipping="";
		$cost="";
		$serialnumber="";
		$tracking="";
		$shpprovider="";


						#################################################################################
						#################################################################################
						#################################################################################
						#################################################################################

						#									PRODUCTS

						#################################################################################
						#################################################################################
						#################################################################################
						#################################################################################


		# Agrega el nuevo producto deseado
		if(!$adddone) {

			($rec->{'ID_products_exchange'} eq '') and ($rec->{'ID_products_exchange'} = $rec->{'ID_products'});
			
			$idpacking = &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'ID_packingopts');
			$edt= &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'edt');
			$sizew=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SizeW');
			$sizeh=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SizeH');
			$sizel=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SizeL');
			#GV Inicia 09may2008
			$discflex=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'flexipago');
			#GV Termina 09may2008
			$size=$sizew*$sizeh*$sizel;
			$weight=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'Weight');
			
			## Fixed/Variable/Table Shipping ? 
			my $shpcal  = &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'shipping_table');
			my $shpmdis = &load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'shipping_discount');
			($shptotal1,$shptotal2,$shptotal3,$shptotal1pr,$shptotal2pr,$shptotal3pr,$va{'shp_text1'},$va{'shp_text2'},$va{'shp_text3'},$va{'shp_textpr1'},$va{'shp_textpr2'},$va{'shp_textpr3'})= &sltv_itemshipping($edt,$size,1,1,$weight,$idpacking,$shpcal,$shpmdis,substr($rec->{'ID_products_exchange'},3,6));
			$cad="$shptotal".$rec->{'shp_type'};
			$va{'shptotal1'}=$shptotal1;
			$va{'shptotal2'}=$shptotal2;
			$va{'shptotal1pr'}=$shptotal1pr;
			$va{'shptotal2pr'}=$shptotal2pr;
			$comillitas=$rec->{'shp_type'};
			$comillitas=1 if(!$comillitas);
			$totshpord=$va{'shptotal'.$comillitas.''};
			$totshpord=0 if(!$rec->{'NewShp'} or !$totshpord or $totshpord  eq '');
			$shipping=", Shipping=$totshpord";
			#$cost=",Cost=".&load_sltvcost($rec->{'ID_products_exchange'});
			$serialnumber="";
			$tracking="";
			$shpprovider="";
			$status=", Status='$in{'meraction'}' ";
			#$price*=-1 if($addprnegativeproduct);
			$price=$rec->{'Saleprice'};
			$price=&load_name('sl_products','ID_products',substr($rec->{'ID_products_exchange'},3,6),'SPrice') if($rec->{'ID_products_exchange'}  and substr($rec->{'ID_products_exchange'},3,6) ne substr($rec->{'ID_products'},3,6));
			
			if($rec->{'merAction'}eq'ReShip') {
				$discount=" ,Discount=$rec->{'Discount'} " if ($rec->{'Discount'}!=0);
			}else{
				$discount="";
			}

			$si=&Do_SQL("INSERT INTO sl_orders_products set ID_products=$rec->{'ID_products_exchange'},ID_orders=$rec->{'ID_orders'}, ID_packinglist=$rec->{'ID_packinglist'}, Quantity=1, SalePrice=$price $shipping $serialnumber $tracking $shpprovider $discount $status,Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");#if($in{'status'}eq'Resolved');

			&auth_logging('orders_products_added',$recl->{'ID_orders'});
			if($rec->{'Discount'}==0) {
				&calc_tax_disc_shp(0,0);
			}else{
				&calc_tax_disc_shp(0,0,1);
			}

			# Se busca servicio relacionado al producto
			if($rec->{'merAction'}eq'Exchange' and $bandextendw) {
				&Do_SQL("INSERT INTO sl_orders_products SET ID_products=600000000+$cfg{'extwarrid'},ID_orders=$rec->{'ID_orders'}, Related_ID_products=$rec->{'ID_products_exchange'},Quantity=1, SalePrice=$price*$cfg{'extwarrpctsfp'}/100 $status ,Date = CURDATE(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}';");#if($in{'status'}eq'Resolved');
				&auth_logging('orders_products_added',$recl->{'ID_orders'});
			}

			# Se calcula el descuento del producto
			$discupdate=0;
			if($recpay eq 1 and $cfg{'fpdiscount'.$discflex}) {

				#Actualiza el descuento de sl_orders
				$discupdate=$price * $cfg{'fpdiscount'.$discflex}/100;
				
			}

			$tax=&calculate_taxes($rec->{'shp_Zip'},$rec->{'shp_State'},$rec->{'shp_City'},$rec->{'ID_orders'});
			$tax=($price-$discupdate)*$tax;

			$sumatoria+=($price+$tax+$totshpord-$discounts);
			$adddone=1;
			#&cgierr($sumatoria);
		}
	}
	
	

						#################################################################################
						#################################################################################
						#################################################################################
						#################################################################################

						#									PAYMENTS

						#################################################################################
						#################################################################################
						#################################################################################
						#################################################################################



	if($payflexvoid){
		if(!$flexivoiddone){
			#GV Inicia modificacian 12jun2008
			#$su=&Do_SQL("update sl_orders_payments set Status='Void' where ID_orders=$rec->{'ID_orders'} and Status='Pending'");#if($in{'status'}eq'Resolved');
			$su=&Do_SQL("update sl_orders_payments set Status='Void' where ID_orders=$rec->{'ID_orders'} and Captured='No' and (CapDate is null or CapDate ='' or CapDate='0000-00-00')  and Status not in('Financed','Cancelled','Void','Order Cancelled')");#if($in{'status'}eq'Resolved');
			#GV Termina modificacian 12jun2008
			$flexivoiddone=1;
		}
	}
	if($paysum){
		#Pendiente por hacer: La sumatoria de los productos quizas se deba calcular antes de terminar la funcian updateinventory
		#
	}
	#Termina Payments
	
	#Inicia Notifications
	if($notfinance){
		#Pendiente desarrollarla
		&notificationsfinance($rec->{'ID_orders'});
	}
	if($notreship){
		#Pendiente desarrollarla
		&notificationsnoreship($rec->{'ID_orders'});
	}
		
	#Termina Notifications
	#Pendiente Actualizar total de ardenes, ya sea aqua o al final de la funcian updateinventory
	#Nota Importante: Tomar en cuenta todo: Discounts, Taxes, Envaos, Cantidades, y todo mas
	return ($adddone,$addshpdone,$shippingdone,$restockdone,$flexivoiddone,$sumfees);
}


sub showitemsordered{
# --------------------------------------------------------
	# Created on: 09/jun/2008 03:42:18 PM GMT -05:00
	# Last Modified on: 8/jul/2008
	# Last Modified by: Jose Ramirez Garcia
	# Author: MCC C. Gabriel Varela S.
	# Description : Muestra los productos de la orden
	# Description 11jun2008 : Se hace que en qcsorting tampoco se muestre el radio. Se filtra por id_orders_products en todos los estados que no se muestra radio
	# Description 8jul2008 : Se muestra solo las ordenes en status Shipped y no se muestran servicios
	# Parameters :
	
	# Last Modified on: 16/jun/2008
	# Last Modified by: MCC C. Gabriel Varela S.
	# Description 11jun2008 : Se hace que en repairret tampoco se muestre el radio. Se filtra por id_orders_products en todos los estados que no se muestra radio
	
	# Last Modified on: 07/18/2008
	# Last Modified by: Jose Ramirez Garcia
	# Description : Se agrego el parametro de products a la funcion build_tracking_link	
	# Last Modified GV: 06/16/08 : Se hace que en qcsorting tampoco se muestre el radio
	# Last Modified RB: 11/18/08  12:31:46 Se agrego upc en la lista
	# Last Modified RB: 11/21/08  13:58:07 Se agrego la etiqueta (EW) a un costado del producto,cuando este cuenta con  Garantia Extendida, Se cambio a mostrar la fecha del producto y se agrego mostrar el Status del producto ademas del status de la orden
	# Last Modified RB: 04/13/09  12:11:46 -- Se agrego icono para ver returns por cada orden. Esta funcion esta ligada con sub.base_sltv
	# Last Modified RB: 06/08/09  15:58:10 -- Cuando el item es un Set, se agrega el detalle de sus partes y sus UPC


	
	my $outputsh,$query;
	$query="";
	$query=" and id_orders_products=$in{'id_orders_products'} " if($in{'cmd'}eq'sorting' or $in{'cmd'}eq'qcreturns' or $in{'cmd'}eq'atcreturns' or $in{'cmd'}eq'crreturns' or $in{'cmd'}eq'retwarehouse');
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders) 
	                    WHERE ID_customers='$in{'id_customers'}' AND sl_orders_products.Status IN ('Active','Exchange','ReShip') 
	                    AND SalePrice >= 0 AND sl_orders.Status = 'Shipped' 
	                    AND LEFT(sl_orders_products.ID_products,1)<>'6' 
	                    AND (Related_ID_products IS NULL OR LEFT(Related_ID_products,1)<>4) 
	                    $query");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT *,sl_orders_products.Date AS Date, sl_orders.Status AS Status, sl_orders_products.Status AS PStatus  
		                    FROM sl_orders INNER JOIN sl_orders_products USING(ID_orders) WHERE ID_customers='$in{'id_customers'}' 
		                    AND sl_orders_products.Status IN ('Active','Exchange','ReShip') AND SalePrice >= 0 
		                    AND sl_orders.Status = 'Shipped' 
		                    AND LEFT(sl_orders_products.ID_products,1)<>'6' 
		                    AND (Related_ID_products IS NULL OR LEFT(Related_ID_products,1)<>4) $query ORDER BY sl_orders.ID_orders, Saleprice DESC;");
		
		while ($rec = $sth->fetchrow_hashref){
			$in{'extwar_'.$rec->{'ID_orders_products'}.''} = &load_name("sl_orders_products","Related_ID_products","$rec->{'ID_products'}\' AND ID_orders = \'$rec->{'ID_orders'}"," IF(COUNT(ID_orders_products) > 0,'(EW)','') ");
			$in{'upc_'.$rec->{'ID_orders_products'}.''} = &get_upc_product_detailed($rec->{'ID_products'});
			$radiotxt="<input type='radio' class='radio' name='ID_orders_products' value='$rec->{'ID_orders_products'}'>" if($in{'cmd'}ne'sorting' and $in{'cmd'}ne'qcreturns' and $in{'cmd'}ne'atcreturns' and $in{'cmd'}ne'crreturns' and $in{'cmd'}ne'retwarehouse'  and $in{'cmd'}ne'repairret' and $in{'cmd'}ne'pendpayments');
			
			$d = 1 - $d;
			$outputsh .= "<tr bgcolor='$c[$d]'>\n";
			$outputsh .= "  <td class='smalltext' valign='top' align='center' nowrap>$radiotxt
					<br><a href='/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}' name='idorder' id='idorder'>$rec->{'ID_orders'}</a><br>"
					. qq|<a href="javascript:return false;" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'idorder');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=orders_viewnotes&id_orders=$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_notes.gif' title='View Notes' alt='' border='0'></a>&nbsp;&nbsp;|
					. &hasreturn_ajax($rec->{'ID_orders'},'wms')
					. "</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top'>
							<span class='smallfieldterr'>ID</span>
								<a href='/cgi-bin/mod/wms/dbman?cmd=mer_products&view=".substr($rec->{'ID_products'},3,6)."'>".&format_sltvid($rec->{'ID_products'})."</a> 
							<span style='color:green;font-size:11px;'>
								<strong>$in{'extwar_'.$rec->{'ID_orders_products'}.''}</strong></span><br>\n
							$in{'upc_'.$rec->{'ID_orders_products'}.''}<br>"
							.&load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3,6),'[Model]  ('.&format_price($rec->{'SalePrice'}).')<br>[Name]').&load_choices($rec->{'ID_products'})."</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top' align='center'>".&build_tracking_link($rec->{'Tracking'},$rec->{'ShpProvider'},$rec->{'ShpDate'},$rec->{'ID_products'})."</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top' align='center'>$rec->{'Status'} / $rec->{'PStatus'}</td>\n";
			$outputsh .= "</tr>\n";
		}
	}else{
	$va{'pageslist'} = 1;
	$outputsh = qq|
	<tr>
		<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
	</tr>\n|;
	}
		return $outputsh;
}


sub showservicesordered{
#-----------------------------------------
# Created on: 12/01/08  11:47:17 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	

	my $outputsh,$query,$stritem,$cmd; 
	#GV Inicia 11jun2008
	$query="";
	$query=" and id_orders_products=$in{'id_orders_products'} " if($in{'cmd'}eq'sorting' or $in{'cmd'}eq'qcreturns' or $in{'cmd'}eq'atcreturns' or $in{'cmd'}eq'crreturns' or $in{'cmd'}eq'retwarehouse');
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.ID_customers='$in{'id_customers'}' AND sl_orders.Status = 'Shipped' AND IF(LEFT(sl_orders_products.ID_products,1) ='6',sl_orders_products.Status = 'Active',sl_orders_products.Status IN ('Exchange,Returned,Undeliverable') OR SalePrice < 0) $query");
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT *,sl_orders_products.Date AS Date, sl_orders.Status AS Status, sl_orders_products.Status AS PStatus  FROM sl_orders, sl_orders_products WHERE sl_orders.ID_orders=sl_orders_products.ID_orders AND sl_orders.ID_customers='$in{'id_customers'}' AND sl_orders.Status = 'Shipped' AND IF(LEFT(sl_orders_products.ID_products,1) ='6',sl_orders_products.Status = 'Active',sl_orders_products.Status IN ('Exchange,Returned,Undeliverable') OR SalePrice < 0) $query ORDER BY sl_orders.Date;");
		#GV Termina 11jun2008
		while ($rec = $sth->fetchrow_hashref){#&cgierr;
			$cmd ='products';
			$in{'extwar_'.$rec->{'ID_orders_products'}.''} = &load_name("sl_orders_products","Related_ID_products","$rec->{'ID_products'}\' AND ID_orders = \'$rec->{'ID_orders'}"," IF(COUNT(ID_orders_products) > 0,'(EW)','') ");
			(substr($rec->{'ID_products'},0,1) eq 6) and ($cmd = 'services') and ($stritem = &load_name("sl_services","ID_services",substr($rec->{'ID_products'},5),"CONCAT(Name,'<br>',Description)"));
			(substr($rec->{'ID_products'},0,1) ne '6') and ($stritem = &load_db_names('sl_products','ID_products',substr($rec->{'ID_products'},3),'[Model]<br>[Name]').&load_choices($rec->{'ID_products'}));
			
			$d = 1 - $d;
			$outputsh .= "<tr bgcolor='$c[$d]'>\n";
			$outputsh .= "  <td class='smalltext' valign='top' align='center' nowrap>f
					<br><a href='/cgi-bin/mod/wms/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}' name='idorder' id='idorder'>$rec->{'ID_orders'}</a><br>"
					. qq|<a href="#idorder" id='ajax_btn' onClick="popup_show('ajax_windows', 'ajax_drag', 'ajax_exit', 'element-right', -1, -1,'idorder');loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=orders_viewnotes&id_orders=$rec->{'ID_orders'}');"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_notes.gif' title='View Notes' alt='' border='0'></a><br>|
					. "</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top'>$rec->{'Date'}</td>\n";
			$outputsh .= "  <td class='smalltext' valign='top'><span class='smallfieldterr'>ID </span><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$cmd&view=".substr($rec->{'ID_products'},3)."'>".&format_sltvid($rec->{'ID_products'})."</a><br>\n
											$stritem </td>\n";
			$outputsh .= "  <td class='smalltext' valign='top' align='center'>$rec->{'PStatus'}</td>\n";
			$outputsh .= "</tr>\n";
		}
	}else{
	$va{'pageslist'} = 1;
	$outputsh = qq|
	<tr>
		<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
	</tr>\n|;
	}
		return $outputsh;
}

#GV Inicia 20jun2008
sub showpackinglist
{
	# Created on: 20/jun/2008 09:54:18 AM GMT -06:00
	# Last Modified on: 
	# Last Modified by: 
	# Author: MCC C. Gabriel Varela S.
	# Description : Mostrara el packinglist al procesar un return cuando el return sea del tipo Exchange o Re Ship
	# Parameters :
	# Last Modified on: 08/28/08 16:52:00
	# Last Modified by: MCC C. Gabriel Varela S: Se cambia para que se contemple el packinglist del nuevo producto en lugar del anterior
	# Last Modified on: 12/15/08 10:56:41
	# Last Modified by: MCC C. Gabriel Varela S: Se hace que se marque el return como pendiente de packing list y se quita ventana de impresian.
	# Last Modification by JRG : 03/13/2009 : 	Se agrega log
	my $autocad;
	$autocad="";
	if(($in{'meractiona'}eq"Exchange" or $in{'meractiona'}eq"ReShip")and $in{'status'}eq"Resolved")
	{
		#Obtener ID y fecha de orden

		$in{'id_orders'}=&load_name('sl_orders_products','ID_orders_products',$in{'id_orders_productsa'},'ID_orders');
		$in{'date'}=&load_name('sl_orders','ID_orders',$in{'id_orders'},'Date');
		$in{'id_products_exchangea'}=&load_name('sl_orders_products','ID_orders_products',$in{'id_orders_productsa'},'ID_products') if(!$in{'id_products_exchangea'});
		my $sthl=&Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders=$in{'id_orders'} AND ID_products=$in{'id_products_exchangea'} order by ID_orders_products desc");
		my $rthl=$sthl->fetchrow;
		$in{'id_orders_productsa'}=$rthl;
		
		#Se marca el return como pendiente de packinglist
		&Do_SQL("Update sl_returns set PackingListStatus='Pending' where ID_returns=$in{'id_returnsa'}");
		&auth_logging('returns_updated',$in{'id_returnsa'});
		
		
		#$autocad = qq|<script language="javascript" type="text/javascript">prnwin("/cgi-bin/common/apps/ajaxbuild?ajaxbuild=showpackinglist&shp_name=$in{'shp_name'}&shp_address1=$in{'shp_address1'}&shp_address2=$in{'shp_address2'}&shp_address3=$in{'shp_address3'}&shp_urbanization=$in{'shp_urbanization'}&shp_city=$in{'shp_city'}&shp_state=$in{'shp_state'}&shp_zip=$in{'shp_zip'}&id_orders=$in{'id_orders'}&date=$in{'date'}&id_orders_products=$in{'id_orders_productsa'}")</script>|;
	}
	delete($in{'meractiona'})and delete($in{'nodel_meractiona'}) if($in{'meractiona'});
	delete($in{'id_returnsa'})and delete($in{'nodel_id_returnsa'}) if($in{'id_returnsa'});
	return $autocad;
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



sub autolist_returnspl{
#-----------------------------------------
# Created on: 04/01/09  11:18:32 By  Roberto Barcenas
# Forms Involved: retwarehouse & processamount
# Description : Autolista para returns en cero
# Parameters :

 	my ($id_orders)	=	@_;
 	
 	
 	my ($sth) = &Do_SQL("INSERT INTO sl_lists VALUES (0,'Returns PL',$id_orders,1470,'sl_orders','orders','Active',CURDATE(),NOW(),1);");
	&auth_logging('list_added',$sth->{'mysql_insertid'});
	
}


sub get_upc_product_detailed{
#-----------------------------------------
# Created on: 06/08/09  12:57:27 By  Roberto Barcenas
# Forms Involved: 
# Description : Devuelve el upc de un producto o bien la lista de partes con sus upcs
# Parameters : $id_products	

	my ($id_products) = @_;
	
	my $strout = &load_name('sl_skus','ID_sku_products',$id_products,'UPC');
	if($strout eq ''){
		(substr($id_products,1) == 6) ?
		$strout  = 'NA' :
		$strout  = "<a href='/cgi-bin/mod/wms/admin?cmd=upc' title='Poner UPC' target='upwin' onClick='upwin();'>Add UPC</a>";
	}
	$strout = "<span class='smallfieldterr'>upc</span> ".$strout;
	
	my $isset=&load_name('sl_skus','ID_sku_products',$id_products,'IsSet');
	
	if($isset eq 'Y'){
		$strout = '';
		my ($sth) = &Do_SQL("SELECT ID_parts FROM sl_skus_parts WHERE ID_sku_products = $id_products");
		while(my($id_parts,$upc) = $sth->fetchrow()){
			$id_parts = &load_name('sl_skus','ID_products',$id_parts,'ID_sku_products');
			$upc = &load_name('sl_skus','ID_sku_products',$id_parts,'UPC');
			$upc  = "<a href='/cgi-bin/mod/wms/admin?cmd=upc' title='Poner UPC' target='upwin' onClick='upwin();'>Add UPC</a>"	if  $upc eq '';
			$id_parts_single = $id_parts;
			$id_parts_single -= 400000000;

			$strout .= qq|&nbsp;&nbsp;&nbsp;&nbsp;<span class='smallfieldterr'>SKU </span><a href="/cgi-bin/mod/wms/dbman?cmd=mer_parts&view=$id_parts_single">|.&format_sltvid($id_parts).qq|</a>  -  <span class='smallfieldterr'>upc </span>$upc<br>\r\n|;
		}
		
	}	
	return $strout;
}


sub send_email_scanconfirmation{
# --------------------------------------------------------
	# Created on: 05/17/2010 013:25:18
	# Author: RB
	# Description : Envia correo de confirmacion de escaneo de orden al cliente
	# Parameters : ShpDate, Tracking, ShpProvider, ID Order, Items Sent,ID Items
	# Last Modified on: AD::06102014::Se agrega parametro OW para templates de Sitios Lineales
	# Last Modified on: HC::13Feb2017::Se añade excepcion para tomar correo para productos Sognare
		
	my ($shpdate,$tracking,$provider,$id_orders,$num,%ids)=@_;

	my $pmail_path = '/cgi-bin/html/en/common/emails/';
	my $pname = "default";
	my $actual_id = 0;
	my $status = -1;
	my $subject = "Tu pedido esta en camino $id_orders";
	my $body ='';

	my ($sth) = &Do_SQL("SELECT sl_orders.ID_customers, sl_customers.Email, sl_orders.language, sl_customers.FirstName, sl_orders.shp_name, sl_orders.shp_Address1, sl_orders.shp_urbanization, sl_orders.shp_Address2, sl_orders.shp_Address3, sl_orders.shp_city, sl_orders.shp_state, sl_orders.shp_zip, sl_orders.Ptype FROM sl_orders INNER JOIN sl_customers ON sl_orders.ID_customers = sl_customers.ID_customers WHERE sl_orders.ID_orders = '$id_orders';");
	my $rec = $sth->fetchrow_hashref();

	# 1. Revisamos si el cliente tiene correo
	my ($id_customers) = $rec->{'ID_customers'};
	my ($to_email) = $rec->{'Email'};
	my ($order_language) = $rec->{'language'};
	
	## Debug Email
	$to_email = ($cfg{'debug_email'} and $cfg{'debug_email'}==1 and $cfg{'to_email_debug'})? $cfg{'to_email_debug'} : $to_email;
	
	##Buscar el template por categoria
	## Si el correo es valido
	if ( $cfg{'from_email'} =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and $to_email =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/  ){

		## Determinamos el from_email correcto
		my ($from_email) = $cfg{'from_email'};

		## Cadena con los items y su tracking number
		PRODUCTS:for my $i(1..$num){
			$id_products=0;

			## El item es parte de un set o es un producto?	
			if ($ids{$i}[3] =~ /SET:(\d+),(\d+)/){
				my ($id_ord_prod) = $1;
				$id_products = &load_name('sl_orders_products','ID_orders_products',$id_ord_prod,'id_products');
		 	}else{
		 		$id_products = $ids{$i}[0];		 	
			}

			### Agregamos solo la info de los productos a la cadena
			if ($actual_id != $id_products){
				$actual_id = $id_products;
				
				my ($pname) = &load_name('sl_products','ID_products',substr($id_products,-6),'Name');
				$va{'items_inorder'} .= "($id_products) - ". $pname . "<br>";
				$from_email = $cfg{'from_email_prostaliv'}  if ($cfg{'from_email_prostaliv'} =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and $pname =~ /prostaliv/i);
				$from_email = $cfg{'from_email_dreambody'}  if ($cfg{'from_email_dreambody'} =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and $pname =~ /dream body/i);
				$from_email = $cfg{'from_email_allnatpro'}  if ($cfg{'from_email_allnatpro'} =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and $pname !~ /dream body|prostaliv/i);
				if( $cfg{'from_email_sognare'} =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/ and $pname =~ /sognare/i){
					$from_email = $cfg{'from_email_sognare'};
					last PRODUCTS;
				}
			}
		}
		
		## Datos para el Email
		$va{'id_orders'} = $cfg{'prefixentershipment'}.$id_orders;
		$va{'name'} = lc($rec->{'FirstName'});
		$va{'shp_name'} = lc($rec->{'shp_name'});
		$va{'shp_address1'} = lc($rec->{'shp_Address1'});
		$va{'shp_urbanization'} =  lc($rec->{'shp_urbanization'});
		$va{'shp_address2'} = lc($rec->{'shp_Address2'});
		$va{'shp_address3'} = lc($rec->{'shp_Address3'});
		$va{'shp_city'} =  lc($rec->{'shp_city'});
		$va{'shp_state'} = lc($rec->{'shp_state'});
		$va{'shp_zip'} = $rec->{'shp_zip'};
		$va{'shpdate'} = $shpdate; 
		$va{'tracking'} = $tracking;
		$va{'shpprovider'} = '('.$provider.')';
		$va{'cservice_phone'} = $cfg{'cservice_phone'};
		my $ptype = lc($rec->{'Ptype'});

		$va{'total'} =  &format_price(&total_orders_products($id_orders));
		
		if ($ptype eq 'cod'){
			$va{'htmlcod'} = qq|
			<div style="border:2px solid #378de8; background-color:#e4f1ff; padding:15px;-moz-border-radius: 5px; border-radius: 5px;text-align:center;"><font   face="century gothic, verdana" size=4>
				<font color=#378de8><b>Pago a la entrega</b></font><br>
				Favor de tener listo el pago de:<br>
				<b>$va{'total'} </b>
			</font> 
			</div>
			<br><br>|;
		}

		if ($va{'tracking'} eq 'DRIVER'){
			$va{'shpprovider'} = '';
			$va{'tracking'}  = '';
		}

		if($provider eq 'UPS'){
			$link = qq|http://wwwapps.ups.com/tracking/tracking.cgi?tracknum=$tracking&loc=es_MX|;
		}elsif($provider eq 'FEDEX'){
			$link = qq|http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcom&cntry_code=us&language=english&tracknumbers=$tracking|;
		}elsif ($provider eq 'USPS'){						
			$link = qq|http://trkcnfrm1.smi.usps.com/PTSInternetWeb/InterLabelInquiry.do?strOrigTrackNum=$tracking|;
		}elsif ($provider eq 'DHL Ground' or $ShpProvider eq 'DHL'){						
			$link = qq|http://track.dhl-usa.com/TrackByNbr.asp?nav=Tracknbr&txtTrackNbrs=$tracking|;
		}elsif ($provider eq 'Fedex'){						
			$link = qq|http://www.fedex.com/Tracking?ascend_header=1&clienttype=dotcomreg&cntry_code=mx&language=spanish&tracknumbers=$tracking|;
		}elsif ($provider eq 'IW'){						
			$link = qq|http://www.islandwide.com/TrackResult.asp?num=$tracking|;
		}elsif ($provider eq 'ESTAFETA'){						
			$link = qq|http://rastreo3.estafeta.com/RastreoWebInternet/consultaEnvio.do?guias=$tracking&idioma=es&dispatch=doRastreoInternet|;
		}else{
			$link = 'http://pedidos.inova.com.mx';
		}


		$va{'link_tracking'} = $link; 
		## Cargamos el template		
		## Mandar template en Ingles para Dreambody
		if ($from_email eq $cfg{'from_email_dreambody'} and -e  $pmail_path . "dreambody_en.html"  and ($order_language eq 'english' or &load_name('sl_customers','ID_customers',$id_customers,'ID_admin_users') eq '5022')){
			$subject = "Your order  is on its way";
			$body = &build_page('common/emails/dreambody_en.html'); 
		}elsif($from_email eq $cfg{'from_email_allnatpro'} and -e $pmail_path . "allnatpro.html"  and &load_name('sl_customers','ID_customers',$id_customers,'ID_admin_users') eq '5020'){
			$body = &build_page('common/emails/allnatpro.html'); 

		}elsif($from_email eq $cfg{'from_email_sognare'} and !($in{'e'} eq 4 and &load_name('sl_customers','ID_customers',$id_customers,'ID_admin_users') eq '5333')){ 
			$body = &build_page('emails/scaned_sognare.html');

		}elsif($order_language eq 'english'){
			$body = &build_page('common/emails/' . $email_template . '_en.html');
		}else{
			$body = &build_page('emails/default.html');

			## Overwritte Template Confirmation
			if ($cfg{'email_confirmation_template_overwritte'} and $cfg{'email_confirmation_template_overwritte'}==1){
				my $id_salesorigins = &load_name('sl_orders','ID_orders',$id_orders,'ID_salesorigins');
				if ($id_salesorigins){
					$body = &build_page("emails/default$id_salesorigins.html");
				}
			}
		}

		if($cfg{'environment'} eq 'production'){

			$status = &send_mandrillapp_email($from_email,$to_email,$subject,$body,$body,'none');
			
			if($status eq 'ok'){
					$in{'db'}='sl_orders';
					&auth_logging('email_scan_sent',$id_orders);
					#&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders='$id_orders', Notes='Email Notification Send', Type='Low', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
					&add_order_notes_by_type($id_orders,"Email Notification Send","Low");
			}else{
					$in{'db'}='sl_orders';
					&auth_logging('email_scan_failed',$id_orders);

					&add_order_notes_by_type($id_orders,"Email Notification Failed:$status","Low");
			}

		}else{

			$status = 'ok';

		}
			
	}elsif($to_email =~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$/){
		$status =  "No esta el archivo " . $pmail_path . $pname . '.html' ;
	}elsif(-e $pmail_path . $pname . '.html'){
		$status = "Invalid email";
	}else{
		$status = "Invalid email and no template found";	
	}
	
	return $status;
}


sub zone_zipcodes{
	# --------------------------------------------------------
	# Created on: 14/01/2013 13:25:18
	# Author: CC
	# Description : Muestra el listado de los zipcodes para una zona
	# Parameters : 
	# Last Modified on: 

	my($search_results) = "No Zipcodes Found.";
	if($in{'toprint'}){		
		$search_results = '<table border="0" cellspacing="0" cellpadding="2" width="100%">';		
		my($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_zipcodes INNER JOIN sl_zipcodes ON sl_zones_zipcodes.ZipCode = sl_zipcodes.ZipCode WHERE sl_zones_zipcodes.ID_zones = '$in{'toprint'}';");
		if (int($sth->fetchrow) > 0){	
			$search_results .= '<tr>';
			$search_results .= '<td class="menu_bar_title">Zip Code</td>';
			$search_results .= '<td class="menu_bar_title">State</td>';
			$search_results .= '<td class="menu_bar_title">County</td>';
			$search_results .= '<td class="menu_bar_title">City</td>';
			$search_results .= '</tr>';

			my ($sth) = &Do_SQL("SELECT sl_zipcodes.* FROM sl_zones_zipcodes INNER JOIN sl_zipcodes ON sl_zones_zipcodes.ZipCode = sl_zipcodes.ZipCode WHERE sl_zones_zipcodes.ID_zones = '$in{'toprint'}';");

			my($tmp_zipcode) = "";
			my($s_zipcode) = "";
			my($drophtml_zipcode) = "";
			my($bgcolor) = "#ffffff";

			while ($rec2 = $sth->fetchrow_hashref){									
				if($tmp_zipcode eq $rec2->{'ZipCode'}){
						$s_zipcode = "";
						$drophtml_zipcode = "";
					}else{
						$tmp_zipcode = $rec2->{'ZipCode'};
						$s_zipcode = $tmp_zipcode;					
					}

				$search_results .= "<tr bgcolor='$bgcolor' >\n";			
				$search_results .= "   <td class='smalltext' >$s_zipcode </td>\n";
				$search_results .= "   <td class='smalltext' >$rec2->{'State'}-$rec2->{'StateFullName'}</td>\n";
				$search_results .= "   <td class='smalltext' >$rec2->{'CountyName'}</td>\n";
				$search_results .= "   <td class='smalltext' >$rec2->{'City'}</td>\n";				
				$search_results .= "</tr>\n";
				if($bgcolor eq '#f2f2f2'){
					$bgcolor = "#ffffff";
				}else{
					$bgcolor = "#f2f2f2";
				}
			}
		}else{
			$search_results .= '<tr>';
			$search_results .= '<td class="smalltext" align="center">No zip codes added yet</td>';
			$search_results .= '</tr>';
		}
		$search_results .= '</table>';
	}
	return $search_results;
}



sub zone_warehouses{
	# --------------------------------------------------------
	# Created on: 14/01/2013 15:25:18
	# Author: CC
	# Description : Muestra el listado de los warehouses para la zona
	# Parameters : 
	# Last Modified on: 

	my($search_results) = "No Warehouses Found.";
	if($in{'toprint'}){		
		$search_results = '<table border="0" cellspacing="0" cellpadding="2" width="100%">';		

		my (@c)   = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_warehouses WHERE ID_zones ='$in{'toprint'}'");
		if (int($sth->fetchrow) > 0){
			$search_results .= '<tr>								
								<td class="menu_bar_title">ID Warehouse</td>
								<td class="menu_bar_title">Name</td>
								</tr>';

			my($bgcolor) = "#ffffff";					
			my ($sth) = &Do_SQL("SELECT sl_w.ID_warehouses,sl_w.Name, sl_z.ID_zones_warehouses FROM sl_warehouses sl_w 
			INNER JOIN sl_zones_warehouses sl_z ON sl_z.ID_warehouses = sl_w.ID_warehouses
			WHERE sl_z.ID_zones = $in{'toprint'};");

			while ($rec = $sth->fetchrow_hashref){
				$search_results .= "<tr bgcolor='$bgcolor'>";				
				$search_results .= " <td class='smalltext'>$rec->{'ID_warehouses'}</td>";
				$search_results .= " <td class='smalltext'>$rec->{'Name'} </td>";
				$search_results .= "</tr>\n";

				if($bgcolor eq '#f2f2f2'){
					$bgcolor = "#ffffff";
				}else{
					$bgcolor = "#f2f2f2";
				}
		 	}

		}else{
			$search_results .= '<tr>								
					<td class="smalltext" align="center">No warehouses added yet.</td>					
					</tr>';
		}
		$search_results .= '</table>';
	}
	return $search_results
}


1;
