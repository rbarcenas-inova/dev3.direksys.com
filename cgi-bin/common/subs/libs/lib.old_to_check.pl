
sub load_shoppy {
# --------------------------------------------------------
	my ($style,$message);	
	if ($in{'cmd'} eq "opr_rmas"){
		$style="position:absolute;left:300px;top:180px;width:250px;height:100px;";
		$message = &trans_txt('opr_rmas_msg');
	}elsif ($in{'cmd'} eq "opr_rfas"){
		$style="position:absolute;left:300px;top:180px;width:250px;height:100px;";		
		$message = &trans_txt('opr_rfas_msg');
	}elsif ($in{'cmd'} eq "opr_rsas"){
		$style="position:absolute;left:300px;top:180px;width:250px;height:100px;";		
		$message = &trans_txt('opr_rsas_msg');
	}elsif ($in{'cmd'} eq "about"){
		$encrypt = &LeoEncrypt("hello world","abc123");
		$va{'encrypt'} = $encrypt;
		$va{'decrypt'} = &LeoDecrypt($encrypt,"abc123");
		$style="position:absolute;left:260px;top:149px;width:340px;height:100px;";
		$message = &trans_txt('about_general');
	}
	$va{'status_image'} = "<div style='$style'>$message</div><img src='[va_imgurl]/[ur_pref_style]/shoppy.jpg' alt='' border='0'></a>";	
}

sub log_finnance_tran {
# --------------------------------------------------------
	my ($type,$record)=@_
	##my ($sth) = &Do_SQL("INSERT INTO sl_financial SET Type='$1',ID_purchaseorders='wreceipt',Amount='".($cost*$items{$1})."',ID_trs='$2',tb_name='sl_purchaseorders_items',Date=Curdate(),Time=NOW(),ID_admin_users='$usr{'id_admin_users'}'");
}



#sub load_inventory_qty {
## --------------------------------------------------------
#
## Author: Jose Ramirez Garcia
## Created on: 07/18/2008
## Last Modified on: 
## Last Modified by: 
## Description : It returns the stock and quantity
## Forms Involved: sub build_track_link
## Parameters : 
#
#	my ($output_stock,$choices);
#	my (@c) = split(/,/,$cfg{'srcolors'});
#	my ($sth) = &Do_SQL("SELECT * FROM sl_warehouses_location,sl_warehouses WHERE sl_warehouses_location.ID_warehouses=sl_warehouses.ID_warehouses AND ID_products='$in{'idp'}' AND Quantity>0 ORDER BY sl_warehouses_location.ID_warehouses;");
#	while ($rec = $sth->fetchrow_hashref){
#		$d = 1 - $d;
#		$output_stock .= "<tr bgcolor='$c[$d]'>\n";
#		$output_stock .= "   <td class='smalltext'>$rec->{'ID_warehouses'} $rec->{'Name'} &lt;$rec->{'City'}, $rec->{'State'} &gt;</td>\n";
#		$output_stock .= "   <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID_products'})."</td>\n";
#		$output_stock .= "   <td class='smalltext' valign='top'>".&load_choices($rec->{'ID_products'})."</td>\n";
#		$output_stock .= "   <td class='smalltext' valign='top'>$rec->{'Location'}</td>\n";
#		$output_stock .= "   <td class='smalltext' align='right' valign='top'>$rec->{'Quantity'}</td>\n";
#		$output_stock .= "</tr>\n";
#	}
#
#	(!$output_stock) and ($output_stock = "<tr>\n<td colspan='4' align='center'>".&trans_txt('nostock')."</td></tr>");
#	return $output_stock;
#}
#
#sub load_po_list {
## --------------------------------------------------------
#
## Author: Jose Ramirez Garcia
## Created on: 07/18/2008
## Last Modified on: 
## Last Modified by: 
## Description : It returns the purchase orders list
## Forms Involved: sub build_track_link
## Parameters : 
#
#	if($in{'id_products'}){
#		my (@c) = split(/,/,$cfg{'srcolors'});
#		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products = '$in{'id_products'}'");
#		$va{'matches'} = $sth->fetchrow;
#		if ($va{'matches'}>0){
#			(!$in{'nh'}) and ($in{'nh'}=1);
#			my ($sth) = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders,Name, sl_purchaseorders.Status,Qty,Price,sl_purchaseorders_items.Date, Etd 
#													FROM sl_purchaseorders_items INNER JOIN sl_purchaseorders 
#													ON sl_purchaseorders_items.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
#													AND ID_products = '$in{'id_products'}' AND sl_purchaseorders_items.Qty>sl_purchaseorders_items.Received 
#													INNER JOIN sl_warehouses ON sl_purchaseorders.ID_warehouses = sl_warehouses.ID_warehouses
#													ORDER BY sl_purchaseorders_items.Date DESC;");
#			while ($rec = $sth->fetchrow_hashref){
#				$d = 1 - $d;
#				$output_po .= "<tr bgcolor='$c[$d]'>\n";
#				$output_po .= "   <td class='smalltext'>$rec->{'ID_purchaseorders'}</td>\n";
#				$output_po .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
#				$output_po .= "   <td class='smalltext'>$rec->{'Qty'}</td>\n";
#				$output_po .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Price'})."</td>\n";
#				$output_po .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
#				$output_po .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
#				$output_po .= "   <td class='smalltext'>$rec->{'ETD'}</td>\n";
#				$output_po .= "</tr>\n";
#			}
#		}else{
#			$output_po = qq|
#				<tr>
#					<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
#				</tr>\n|;
#		}
#	} else {
#		$output_po = qq|
#				<tr>
#					<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
#				</tr>\n|;
#	}
#	return $output_po;
#}
#
#sub load_po_notes {
## --------------------------------------------------------
#
## Author: Jose Ramirez Garcia
## Created on: 07/18/2008
## Last Modified on: 
## Last Modified by: 
## Description : It returns the purchase orders notes
## Forms Involved: sub build_track_link
## Parameters : 
#
#	if($in{'id_products'}){
#		my (@c) = split(/,/,$cfg{'srcolors'});
#		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_notes, sl_purchaseorders_items WHERE sl_purchaseorders_notes.ID_purchaseorders=sl_purchaseorders_items.ID_purchaseorders AND ID_products = '$in{'id_products'}'");
#		$va{'matches'} = $sth->fetchrow;
#		if ($va{'matches'}>0){
#			(!$in{'nh'}) and ($in{'nh'}=1);
#			my ($sth) = &Do_SQL("SELECT sl_purchaseorders_notes.ID_admin_users,sl_purchaseorders_notes.Date as mDate,sl_purchaseorders_notes.Time as mTime,FirstName,LastName,Type,Notes 
#													FROM sl_purchaseorders_notes,admin_users 
#													WHERE sl_purchaseorders_notes.ID_admin_users=admin_users.ID_admin_users 
#													AND sl_purchaseorders_notes.ID_purchaseorders IN 
#													(SELECT sl_purchaseorders_items.ID_purchaseorders FROM sl_purchaseorders_items INNER JOIN sl_purchaseorders ON sl_purchaseorders_items.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders AND ID_products = '$in{'id_products'}' AND sl_purchaseorders_items.Qty>sl_purchaseorders_items.Received ) 
#													ORDER BY ID_purchaseorders_notes DESC;");
#			while ($rec = $sth->fetchrow_hashref){
#				$d = 1 - $d;
#				$rec->{'Notes'} =~ s/\n/<br>/g;
#				$output_notes .= "<tr bgcolor='$c[$d]'>\n";
#				$output_notes .= "  <td class='smalltext' valign='top'>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
#				$output_notes .= "  <td class='smalltext' valign='top'>$rec->{'Type'}</td>\n";
#				$output_notes .= "  <td class='smalltext' valign='top'>$rec->{'Notes'}</td>\n";
#				$output_notes .= "</tr>\n";
#			}
#		}else{
#			$output_notes = qq|
#				<tr>
#					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
#				</tr>\n|;
#		}
#	} else {
#		$output_notes = qq|
#				<tr>
#					<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
#				</tr>\n|;
#	}
#	return $output_notes;
#}


