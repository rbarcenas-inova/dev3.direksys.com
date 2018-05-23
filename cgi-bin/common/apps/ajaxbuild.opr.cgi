sub moreinfotrackinglink{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 08/21/2008
# Last Modified on: 
# Last Modified by: 
# Description : It shows more info when there's no trackilng link
# Forms Involved: sub build_tracking_link
# Parameters : 

	my ($linkpo); 
	 
	$in{'urlscr'} =~ /\/(cgi-bin)\/(.+)\/(.+)/;
	$linkpo = "";

	if($in{'id_moreinfo'}){
		my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_products='$in{'id_moreinfo'}';");
		$va{'mi_stock'}=$sth->fetchrow;
		if(!$va{'mi_stock'}){
			$va{'mi_stock'} = "No Stock";
		}
		my (@c) = split(/,/,$cfg{'srcolors'});
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_purchaseorders_items WHERE ID_products = '$in{'id_moreinfo'}'");
		$va{'matches'} = $sth->fetchrow;
		if ($va{'matches'}>0){
			(!$in{'nh'}) and ($in{'nh'}=1);
			my ($sth) = &Do_SQL("SELECT sl_purchaseorders.ID_purchaseorders,Name, sl_purchaseorders.Status,Qty,Price,sl_purchaseorders_items.Date, Etd 
													FROM sl_purchaseorders_items INNER JOIN sl_purchaseorders 
													ON sl_purchaseorders_items.ID_purchaseorders = sl_purchaseorders.ID_purchaseorders
													AND ID_products = '$in{'id_moreinfo'}' AND sl_purchaseorders_items.Qty>sl_purchaseorders_items.Received 
													INNER JOIN sl_warehouses ON sl_purchaseorders.ID_warehouses = sl_warehouses.ID_warehouses
													ORDER BY sl_purchaseorders_items.Date DESC;");
			while ($rec = $sth->fetchrow_hashref){
				$d = 1 - $d;
				($2 eq 'administration') and ($linkpo = qq|onClick="trjump('dbman?cmd=mer_po&view=$rec->{'ID_purchaseorders'}#tabs')"|);	
				$output_po .= qq|<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)' $linkpo >\n|;
				$output_po .= "   <td class='smalltext'>$rec->{'ID_purchaseorders'}</td>\n";
				$output_po .= "   <td class='smalltext'>$rec->{'Qty'}</td>\n";
				$output_po .= "   <td class='smalltext'>$rec->{'Etd'}</td>\n";
				$output_po .= "</tr>\n";
			}
		}
	}
	if(!$output_po){
		$output_po = qq|
			<tr>
				<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	print "Content-type: text/html\n\n";
	print qq|
	<div class="smalltext" align='center'>
		<table border="0" cellspacing="0" cellpadding="4" width="300" class="formtable">
			<tr>
				<td colspan="3" class='smalltext'>Actual Inventory : $va{'mi_stock'}</td>
			</tr>		
			<tr>
				<td class="menu_bar_title">PO ID</td>
				<td class="menu_bar_title">Quantity</td>
				<td class="menu_bar_title">ETD</td>
			</tr>
			$output_po
		</table>	
	</div>
	|;
	
}


#############################################################################
#############################################################################
#   Function: adjustments_edit
#				
#       Es: Maneja  add/drop para adjustments items
#       En: 
#
#
#    Created on: 03/25/2013  19:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		- id_adjustments = id from table
#		- type = load_data | add | drop
#       - id_warehouses = ID Warehouse
#       - keyword = search word
#		- data_in = idwl:qty
#		
#  Returns:
#
#      - Error/datasource/table with data
#
#   See Also:
#
#	<view_opr_adjustments>
#
sub adjustments_edit {
#############################################################################
#############################################################################

	my ($id_adjustments) = int($in{'id'});
	my ($type) = &filter_values($in{'type'});
	my ($id_warehouses) = int($in{'id_warehouses'});
	my ($keyword) = &filter_values($in{'keyword'});
	my ($idai) = int($in{'idai'});
	my ($data_in) = &filter_values($in{'data_in'});


	if($type eq 'load_data'){

		print "Content-type:  application/json\n\n";
		
		my ($str,$ids);
		my $mod = $keyword ne '' ? " AND (Name LIKE '%$keyword%' OR Model LIKE '%$keyword%' OR ID_parts LIKE '%$keyword%') " : '';
		
		## 1. Parts with Qty
		my ($sth) =  &Do_SQL("SELECT ID_products, Name, IF(Location IS NULL,'Location',Location), IF(SUM(Quantity) IS NULL,0,SUM(Quantity))
	                    FROM sl_parts INNER JOIN sl_warehouses_location ON 
	                    ID_parts = RIGHT(ID_products,4) 
	                    WHERE ID_warehouses = '$id_warehouses' $mod
	                    GROUP BY ID_parts,Location ORDER BY Name,Location,SUM(Quantity) DESC;");

		while(my($id_parts, $name, $location, $qty) = $sth->fetchrow()){
			$ids .="$id_parts|";
			$str .= '{"id":"'.$id_parts.'","name":"'.$name.'","location":"'.$location.'","qty":"'.$qty.'"},';
		}

		# 2. Parts No Qty
		my ($sth) =  &Do_SQL("SELECT 400000000 + ID_parts, Name, 'Location',0
	                    FROM sl_parts WHERE 1 $mod ORDER BY Name");
		while(my($id_parts, $name, $location, $qty) = $sth->fetchrow()){
			$str .= '{"id":"'.$id_parts.'","name":"'.$name.'","location":"'.$location.'","qty":"'.$qty.'"},' if $ids !~ /$id_parts/;
			$ids .="$id_parts|";
		}
		chop($str);
		$str = '{"skus":['.$str.']}';
		print $str;
	
	}elsif($type =~ /add|drop/) {

		print "Content-type: text/html\n\n";

		if($type eq 'add' and (!$id_warehouses or !$id_adjustments or !$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif($type eq 'drop' and !$idai){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my $str,$str_out,$t;

		if($type eq 'add') {

			my ($id_products, $location , $qty) = split(/:/, $data_in);
			$location = &load_name('sl_locations','ID_warehouses',$id_warehouses,'Code') if lc($location) eq 'location';
			my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_adjustments_items SET ID_adjustments = '$id_adjustments', ID_products = '".int($id_products)."', ID_warehouses = '$id_warehouses',
					Location = '".&filter_values($location)."', Qty = '".int($qty)."', Adj=0, Price=0, Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			$t = $sth->rows();

		}elsif($type eq 'drop'){	
			my ($sth) = &Do_SQL("DELETE FROM sl_adjustments_items WHERE ID_adjustments_items = '$idai';");
			$t = $sth->rows();
		}

		if(!$t) {
			print "Error: Duplicated Record" if $type eq 'add';
			print "Error: Record Not Dropped" if $type eq 'drop';
			return;
		}

		my ($sth) =  &Do_SQL("SELECT ID_adjustments_items, ID_products, sl_warehouses.Name, 
						sl_warehouses.ID_warehouses, sl_parts.Name, Location,Qty
	                    FROM sl_parts INNER JOIN sl_adjustments_items 
	                    ON ID_parts = RIGHT(ID_products,4) 
	                    INNER JOIN sl_warehouses USING(ID_warehouses)
	                    WHERE ID_adjustments = '$id_adjustments'
	                    ORDER BY ID_adjustments_items;");
		while(my($idai, $id_parts, $whname, $id_warehouses, $name, $location, $qty) = $sth->fetchrow()){

			$str_out .= qq|<tr id="row-$idai">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$idai" style="cursor:pointer" title="Drop $id_parts"></td>\n
								<td>|.&format_sltvid($id_parts).qq|</td>\n
								<td>$name</td>\n 
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$id_warehouses" title="View $id_warehouses">($id_warehouses) $whname</a></td>\n 
								<td align="center">$location</td>\n 
								<td  align="right">$qty</td>\n 
							</tr>|;	
		}

		if($str_out) {
			$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">ID</td>\n 
								<td align="center" class="menu_bar_title">Name</td>\n 
								<td align="center" class="menu_bar_title">Warehouse</td>\n 
								<td align="center" class="menu_bar_title">Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n 
							</tr>\n
							$str_out
						</table>\n|;
			print $str_out;				
		}

	}	
	

	return;
}


#############################################################################
#############################################################################
#   Function: manifests_edit
#				
#       Es: Maneja  add/drop para transfer items
#       En: 
#
#
#    Created on: 03/25/2013  19:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		- id_manifests = id from table
#		- type = load_data | add | drop
#       - id_warehouses = ID Warehouse
#       - keyword = search word
#		- data_in = idwl:qty
#		
#  Returns:
#
#      - Error/datasource/table with data
#
#   See Also:
#
#	<view_opr_adjustments>
#
sub manifests_edit {
#############################################################################
#############################################################################

	my ($id_manifests) = int($in{'id'});
	my ($type) = &filter_values($in{'type'});
	my ($id_warehouses) = int($in{'id_warehouses'});
	my ($keyword) = &filter_values($in{'keyword'});
	my ($idmi) = int($in{'idmi'});
	my ($data_in) = &filter_values($in{'data_in'});
	my ($des_sku_qty) = &filter_values($in{'des_sku_qty'});
	my $qty_completed = 0;
	my $remaining_qty = 0;

	if ($type eq 'list_skus_qty') {
		print "Content-type: text/html\n\n";
		
		my ($str,$ids);
		my $cntr = 0;
		my $mod = $keyword ne '' ? " AND (ID_products = '$keyword') " : '';
		
		my ($sth_total) =  &Do_SQL("SELECT ID_products, Name, IF(Location IS NULL,'Location',Location), IF(SUM(Quantity) IS NULL,0,SUM(Quantity))
	                    FROM sl_parts INNER JOIN sl_warehouses_location ON 
	                    ID_parts = RIGHT(ID_products,4) 
	                    WHERE ID_warehouses = '$id_warehouses' $mod
	                    GROUP BY ID_parts ORDER BY SUM(Quantity) DESC;");
		my $total_qty = $sth_total->fetchrow();
		if (!$des_sku_qty) {
			print qq|	<span class="smallfieldterr">The desired quantity must be greater than 0.</span>|;
			return;
		} elsif ($des_sku_qty > $total_qty) {
			print qq|	<span class="smallfieldterr">The desired quantity is greater than the available.</span>
						<br/>
						<span class="smallfieldterr">Total available: $total_qty</span>|;
			return;
		} elsif (!$total_qty) {
			print qq|	<span class="smallfieldterr">No records found.</span>|;
			return;
		} else {
			## 1. Parts with Qty
			my ($sth) =  &Do_SQL("SELECT ID_products, Name, IF(Location IS NULL,'Location',Location), IF(SUM(Quantity) IS NULL,0,SUM(Quantity))
							FROM sl_parts INNER JOIN sl_warehouses_location ON 
							ID_parts = RIGHT(ID_products,4) 
							WHERE ID_warehouses = '$id_warehouses' $mod
							GROUP BY ID_parts,Location ORDER BY SUM(Quantity) DESC;");
			$str = qq|<table>|;
			$str .= qq|	<tr>
							<td align="center" class="menu_bar_title">Item ID</td>
							<td align="center" class="menu_bar_title">Name</td>
							<td align="center" class="menu_bar_title">Location</td>
							<td align="center" class="menu_bar_title">Qty</td>
							<td align="center" class="menu_bar_title">Qty to take</td>
						</tr>|;
			while(my($id_parts, $name, $location, $qty) = $sth->fetchrow()) {
				++$cntr;
				my $qty_aux = '';
				if ($total_qty >= $des_sku_qty) {
					if ($des_sku_qty <= $qty and !$qty_completed) {
						$qty_aux = $des_sku_qty;
						$qty_completed = 1;
					} elsif(!$qty_completed) {
						$remaining_qty = $des_sku_qty - $qty;
						
						$des_sku_qty = $remaining_qty;
						
						$qty_aux = $qty;
					}	
				}
				$str .= qq|
						<tr>
							<td>$id_parts</td>
							<td>$name</td>
							<td>$location</td>
							<td>$qty</td>
							<td>
								&nbsp; X &nbsp;
								<input type="text" disabled="disabled" name="from_sku_qty_|.$cntr.qq|" id="from_sku_qty_|.$cntr.qq|" value="$qty_aux" size="6" />
								<input type="hidden" name="from_sku_location_|.$cntr.qq|" id="from_sku_location_|.$cntr.qq|" value="$location" />
							</td>
						</tr>
						|;
				$qty_aux = '' if($qty_completed);
			}
			$str .= qq|</table>|;
			chop($str);
			
			print $str;
		}
	}
	
	if($type eq 'load_sku_data'){

		print "Content-type:  application/json\n\n";
		
		my ($str,$ids);
		my $mod = $keyword ne '' ? " AND (sl_parts.Name LIKE '%$keyword%' OR sl_parts.Model LIKE '%$keyword%' OR (sl_parts.ID_parts + 400000000) LIKE '%$keyword%') " : '';
		
		## 1. Parts with Qty
		my ($sth) =  &Do_SQL("SELECT (sl_parts.ID_parts + 400000000) as ID_prods, sl_skus.UPC, sl_parts.Model, sl_parts.Name
	                    FROM sl_parts
						INNER JOIN sl_skus ON (sl_parts.ID_parts = sl_skus.ID_products)
	                    WHERE sl_parts.Status = 'Active' $mod
	                    ORDER BY sl_skus.ID_products DESC;");

		while(my($id_parts, $upc, $model, $name) = $sth->fetchrow()){
			$ids .="$id_parts|";
			$str .= '{"id_parts":"'.$id_parts.'","upc":"'.$upc.'","model":"'.$model.'","name":"'.$name.'"},';
		}
		chop($str);
		$str = '{"skus":['.$str.']}';
		print $str;
	
	}
	
	if($type =~ /skus_add|skus_drop/) {

		print "Content-type: text/html\n\n";
		
		if($type eq 'skus_add' and (!$id_warehouses or !$id_manifests or !$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif($type eq 'skus_drop' and !$idmi){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my ($str,$str_out,$t);
		$str_out = '';
		if($type eq 'skus_add') {
			
			my ($id_products, $location , $to_warehouses, $to_location, $qty, $to_sku) = split(/:/, $data_in);

			## Location Exists?
			my ($sth) = &Do_SQL("SELECT ID_locations FROM sl_locations WHERE ID_warehouses = '$to_warehouses' AND Code = '$to_location';");
			my ($idl) = $sth->fetchrow();

			if(!$idl) {
				print "Error: Location Unknown";
				return;
			}

			my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_warehouses = '$id_warehouses' AND ID_products = '$id_products' AND Location = '$location' ORDER BY Date LIMIT 1;");
			my ($this_qty) = $sth->fetchrow();

			if(!$this_qty or $this_qty < $qty) {
				print "Error: Stock Limitation $this_qty < $qty";
				return;
			}
			
			my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_skustransfers_items SET ID_skustransfers = '$id_manifests', FromSku = '".int($id_products)."', From_Warehouse = '$id_warehouses', From_Warehouse_Location = '$location',
					To_Warehouse = '$to_warehouses', To_Warehouse_Location = '$to_location', ToSku='$to_sku', Qty = '".int($qty)."', Status = 'New', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			$t = $sth->rows();

		}elsif($type eq 'skus_drop'){
			my ($sth) = &Do_SQL("DELETE FROM sl_skustransfers_items WHERE ID_skustransfers_items = '$idmi';");
			$t = $sth->rows();
		}

		if(!$t) {
			print "Error: Duplicated Record" if $type eq 'skus_add';
			print "Error: Record Not Dropped" if $type eq 'drop';
			return;
		}

		my ($sth) =  &Do_SQL("SELECT ID_skustransfers_items, FromSku, ToSku, sl_parts.Name, From_warehouse, From_warehouse_Location,To_warehouse, To_warehouse_Location,Qty
						,(SELECT Name FROM sl_parts WHERE ID_parts = RIGHT(sl_skustransfers_items.ToSku,4)) as to_name
	                    FROM sl_parts
						INNER JOIN sl_skustransfers_items ON ID_parts = RIGHT(FromSku,4)
	                    WHERE ID_skustransfers = '$id_manifests'
	                    ORDER BY ID_skustransfers_items;");
		while(my($idmi, $id_parts, $to_id_parts, $name, $fwh, $from_location, $twh, $to_location, $qty, $to_name) = $sth->fetchrow()) {

			my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $fwh, 'Name');
			my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $twh, 'Name');

			$str_out .= qq|<tr id="row-$idai">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$idmi" style="cursor:pointer" title="Drop $id_parts"></td>\n
								<td>|.&format_sltvid($id_parts).qq|</td>\n
								<td>$name</td>\n
								<td>|.&format_sltvid($to_id_parts).qq|</td>\n
								<td>$to_name</td>\n 
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$fwh" title="View $fwh">($fwh) $fwhname / $from_location</a></td>\n 
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$twh" title="View $twh">($twh) $twhname / $to_location</a></td>\n
								<td  align="right">$qty</td>\n 
							</tr>|;	
		}

		if($str_out) {
			$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">From ID</td>\n
								<td align="center" class="menu_bar_title">From Name</td>\n
								<td align="center" class="menu_bar_title">To ID</td>\n 
								<td align="center" class="menu_bar_title">To Name</td>\n 
								<td align="center" class="menu_bar_title">From Warehouse / Location</td>\n 
								<td align="center" class="menu_bar_title">To Warehouse / Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n 
							</tr>\n
							$str_out
						</table>\n|;
			print $str_out;				
		}
	}
	
	if($type eq 'load_data_from'){

		print "Content-type:  application/json\n\n";
		
		my ($str,$ids);
		my $mod = $keyword ne '' ? " AND (sl_parts.Name LIKE '%$keyword%' OR sl_parts.Model LIKE '%$keyword%' OR sl_parts.ID_parts LIKE '%$keyword%') " : '';
		
		## 1. Parts with Qty
		my ($sth) =  &Do_SQL("SELECT 
								sl_warehouses_location.ID_products
								, sl_skus.UPC
								, sl_parts.Name
								, sl_warehouses_location.Location
								, sl_warehouses_location.Quantity
		                    FROM 
		                    	sl_parts 
								INNER JOIN( 
									SELECT ID_warehouses, ID_products, Location, SUM(Quantity) AS Quantity
									FROM sl_warehouses_location
									WHERE sl_warehouses_location.ID_warehouses = $id_warehouses
									GROUP BY ID_products, Location		
								) AS sl_warehouses_location ON ID_parts = RIGHT(ID_products,4)
								INNER JOIN sl_locations ON Location = Code AND sl_locations.ID_warehouses=sl_warehouses_location.ID_warehouses
								INNER JOIN sl_skus ON  ID_parts = sl_skus.ID_products
		                    WHERE 
		                    	sl_skus.status = 'Active' 
		                    	AND sl_warehouses_location.ID_warehouses = $id_warehouses 
		                    	$mod
		                    	AND sl_locations.Status = 'Active'
		                    	AND sl_locations.Locked='Inactive'
		                    GROUP BY 
		                    	sl_parts.ID_parts
		                    	, sl_warehouses_location.Location 
							ORDER BY 
								sl_parts.Name
								, sl_warehouses_location.Location
								, SUM(sl_warehouses_location.Quantity) DESC;");
		
		while(my($id_parts, $str_upc, $name, $location, $qty) = $sth->fetchrow()){
			$name =~ s/"|'//g;
			$ids .="$id_parts|";
			#$str .= '{"id":"'.$id_parts.'","name":"'.$name.'","location":"'.$location.'","qty":"'.$qty.'"},';
			$str .= '{"id":"'.$id_parts.'","upc":"'.$str_upc.'","name":"'.$name.'","location":"'.$location.'","qty":"'.$qty.'"},';
		}
		chop($str);
		$str = '{"skus":['.$str.']}';
		print $str;
	
	}elsif($type eq 'load_data_to'){
	
		print "Content-type:  application/json\n\n";
		
		my ($str);
		my $mod = $keyword ne '' ? " AND Code LIKE '%$keyword%' " : '';
		
		## 1. Parts with Qty
		my ($sth) =  &Do_SQL("SELECT 
								Code 
							FROM 
								sl_locations 
							WHERE 
								ID_warehouses = '$id_warehouses' 
								$mod 
								AND Status = 'Active' AND Locked='Inactive'
							ORDER BY 
								Code;");
		while(my($location) = $sth->fetchrow()){
			$str .= '{"name":"'.$location.'"},';
		}
		chop($str);
		$str = '{"locations":['.$str.']}';
		print $str;

	}elsif($type =~ /add|drop/) {

		print "Content-type: text/html\n\n";

		if($type eq 'add' and (!$id_warehouses or !$id_manifests or !$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif($type eq 'drop' and !$idmi){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my $str,$str_out,$t;

		if($type eq 'add') {

			my ($id_products, $location , $to_warehouses, $to_location, $qty) = split(/:/, $data_in);

			## Location Exists?
			my ($sth) = &Do_SQL("SELECT ID_locations, Status FROM sl_locations WHERE ID_warehouses = '$to_warehouses' AND Code = '$to_location';");
			my ($idl, $stl) = $sth->fetchrow();

			if(!$idl) {
				print "Error: Location Unknown";
				return;
			}

			if($stl ne 'Active') {
				print "Error: Location Not Active";
				return;
			}			

			my ($sth) = &Do_SQL("SELECT SUM(Quantity) FROM sl_warehouses_location WHERE ID_warehouses = '$id_warehouses' AND ID_products = '$id_products' AND Location = '$location' ORDER BY Date LIMIT 1;");
			my ($this_qty) = $sth->fetchrow();

			if(!$this_qty or $this_qty < $qty) {
				print "Error: Stock Limitation $this_qty < $qty";
				return;
			}
			
			my ($sth) = &Do_SQL("INSERT IGNORE INTO sl_manifests_items SET ID_manifests = '$id_manifests', ID_products = '".int($id_products)."', From_Warehouse = '$id_warehouses', From_Warehouse_Location = '$location',
					To_Warehouse = '$to_warehouses', To_Warehouse_Location = '$to_location', Qty = '".int($qty)."', Status = 'New', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
			$t = $sth->rows();

		}elsif($type eq 'drop'){	
			my ($sth) = &Do_SQL("DELETE FROM sl_manifests_items WHERE ID_manifests_items = '$idmi';");
			$t = $sth->rows();
		}

		if(!$t) {
			print "Error: Duplicated Record" if $type eq 'add';
			print "Error: Record Not Dropped" if $type eq 'drop';
			return;
		}

		my ($sth) =  &Do_SQL("SELECT ID_manifests_items, ID_products, sl_parts.Name, From_warehouse, From_warehouse_Location,To_warehouse, To_warehouse_Location,Qty
	                    FROM sl_parts INNER JOIN sl_manifests_items 
	                    ON ID_parts = RIGHT(ID_products,4) 
	                    WHERE ID_manifests = '$id_manifests'
	                    ORDER BY ID_manifests_items;");
		while(my($idmi, $id_parts, $name, $fwh, $from_location, $twh, $to_location, $qty) = $sth->fetchrow()){

			my $fwhname = &load_name('sl_warehouses', 'ID_warehouses', $fwh, 'Name');
			my $twhname = &load_name('sl_warehouses', 'ID_warehouses', $twh, 'Name');

			$str_out .= qq|<tr id="row-$idai">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$idmi" style="cursor:pointer" title="Drop $id_parts"></td>\n
								<td>|.&format_sltvid($id_parts).qq|</td>\n
								<td>$name</td>\n 
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$fwh" title="View $fwh">($fwh) $fwhname / $from_location</a></td>\n 
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouses&view=$twh" title="View $twh">($twh) $twhname / $to_location</a></td>\n
								<td  align="right">$qty</td>\n 
							</tr>|;	
		}

		if($str_out) {
			$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">ID</td>\n 
								<td align="center" class="menu_bar_title">Name</td>\n 
								<td align="center" class="menu_bar_title">From Warehouse / Location</td>\n 
								<td align="center" class="menu_bar_title">To Warehouse / Location</td>\n 
								<td align="center" class="menu_bar_title">Quantity</td>\n 
							</tr>\n
							$str_out
						</table>\n|;
			print $str_out;				
		}

	}	
	

	return;
}


sub edit_products {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	#if ($usr{'usergroup'} eq 1){
	if(&check_permissions('opr_orders_products','_edit','')){
		$va{'script_url'} = $in{'script_url'};
		$va{'hiddenfields'} = qq|
		<input type="hidden" name="cmd" value="[in_cmd]">
		<input type="hidden" name="tab" value="1">
		<input type="hidden" name="view" value="[in_id_orders]">
		<input type="hidden" name="updateprodinfo" value="1">
		<input type="hidden" name="id_orders_products" value="[in_id_orders_products]">\n|;
	
		&load_cfg('sl_orders_products');
		$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};	
		$db_select_fields{'ajaxshpprovider'} = $db_select_fields{'shpprovider'};
		$db_select_fields{'ajaxupsell'} = $db_select_fields{'upsell'};	
		@headerfields = (@db_cols[6..8],$db_cols[17],$db_cols[14],$db_cols[15],$db_cols[13],$db_cols[18]);
		@titlefields  = (@db_cols[6..8],$db_cols[17],$db_cols[14],$db_cols[15],$db_cols[13],$db_cols[18]);
		$va{'searchform'} = &html_record_form (&get_record('ID_orders_products',$in{'id_orders_products'},'sl_orders_products'));
	}else{
		$va{'script_url'} = $in{'script_url'};
		$va{'hiddenfields'} = qq|
		<input type="hidden" name="cmd" value="[in_cmd]">
		<input type="hidden" name="tab" value="1">
		<input type="hidden" name="view" value="[in_id_orders]">
		<input type="hidden" name="updateprodinfo" value="1">
		<input type="hidden" name="id_orders_products" value="[in_id_orders_products]">\n|;
	
		&load_cfg('sl_orders_products');
		$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};	
		#$db_select_fields{'ajaxshpprovider'} = $db_select_fields{'shpprovider'};	
		@headerfields = (@db_cols[6..7],$db_cols[18]);
		@titlefields = (@db_cols[6..7],$db_cols[18]);
		$va{'searchform'} = &html_record_form (&get_record('ID_orders_products',$in{'id_orders_products'},'sl_orders_products'));
		
	}
	print &build_page('forms:general_form.html');
}

sub split_products_qty {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	#if ($usr{'usergroup'} eq 1){
	if(&check_permissions('opr_orders_products','_edit','')){
		$va{'script_url'} = $in{'script_url'};
		$va{'hiddenfields'} = qq|
		<input type="hidden" name="cmd" value="[in_cmd]">
		<input type="hidden" name="tab" value="1">
		<input type="hidden" name="view" value="[in_id_orders]">
		<input type="hidden" name="split_qty" value="1">
		<input type="hidden" name="current_qty" value="[in_current_qty]" />
		<input type="hidden" name="aux_date" value="[in_date]" />
		<input type="hidden" name="aux_time" value="[in_time]" />
		<input type="hidden" name="id_orders_products" value="[in_id_orders_products]">\n|;
		
	
		#&load_cfg('sl_orders_products');
		#$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};	
		#$db_select_fields{'ajaxshpprovider'} = $db_select_fields{'shpprovider'};
		#$db_select_fields{'ajaxupsell'} = $db_select_fields{'upsell'};	
		#@headerfields = (@db_cols[6..8],$db_cols[17],$db_cols[14],$db_cols[15],$db_cols[13],$db_cols[18]);
		#@titlefields  = (@db_cols[6..8],$db_cols[17],$db_cols[14],$db_cols[15],$db_cols[13],$db_cols[18]);
		#$va{'searchform'} = &html_record_form (&get_record('ID_orders_products',$in{'id_orders_products'},'sl_orders_products'));
		$va{'searchform'} = qq|
		<tr>
			<td>&nbsp;</td>
			<td valign="top" nowrap="">Quantity : </td>
			<td>
				<input type="text" onblur="focusOff( this )" onfocus="focusOn( this )" size="25" value="" name="ajaxquantity">
			</td>
		</tr>|;
	}else{
		
		
	}
	print &build_page('forms:general_form.html');
}

sub edit_payments {
#-----------------------------------------
# Created on: 07/28/09  12:41:19 By  Roberto Barcenas
# Forms Involved: 
# Description : Edita los Payments en Modo Clean Up desde el tab de Payments
# Parameters : 
# Notes: Para que existe la variable $in{'format'}, que determina?


	print "Content-type: text/html\n\n";
	$va{'script_url'} = $in{'script_url'};
	$va{'hiddenfields'} = qq|
	<input type="hidden" name="cmd" value="[in_cmd]">
	<input type="hidden" name="tab" value="2">
	<input type="hidden" name="view" value="[in_id_orders]">
	<input type="hidden" name="ida_banks" value="[in_ida_banks]">
	<input type="hidden" name="updatepayinfo" value="1">
	<input type="hidden" name="id_orders_payments" value="[in_id_orders_payments]">\n|;

	&load_cfg('sl_orders_payments');
	my (%rec) = &get_record('ID_orders_payments',$in{'id_orders_payments'},'sl_orders_payments');

	if(&check_permissions('opr_orders_payments','_edit','')){

		if ($in{'format'}) {

			if ($in{'format'} == 2) {
				
				########################################
				########################################
				########################################
				######
				###### From Tab2 Payments - Pencil
				######
				########################################
				########################################
				########################################
				#if ($rec{'type'} eq 'Credit-Card'){
					 
					$db_select_fields{'ajaxcaptured'} = $db_select_fields{'captured'};
					$db_valid_types{'captured'}='radio';
					
					@headerfields = (@db_cols[19..20],$db_cols[17]);
					@titlefields = ('Captured','CapDate','AuthCode');
					@remfields = ('PmtField1','PmtField2','PmtField3','PmtField4','PmtField5','PmtField6','PmtField7','PmtField8','PmtField9','Amount','Reason','Paymentdate','Status');
										
				#} else {

				#	$db_valid_types{'pmtfield7'}='selection';
				#	$db_select_fields{'ajaxpmtfield7'} = join(',',&load_enum_toarray('sl_orders','State'));
				#	$db_valid_types{'pmtfield8'}='radio';
				#	$db_select_fields{'ajaxpmtfield8'} = 'P,C';
				#	$db_valid_types{'captured'}='radio';
				#	$db_valid_types{'reason'} = 'selection';
				#	$db_select_fields{'ajaxreason'}= 'Sale,Exchange,Reship,Other';
									
				#	$db_select_fields{'ajaxcaptured'} = $db_select_fields{'captured'};
				#	$db_select_fields{'ajaxstatusy'} = $db_select_fields{'status'};
				#	@headerfields = (@db_cols[3..14],@db_cols[16..18],@db_cols[20]);
				#	@titlefields =  ('Name in check','Routing (ABA) #','Account #','Cheque #','Birth Date','Licencia','State Lic','Check Type','Lic Number','Amount','Reason','Pay Date','AuthCode','Captured','CapDate','Status');;
				#}

				$va{'searchform'} = &html_record_form_hidden_fields (%rec);
				print &build_page('forms:general_form.html');
				return;

			}

		} else {

			if ($rec{'type'} eq 'Credit-Card'){

				$db_valid_types{'pmtfield1'}='selection';
				$db_select_fields{'ajaxpmtfield1'}= 'Visa,Mastercard,American Express,Discover';
				$db_valid_types{'reason'} = 'selection';
				$db_select_fields{'ajaxreason'}= 'Sale,Exchange,Reship,Other';
				$db_valid_types{'captured'}='radio';
				$db_select_fields{'ajaxcaptured'} = $db_select_fields{'captured'};
				$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};		
				@headerfields = (@db_cols[3..8],@db_cols[12..15],@db_cols[17..18],$db_cols[20]);
				@titlefields = ('Card Type','Name in card','Card #','Expiration','CVN','Phone','Amount','Reason','Payment Date','AuthCode','Captured','CapDate','Status');
			}else{
				$db_valid_types{'pmtfield7'}='selection';
				$db_select_fields{'ajaxpmtfield7'} = join(',',&load_enum_toarray('sl_orders','State'));
				$db_valid_types{'pmtfield8'}='radio';
				$db_select_fields{'ajaxpmtfield8'} = 'P,C';
				$db_valid_types{'captured'}='radio';
				$db_valid_types{'reason'} = 'selection';
				$db_select_fields{'ajaxreason'}= 'Sale,Exchange,Reship,Other';
				
			
				$db_select_fields{'ajaxcaptured'} = $db_select_fields{'captured'};
				$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};
				@headerfields = (@db_cols[3..14],@db_cols[16..18],@db_cols[20]);
				@titlefields =  ('Name in check','Routing (ABA) #','Account #','Cheque #','Birth Date','Licencia','State Lic','Check Type','Lic Number','Amount','Reason','Pay Date','AuthCode','Captured','CapDate','Status');;
			}
			
		}
	}else{
		if ($rec{'type'} eq 'Credit-Card'){
			$db_valid_types{'pmtfield1'}='selection';
			$db_select_fields{'ajaxpmtfield1'}= 'Visa,Mastercard,American Express,Discover';
			$db_valid_types{'captured'}='radio';
			$db_select_fields{'ajaxcaptured'} = $db_select_fields{'captured'};
			$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};		
			@headerfields = ($db_cols[12],$db_cols[14]);
			@titlefields =  ('Amount','Payment Date');
		}else{
			$db_valid_types{'pmtfield7'}='selection';
			$db_select_fields{'ajaxpmtfield7'} = join(',',&load_enum_toarray('sl_orders','State'));
			$db_valid_types{'pmtfield8'}='radio';
			$db_select_fields{'ajaxpmtfield8'} = 'P,C';
			$db_valid_types{'captured'}='radio';
			
		
			$db_select_fields{'ajaxcaptured'} = $db_select_fields{'captured'};
			$db_select_fields{'ajaxstatus'} = $db_select_fields{'status'};
			@headerfields = @db_cols[12];
			@titlefields =  ('Amount');
		}
	}
	$va{'searchform'} = &html_record_form (%rec);
	
	print &build_page('forms:general_form.html');
}


sub customer_addpmt{
#-----------------------------------------
	my ($invoice_info,$total_payments,@id_orders_payments,%services_mnt,$last_order,$link_to_join,$err_amount);
	my (@c) = split(/,/,$cfg{'srcolors'});
	## Colsolidate Payments

	$va{'accounting_date'} = $in{'eff_date'};

	INS: foreach my $key (keys %in){
		if ($key =~ /cons_(\d+)\./)	{
			if ($1>0){
				my ($sth) = &Do_SQL("SELECT SUM(Amount),COUNT(*) FROM `sl_orders_payments` WHERE ID_orders=$1 AND Amount>0  AND Reason='Sale' AND (Captured ='Yes' OR Captured IS NULL) AND `Status`='Approved' AND Type='Deposit'");
				my ($total_amount,$total_qty) = $sth->fetchrow_array();
				if ($total_qty>1){
					my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM `sl_orders_payments` WHERE ID_orders=$1 AND Amount>0  AND Reason='Sale' AND (Captured ='Yes' OR Captured IS NULL) AND `Status`='Approved' AND Type='Deposit' ORDER BY Amount LIMIT 0,1");
					my ($id) = $sth->fetchrow();
					my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Amount='$total_amount' WHERE ID_orders_payments='$id'");
					my ($sth) = &Do_SQL("DELETE FROM sl_orders_payments WHERE ID_orders_payments<>$id AND ID_orders=$1 AND Amount>0  AND Reason='Sale' AND (Captured ='Yes' OR Captured IS NULL) AND `Status`='Approved' AND Type='Deposit'");
					### logs
					$in{'db'} = "sl_orders";
					&auth_logging('orders_payments_updated',$1);
				}
			}
			last INS;
		}
	}

	$va{'btnname'} = &trans_txt('bills_expenses_addbtn'); 
	$va{'btncfm'} = &trans_txt('bills_expenses_confbtn'); 
	$va{'btnres'} = &trans_txt('bills_expenses_resbtn'); 
	
	$va{'confirmation_js'} ='';

	#### Build Services List
	if ($in{'add_amount'}>0){

		$in{'add_id_orders'} = int($in{'add_id_orders'});
		$in{'add_id_services'} = int($in{'add_id_services'});
		if (!$in{'add_type'}){
			$error{'add_type'} = &trans_txt('required');
			++$err;
		}
		if (!$in{'add_id_services'}){
			$error{'add_id_services'} = &trans_txt('required');
			++$err;
		}
		if (!$in{'add_id_orders'}){
			$error{'add_id_orders'} = &trans_txt('required');
			++$err;
		}
		if ($in{'add_type'} and $in{'add_id_services'} and $in{'add_id_orders'}){
			++$in{'extra_services'};
			$in{'service'.$in{'extra_services'}.'_type'} = $in{'add_type'};
			$in{'service'.$in{'extra_services'}.'_id_services'} = int($in{'add_id_services'});
			$in{'service'.$in{'extra_services'}.'_id_orders'} = int($in{'add_id_orders'});
			$in{'service'.$in{'extra_services'}.'_amount'} = $in{'add_amount'};
			$in{'service_to_add'} = 1;
			delete($in{'add_type'});
			delete($in{'add_id_services'});
			delete($in{'add_id_orders'});
			delete($in{'add_amount'});
		}
	}

	## Build Added Service List
	for my $i(0..$in{'extra_services'}){
		$in{'service'.$i.'_id_orders'} = int($in{'service'.$i.'_id_orders'});
		$in{'service'.$i.'_id_services'} = int($in{'service'.$i.'_id_services'});
		if ($in{'service'.$i.'_amount'}>0){
			$d = 1 - $d;
			my ($err_amount) = '';
			if($in{'service'.$i.'_id_services'} and $in{'service'.$i.'_id_orders'}){

				## Credit / Debit
				if ($in{'service'.$i.'_type'} eq 'Credit'){
					$in{'service_order_'.$in{'service'.$i.'_id_orders'}} -= $in{'service'.$i.'_amount'};
					## Service
					my $id_services = 600000000 + $in{'service'.$i.'_id_services'};
					my $id_orders = $in{'service'.$i.'_id_orders'};
	
					## Price
					my $saleprice = $in{'service'.$i.'_amount'};
					$tax_percent = &load_name('sl_services','ID_services',$id_services,'Tax');
					$tax_percent = 0 if(!$tax_percent);
					$tax = $saleprice * $tax_percent;
					$tax = 0 if(!$tax);
					$total_saleprice = $saleprice + $tax;
				
					$total_order = &get_order_amountdue($id_orders);
					if ($total_order < $total_saleprice){
						$err_amount = &trans_txt('invalid');
						++$err;
					}
					my ($sth) = &Do_SQL("SELECT ID_orders_payments,Amount FROM sl_orders_payments WHERE ID_orders=$in{'service'.$i.'_id_orders'} AND Amount>=$in{'service'.$i.'_amount'}  AND Reason='Sale' AND (Captured ='Yes' OR Captured IS NULL) AND `Status`='Approved' AND Type='Deposit' ORDER BY Amount LIMIT 0,1");
					my ($id,$p_amount) = $sth->fetchrow_array;
					if (($in{'payments_'.$id}-$in{'service'.$i.'_amount'})>$p_amount){
						$err_amount = &trans_txt('invalid');
						++$err;
					}
				}else{
					$in{'service_order_'.$in{'service'.$i.'_id_orders'}} += $in{'service'.$i.'_amount'};
				}
			}
			$va{'list_services'} .= "
		<tr bgcolor='$c[$d]'>
			<td valign='top' class='smalltext'>$in{'service'.$i.'_type'}</td>
			<td valign='top' class='smalltext'>$in{'service'.$i.'_id_orders'}</td>
			<td valign='top' class='smalltext'>($in{'service'.$i.'_id_services'}) ".&load_name('sl_services','ID_services',$in{'service'.$i.'_id_services'},'Name')."</td>
			<td align='right'><input type='text' name='service".$i."_amount' value='$in{'service'.$i.'_amount'}' onfocus='focusOn( this )' onblur='focusOff( this )'>  
				<span class='smallfieldterr'>$err_amount</span>
				<input type='hidden' name='service".$i."_type' value='$in{'service'.$i.'_type'}'>
				<input type='hidden' name='service".$i."_id_services' value='$in{'service'.$i.'_id_services'}'>
				<input type='hidden' name='service".$i."_id_orders' value='$in{'service'.$i.'_id_orders'}'>
			</td>
		</tr>\n";
		}
	}


	####################################
	####################################
	##########
	########## Payments List Section
	##########
	####################################
	####################################
	$va{'div_height'} = 50;
	my $id_customers = int($in{'id_customers'});
	my $total_amount = 0;
	my ($sth) =  &Do_SQL("SELECT ID_vars, Subcode FROM sl_vars WHERE VValue = '$id_customers' AND VName = 'Customer Payment';");
	while(my($id_vars, $data) = $sth->fetchrow()){

		$va{'div_height'} += 22;
		my ($id_orders,$id_payments,$id_invoices,$amount) = split(/:/, $data);
		$total_amount += $amount;
		my ($sth) = &Do_SQL("SELECT CONCAT(doc_serial,doc_num), xml_fecha_certificacion FROM cu_invoices WHERE ID_invoices = '$id_invoices';");
		my($inv_name,$inv_date) = $sth->fetchrow();
		my ($sth_terms) = &Do_SQL("SELECT IF(LENGTH(Pterms) > 0,DATE_ADD('$inv_date',INTERVAL  CreditDays DAY), '$inv_date') FROM sl_orders LEFT JOIN sl_terms ON Name=Pterms WHERE ID_orders = '$id_orders';");
		my ($order_due_date) = $sth_terms->fetchrow();

		$va{'ids_in'} .= qq|<tr id="row-$id_vars">\n
							<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$id_vars" style="cursor:pointer" title="Drop Line"></td>\n
							<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders" title="View $id_orders">$id_orders</a></td>\n
							<td>$inv_date</td>\n 
							<td>$order_due_date</td>\n 
							<td>$inv_name</td>\n
							<td align="right">|. &format_price($amount).qq|</td>\n 
						</tr>|;

	}


	if($va{'ids_in'}) {
		$va{'ids_in'} = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
						<tr>\n 
							<td align="center" class="menu_bar_title">&nbsp;</td>\n 
							<td align="center" class="menu_bar_title">Order</td>\n 
							<td align="center" class="menu_bar_title">Pmt Date</td>\n 
							<td align="center" class="menu_bar_title">Due Date</td>\n 
							<td align="center" class="menu_bar_title">Invoice</td>\n 
							<td align="center" class="menu_bar_title">(|.&format_price($total_amount).qq|) Amount Assigned </td>\n 
						</tr>\n
						$va{'ids_in'}
					</table>\n
					<input type="hidden" id="total_amt" name="total_amt" value="$total_amount">\n|;
	}


	if ($in{'action'}) {

		############################################# 
		############################################# 
		############################################# 
		###
		### APLICACION DE PAGO
		###
		############################################# 
		############################################# 
		############################################# 

		## Validamos datos requeridos
		$in{'id_banks'} = int($in{'id_banks'});
		$in{'amount'} = $in{'amount'}*1;
		$in{'bankdate'} = &filter_values($in{'bankdate'});
		$in{'consdate'} = &filter_values($in{'consdate'});
		$in{'refnum'} = &filter_values($in{'refnum'});
		$in{'memo'} = &filter_values($in{'memo'});
		my $ida_banks; my $exchange_rate;
		
		if (!$in{'id_banks'} or $in{'id_banks'} eq ''){
			$error{'id_banks'} = &trans_txt('required');
			++$err;
		}else{

			###
			### 1. Validacion Cuenta Contable Banco existente
			###
			my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts 
								FROM sl_banks 
									INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts 
								WHERE sl_banks.ID_banks = ".int($in{'id_banks'})." 
									AND sl_banks.`Status` = 'Active' 
									AND sl_accounts.`Status` = 'Active'
								LIMIT 1;");
			$ida_banks = $sth->fetchrow();
			
			if(!$ida_banks){
				$error{'id_banks'} = &trans_txt('mer_bills_bank_accounting_missing');
				++$err;	
			}

			###
			### 2. Validacion Moneda/TipoCambio
			###
			my $bank_currency = &load_name('sl_banks','ID_banks',$in{'id_banks'},'Currency');
			$exchange_rate = $bank_currency ne $cfg{'acc_default_currency'} ? &get_exchangerate($bank_currency, $in{'bankdate'}) : 1;

			if(!$exchange_rate){
				$error{'id_banks'} = &trans_txt('opr_orders_exchangerate_missing');
				++$err;	
			}

		}
		if (!$in{'bankdate'}){
			$error{'bankdate'} = &trans_txt('required');
			++$err;
		}

		if (!$in{'eff_date'} or $in{'eff_date'} eq ''){
			$error{'eff_date'} = &trans_txt('required');
			++$err;
		}else{
			## Validamos que la fecha que se solicito para registrar la contabilidad este en en Periodo Abierto
			if(!&validate_date_in_openperiod($in{'eff_date'})){
				$error{'eff_date'} = &trans_txt('invalid_date_on_open_period');
				++$err;
			}
		}

		if (!$in{'amount'} or $in{'amount'} <= 0){
			$error{'amount'} = &trans_txt('required');
			++$err;
		}
		if (!$in{'doc_type'}) {
			$error{'doc_type'} = &trans_txt('required');
			++$err;
		}
		
		my $total_payments = filter_values($in{'total_amt'});
		$total_payments *= 1;
		my $overpayments = 0;

		## check Valid Total
		if (abs($total_payments - $in{'amount'}) > 0){ 

			if( $total_payments < $in{'amount'} and $in{'accept_greather_amount'} and $cfg{'allow_payment_greather_amount'} == 1){

				$overpayments = round($in{'amount'} - $total_payments,2);

			}else{

				$error{'amount'} = &trans_txt('invalid');
				++$err;

			}

		}

		my @id_orders_payments; my $x = 0; my @this_id_vars;
		my @invoices;
		my ($sth) = &Do_SQL("SELECT ID_vars, Subcode FROM sl_vars WHERE VValue = '$in{'id_customers'}' AND VName = 'Customer Payment';");
		my $sobrante = 0;
		my $sum_aux = 0;
		while( my ($id_vars, $data) = $sth->fetchrow()){

			push(@this_id_vars,$id_vars);
			my ($id_orders,$id_payments,$id_invoices,$amount) = split(/:/, $data);
			push(@id_orders_payments,$id_payments);
			push(@invoices, {'id_invoices' => $id_invoices, 'amount' => $amount} );
			$in{'payments_'.$id_orders_payments[$x]} = $amount;
			$x++;
			$sum_aux += $amount;
		}
		$sobrante = round($in{'amount'} - $sum_aux, 2);
		## check Valid Total
		if (scalar @id_orders_payments == 0 && !$in{'accept_greather_amount'}){
			$error{'amount'} = &trans_txt('invalid');
			++$err;
		}


		if (!$err and $in{'actbutton'} eq &trans_txt('bills_expenses_addbtn')) {

			## Validacion para evitar un movimiento duplicado
			my $sth = &Do_SQL("SELECT COUNT(*) FROM `sl_banks_movements` WHERE `ID_banks`='$in{'id_banks'}' AND `Type`='Debits' AND `BankDate`='$in{'bankdate'}'  AND `Amount`=$in{'amount'} AND `RefNum`='$in{'refnum'}' AND `Memo`='$in{'memo'}';");
			my ($duplicate) = $sth->fetchrow_array();
			my ($applied_payment, $id_banks_movements,$orig_payment,$id_orders);

			if (!$duplicate) {
				# cgierr();
				my $flag = 0; my $flag_customers_advances = 0; my $flag_accounting = 0; my $flag_accounting_str;
				$va{'this_accounting_time'} = time();
				$sl_banks_movements_amount = $in{'amount'};

				&Do_SQL("START TRANSACTION;");

				my ($order_type, $ctype, $ptype, @params);

				#### Saving Extra Services
				if ($in{'extra_services'} > 0) {

					for my $i(0..$in{'extra_services'}){
						if ($in{'service'.$i.'_amount'}>0){
							## Tax
							$tax_percent = &load_name('sl_services','ID_services',(600000000 + $in{'service'.$i.'_id_services'}),'Tax');
							$tax_percent = 0 if(!$tax_percent);
							$tax = $in{'service'.$i.'_amount'} * $tax_percent;
							$tax = 0 if(!$tax);
							
							
							# Agrego el servicio a la orden
							if($in{'service'.$i.'_type'} eq 'Credit'){
								my ($sth) = &Do_mSQL("
								/*START TRANSACTION;*/
								SELECT \@A:=(600000000 + COUNT(*)) FROM `sl_orders_products` WHERE ID_orders=$in{'service'.$i.'_id_orders'} AND RIGHT( ID_orders_products, 1 ) =6;
								INSERT INTO `sl_orders_products`  SET
								 ID_products=\@A,
								 Related_ID_products=600000000+$in{'service'.$i.'_id_services'} , ID_orders=$in{'service'.$i.'_id_orders'}, Quantity=1, 
								 SalePrice=-$in{'service'.$i.'_amount'}, Shipping=0, Cost=0, Tax=$tax, Tax_percent=$tax_percent, 
								 Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};
								 COMMIT;");
								$id_orders_products_new = $sth->{'mysql_insertid'};
							}else{
								my ($sth) = &Do_mSQL("
								/*START TRANSACTION;*/
								SELECT \@A:=(600000000 + COUNT(*)) FROM `sl_orders_products` WHERE ID_orders=$in{'service'.$i.'_id_orders'} AND RIGHT( ID_orders_products, 1 ) =6;
								INSERT INTO `sl_orders_products`  SET
								 ID_products=\@A,
								 Related_ID_products=600000000+$in{'service'.$i.'_id_services'} , ID_orders=$in{'service'.$i.'_id_orders'}, Quantity=1, 
								 SalePrice=$in{'service'.$i.'_amount'}, Shipping=0, Cost=0, Tax=$tax, Tax_percent=$tax_percent, 
								 Status='Active', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'};
								 COMMIT;");
								$id_orders_products_new = $sth->{'mysql_insertid'};
							}

							#log
							$in{'db'} = "sl_orders";
							&auth_logging('orders_products_added',$in{'service'.$i.'_id_orders'});
							if($in{'service'.$i.'_type'} eq 'Credit'){

								my ($sth) = &Do_SQL("SELECT ID_orders_payments,Amount FROM sl_orders_payments WHERE ID_orders = '". $in{'service'.$i.'_id_orders'} ."' AND Amount >= '". $in{'service'.$i.'_amount'} ."' AND Reason = 'Sale' AND (Captured = 'Yes' OR Captured IS NULL) AND Status = 'Approved' AND Type = 'Deposit' ORDER BY Amount DESC LIMIT 0,1");
								my ($id,$p_amount) = $sth->fetchrow_array;
								&Do_SQL("UPDATE sl_orders_payments SET Amount = '". ($p_amount - $in{'service'.$i.'_amount'} - $tax) ."' WHERE ID_orders_payments = '". $id ."';");

							}else{

								my ($sth) = &Do_SQL("SELECT ID_orders_payments,Amount FROM sl_orders_payments WHERE ID_orders=$in{'service'.$i.'_id_orders'} AND Amount>0  AND Reason='Sale' AND (Captured ='Yes' OR Captured IS NULL) AND `Status`='Approved' AND Type='Deposit' ORDER BY Amount DESC LIMIT 0,1");
								my ($id,$p_amount) = $sth->fetchrow_array;
								&Do_SQL("UPDATE sl_orders_payments SET Amount = '". ($p_amount + $in{'service'.$i.'_amount'} + $tax) ."' WHERE ID_orders_payments = '". $id ."';");

							}

							#log
							$in{'db'} = "sl_orders";
							&auth_logging('orders_payments_updated',$id_orders);
							&recalc_totals($id_orders);

							$va{'messages'} .= "<li>".&trans_txt('banks_mv_service_added_order').' '.$id_orders."</li>";

						}

					}
				}

				my $bank_currency = &load_name('sl_banks','ID_banks',$in{'id_banks'},'Currency');
				$exchange_rate = $bank_currency ne $cfg{'acc_default_currency'} ? &get_exchangerate($bank_currency, $in{'bankdate'}) : 1;

				##
				### Bank Movement
				##
				# use Data::Dumper;
				# cgierr(Dumper \%in);
				my $sth = &Do_SQL("INSERT INTO sl_banks_movements SET 
					ID_banks = '". $in{'id_banks'} ."', 
					Type = 'Debits', 
					BankDate = '". $in{'bankdate'} ."', 
					Amount = '". round( $in{'amount'} * $exchange_rate, 2) ."', 
					AmountCurrency = '". $in{'amount'} ."', 
					currency_exchange = '".$exchange_rate."', 
					RefNum = '". $in{'refnum'} ."', 
					doc_type = '". $in{'doc_type'} ."', 
					account_number = '$in{'cuenta_emisor'}',
					payment_type = '$in{'payment_type'}',
					use_cfdi = '$in{'use_cfdi_ingreso'}',
					fcode_bank = '$in{'rfc_banco_emisor'}',
					bank = '$in{'banco_emisor'}',
					payment_method = '$in{'payment_method'}',
					Memo = '". $in{'memo'} ."', 
					Date = CURDATE(), 
					Time = CURTIME(), 
					ID_admin_users = '". $usr{'id_admin_users'} ."';");
				$id_banks_movements = $sth->{'mysql_insertid'};
				##
				### 1 Application vs Multiple Applications
				##
				my $total_applied = 0; my $id_customers_advances = 0;
				if(scalar @id_orders_payments == 1 and !$overpayments){

					##
					### 1 Application. All amount vs Order
					##
					for my $i (0..$#id_orders_payments) {

						my ($sth) = &Do_SQL("SELECT Amount,ID_orders FROM sl_orders_payments WHERE ID_orders_payments = '". $id_orders_payments[$i] ."';");
						($orig_payment,$id_orders) = $sth->fetchrow_array();

						if ( abs($in{'payments_'.$id_orders_payments[$i]}) == abs($orig_payment) ) {

							### Full Payment
							&Do_SQL("UPDATE sl_orders_payments SET Captured = 'Yes', Authcode = 'BM-". $id_banks_movements ."', CapDate = CURDATE(), PostedDate = CURDATE(), Paymentdate = IF(Paymentdate = '0000-00-00', CURDATE(), Paymentdate), Status = 'Approved', AccountingDate='".$va{'accounting_date'}."' WHERE ID_orders_payments = '". $id_orders_payments[$i] ."';");
							$applied_payment = $id_orders_payments[$i];

						}else{

							my (%overwrite) = ('amount'=>$in{'payments_'.$id_orders_payments[$i]},'captured'=>'Yes', 'capdate'=>$in{'bankdate'}, 'status'=>'Approved');
							$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '". $id_orders_payments[$i] ."'", " ", " ", %overwrite);
							&Do_SQL("UPDATE sl_orders_payments SET Amount = (Amount - ". $in{'payments_'.$id_orders_payments[$i]} .") WHERE ID_orders_payments = '". $id_orders_payments[$i] ."';");
							&Do_SQL("UPDATE sl_orders_payments SET Captured = 'Yes', Authcode = 'BM-". $id_banks_movements ."', CapDate = CURDATE(), PostedDate = CURDATE(), Paymentdate = IF(Paymentdate = '0000-00-00', CURDATE(), Paymentdate), Status = 'Approved', AccountingDate='".$va{'accounting_date'}."' WHERE ID_orders_payments = '". $applied_payment ."';");

						}
						&Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = '". $id_banks_movements ."', tablename = 'orders_payments', tableid = '". $applied_payment ."', AmountPaid = '". $in{'payments_'.$id_orders_payments[$i]} ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."';");


						&payment_logging($id_banks_movements, $in{'id_customers'}, 'Apply', $invoices[$i]{'amount'}, 'cu_invoices', $invoices[$i]{'id_invoices'});

						### logs
						$in{'db'} = "sl_orders";
						&auth_logging('orders_payments_updated',$id_orders);
						
						### Accounting Key Point
						my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$id_orders';");
						($order_type, $ctype) = $sth->fetchrow();
						$ptype = &get_deposit_type($applied_payment,'');
						@params = ($id_orders, $applied_payment ,$ida_banks, $exchange_rate);
						my ($this_acc, $this_acc_str) = &accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
						$flag_accounting++ if $this_acc;
						$flag_accounting_str .= qq|<br>|. $this_acc_str;
						
						
						&add_order_notes_by_type($id_orders,"Payment Applied\n$in{'bankdate'} @ $exchange_rate","Low");
						&auth_logging('orders_payments_applied',$id_orders);

					}

				}else{

					##
					### Multiple Applications. All vs Customer Deposit + Post Application
					##
					my ($sth) = &Do_SQL("INSERT INTO sl_customers_advances (ID_customers, exchangerates, Reference, Description, Amount, AccountingDate, Status, Date, Time, ID_admin_users)
										VALUES ('". $id_customers ."', '". $exchange_rate ."', '". $in{'refnum'} ."', '". $in{'memo'} ."', '". $in{'amount'}."', '".$va{'accounting_date'}."', 'New', CURDATE(), CURTIME(),'".$usr{'id_admin_users'}."');");
					($id_customers_advances) = $sth->{'mysql_insertid'}; 
					&payment_logging($id_banks_movements, $in{'id_customers'}, 'In', $sobrante, 'sl_customers_advances', $id_customers_advances);

					if($id_customers_advances){

						## Bank Movrel
						&Do_SQL("INSERT INTO sl_banks_movrel SET ID_banks_movements = '". $id_banks_movements ."', tablename = 'customers_advances', tableid = '". $id_customers_advances ."', AmountPaid = '". $in{'amount'} ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '".$usr{'id_admin_users'}."';");

						### Accounting Key Point
						$ctype = &load_name('sl_customers', 'ID_customers', $id_customers, 'Type');
						@params = ($id_customers_advances, $ida_banks, $id_banks_movements ,$in{'amount'}, $exchange_rate);
						my ($this_acc, $this_acc_str) = &accounting_keypoints('customer_deposit_' . $ctype, \@params);
						# cgierr(this_acc_str);
						$flag_accounting++ if $this_acc;

						## Adding Orders
						ORDERS:for my $i (0..$#id_orders_payments) {
							&payment_logging($id_banks_movements, $in{'id_customers'}, 'Apply', $invoices[$i]{'amount'}, 'cu_invoices', $invoices[$i]{'id_invoices'});

							my $this_amount = round($in{'payments_'.$id_orders_payments[$i]},2);
							my ($sth) = &Do_SQL("SELECT Amount,ID_orders FROM sl_orders_payments WHERE ID_orders_payments = '". $id_orders_payments[$i] ."';");
							($orig_payment,$id_orders) = $sth->fetchrow_array();

							my $id_orders_payments = ( abs($in{'payments_'.$id_orders_payments[$i]}) == abs($orig_payment) ) ? $id_orders_payments[$i] : 0;

							my ($sth) = &Do_SQL("INSERT INTO sl_customers_advances_payments SET 
												ID_customers_advances = '". $id_customers_advances ."'
												, ID_orders = '". $id_orders ."',
												/*, ID_orders_payments = '". $id_orders_payments[$i] ."',*/
												Amount = '". $this_amount ."', Date = CURDATE(), 
												Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';");
							my $id_customers_advances_payments = $sth->{'mysql_insertid'};

							##
							### Applying each advance
							##
							my ($this_status, $this_str) = &apply_customers_advances($id_customers_advances, $total_applied, $id_customers_advances_payments, $id_orders_payments, $in{'amount'});
							
							if($this_status){

								$flag_customers_advances_application = 1;
								$va{'messages'} = $this_str;
								last ORDERS;

							}

							$total_applied += round($this_amount,2);
							
						}

					}else{

						$flag_customers_advances = 1;

					}

				}

				##
				### Applies Verification
				##
				if($flag_customers_advances_application){

					## 1. Customer Advances Application Failed
					&Do_SQL("ROLLBACK;");

				}elsif($flag_customers_advances){

					## 2. Customers Advances Failed
					&Do_SQL("ROLLBACK;");
					$va{'messages'} .= "<li>".&trans_txt('opr_customers_addpmt_customers_advances')."</li>";

				}elsif($flag_accounting){

					## 3. Accounting Failed
					&Do_SQL("ROLLBACK;");
					$va{'messages'} .= "<li>". &trans_txt('acc_general') .' '. $flag_accounting_str ."</li>";

				}else{
	
					## All done
					if($id_customers_advances){

						## CUstomer Advances Update
						my $this_status = abs($in{'amount'} - $total_applied) < 1 ? 'Applied':'Partial';
						&Do_SQL("UPDATE sl_customers_advances SET Status = '". $this_status ."' WHERE ID_customers_advances = '". $id_customers_advances ."';");

					}
					
					$va{'ids_in'} = qq|<p align="center" style="font-size:2em;color:green">(<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_banks_movements&view=$id_banks_movements" title="View $id_orders">$id_banks_movements</a>) |.&trans_txt('opr_customers_addpmt_done').qq|</p>\n|;
					$va{'this_application_style'} = qq|style="display:none;"|;
					&Do_SQL("DELETE FROM sl_vars WHERE ID_vars IN(". join(',', @this_id_vars) .");") if (scalar @this_id_vars > 0);
					

					# Validacion para Verificar si se creara el Invoice de Pago
					if($cfg{'validate_customer_payment'}){
						$generate_payment_invoice = &Do_SQL(qq|SELECT GeneratePaymentInvoice FROM cu_customers_addresses WHERE cu_customers_addresses.PrimaryRecord = 'Yes' AND ID_customers = '$id_customers' LIMIT 1|)->fetchrow();
						if($generate_payment_invoice){
							&export_info_for_payment_invoices( $id_banks_movements );
						}	
					}else{
						&export_info_for_payment_invoices( $id_banks_movements );
					}

					&Do_SQL("COMMIT;");

				}
				delete($in{'bankdate'});
				delete($va{'this_accounting_time'});
				delete($va{'accounting_date'});

				#$va{'messages'} = 'done';				
			}else {
			 	## Enviar mensaje de error, no se puede procesar algo que ya fue procesado
			 	$va{'messages'} .= "<li>".&trans_txt('banks_mv_no_editable')."</li>";
			}
			

		}elsif ($err) {
			$va{'messages'} .= "<li>".&trans_txt('reqfields_short')."</li>";
		}

	}

	## 
	$query = qq|SELECT 
		UPPER(cu_customers_addresses.Account_Number)Account_Number
		, UPPER(cu_customers_addresses.Payment_Type)Payment_Type
		, UPPER(cu_customers_addresses.Use_Cfdi_invoice)Use_Cfdi
		, UPPER(cu_customers_addresses.FCode_Bank)FCode_Bank
		, UPPER(cu_customers_addresses.Bank)Bank
		, cu_customers_addresses.Payment_Method
	FROM cu_customers_addresses
	INNER JOIN sl_customers ON cu_customers_addresses.ID_customers=sl_customers.ID_customers
	WHERE cu_customers_addresses.ID_customers = $in{'id_customers'}
	AND cu_customers_addresses.PrimaryRecord='Yes'
	LIMIT 1;|;
	($va{'account_number'}, $in{'payment_type'}, $in{'use_cfdi'}, $va{'fcode_bank'}, $va{'bank'}, $in{'payment_method'}) = &Do_SQL($query)->fetchrow();
	# $column,$value,$tabindex,$fname,$db,$style
	# $in{'payment_type'} = int($in{'payment_type'});
	$va{'payment_method'} = &build_select_dbfield('payment_method', '', '', 'description', 'cu_metodo_pago', '', 1, '', 1);
	$va{'payment_type'} = &build_select_dbfield('payment_type', '', '', 'description', 'cu_forma_pago', '', 1, '', '');
	$va{'use_cfdi'} = &build_select_dbfield('use_cfdi_ingreso', '', '', 'description', 'cu_uso_cfdi', '', 1, '', 1);
	
	$va{'allow_payment_greather_amount'} = $cfg{'allow_payment_greather_amount'};
	print "Content-type: text/html\n\n";
	print &build_page('ajaxbuild:customer_payment.html');
}

#############################################################################
#   Function: customer_addpmt_dev
#				
#       Es: Registra movimientos bancarios y manda llamar Keypoint para generar movimientos de ajuste por perdida de efectivo COD
#       En: 
#
#
#    Created on: 30/06/2016
#
#    Author: RB
#
#    Modifications:
#
#    Parameters: $invoice_info,$total_payments,@id_orders_payments,%services_mnt,$last_order,$link_to_join,$err_amount
#		
#  Returns:
#
#      - View customer_payment_dev
#
#   See Also:
#
#
sub customer_addpmt_dev{
#-----------------------------------------
	my ($invoice_info,$total_payments,@id_orders_payments,%services_mnt,$last_order,$link_to_join,$err_amount);
	my (@c) = split(/,/,$cfg{'srcolors'});
	## Colsolidate Payments

	$va{'btnname'} = &trans_txt('bills_expenses_addbtn'); 
	$va{'btncfm'} = &trans_txt('bills_expenses_confbtn'); 
	$va{'btnres'} = &trans_txt('bills_expenses_resbtn'); 
	
	$va{'confirmation_js'} ='';

	
	
	if ($in{'action'} eq "1") {
		############################################# 
		############################################# 
		############################################# 
		###
		### APLICACION DE PAGO
		###
		############################################# 
		############################################# 
		############################################# 

		## Validamos datos requeridos
		$in{'id_banks'} = int($in{'id_banks'});
		$in{'amount'} = $in{'amount'}*1;
		$in{'bankdate'} = &filter_values($in{'bankdate'});
		$in{'consdate'} = &filter_values($in{'consdate'});
		$in{'refnum'} = &filter_values($in{'refnum'});
		$in{'memo'} = &filter_values($in{'memo'});
		my $ida_banks; my $exchange_rate;
		
		if (!$in{'id_banks'} or $in{'id_banks'} eq ''){
			$error{'id_banks'} = &trans_txt('required');
			++$err;
		}

		###
		### 1. Validacion Cuenta Contable Banco existente
		###
		my ($sth) = &Do_SQL("SELECT sl_banks.ID_accounts 
							FROM sl_banks 
								INNER JOIN sl_accounts ON sl_accounts.ID_accounts = sl_banks.ID_accounts
							WHERE sl_banks.ID_banks = ".int($in{'id_banks'})." 
								AND sl_banks.`Status` = 'Active' 
								AND sl_accounts.`Status` = 'Active'
							LIMIT 1;");
		$ida_banks = $sth->fetchrow();

		
		if(!$ida_banks){
			$error{'id_banks'} = &trans_txt('mer_bills_bank_accounting_missing');
			++$err;	
		}

		###
		### 2. Validacion Moneda/TipoCambio
		###
		my $bank_currency = &load_name('sl_banks','ID_banks',$in{'id_banks'},'Currency');
		$exchange_rate = $bank_currency ne $cfg{'acc_default_currency'} ? &get_exchangerate($bank_currency, $in{'bankdate'}) : 1;

		if(!$exchange_rate){
			$error{'id_banks'} = &trans_txt('opr_orders_exchangerate_missing');
			++$err;	
		}

		
		if (!$in{'bankdate'}){
			$error{'bankdate'} = &trans_txt('required');
			++$err;
		}
		if (!$in{'amount'} or $in{'amount'} <= 0){
			$error{'amount'} = &trans_txt('required');
			++$err;
		}
		if (!$in{'doc_type'}) {
			$error{'doc_type'} = &trans_txt('required');
			++$err;
		}
		
		my $total_payments = filter_values($in{'total_amt'});
		$total_payments *= 1;
		my $overpayments = 0;

		## check Valid Total
		if (abs($total_payments - $in{'amount'}) > 0){ 

			if( $total_payments < $in{'amount'} and $in{'accept_greather_amount'}){

				$overpayments = round($in{'amount'} - $total_payments,2);

			}else{

				$error{'amount'} = &trans_txt('invalid');
				++$err;
			}
		}

		my ($sth) = &Do_SQL("SELECT Type FROM sl_customers WHERE ID_customers=".$in{'id_customers'});
		my ($CType) = $sth->fetchrow();		
		my (@params);
		
		#####Comenzamos con la insercion en sl_banks_movements
		&Do_SQL("START TRANSACTION;");
		my $sth = &Do_SQL("INSERT INTO sl_banks_movements SET ID_banks = '". $in{'id_banks'} ."', Type = 'Debits', BankDate = '". $in{'bankdate'} ."', Amount = '". $in{'amount'} ."', AmountCurrency = '". $in{'amount'} ."', currency_exchange = '".$exchange_rate."', RefNum = '". $in{'refnum'} ."', doc_type = '". $in{'doc_type'} ."', Memo = '". $in{'memo'} ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';");
		my $id_banks_movements = $sth->{'mysql_insertid'};
		

		my $id_movements1 = '';my $id_movements2 = '';my $id_bankmovrel = '';

		my @id_vars; my $x = 0; my @this_id_vars; my $currSth=''; my $ordersids='';
		my $sthBankMovrel='';
		my ($sth) = &Do_SQL("SELECT ID_vars, CONCAT(VValue,':',Subcode) FROM sl_vars WHERE VValue = '".$in{'id_customers'}."' AND VName = 'Customer Payment dev';");
		while( my ($id_vars, $data) = $sth->fetchrow()){
			my ($id_customer,$id_orders,$id_account,$amount) = split /:/, $data;
			$ordersids.=$id_orders.',';
			
			#####Insertamos los movimientos y asignamos el ID del movimiento con el que relacionaremos movrel
			@params = ($id_account,$ida_banks,$amount,$id_orders,$id_banks_movements);		
			&accounting_keypoints('customer_apply_balance_'.$CType, \@params);
			
			###Relacionamos a traves de la tabla de sl_movrel				
			$sthBankMovrel=&Do_SQL('INSERT INTO sl_banks_movrel
						      SET
						      id_banks_movements='.$id_banks_movements.',
						      tablename="banks_movements",
						      tableid='.$va{'id_movements'}.',
						      AmountPaid='.$amount.',
						      Status="Active",
						      Date=CURDATE(), Time=CURTIME(), ID_admin_users='.$usr{'id_admin_users'});
			$id_bankmovrel=$sthBankMovrel->{'mysql_insertid'};	
		}

		my $lastChar = chop($ordersids);
		my ($updtBankMovement)= &Do_SQL("UPDATE sl_banks_movements SET Memo=CONCAT(Memo,' | Affected Orders: ".$ordersids."') WHERE ID_banks_movements=".$id_banks_movements);
		my ($dltVars) = &Do_SQL("DELETE FROM sl_vars WHERE VValue = '$in{'id_customers'}' AND VName = 'Customer Payment dev';");

		if($va{'id_movements'}){
			&Do_SQL("COMMIT;");	
			$va{'message'}='<center><span style="text-align:center;color:red;font-size:15px">Balance Applied</span></center>';	
			$va{'flag_updated'}=1;
		}else{
			&Do_SQL("ROLLBACK;");
			$va{'message'}='<center><span style="text-align:center;color:red;font-size:15px">'.&trans_txt("opr_orders_chargebacks_erraccounting").'</span></center>';	
			$va{'flag_updated'}=0;
		}

		delete($va{'id_movements'}) if $va{'id_movements'};
		
	}

	####################################
	####################################
	##########
	########## Payments List Section
	##########
	####################################
	####################################
	$va{'div_height'} = 200;
	my $id_customers = int($in{'id_customers'});
	my $total_amount = 0;
	my ($sth) =  &Do_SQL("SELECT ID_vars, CONCAT(VValue,':',Subcode) FROM sl_vars WHERE VValue = '$id_customers' AND VName = 'Customer Payment dev';");
	while(my($id_vars, $data) = $sth->fetchrow()){

		my ($id_customer,$id_orders,$id_account,$amount) = split /:/, $data;
		$total_amount += $amount;
		 my $customer=&load_name('sl_customers','ID_customers',$id_customers,'FirstName');
		 my $account=&load_name('sl_accounts','ID_accounts',$id_account,'Name');

		$str_out .= qq|<tr id="row-$id_vars">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$id_vars" style="cursor:pointer" title="Drop Line"></td>\n
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders" title="View $id_orders">$id_orders</a></td>\n
								<td>$customer</td>\n 
								<td>$account</td>\n 
								<td  align="right">|. &format_price($amount).qq|</td>\n 
							</tr>|;
	}


	if($str_out) {
		$va{'ids_in'} = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">Order</td>\n 
								<td align="center" class="menu_bar_title">Customer</td>\n 
								<td align="center" class="menu_bar_title">Account</td>\n 
								<td align="center" class="menu_bar_title">(|.&format_price($total_amount).qq|) Amount Assigned</td>\n 
							</tr>\n
							$str_out
						</table>\n
						<input type="hidden" id="total_amt" name="total_amt" value="$total_amount">\n|;
	}

	print "Content-type: text/html\n\n";
	print &build_page('ajaxbuild:customer_payment_dev.html');
}


sub orders_viewnotes {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_notes WHERE ID_orders='$in{'id_orders'}';");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		print qq|	<table border="0" cellspacing="0" cellpadding="2" width="550" bgcolor="#CEFFCE" class="formtable">
				<tr>
					<td colspan="3" align="center">Order Status : |.&load_name('sl_orders','ID_orders',$in{'id_orders'},'Status').qq|</td>
				</tr>\n|;
		my ($sth) = &Do_SQL("SELECT sl_orders_notes.ID_admin_users,sl_orders_notes.Date as mDate,sl_orders_notes.Time as mTime,FirstName,LastName,Type,Notes FROM sl_orders_notes,admin_users WHERE ID_orders='$in{'id_orders'}' AND sl_orders_notes.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_orders_notes DESC LIMIT 0,10;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			print qq|
							<tr bgcolor='$c[$d]'>
								<td class='smalltext' valign="top" nowrap>$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>
								<td class='smalltext' valign="top">$rec->{'Type'}</td>
								<td class='smalltext' valign="top">$rec->{'Notes'}</td>
							</tr>\n|;
		}
		print "</table>";
	}else{
		$va{'pageslist'} = 1;
		print qq|
						<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#CEFFCE">
							<tr>
								<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
							</tr>
							</table>\n|;
	}
	
}


sub orders_viewreturns {
#-----------------------------------------
# Created on: 04/13/09  12:11:16 By  Roberto Barcenas
# Forms Involved: 
# Description : Muestra una ventana en ajax con los returns que tiene una orden
# Parameters : 

	print "Content-type: text/html\n\n";

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_orders='$in{'id_orders'}';");
	if ($sth->fetchrow>0){
		my (@c) = split(/,/,$cfg{'srcolors'});
		print qq|	<table border="0" cellspacing="0" cellpadding="2" width="550" bgcolor="#CEFFCE" class="formtable">
				<tr>
					<td align="center">ID return</td>
					<td align="center">Action</td>
					<td align="center">Status</td>
					<td align="center">Date/ID user</td>
				</tr>\n|;
		my ($sth) = &Do_SQL("SELECT ID_returns,sl_returns.ID_admin_users,sl_returns.Date as mDate,merAction,sl_returns.Status,
												IF(sl_returns.Status = 'In Process','sorting',
												IF(sl_returns.Status =	'Repair','repairret',
												IF(sl_returns.Status	=	'QC/IT','qcreturns',
												IF(sl_returns.Status	=	'ATC','atcreturns',
												IF(sl_returns.Status	=	'Processed','crreturns',
												IF(sl_returns.Status	=	'Back to inventory','retwarehouse','opr_returns')))))) AS cmd,
												FirstName,LastName FROM sl_returns,admin_users WHERE ID_orders='$in{'id_orders'}' AND sl_returns.ID_admin_users=admin_users.ID_admin_users ORDER BY ID_returns DESC LIMIT 10;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$rec->{'Notes'} =~ s/\n/<br>/g;
			print qq|
							<tr bgcolor='$c[$d]'>
								<td class='smalltext' align="center" nowrap width="25%"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=$rec->{'cmd'}&modify=$rec->{'ID_returns'}">$rec->{'ID_returns'}</a></td>
								<td class='smalltext' align="center" width="25%">$rec->{'merAction'}</td>
								<td class='smalltext' align="center" width="25%">$rec->{'Status'}</td>
								<td class='smalltext' align="right" width="25%">$rec->{'mDate'} &nbsp; $rec->{'mTime'}<br>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>
							</tr>\n|;
		}
		print "</table>";
	}else{
		$va{'pageslist'} = 1;
		print qq|
						<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#CEFFCE">
							<tr>
								<td colspan='3' align="center">|.&trans_txt('search_nomatches').qq|</td>
							</tr>
							</table>\n|;
	}
	
}



sub order_toreview_payment {
# --------------------------------------------------------
	## To Review Payment
	## status=Review
	## Add Note : Review Payment
	my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='Pending',StatusPay='Review Order' WHERE ID_orders='$in{'id_orders'}';");
	
	&add_order_notes_by_type($in{'id_orders'},"Review Payment","Medium");
	&auth_logging('opr_orders_to_rpay',$in{'id_orders'});
	&auth_logging('opr_orders_stPending',$in{'id_orders'});
	&status_logging($in{'id_orders'},'Pending');
		
	print "Content-type: text/html\n\n";
	print qq|
					<table border="0" cellspacing="0" cellpadding="2" width="350" bgcolor="#FFCFCE">
					<tr>
						<td align="center"><p>&nbsp;</p><b>Order $in{'id_orders'} to Review Payment</b><p>&nbsp;</p></td>
					</tr>
					</table>|;
}





sub add_flags {
# --------------------------------------------------------
	if ($in{'action'} and $in{'id_orders'}){
		my ($num) = 10 ** ($in{'action'}-1);
		$in{'db'} = 'sl_orders';
		if ($in{'remove'}){
			my ($sth) = &Do_SQL("UPDATE sl_orders SET Flags=Flags-$num WHERE ID_orders='$in{'id_orders'}';");
			&auth_logging('opr_orders_flagdel',$in{'id_orders'});
		}else{
			my ($sth) = &Do_SQL("UPDATE sl_orders SET Flags=Flags+$num WHERE ID_orders='$in{'id_orders'}';");
			&auth_logging('opr_orders_flagadd',$in{'id_orders'});
		}
		return;
	}
	print "Content-type: text/html\n\n";
	my ($flags) = &load_name('sl_orders','ID_orders',$in{'id_orders'},'Flags');
	if (!$flags){
		my ($sth) = &Do_SQL("UPDATE sl_orders SET Flags=0 WHERE ID_orders='$in{'id_orders'}';");
	}
	$flags = 0 x (16-length($flags)) . $flags;
	
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders_flags WHERE Status='Active';");
	print qq|<table border="0" cellspacing="0" cellpadding="4" width="350" class="formtable">\n|;
	while ($rec = $sth->fetchrow_hashref){
		$x = substr($flags,16-$rec->{'ID_orders_flags'},1);
		if ($x){
			print qq|
							<tr>
								<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=add_flags&action=$rec->{'ID_orders_flags'}&remove=1&id_orders=$in{'id_orders'}');popup_exit()"><img src='$va{'imgurl'}/$usr{'pref_style'}/flag.gif' title='Remove Flag' alt='' border='0'>$rec->{'Name'}</td>
							</tr>\n|;
		}else{
			print qq|
							<tr>
								<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=add_flags&action=$rec->{'ID_orders_flags'}&id_orders=$in{'id_orders'}');popup_exit()">$rec->{'Name'}</td>
							</tr>\n|;
		}
	}
	print "</table> ";
	print $flags;
	return;	

}

#sub edit_status {
## --------------------------------------------------------
## Last Modified RB: 06/01/09  17:45:26 -- No se puede poner a Cancelled una orden que tiene 1 pago Capturado.
## Last Modified RB: 06/01/09  17:46:07 -- Al cambiar Status a Shipped, se pone el PostedDate a la orden del curdate(). 
## Last Modified RB: 10/19/2010  17:40:07 -- Imposible cambiar status de Ordenes COD escaneadas (solo usuario developer se permite)
## Last Modified by RB on 03/30/2011 01:36:48 PM : Se agregan Status Void y System Error para ordenes con pagos capturados
## Last Modified by RB on 06/23/2011 06:10:00 PM : Se agrega actualizacion sl_cod_sales para ordenes COD  
#
#	print "Content-type: text/html\n\n";
#	my ($sth) = &Do_SQL("SELECT Status,statuspay,statusprd,Ptype FROM sl_orders WHERE ID_orders='$in{'id_orders'}';");
#	my ($rec) = $sth->fetchrow_hashref;	
#	
#	my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$in{'id_orders'}' AND Captured='Yes' AND CapDate IS NOT NULL AND CapDate != '0000-00-00' AND CapDate != '';");
#	$pcaptured = $sth2->fetchrow(); 
#	
#	
#	if ($in{'action'}){
#		$in{'db'}= 'sl_orders';
#		if (!&check_permissions('edit_order_status','','') and  ($rec->{'Status'} eq 'Shipped' or $rec->{'Status'} eq 'Cancelled') and $in{'status'}){
#			$va{'message'} = "<span class='stdtxterr'>".&trans_txt('page_unauth')."</span>"; 
#		}elsif($in{'status'} and ( ($in{'status'} ne 'Cancelled' and $in{'status'} ne 'Void' and $in{'status'} ne 'System Error') or $pcaptured == 0 or &check_permissions('edit_order_status','','')) ){
#
#			## Actualizacion en sl_cod_sales
#			if($rec->{'Ptype'} eq 'COD'){
#				my $n_status = $in{'status'} eq 'Processed' ? 'Processed-To be fulfilled' : $in{'status'};
#				&mod_cod_sales_table($in{'id_orders'},$n_status,'Ajaxbuild:Edit Status');
#			}
#			
#			
#			my ($sth) = &Do_SQL("UPDATE sl_orders SET Status='$in{'status'}' WHERE ID_orders='$in{'id_orders'}';");
#			&auth_logging('opr_orders_st'.$in{'status'},$in{'id_orders'});
#			$rec->{'Status'} = $in{'status'};
#			
#			if($rec->{'Status'} eq 'Shipped'){
#				&Do_SQL("UPDATE sl_orders SET  PostedDate=CURDATE() WHERE ID_orders='$in{'id_orders'}' AND (PostedDate IS NULL OR PostedDate='' OR PostedDate ='0000-00-00');"); 
#			}
#			
#		}elsif ($in{'statuspay'} and &check_permissions('edit_order_statuspay','','')){
#			my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPay='$in{'statuspay'}' WHERE ID_orders='$in{'id_orders'}';");
#			&auth_logging('opr_orders_stp'.$in{'statuspay'},$in{'id_orders'});
#			$rec->{'statuspay'} = $in{'statuspay'};
#		}elsif ($in{'statusprd'} and &check_permissions('edit_order_statusprd','','')){
#			my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPrd='$in{'statusprd'}' WHERE ID_orders='$in{'id_orders'}';");
#			&auth_logging('opr_orders_str'.$in{'statusprd'},$in{'id_orders'});
#			$rec->{'statusprd'} = $in{'statusprd'};
#		}
#	}
#	
#	my (@status) = &load_enum_toarray('sl_orders','Status');
#	my (@statuspay) = &load_enum_toarray('sl_orders','statuspay');
#	my (@statusprd) = &load_enum_toarray('sl_orders','statusprd');
#	my ($cols) = $#statuspay;
#	($cols < $#statusprd) and ($cols = $#statusprd);
#	($cols < $#status) and ($cols = $#status);
#
#
#	my ($block_to_change,$flagst,$flagstpay,$flagstprd,$header);
#	## No se puede editar una orden si se encuentra en una remesa
#	my ($sth_wh) = &Do_SQL("SELECT IF(sl_warehouses_batches.Status IS NULL,'ok',sl_warehouses_batches.Status)AS warning_batch,
#							ID_warehouses_batches
#							FROM sl_orders_products
#							LEFT JOIN sl_warehouses_batches_orders
#							USING(ID_orders_products)
#							LEFT JOIN sl_warehouses_batches
#							USING(ID_warehouses_batches)
#							WHERE ID_orders = '$in{'id_orders'}'
#							GROUP BY ID_orders
#							ORDER BY ID_orders;");
#															
#	my ($status_wh, $id_batch) = $sth_wh->fetchrow();
#	if($status_wh =~ /Sent|Processed/){
#		$block_to_change = 1;
#	}
#
#
#	## Si la orden es COD y esta escaneada, no se permite modificar
#	($rec->{'Ptype'} eq 'COD' and &is_codorder_in_transit($in{'id_orders'})) and ($block_to_change = 1);
#	
#
#	### Columnas de Status
#	if(!$block_to_change or &check_permissions('edit_order_status','','')) { 
#		$header .='<td class="menu_bar_title">Status</td>';
#		$flagst = 1;
#	}else{
#		$header = ''; 
#	}
#
#	if(&check_permissions('edit_order_statuspay','','')) { 
#		$header .='<td class="menu_bar_title">Pay Exception</td>';
#		$flagstpay = 1;
#	}else{
#		$header = ''; 
#	}
#
#	if(&check_permissions('edit_order_statusprd','','')) { 
#		$header .='<td class="menu_bar_title">Prod Exception</td>';
#		$flagstprd = 1;
#	}else{
#		$header = ''; 
#	}
#
#	
#	
#	print qq|$va{'message'}<table border="0" cellspacing="0" cellpadding="4" width="350" class="formtable">
#			<tr>
#				$header
#			</tr>\n|;
#
#	for (0..$cols){
#		print "			<tr>\n";
#
#		if ($status[$_] eq $rec->{'Status'} and $flagst){
#			print qq|	<td class="menu_bar_title">$status[$_]</td>\n|;
#		}elsif($flagst and ($status[$_] ne 'Cancelled' or $pcaptured == 0)){
#			print qq|	<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_status&action=1&status=$status[$_]&id_orders=$in{'id_orders'}');">
#				$status[$_]</td>\n|;
#		}
#
#		if($flagstpay) {
#			if ($statuspay[$_] eq $rec->{'statuspay'}){
#				print qq|	<td class="menu_bar_title">$statuspay[$_]</td>\n|;
#			}else{
#				print qq|	<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_status&action=1&statuspay=$statuspay[$_]&id_orders=$in{'id_orders'}');">
#					$statuspay[$_]</td>\n|;
#			}
#		}
#
#		if($flagstprd) {
#			if ($statusprd[$_] eq $rec->{'statusprd'}){
#				print qq|	<td class="menu_bar_title">$statusprd[$_]</td>\n|;
#			}else{
#				print qq|	<td class="smalltext" onmouseover='m_over(this)' onmouseout='m_out(this)' OnClick="loadDoc('/cgi-bin/common/apps/ajaxbuild?ajaxbuild=edit_status&action=1&statusprd=$statusprd[$_]&id_orders=$in{'id_orders'}');">
#					$statusprd[$_]</td>\n|;
#			}
#		}
#
#
#		print "	</tr>\n";
#	
#	}
#	print "</table> ";
#	print $flags;
#	return;	
#}


sub update_customerdata{
# --------------------------------------------------------
# Forms Involved: opr_orders_view, orders_view
# Created on: 30 Dec 2011 17:55:14
# Author: Roberto Barcenas
# Description :
# Description: Actualiza Phone,Phone2,Cellphone,Email de un cliente
# Parameters :
# Last Modified RB: 12/30/2011

	print "Content-type: text/html\n\n";
	#print "Esto es prueba";
	#return;

	if(!$in{'id_customers'} or !$in{'field'}){ # or !$in{'val'}
		print "error = $in{'id_customers'} - $in{'field'} - $in{'val'}";
		return;
	}

	my $field = ucfirst($in{'field'});
	$in{'val'} =~ s/\(|\)|-| //g;

	#print "error:UPDATE sl_customers SET $field ='".&filter_values($in{'val'})."' WHERE ID_customers = '$in{'id_customers'}';";
	#return;

	my ($sth)=&Do_SQL("UPDATE sl_customers SET $field ='".&filter_values($in{'val'})."' WHERE ID_customers = '$in{'id_customers'}';");
	
	if($sth->rows() == 1){
		
		$in{'db'}='sl_customers'; $in{'cmd'}='customers';
		&auth_logging($field.'customers_updated',$in{'id_customers'});
		my ($sth) = &Do_SQL("INSERT INTO sl_customers_notes SET ID_customers = '$in{'id_customers'}', Notes = '$field edited', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{'id_customers'},0);
		print 'ok';
		
	}else{
		print  "error:".$sth->errmsg();
	}
	return;
}

sub update_orderdata{
# --------------------------------------------------------
# Forms Involved: orders_view
# Created on: 15 apr 2013 11:30:14
# Author: Erik Osornio
# Description :
# Description: Actualiza Ptype de una orden
# Parameters :
# Last Modified RB: 12/30/2011

	print "Content-type: text/html\n\n";

	if(!$in{'id_orders'} or !$in{'field'} or !$in{'val'}){
		print "error = $in{'id_orders'} - $in{'field'} - $in{'val'}";
		return;
	}
	#print "id_orders: $in{'id_orders'}, in_field: $in{'field'}, in_val: $in{'val'}";
	my (@values) = split(/ \| /, $in{'val'});
	
	$in{'val'} = $values['0'];
	
	if (&check_permissions('edit_order_cleanup','','')) {
		my ($sth) = &Do_SQL("SELECT ID_orders_parts FROM sl_orders_products oprod JOIN sl_orders_parts oparts ON oprod.ID_orders_products=oparts.ID_orders_products WHERE ID_orders='$in{'id_orders'}';");
		if ($sth->rows() == 0) {
			
			$in{'db'} = 'sl_orders'; $in{'cmd'} = 'opr_orders';
			my $field = ucfirst($in{'field'});
			my ($sth2)=&Do_SQL("UPDATE sl_orders SET $field ='".&filter_values($in{'val'})."' WHERE ID_orders = '$in{'id_orders'}' LIMIT 1;");
			
			if ($sth2->rows() == 1) {

				&auth_logging('orders_updated',$in{'id_orders'});
				&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{'id_orders'},0);

				if (lc($field) eq 'status'){

					&auth_logging('opr_orders_st' . $in{'val'},$in{'id_orders'});
					&status_logging($in{'id_orders'},$in{'val'});

				}

			}else {
				print  "error: ".$sth2->errmsg();
			}

		} else {
			print "error: La orden ha sido escaneada.";
		}

    }
	
	return;
}


sub order_chg_statusprd {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	if(&check_permissions('edit_order_statusprd','','') and $in{'id_orders'}>0 and $in{'val'}) { 
		$in{'db'} = 'sl_orders'; $in{'cmd'} = 'opr_orders';
		my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPrd='$in{'val'}' WHERE ID_orders='$in{'id_orders'}';");
		&auth_logging('opr_orders_str'.$in{'val'},$in{'id_orders'});
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{'id_orders'},0);
		print 'ok';
	}else{
		print 'error';
	}
}

sub order_chg_statuspay {
# --------------------------------------------------------
	print "Content-type: text/html\n\n";
	if(&check_permissions('edit_order_statuspay','','') and $in{'id_orders'}>0 and $in{'val'}) { 
		$in{'db'} = 'sl_orders'; $in{'cmd'} = 'opr_orders';
		my ($sth) = &Do_SQL("UPDATE sl_orders SET StatusPay='$in{'val'}' WHERE ID_orders='$in{'id_orders'}';");
		&auth_logging('opr_orders_stp'.$in{'val'},$in{'id_orders'});
		&memcached_delete('e' . $in{'e'} . '_' .$in{'db'} . '_' . $in{'id_orders'},0);
		print 'ok';
	}else{
		print 'error';
	}
}

sub pay_referenced_deposit{

	# $in{'id_orders'}
	# $in{'id_orders_payments'}
	# $in{'rsid'}

	print "Content-type: text/html\n\n";
	if(!&check_permissions('edit_order_cleanup','','')){
		$va{'message'} = &trans_txt('perms_insufficient_perms');
		$va{'display'} = 'display:none;';
	}

	print &build_page('ajaxbuild:payment_charge.html');
}



#############################################################################
#############################################################################
#   Function: customers_addpmt_edit
#				
#       Es: Maneja  add/drop para customer payments
#       En: 
#
#
#    Created on: 03/25/2013  19:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		- id_customers = id from table
#		- type = load_data | add | drop
#       - keyword = search word
#		- data_in = idwl:qty
#		
#  Returns:
#
#      - Error/datasource/table with data
#
#   See Also:
#
#	<view_opr_adjustments>
#
sub customers_addpmt_edit {
#############################################################################
#############################################################################

	my ($id_customers) = int($in{'id'});
	my ($type) = &filter_values($in{'type'});
	my ($keyword) = &filter_values($in{'keyword'});
	my ($data_in) = &filter_values($in{'data_in'});
	my ($idmi) = &filter_values($in{'idmi'});
	my $qty_completed = 0;
	my $remaining_qty = 0;

	
	if($type eq 'load'){

		print "Content-type:  application/json\n\n";
		
		my ($str,$ids);
		my $mod = $keyword ne '' ? " AND ( CONCAT(doc_serial,doc_num) LIKE '%$keyword%' OR ID_orders = '$keyword'  OR CONCAT( MONTHNAME(xml_fecha_certificacion), ' ', YEAR(xml_fecha_certificacion)) LIKE '%$keyword%' )  " : '';
		
		## Customer Invoices
		my $query = "SELECT ID_invoices, 
		  			ID_orders, 
				    CONCAT(doc_serial,doc_num), 
				    CONCAT( MONTHNAME(xml_fecha_certificacion), ' ', YEAR(xml_fecha_certificacion)), 
					invoice_total, AmtDue 
					FROM cu_invoices_lines 
					INNER JOIN cu_invoices 
					USING(ID_invoices) 
					INNER JOIN 
					(
						SELECT ID_orders, SUM(Amount) AS AmtDue 
						FROM sl_orders INNER JOIN sl_orders_payments 
						USING(ID_orders)
						WHERE ID_customers = '$id_customers' 
						AND sl_orders.Status NOT IN ('Cancelled','Void','System Error')
						AND sl_orders_payments.Status NOT IN ('Void','Order Cancelled','Cancelled')
						AND (CapDate IS NULL OR CapDate = '0000-00-00')
						GROUP BY sl_orders.ID_orders
						HAVING AmtDue > 0
					)sl_orders
					USING(ID_orders) 
					WHERE 
					cu_invoices.Status = 'Certified'
					AND invoice_type = 'ingreso'
					$mod
					GROUP BY cu_invoices.ID_invoices, sl_orders.ID_orders
					ORDER BY CONCAT(doc_serial,doc_num), invoice_total, AmtDue ;";
		my ($sth) =  &Do_SQL($query);
		# cgierr($query);
		while(my($id_invoices, $id_orders, $invoice, $mdate, $amt_total, $amt_due) = $sth->fetchrow()){
			$ids .="$id_orders|";
			$str .= '{"ido":"'.$id_orders.'","idi":"'.$id_invoices.'","name":"'.$invoice.'","mdate":"'.$mdate.'","due":"'.$amt_due.'"},';
		}
		chop($str);
		$str = '{"inv":['.$str.']}';
		print $str;
		return;

	}
	
	if($type =~ /add|drop/) {

		print "Content-type: text/html\n\n";
		
		if($type eq 'add' and (!$id_customers or !$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif($type eq 'drop' and !$idmi){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my ($str,$str_out);
		$str_out = '';
		my $t = 0;


		&Do_SQL("START TRANSACTION");
		if($type eq 'add') {

			####################################
			####################################
			##########
			########## Add Section
			##########
			####################################
			####################################
			
			my ($id_orders, $id_invoices, $amount) = split(/:/, $data_in);
			my $overpayment;

			$id_orders = int($id_orders);
			$id_invoices = int($id_invoices);
			$amount = round($amount,2);

			if(!$id_orders or !$id_invoices or !$amount) {
				&Do_SQL("ROLLBACK");
				print "Error: Data In Wrong ($data_in)";
				return;
			}

			my ($sth) = &Do_SQL("SELECT IF(SUM(Amount) IS NULL,0, SUM(Amount)),COUNT(*),SUM(IF(Amount > 0 AND Reason IN('Sale', 'Exchange', 'Reship'),1,0)) 
								FROM sl_orders INNER JOIN sl_orders_payments USING(ID_orders)
								WHERE ID_orders = ". $id_orders ."
								AND sl_orders.Status NOT IN ('Cancelled','Void','System Error')
								AND sl_orders_payments.Status NOT IN ('Void','Order Cancelled','Cancelled')
								AND (CapDate IS NULL OR CapDate = '0000-00-00')
								GROUP BY sl_orders.ID_orders;");
			my ($this_amt, $qty_to, $qty_pmt) = $sth->fetchrow();

			if($this_amt < $amount) {
				if( $in{'accept_greater_amt'} ne '1' ){
					&Do_SQL("ROLLBACK");
					print "Error: Amount Due Lesser: $this_amt < $amount";
					return;
				}else{
					$overpayment = $amount - $this_amt;
					$amount = $this_amt;
				}
			}

			my ($sth1) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments 
								WHERE ID_orders = ". $id_orders ."
								AND Status NOT IN ('Void','Order Cancelled','Cancelled')
								AND (CapDate IS NULL OR CapDate = '0000-00-00')
								AND Reason IN('Sale', 'Exchange', 'Reship') AND Amount > 0
								ORDER BY PaymentDate LIMIT 1;");
			my ($id_1) = $sth1->fetchrow();
			my ($sthx) = &Do_SQL("UPDATE sl_orders_payments SET Amount = '". $amount ."', Captured = 'No', CapDate = '0000-00-00' WHERE ID_orders_payments = ". $id_1 .";");
			$t = $sthx->rows();

			if($t){

				####
				#### Guardamos linea en sl_vars
				####

				###
				### 1) Registro anterior?
				###
				my ($sthr1) = &Do_SQL("DELETE FROM sl_vars WHERE VValue = '$id_customers' AND VName = 'Customer Payment' AND Subcode LIKE '$id_orders%';");

				###
				### 2) Linea nueva
				###
				my $pairs = "$id_orders:$id_1:$id_invoices:$amount";
				my ($sthr2) = &Do_SQL("INSERT INTO sl_vars SET VName = 'Customer Payment', Subcode = '$pairs', VValue = '$id_customers';");
				

				#####
				##### Necesita actualizarse el pago?
				#####
				if($this_amt > $amount){

					if($qty_pmt == 1){

						###
						### 1) Insert?
						###

						my $qwhere = "ID_orders_payments = '". $id_1 ."'";
						my (%overwrite) = ( 'amount' => round($this_amt - $amount,2), 'captured' => 'no', 'capdate' => '0000-00-00', 'paymentdate' => 'curdate()' );
						my $new_pmt =  &Do_selectinsert('sl_orders_payments', $qwhere , '', '', %overwrite);
					
					}else{

						###
						### 2) Update 
						###

						##
						### 2.1) Actualizamos 1 pago por el monto restante
						##
						my ($sth2) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments
								WHERE ID_orders = ". $id_orders ."
								AND Status NOT IN ('Void','Order Cancelled','Cancelled')
								AND (CapDate IS NULL OR CapDate = '0000-00-00') 
								AND Reason IN('Sale', 'Exchange', 'Reship') AND Amount > 0
								AND ID_orders_payments NOT IN (". $id_1 .")
								ORDER BY PaymentDate LIMIT 1;");
						my ($id_2) = $sth2->fetchrow();
						my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Amount = (". $this_amt ." - ". $amount .") WHERE ID_orders_payments = '". $id_2 ."';");

						if($qty_pmt > 2){

							##
							### 2.2) Si hay mas pagos activos, se cancelan
							##
							my ($sth) = &Do_SQL("UPDATE sl_orders_payments SET Status = 'Cancelled' WHERE ID_orders = ". $id_orders ."
												AND ID_orders_payments NOT IN(". $id_1 .", ". $id2 .")
												AND Status NOT IN ('Void','Order Cancelled','Cancelled')
												AND Reason IN('Sale', 'Exchange', 'Reship') AND Amount > 0
												AND (CapDate IS NULL OR CapDate = '0000-00-00');");

						}


					}


				}


			}

		}elsif($type eq 'drop'){

			####################################
			####################################
			##########
			########## Drop Section
			##########
			####################################
			####################################

			my ($sth) = &Do_SQL("DELETE FROM sl_vars WHERE ID_vars = '". $idmi ."';");
			$t = $sth->rows();
			

		}

		if(!$t) {
			&Do_SQL("ROLLBACK");
			print "Error: Duplicated Record" if $type eq 'add';
			print "Error: Record Not Dropped $idmi" if $type eq 'drop';
			return;
		}

		&Do_SQL("COMMIT");
		####################################
		####################################
		##########
		########## Payments List Section
		##########
		####################################
		####################################


		my $total_amount = 0;
		my ($sth) =  &Do_SQL("SELECT ID_vars, Subcode FROM sl_vars WHERE VValue = '$id_customers' AND VName = 'Customer Payment';");
		while(my($id_vars, $data) = $sth->fetchrow()){

			my ($id_orders,$id_payments,$id_invoices,$amount) = split(/:/, $data);
			$total_amount += $amount;
			my ($sth) = &Do_SQL("SELECT CONCAT(doc_serial,doc_num), xml_fecha_certificacion FROM cu_invoices WHERE ID_invoices = '$id_invoices';");
			my($inv_name,$inv_date) = $sth->fetchrow();
			my ($sth_terms) = &Do_SQL("SELECT IF(LENGTH(Pterms) > 0,DATE_ADD('$inv_date',INTERVAL  CreditDays DAY), '$inv_date') FROM sl_orders LEFT JOIN sl_terms ON Name=Pterms WHERE ID_orders = '$id_orders';");
			my ($order_due_date) = $sth_terms->fetchrow();

			$str_out .= qq|<tr id="row-$id_vars">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$id_vars" style="cursor:pointer" title="Drop Line"></td>\n
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders" title="View $id_orders">$id_orders</a></td>\n
								<td>$inv_date</td>\n 
								<td>$order_due_date</td>\n 
								<td>$inv_name</td>\n
								<td  align="right">|. &format_price($amount).qq|</td>\n 
							</tr>|;

		}

		if($str_out) {
			$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">Order</td>\n 
								<td align="center" class="menu_bar_title">Pmt Date</td>\n 
								<td align="center" class="menu_bar_title">Due Date</td>\n 
								<td align="center" class="menu_bar_title">Invoice</td>\n 
								<td align="center" class="menu_bar_title">(|.&format_price($total_amount).qq|) Amount Assigned</td>\n 
							</tr>\n
							$str_out
						</table>\n
						<input type="hidden" id="total_amt" name="total_amt" value="$total_amount">\n|;
			print $str_out;				
		}

		return;
	}	
	

	print "Content-type: text/html\n\n";
	print "-1";
	return;
}


#############################################################################
#   Function: customers_addpmt_edit_dev
#				
#       Es: Manipula los registros temporales de la tabla sl_vars referente a los montos ingresados de pagos por concepto de perdida de efectivo por parte de paqueteria
#       En: 
#
#
#    Created on: 30/06/2016
#
#    Author: RB
#
#    Modifications:
#
#    Parameters: $id_customers,$type,$keyword,$data_in,$idmi
#		
#  Returns:
#
#      - View customer_payment_dev
#
#   See Also:
#
#
sub customers_addpmt_edit_dev {
#############################################################################
#############################################################################

	my ($id_customers) = int($in{'id'});
	my ($type) = &filter_values($in{'type'});
	my ($keyword) = &filter_values($in{'keyword'});
	my ($data_in) = &filter_values($in{'data_in'});
	my ($idmi) = &filter_values($in{'idmi'});
	my $qty_completed = 0;
	my $remaining_qty = 0;

	
	if($type eq 'load'){

		print "Content-type:  application/json\n\n";
		
		my ($str,$ids);
				
		## Customer Invoices
		my $query = 'SELECT sl_orders.ID_orders, sl_customers.ID_accounts_debit,sl_customers.ID_customers,
					sl_movements.Amount as "Debit",
					(
						SELECT SUM(m2.Amount) 
						FROM sl_movements m2
						JOIN sl_customers c2 ON c2.ID_accounts_debit=m2.ID_accounts
						WHERE m2.ID_tableused=sl_orders.ID_orders
						and m2.tableused="sl_orders"
						AND m2.Credebit="Credit"
						AND c2.ID_customers='.$id_customers.'
					) as "Credit"
					FROM sl_movements 
					JOIN sl_orders ON sl_orders.ID_orders=sl_movements.ID_tableused
					JOIN sl_customers ON sl_customers.ID_accounts_debit=sl_movements.ID_accounts
					join sl_accounts on sl_accounts.ID_accounts=sl_customers.ID_accounts_debit
					WHERE
						sl_orders.ID_orders='.$keyword.'
						AND sl_movements.ID_accounts=sl_customers.ID_accounts_debit
						AND sl_movements.Status = "Active"
						AND sl_movements.tableused="sl_orders"
						AND sl_movements.Credebit="Debit"
					GROUP BY(ID_orders);';
		my ($sth) =  &Do_SQL($query);

		while(my($ID_orders, $ID_accounts_debit, $ID_customers, $Amount,$credit) = $sth->fetchrow()){
			if(!$credit){
				$credit="0.00";
			}
			$str .= '{"ido":"'.$ID_orders.'","iad":"'.$ID_accounts_debit.'","idc":"'.$ID_customers.'","amnt":"'.$Amount.'","dbt":"'.$credit.'"},';
		}
		chop($str);
		$str = '{"inv":['.$str.']}';
		print $str;
		return;

	}
	
	if($type =~ /add|drop/) {

		print "Content-type: text/html\n\n";
		
		# use Data::Dumper;
		# cgierr(Dumper \%data_in);
		# cgierr($data_in);

		if($type eq 'add' and (!$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif($type eq 'drop' and !$idmi){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my ($str,$str_out);
		$str_out = '';
		my $t = 0;

		if($type eq 'add') {			
			my ($id_customer,$id_orders, $id_account, $amount) = split /:/, $data_in;
			# my ($sthr1) = &Do_SQL("DELETE FROM sl_vars WHERE VValue = '$id_customers' AND VName = 'Customer Payment dev' AND Subcode LIKE '$id_orders%';");
			my $pairs = "$id_orders:$id_account:$amount";
			my ($sthr2) = &Do_SQL("INSERT INTO sl_vars SET VName = 'Customer Payment dev', Subcode = '$pairs', VValue = '$id_customers';");
		}elsif($type eq 'drop'){
			my ($sth) = &Do_SQL("DELETE FROM sl_vars WHERE ID_vars = '$idmi';");
			$t = $sth->rows();
		}


		####################################
		####################################
		##########
		########## Payments List Section
		##########
		####################################
		####################################


		my $total_amount = 0;
		my ($sth) =  &Do_SQL("SELECT ID_vars, CONCAT(VValue,':',Subcode) FROM sl_vars WHERE VValue = '$id_customers' AND VName = 'Customer Payment dev';");
		while(my($id_vars, $data) = $sth->fetchrow()){

			my ($id_customer,$id_orders,$id_account,$amount) = split /:/, $data;
			$total_amount += $amount;
			 my $customer=&load_name('sl_customers','ID_customers',$id_customers,'FirstName');
			 my $account=&load_name('sl_accounts','ID_accounts',$id_account,'Name');
			
			$str_out .= qq|<tr id="row-$id_vars">\n
								<td><img src="/sitimages/default/b_drop.png" class="rdrop" id="drop-$id_vars" style="cursor:pointer" title="Drop Line"></td>\n
								<td><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$id_orders" title="View $id_orders">$id_orders</a></td>\n
								<td>$customer</td>\n 
								<td>$account</td>\n 
								<td  align="right">|. &format_price($amount).qq|</td>\n 
							</tr>|;

		}

		if($str_out) {
			$str_out = qq|<table id="tbl-id-in" width="98%" align="center" cellspacing="2" cellpadding="2" class="formtable">\n 
							<tr>\n 
								<td align="center" class="menu_bar_title">&nbsp;</td>\n 
								<td align="center" class="menu_bar_title">Order</td>\n 
								<td align="center" class="menu_bar_title">Customer</td>\n 
								<td align="center" class="menu_bar_title">Account</td>\n 
								<td align="center" class="menu_bar_title">(|.&format_price($total_amount).qq|) Amount Assigned</td>\n 
							</tr>\n
							$str_out
						</table>\n
						<input type="hidden" id="total_amt" name="total_amt" value="$total_amount">\n|;
			print $str_out;				
		}

		return;
	}	
	

	print "Content-type: text/html\n\n";
	print "-1";
	return;
}

#############################################################################
#############################################################################
#   Function: returns_edit
#				
#       Es: Maneja  list/add/drop para exchange items
#       En: 
#
#
#    Created on: 03/25/2013  19:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		- id_returns = id from table
#		- type = load_data | add | drop
#       - idri = the row to drop
#		- data_in = data entered
#		
#  Returns:
#
#      - Error/datasource/table with data
#
#   See Also:
#
#	<view_opr_returns>
#
sub returns_edit {
#############################################################################
#############################################################################

	my ($id_returns) = int($in{'id'});
	my ($type) = &filter_values($in{'type'});
	my ($idri) = int($in{'idri'});
	my ($data_in) = &filter_values($in{'data_in'});
	
	my $qty_completed = 0;
	my $remaining_qty = 0;

	
	if($type eq 'load_data'){

		########################################
		########################################
		########################################
		####
		#### 1) Busca Payment options de acuerdo a los datos de la orden
		####
		########################################
		########################################
		########################################

		my ($id_kits, $pname) = split(/ @@ /, $data_in);
		my ($id_products) = substr($id_kits,-6);

		my ($sth_p) = Do_SQL("SELECT 
								FP
								, Ptype
								, ID_salesorigins
							FROM sl_returns INNER JOIN sl_orders USING(ID_orders)
							INNER JOIN sl_orders_products USING(ID_orders)
							INNER JOIN sl_orders_payments USING(ID_orders) 	
							WHERE ID_returns = '$id_returns'
								AND sl_orders_products.Status IN ('Active', 'Reship', 'Exchange')
								AND sl_orders_payments.Status IN ('Approved','Denied','Pending','Insufficient Funds','Void','Order Cancelled','Cancelled')
								GROUP BY sl_orders.ID_orders
								ORDER BY sl_orders_payments.Status, sl_orders_products.Status;");
		my ($fp, $paytype, $id_salesorigins) = $sth_p->fetchrow();

		my ($sth) = &Do_SQL("SELECT 
								ID_products_prices
								, Price
								, CONCAT(Price,' - ',Name) 
							FROM sl_products_prices
							WHERE ID_products = '$id_products'
								AND (FP = '$fp' OR FP = 1)
								AND PayType = '$paytype'
								AND (ValidKits IS NULL OR ValidKits = '' OR ValidKits LIKE '%$id_kits%')
								AND (Origins IS NULL OR Origins LIKE '%|$id_salesorigins|%')
								AND Status = 'Active'");
		while(my($id_prod_prices, $price, $name) = $sth->fetchrow()){
			$str .= '{"idpp":"'.$price.'","pname":"'.$name.'"},';
		}

		chop($str);
		$str = '{"resp":['.$str.']}';

		print "Content-type:  application/json\n\n";
		print $str;
	
	}elsif($type =~ /add|drop/) {

		########################################
		########################################
		########################################
		####
		#### 2) Add / Drop Lines To/ From sl_vars
		####
		########################################
		########################################
		########################################

		print "Content-type: text/html\n\n";

		if($type eq 'add' and (!$id_returns or !$data_in) ){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}elsif($type eq 'drop' and !$idri){
			print "Error: " .&trans_txt('reqfields_short');
			return;
		}
		my $str,$str_out,$t;

		if($type eq 'add') {

			########################################
			########################################
			########################################
			####
			#### 2.1) Adding Lines to sl_vars
			####
			########################################
			########################################
			########################################

			#print "Data: $data_in";
			#return;

			my ($this_id, $this_qty, $the_price, $this_shp, $taxmode) = split(/:/, $data_in);
			my @ary_products; my @ary_percents; my $promo; my $total_products; my $percents; my $t;
			$the_price =~ s/\$|,\s//g;
			$this_shp =~ s/\$|,\s//g;


			if(substr($this_id,3) > 100){

				############
				############ 1) Promo?
				############

				my $id_promo = substr($this_id,-6);
				my $sth = &Do_SQL("SELECT 
									(SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName = 'promo". $id_promo ."' )ID_products
									, (SELECT TRIM( BOTH '|' FROM VValue ) FROM sl_vars WHERE sl_vars.VName = 'percent_promo". $id_promo ."' )Percents");
				($promo,$percents) = $sth->fetchrow;
				@ary_products = split(/\|/,$promo);
				$total_products = scalar @ary_products;
				if ($percents){
					@ary_percents = split(/\|/,$percents);
				}

			}
			

			#########
			######### 2) Load Product into array (due to promo possibility)
			#########
			if(!$total_products){
				$total_products = 1;
				push(@ary_products, $this_id);
			}
			#&cgierr("TP:$total_products $percents");

			#########
			######### 2.1) Generate UNIQUE val to link all products
			#########
			my ($sths) = &Do_SQL("SELECT SHA1(CONVERT(NOW(),UNSIGNED INTEGER) + CEIL( RAND( ) * 1000000 ) );");
			my ($ses) = $sths->fetchrow();

			my $this_price = 0; my $this_offer = 0; 
			for(0..$#ary_products){

				#########
				######### 3) Products to insert
				#########
				my $this_line_product = $_;

				($this_line_product > 0) and ($this_shp = 0);
				$this_price = $the_price;
				my $this_tax = 0;
				my $this_shptax = 0;
				my $this_tax_pct = 0;
				$this_offer = length($ary_products[$_]) == 6 ? int(100000000 + $ary_products[$_]) : int($ary_products[$_]);
				my $id_products = length($ary_products[$_]) == 6 ? int($ary_products[$_]) : int( substr($ary_products[$_],-6) );
				my $this_price_type = &load_name('sl_products','ID_products',$id_products,'PriceType');
				

				if ($taxmode eq 'on'){
		
					#############
					############# 3.1) Tax Pct
					#############
					if ($this_offer > 400000000 and $this_offer < 500000000){
						# is an SKU
						$this_tax_pct = &load_name('sl_parts','ID_parts',($this_offer - 400000000),'Sale_Tax')/100;
					}elsif($this_offer < 700000000 and $this_offer > 600000000){
						## is a Service
						$this_tax_pct = &load_name('sl_services','ID_services',($this_offer - 600000000),'Tax')/100;
					}else{
						## is a Product
						$this_tax_pct = &load_name('sl_products','ID_products',substr($this_offer, -6),'TaxAux')/100;
					}

					#############
					############# 3.2) Price Calc
					#############
					if ($percents){
						$this_price = ($ary_percents[$_] == 0) ? 0 : $ary_percents[$_] * $the_price / 100;
					}else{								
						$this_price = $the_price / $total_products;
					}

					#############
					############# 3.3) Tax Calc
					#############
					if($this_price > 0){

						$this_tax = $this_price_type eq 'Gross' ?
							&round( $this_price -  ($this_price / ( 1 + $this_tax_pct) ),$sys{'fmt_curr_decimal_digits'}) :
							&round( $this_price * $this_tax_pct ,$sys{'fmt_curr_decimal_digits'});

						$this_price = &round( $this_price / ( 1 + $this_tax_pct),$sys{'fmt_curr_decimal_digits'}) if($this_price_type eq 'Gross');

					}

					#############
					############# 3.4) ShpTax Pct
					#############
					if ($this_shp > 0 and $cfg{'shptax'} and $cfg{'shptax_percent_default'}){
						
						$this_shptax = lc($cfg{'shptaxtype'}) eq 'gross' ?
							&round( $this_shp -  ($this_shp / ( 1 + $cfg{'shptax_percent_default'}) ),$sys{'fmt_curr_decimal_digits'}) :
							&round( $this_shp * $cfg{'shptax_percent_default'} ,$sys{'fmt_curr_decimal_digits'});

						$this_shp = &round( $this_shp / ( 1 + $cfg{'shptax_percent_default'}),$sys{'fmt_curr_decimal_digits'}) if lc($cfg{'shptaxtype'}) eq 'gross';

					}

				}
				
				######### 656489
				######### 3.1) Insertar Productos con Tax + Shipping (Basarse en e_orders.html.cgi)
				#########
				my $pairs = "$this_offer:$this_price:$this_tax:$this_shp:$this_shptax";
				my $ds = $total_products > 1 ? ", Definition_Sp = '$this_id'" : '';
				for(1..$this_qty){
					my ($sthiv) = &Do_SQL("INSERT INTO sl_vars SET VName = 'Exchange Process', Subcode = '$id_returns', VValue = '$pairs', Definition_En = '$ses' $ds;");
					$t = 1;
				}

			}

			
		}elsif($type eq 'drop'){

			########################################
			########################################
			########################################
			####
			#### 2.2) Dropping Lines from sl_vars
			####
			########################################
			########################################
			########################################

			my ($sth) = &Do_SQL("SELECT Definition_En FROM sl_vars WHERE ID_vars = '$idri';");
			my ($this_ses) = $sth->fetchrow();

			my $modquery = $this_ses ? " OR Definition_En = '$this_ses'" : '';
			my ($sth) = &Do_SQL("DELETE FROM sl_vars WHERE ID_vars = '$idri' $modquery;");
			$t = $sth->rows();
			
		}

		if(!$t and $type eq 'drop') {
			#print "Error: Duplicated Record" if $type eq 'add';
			print "Error: Record Not Dropped" if $type eq 'drop';
			return;
		}


		########################################
		########################################
		########################################
		####
		#### 3) Showing Lines From sl_vars
		####
		########################################
		########################################
		########################################

		$str_out = &get_edit_returns_exchange_lines($id_returns);
		$va{'div_height'} += 70;
		print $str_out;

	}	
	
	return;
}


#############################################################################
#############################################################################
#   Function: search_product_prices
#
#       Es: Busca precios de producto basado en salesorigin + paytype
#       En: Searchs product prices based in salesorigin + paytype
#
#
#    Created on: 05/28/2014  11:39:34
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#   Parameters:
#
#       - 
#		- 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
#
sub search_product_prices{
#############################################################################
#############################################################################


	if($in{'action'}){

		my $modquery;
		my $id_orders = int($in{'id_orders'});
		my $ptype = &load_name('sl_orders','ID_orders',$id_orders,'Ptype');
		my $id_salesorigins = &load_name('sl_orders','ID_orders',$id_orders,'ID_salesorigins');

		if($in{'id_products'}){

			$modquery .= " AND sl_products.ID_products = '$in{'id_products'}'";

		}

		if($in{'keyword'}){

			$modquery .= " AND (sl_products.Name LIKE '%". $in{'keyword'} ."%' OR Model LIKE '%". $in{'keyword'} ."%')";

		}

		my (@c) = split(/,/,$cfg{'srcolors'});
		my $query = "SELECT 
						sl_products.ID_products
						, UPPER(sl_products.Name)
						, sl_products_prices.Name
						, sl_products_prices.Price
						, sl_products_prices.FP
						, sl_products_prices.PayType
						, sl_products_prices.origins
					FROM sl_products_prices INNER JOIN sl_products USING(ID_products)
					WHERE 1 
						AND sl_products.Status = 'On-Air'
						AND (BelongsTo IS NULL OR BelongsTo = '') 
						AND sl_products_prices.PayType = '$ptype'
						AND IF(LENGTH(origins) > 0, origins LIKE('%|$id_salesorigins|%'), 1)
						$modquery 
						ORDER BY FP DESC,Price DESC;";
		my ($sth) = &Do_SQL($query);
		while( my ($id_products, $product_name, $price_name, $price, $fp, $paytype ) = $sth->fetchrow()){

			$d = 1 - $d;
			$va{'pname'} = $in{'keyword'} ? uc($in{'keyword'}) : $product_name;
			$va{'searchresult'} .= qq|<tr bgcolor='$c[$d]'>\n
										<td align="left" class="smalltext">|. &format_sltvid($id_products) .qq|</td>\n
										<td align="left" class="smalltext">$product_name</td>\n
										<td align="left" class="smalltext">$price_name</td>\n
										<td align="center" class="smalltext">$paytype</td>\n
										<td align="center" class="smalltext">$fp</td>\n
										<td align="right" class="smalltext" nowrap>|. &format_price($price) .qq|</td>\n
									</tr>\n|;

		}


	}
	


	print "Content-type: text/html\n\n";
	print &build_page('apporders/search_product_prices.html');

}


#############################################################################
#############################################################################
#   Function: edit_refund_chargeback
#
#       Es: Manejo de chgargebacks desde view_orders
#       En: 
#
#
#    Created on: 05/08/2015  11:39:34
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#    
#    				Last Time Modified by _RB_: Cambia de nombre de edit_chargeback   --> edit_refund_chargeback . Se agrega funcionalidad para trabajar con refunds  
#    				Last Time Modified by _RB_ on 2015/11/03: Funcion puede procesar Contracargos de Ordenes Enviadas|No enviadas + Reembolsos de ordenes No Enviadas.
#
#   Parameters:
#
#       - 
#		- 
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
#
sub edit_refund_chargeback{
#############################################################################
#############################################################################

	my $this_event = $in{'refund'} ? 'refund' : 'chargeback';

	#&cgierr('opr_orders_'. lc($this_event) .'s');
	if(&check_permissions('opr_orders_'. lc($this_event) .'s','','')){

		my $id_orders = int($in{'id_orders'});

		if($in{'action'}){

			#&cgierr('opr_orders_'. lc($this_event) .'s');
			####
			#### 1. Validacion
			####

			## 1.1. Formulario trae lineas de id_orders_products
			my $err = /id_orders_products_/ ~~ %in ? 0 : 1;
			($err) and ($error{'products'} = &trans_txt('required')) and ($va{'er_products'} = qq|background-color:#F0F0A8;font-weight:bold; color:#DC3438|);

			## 1.2 AuthCode
			#(!$in{'authcode'}) and (++$err) and ($error{'authcode'} = &trans_txt('required'));

			## 1.3 Fecha de Banco
			(!$in{'bankdate'}) and ($error{'bankdate'} = &trans_txt('invalid')) and (++$err);

			## 1.4. Lineas de orders products
			my @ary_idop; my $amount_total = 0; my $price_total = 0; my $discount_total = 0; my $shipping_total = 0; my $tax_total = 0; my $this_tax_pct = 0;
			foreach my $key (keys %in) {
			    
			    #$str .= "$key = " . $in{$key} . "\n"; and $in{$key}
				if($key =~ /^id_orders_products_(\d{1,10})$/ ){
					push(@ary_idop, $1);
					$amount_total += round($in{$key},2);
					$price_total += round($in{'id_orders_products_price_' . $1}, 2);
					$discount_total += round($in{'id_orders_products_discount_' . $1}, 2);
					$shipping_total += round($in{'id_orders_products_shipping_' . $1}, 2);
					$tax_total += round($in{'id_orders_products_tax_' . $1}, 2);
					$this_tax_pct = $in{'id_orders_products_taxpct_' . $1} if $in{'id_orders_products_taxpct_' . $1} > 0;
				}

			}

			## 1.5 Tipo de Orden / Status / Productos Enviados
			my $modquery = scalar @ary_idop > 0 ? " AND ID_orders_products IN(". join(',', @ary_idop) .") " : '';
			my ($sth) = &Do_SQL("SELECT 
									sl_orders.Status
									, SUM(IF(ID_orders_parts IS NOT NULL, 1 , 0))AS PartSent
									, SUM(IF(sl_orders_products.ID_products < 600000000,1,0))AS ProductsInOrder
									, SUM(IF(sl_orders_products.ID_products > 600000000,1,0))AS ServicesInOrder 
								FROM 
									sl_orders INNER JOIN sl_orders_products USING(ID_orders) 
									LEFT JOIN sl_orders_parts USING(ID_orders_products) 
								WHERE 
									ID_orders = ". $id_orders ." 
									AND Ptype = 'Credit-Card' 
									AND 0 < (SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders = '". $id_orders ."' $modquery AND Captured='Yes' AND CapDate <> '0000-00-00');");
			my ($this_status, $has_sent, $num_products, $num_services) = $sth->fetchrow();
			(!$this_status) and (++$err) and ($va{'message'} = &trans_txt('opr_orders_chargebacks_nocc'));

			## 1.6. Orden Enviada sin servicio negativo?
			$in{'id_services'} += 600000000 if ($in{'id_services'} and $in{'id_services'} < 600000000);
			if($in{'isshipped'} and !$in{'id_services'}){

				$error{'id_services'} = &trans_txt('required');
				++$err;

			}

			## 1.7. Buscamos servicios para contracargos/reembolsos.
			my ($sth) = &Do_SQL("SELECT Code, Subcode FROM sl_vars_config WHERE Command = 'chargebacks_refunds';");
			my ($id_services_chargeback, $id_services_refund) = $sth->fetchrow();
			if(!$id_services_chargeback){

				$va{'message'} .= "<br>" . &trans_txt('opr_orders_service_chargeback_notfound');
				++$err

			}

			if(!$id_services_refund){

				$va{'message'} .= "<br>" . &trans_txt('opr_orders_service_refund_notfound');
				++$err

			}


			if(!$err){

				$id_services_chargeback += 600000000;
				$id_services_refund += 600000000;
				my $this_id_products = $this_event eq 'chargeback' ? $id_services_chargeback : $id_services_refund;
				####
				#### 2. Aplicacion
				####
				&Do_SQL("START TRANSACTION;");

				my $nrows = 0; my $id_chargebacks = 0;
				if($this_event eq 'chargeback'){

					####
					#### Only Chargeback
					####

					my $modquery = $in{'chargebackto'} ne '' ? " ChargeBackTo = '". &filter_values($in{'chargebackto'}) ."', " : '';
					my ($sth_cb) = &Do_SQL("INSERT INTO sl_chargebacks SET ID_orders = '". $id_orders ."', Description = '". &filter_values($in{'description'}) ."', Amount = '". $amount_total ."', $modquery BankDate = '". &filter_values($in{'bankdate'}) ."', Status = 'Opened', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';");
					$id_chargebacks = $sth_cb->{'mysql_insertid'};

					
					for(0..$#ary_idop){

						my $id_orders_products = $ary_idop[$_];
						my ($sthl) = &Do_SQL("INSERT INTO sl_chargebacks_items SET ID_chargebacks = '". $id_chargebacks ."', ID_orders_products = '". $id_orders_products."', Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';");
						$nrows += $sthl->rows();

					}

				}

				my $id_orders_payments;
				my $batch_active;
				my $flag_accounting;
				my $flag_creditmemos;
				my $this_isshipped_service;
				my $isshipped = $in{'isshipped'} ? 1 : 0; ## Se envia por URL desde el View

				if( ($id_chargebacks and $nrows) or $this_event eq 'refund' ){

					my ($stacc_open,$msg_open,$stacc_close,$msg_close);

					
					&add_order_notes_by_type($id_orders, &trans_txt('opr_orders_'. $this_event .'s_opened') ."\n". &filter_values($in{'description'}) ,"Medium");
					&auth_logging('opr_orders_'. $this_event .'s_opened',$id_orders);
					
					if(!$has_sent and ($num_products or $num_services) ){

						#####################################################################
						#####################################################################
						#####################################################################
						###
						### 2.1. Orden No Enviada (Contracargo/Reembolso)
						###
						#####################################################################
						#####################################################################
						#####################################################################

						my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(DISTINCT sl_warehouses_batches.ID_warehouses_batches) FROM sl_warehouses_batches INNER JOIN sl_warehouses_batches_orders USING(ID_warehouses_batches) WHERE ID_orders_products IN(". join(',', @ary_idop) .") AND sl_warehouses_batches.Status <> 'Void' AND sl_warehouses_batches_orders.Status NOT IN('Cancelled','Error','Returned');");
						$batch_active = $sth->fetchrow();

						
						if(!$batch_active){

							## 2.1.1 Orden Fuera de Remesa | Se puede cancelar por completo en el proceso
							
							## 2.1.1.1. Cancelamos los productos de la orden
							#&Do_SQL("UPDATE sl_orders_products SET Status = 'Inactive' WHERE ID_orders = '". $id_orders ."' AND ID_orders_products IN(". join(',', @ary_idop) .");");
							#my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders = '". $id_orders ."' AND Status NOT IN('Returned','Order Cancelled','Inactive');");
							#my ($pactive) = $sth->fetchrow();
							my $pactive = 0 if !$pactive;
							my ($sth) = &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders = '". $id_orders."' AND Status = 'Active' ORDER BY ID_orders_products DESC LIMIT 1;");
							my ($id_orders_products) = $sth->fetchrow();
							my (%overwrite) = ('saleprice' => ($amount_total * -1), 'id_products' => $this_id_products ,'related_id_products' => '', 'id_products_prices' => '', 'shipping' => '0.00', 'cost' => '00.00', 'tax' => '00.00', 'tax_percent' => '0.00', 'discount' => '00.00', 'fp' => 1, 'shpdate' => '0000-00-00', 'shptax' => '00.00', 'shptax_percent' => '0.00', 'posteddate' => '0000-00-00', 'upsell' => 'No', 'status' => 'returned');
							my $applied_product = &Do_selectinsert('sl_orders_products', "ID_orders_products = '$id_orders_products'", "", "", %overwrite);
							&Do_SQL("UPDATE sl_orders_products SET ShpDate = CURDATE(), PostedDate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."' WHERE ID_orders_products = '". $applied_product ."';");
			

							my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '". $id_orders."' AND LENGTH(PmtField3) >= 13 AND Captured = 'Yes' AND CapDate <> '0000-00-00' AND LENGTH(AuthCode) >=2 AND AuthCode <> '0000'  AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit') ORDER BY ID_orders_payments DESC LIMIT 1;");
							$id_orders_payments = $sth->fetchrow();
							my $applied_payment;

							if($id_orders_payments){

								## 2.1.1.2. Agregamos pago como credito para cancelar el deposito recibido
								my $this_even_query = $this_event eq 'refund' ? '' : "Captured = 'Yes', CapDate = '". $in{'bankdate'}."',";
								my (%overwrite) = ('amount' => ($amount_total * -1), 'pmtfield8' => '1' ,'authcode' => '', 'authdatetime' => '', 'captured' => 'No', 'capdate' => '0000-00-00', 'status' => 'Credit', 'reason' => $this_event);
								$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '$id_orders_payments'", "", "", %overwrite);
								&Do_SQL("UPDATE sl_orders_payments SET Amount = ($amount_total * -1), Paymentdate = CURDATE(), ". $this_even_query ." Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders = '". $id_orders ."' AND ID_orders_payments = '". $applied_payment ."';");

								if($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1){
									my $id_payments = $applied_payment;
									my $id_pcd = &load_name("sl_orders_cardsdata", "ID_orders_payments", $id_orders_payments, "ID_orders_cardsdata");									
									&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders,ID_orders_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users) 
											 SELECT ID_orders,$id_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users FROM sl_orders_cardsdata WHERE ID_orders_cardsdata = $id_pcd;");
								}

								## 2.1.1.3. Contabilidad
								my ($order_type, $ctype, $ptype,@params);
								my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $id_orders ."';");
								($order_type, $ctype) = $sth->fetchrow();
								@params = ($id_orders, $applied_payment, 1, $this_event, $isshipped);
								($stacc_open,$msg_open) = &accounting_keypoints('order_chargeback_open_'. $ctype .'_'. $order_type , \@params);
								$flag_accounting += $stacc_open;
								$va{'message'} .= "<br>". $msg_open;
								sleep(1);
								($stacc_close,$msg_close) = &accounting_keypoints('order_chargeback_close_'. $ctype .'_'. $order_type , \@params);
								#$flag_accounting += $stacc_close;
								#$va{'message'} .= "<br>". $msg_close;
								#&cgierr($flag_accounting);

								## 2.1.1.3. Nota | Login | Cierre de Chaergeback
								&Do_SQL("UPDATE sl_orders SET Status = IF(". $pactive ." > 0,Status,'Cancelled'), StatusPrd = 'None', StatusPay = IF('". $this_event ."' = 'refund', 'Pending Refund', 'None') WHERE ID_orders = '". $id_orders ."';");								
								&add_order_notes_by_type($id_orders,&trans_txt('opr_orders_'. $this_event .'s_closed'),"Low");
								&auth_logging('opr_orders_'. $this_event .'s_closed',$id_orders);
								&Do_SQL("UPDATE sl_chargebacks SET Status = 'Paid' WHERE ID_chargebacks = '". $id_chargebacks ."';") if $this_event eq 'chargeback';

							}

						}

					}else{

						#####################################################################
						#####################################################################
						#####################################################################
						###
						### 2.2. Orden Enviada (Contracargo de Orden Enviada no Recuperada)
						###
						#####################################################################
						#####################################################################
						#####################################################################

						## 2.2.1. Insertamos pago negativo capturado
						my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = '". $id_orders."' AND LENGTH(PmtField3) >= 13 AND Captured = 'Yes' AND CapDate <> '0000-00-00' AND LENGTH(AuthCode) >=2 AND AuthCode <> '0000'  AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit') ORDER BY ID_orders_payments DESC LIMIT 1;");
						$id_orders_payments = $sth->fetchrow();
						my $applied_payment;

						if($id_orders_payments){

							## 2.2.3.1. Agregamos pago como credito para cancelar el deposito recibido
							my $this_even_query = $this_event eq 'refund' ? '' : "Captured = 'Yes', CapDate = '". $in{'bankdate'}."',";
							my (%overwrite) = ('amount' => ($amount_total * -1), 'pmtfield8' => '1' ,'authcode' => '', 'authdatetime' => '', 'captured' => 'No', 'capdate' => '0000-00-00', 'status' => 'Credit', 'reason' => $this_event);
							$applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '$id_orders_payments'", "", "", %overwrite);
							&Do_SQL("UPDATE sl_orders_payments SET Amount = ($amount_total * -1), Paymentdate = CURDATE(), ". $this_even_query ." PostedDate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders = '". $id_orders ."' AND ID_orders_payments = '". $applied_payment ."';");

							if($cfg{'encrypt_cc'} and $cfg{'encrypt_cc'} == 1){
								my $id_payments = $applied_payment;
								my $id_pcd = &load_name("sl_orders_cardsdata", "ID_orders_payments", $id_orders_payments, "ID_orders_cardsdata");									
								&Do_SQL("INSERT INTO sl_orders_cardsdata(ID_orders,ID_orders_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users) 
										 SELECT ID_orders,$id_payments,card_number,card_date,card_cvn,Date,Time,ID_admin_users FROM sl_orders_cardsdata WHERE ID_orders_cardsdata = $id_pcd;");
							}

							## 2.2.2. Credit Note
							my $id_customers = &load_name('sl_orders','ID_orders',$id_orders,'ID_customers');
							my ($sth_cm) = &Do_SQL("INSERT INTO sl_creditmemos SET ID_customers = '". $id_customers ."', Reference = '". $id_chargebacks ."', Description = '". &trans_txt('opr_orders_chargebacks_creditmemo_new') ."', Status = 'Applied', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
							my $id_creditmemos = $sth_cm->{'mysql_insertid'};
							### Shp-Tax
							my $return_shp_tax = 0; my $return_shp_tax_pct = 0;
							if( $shipping_total > 0 ){
								$return_shp_tax_pct = ($cfg{'shptax_percent_default'}) ? $cfg{'shptax_percent_default'} : 0.16;
								$return_shp_tax = round($shipping_total * $return_shp_tax_pct, 2);

								$tax_total -= $return_shp_tax if( $tax_total > 0 );
							}
							&Do_SQL("INSERT INTO sl_creditmemos_products SET ID_products = '". int($in{'id_services'}) ."', ID_creditmemos = '". $id_creditmemos ."', Quantity = 1,  SalePrice = '". $price_total ."', Discount = '". $discount_total ."', Shipping = '". $shipping_total ."', Tax = '". $tax_total ."', Tax_percent = ". ($this_tax_pct * 100) .", Cost = '0', Cost_Adj = '0', ShpDate = CURDATE(), ShpTax = '". $return_shp_tax ."', ShpTax_percent = '". ($return_shp_tax_pct * 100) ."', Status = 'Active', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
							&Do_SQL("INSERT INTO sl_creditmemos_payments SET ID_creditmemos = '". $id_creditmemos ."', ID_orders = '". $id_orders ."', ID_orders_payments = 0, ID_orders_payments_added = '". $applied_payment ."', ID_orders_products_added = '". $id_orders_products ."', Amount = '". ($price_total - $discount_total + $shipping_total + $tax_total) ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

							if ($id_creditmemos){ 

								my ($message, $status, $id_invoices) = &export_info_for_credits_notes($id_creditmemos);
								$flag_creditmemos = 1 if !$id_invoices;

							}

							my ($sth_cop) = &Do_SQL("SELECT COUNT(*) + 1 FROM sl_orders_products WHERE ID_orders = '". $id_orders ."' AND RIGHT(ID_products,6) = 800000;");
							my ($new_line) = $sth_cop->fetchrow();

							## 2.2.3. Insertamos Servicio						
							my ($sth_op) = &Do_SQL("INSERT INTO sl_orders_products SET ID_orders = '". $id_orders ."', ID_products = '". (800000000 + $new_line) ."', ID_packinglist = 0, Related_ID_products = '". $id_creditmemos ."', Quantity = 1, SalePrice = '". ($price_total * -1) ."', Discount = '". ($discount_total * -1) ."', Shipping = '". ($shipping_total * -1) ."', Tax = '". ($tax_total * -1) ."', Tax_percent = ". $this_tax_pct .", ShpTax = '0', ShpTax_percent = '0', PostedDate = CURDATE(), Upsell = 'No', Status = 'Returned', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';");
							$this_isshipped_service = $sth->{'mysql_insertid'};


							## 2.2.4. Contabilidad
							my ($order_type, $ctype, $ptype,@params);
							my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $id_orders ."';");
							($order_type, $ctype) = $sth->fetchrow();
							@params = ($id_orders, $applied_payment, 1, $this_event, $isshipped);
							($stacc_open,$msg_open) = &accounting_keypoints('order_chargeback_open_'. $ctype .'_'. $order_type , \@params);
							$flag_accounting += $stacc;
							sleep(1);
							($stacc_close,$msg_close) = &accounting_keypoints('order_chargeback_close_'. $ctype .'_'. $order_type , \@params);
							#$flag_accounting += $stacc;

							## 2.2.3.3. Nota | Login | Cierre de Chargeback
							&Do_SQL("UPDATE sl_orders SET StatusPrd = 'None', StatusPay = 'None' WHERE ID_orders = '". $id_orders ."';");
							
							&add_order_notes_by_type($id_orders,&trans_txt('opr_orders_'. $this_event .'s_closed'),"Low");
							&auth_logging('opr_orders_'. $this_event .'s_closed',$id_orders);
							&Do_SQL("UPDATE sl_chargebacks SET Status = 'Paid' WHERE ID_chargebacks = '". $id_chargebacks ."';") if $this_event eq 'chargeback';

						}


					}

					## 2.3 Validaciones finales
					if($flag_creditmemos){

						## Problema encontrado al generar la nota de credito fiscal
						&Do_SQL("ROLLBACK;");
						$va{'message'} = &trans_txt('opr_orders_chargebacks_noinvoice');
						$va{'style_message'} = qq|line-height:30px;background-color:#F0F0A8; font-size:20px; font-weight:bold; color:#DC3438|

					}elsif($flag_accounting){

						## Problema encontrado en contabilidad
						&Do_SQL("ROLLBACK;");
						$va{'message'} = &trans_txt('acc_error') . $va{'message'};
						$va{'style_message'} = qq|line-height:30px;background-color:#F0F0A8; font-size:20px; font-weight:bold; color:#DC3438|

					}elsif(!$id_orders_payments and !$has_sent and !$batch_active){

						## No se encontro el pago original
						&Do_SQL("ROLLBACK;");
						$va{'message'} = &trans_txt('opr_orders_chargebacks_nopayment');
						$va{'style_message'} = qq|line-height:30px;background-color:#F0F0A8; font-size:20px; font-weight:bold; color:#DC3438|

					}elsif(!$has_sent and $batch_active){

						## Orden en Remesa
						&Do_SQL("ROLLBACK;");
						$va{'message'} = &trans_txt('opr_orders_chargebacks_activebacth') . $batch_active;
						$va{'style_message'} = qq|line-height:30px;background-color:#F0F0A8; font-size:20px; font-weight:bold; color:#DC3438|

					}elsif(lc($stacc_open) eq 'error' or lc($stacc_close) eq 'error'){

						## Movimientos Contables
						&Do_SQL("ROLLBACK;");
						$va{'message'} = &trans_txt('opr_orders_chargebacks_erraccounting') . '<br>' . $msg_open . '<br>' . $msg_close;
						$va{'style_message'} = qq|line-height:30px;background-color:#F0F0A8; font-size:20px; font-weight:bold; color:#DC3438|

					}else{

						## Todo OK. Se aplican operaciones
						&Do_SQL("COMMIT;");
						$va{'message'} = &trans_txt('done');
						$va{'div_chargebackinfo'} = qq|display:none|;
						$va{'style_message'} = qq|line-height:30px;background-color:#7CBF7C; font-size:20px; font-weight:bold; color:#214121|

					}

				}else{

					####
					#### 3. No se inserto el chargeback
					####
					&Do_SQL("ROLLBACK;");
					$va{'style_message'} = qq|line-height:30px;background-color:#F0F0A8; font-size:20px; font-weight:bold; color:#DC3438|;
					$va{'message'} = &trans_txt('opr_orders_chargebacks_nochargeback');

				}
			
			} ## Fin no error

		} ## Fin action
		
		my ($sth) = &Do_SQL("SELECT 
								sl_orders_products.ID_orders_products
								, sl_orders_products.ID_products
								, SalePrice
								, sl_orders_products.Discount
								, Shipping
								, sl_orders_products.Tax
								, ShpTax
								, Tax_percent
								, IF(sl_orders_parts.ShpDate IS NULL,IF(sl_orders_products.ShpDate IS NULL, 'N/A',sl_orders_products.ShpDate), sl_orders_parts.ShpDate) AS ShpDate
								, IF(sl_products.Name IS NULL, IF(sl_services.Name IS NULL , 'Service', sl_services.Name) ,sl_products.Name) AS Name
								, choice1
								, choice2
								, choice3
								, sl_orders_products.Quantity
								, sl_orders_products.Status
							FROM sl_orders_products
							LEFT JOIN sl_services ON sl_orders_products.ID_products = 600000000 + sl_services.ID_services
							LEFT JOIN sl_skus ON sl_orders_products.ID_products = ID_sku_products
							LEFT JOIN sl_orders_parts USING(ID_orders_products) 
							LEFT JOIN sl_products ON sl_products.ID_products = RIGHT(sl_orders_products.ID_products,6) 
							WHERE 
								ID_orders = '$id_orders'
								AND sl_orders_products.Status IN('Active','Exchange','ReShip')
								AND 1 > (
											SELECT 
												COUNT(*) 
											FROM 
												sl_chargebacks INNER JOIN sl_chargebacks_items USING(ID_chargebacks) 
											WHERE 
												sl_chargebacks_items. ID_orders_products = sl_orders_products.ID_orders_products
												AND sl_chargebacks.Status <> 'Denied'
												AND sl_chargebacks_items.Status = 'Active'
										)
							GROUP BY sl_orders_products.ID_orders_products
							ORDER BY sl_orders_parts.ShpDate <> NULL, sl_orders_products.ID_orders_products;");

		while (my ($id_orders_products, $id_products, $sprice, $this_discount, $this_shipping, $this_tax, $shptax, $this_tax_pct, $shpdate, $pname, $c1, $c2, $c3, $quantity, $this_status ) = $sth->fetchrow() ){

			$pname .= ' ' . $c1 . ' ' . $c2 . ' ' . $c3;
			my $this_amount = round($sprice + $this_shipping + $this_tax + $shptax - $this_discount, 2);
			my $this_ftax = round($this_tax + $shptax, 2);
			$va{'searchresult'} .= qq|<tr>\n|;

			$va{'searchresult'} .= qq|   <td class='smalltext' valign='top' nowrap align="center"><input type="checkbox" checked="checked" class="checkbox" id="id_orders_products_|. $id_orders_products .qq|" name="id_orders_products_|. $id_orders_products .qq|" value="|. $this_amount .qq|">\n|;
			$va{'searchresult'} .= qq|   <input type="hidden" id="id_orders_products_price_|. $id_orders_products .qq|" name="id_orders_products_price_|. $id_orders_products .qq|" value="|. round($sprice,2) .qq|">\n|;
			$va{'searchresult'} .= qq|   <input type="hidden" id="id_orders_products_discount_|. $id_orders_products .qq|" name="id_orders_products_discount_|. $id_orders_products .qq|" value="|. round($this_discount,2) .qq|">\n|;
			$va{'searchresult'} .= qq|   <input type="hidden" id="id_orders_products_shipping_|. $id_orders_products .qq|" name="id_orders_products_shipping_|. $id_orders_products .qq|" value="|. $this_shipping .qq|">\n|;
			$va{'searchresult'} .= qq|   <input type="hidden" id="id_orders_products_tax_|. $id_orders_products .qq|" name="id_orders_products_tax_|. $id_orders_products .qq|" value="|. $this_ftax .qq|">\n|;
			$va{'searchresult'} .= qq|   <input type="hidden" id="id_orders_products_taxpct_|. $id_orders_products .qq|" name="id_orders_products_taxpct_|. $id_orders_products .qq|" value="|. $this_tax_pct .qq|">\n|;
			$va{'searchresult'} .= qq|   <td class='smalltext' valign='top' nowrap align="left">|. &format_sltvid($id_products) .qq|</td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $pname .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $quantity .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $shpdate .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="left"><b>|. $this_status .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($sprice) .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b style="color:#C52525;">|. &format_price($this_discount) .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($this_shipping) .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($this_tax + $shptax) .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="right"><b>|. &format_price($this_amount) .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|</tr>\n|;
			$amount += round($sprice,2);
			$tax += round($this_tax + $shptax,2);
			$amount_total += round($this_shipping,2);
		
		}
		$amount_total += ($amount + $tax);


		if(!$va{'searchresult'}){

			$va{'searchresult'} .= qq|<tr>\n|;
			$va{'searchresult'} .= qq|	 <td class='smalltext' valign='top' nowrap align="center" colspan="11"><b>|. &trans_txt('opr_orders_chargebacks_no_products_available') .qq|</b></td>\n|;
			$va{'searchresult'} .= qq|</tr>\n|;

		}else{

				$va{'searchresult'} .= qq|<tr>
											<td class="menu_bar_title" colspan="10">&nbsp;</td>\n
											<td class="menu_bar_title" align="right" style="background-color:#1e90ff;font-weight:bolder;><label id="lbl_amount_total" style=";"> |. &format_price($amount_total) .qq|</label></td>\n
										</tr>|;

		}

		
	}else{
		
		
	}
	$va{'this_event'} = $this_event eq 'refund' ? 'Refund' : 'Chaergeback';
	$va{'this_event_style'} = $this_event eq 'refund' ? 'visibility:collapse;' : 'visibility:visible;';
	$va{'isshipped_style'} = !$in{'isshipped'} ? 'visibility:collapse;' : 'visibility:visible;';
	$va{'isshipped_chargeback_info'} = &trans_txt('opr_orders_chargebacks_isshipped');
	$va{'isshipped_chargeback_info_notok'} = &trans_txt('opr_orders_chargebacks_isshipped_notok');
	$in{'bankdate'} = &get_sql_date() if !$in{'bankdate'};


	print "Content-type: text/html\n\n";
	print &build_page('apporders/add_chargeback.html');

}

sub get_customers_addresses{

	my ($options);

	if ($in{'id_customers'}){
		$options = &build_select_customers_address($in{'id_customers'});
	}
	
	print "Content-type: text/html\n\n";
	print $options;

}

sub get_customers_address2{

	my ($options);

	if ($in{'id_customers'}){
		$options = &build_select_customers_address2($in{'id_customers'});
	}
	print "Content-type: text/html\n\n";
	print $options;
}


sub order_add_shipping{

	my %config_values_prices = (
		'cod',	{1,'shipment_cod_standard',2,'shipment_cod_express',3,'shipment_cod_cod'}, 
		'credit-card',	{1,'shipment_cc_standard',2,'shipment_cc_express',3,'shipment_cc_cod' },
		'referenced deposit',	{1,'shipment_rd_standard',2,'shipment_rd_express',3,'shipment_rd_cod' }
	);
	use Data::Dumper;
	my ($sth) = &Do_SQL("SELECT shp_type,Ptype FROM sl_orders WHERE ID_orders='$in{'id_orders'}'");
	my ($shp_type,$Ptype) = $sth->fetchrow;
	$total_shp = $cfg{$config_values_prices{lc($Ptype)}{$shp_type}};
	print "Content-type:  application/json\n\n";
	print '{"code":"200","total":"'.$total_shp.'.00"}';

}



#############################################################################
#############################################################################
#   Function: user_notes
#
#       Es: Manejo de notas del usuario
#       En: 
#
#
#    Created on: 21/10/2015  12:22:00
#
#    Author: Fabián Cañaveral
#
#    Modifications:
#    
#    				
#
#   Parameters:
#
#       - ID_admin_users
#		- Note
#		- Type
#		
#
#  Returns:
#
#      - HTML -> for show Notes 
#      - Status -> save note.
#
#   See Also:
#
#      
#
#
sub user_notes{
#############################################################################
#############################################################################
	
	if($in{'type'} and $in{'type'} eq 'note'){
		print "Content-type:  text/html\n\n";
		$va{'form_action'} = "/cgi-bin/common/apps/ajaxbuild?ajaxbuild=user_notes&id_admin_users=$usr{'id_admin_users'}";
		my ($sth) = &Do_SQL("select notes from cu_notepad where ID_admin_users='".$usr{'id_admin_users'}."'");
		$rs = $sth->fetchrow;
		$va{'id_admin_users'} = $usr{'id_admin_users'};
		$va{'user_notes'}=$rs;
		print &build_page('ajaxbuild/user_notes.html');
	}elsif($in{'type'} and $in{'type'} eq 'save'){
		my ($sth) = &Do_SQL("select count(*) total from cu_notepad where ID_admin_users='".$usr{'id_admin_users'}."'");
		$rs = $sth->fetchrow;
		if($rs > 0){
			&Do_SQL("update cu_notepad set ID_admin_users='$usr{'id_admin_users'}', notes='".$in{'notes'}."', Last_update=now() where ID_admin_users='".$usr{'id_admin_users'}."'");
		}else{
			&Do_SQL("insert into cu_notepad (ID_admin_users,notes,Last_update) values('$usr{'id_admin_users'}','".$in{'notes'}."',now())");
		}
		print "Content-type:  application/json\n\n";
		print '{"code":"200","msg":'.$rs.'}';
	}

}


#############################################################################
#############################################################################
#   Function: express_delivery_applies
#
#       Es: Valida si un CP aplica para Express Delivery
#       En: Validate ZipCode to Express Delivery
#
#
#    Created on: 24/09/2015  16:03:10
#
#    Author: Jonathan Alcantara Martinez
#    Modifications:
#
#        -
#
#   Parameters:
#
#       -
#
#   See Also:
#
sub express_delivery_applies {
#############################################################################
#############################################################################

	print "Content-type: text/html\n\n";
	print &validate_express_delivery($in{'shp_zip'});

}

sub billingcontrol{
## --------------------------------------------------------
	print "Content-type: text/html\n\n";
	$opt = $in{'rdooption'};	

	my ($sth) = &Do_SQL('UPDATE sl_vars SET VValue='.$opt.' WHERE VName="billingstat"');

	my $message = ( $opt eq "0") ? "Disable" : "Enable";
	$sql_log = "LogDate=CURDATE(), LogTime=CURTIME(), ID_admin_users='$usr{'id_admin_users'}', tbl_name='sl_vars',Logcmd='$in{'ajaxbuild'}', Type='Application', application='admin', Message='$message', Action='0', IP='" . &get_ip . "'";
	&Do_SQL("INSERT INTO admin_logs SET ".$sql_log);
}


#############################################################################
#############################################################################
#   Function: customer_ar_debtcancellation
#				
#       Es: Muestra y procesa invoices para cancelar saldo
#       En: 
#
#
#    Created on: 02/12/2017  12:20:10
#
#    Author: RB
#
#    Modifications:
#
#    Parameters:
#
#		
#  Returns:
#
#      - List of invoices able to debt cancellation
#
#   See Also:
#
#	</cgi-bin/common/subs/sub.func.html.cgi -> func_customers_ar>>
#
sub customer_ar_debtcancellation {
#############################################################################
#############################################################################


	if($in{'action'}){

		#&cgierr();
		$va{'message'} = '';
		foreach my $key (keys %in) {
			    
		   	## Looking for orders to debt cancel
			if($key =~ /^id_orders_(\d{1,10})$/ ){

				## Order found
				my $id_orders = int($1);
				my $this_amount = $in{'id_orders_' . $id_orders};
				
				if($id_orders and $this_amount){

					my $this_acc; my $this_acc_str; my $flag_accounting;
					$va{'this_accounting_time'} = time();

					&Do_SQL("START TRANSACTION");
					my ($sth) = &Do_SQL("SELECT ID_orders_payments FROM sl_orders_payments WHERE ID_orders = ". $id_orders ." AND ABS(Amount - '". $this_amount ."') < 0.5 AND (Captured <> 'Yes' OR Captured IS NULL) AND (CapDate = '0000-00-00' OR CapDate IS NULL) ORDER BY ABS(Amount - '". $this_amount ."') LIMIT 1;");
					my ($id_orders_payments) = $sth->fetchrow();
					
					if($id_orders_payments){

						my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET PmtField1 = '". &trans_txt('acc_amount_difference') ."', Amount = '". $this_amount ."', Captured = 'Yes', CapDate = CURDATE(), AuthCode = FLOOR(RAND() * 4000) + 1000 WHERE ID_orders_payments = ". $id_orders_payments .";");
						my $lid = $sth2->rows();

						if($lid){

							## Accounting Keypoints
							my ($order_type, $ctype, $ptype,@params);
							my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = ". $id_orders .";");
							($order_type, $ctype) = $sth->fetchrow();
							$ptype = get_deposit_type($id_orders_payments,'');
							@params = ($id_orders, $id_orders_payments,-1,1);


							if($order_type and $ctype and $ptype){

								## Movimientos Contables		
								my ($this_acc, $this_acc_str) = &accounting_keypoints('order_deposit_'. $ctype .'_'. $order_type .'_'. $ptype, \@params);
								$flag_accounting++ if $this_acc;


								if(!$flag_accounting){

									&Do_SQL("INSERT INTO sl_orders_notes SET ID_orders = ". $id_orders .", Notes = '". &trans_txt('opr_orders_payment_captured') ." : ". $this_amount ."', Type = 'LOW', Date=CURDATE(), Time=CURTIME(), ID_admin_users=".$usr{'id_admin_users'}.";");
									&Do_SQL("COMMIT");

									## Log
									$in{'db'} = "sl_orders";
									&auth_logging('orders_payments_updated',$id_orders);
									$va{'message'} .= '<li>ID: ' . $id_orders . ' ' . &trans_txt('done') . '</li>';

								}else{

									## Orden con Problema de datos requeridos
									&Do_SQL("ROLLBACK");
									$va{'message'} .= '<li>' . $id_orders . ' ' . &trans_txt('acc_general') . ' - ' .$this_acc .'</li>';

								}

							}else{

								## Orden con Problema de datos requeridos
								&Do_SQL("ROLLBACK");
								$va{'message'} .= '<li>ID: ' . $id_orders . ' ' . &trans_txt('acc_general') . '</li>';

							}

						}else{

							## No se actualizo el payment
							&Do_SQL("ROLLBACK");
							va{'message'} .= '<li>ID: ' . $id_orders . ' ' . &trans_txt('error') . '<li>';

						}

					}

				}

			}

		}

	}


	$va{'result_list'};

	## Customer Invoices
	my $this_query = get_customers_ar_debtcancellation('query');
	my ($sth) = &Do_SQL($this_query);

	while(my($id_invoices, $id_orders, $invoice, $mdate, $amt_total, $amt_due) = $sth->fetchrow()){

		## Build List with checkboxes
		$va{'result_list'} .= qq|<tr id="row-$id_orders">\n
								<td><input type="checkbox" class="checkbox" style="cursor:pointer" id="id_orders_|. $id_orders .qq|" name="id_orders_|. $id_orders .qq|" value="|. $amt_due .qq|"></td>\n
								<td>$id_orders</td>\n 
								<td>$invoice</td>\n 
								<td align="right">|. &format_price($amt_total).qq|</td>\n 
								<td align="right">|. &format_price($amt_due).qq|</td>\n 
							</tr>|;

	}
	

	print "Content-type: text/html\n\n";
	print &build_page('ajaxbuild:customer_debtcancellation.html');

}


1;

