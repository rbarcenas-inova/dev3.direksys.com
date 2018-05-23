##########################################################
##		WAREHOUSE RECEIPT	  ##
##########################################################
sub loaddefault_mer_wreceipts {
# --------------------------------------------------------
	$in{'status'} = 'New';
	return $err;
}
sub loading_mer_wreceipts {
# --------------------------------------------------------
	## Load Vendor Info & Currency Info
	if ($in{'id_vendors'}>0){
		my ($sth) = &Do_SQL("SELECT CompanyName, Currency, Category FROM sl_vendors WHERE ID_vendors=$in{'id_vendors'}");
		($va{'vendor_name'},$va{'vendor_currency'},$va{'vendor_category'}) = $sth->fetchrow_array();
	}

	if ($va{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'}){
		$va{'currency'} = &format_price(&load_name('sl_exchangerates','ID_exchangerates',$in{'id_exchangerates'},'exchange_rate')) if ($in{'id_exchangerates'}>0);
		$va{'curstyle'} = '';
	}else{
		$va{'currency'} = 'b';
		$va{'curstyle'} = qq|style="display:none;"|;
	}
}

sub validate_mer_wreceipts {
# --------------------------------------------------------
	my ($err);
	if ($in{'edit'} and $in{'status'} eq 'Processed'){
		$in{'view'}=$in{'id_wreceipts'};
		$va{'message'} = &trans_txt('wreceipt_notedit');
		&html_view_record;
		exit;
	}
	
	my $id_vendors = int($in{'id_vendors'});
	my $id_purchaseorders = int($in{'id_purchaseorders'});
	
	if($id_vendors != 0 and $id_purchaseorders != 0) {
		my $id_vendors_ok = &load_name('sl_purchaseorders','ID_purchaseorders',$id_purchaseorders,'ID_vendors');
		if($id_vendors_ok != $id_vendors) {
			$va{'vendors_no_match'} = &trans_txt('wreceipt_vendors_no_match');
			$err++;

		}
	}

	if($id_purchaseorders != 0) {
		my $id_vendors = &load_name('sl_purchaseorders','ID_purchaseorders',$id_purchaseorders,'ID_vendors');
		$in{'id_vendors'} = $id_vendors;
	}
	

	### PO Open?
	if($id_purchaseorders) {
		my ($sth) = &Do_SQL("SELECT IF(SUM(sl_purchaseorders_items.Received) < SUM(Qty) AND Status = 'In Process', 1,0) FROM sl_purchaseorders LEFT JOIN sl_purchaseorders_items USING(ID_purchaseorders) WHERE sl_purchaseorders.ID_purchaseorders = '".$id_purchaseorders."' GROUP BY sl_purchaseorders.ID_purchaseorders;");
		my ($po_opened) = $sth->fetchrow();

		if(!$po_opened) {
			$error{'status'} = &trans_txt('mer_po_blocked_rs');
			++$err;
		}

	}

	return $err;
}

sub view_mer_wreceipts {
# --------------------------------------------------------

	if ($in{'chg_in_process'}==1 and  $in{'status'} eq 'New'){
		&Do_SQL("UPDATE sl_wreceipts SET Status='In Process' WHERE ID_wreceipts = '$in{'id_wreceipts'}' LIMIT 1;");
		$in{'db'} = "sl_wreceipts";
		&auth_logging('mer_wreceipts_chg_in_process',$in{'id_wreceipts'});
		$va{'message'} = &trans_txt('mer_wreceipts_chg_in_process');

		## Status
		$in{'status'} = 'In Process';
	}

	## Cancel WR
	if($in{'cancel'}) {
		if ($in{'status'} eq 'In Process') {

			&Do_SQL("UPDATE sl_wreceipts SET Status='Cancelled' WHERE ID_wreceipts = '$in{'id_wreceipts'}' LIMIT 1;");
			$in{'db'} = "sl_wreceipts";
			&auth_logging('mer_wreceipts_cancelled',$in{'id_wreceipts'});
			$va{'message'} = &trans_txt('mer_wreceipts_cancelled');
			
			## Status
			$in{'status'} = 'Cancelled';
		}
	}
	
	## Update items info
	if ($cfg{'use_customs_info'} and $cfg{'use_customs_info'}==1 and $in{'update'}==1 and ($in{'status'} eq 'New' or $in{'status'} eq 'In Process')){
		my $log='';
		&Do_SQL("START TRANSACTION");
		$log .= "START TRANSACTION<br>\n";

		my $sql ="SELECT ID_wreceipts_items, ID_customs_info FROM sl_wreceipts_items WHERE ID_wreceipts = '$in{'id_wreceipts'}';";
		$log .= $sql."<br>\n";
		my ($sth) = &Do_SQL($sql);
		while (my $rec = $sth->fetchrow_hashref){
			my $add_sql = ($in{'import_declaration_number_'.$rec->{'ID_wreceipts_items'}})?" AND cu_customs_info.import_declaration_number='".$in{'import_declaration_number_'.$rec->{'ID_wreceipts_items'}}."' ":"";
			$add_sql .= ($in{'import_declaration_date_'.$rec->{'ID_wreceipts_items'}})?" AND cu_customs_info.import_declaration_date='".$in{'import_declaration_date_'.$rec->{'ID_wreceipts_items'}}."' ":"";
			$add_sql .= ($in{'customs_'.$rec->{'ID_wreceipts_items'}})?" AND cu_customs_info.customs='".$in{'customs_'.$rec->{'ID_wreceipts_items'}}."' ":"";
			$add_sql .= ($in{'id_customs_broker_'.$rec->{'ID_wreceipts_items'}})?" AND cu_customs_info.ID_vendors='".$in{'id_customs_broker_'.$rec->{'ID_wreceipts_items'}}."' ":"";
			
			if( $in{'import_declaration_number_'.$rec->{'ID_wreceipts_items'}} and $in{'import_declaration_date_'.$rec->{'ID_wreceipts_items'}} and $in{'customs_'.$rec->{'ID_wreceipts_items'}} ){
				$sql = "SELECT ID_customs_info FROM cu_customs_info WHERE 1 $add_sql LIMIT 1;";
				$log .= $sql."<br>\n";
				my ($sth_customs_info) = &Do_SQL($sql);
				my $id_customs_info = $sth_customs_info->fetchrow_array();

				if (!$id_customs_info){

					$sql = "INSERT INTO cu_customs_info SET 
					ID_wreceipts='".$in{'id_wreceipts'}."'
					, import_declaration_number='".$in{'import_declaration_number_'.$rec->{'ID_wreceipts_items'}}."'
					, import_declaration_date='".$in{'import_declaration_date_'.$rec->{'ID_wreceipts_items'}}."'
					, customs='".$in{'customs_'.$rec->{'ID_wreceipts_items'}}."'
					, ID_vendors='".$in{'id_customs_broker_'.$rec->{'ID_wreceipts_items'}}."'
					, Status='Active'
					, Date=CURDATE()
					, Time=CURTIME()
					, ID_admin_users='".$usr{'id_admin_users'}."';";
					$log .= $sql."<br>\n";
					my ($sth_customs) = &Do_SQL($sql);
					$new_id_customs_info = $sth_customs->{'mysql_insertid'};

					$sql = "UPDATE sl_wreceipts_items SET ID_customs_info='".$new_id_customs_info."' WHERE ID_wreceipts_items='".$rec->{'ID_wreceipts_items'}."' LIMIT 1;";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);

				}else{
					$sql = "UPDATE cu_customs_info SET 
					ID_wreceipts='".$in{'id_wreceipts'}."'
					, import_declaration_number='".$in{'import_declaration_number_'.$rec->{'ID_wreceipts_items'}}."'
					, import_declaration_date='".$in{'import_declaration_date_'.$rec->{'ID_wreceipts_items'}}."'
					, customs='".$in{'customs_'.$rec->{'ID_wreceipts_items'}}."'
					, ID_vendors='".$in{'id_customs_broker_'.$rec->{'ID_wreceipts_items'}}."'
					WHERE ID_customs_info='".$id_customs_info."';";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);

					$sql = "UPDATE sl_wreceipts_items SET ID_customs_info='".$id_customs_info."' WHERE ID_wreceipts_items='".$rec->{'ID_wreceipts_items'}."' LIMIT 1;";
					$log .= $sql."<br>\n";
					&Do_SQL($sql);
				}
			}
		}

		# &Do_SQL("ROLLBACK"); Only debug
		# $log .= "ROLLBACK<br>";
		&Do_SQL("COMMIT");
		$log .= "COMMIT<br>\n";
		&Do_SQL("INSERT INTO sl_debug (cmd, id, log, Date, Time, ID_admin_users) VALUES ('WReceipts', '$in{'id_wreceipts'}', '".&filter_values($log)."', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');");
		# &cgierr($log.'<----');
	}
	
	if ($in{'status'} eq 'New') {
		$va{'new'} .= '&nbsp;  <a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_wreceipts&view='.$in{'id_wreceipts'}.'&chg_in_process=1" onclick="return confirm_chg_in_process()">In Process</a>';
	}	if ($in{'status'} eq 'In Process') {
		$va{'cancel'} .= '&nbsp;  <a href="/cgi-bin/mod/'.$usr{'application'}.'/dbman?cmd=mer_wreceipts&view='.$in{'id_wreceipts'}.'&cancel=1"><img src="/sitimages/default/delete.png" title="'.trans_txt('mer_wreceipts_cancel').'"></a>';
	}

	# block edition from WReceipt
	$va{'block_edition'} = ($in{'status'} eq 'In Process' or $in{'status'} eq 'New')? 0: 1;

	if ($in{'additem'}){
		if ($in{'status'} ne 'Processed'){
			# Multiple / Single items
			@arr_items = split /\|/, $in{'additem'};
			for my $i (0..$#arr_items) {
				### Se obtiene la cantidad que ya está asignada a esta recepción
				my $sth = &Do_SQL("SELECT SUM(Qty) FROM sl_wreceipts_items WHERE ID_wreceipts=".$in{'id_wreceipts'}." AND ID_products=".$arr_items[$i].";");
				my $qty_this_wreceipt = $sth->fetchrow();
				$qty_this_wreceipt = 0 if( !$qty_this_wreceipt );

				my ($sth) = &Do_SQL("INSERT INTO sl_wreceipts_items SET ID_wreceipts='$in{'id_wreceipts'}',ID_products='".$arr_items[$i]."',Serial='".&filter_values($in{'serial'})."',Qty=ifnull( (SELECT sum(if((Qty - Received - $qty_this_wreceipt) > 0, (Qty - Received - $qty_this_wreceipt), 1)) as quantity FROM sl_purchaseorders_items WHERE ID_purchaseorders = '".$in{'id_purchaseorders'}."' AND ID_products = '".$arr_items[$i]."' ), 0),Date=CURDATE(),Time=CURTIME(),ID_admin_users='$usr{'id_admin_users'}'");
				$va{'tabmessage'} = &trans_txt('wreceipt_itemadded');
				&auth_logging('wreceipt_itemadded',$arr_items[$i]);
			}

		}else{
			$va{'tabmessage'} = &trans_txt('mer_wreceipts_notedit');
		}
		
	}elsif($in{'ajaxresp'}){
		my ($sth) = &Do_SQL("UPDATE sl_wreceipts_items SET ID_products='$in{'ajaxresp'}' WHERE ID_wreceipts_items='$in{'id_wreceipts_items'}'");
		&auth_logging('wreceipt_itemupd',$in{'id_wreceipts'});
	}elsif($in{'drop'}){
		my ($sth) = &Do_SQL("DELETE FROM sl_wreceipts_items WHERE ID_wreceipts_items='$in{'drop'}'");
		&auth_logging('wreceipt_itemdel',$in{'id_wreceipts'});
	}

	## Load Vendor Info & Currency Info
	if ($in{'id_vendors'}>0){
		my ($sth) = &Do_SQL("SELECT CompanyName, Currency, Category FROM sl_vendors WHERE ID_vendors=$in{'id_vendors'}");
		($va{'vendor_name'},$va{'vendor_currency'},$va{'vendor_category'}) = $sth->fetchrow_array();
	}

	if ($va{'vendor_currency'} ne $cfg{'acc_default_currency'} and $cfg{'acc_default_currency'}){
		$va{'currency'} = &format_price(&load_name('sl_exchangerates','ID_exchangerates',$in{'id_exchangerates'},'exchange_rate'), 4) if ($in{'id_exchangerates'}>0);
		$va{'curstyle'} = '';
	}else{
		$va{'currency'} = '';
		$va{'curstyle'} = qq|style="display:none;"|;
	}

	$va{'btncustoms_style'} = ($in{'status'} eq 'Processed') ? 'style="display: none;"' : 'style="display: inline-block;"';

	## Build PO
	my ($choices,$tot_qty,$tot_po,$vendor_sku,$line,$name,$cmdlink,$unit);
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wreceipts_items WHERE ID_wreceipts = '$in{'id_wreceipts'}'");	
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT Serial, ID_wreceipts, ID_wreceipts_items, sl_wreceipts_items.ID_products, Model, Name, Qty, SPrice , RIGHT(sl_wreceipts_items.ID_products,6)AS PROD, ID_customs_info
				FROM sl_wreceipts_items 
				INNER JOIN sl_products ON (RIGHT(sl_wreceipts_items.ID_products,6)=sl_products.ID_products ) 
				WHERE ID_wreceipts='$in{'id_wreceipts'}' 
				AND sl_wreceipts_items.ID_products NOT LIKE '4%'
				UNION
				SELECT Serial, ID_wreceipts, ID_wreceipts_items, sl_wreceipts_items.ID_products, Model, Name, Qty, 0 as SPrice , RIGHT(sl_wreceipts_items.ID_products,6)AS PROD, ID_customs_info
				FROM sl_wreceipts_items 
				INNER JOIN sl_parts ON (RIGHT(sl_wreceipts_items.ID_products,4)=sl_parts.ID_parts ) 
				WHERE ID_wreceipts='$in{'id_wreceipts'}' 
				AND sl_wreceipts_items.ID_products LIKE '4%'
				ORDER BY ID_wreceipts_items DESC");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			#$status_wreceipt = &load_name('sl_wreceipts','ID_wreceipts',$rec->{'ID_wreceipts'},'Status');
			(!$rec->{'Serial'}) and ($rec->{'Serial'} = '---');
			
			$va{'polist'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'><a href='$script_url?cmd=mer_parts&view=$rec->{'PROD'}'>".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'polist'} .= "   <td class='smalltext'>$rec->{'Model'}<br>$rec->{'Name'}</td>\n";
			$va{'polist'} .= "   <td class='smalltext' valign='top'>$rec->{'Serial'}</td>\n";
			if ($va{'block_edition'}) {
				$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'>".&format_number($rec->{'Qty'})."</td>\n"; 
			}else{
				$va{'polist'} .= "   <td class='smalltext' align='right' valign='top'><span id='span_qty_$rec->{'ID_wreceipts_items'}' class='editable'>".&format_number($rec->{'Qty'})."</span> $unit <span id='span_chg_qty_$rec->{'ID_wreceipts_items'}'><img id='btn_chg_qty_$rec->{'ID_wreceipts_items'}' class='triggers_editable' src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' title='".&trans_txt('clicktoedit')."' style='cursor:pointer;'></span></td>\n"; 
			}
			$va{'polist'} .= "</tr>\n";

			if ($cfg{'use_customs_info'} and $cfg{'use_customs_info'}==1 and ($in{'status'} eq 'In Process' or $in{'status'} eq 'New') and $va{'vendor_currency'} ne $cfg{'acc_default_currency'}){
				$sql = "SELECT import_declaration_number, import_declaration_date, customs, ID_vendors FROM cu_customs_info WHERE ID_customs_info='".$rec->{'ID_customs_info'}."';";
				$log .= $sql."<br>";
				my ($sth_customs_info) = &Do_SQL($sql);
				my ($import_declaration_number, $import_declaration_date, $customs, $id_vendors) = $sth_customs_info->fetchrow_array();

				my $bs_customs = &build_select_from_enum("customs","cu_customs_info");
				$va{'polist'} .= qq|
				<tr bgcolor="$c[$d]">
					<td>
						<input placeholder='Pedimento' type="text" size="30" value="$import_declaration_number" name="import_declaration_number_$rec->{'ID_wreceipts_items'}" id="import_declaration_number_$rec->{'ID_wreceipts_items'}" onfocus="focusOn( this )" onblur="focusOff( this )" style="cursor: pointer; background-color: rgb(255, 255, 255);" />
					</td>
					<td>
						<input placeholder='Fecha' type="text" size="10" value="$import_declaration_date" name="import_declaration_date_$rec->{'ID_wreceipts_items'}" id="import_declaration_date_$rec->{'ID_wreceipts_items'}" onfocus="focusOn( this )" onblur="focusOff( this )" style="cursor: pointer; background-color: rgb(255, 255, 255);" />
					</td>
					<td>
						<select name="customs_$rec->{'ID_wreceipts_items'}" onFocus='focusOn( this )' onBlur='focusOff( this )' >
							<option value="">--- Aduana ---</option>
							$bs_customs
						</select>
					</td>
					<td>
						<select name="id_customs_broker_$rec->{'ID_wreceipts_items'}" onFocus='focusOn( this )' onBlur='focusOff( this )' >
							<option value="">--- Agente Aduanal ---</option>
							[fc_build_select_vendors_adjustments]
						</select>
					</td>
				</tr>\n|;
				
				$va{'js_chg_select'} .= qq|
					chg_select('customs_$rec->{'ID_wreceipts_items'}','$customs');
					chg_select('id_customs_broker_$rec->{'ID_wreceipts_items'}','$id_vendors');|;

				$va{'js_date_ui'} .= qq|
					\$("\#import_declaration_date_$rec->{'ID_wreceipts_items'}").datepicker({
					    maxDate: 0,
					    dateFormat: 'yy-mm-dd',
					    changeMonth: true,
						numberOfMonths: 3
					});|;
			}

			$tot_qty += $rec->{'Qty'};
			$tot_po +=$rec->{'SPrice'}*$rec->{'Qty'};
		}

	}else{
		$va{'polist'} = qq|
			<tr>
				<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}	
}

