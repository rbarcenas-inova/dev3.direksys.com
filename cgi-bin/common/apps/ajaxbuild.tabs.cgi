sub orders_tab1{
# --------------------------------------------------------
# Forms Involved: products_tab2
# Created on: 06/23/2008 12:00 PM
# Last Modified on:
# Last Modified by:
# Author: Jose Ramirez Garcia
# Description : order actions menu
# Parameters :
# Last Modified on: 11/18/08 13:09:45
# Last Modified by: MCC C. Gabriel Varela S: Se agrega edici?n de ?rdenes
# Last Modified on: 12/03/08 09:56:13
# Last Modified by: MCC C. Gabriel Varela S: Dependiendo de la variable de configuraci?n order_edition se mostrar? o no el men? de edici?n de ?rdenes.
# Last Modified on: 12/04/08 09:24:12
# Last Modified by: MCC C. Gabriel Varela S: Se deja s?lo Edit order dependiendo de la variable de sistema.
# Last Modified on: 12/11/08 11:54:54
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta old_order_edition
	if($ENV{'HTTP_REFERER'} =~ /admin/){
		$mod = 'adm';
	} elsif($ENV{'HTTP_REFERER'} =~ /crm/){
		$mod = 'ccs';
	} elsif($ENV{'HTTP_REFERER'} =~ /crm/){
		$mod = 'fup';
	}
	print "Content-type: text/html\n\n";
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			|;
	print qq|
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_item(); popup_exit();">&nbsp;&nbsp; Add new Item</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_nitem(); popup_exit();">&nbsp;&nbsp; Add Non Inventory</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="shp_disc(); popup_exit();">&nbsp;&nbsp; Shipping Discount</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="shp_chrg(); popup_exit();">&nbsp;&nbsp; Shipping Charges</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_retfee(); popup_exit();">&nbsp;&nbsp; Return Fee</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_resfee(); popup_exit();">&nbsp;&nbsp; ReStock Fee</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="enter_shp(); popup_exit();">&nbsp;&nbsp; Enter Shipment</td>
			</tr>			
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="adjust_price(); popup_exit();">&nbsp;&nbsp; Adjust Price</td>
			</tr>			
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_return(); popup_exit();">&nbsp;&nbsp; Add return</td>
			</tr>
	|if($cfg{'order_old_edition'}==1);
	if($cfg{'order_old_edition'}==1 && $cfg{'add_sample_'.$mod} == 1){
		print qq|<tr>
			<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_sample(); popup_exit();">&nbsp;&nbsp; Add sample</td>
		</tr>|;		
	}
	print qq|
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="edit_order(); popup_exit();">&nbsp;&nbsp; Edit order</td>
			</tr>
	|if($cfg{'order_edition'}==1);
	
	print qq|
		</table>
	|;
	
}


sub orders_tab15{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/16/09 17:32:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: text/html\n\n";
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			|;
	print qq|
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="edit_movements(); popup_exit();">&nbsp;&nbsp; Edit Movements</td>
			</tr>
	|;
	print qq|
		</table>
	|;
}

sub purchaseorders_tab9{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/16/09 17:32:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: text/html\n\n";
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			|;
	print qq|
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="edit_movements(); popup_exit();">&nbsp;&nbsp; Edit Movements</td>
			</tr>
	|;
	print qq|
		</table>
	|;
}

sub adjustments_tab5{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 06/16/09 17:32:26
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	print "Content-type: text/html\n\n";
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			|;
	print qq|
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="edit_movements(); popup_exit();">&nbsp;&nbsp; Edit Movements</td>
			</tr>
	|;
	print qq|
		</table>
	|;
}


sub returns_tab3{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10/22/2008 17:38 
# Last Modified on:
# Last Modified by:
# Author: MCC C. Gabriel Varela S.
# Description : 
# Parameters :
	print "Content-type: text/html\n\n";
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_upc(); popup_exit();">&nbsp;&nbsp; Add new UPC</td>
			</tr>					
		</table>
	
	|;
	
}

