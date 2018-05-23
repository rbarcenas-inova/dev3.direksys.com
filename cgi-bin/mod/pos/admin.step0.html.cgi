#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 0 : CUSTOMER SEARCH
##################################################################
# Created on: 08/12/08 @ 11:12:30
# Author: Carlos Haas
# Last Modified on: 08/12/08 @ 11:12:30
# Last Modified by: Carlos Haas
# Description : 
# Parameters : 
#			   


##
## TO-DO: 
##		- Filtrar los productos basados en que se tenga inventario en el WH asociado al usuario
##		- Filtrar busqueda basada en el submit del search
##		- Permitir Hacer Link en el producto para ver la ficha tecnica
	&save_callsession('delete');
	my $data = loadDataPos();
	$id_warehousesPOS = $data->{'id_warehouse'};
	$id_customerPOS = &Do_SQL("select ID_customers from sl_customers where  CID= 'POS_$id_warehousesPOS'")->fetchrow();
	$va{'steptemp'} = 0;
	$sth = &Do_SQL("SELECT  
							COUNT(*)
							FROM sl_warehouses_location
							INNER JOIN sl_skus ON 
							(sl_warehouses_location.ID_products = sl_skus.ID_sku_products)
							INNER JOIN sl_parts ON 
							(sl_skus.ID_products = sl_parts.ID_parts)
							INNER JOIN sl_customers_parts ON
							(sl_parts.ID_parts = sl_customers_parts.ID_parts)
							WHERE 1
							AND sl_warehouses_location.ID_warehouses = '$id_warehousesPOS'
							AND sl_skus.Status = 'Active'
							AND sl_parts.Status = 'Active'
							AND sl_customers_parts.ID_customers = '$id_customerPOS'
							AND sl_warehouses_location.Quantity > 0");
	
	$va{'matches'} = $sth->fetchrow();
	if ($va{'matches'}>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		($va{'pageslist'},$in{'qs'}) = &pages_list($in{'nh'},"$cfg{'path_ns_cgi'}$cfg{'path_ns_cgi_admin'}", $va{'matches'}, $usr{'pref_maxh'});
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		my ($sth) = &Do_SQL("SELECT 
							sl_warehouses_location.ID_warehouses_location,
							sl_warehouses_location.ID_warehouses,
							sl_warehouses_location.ID_products,
							sl_warehouses_location.Location,
							sl_warehouses_location.Quantity,
							sl_skus.UPC,
							sl_parts.Model,
							sl_parts.Name,
							sl_customers_parts.ID_customers,
							sl_customers_parts.SPrice,
							sl_parts.Sale_Tax
							FROM sl_warehouses_location
							INNER JOIN sl_skus ON 
							(sl_warehouses_location.ID_products = sl_skus.ID_sku_products)
							INNER JOIN sl_parts ON 
							(sl_skus.ID_products = sl_parts.ID_parts)
							INNER JOIN sl_customers_parts ON
							(sl_parts.ID_parts = sl_customers_parts.ID_parts)
							WHERE 1
							AND sl_warehouses_location.ID_warehouses = '$id_warehousesPOS'
							AND sl_skus.Status = 'Active'
							AND sl_parts.Status = 'Active'
							AND sl_customers_parts.ID_customers = '$id_customerPOS'
							AND sl_warehouses_location.Quantity > 0
							ORDER BY sl_parts.Model
							LIMIT $first,$usr{'pref_maxh'};");

	
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			my $price = ($rec->{'SPrice'}) * (1 + ($rec->{'Sale_Tax'} / 100));
			$va{'searchresults'} .= "
			<tr id='hide_".$rec->{'ID_products'}."' style='display:none;'>
				<td class='smalltext' id='cant_$rec->{'ID_products'}'></td>
				<td class='smalltext' >".&format_sltvid($rec->{'ID_products'})."</td>
				<td class='smalltext' >$rec->{'Model'}<input type='hidden' id='model_$rec->{'ID_products'}' value='$rec->{'Model'}' /></td>
				<td class='smalltext' align='right' id='fullPrice_$rec->{'ID_products'}'></td>
			</tr>";
			$va{'searchresults'} .= "<tr onmouseover='m_over(this)' onmouseout='m_out(this)' bgcolor='$c[$d]' id='tr_".$rec->{'ID_products'}."'>\n";
			$va{'searchresults'} .= "   <td class='smalltext' nowrap><img src=/sitimages/pos/prod/".&format_sltvid($rec->{'ID_products'}).".jpg onError=this.onerror=null;this.src='/sitimages/pos/prod/none.jpg'; ></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'> $rec->{'Model'} / $rec->{'Name'} <br>ID: ".&format_sltvid($rec->{'ID_products'})." </td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' nowrap align='right'>".&format_price($price)." <input type='hidden' id='price_$rec->{'ID_products'}' value='$price' /> </td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' nowrap><input id='total_".$rec->{'ID_products'}."' type='text' onFocus='focusOn( this )' onBlur='focusOff( this )' size='1' autocomplete='off' style='height:23px;text-align:right;' class='inputchange'> 
			<img  width='20' src='/sitimages/pos/cart.png' alt='Add' title='Add' class='addSKU' id='sku_".$rec->{'ID_products'}."'></td>\n";
			$va{'searchresults'} .= "   <td style='font-size:10px;' >$rec->{'Quantity'}<input type='hidden' id='inv_$rec->{'ID_products'}' value='$rec->{'Quantity'}' ></td>\n";
			$va{'searchresults'} .= "</tr>\n";
		} 

	}else{
		$va{'searchresults'} = "		<tr>\n		    <td align='center' colspan='6'><p>&nbsp;</p>" . trans_txt('search_nomatches') . "<p>&nbsp;</p></td>\n		 </tr>\n";
		$va{'pageslist'} = 0;
		$va{'matches'}     = 0;
	}

1;