#############################################################################
#############################################################################
#   Function: load_po_items
#
#       Es: Muestra los items de un po
#       En: English description if possible
#
#
#    Created on: 30/01/2013  12:00:00
#
#    Author: Enrique Peña
#
#    Modifications:
#
#
#   Parameters:
#
#      - id_po Id Purcharse Order
#
#  Returns:
#
#      - Items de un PO, asi como resumen (Descripcion,TOTAL)
#
#   See Also:
#
#
#
sub load_wreceipts_items{
#############################################################################
#############################################################################s
	my ($choices,$vendor_sku,$line,$name,$cmdlink,$unit,$output);
	$output = "";
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_wreceipts_items WHERE ID_wreceipts='$in{'id_wreceipts'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT * FROM sl_wreceipts_items WHERE ID_wreceipts='$in{'id_wreceipts'}' ORDER BY ID_wreceipts_items DESC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;
			
			## Choices
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{ID_products}' and Status='Active'");
			$tmp = $sth2->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
			
			## Name Model
			if ($rec->{'ID_products'} =~ /^5/){
				## Non Inventory
				$cmdlink = 'mer_noninventory';
				$unit = &load_db_names('sl_noninventory','ID_noninventory',($rec->{ID_products}-500000000),'[Units]');
				$name = &load_db_names('sl_noninventory','ID_noninventory',($rec->{ID_products}-500000000),'[Name]');
			}elsif ($rec->{'ID_products'}  =~ /^4/){
				## Part
				$unit  = "Unit";
				$cmdlink = 'mer_parts';
				$name = &load_db_names('sl_parts','ID_parts',($rec->{ID_products}-400000000),'[Model]<br>[Name]');
			}
			
				$output .= "<tr>\n";
				$output .= "   <td style='border-bottom:solid 1px #333333;border-right:solid 1px #333333;' class='smalltext' valign='top' align='center'>$line</td>\n";
				$output .= "   <td style='border-bottom:solid 1px #333333;border-right:solid 1px #333333;'>".&format_sltvid($rec->{'ID_products'})."</td>";
				$output .= "   <td style='border-bottom:solid 1px #333333;border-right:solid 1px #333333;' class='smalltext' valign='top' align='left' nowrap> $name</td>\n";
				$output .= "   <td style='border-bottom:solid 1px #333333;border-right:solid 1px #333333;' class='smalltext' valign='top' align='right'>".$rec->{'Serial'}."</td>\n";
				$output .= "   <td style='border-bottom:solid 1px #333333' class='smalltext' valign='top' align='right'>".&format_number($rec->{'Qty'})."</td>\n";
				$output .= "</tr>\n";
			
		}		
			
	}else{
		$output = qq| <tr>
					<td colspan='7' align="center">|.&trans_txt('search_nomatches').qq|</td>
				    </tr>\n|;
	}
	
	return $output;
}


1;