sub orders_tab2{
# --------------------------------------------------------
# Forms Involved: products_tab2
# Created on: 06/23/2008 12:00 PM
# Last Modified on: 08/01/2008
# Last Modified by:Jose Ramirez Garcia
# Author: Jose Ramirez Garcia
# Description : order actions menu
# Parameters :
# Last Modified on: 11/18/08 13:18:27
# Last Modified by: MCC C. Gabriel Varela S: Se agrega edici?n de ?rdenes
# Last Modified on: 12/03/08 09:57:24
# Last Modified by: MCC C. Gabriel Varela S: Dependiendo de la variable de configuraci?n order_edition se mostrar? o no el men? de edici?n de ?rdenes.
# Last Modified on: 12/04/08 09:26:42
# Last Modified by: MCC C. Gabriel Varela S: Remover del tab2, Duplicate Payments, Add Credit Card, Add Check, Add Charge, Add Insurance Payment
# Last Modified on: 12/11/08 11:54:54
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta old_order_edition
	print "Content-type: text/html\n\n";
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_flexipay(); popup_exit();">&nbsp;&nbsp; Duplicate Payments</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_cc(); popup_exit();">&nbsp;&nbsp; Add Credit Card</td>
			</tr>
			
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="changecc(); popup_exit();">&nbsp;&nbsp; Change Credit Card</td>
			</tr>
			
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_chk(); popup_exit();">&nbsp;&nbsp; Add Check</td>
			</tr>
<!--	<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="upd_dts(); popup_exit();">&nbsp;&nbsp; Update Dates</td>
			</tr>-->
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_chrg(); popup_exit();">&nbsp;&nbsp; Add Charge</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_bb();popup_exit();">&nbsp;&nbsp; MFS Buy Back</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_fpd(); popup_exit();">&nbsp;&nbsp; MFS FPD</td>
			</tr>						
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_na(); popup_exit();">&nbsp;&nbsp; MFS not Accepted</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_na(); popup_exit();">&nbsp;&nbsp; Filter : not Cancelled</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_na(); popup_exit();">&nbsp;&nbsp; Filter : Remove Filter</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="add_inp(); popup_exit();">&nbsp;&nbsp; Add Insurance Payment</td>
			</tr>
	|if($cfg{'order_old_edition'}==1);
	print qq|

		<table border="0" cellspacing="0" width="120" class="formtable">
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="check_avs();">&nbsp;&nbsp; Check AVS</td>
			</tr>		
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="changecc(); popup_exit();">&nbsp;&nbsp; Change Credit Card</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_bb();popup_exit();">&nbsp;&nbsp; MFS Buy Back</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_fpd(); popup_exit();">&nbsp;&nbsp; MFS FPD</td>
			</tr>						
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_na(); popup_exit();">&nbsp;&nbsp; MFS not Accepted</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_na(); popup_exit();">&nbsp;&nbsp; Filter : not Cancelled</td>
			</tr>
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="mfs_na(); popup_exit();">&nbsp;&nbsp; Filter : Remove Filter</td>
			</tr>

	|if($cfg{'order_old_edition'}==0);
	print qq|
			<tr>
				<td class="menu_bar" onmouseover='m_over(this)' onmouseout='m_out(this)' onClick="edit_order(); popup_exit();">&nbsp;&nbsp; Edit order</td>
			</tr>
	|if($cfg{'order_edition'}==1);
	print qq|
		</table>
	|;
}

