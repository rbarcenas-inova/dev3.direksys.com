#!/usr/bin/perl
####################################################################
########             CUSTOMERS                  ########
####################################################################

# Last Modified on: 07/15/08  13:02:41
# Last Modified by: Roberto Barcenas
# Last Modified Desc: empty notes were fixed

sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 1){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_customers_notes';
	}elsif($in{'tab'} eq 8){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_customers';
	}
}
 
 


sub load_tabs2 {
# --------------------------------------------------------
##############################################
#### tab2 - Order/Products	
##############################################
# Last Time Modified by RB on 30/11/2011: Se resuelve problema con ordenes tipo wholesale y con servicios				
 	my (@c) = split(/,/,$cfg{'srcolors'});	

 	## Se eliminan los telefonos paraq que no causen problema en la paginacion
 	delete($in{'phone1'});
 	delete($in{'phone2'});

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE ID_customers='$in{'id_customers'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT sl_orders_products.Date, sl_orders_products.Time, concat( sl_orders_products.Date, sl_orders_products.Time ) AS orderDate, sl_orders.ID_orders,
					IF(RIGHT(sl_orders_products.ID_products,6)=000000,Related_ID_products,sl_orders_products.ID_products)AS ID_products,sl_orders_products.Quantity,sl_orders.Status
					FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
					AND ID_customers='$in{'id_customers'}'
					ORDER BY sl_orders.ID_orders DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT sl_orders_products.Date, sl_orders_products.Time, concat( sl_orders_products.Date, sl_orders_products.Time ) AS orderDate, sl_orders.ID_orders,
					IF(RIGHT(sl_orders_products.ID_products,6)=000000,Related_ID_products,sl_orders_products.ID_products)AS ID_products,sl_orders_products.Quantity,sl_orders.Status
					FROM sl_orders INNER JOIN sl_orders_products ON sl_orders.ID_orders = sl_orders_products.ID_orders
					AND ID_customers='$in{'id_customers'}'
					ORDER BY sl_orders.ID_orders DESC
					LIMIT $first,$usr{'pref_maxh'};");
		}
		while ($rec = $sth->fetchrow_hashref){
			my ($idp);
			#Services		
			if($rec->{'ID_products'} < 99999 or substr($rec->{'ID_products'},0,1) == 6){				
				$link_ts = "mer_services";
				$idp		= $rec->{'ID_products'}-600000000;
				$rec->{'Name'}	= &load_name("sl_services","ID_services",$idp,"Name");
			#Skus	
			}elsif(substr($rec->{'ID_products'},0,1) == 4){
				$idp=$rec->{'ID_products'}-400000000;
				$link_ts 	= "mer_parts";
				$rec->{'Name'} 	= &load_name("sl_parts","ID_parts",$idp,"Name");
				$rec->{'Model'}	= &load_name("sl_parts","ID_parts",$idp,"Model");
			#Products	
			}else{
				$idp=$rec->{'ID_products'}-100000000;
				$link_ts 	= "mer_products";
				$rec->{'Name'}	= &load_name("sl_products","ID_products",$idp,"Name");
				$rec->{'Model'}	= &load_name("sl_products","ID_products",$idp,"Model");
			}
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'} / $rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=".$link_ts."&view=".$idp."\">".&format_sltvid($rec->{'ID_products'})."</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}/$rec->{'Model'}</td>\n";					
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}


sub load_tabs4 {
# --------------------------------------------------------
##############################################
## tab4: RETURNS
##############################################

	my ($ttable,$trow,$rvalue,$rorder,@data,@links);
	$ttable 	= 	'sl_returns';
	$trow			=		'ID_customers';
	$rvalue		=		$in{'id_customers'};
	$rorder		=		'ID_returns';
	@links 		= 	qw(opr_returns);
	@data 		= 	qw(ID_returns	Type	merAction	Status	Date);
	push(@data,\@links);	
	&build_pretab_list($ttable,$trow,$rvalue,$rorder,@data);
}

