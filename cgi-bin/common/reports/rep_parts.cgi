#!/usr/bin/perl
##################################################################
#   REPORTS : PARTS
##################################################################

sub rep_parts_qty{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/16/09 13:49:11
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
# Last Modified RB: 03/18/09  16:18:59 -- Se agrego la impresion y la exportacion general y detallada a excel. Tambien se corrigio el shp_type=0 por shp_type=3
# Last Modified on: 03/19/09 12:42:10
# Last Modified by: MCC C. Gabriel Varela S: Se toma en cuenta $cfg{'codshptype'}
# Last Modified on: 05/19/09 13:56:15
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para mostrar el inventario por medio de ventana emergente y la diferencia seg?n corresponda.



	$va{'matches'} = 1;
	$va{'pageslist'} = 1;
	$in{'id_warehouses'} = int($in{'id_warehouses'});
	my ($q_status, $q_ptype,  $nopack);
	
	if ($in{'excludepack'}){
		$nopack = 1;
	}
	#######################################
	### Query & Menu Building
	#######################################
	if ($in{'type'} eq 'sku'){
		$va{'byproduct'} = 'font-weight: bold';
	}else{
		$in{'type'} = 'products';
		$va{'bysku'} = 'font-weight: bold';
	}
	if ($in{'status'} eq 'all'){
		$q_status = "'New','Processed'";
		$va{'byall'} = 'font-weight: bold';
	}else{
		$in{'status'} eq 'processed';
		$q_status = "'Processed'";
		$va{'byprocessed'} = 'font-weight: bold';
	}
	if ($in{'ptype'} eq 'Credit-Card'){
		$q_ptype = "Credit-Card";
		$va{'bycc'} = 'font-weight: bold';
	}else{
		$q_ptype = "COD";
		$in{'ptype'} = 'COD';
		$va{'bycod'} = 'font-weight: bold';
	}
	
	my $sth=&Do_SQL("SELECT COUNT(ID)
					FROM (SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'/',Model)AS PName,SUM(Quantity) AS Total
					FROM sl_orders
					INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
					INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
					WHERE (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00') 
					AND sl_orders.Status IN ($q_status) AND sl_orders_products.Status = 'Active'
					AND sl_orders_products.ID_products>1000000
					AND Ptype='$q_ptype'
					GROUP BY sl_orders_products.ID_products ORDER BY SUM(Quantity) DESC) as account");

						
	($va{'matches'}) = $sth->fetchrow;
	if ($va{'matches'}>0){
		
		$in{'export'}	=	int($in{'export'});
		if($in{'export'} and $in{'export'} eq '1'){
			print "Content-type: application/octet-stream\n";
			print "Content-disposition: attachment; filename=cod_prodqty_gral.csv\n\n";
			print  "SLTVID,Model/Name,Quantity,Inventory,Difference\r\n";
		}elsif($in{'export'}){
			&opr_cod_repsltvid if $in{'export'} > 1;
			return;
		}
		
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/admin",$va{'matches'},$usr{'pref_maxh'});
		my $page_limit;
		if ($in{'print'} or $in{'export'}){
			$page_limit = '';
		}else{
			$page_limit = " LIMIT $first,$usr{'pref_maxh'}";
		}		
		my (@c) = split(/,/,$cfg{'srcolors'});
		
		my $sth=&Do_SQL("SELECT sl_orders_products.ID_products AS ID, CONCAT(Name,'/',Model)AS PName,SUM(Quantity) AS Total
									FROM sl_orders
									INNER JOIN sl_orders_products ON sl_orders.ID_orders=sl_orders_products.ID_orders
									INNER JOIN sl_products ON sl_products.ID_products=RIGHT(sl_orders_products.ID_products,6)
									WHERE (ISNULL(ShpDate) OR ShpDate='' OR ShpDate='0000-00-00') 
									AND sl_orders.Status in ($q_status) AND sl_orders_products.Status = 'Active'
									AND sl_orders_products.ID_products>1000000
									AND Ptype='$q_ptype'
									GROUP BY sl_orders_products.ID_products ORDER BY SUM(Quantity) DESC $page_limit");
	
		$va{'searchresults'}="";
		while(my $rec=$sth->fetchrow_hashref){
			
			my ($stin) = &Do_SQL("SELECT IF(SUM(Quantity) > 0,SUM(Quantity),0) FROM sl_warehouses_location WHERE ID_warehouses = 1003 AND  ID_products = '$rec->{'ID'}'");
			my ($inventory) = $stin->fetchrow();
			
			
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid($rec->{'ID'})."</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top'>$rec->{'PName'}</td>";
			$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>$rec->{'Total'}</td>\n";
			if ($rec->{'ID'} >400000000 and $rec->{'ID'}<500000000){
				my ($html_link,$inv)=&inventory_by_id($rec->{'ID'},$in{'id_warehouses'},$nopack);
				$cadinv=&inventory_by_id($rec->{'ID'});
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' nowrap>$html_link</td>\n";
				if ($inv-$rec->{'Total'}<0){
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right' style='Color:Red'>".&format_number($inv-$rec->{'Total'})."</td>\n";
				}else{
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($inv-$rec->{'Total'})." <a href='$script_url?cmd=$in{'cmd'}&export=$rec->{'ID'}' title='Export this Orders'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_xls.gif' title='Export |.format_sltvid($rec->{'ID'}).qq| Info' alt='' border='0'></a></td>\n";
				}
				if($in{'export'}){
					$rec->{'PName'}	=~	s/,/ /g;
					print &format_sltvid($rec->{'ID'}).",$rec->{'PName'},$rec->{'Total'},".($inv-$rec->{'Total'}).",".($inv-$rec->{'Total'})."\r\n";
				}
			}else{
				$va{'searchresults'} .= "  <td class='smalltext' valign='top' colspan='2'></td>\n";
				if($in{'export'}){
					$rec->{'PName'}	=~	s/,/ /g;
					print &format_sltvid($rec->{'ID'}).",$rec->{'PName'},$rec->{'Total'},---,---\r\n";
				}
			}
			$va{'searchresults'} .= "</tr>\n";

			
			if ($rec->{'ID'}<400000000){
				my $sth2=&Do_SQL("SELECT * FROM sl_skus_parts 
						LEFT JOIN sl_parts ON sl_skus_parts.ID_parts=sl_parts.ID_parts
						WHERE ID_sku_products=$rec->{'ID'}");
				while(my $sku=$sth2->fetchrow_hashref){
					$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' >\n";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'></td>";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top'>".&format_sltvid(400000000+$sku->{'ID_parts'})." &nbsp; : &nbsp; $sku->{'Name'}</td>";
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($sku->{'Qty'}*$rec->{'Total'})."</td>\n";
					my($html_link,$inv)=&inventory_by_id(400000000+$sku->{'ID_parts'},$in{'id_warehouses'},$nopack);
					$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right' nowrap>".$html_link."</td>\n";
					if ($inv-$sku->{'Qty'}*$rec->{'Total'}<0){
						$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right' style='Color:Red'>".&format_number($inv-$sku->{'Qty'}*$rec->{'Total'})."</td>\n";
					}else{
						$va{'searchresults'} .= "  <td class='smalltext' valign='top' align='right'>".&format_number($inv-$sku->{'Qty'}*$rec->{'Total'})."</td>\n";
					}
					if($in{'export'}){
						$sku->{'Name'}	=~	s/,/ /g;
						print "---,".&format_sltvid(400000000+$sku->{'ID_parts'})." $sku->{'Name'},".($sku->{'Qty'}*$rec->{'Total'}).",".($inv).",".($inv-$sku->{'Qty'}*$rec->{'Total'})."\r\n";
					}
				}
			}
			
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
		<tr>
			<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
		</tr>\n|;
	}
	

	if ($in{'print'}){
		print "Content-type: text/html\n\n";
		print &build_page('header_print.html');
		print &build_page('rep_parts_qty_print.html');
	}elsif(!$in{'export'}){
		print "Content-type: text/html\n\n";
		print &build_page('rep_parts_qty.html');
	}

}



1;