sub vendors_tab8{
#-----------------------------------------
# Created on: 06/24/09  16:59:57 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 
	
	&html_print_headers('SOSL');
	
	###### Construimos el Listado de los POs con sus pagos
	my ($info);
	my ($sth) = &Do_SQL("SELECT 
											sl_purchaseorders.ID_purchaseorders,
											sl_purchaseorders.PODate,
											IF(PO IS NULL,0,PO) AS PO,
											IF(Payments IS NULL,0,Payments)AS Paid
											FROM sl_purchaseorders
											LEFT JOIN
											(
											SELECT ID_purchaseorders, SUM( Qty * Price ) AS PO
											FROM sl_purchaseorders_items
											GROUP BY ID_purchaseorders
											)AS tmp_po
											ON sl_purchaseorders.ID_purchaseorders = tmp_po.ID_purchaseorders
											LEFT JOIN
											(
											SELECT ID_purchaseorders, SUM( Amount ) AS Payments
											FROM sl_vendors_payments
											GROUP BY ID_purchaseorders
											)AS tmp_pay
											ON sl_purchaseorders.ID_purchaseorders = tmp_pay.ID_purchaseorders
											WHERE sl_purchaseorders.ID_vendors = $in{'id_vendors'}
											HAVING PO-Paid > 0 OR PO = 0 ");
		while(my($idpo,$date,$po,$paid) = $sth->fetchrow()){
			$info .=qq|<tr><td align="left">$idpo</td><td align="right">|.&format_price($po).qq|
								<td align="right">|.&format_price($paid).qq|
								<td><input type="text" name="po_$idpo" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'></td></tr>|;
			$po_list .= "$idpo,";
		}
		#<td>$date</td>									
		chop($po_list);									
	
	
	$strout .= qq|
		<form action="/cgi-bin/mod/$usr{'application'}/dbman" method="post" name="sitform" onsubmit="return disableSubmits();">
			<input type="hidden" name="cmd" value="mer_vendors">
			<input type="hidden" name="view" value="$in{'id_vendors'}">
			<input type="hidden" name="id_vendors" value="$in{'id_vendors'}">
			<input type="hidden" name="po_list" value="$po_list">
			<input type="hidden" name="add_payment" value="1">
			<input type="hidden" name="tab" value="8">
			
		
			<table border="0" cellspacing="0" cellpadding="2" width="450">
				<tr>
				  <td class="titletext" align="center" colspan="2">Add Payment</td>
				</tr>
			</table>
			
			<table border="0" cellspacing="0" cellpadding="2" width="100%">
				<tr>
			  	<td width="30%">Amount:</td>
					<td class="smalltext"><input type="text" name="amount" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>
				</tr>
				<tr>
			    <td valign="top" width="30%">Check Number:</td>
			    <td class="smalltext"><input type="text" name="checkn" size="20" onFocus='focusOn( this )' onBlur='focusOff( this )'></td>
				</tr>
				<!--
				<tr>
			    <td valign="top" width="30%">Prepaid:</td>
			    <td class="smalltext">
			    <input type="radio" name="prepaid" value="yes" class="radio">Yes &nbsp;&nbsp;
     			<input type="radio" name="prepaid" value="no" class="radio">No
			    </td>
				</tr>
				-->
				<tr><td colspan="2">&nbsp;</td></tr>
				<tr>
				  <td class="smalltext" colspan="2">
						<table align="center" width="100%">
							<tr>
								<td class="menu_bar_title" align="Center" width="25%">ID PO</td>
								<!--<td class="menu_bar_title" align="Center" width="25%">>Date</td>-->
								<td class="menu_bar_title" align="Center" width="25%">Total</td>
								<td class="menu_bar_title" align="Center" width="25%">Paid</td>
								<td class="menu_bar_title" align="Center" width="25%">&nbsp;</td>
							</tr>
							$info
						</table>
	     		</td>
			 	</tr>
			 </table>
			 <p align="center"><input type="submit" value="Add Payment" class="button"></p>
	  </form>|;
	  
	print $strout;
}

#############################################################################
#############################################################################
# Function: userman_tab2
#
# Es: Elimina usuario de un grupo
# En: 
#
# Created on: 02/08/2016 
#
# Author: Fabián Cañaveral
#
# Modifications: 
#		
#
# Parameters:
#
#
# Returns:
#
#
# See Also:
#
#  Todo: Funciones para agregar y editar.
#
sub userman_tab2{
#############################################################################
#############################################################################
	use JSON;
	my %response = ();
	$response{'code'} = 500;
	if(!&check_permissions('user_group_edit','','')) {
		$response{'msg'} = &trans_txt('unauth_action');
		print "Content-type: application/json\n\n";
		print encode_json \%response;
		return;
	}
	if($in{'action'} eq 'drop'){
		if($in{'id'}){
			&Do_SQL(qq|delete from admin_users_groups where id_admin_users_perms='$in{'id'}' limit 1|);
			$response{'code'} = 200;
			$response{'msg'} = &trans_txt('usrman_updated');
		}else{
			$response{'msg'} = &trans_txt('notappliead');
		}
	}
	print "Content-type: application/json\n\n";
	print encode_json \%response;

}

1;
