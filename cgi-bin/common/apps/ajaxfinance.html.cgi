sub editing_movements{
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
# Last Modified by: MCC C. Gabriel Varela S: Se manda a llamar primero a update_updatables.
# Last Modified on: 03/18/09 18:03:50
# Last Modified by: MCC C. Gabriel Varela S: Se habilita que cuando se finalice la edición, se borren los registros. Y también todos los registros previos para ese usuario.
# Last Modified RB: 04/06/09  16:22:38 -- Se hace dinamico el prefijo opr_
# Last Modified on: 05/01/09 11:03:06
# Last Modified by: MCC C. Gabriel Varela S: Se cambia if relacionado con check_pretotals e in edit_finished
# Last Modified on: 06/18/09 09:22:26
# Last Modified by: MCC C. Gabriel Varela S: Se agrega categoría Undefined a la creación de la tabla temporal.


	print "Content-type: text/html\n\n";
	if(&check_permissions('edit_order_movements','','')) {
		my $tot_cred,$tot_debs;
		my $cmdret = '';
		my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
		
		&update_updatables();
		if(($in{'finish'} or $in{'edit_finished'})and &check_pretotals==0) {
			$cmdret ='opr_';	#if	$in{'path'}	!~	/crm/;
			$cmdret ='mer_'	if	$in{'edit_type'}	=~	/purchase|vendors|bills/;	

			#$cmdret = '' if($in{'edit_type'} eq 'adjustments')	;
			&process_edition;
			#$va{'script_url'}= $in{'path'};
			$in{'dototemp'}="NO";
			$cmdpart=$in{'edit_type'};
			$cmdpart.='orders' if !$in{'edit_type'};  #ne 'adjustments');
			$cmdpart='po'if	$in{'edit_type'}	=~	/purchase/;
			$va{'javascriptvar'}="<script type='text/javascript'>
								//<![CDATA[
									onload = function(){
										top.location.href='[in_path]?cmd=".$cmdret."$cmdpart&view=$in{$cadidorders}&edit_finished=1#tabsl';
									}
								//]]>
								</script>";
		
		}else{
			#$va{'script_url'}= $cfg{'pathcgi_ajaxfinance'};

			#Se crea tabla temporal de movimientos
			&Do_SQL("CREATE TABLE IF NOT EXISTS sl_movementstmp (
					  ID_movements int(11) NOT NULL,
					  ID_accounts int(11) NOT NULL,
					  Amount decimal(12,3) NOT NULL,
					  Reference varchar(50) DEFAULT NULL,
					  EffDate date NOT NULL,
					  tableused varchar(50) NOT NULL DEFAULT '',
					  ID_tableused int(11) NOT NULL,
					  Category enum('Sale', 'Return', 'Exchange', 'A/R', 'A/P', 'Deposit Decrement', 'Deposit', 'Flexpay', 'Auxiliar', 'Refund', 'Payment', 'Inventory', 'Expense', 'Income', 'Undefined', 'Treasury', 'Ventas','Cobranza','Devoluciones','Descuentos','Anticipo Clientes','Reembolsos','Contracargos','Cambios Fisicos','Compras','Pagos','Gastos','Aplicacion Anticipos AP','Tesoreria','Reclasificaciones','Refacturacion','Inventario','Costos') NOT NULL,
					  Credebit enum('Credit','Debit') NOT NULL,
					  Status enum('Active', 'Pending', 'Inactive') NOT NULL default 'Active',
						ID_admin_users int(11) NOT NULL,
						Action enum('Original','Edited','Created'),
						comefrom enum('Original','Add','Dupl','Return','Drop'),
					  KEY ID_accounts (ID_accounts,EffDate,ID_admin_users),
					  KEY ID_tableused (ID_tableused),
					  KEY Category (Category),
					  KEY Credebit (Credebit),
					  KEY Status (Status),
					  KEY tableused (tableused),
					  KEY PrimaryRecord (tableused,ID_tableused,Status)
					);");
			
			if($in{'dototemp'}eq"YES") {
				#Se borran los registros de la orden con el usuario en la temporal
				&Do_SQL("DELETE FROM sl_movementstmp where ID_tableused=$in{$cadidorders} and tableused='$cadtborders' and ID_admin_users=$usr{'id_admin_users'};");
				#Se pasan los registros de la orden a las temporales
			  	
			  	my($tmp_sth) = &Do_SQL("SELECT ID_movements,ID_accounts,Amount,Reference,EffDate,Category,Credebit,ID_segments,ID_journalentries,Status from sl_movements where Id_tableused=$in{$cadidorders} and tableused='$cadtborders' ORDER BY ID_movements DESC;");

			  	while( my ( $tmp_id_movements, $tmp_id_accounts, $tmp_amount, $tmp_reference, $tmp_effDate, $tmp_category, $tmp_credebit, $tmp_id_segments, $tmp_id_journalentries, $tmp_status ) = $tmp_sth->fetchrow_array() )
			  	{
			  		&Do_SQL("INSERT INTO sl_movementstmp (ID_movements,ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,ID_journalentries,Status,ID_admin_users,Action,comefrom)
					   VALUES( '$tmp_id_movements','$tmp_id_accounts','$tmp_amount','$tmp_reference','$tmp_effDate','$cadtborders',$in{$cadidorders},'$tmp_category','$tmp_credebit','$tmp_id_segments','$tmp_id_journalentries','$tmp_status',$usr{'id_admin_users'},'Original','Original' );");
				}
			}

			&movements_actions('debit');
			&movements_actions('credit');
			$tot_debs=&show_movements('debit');
			$tot_cred=&show_movements('credit');
			$check_pretot=&check_pretotals;
			$va{'diff'}=&format_price($check_pretot);
			
			if($check_pretot!=0 or $in{'dototemp'}eq"YES") {
				$va{'finish'}="0";
				$va{'script_url'}= $cfg{'pathcgi_ajaxfinance'};
				$va{'cmdtoapply'}="editing_movements";
				$va{'btntxt'}="<input id='btnact' type='submit' align='center' value='Calcular' class='button' onclick='editmovements()'>";
			
			}else{
				$va{'finish'}="1";
				$va{'script_url'}= $cfg{'pathcgi_ajaxfinance'};
				$va{'cmdtoapply'}="editing_movements";
				$va{'btntxt'}="<input id='btnact' type='submit' align='center' value='Finalizar' class='button' onclick='editmovements()'>";
			}
		}
		
		$va{'view'}="<input type='hidden' name='view' value='$in{$cadidorders}'>";
		print &build_page('editing_movements.html');

	}else{

		##ToDo: Pagina de no autorizado
		print &build_page('unauth_small.html');
		
	}	
}

sub movements_actions{
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
# Last Modified on: 06/18/09 09:18:46
# Last Modified by: MCC C. Gabriel Varela S: Se arregla agregar movement
	my($type)=@_;
	my $sth,$rec,$bandextwar=0;
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	###############################################################################################################
	######ACCIONES PARA Movements##########################################################################
	###############################################################################################################
	
	####Eliminar/Inactivar movement####
	#&cgierr("MES: drop$type");
	$dropcad="drop$type";
	if($in{$dropcad})
	{
		$sth = &Do_SQL("SELECT * 
		FROM sl_movementstmp 
		WHERE ID_movements='$in{$dropcad}' 
		and ID_admin_users=$usr{'id_admin_users'}
		and Id_tableused=$in{$cadidorders} 
		and tableused='$cadtborders'");
		$rec=$sth->fetchrow_hashref;
		if($sth->rows>0)
		{
			if($rec->{'Status'}ne"Inactive")
			{
				if($rec->{'Action'}ne"Created")#Se modifica el status
				{
					&Do_SQL("Update sl_movementstmp 
					set Status='Inactive',Action='Edited' 
					where ID_movements='$in{$dropcad}' 
					and ID_admin_users=$usr{'id_admin_users'}
					and Id_tableused=$in{$cadidorders} 
					and tableused='$cadtborders'");
				}
				else #Se elimina la fila
				{
					&Do_SQL("DELETE FROM sl_movementstmp 
					where ID_movements='$in{$dropcad}' 
					and ID_admin_users=$usr{'id_admin_users'}
					and Id_tableused=$in{$cadidorders} 
					and tableused='$cadtborders'");
				}
			}
		}
	}
	
	####Activar producto####
	if($in{'activpr'})
	{
		$sth = &Do_SQL("SELECT * 
		FROM sl_movementstmp 
		WHERE ID_movements='$in{'activpr'}' 
		and ID_admin_users=$usr{'id_admin_users'}
		and Id_tableused=$in{$cadidorders} 
		and tableused='$cadtborders'");
		$rec=$sth->fetchrow_hashref;
		if($sth->rows>0)
		{
			if($rec->{'Status'}ne"Active")
			{
				&Do_SQL("Update sl_movementstmp 
				set Status='Active',Action='Edited' 
				where ID_movements='$in{'activpr'}' 
				and ID_admin_users=$usr{'id_admin_users'}
				and Id_tableused=$in{$cadidorders} 
				and tableused='$cadtborders'");
			}
		}
	}
	
	####Duplicar producto####
	$duplcad="dupl$type";
	if($in{"dupl$type"})
	{
		$sth = &Do_SQL("SELECT * 
		FROM sl_movementstmp 
		WHERE ID_movements='$in{$duplcad}' 
		and ID_admin_users=$usr{'id_admin_users'}
		and Id_tableused=$in{$cadidorders} 
		and tableused='$cadtborders'");
		$rec=$sth->fetchrow_hashref;
		if($sth->rows>0)
		{
			#Obtener próximo ID
			$sth = &Do_SQL("SELECT max(ID_movements)+1 FROM sl_movementstmp");
			$lastid=$sth->fetchrow;

			my ($tmp_sth) = &Do_SQL("SELECT ID_accounts, Amount, Reference, EffDate, tableused, ID_tableused, Category, Credebit, ID_segments, ID_journalentries, Status FROM sl_movementstmp WHERE ID_movements=$in{$duplcad} and ID_admin_users=$usr{'id_admin_users'} and Id_tableused=$in{$cadidorders} and tableused='$cadtborders';");

			while( my( $tmp_id_accounts, $tmp_amount, $tmp_reference, $tmp_effdate, $tmp_tableused, $tmp_id_tableused, $tmp_category, $tmp_credebit, $tmp_id_segments, $tmp_id_journalentries, $tmp_status ) = $tmp_sth->fetchrow_array() )
			{
				&Do_SQL("INSERT INTO sl_movementstmp (ID_movements,ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,ID_journalentries,Status,ID_admin_users,Action,comefrom)
						VALUES ( $lastid,'$tmp_id_accounts','$tmp_amount','$tmp_reference','$tmp_effdate','$tmp_tableused','$tmp_id_tableused','$tmp_category','$tmp_credebit','$tmp_id_segments','$tmp_id_journalentries','$tmp_status',$usr{'id_admin_users'},'Created','Dupl' );");
			}
		}
	}
	
	####Add product####
	if($in{'addmovement'} and $type eq $in{'type'}) {
		$sth = &Do_SQL("SELECT max(ID_movements)+1 FROM sl_movementstmp");
		$lastid=$sth->fetchrow;
		$lastid=1 if !$lastid;
		my ($comefrom,$returnid);
		$comefrom="Add";
		my ($sth) = &Do_SQL("INSERT INTO sl_movementstmp SET ID_movements=$lastid,ID_accounts=$in{'addmovement'},Amount=0,EffDate=Curdate(),tableused='$cadtborders',ID_tableused=$in{$cadidorders},Category='Undefined',Credebit='$in{'type'}',ID_segments=0,ID_journalentries='',Status='Active',ID_admin_users='$usr{'id_admin_users'}',Action='Created',comefrom='$comefrom'");
	}
}

sub show_movements{
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
# Last Modified RB: 09/28/09  15:34:34 -- Se agregan colores de acuerdo a la fecha efectiva y se intercambian posiciones, primero se despliegan debits y despues credits.



	###############################################################################################################
	####Productos##################################################################################################
	###############################################################################################################
	my($type)=@_;
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my $tot_mov,$cadtoshow;
	my $movtot=0,$i=0,$d,$sku_id_p,$decor;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my @colors =("#ffefd5","#c1cdc1","#eedd82","#add8e6","#f0e68c","#eeeee0","deb887","d8bfd8","ffe4e1","b0c4de");
	my $actdate='';
	my $color_style = '';
	my %colors;
	my $x=-1;
	
	my ($sth) = &Do_SQL("SELECT COUNT(ID_movements)
	FROM sl_movementstmp
	WHERE tableused = '$cadtborders' 
	AND ID_tableused=$in{$cadidorders}
	AND Credebit = '$type'
	AND ID_admin_users = '$usr{'id_admin_users'}';");
	$va{"matches$type"} = $sth->fetchrow;
	
	if ($va{"matches$type"} > 0){

		# IF(ID_journalentries IS NULL OR ID_journalentries = '',0,ID_journalentries)
		my ($sth1) = &Do_SQL("SELECT sl_movementstmp.* 
							, IF(/*sl_journalentries.Status = 'New' OR */ sl_journalentries.ID_journalentries IS NULL,0,1)AS Posted
							, sl_journalentries.Status AS Stj
							FROM sl_movementstmp
							LEFT JOIN sl_journalentries USING(ID_journalentries)
							WHERE tableused = '$cadtborders' 
							AND ID_tableused = '$in{$cadidorders}'
							AND Credebit = '$type'
							AND sl_movementstmp.ID_admin_users = '$usr{'id_admin_users'}'
							ORDER BY EffDate,sl_movementstmp.Status,ID_movements");

		my $gvcolor;
		
		while ($col = $sth1->fetchrow_hashref){

			#&cgierr($col->{'Status'}) if $col->{'ID_movements'} eq '22981';
			(!$col->{'ID_journalentries'}) and ($col->{'ID_journalentries'} = 0);
			if($actdate ne $col->{'EffDate'}){
				$x++;
				$actdate = $col->{'EffDate'};
			}
			
			if($col->{'Action'}eq"Original"){
				$gvcolor="green";
			}elsif($col->{'Action'}eq"Edited"){
				$gvcolor="blue";
			}elsif($col->{'Action'}eq"Created"){
				$gvcolor="red";
			}

			$i++;
			$d = 1 - $d;
			my($status,%tmp);
			
			$movtot=$col->{'Amount'};
			$cadtoshow=&load_name('sl_accounts','ID_accounts',$col->{'ID_accounts'},'Name');
			
			if ($col->{'Status'} eq 'Inactive'){
				$decor = 'style="text-decoration: line-through;background-color:'.$colors[$x].';"';
			}else{
				$tot_mov +=$movtot;
				$decor = 'style="background-color:'.$colors[$x].';"';
			}
			
			$va{"searchresults$type"} .= "<tr $decor >\n";
			$va{"searchresults$type"} .= "  <td class='smalltext'>";
			
			if($col->{'Status'} ne 'Inactive'){
				(!$col->{'Posted'}) and ($va{"searchresults$type"} .= qq| <a href="$script_url?cmd=[in_cmd]&tableused=$cadtborders&$cadidorders=$in{$cadidorders}&drop$type=$col->{'ID_movements'}&path=$in{'path'}&edit_type=$in{'edit_type'}&type=$type"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark_off.gif' title='Drop' alt='' border='0'></a>|);
				$va{"searchresults$type"} .= qq| <a href="$script_url?cmd=[in_cmd]&tableused=$cadtborders&$cadidorders=$in{$cadidorders}&dupl$type=$col->{'ID_movements'}&path=$in{'path'}&edit_type=$in{'edit_type'}&type=$type"><img src='$va{'imgurl'}/$usr{'pref_style'}/duplicate.gif' title='Duplicate' alt='' border='0'></a>|;
			
			}elsif($col->{'Status'} eq 'Inactive' or $col->{'Status'} eq '' or $col->{'ID_journalentries'}){
				$va{"searchresults$type"} .= qq| <a href="$script_url?cmd=[in_cmd]&tableused=$cadtborders&$cadidorders=$in{$cadidorders}&activpr=$col->{'ID_movements'}&path=$in{'path'}&edit_type=$in{'edit_type'}&type=$type"><img src='$va{'imgurl'}/$usr{'pref_style'}/checkmark.gif' title='Activate' alt='' border='0'></a>|;
			}

			my $accountnumber=&load_name('sl_accounts','ID_accounts',$col->{'ID_accounts'},'ID_accounting');
			my $accountname=&load_name('sl_accounts','ID_accounts',$rec->{'ID_accounts'},'Name');
			my $segmentname = $rec->{'ID_segments'} > 0 ? &load_name('sl_accounts_segments','ID_segments',$rec->{'ID_segments'},'Name') : 'N/A';


			$va{"searchresults$type"} .= "</td>";
			$va{"searchresults$type"} .= " <td class='smalltext' valign='top'>";
			
			$va{"searchresults$type"} .= "<br>".&format_account($accountnumber);
			$va{"searchresults$type"} .= "</td>\n";
			$va{"searchresults$type"} .= "  <td class='smalltext' valign='top'>".substr($cadtoshow,0,30)."</td>\n";
			
			if($col->{'Status'} eq 'Inactive' or $col->{'Posted'}) { 
				#Se muestran textos

				$va{"searchresults$type"} .= "  <td class='smalltext'>$segmentname $txtp </td>";
				$va{"searchresults$type"} .= "  <td class='smalltext' valign='top'>$col->{'Category'}</td>\n";
				$va{"searchresults$type"} .= "  <td class='smalltext' align='right' valign='top' nowrap>".&format_price($col->{'Amount'})."</td>";
				$va{"searchresults$type"} .= "  <td class='smalltext' align='right' valign='top' nowrap>$col->{'EffDate'}</td>";
				$va{"searchresults$type"} .= "  <td class='smalltext' align='right' valign='top' nowrap>$col->{'ID_journalentries'}</td>";
			
			}else {
				#Se muestran cajas de edición

				$va{"searchresults$type"} .= "  <td class='smalltext' valign='top' $decor nowrap>
													<select name='segment_$col->{'ID_movements'}' onFocus='focusOn( this )' onBlur='focusOff( this )'>
														".&build_select_segments($col->{'ID_segments'})."
													</select>
												</td>\n";
				$va{"searchresults$type"} .= "  <td class='smalltext' valign='top' $decor nowrap>
													<select name='category_$col->{'ID_movements'}' onFocus='focusOn( this )' onBlur='focusOff( this )'>
														".&build_select_fcategory($col->{'Category'})."
													</select>
												</td>\n";
				$va{"searchresults$type"} .= "  <td class='smalltext' align='right' valign='top' nowrap><input type='hidden' name='upd_$col->{'ID_movements'}' value='$col->{'ID_movements'}'><input size=5 type='text' name='amount_$col->{'ID_movements'}' value='$col->{'Amount'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
				$va{"searchresults$type"} .= "  <td class='smalltext' align='right' valign='top' nowrap><input size=12 type='text' name='effdate_$col->{'ID_movements'}' value='$col->{'EffDate'}' size='30' onFocus='focusOn( this )' onBlur='focusOff( this );' onChange='change_txt_button'></td>";
				$va{"searchresults$type"} .= "  <td class='smalltext' align='right' valign='top' nowrap>$col->{'ID_journalentries'}</td>";
			}
			$va{"searchresults$type"} .= "  <td class='tbltextttl' align='right' valign='top' nowrap><font color='$gvcolor'>$col->{'Action'}</font></td>\n";
		}
		$va{"searchresults$type"} .= qq|
			<tr>
				<td colspan='4' class='smalltext' align="right">|.&trans_txt('mer_vpo_total').qq|</td>
				<td align="right" class='smalltext' nowrap>|.&format_price($tot_mov).qq|</td>
			</tr>\n|;
	}
	else
	{
		$va{'pageslist'} = 1;
		$va{"searchresults$type"} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	return $tot_mov;
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
# Last Modified RB: 09/30/09  13:12:27 -- Se valida diferencia mayor o igual a 1 centavo


	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	$sth=&Do_SQL("Select if(not isnull(sum(if(Credebit='Credit',Amount,0))),sum(if(Credebit='Credit',Amount,0)),0)-if(not isnull(sum(if(Credebit='Debit',Amount,0))),sum(if(Credebit='Debit',Amount,0)),0)as Diff
from sl_movementstmp
where ID_admin_users=$usr{'id_admin_users'}
and Id_tableused=$in{$cadidorders} 
and tableused='$cadtborders'
and Status='Active'
group by ID_tableused");

	my $diff = $sth->fetchrow();

	if(($diff <= 0.0099 and $diff > 0) or ($diff < 0 and $diff >= -0.0099)){
		return 0.00;
	}else{
		return $diff;
	}
}

sub edit_addmovements{
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

	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();

	my ($query,$querytoapply,$str_id);
	$query=" and Status!='Inactive' ";
	if ($in{'keyword'}){
		$in{'keyword'}=&filter_values($in{'keyword'});
		$query .= " AND (Name like '%$in{'keyword'}%' OR Description like '%$in{'keyword'}%' OR ID_accounting like '%$in{'keyword'}%')";
	}
	$querytoapply="select COUNT(*)
	from sl_accounts
	WHERE 1 $query";
	my ($sth) = &Do_SQL($querytoapply);
	$va{'matches'} = $sth->fetchrow();
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/common/apps/ajaxfinance",$va{'matches'},$usr{'pref_maxh'});
		$querytoapply="select *
	from sl_accounts
	WHERE 1 $query 
	LIMIT $first,$usr{'pref_maxh'};";
		my ($sth) = &Do_SQL($querytoapply);
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$str_id = &format_account($rec->{'ID_accounting'});
			#Category
			$category=&load_name('sl_accategories','ID_accategories',$rec->{'ID_accategories'},'Name');
			#Parent
			$parent=&load_db_names('sl_accounts','ID_accounts',$rec->{'ID_parent'},'[ID_accounting]<br>[Name]');
			$va{'searchresults'} .= qq|
			<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' onclick="trjump('/cgi-bin/common/apps/ajaxfinance?cmd=editing_movements&$cadidorders=$in{$cadidorders}&addmovement=$rec->{'ID_accounts'}&path=$in{'path'}&tableused=$cadtborders&edit_type=$in{'edit_type'}&type=$in{'type'}')">
				<td class="smalltext" valign="top">$str_id</td>
				<td class="smalltext">$rec->{'Name'}</td>
				<td class="smalltext">$category</td>
				<td class="smalltext">$parent</td>
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
		    <td class="menu_bar_title">Account ID</td>
		    <td class="menu_bar_title">Name</td>
		    <td class="menu_bar_title">Category</td>
		    <td class="menu_bar_title">Belongs to account</td>
		 </tr>\n|;
	$in{'id_name'} = "$cadidorders";
	$in{'id_value'} = $in{$cadidorders};
	$in{'id_name2'} = "tableused";
	$in{'id_value2'} = $cadtborders;
	$in{'id_name3'} = "type";
	$in{'id_value3'} = $in{'type'};
	$in{'id_name4'} = "edit_type";
	$in{'id_value4'} = $in{'edit_type'};

	print "Content-type: text/html\n\n";
	print &build_page('searchid:addid.html');
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


	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();

	my ($sth,$rec);
	#############################################
	##################Productos##################
	#############################################
	$sth=&Do_SQL("Select *
	from sl_movementstmp 
	where ID_tableused=$in{$cadidorders} 
	and tableused='$cadtborders'
	and ID_admin_users=$usr{'id_admin_users'} 
	and Action!='Original'/* and comefrom!='Original'*/;");
	
	while($rec=$sth->fetchrow_hashref){
		##Editados##
		&Do_SQL("UPDATE sl_movements 
		SET 
		ID_segments='$rec->{'ID_segments'}',
		Category='$rec->{'Category'}',
		Amount=$rec->{'Amount'},
		EffDate='$rec->{'EffDate'}',
		Status='$rec->{'Status'}'
		/*,ID_admin_users=$rec->{'ID_admin_users'}*/ 
		where ID_movements=$rec->{'ID_movements'}")if($rec->{'Action'}eq'Edited');
		##Creados##
		&Do_SQL("INSERT INTO sl_movements (ID_accounts,Amount,EffDate,tableused,ID_tableused,Category,Credebit,ID_segments,Status ,Date ,Time ,ID_admin_users )
							VALUES ('$rec->{'ID_accounts'}','$rec->{'Amount'}','$rec->{'EffDate'}','$rec->{'tableused'}','$rec->{'ID_tableused'}','$rec->{'Category'}','$rec->{'Credebit'}','$rec->{'ID_segments'}','$rec->{'Status'}',Curdate(),Now(),'$rec->{'ID_admin_users'}');")if($rec->{'Action'}eq'Created');
	}
	
	#Se borran los registros de la orden con el usuario en la temporal
	&Do_SQL("DELETE FROM sl_movementstmp where ID_tableused=$in{$cadidorders} and tableused='$cadtborders' and ID_admin_users=$usr{'id_admin_users'};");
	&auth_logging('opr_orders_movements_edited',$in{$cadidorders});
}

sub update_updatables{
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
	
	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();
	
	my $key,$id_segments,$category,$amount,$cadsegment,$cadcategory,$cadamount,$oldsegment,$oldcategory,$oldamount,$bandedition=0,$cadamt,$amount,$oldamt,$cadeffdate,$effdate,$oldeffdate;
	$va{'bandedition'}=0;
	foreach my $key (sort(keys %in)) {
		
		if($key =~/^(upd_)(\d+)/) {

			$cadsegment="segment_$2";
			$cadcategory="category_$2";
			$cadamount="amount_$2";
			$cadeffdate="effdate_$2";
			$id_segments=$in{$cadsegment};
			$category=$in{$cadcategory};
			$amount=$in{$cadamount};
			$effdate=$in{$cadeffdate};
			$oldsegment=&load_name('sl_movementstmp','ID_movements',$2,'ID_segments');
			$oldcategory=&load_name('sl_movementstmp','ID_movements',$2,'Category');
			$oldamount=&load_name('sl_movementstmp','ID_movements',$2,'Amount');
			$oldeffdate=&load_name('sl_movementstmp','ID_movements',$2,'EffDate');
#			$category=$oldcategory if($category eq "");
#			$amount=$oldamount if($amount eq "");
#			$effdate=$oldeffdate if($effdate eq "");
			#&cgierr("$cadcategory:$cadamount:$cadeffdate:$oldcategory!=$category or $amount!=$oldamount or $effdate!=$oldeffdate")if($2==5);
			
			if($oldcategory ne $category or $amount ne $oldamount or $effdate ne $oldeffdate or $oldsegment ne $id_segments){
				$bandedition=1;
				$va{'bandedition'}=1;
				&Do_SQL("UPDATE sl_movementstmp SET ID_segments='$id_segments',Category='$category',Amount='$amount',EffDate='$effdate',Action=if(comefrom!='Original',Action,'Edited') where ID_movements=$2");
			}
		}
  	}
}

sub list_vendor_bills {
	$sth = &Do_SQL("SELECT  ID_bills,  ID_vendors,  Type,  Currency,  Amount,  Terms,  Memo,  BillDate,  DueDate,  AuthBy,  Status,  Date,  Time,  ID_admin_users FROM sl_bills Order By Date DESC");
	while($rec=$sth->fetchrow_hashref) {

	}
	
	print "Content-type: text/html\n\n";
	print &build_page('ajaxbuild:vendors_bills.html');
}

#############################################################################
#############################################################################
# Function: movements_editor
#
# Es: Editor de movimientos Contables
# En: 
#
# Created on: 19/07/2016 
#
# Author: Ing. Fabián Cañaveral
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub movements_editor{
#############################################################################
#############################################################################
	use Data::Dumper;
	use JSON;

	my ($cadtborders,$cadtbproducts,$cadtbproductstmp,$cadtbpayments,$cadtbpaymentstmp,$cadtbcustomers,$cadidorders,$cadidorderproducts,$cadidorderpayments,$cadidcustomers)=&edition_type();


	if(!&check_permissions('edit_movements','','')) {
		print "Content-type: text/html\n\n";
		print &build_page('unauth_small.html');
		return;
	}
	print "Content-type: text/html\n\n";
	$movements = &Do_SQL("
	SELECT 
		sl_accounts.ID_accounting
		, sl_accounts.Name AccountName
		, sl_movements.ID_segments
		, sl_accounts_segments.Name SegmentName
		, sl_movements.Category
		, IF(sl_movements.Credebit = 'Debit', sl_movements.Amount, 0) Debit
		, IF(sl_movements.Credebit = 'Credit', sl_movements.Amount, 0) Credit
		, sl_movements.Amount
		, sl_movements.EffDate
		, sl_movements.Status 
		, sl_movements.ID_movements
		, sl_movements.ID_accounts
		, sl_movements.Reference
		, sl_movements.Credebit
		, sl_movements.ID_segments
		, sl_movements.ID_journalentries
		, sl_movements.tablerelated
		, sl_movements.ID_tablerelated
	FROM sl_movements 
	LEFT JOIN sl_accounts on sl_movements.ID_accounts = sl_accounts.ID_accounts
	LEFT JOIN sl_accounts_segments on sl_movements.ID_segments = sl_accounts_segments.ID_accounts_segments
	LEFT JOIN sl_journalentries on sl_journalentries.ID_journalentries = sl_movements.ID_journalentries
	INNER JOIN sl_accounting_periods on sl_accounting_periods.Status = 'Open'
	WHERE 1
		AND sl_movements.Id_tableused=$in{$cadidorders}
		AND sl_movements.tableused='$cadtborders' 
		AND sl_movements.Status = 'Active'
		AND sl_journalentries.ID_journalentries is null
		AND sl_movements.EffDate between sl_accounting_periods.From_Date AND sl_accounting_periods.To_Date
	ORDER BY sl_movements.ID_movements DESC;");
	
	# print '<pre>';
	@results = ();
	while ($rec = $movements->fetchrow_hashref() ) {
		my %temp = (
			'ID_tableused' => $in{$cadidorders},
			'tableused' => $cadtborders,
			'ID_movements' => $rec->{'ID_movements'},
			'ID Account' =>&format_account($rec->{'ID_accounting'}),
			'Account Name' => $rec->{'AccountName'},
			'Segment' => $rec->{'ID_segments'},
			'Category' => $rec->{'Category'},
			'Debit' => $rec->{'Debit'},
			'Credit' => $rec->{'Credit'},
			'Eff Date' => $rec->{'EffDate'},
			'Journal Entry' => $rec->{'ID_journalentries'},
			'Table Related' => $rec->{'tablerelated'},
			'ID tablerelated' => $rec->{'ID_tablerelated'}
		);


		push @results, \%temp;
	}

	my ($sth) = &Do_SQL("SELECT * FROM sl_accounts_segments ORDER BY Name;");
	$output .= "<option value='0'>".&trans_txt('none')."</option>\n";
	while ($rec = $sth->fetchrow_hashref){
		my $selectedtxt = $rec->{'ID_accounts_segments'} == $id_segments ? "selected" : '';
		$output .= "<option value='$rec->{'ID_accounts_segments'}' $selectedtxt>$rec->{'Name'}</option>\n";
	}

	$va{'segments'} = &table_to_json('sl_accounts_segments', 'ID_accounts_segments Id, Name', "Status = 'Active'");

	$va{'categories'} = &enum_to_json('sl_movements','Category');

	$va{'data'} = encode_json \@results;

	$va{'tableused'} = $cadtborders;

	$va{'id_tabled'} = $in{$cadidorders};
	# cgierr(Dumper \@results);
	$va{'tables'} = &table_to_json('sl_vars_config','sl_vars_config.Code Id, sl_vars_config.Code Name','command = \'movements_tablerelated\' ');

	$va{'urlservice'} = '/cgi-bin/common/apps/ajaxfinance';

	($va{'from_date'}, $va{'to_date'}) = &Do_SQL("select From_Date, To_Date from sl_accounting_periods 
		where 1
			AND Status = 'Open'
		order by id_accounting_periods desc
		limit 1")->fetchrow();

	if($in{'full'}){
		$va{'header'} = &build_page('header_ebar.html');
	}
	print &build_page('movements_editor.html');
}



#############################################################################
#############################################################################
# Function: movement_actions
#
# Es: Acciones de los movimientos
# En: 
#
# Created on: 20/07/2016 
#
# Author: Ing. Fabián Cañaveral
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub movement_actions{
#############################################################################
#############################################################################
	use Encode qw(decode encode);
	use Data::Dumper;
	use JSON;
	my %response = ();
	if(!&check_permissions('edit_movements','','')) {
		print "Content-type: text/html\n\n";
		print &build_page('unauth_small.html');
		return;
	}
	if($in{'description'}){
		$in{'description'} = &filter_values($in{'description'});
		$in{'description'} =encode('latin1', decode('utf8', $in{'description'}));
	}
	if(!$in{'action'}){
		$response{'code'} = 500;
	}
	if($in{'action'} eq 'add'){
		$response{'code'} = 200;
		if($in{'table'} and $in{'idtable'} ne ''){
			$query = "INSERT INTO sl_movements(ID_accounts, Amount, EffDate, ID_tableused, tableused, Category, Credebit, ID_segments, Status, Date, Time, ID_admin_users, tablerelated, id_tablerelated) VALUES";
			if($in{'id account'}){
				$in{'id account'} =~ s/-//g;
				$id_accounts = &Do_SQL("SELECT ID_accounts from sl_accounts where ID_accounting = '$in{'id account'}' and Status = 'Active' and isdetailaccount='Yes' limit 1")->fetchrow();
				if($id_accounts){
					$credebit = '';
					$amount = 0;
					if($in{'credit'} ne '0.00'){
						$amount = $in{'credit'};
						$credebit = 'credit';
					}else{
						$amount = $in{'debit'};
						$credebit = 'debit';
					}
					$query.=qq|('$id_accounts','$amount', '$in{'eff date'}', '$in{'table'}','$in{'idtable'}','$in{'category'}','$credebit', '$in{'segment'}','Active', curdate(),curtime(),'$usr{'id_admin_users'}', '$in{'table related'}', '$in{'id tablerelated'}')|;
					if($in{'eff date'}){
						$qry = "select count(*) R from sl_accounting_periods 
						where 1
							AND Status = 'Open'
							AND '$in{'eff date'}' BETWEEN from_date AND to_date 
						order by id_accounting_periods desc
						limit 1";
						$r = &Do_SQL($qry)->fetchrow();
						if($r > 0){
							$set .= " EffDate = '$in{'eff date'}',";
						}else{
							$response{'code'} = 500;
							$response{'msg'} = "Fecha fuera de periodo Activo";
						}
					}
					if($response{'code'} == 200){
						&Do_SQL($query);
						$id = &Do_SQL("SELECT LAST_INSERT_ID()")->fetchrow();
						if($in{'id_journalentries'}){
							&Do_SQL("UPDATE sl_movements SET ID_journalentries='$in{'id_journalentries'}' WHERE ID_movements = '$id' LIMIT 1");
						}
						if($in{'description'}){

							&Do_SQL("INSERT INTO `sl_movements_auxiliary` (`ID_movements`, `FieldName`, `FieldValue`) VALUES ('$id', 'Description', '$in{'description'}');");
						}
						$response{'code'} = 200;
						$response{'msg'} = 'Movimiento Contable Actualizado.';
						$in{'db'} = $in{'idtable'};
						&auth_logging('opr_orders_movements_added', $in{'table'});
					}
				}
				
			}
		}
	}
	if($in{'action'} eq 'update'){
		$response{'code'} = 200;
		if($in{'id_movements'}){
			$set = 'set';
			if($in{'category'}){
				$set .= " Category = '$in{'category'}',";
			}
			if($in{'credit'} and $in{'credit'} ne '0.00'){
				$set .= " Credebit = 'Credit', Amount ='$in{'credit'}',";
			}
			if($in{'debit'} and $in{'debit'} ne '0.00'){
				$set .= " Credebit = 'Debit', Amount ='$in{'debit'}',";
			}
			if($in{'eff date'}){
				$qry = "select count(*) R from sl_accounting_periods 
				where 1
					AND Status = 'Open'
					AND '$in{'eff date'}' BETWEEN from_date AND to_date 
				order by id_accounting_periods desc
				limit 1";
				$r = &Do_SQL($qry)->fetchrow();
				if($r > 0){
					$set .= " EffDate = '$in{'eff date'}',";
				}else{
					$response{'code'} = 500;
					$response{'msg'} = "Fecha fuera de periodo Activo";
				}
			}

			if($in{'ID_journalentries'}){
				$set .= " ID_journalentries = '$in{'ID_journalentries'}',";
			}
			if($in{'table related'}){
				$set .= " tablerelated = '$in{'table related'}',";
			}
			if($in{'id tablerelated'}){
				$set .= " id_tablerelated = '$in{'id tablerelated'}',";
			}
			if($in{'id account'}){
				$in{'id account'} =~ s/-//g;
				$id_accounts = &Do_SQL("SELECT ID_accounts from sl_accounts where ID_accounting = '$in{'id account'}' and Status = 'Active' and isdetailaccount='Yes' limit 1")->fetchrow();
				$set .= " ID_accounts='$id_accounts',";
			}
			if($in{'segment'}){
				$set .= " ID_segments = '$in{'segment'}',";
			}
			if($set ne 'set' and $response{'code'} != 500){
				chop($set);
				$query = "UPDATE sl_movements $set where ID_movements = '$in{'id_movements'}'";
				&Do_SQL($query);
				if($in{'description'}){

					$count = &Do_SQL("SELECT count(*) FROM sl_movements_auxiliary WHERE id_movements = '$in{'id_movements'}' AND FieldName = 'Description'")->fetchrow();
					if($count > 0){
						&Do_SQL("UPDATE `sl_movements_auxiliary` SET FieldValue ='$in{'description'}' WHERE ID_movements = '$in{'id_movements'}' AND FieldName = 'Description'");
					}else{
						&Do_SQL("INSERT INTO `sl_movements_auxiliary` (`ID_movements`, `FieldName`, `FieldValue`) VALUES ('$in{'id_movements'}', 'Description', '$in{'description'}');");
					}
				}
				$response{'msg'} = 'Movimiento Contable Actualizado.';
				$in{'db'} = $in{'idtable'};
				&auth_logging('opr_orders_movements_updated', $in{'table'});

			}
		}
	}

	if($in{'action'} eq 'remove'){
		$response{'code'} = 500;
		if($in{'id_movements'}){
			&Do_SQL("UPDATE sl_movements set Status='Inactive' where ID_movements = '$in{'id_movements'}'");
			$response{'code'} = 200;
			$response{'msg'} = 'Movimiento Borrado Satisfactoriamente.';
			$in{'db'} = $in{'idtable'};
			&auth_logging('opr_orders_movements_deleted',$in{'table'});

		}
	}

	if($in{'action'} eq 'validateDate'){
		$response{'code'} = 500;
		$qry = "select count(*) R from sl_accounting_periods 
		where 1
			AND Status = 'Open'
			AND '$in{'date'}' BETWEEN from_date AND to_date 
		order by id_accounting_periods desc
		limit 1";
		$r = &Do_SQL($qry)->fetchrow();
		if($r > 0){
			$response{'code'} = 200;
		}else{
			$response{'code'} = 500;
			$response{'msg'} = "Fecha fuera de periodo Activo";
		}
	}

	if($in{'action'} eq 'getAll'){
		$response{'code'} = 500;
		if($in{'table'} and $in{'idtable'} ne ''){
			$response{'code'} = 200;
			$filter = '';
			if($in{'table'} eq 'Unknown' and $in{'ID_journalentries'}){
				$filter = "AND ID_journalentries = '$in{'ID_journalentries'}'";
			}
			$movements = &Do_SQL("
			SELECT 
				sl_accounts.ID_accounting
				, sl_accounts.Name AccountName
				, sl_movements.ID_segments
				, sl_accounts_segments.Name SegmentName
				, sl_movements.Category
				, IF(sl_movements.Credebit = 'Debit', sl_movements.Amount, 0) Debit
				, IF(sl_movements.Credebit = 'Credit', sl_movements.Amount, 0) Credit
				, sl_movements.Amount
				, sl_movements.EffDate
				, sl_movements.Status 
				, sl_movements.ID_movements
				, sl_movements.ID_accounts
				, sl_movements.Reference
				, sl_movements.Credebit
				, sl_movements.ID_segments
				, sl_movements.ID_journalentries
				, sl_movements.tablerelated
				, sl_movements.ID_tablerelated
				, sl_movements.Status
			FROM sl_movements 
			LEFT JOIN sl_accounts on sl_movements.ID_accounts = sl_accounts.ID_accounts
			LEFT JOIN sl_accounts_segments on sl_movements.ID_segments = sl_accounts_segments.ID_accounts_segments
			LEFT JOIN sl_journalentries on sl_journalentries.ID_journalentries = sl_movements.ID_journalentries
			WHERE 1
				AND sl_movements.Id_tableused=$in{'idtable'}
				AND sl_movements.tableused='$in{'table'}' 
				$filter
			ORDER BY sl_movements.ID_movements DESC;");
			@results = ();
			while ($rec = $movements->fetchrow_hashref() ) {
				my %temp = (
					'ID_movements' => $rec->{'ID_movements'},
					'ID Account' =>&format_account($rec->{'ID_accounting'}),
					'Account Name' => $rec->{'AccountName'},
					'Segment' => $rec->{'ID_segments'},
					'Category' => $rec->{'Category'},
					'Debit' => $rec->{'Debit'},
					'Credit' => $rec->{'Credit'},
					'Eff Date' => $rec->{'EffDate'},
					'Journal Entry' => $rec->{'ID_journalentries'},
					'Table Related' => $rec->{'tablerelated'},
					'ID tablerelated' => $rec->{'ID_tablerelated'},
					'Status' => $rec->{'Status'}
				);
				push @results, \%temp;
			}
			$response{'data'} = \@results;
		}
	}
	
	print "Content-type: application/json\n\n";
	print encode_json \%response;
}


#############################################################################
#############################################################################
# Function: rs_to_json
#
# Es: Devuelve json de una consulta simple
# En: 
#
# Created on: 20/07/2016 
#
# Author: Ing. Fabián Cañaveral
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub get_account_name{
#############################################################################
#############################################################################
	if(!$in{'id'}){
		print "Content-type: application/json\n\n";	
		print qq|{"code":500}|;
		return;
	}
	$response = &table_to_json('sl_accounts', 'name', "id_accounting=$in{'id'} and status= 'Active' and isdetailaccount='Yes' ");
	print "Content-type: application/json\n\n";
	print $response;
}


#############################################################################
#############################################################################
# Function: adjustment_editor
#
# Es: Editor de movimientos Contables
# En: 
#
# Created on: 19/07/2016 
#
# Author: Ing. Fabián Cañaveral
#
# Modifications:
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#
sub adjustment_editor{
#############################################################################
#############################################################################
	use Data::Dumper;
	use JSON;

	print "Content-type: text/html; charset=UTF-8\n\n";

	if($in{'exchange_rate'})
	{
		$va{'exchange_rate'} = $in{'exchange_rate'};
	}

	if($in{'action'})
	{ 

		$in{'id_extracharges'} = int($in{'id_extracharges'});
		
		if (!$in{'description'}){
			$error{'description'} = &trans_txt('required');
			++$err;
		}
		
		if (!$in{'amount'}){
			$error{'amount'} = &trans_txt('required');
			++$err;
		}
		
		if (!$in{'amount_original'}){
			$error{'amount_original'} = &trans_txt('required');
			++$err;
		}

		if (!$in{'id_extracharges'}){
			$error{'id_extracharges'} = &trans_txt('required');
			++$err;
		}else{
			my ($sth) = &Do_SQL("SELECT Name,ID_accounts FROM sl_extracharges WHERE ID_extracharges = '$in{'id_extracharges'}';");
			($in{'type'}, $in{'id_accounts'}) = $sth->fetchrow_array();
			if (!$in{'id_accounts'}){
				$error{'id_extracharges'} = &trans_txt('required');
				++$err;
			}
			my ($sth) = &Do_SQL("SELECT sl_extracharges.Tax_percent FROM sl_extracharges WHERE sl_extracharges.ID_extracharges = ".$in{'id_extracharges'}.";");
			($in{'tax_percent'}) = $sth->fetchrow_array();
			if ($in{'tax_percent'} eq '') {
				$error{'id_extracharges'} = &trans_txt('notfound')." Tax Percent";
				++$err;
			}
		}

		(!$in{'id_extvendors'}) and ($in{'id_extvendors'} = $in{'id_vendors'});

		##--------------------------------------------------
		## Se validan los montos dependiendo del Currency
		## del Vendor-PO y del Vendor-Adj.
		##--------------------------------------------------
		# $currency_vendor_adj	= &load_name('sl_vendors','ID_vendors',$in{'id_extvendors'},'Currency');
		# $currency_vendor_po		= &load_name('sl_vendors','ID_vendors',$in{'id_vendors'},'Currency');			
		
		# if (($currency_vendor_adj eq $currency_vendor_po) and ($in{'amount_original'} != $in{'amount'})){
		# 	$error{'amount'} = &trans_txt('invalid');
		# 	$error{'amount_original'} = &trans_txt('invalid');
		# 	++$err;
		# }
		##--------------------------------------------------

		if ($err>0){
				
			$error{'message'} = &trans_txt('reqfields');
			my $json_txt = encode_json \%error;			 
			print $json_txt;
			exit;

		}else{				
			($in{'tax_percent'} > 1) ? ($in{'tax_percent'} = $in{'tax_percent'} / 100) : ($in{'tax_percent'});
			#($in{'incogs'}) ? ($query = ",InCOGS='Yes'"):($query = ",InCOGS='No'");
			my $InCogs = load_name('sl_extracharges', 'ID_extracharges', $in{'id_extracharges'}, 'InCOGS');
			$query = ",InCOGS='".$InCogs."'";
			my $tax = $in{'amount'} * $in{'tax_percent'};
			my $total = $in{'amount'} + $tax;
			$va{'tabmessages'} = &trans_txt('mer_po_adj_added');
			my $total_original = ( $in{'tax_percent'} > 0 and $in{'amount_original'} > 0 ) ? $in{'amount_original'} * ($in{'tax_percent'} + 1) : 0;
			my ($sth) = &Do_SQL("INSERT INTO sl_purchaseorders_adj SET ID_purchaseorders = '$in{'id_purchaseorders'}', ID_vendors = '$in{'id_extvendors'}', ID_accounts = '$in{'id_accounts'}' $query  , Description = '$in{'description'}', Amount = '$in{'amount'}',  Amount_original = '$in{'amount_original'}', Tax_percent = '$in{'tax_percent'}', Tax = '$tax', Total = '$total', TotalOriginal = '$total_original', Type = '$in{'type'}', Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			delete($in{'description'});
			delete($in{'amount'});
			delete($in{'amount_original'});
			delete($in{'tax_percent'});
			$va{'searchresults'} .= "<script language=\"JavaScript1.2\">\ntrjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&tab=2&tabmessages=$va{'tabmessages'}')\n</script>";
			&auth_logging('mer_po_adj_added',$in{'id_purchaseorders'});
		}

		exit;
	}

	my ($err,$item,$query);
	my ($authby) = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'AuthBy');
	$in{'status'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Status') if (!$in{'status'});
	my ($permadj) = &check_permissions('mer_po_adjustments','','');

	if($in{'drop'} and ($permadj or $authby)){
		$va{'tabmessages'} = &trans_txt('mer_po_adj_del');
		my ($sth) = &Do_SQL("DELETE FROM sl_purchaseorders_adj WHERE ID_purchaseorders_adj='$in{'drop'}'");
		#$va{'searchresults'} .= "<script language=\"JavaScript1.2\">\ntrjump('/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_po&view=$in{'id_purchaseorders'}&tab=2&tabmessages=$va{'tabmessages'}')\n</script>";
		&auth_logging('mer_po_adj_del',$in{'id_purchaseorders'});
	}

	my ($sth) = &Do_SQL("	SELECT currency 
							FROM sl_purchaseorders INNER JOIN sl_vendors ON sl_purchaseorders.ID_vendors = sl_vendors.ID_vendors
							WHERE sl_purchaseorders.ID_purchaseorders = ".$in{'id_purchaseorders'}.";");
	$va{'po_currency'} = $sth->fetchrow;

	$in{'type'} = &load_name('sl_purchaseorders','ID_purchaseorders',$in{'id_purchaseorders'},'Type');

	if( !$permadj and ($authby or $in{'type'} eq 'Return to Vendor') or $in{'status'} eq 'Received' or $in{'status'} eq 'Cancelled') 
	{

		###################
		###################
		### PO Authorized or Return to Vendor
		###################
		###################

		$va{'po_blocked_start'} = '<!--';
		$va{'po_blocked_end'} = '-->';

		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|<tr><td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td></tr>\n|;

	}else{

		## LIST
		my ($choices_on, $tot_qty, $tot_po, $vendor_sku);
		my (@c) = split(/,/, $cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}'");
		$va{'matches'} = $sth->fetchrow;

		if ($va{'matches'}>0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_purchaseorders_adj WHERE ID_purchaseorders='$in{'id_purchaseorders'}' ORDER BY ID_purchaseorders_adj DESC;");
			while ($rec = $sth->fetchrow_hashref) {
				$d = 1 - $d;
				my $id_products_code = substr($rec->{'ID_products'},0,3) .'-'.substr($rec->{'ID_products'},3,3);
				my $vname = &load_name('sl_vendors', 'ID_vendors', $rec->{'ID_vendors'}, 'CompanyName');

				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				my ($drop_item) = '';
				if ( ($authby or $permadj) and $rec->{'Validate'} == 0 ){
					$drop_item = "<a href='/cgi-bin/common/apps/ajaxfinance?cmd=adjustment_editor&id_purchaseorders=$rec->{'ID_purchaseorders'}&drop=$rec->{'ID_purchaseorders_adj'}'>
									<img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'>
								</a>";
				}
				
				$va{'searchresults'} .= "   <td class='smalltext'>".$drop_item."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>".$rec->{'Type'}."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$vname <a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_vendors&view=$rec->{'ID_vendors'}'>( $rec->{'ID_vendors'} )</a></td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Description'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount_original'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Tax'})." (".($rec->{'Tax_percent'}*100)." %)</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
				$tot_po += $rec->{'Total'};
			}

			$va{'searchresults'} .= qq|
				<tr>
					<td colspan='6' class='smalltext' align="right">|.&trans_txt('mer_po_total').qq|</td>
					<td align="right" class='smalltext'>|.&format_price($tot_po).qq|</td>
				</tr>\n|;

		}else{

			$va{'pageslist'} = 1;
			$va{'searchresults'} = qq|
				<tr>
					<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
				</tr>\n|;

		}

		$in{'tax_percent'} = $cfg{'taxp_default'} * 100 if !$in{'tax_percent'};

	}


	print &build_page('adjustment_editor.html');
}





1;