#GV Inicia
#GV Inicia 06may2008
sub notificationsfinance{
#Acción: Creación
#Comentarios:
# --------------------------------------------------------
# Forms Involved: \cgi-bin\templates\en\forms\retwarehouse_view.html
# Created on: 06/may/2008 05:04PM GMT -0600
# Last Modified on: 
# Last Modified by:
# Author: MCC C. Gabriel Varela S.
# Description :  Hará las acciones que se seleccionen según el tipo de return para Notificaciones Finance
# Parameters :ID de orden
	$idorders=@_;
	return;
}

sub notificationsnoreship{
#Acción: Creación
#Comentarios:
# --------------------------------------------------------
# Forms Involved: \cgi-bin\templates\en\forms\retwarehouse_view.html
# Created on: 06/may/2008 05:06PM GMT -0600
# Last Modified on: 
# Last Modified by:
# Author: MCC C. Gabriel Varela S.
# Description :  Hará las acciones que se seleccionen según el tipo de return para Notificaciones No Re-Ship
# Parameters :ID de orden
	$idorders=@_;
	return;
}
#GV Termina 06may2008


sub mtycollection{
#-----------------------------------------
# Created on: 02/10/09  09:52:02 By  Roberto Barcenas
# Forms Involved: ajaxpayments.cgi, cybersubs.cgi
# Description : Check if the order was marked as MTY Collection
# Parameters : $id_orders

	my($id_orders)	= 	@_;
	
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_plogs INNER JOIN sl_orders_notes ON sl_orders_plogs.ID_orders=sl_orders_notes.ID_orders WHERE sl_orders_notes.ID_orders = '$id_orders' AND (Data like 'Order Moved to: Monterey:On Collection. Do not Charge%' OR Notes='Payments Disabled by Monterey Deal');");
	
	return $sth->fetchrow();
}


sub view_shows {
# --------------------------------------------------------
# Author : Carlos Haas
# Notes : Look for duplicates in other modules

	$va{'categoryname'} = &load_name('sl_categories','ID_categories',$in{'id_categories'},'Title');	
	(!$va{'categoryname'}) and ($va{'categoryname'}=&trans_txt('top_level'));
	$va{'shourtext'} = &shour_to_txt($in{'shour'});	
}




1;