sub load_tabs5 {
# --------------------------------------------------------
##############################################
## tab4: REP. MEMOS
##############################################
	## Logs
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_returns WHERE ID_customers='$in{'id_customers'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		if ($in{'print'}){
			$sth = &Do_SQL("SELECT * FROM sl_returns WHERE ID_customers='$in{'id_customers'}' ORDER BY ID_returns DESC;");
		}else{
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			$sth = &Do_SQL("SELECT * FROM sl_returns WHERE ID_customers='$in{'id_customers'}' ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		}
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogDate'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'LogTime'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>".&trans_txt($rec->{'Message'})."</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'IP'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
	$va{'date'} = load_name("sl_customers","ID_customers",$in{'id_customers'},"Date");
	$va{'time'} = load_name("sl_customers","ID_customers",$in{'id_customers'},"Time");
	$va{'admin_user'} = load_name("sl_customers,admin_users ","ID_customers","$in{'id_customers'} and sl_customers.ID_admin_users = admin_users.ID_admin_users " ,"CONCAT('(',admin_users.ID_admin_users,') ',admin_users.FirstName,' ',admin_users.LastName) ");
}

#############################################################################
#############################################################################
#   Function: load_tabs6
#
#       Es: Muestra los Charge Backs relacionados al customer
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Peña
#
#    Modifications:
#
#        - Modified on *21/11/2012* by _Enrique Peña_ : Se agrego funciones para mostrar charge Backs
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
#
sub load_tabs6 {
#############################################################################
#############################################################################	
	
	return;
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_chargebacks WHERE ID_orders_products = (SELECT ID_orders FROM sl_orders WHERE ID_customers = '$in{'id_customers'}' LIMIT 1)");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT * FROM sl_chargebacks WHERE ID_orders_products = (SELECT ID_orders FROM sl_orders WHERE ID_customers = '$in{'id_customers'}' LIMIT 1) ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ChargeBackTo'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ProdCategory'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs7
#
#       Es: Muestra los Coupons relacionados a las ordenes del customer
#
#
#    Created on: 21/11/2012  13:20:10
#
#    Author: Enrique Peña
#
#    Modifications:
#
#        - Modified on *21/11/2012* by _Enrique Peña_ : Se agrego funciones para mostrar los coupons
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
#
sub load_tabs7 {
#############################################################################
#############################################################################	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_coupons WHERE ID_coupons = (SELECT Coupon FROM sl_orders WHERE ID_customers = '$in{'id_customers'}' LIMIT 1)");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT * FROM sl_coupons WHERE ID_coupons = (SELECT Coupon FROM sl_orders WHERE ID_customers = '$in{'id_customers'}' LIMIT 1) ORDER BY Date DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PublicID'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Name'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Time'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs9
#
#       Es: Muestra los Invoices relacionados al customer.
#
#
#    Created on: 30/01/2013 18:00:00
#
#    Author: Enrique Peña
#
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
#
sub load_tabs9 {
#############################################################################
#############################################################################
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM (SELECT 1 FROM cu_invoices WHERE ID_customers = '$in{'id_view'}' GROUP BY ID_invoices)AS invoices");
	$va{'matches'} = int($sth->fetchrow_array);
	$va{'geninvoice'} = '';
	
	if ($va{'matches'} and $va{'matches'} > 0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
		$sth = &Do_SQL("SELECT CONCAT(doc_serial,doc_num) AS invoice, cu_invoices.ID_invoices,ID_customers,ID_orders,CONCAT(customer_fcode,' ',customer_fname) AS NAME, cu_invoices.Status,cu_invoices.Date, doc_serial, doc_num
				FROM cu_invoices_lines
				INNER JOIN cu_invoices ON cu_invoices.ID_invoices = cu_invoices_lines.ID_invoices
				WHERE ID_customers = '$in{'id_view'}'
				GROUP BY ID_invoices
				ORDER BY ID_invoices DESC LIMIT $first,$usr{'pref_maxh'};");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			
			my $pdf_name = $rec->{'doc_serial'}.'_'.$rec->{'doc_num'};
			my $link_pdf = "/cfdi/pages/cfdi/cfdi_doc.php?f=".$pdf_name.".pdf";
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			$va{'searchresults'} .= ($rec->{'Status'} eq 'Certified')?
									"   <td class='smalltext'><a href='$link_pdf' target='_blank'><img src='[va_imgurl]/[ur_pref_style]/pdf.gif' title='PDF' alt='PDF' border='0'></a></td>\n":
									"   <td class='smalltext'></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_invoices&view=$rec->{'ID_invoices'}\">$rec->{'ID_invoices'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'invoice'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$rec->{'ID_customers'}\">($rec->{'ID_customers'}) $rec->{'NAME'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Date'}</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;		
	}
}

sub load_tabs10 {
# --------------------------------------------------------
##############################################
## tab10 : address customer
##############################################
	use Data::Dumper;
	use HTML::Entities;

	## update
	if ($in{'action'}){
		#agregar una validacion de campos
		if(!$in{'drop_item'}) {
			## New Address
			my $mod1 = !$in{'id_customers_addresses'} ? "INSERT INTO" : "UPDATE";
			my $mod2 = !$in{'id_customers_addresses'} ? "" : " WHERE ID_customers_addresses = '".int($in{'id_customers_addresses'})."' ";
			my $id_customers = int($in{'view'});

			###no esta pasando address
			my $new_address1 = $in{'ca_street'};
			$new_address1 .= ($in{'ca_num'} ne '')?' No. '.$in{'ca_num'}:'';
			$new_address1 .= ($in{'ca_num2'} ne '')?' Int. '.$in{'ca_num2'}:'';
			my $new_address2 = $in{'ca_street'};
			my $new_address3 = $in{'ca_street'};
			#$in{'ca_cu_state'} = (&filter_values($in{'ca_cu_state'}) eq '')?$in{'ca_state'}:$in{'ca_cu_state'};
			
			my $query = "$mod1 cu_customers_addresses SET 
			 ID_customers=".&filter_values($id_customers)."
			,  Code='".&filter_values($in{'ca_code'})."'
			,  Alias='".&filter_values($in{'ca_alias'})."'
			,  Address1='".&filter_values($new_address1)."'
			,  Address2=''
			,  Address3=''
			,  Urbanization='".&filter_values($in{'ca_urbanization'})."'
			,  City='".&filter_values($in{'ca_city'})."'
			,  State='".&filter_values($in{'ca_state'})."'
			,  Zip='".&filter_values($in{'ca_zipcode'})."'
			,  Country='".&filter_values($in{'ca_country'})."'
			,  cu_Street='".&filter_values($in{'ca_street'})."' 
			,  cu_Num='".&filter_values($in{'ca_num'})."'
			,  cu_Num2='".&filter_values($in{'ca_num2'})."'
			,  cu_Urbanization='".&filter_values($in{'ca_urbanization'})."'
			,  cu_City='".&filter_values($in{'ca_city'})."'
			,  cu_State='".&filter_values($in{'ca_cu_state'})."'
			,  cu_Zip='".&filter_values($in{'ca_zipcode'})."'
			,  cu_Country='".&filter_values($in{'ca_country'})."'
			,  PrimaryRecord='".&filter_values($in{'ca_primaryrecord'})."'
			,  Date=curdate()
			,  Time=curtime()
			,  ID_admin_users='".$usr{'id_admin_users'}."'
			$mod2 ;";

			my ($sth)=&Do_SQL($query);

			### PrimaryRecord?
			$in{'id_customers_addresses'} = $sth->{'mysql_insertid'} if !$in{'id_customers_addresses'};
			my $sth = &Do_SQL("UPDATE cu_customers_addresses SET PrimaryRecord = 'No' WHERE ID_customers_addresses != '".int($in{'id_customers_addresses'})."' AND ID_customers='".int($in{'id_customers'})."';") if $in{'ca_primaryrecord'} eq 'Yes';

		}elsif($in{'drop_item'}) {
			## Delete customer address

			my $pr = &load_name('cu_customers_addresses','ID_customers_addresses',$in{'id_customers_addresses'},'PrimaryRecord');
			my $sth = &Do_SQL("DELETE FROM cu_customers_addresses WHERE ID_customers_addresses = '$in{'drop_item'}'");
			my $sth = &Do_SQL("UPDATE cu_customers_addresses SET PrimaryRecord = 'Yes' ORDER BY ID_customers_addresses LIMIT 1;") if $pr eq 'Yes';
			delete($in{'drop_item'});

		}  # End if drop_item
      
		delete($in{'action'});
	}  # End if action

	## Listing
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM cu_customers_addresses WHERE ID_customers=$in{'view'} AND Status = 'Active'");
	$va{'matches'} = $sth->fetchrow;
	delete($in{'address1'});
	delete($in{'address2'});
	delete($in{'address3'});
	my (@c) = split(/,/,$cfg{'srcolors'});

	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		$sth = &Do_SQL("SELECT * FROM cu_customers_addresses WHERE ID_customers=$in{'view'} AND Status = 'Active' ORDER BY ID_customers_addresses DESC LIMIT $first,$usr{'pref_maxh'};");
		## Using rel='#overlay' for anchor makes overlay popup
		while($rec=$sth->fetchrow_hashref()) {
			$d = 1 - $d;
			
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			#$va{'searchresults'} .= "   <td class='smalltext' width='60px' nowrap>";
			#$va{'searchresults'} .= "		<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$in{'id_customers'}&tab=$in{'tab'}&action=1&belongsto=$rec->{'BelongsTo'}&drop_item=$rec->{'ID_customers_addresses'}\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' alt='Delete' title='Delete' border='0'></a>&nbsp;&nbsp;";
			#$va{'searchresults'} .= "   	<a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_customers_address&id_row=$rec->{'ID_customers_addresses'}' rel='#overlay' style='text-decoration:none'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' alt='Edit' title='Edit' border='0'></a>&nbsp;&nbsp;";
			#$va{'searchresults'} .= "\n		</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='50px'><span id='address'>$rec->{'Alias'}</span>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='180px'><span id='City'>".($rec->{'City'})."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='180px'><span id='State'>".($rec->{'State'})."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='60px'><span id='Zipcode'>".$rec->{'Zip'}."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='60px' align='center'><span id='Zipcode'>".&trans_txt($rec->{'PrimaryRecord'})."</span></td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}  # End while

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}  # End if str_sql
}

sub load_tabs11 {
# --------------------------------------------------------
##############################################
## tab11 : customers parts alias
##############################################
	use Data::Dumper;
	use HTML::Entities;

	## update
	if ($in{'action'}){
		#agregar una validacion de campos
		if($in{'add_new'}){
			my $id_customers = int($in{'view'});
			
			my ($sths) = &Do_SQL("SELECT sku_customers FROM sl_customers_parts INNER JOIN sl_parts USING(id_parts) WHERE id_customers=$in{'view'} AND sku_customers='".filter_values($in{'new_sku_customers'})."'");
			if ($sths->rows == 0 || $in{'new_sku_customers'} eq '') {
				my ($sth)=&Do_SQL("INSERT INTO sl_customers_parts SET 
				ID_customers=".&filter_values($id_customers)."
				,  ID_parts='".&filter_values($in{'new_id_parts'})."'
				,  SPrice='".&filter_values($in{'new_sprice'})."'
				,  size='".&filter_values($in{'new_size'})."'
				,  sku_customers='".&filter_values($in{'new_sku_customers'})."'");
				$id_new = $sth->{'mysql_insertid'};
	
				delete($in{'add_new'});
			}
			else {
				$va{'tabmessages'}=&trans_txt('opr_customers_sku_alias_duplicated');
			}
			
		}  # End if add_new


		## Updating Product Data in sl_products_prior for Ecommerce Purposes
		if($in{'upd_item'}){
			my $id_customers_parts = int($in{'upd_item'});
			my $id_customers = int($in{'view'});

			my ($sth)=&Do_SQL("UPDATE sl_customers_parts SET 
			ID_customers=".&filter_values($id_customers)."
			,  SPrice='".&filter_values($in{'new_sprice'})."'
			,  sku_customers='".&filter_values($in{'new_sku_customers'})."'
			WHERE ID_customers_parts = '".$id_customers_parts."'");
		 
			delete($in{'upd_item'});
		}  # End if upd_item


		## Delete address customer
		if($in{'drop_item'}) {
			my $sth = &Do_SQL("DELETE FROM sl_customers_parts WHERE ID_customers_parts = '$in{'drop_item'}'");		

			delete($in{'drop_item'});

		}  # End if drop_item
      
      
		delete($in{'action'});
	}  # End if action


	## Listing
	$str_sql = "SELECT COUNT(*) FROM sl_customers_parts INNER JOIN sl_parts USING(id_parts) WHERE sl_parts.Status !='Inactive' AND id_customers=$in{'view'}";

	my ($sth)=&Do_SQL($str_sql);
	$va{'matches'} = $sth->fetchrow;

	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		my (@c) = split(/,/,$cfg{'srcolors'});
		
		my ($sth)=&Do_SQL("SELECT * FROM sl_customers_parts INNER JOIN sl_parts USING(id_parts) WHERE sl_parts.Status !='Inactive' AND id_customers=$in{'view'} ORDER BY Name ASC LIMIT $first,$usr{'pref_maxh'};");
		
		## Using rel='#overlay' for anchor makes overlay popup
		while($rec=$sth->fetchrow_hashref()) {
			$d = 1 - $d;

			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			#$va{'searchresults'} .= "   <td class='smalltext' width='60px' nowrap>";
			#$va{'searchresults'} .= "		<a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$in{'id_customers'}&tab=$in{'tab'}&action=1&belongsto=$rec->{'BelongsTo'}&drop_item=$rec->{'ID_customers_parts'}\"><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' alt='Delete' title='Delete' border='0'></a>&nbsp;&nbsp;";
			#$va{'searchresults'} .= "   	<a href='/cgi-bin/common/apps/ajaxbuild?tab=$in{'tab'}&ajaxbuild=overlay_customers_parts&id_row=$rec->{'ID_customers_parts'}&belongsto=$rec->{'BelongsTo'}' rel='#overlay' style='text-decoration:none'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_edit.png' alt='Edit' title='Edit' border='0'></a>&nbsp;&nbsp;";
			#$va{'searchresults'} .= "\n		</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='id_parts'><a href='/cgi-bin/mod/".$usr{'application'}."/dbman?cmd=mer_parts&view=".$rec->{'ID_parts'}."''>".($rec->{'ID_parts'})."</a></span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px'><span id='sku_customers'>".($rec->{'sku_customers'})."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='180px'><span id='Name'>".$rec->{'Name'}."</span></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' width='120px' align='right'><span id='Name'>".&format_price($rec->{'SPrice'})."</span></td>\n";

			
			$va{'searchresults'} .= "</tr>\n";
		}  # End while

	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='8' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}  # End if str_sql
}

# Tab Payments
sub load_tabs12 {
##############################################
## tab12 : payments
##############################################
	## Primero listamos todos los pagos que ha hecho este cliente	
	$va{'divlist'} = "";
	$va{'divadd'} = "display:none;";
	my $invoice_status = ($cfg{'invoice_status'} ne '')?$cfg{'invoice_status'}:'Certified';
	
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*)
	FROM sl_banks_movements
	INNER JOIN sl_banks_movrel USING(ID_banks_movements)
	INNER JOIN sl_orders_payments ON ID_orders_payments=tableid AND tablename='orders_payments'
	INNER JOIN sl_orders USING(ID_orders)
	WHERE 1 AND sl_orders.ID_customers = '$in{'view'}'
	AND sl_orders_payments.Status IN ('Approved')
	AND sl_orders_payments.Captured = 'Yes'
	AND sl_orders.Status NOT IN ('Cancelled','Void','System Error'); ");

	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		$sth = &Do_SQL("SELECT ID_orders, ID_orders_payments
		, sl_orders_payments.Type, sl_orders_payments.Amount, Reason, Paymentdate, sl_orders_payments.Status, sl_orders.Ptype, sl_orders.Pterms, sl_orders.StatusPrd, sl_orders.StatusPay, sl_orders.Status OrderStatus, sl_orders.OrderNotes
		FROM sl_banks_movements
		INNER JOIN sl_banks_movrel USING(ID_banks_movements)
		INNER JOIN sl_orders_payments ON ID_orders_payments=tableid AND tablename='orders_payments'
		INNER JOIN sl_orders USING(ID_orders)
		WHERE 1 AND sl_orders.ID_customers = '$in{'view'}'
		AND sl_orders_payments.Status IN ('Approved')
		AND sl_orders_payments.Captured = 'Yes'
		AND sl_orders.Status NOT IN ('Cancelled','Void','System Error')
		ORDER BY ID_orders DESC LIMIT $first,$usr{'pref_maxh'};");
		
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
			# $va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_invoices&view=$rec->{'ID_invoices'}\">$rec->{'ID_invoices'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'OrderStatus'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Type'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Pterms'}</td>\n";
			$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Amount'})."</td>\n";
			$va{'searchresults'} .= "</tr>\n";
		}
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

sub load_tabs13 {
# --------------------------------------------------------
##############################################
## tab13 : AR
##############################################
	####
	#### CAULQUEIR CAMBIO EN ESTE CODIGO DEBE SER TAMBIEN HECHO EN
	#### ADMIN/ADMIN_OPR.CGI opr_ar_statements
	####
	my ($line,$showlist);
	my ($sth) = &Do_SQL("SELECT * FROM sl_orders 
						LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
						WHERE sl_orders.Status='Shipped' AND  
						ID_customers=$in{'id_customers'}
						GROUP BY sl_orders.ID_orders");
	$va{'matches'} = $sth->rows()-1;
	my (@c) = split(/,/,$cfg{'srcolors'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		my $first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		$sth = &Do_SQL("SELECT 
						sl_orders.ID_orders, 
						sl_orders.Date AS OrderDate,
						sl_orders.PostedDate,
						Paymentdate,
						DATEDIFF(CURDATE(),sl_orders.PostedDate) AS df1,
						DATEDIFF(CURDATE(),Paymentdate) AS df2,
						SUM(Amount) AS Total,
						SUM(IF(Captured='Yes',Amount,0)) AS Paid
						
						FROM sl_orders 
						LEFT JOIN sl_orders_payments ON sl_orders.ID_orders=sl_orders_payments.ID_orders
						WHERE sl_orders.Status='Shipped' AND sl_orders_payments.Status='Approved' AND 
						ID_customers=$in{'id_customers'}
					GROUP BY sl_orders.ID_orders
					HAVING (Total>Paid)
					ORDER BY df1 DESC;");
		## Using rel='#overlay' for anchor makes overlay popup
		my (@steps) = ("90","60","30","1");
		while($rec=$sth->fetchrow_hashref()) {
			$showlist=1;
			($line<$first) and ($showlist=0);
			($line>=($first+$usr{'pref_maxh'})) and ($showlist=0);
			++$line;
			for my $i(0..$#steps){
				if ($rec->{'df2'}>=$steps[$i] and $rec->{'df2'}>0){
					$va{'due'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
				}elsif(-$rec->{'df2'}>=$steps[$i] and $rec->{'df2'}<0){
					$va{'ndue'.$steps[$i]} += $rec->{'Total'}-$rec->{'Paid'};
				}elsif($rec->{'df2'} eq 0){
					$va{'due0'} += $rec->{'Total'}-$rec->{'Paid'};
				}
			}
			if ($showlist){
				$d = 1 - $d;
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'OrderDate'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'PostedDate'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Paymentdate'}</td>\n";
				if ($rec->{'df2'}<0){
					$va{'searchresults'} .= "   <td class='smalltext' align='right'>".(-$rec->{'df2'})."</td>\n";
				}else{
					$va{'searchresults'} .= "   <td class='smalltext' align='right' style='Color:Red'>$rec->{'df2'}</td>\n";
				}
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Total'}-$rec->{'Paid'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>". &invoices_list($rec->{'ID_orders'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
			$va{'total_balance'} += $rec->{'Total'}-$rec->{'Paid'}
		}  # End while
		$va{'total_balance'} = &format_price($va{'total_balance'});
		for (0..$#steps){
			$va{'due'.$steps[$_]} = &format_price($va{'due'.$steps[$_]});
			$va{'ndue'.$steps[$_]} = &format_price($va{'ndue'.$steps[$_]});
		}
		$va{'due0'} = &format_price($va{'due0'});
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}  # End if str_sql
}

sub load_tabs14 {
##############################################
## tab14 : Movements
##############################################
	## Primero listamos todos los pagos que ha hecho este cliente	
	$va{'divlist'} = "";
	$va{'divadd'} = "display:none;";
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL('SELECT ID_orders sl_orders
						FROM sl_movements 
						JOIN  sl_orders on sl_orders.ID_orders=sl_movements.ID_tableused
						join sl_customers on sl_customers.ID_accounts_debit=sl_movements.ID_accounts
						WHERE 
							sl_customers.ID_customers='.$in{'view'}.'
							AND sl_movements.Status = "Active"
							AND sl_movements.tableused="sl_orders"
						order by 
							sl_orders.ID_orders DESC,  
							sl_movements.Amount DESC,
							sl_movements.EffDate DESC');


	$va{'matches'} = $sth->rows();
	#cgierr("Se encontraron ".$va{'matches'});
	if ($va{'matches'}>0){
		(!$in{'nh'}) and ($in{'nh'}=1);
		$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};			
		($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});

		$sth = &Do_SQL('SELECT sl_orders.ID_orders, sl_orders.`Status`, sl_orders.Ptype, sl_movements.EffDate,
						sl_movements.Amount as "Debit",
						(
							SELECT SUM(m2.Amount) 
							FROM sl_movements m2
							-- JOIN sl_customers c2 ON c2.ID_accounts_debit=m2.ID_accounts
							WHERE m2.ID_tableused=sl_orders.ID_orders
							and m2.tableused="sl_orders"
							AND m2.Credebit="Credit"
							AND m2.tablerelated="sl_banks_movements"
							-- AND c2.ID_customers='.$in{'view'}.'
						) as "Credit"
						FROM sl_movements 
						JOIN sl_orders ON sl_orders.ID_orders=sl_movements.ID_tableused
						JOIN sl_customers ON sl_customers.ID_accounts_debit=sl_movements.ID_accounts
						WHERE
							sl_customers.ID_customers='.$in{'view'}.'
							AND sl_movements.ID_accounts=sl_customers.ID_accounts_debit
							AND sl_movements.Status = "Active"
							AND sl_movements.tableused="sl_orders"
							AND sl_movements.Credebit="Debit"
						GROUP BY(ID_orders)
						LIMIT '.$first.','.$usr{'pref_maxh'});


	while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			if(&format_price($rec->{'Debit'}) ne &format_price($rec->{'Credit'})){
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]'>\n";
				$va{'searchresults'} .= "   <td class='smalltext'><a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_orders&view=$rec->{'ID_orders'}\">$rec->{'ID_orders'}</a></td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Status'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'Ptype'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'EffDate'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Debit'})."</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext' align='right'>".&format_price($rec->{'Credit'})."</td>\n";
				$va{'searchresults'} .= "</tr>\n";
			}
		}
	}else{
		$va{'matches'} = 0;
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='6' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

1;