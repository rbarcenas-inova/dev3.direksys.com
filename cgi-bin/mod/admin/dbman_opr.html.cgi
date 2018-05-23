sub loaddefault_opr_warehouse {
# --------------------------------------------------------
	$in{'address1'}= '';
}

##########################################################
##	  OPERATIONS	: INORDERS        ##
##########################################################
sub view_opr_inorders {
# --------------------------------------------------------
	if ($in{'id_pricelevels'}){
		$in{'pricelevels_name'} = &load_db_names('sl_pricelevels','ID_pricelevels',$in{'id_pricelevels'},'[Name]');
	}

	### Question/Answer table
	for (1..5){
		(!$in{'question'.$_}) and ($in{'question'.$_}='---');
		(!$in{'answer'.$_}) and ($in{'answer'.$_}='---');
	}
}

sub view_opr_invoices{
#-----------------------------------------
# Created on: 05/11/09  10:54:03 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	
#Last modified on 7 Feb 2011 19:04:51
#Last modified by: MCC C. Gabriel Varela S. : Se valida para cambio de invoice para wholesale orden
#Last modified on 8 Feb 2011 11:22:34
#Last modified by: MCC C. Gabriel Varela S. :Se hace que siempre se ponga el company_name, aunque estÃ© vacÃ­o
# Last Modified by RB on 03/30/2011 07:32:07 PM : Se agrega validacion para allnatpro 
#Last modified on 26 May 2011 13:01:14
#Last modified by: MCC C. Gabriel Varela S. :Se hace que aquÃ­ se asignen los puntos de fidelizaciÃ³n.
# Last Modified by RB on 10/11/2011: Se agrega idioma de invoice
	
	my($emp);
	&set_reward_points($in{'id_orders'});
	$emp ='';
	$emp = 'e'.$in{'e'} if $in{'e'} > 0;
	
	#$va{'shp_phone'} = &load_customer_phone($in{'id_customers'});
	$va{'shp_phone'} = "";
	$va{'logo_gris'} = 'logo_gris.'.$emp.'.gif';
	$va{'url_txt'} = 'url.'.$emp.'.gif';
	
	# Extraemos el tipo de cliente
	my $customer_type=&load_name('sl_customers','ID_customers',$in{'id_customers'},'Type');

	if(&is_adm_order($in{'id_orders'}) and &is_exportation_order($in{'id_orders'}) or ($customer_type =~ /wholesale/i))
	{
		
		my $company_name=&load_name('sl_customers','ID_customers',$in{'id_customers'},'company_name');
		$in{'shp_name'}=$company_name;	
		$in{'cmd'}.='_whole';
	
	}elsif($customer_type eq 'Allnatpro'){
	
		$va{'logo_gris'} = 'logo_gris_allnatpro.'.$emp.'.gif';
		$va{'url_txt'} = 'url_allnatpro.'.$emp.'.gif';
	
		$in{'shp_name'}=$customer_type;	
		$in{'cmd'}.='_allnatpro';
	
	}

	# Extraemos el idioma del invoice
	my $order_lang= &load_name('sl_orders','ID_orders',$in{'id_orders'},'language')eq'english' ? '_en' : '';
	$in{'cmd'}.= $order_lang;

	
}

sub view_opr_pinvoices{
#-----------------------------------------
# Created on: 05/11/09  10:54:03 By  Roberto Barcenas
# Forms Involved: 
# Description :
# Parameters : 	
#Last modified on 7 Feb 2011 19:04:51
#Last modified by: MCC C. Gabriel Varela S. : Se valida para cambio de invoice para wholesale orden
#Last modified on 8 Feb 2011 11:23:01
#Last modified by: MCC C. Gabriel Varela S. :Se hace que siempre se utilice el company_name, aunque estÃ© vacÃ­o.
# Last Modified by RB on 10/11/2011: Se agrega idioma de invoice

	
	my($emp);
	
	$emp ='';
	$emp = 'e'.$in{'e'} if $in{'e'} > 0;
	
	#$va{'shp_phone'} = &load_customer_phone($in{'id_customers'});
	$va{'shp_phone'} = "";
	$va{'logo_gris'} = 'logo_gris.'.$emp.'.gif';
	$va{'url_txt'} = 'url.'.$emp.'.gif';
	
	# Extraemos el tipo de cliente
	my $customer_type=&load_name('sl_customers','ID_customers',$in{'id_customers'},'Type');

	if(&is_adm_order($in{'id_orders'}) and &is_exportation_order($in{'id_orders'}))
	{

		my $company_name=&load_name('sl_customers','ID_customers',$in{'id_customers'},'company_name');
		$in{'shp_name'}=$company_name;
		$in{'cmd'}.='_whole';

	}elsif($customer_type eq 'Allnatpro'){

		$va{'logo_gris'} = 'logo_gris_allnatpro.'.$emp.'.gif';
		$va{'url_txt'} = 'url_allnatpro.'.$emp.'.gif';

		$in{'shp_name'}=$customer_type;
		$in{'cmd'}.='_allnatpro';

	}

	# Extraemos el idioma del invoice
	my $order_lang= &load_name('sl_orders','ID_orders',$in{'id_orders'},'language')eq'english' ? '_en' : '';
	$in{'cmd'}.= $order_lang;
	
}




##########################################################
##	OPERATIONS : SPEECH
##########################################################

sub view_opr_speech {
# --------------------------------------------------------
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia Number por DNIS en sl_mediadids
	if ($in{'id_dids'}){
		#($db,$id_name,$id_value,$field)
		$in{'didname'} = &load_name('sl_mediadids','didmx',$in{'id_dids'},'product');
		$in{'didnumber'} = $in{'num800'};  #&load_name('sl_di ds','ID_dids',$in{'id_dids'},'DNIS');
	}
}



sub validate_opr_zipcodes {
# --------------------------------------------------------
	$in{'not_autoincrement'} = 1;	
	return 0;
}



sub advsearch_opr_returns{
# --------------------------------------------------------
# Created on: 6/18/2008 11:20 AM
# Last Modified on:
# Last Modified by:
# Author: Jose Ramirez Garcia
# Description : Search returns using all fields
# Parameters : inputs
	if($in{'action'}){
		if($in{'firstname'}){
			$qry .= " $st sl_customers.firstname='$in{'firstname'}' ";
		}
		if($in{'lastname1'}){
			$qry .= " $in{'st'} sl_customers.lastname1='$in{'lastname1'}' ";
		}
		if($in{'lastname2'}){
			$qry .= " $in{'st'} sl_customers.lastname2='$in{'lastname2'}' ";
		}
		if($in{'phone1'}){
			$qry .= " $in{'st'} sl_customers.phone1='$in{'phone1'}' ";
		}
		if($in{'phone2'}){
			$qry .= " $in{'st'} sl_customers.phone2='$in{'phone2'}' ";
		}
		if($in{'cellphone'}){
			$qry .= " $in{'st'} sl_customers.cellphone='$in{'cellphone'}' ";
		}		
		if($in{'id_orders'}){
			my ($sth) = &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE ID_orders='$in{'id_orders'}'");
			while ($rec = $sth->fetchrow_hashref){
				$id_orders_products .= $rec->{'ID_orders_products'}.",";
			}
			chop($id_orders_products);
			if($id_orders_products){
				$qry .= " $in{'st'} sl_returns.id_orders_products IN($id_orders_products) ";
			}
		}		
		if($in{'id_returns'}){
			$qry .= " $in{'st'} sl_returns.id_returns='$in{'id_returns'}' ";
		}		
		if($in{'status'}){
			$qry .= " $in{'st'} sl_returns.status='$in{'status'}' ";
		}
		if($in{'type'}){
			$qry .= " $in{'st'} sl_returns.type='$in{'type'}' ";
		}
		if($in{'meraction'}){
			$qry .= " $in{'st'} sl_returns.meraction='$in{'id_meraction'}' ";
		}
		$in{'from_date'} = $in{'fromdate'} if $in{'fromdate'};
		$in{'to_date'}	= $in{'todate'} if $in{'todate'};					
		if($in{'from_date'} && $in{'to_date'}){
			$barra = '/';
			$guion = '-';
			$in{'from_date'}=~ s/$barra/$guion/g;
			$in{'to_date'}=~ s/$barra/$guion/g;
				$qry .= "$in{'st'} sl_returns.Date BETWEEN '$in{'from_date'}' AND '$in{'to_date'}' ";				
		}
		
		if($in{'sb'}){
			$qry2 .= " ORDER BY $in{'sb'} ";
			if($in{'st'}){
				$qry2 .= " $in{'so'} ";
			}
		}
		@db_cols = ('ID_returns','Date','Type','merAction','FirstName','LastName1','ID_customers');

		my $query = " sl_returns.id_customers=sl_customers.id_customers  $qry  $qry2 ";

		$in{'nh'} ? ($nh = $in{'nh'}) : ($nh = 1);
		$numhits = 0;
		
		my ($sth) = &Do_SQL("SELECT COUNT(sl_returns.id_returns) FROM sl_returns, sl_customers WHERE $query ");
		$numhits = $sth->fetchrow();
		if ($numhits == 0){
			return (0,'');
		}
		$first = ($usr{'pref_maxh'} * ($nh - 1));
		
		my ($sth) = &Do_SQL("SELECT sl_returns.*, sl_customers.ID_customers, sl_customers.FirstName, sl_customers.LastName1 FROM sl_returns, sl_customers WHERE $query LIMIT $first,$usr{'pref_maxh'}");
		while ($rec = $sth->fetchrow_hashref){
			foreach $column (@db_cols) {
				push(@hits, $rec->{$column});
			}
		}
		return ($numhits, @hits);		
	}else{
		return &query('sl_returns');
	}
}

sub view_opr_repmemos {
# --------------------------------------------------------
# Created on: 06/26/2008
# Last Modified on:7/16/2008
# Last Modified by: JoaquÃ­n NuÃ±ez E. 
# Author: Jose Ramirez Garcia
# Description : Approve/Deny the replacement memo
# Parameters : chg_status
# Last Modified on: 09/04/08 16:48:18
# Last Modified by: MCC C. Gabriel Varela S: Se agrega funciÃ³n &calc_tax_disc_shp
	
  $va{'authby'}='';
  $va{'invoice_link'}='';
  
  if($in{'chg_status'}){
		my ($sth) = &Do_SQL("SELECT Status FROM sl_repmemos WHERE ID_repmemos=$in{'id_repmemos'};");
		$old_status = $sth->fetchrow;
		if($old_status eq "New"){			
			if(&Do_SQL("UPDATE sl_repmemos SET Status='$in{'chg_status'}',AuthBy='$usr{'id_admin_users'}' WHERE ID_repmemos=$in{'id_repmemos'} AND Status='New';")){
				my ($sth) = &Do_SQL("SELECT Status FROM sl_repmemos WHERE ID_repmemos=$in{'id_repmemos'};");
				$in{'status'} = $sth->fetchrow;
				my ($sth) = &Do_SQL("INSERT INTO sl_orders_products (ID_products, ID_orders, Saleprice, Quantity, Status, Date, Time, ID_admin_users) VALUES('$in{'id_products'}',$in{'id_orders'},0,1,'Active',Curdate(),NOW(),$usr{'id_admin_users'})");
				&calc_tax_disc_shp(0,1);
				$va{'statusmsg'} = &trans_txt('opr_repmemos_statusupdate')." ".$in{'status'};
			}
		}
	}
	
	if($in{'status'} eq "New"){
		$va{'modifystatusrm'} = qq|&nbsp;&nbsp; 
			<a href="#"><img src='[va_imgurl]/[ur_pref_style]/b_ok.png' title='Approve Replacement Memo' alt='' border='0' onClick='if(confirm("Do you want to APPROVE this replacement memo?")){trjump("[va_script_url]?cmd=[in_cmd]&view=[in_id_repmemos]&chg_status=Approved")}'></a>
			&nbsp;&nbsp;
			<a href="#"><img src='[va_imgurl]/[ur_pref_style]/b_drop.png' title='Deny Replacement Memo' alt='' border='0' onClick='if(confirm("Do you want to DENY this replacement memo?")){trjump("[va_script_url]?cmd=[in_cmd]&view=[in_id_repmemos]&chg_status=Denied")}'></a>|;
	}
	#&cgierr("asdasd");
	#Se obtiene el Nombre del cliente en relacion al RepMemos y al ID_order
	
	my ($sth) = &Do_SQL("SELECT sl_orders.shp_name AS name_customer FROM sl_orders,sl_customers WHERE sl_orders.ID_customers=sl_customers.ID_customers AND sl_orders.ID_orders=$in{'id_orders'};");
	$va{'name_customer'} = $sth->fetchrow;
	
	if($in{'authby'} > 0){
	  $va{'authby'} .= qq|<tr>
                        <td class="smalltext" width="30%">Authorized By : </td>
                        <td class="smalltext">|.&load_db_names('admin_users','ID_admin_users',$in{'authby'},"[LastName], [FirstName]").qq|</td>
                     </tr>|;
	}
	
	if($in{'authby'} > 0 and $in{'status'} eq "Approved"){
	  $va{'invoice_link'} = qq|<a href="" onClick="javascript:prnwin('/cgi-bin/mod/admin/admin?cmd=$in{'cmd'}&toprint=$in{'id_repmemos'}');return false;"><img src="[va_imgurl]/[ur_pref_style]/b_pinvoice.gif" title="Print RepMemo Invoice" alt="" border="0"></a>|;
	}
	
	$in{'repnotes'} = $in{'notes'};
	$in{'notes'}    = "";

}

sub validate_opr_repmemos {
# --------------------------------------------------------
# Created on: 26 JUN 2008
# Last Modified on: 7/17/2008
# Last Modified by:JoaquÃ­n Nunez E. 
# Author: Jose Ramirez Garcia
# Description : validate the replacement memo status is new
# Parameters :
	if($in{'add'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders WHERE id_orders='$in{'id_orders'}'");
		$order = $sth->fetchrow;
		if($order ne 1){
			$va{'message'} = &trans_txt('reqfields');
			$error{'id_orders'} = &trans_txt('invalid');
			++$err;
		}
		if(substr($in{'id_products'},0,1) eq 4){
			$parts = substr($in{'id_products'},5,4);
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_parts WHERE id_parts='$parts'");
			$products = $sth->fetchrow;
			if($products ne 1){
				$va{'message'} = &trans_txt('reqfields');
				$error{'id_products'} = &trans_txt('invalid');
				++$err;
			}			
		} else {
			my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_skus WHERE ID_sku_products='$in{'id_products'}'");
			$products = $sth->fetchrow;
			if($products < 1){
				$va{'message'} = &trans_txt('reqfields');
				$error{'id_products'} = &trans_txt('invalid');
				++$err;
			}
		}
	} elsif($in{'edit'}){
		if($in{'status'} ne "New"){
			$va{'message1'} = &trans_txt('blocked');
			#$error{'status'} = &trans_txt('invalid');
			++$err;
		}
	}
	return $err;
}



sub validate_opr_chargebacks{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/12/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 

	my ($err);
	if(!$in{'id_orders'}){
		$error{'id_orders'} = &trans_txt('required');
		$va{'message'} = &trans_txt('reqfields');
		++$err;
	}
	if(!$in{'id_products'}){
		$error{'id_products'} = &trans_txt('required');
		$va{'message'} = &trans_txt('reqfields');
		++$err;
	}
	if($in{'id_orders_products'} && $in{'id_orders'} && $in{'id_products'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='".$in{'id_orders'}."' AND ID_products='".$in{'id_products'}."' AND ID_orders_products='".$in{'id_orders_products'}."' ");
		if($sth->fetchrow!=1){
			$error{'id_orders'} = &trans_txt('invalid');
			$error{'id_products'} = &trans_txt('invalid');
			++$err;
		}
	}
	return $err;

}

sub view_opr_chargebacks {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/12/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if ($in{'id_orders_products'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products='$in{'id_orders_products'}'");
		my ($rec) = $sth->fetchrow_hashref;
		my (@cols)= ('ID_orders','ID_products');
		for (0..$#cols){
			$in{lc($cols[$_])} = $rec->{$cols[$_]};
			$in{'orders_products.'.lc($cols[$_])} = $rec->{$cols[$_]};
		}
		$va{'id_products'} = substr($rec->{ID_products},3,6);
		$va{'products_desc'} = substr($in{'orders_products.id_products'},3,9)." (".&load_db_names('sl_products','ID_products',substr($rec->{ID_products},3,6),'[Name] [Model]')." ".&load_db_names('sl_skus','ID_sku_products',$rec->{ID_products},'[choice1] [choice1] [choice3] [choice4]').")";
	}
}

sub loading_opr_chargebacks {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if ($in{'id_orders_products'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products='$in{'id_orders_products'}'");
		my ($rec) = $sth->fetchrow_hashref;
		my (@cols)= ('ID_orders','ID_products');
		for (0..$#cols){
			$in{lc($cols[$_])} = $rec->{$cols[$_]};
			$in{'orders_products.'.lc($cols[$_])} = $rec->{$cols[$_]};
		}
	}
}

sub advsearch_opr_chargebacks {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if(($in{'id_orders'} || $in{'id_products'}) && !$in{'id_orders_products'}){
		my ($qry);
		if($in{'id_orders'}){
			$qry = " ID_orders='".$in{'id_orders'}."' ";
		}
		if($in{'id_products'}){
			$qry .= " ID_products='".$in{'id_products'}."' ";
		}
		my ($sth)	= &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE $qry");
		$in{'id_orders_products'} = $sth->fetchrow_array;
	}
	return &query('sl_chargebacks');

}


##########################################################
##	OPERATIONS : CREDITMEMO
##########################################################
sub loaddefault_opr_creditmemos {
# --------------------------------------------------------
	$in{'status'} = 'New';
}

sub validate_opr_creditmemos {
# --------------------------------------------------------
	if (!$in{'id_customers'}){
		$err++;
		$error{'id_customers'} = &trans_txt('invalid');
	}

	if ($in{'add'}){
		$in{'status'} = 'New';
		$in{'id_exchangerates'} = 0;
	}

	if ($in{'edit'}){

		### Revisa que no se modifique el Cliente si el CM ya está aprovado o aplicado
		my ($id_customers_current, $status_current) = &load_name('sl_creditmemos', 'ID_creditmemos', $in{'id_creditmemos'}, 'ID_customers,Status');
		if( $status_current ne 'New' and $id_customers_current != $in{'id_customers'} ){
			$err++;
			$error{'id_customers'} = &trans_txt('invalid');
		}

	}

	return $err;
}


#############################################################################
#############################################################################
#   Function: view_opr_creditmemos
#
#       Es: Vista de Credit Memos
#       En: 
#
#
#    Created on: 
#
#    Author: Roberto Barcenas
#
#    Modifications:
#		- 09/07/2014: Se hace reingenieria de productos. Se agrupa por porcentaje y se inserta en orders_products como un porcentaje del total del credit memo, basado en el monto de devolucion total / monto de la orden 
#
#
#   Parameters:
#
#      - 
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub view_opr_creditmemos {
#############################################################################
#############################################################################
	## Validation
	$in{'addorder'} = int($in{'addorder'});
	$in{'delorder'} = int($in{'delorder'});
	$va{'currency'} = load_name('sl_customers', 'ID_customers', $in{'id_customers'}, 'Currency');

	my ($err);
	
	if ($cfg{'shptax'}){
		my ($sth) = &Do_SQL("SELECT ROUND(SUM((SalePrice * Quantity) - Discount + Tax + IFNULL(Shipping,0) + (IFNULL(Shipping,0) * IF(ShpTax_percent>0,(ShpTax_percent/100),0))),2) FROM sl_creditmemos_products WHERE ID_creditmemos='$in{'id_creditmemos'}' GROUP BY ID_creditmemos;");
		$in{'amount'} = $sth->fetchrow();	
	}else{
		my ($sth) = &Do_SQL("SELECT ROUND(SUM((SalePrice * Quantity) - Discount + Tax + IF(Shipping IS NULL,0,Shipping)),2) FROM sl_creditmemos_products WHERE ID_creditmemos='$in{'id_creditmemos'}' GROUP BY ID_creditmemos;");
		$in{'amount'} = $sth->fetchrow();
	}

	##############################################################################
	##############################################################################
	##############################################################################
	###
	### 								Actions
	###
	##############################################################################
	##############################################################################
	##############################################################################
	
	if ($in{'addorder'}>0 and $in{'status'} ne 'Applied'){

		################
		################ TAB2: Agrega una orden al creditmemo
		################
		my ($sth) = &Do_SQL("REPLACE INTO sl_creditmemos_payments SET ID_orders = '$in{'addorder'}', ID_creditmemos='$in{'id_creditmemos'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'}");
	
	}elsif($in{'delorder'} and $in{'status'} eq 'New'){

		my ($sth) = &Do_SQL("DELETE FROM sl_creditmemos_payments WHERE ID_orders='$in{'delorder'}' AND ID_creditmemos='$in{'id_creditmemos'}'");

	}elsif($in{'delprod'} and $in{'status'} eq 'New'){

		my ($sth) = &Do_SQL("DELETE FROM sl_creditmemos_products WHERE ID_creditmemos_products='$in{'delprod'}'");
		#se puede borrar un servicio de devolucion de mercancia cuando el CM esta aprobado
		
	}elsif($in{'delprod'} and $in{'status'} eq 'Approved'){
		$sth = &Do_SQL("select ID_creditmemos_products from direksys2_e3.sl_creditmemos_products where ID_creditmemos=6785 and id_products='400001043';");
		$ID_creditmemos_products = $sth->fetchrow();
		if($ID_creditmemos_products > 0){
			my ($sth) = &Do_SQL("DELETE FROM sl_creditmemos_products WHERE ID_creditmemos_products='$in{'delprod'}'");
		}
	
	}elsif($in{'addsku'}>0 and $in{'status'} eq 'New'){
		#Se agregan productos siempre y cuando el CM no se hubiese vinculado con un pago
		my $this_customer_currency = &load_name('sl_customers', 'ID_customers', $in{'id_customers'}, 'Currency');
		my ($tax_porc) = ( $cfg{'acc_default_currency'} ne '' and uc($this_customer_currency) ne uc($cfg{'acc_default_currency'})) ? 0 : &load_name('sl_parts','ID_parts',$in{'addsku'},'Sale_Tax');

		&Do_SQL("INSERT INTO sl_creditmemos_products SET ID_creditmemos='$in{'id_creditmemos'}',Tax_percent='$tax_porc', ID_products=400000000+$in{'addsku'},Quantity=1,Status='Active',Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'}");

	}elsif($in{'addserv'}>0 and $in{'status'} eq 'New'){

		my ($tax) = &load_name('sl_services','ID_services',$in{'addserv'},'Tax');
		my ($sth) = &Do_SQL("INSERT INTO sl_creditmemos_products SET ID_creditmemos='$in{'id_creditmemos'}',Tax_percent='$tax', ID_products=600000000+$in{'addserv'},Quantity=1,Status='Active',Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'}");
	
	}elsif($in{'update_prods'} and $in{'status'} ne 'Applied'){
		
		###
		### UPDATE PRODUCTS
		###
		
		my ($err);
		foreach my $key (keys %in){
			if ($key =~ /prods_qty_(\d+)/){
				if ($in{$key}>0){
					my ($sth) = &Do_SQL("SELECT * FROM sl_creditmemos_products WHERE ID_creditmemos_products='$1'");
					$rec = $sth->fetchrow_hashref;
					if ($rec->{'ID_products'} >= 400000000 and $rec->{'ID_products'} < 500000000){
						$taxxxx = &load_name('sl_parts','ID_parts',($rec->{'ID_products'} - 400000000),'Sale_Tax');
					}
					if ($rec->{'ID_products'} >= 600000000){}
					#Los productos se pueden modificar si el CM no esta aplicado
					#Los servicios se modifican solo en New
					#@ivanmiranda
					if($in{'status'} eq 'New'){
					# if(
					# 	($in{'status'} eq 'New' and $rec->{'ID_products'} >= 600000000)
					# 	or
					# 	($in{'status'} eq 'Approved' and $rec->{'ID_products'} >= 400000000 and $rec->{'ID_products'} < 500000000)
					# ){
						my $tax_percent = ($rec->{'Tax_percent'}) ? ($rec->{'Tax_percent'}/100):0;
						# &cgierr($taxxxx.'<-'.$tax_percent.'->'.$rec->{'ID_products'});
						my $tax = &round(((($in{'prods_saleprice_'.$1}*$in{'prods_qty_'.$1})-$in{'prods_discount_'.$1}) * $tax_percent), $sys{'fmt_curr_decimal_digits'});
						# $in{'prods_saleprice_'.$1} = ($in{'prods_saleprice_'.$1}*$in{'prods_qty_'.$1}) + $tax;
						my ($sth) = &Do_SQL("UPDATE sl_creditmemos_products SET Quantity='$in{'prods_qty_'.$1}',
							Saleprice='$in{'prods_saleprice_'.$1}',
							Shipping='$in{'prods_shipping_'.$1}', 
							Tax='$tax',
							Cost='$in{'prods_cost_'.$1}',
							Discount='$in{'prods_discount_'.$1}'
							WHERE ID_creditmemos_products=$1");
					}
				}else{

					my ($sth) = &Do_SQL("DELETE FROM sl_creditmemos_products WHERE ID_creditmemos_products=$1");
				
				}
			}
		}
		if (!$err){
			$va{'message'} = &trans_txt('opr_creditmemos_amnts');
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}

	}elsif($in{'update_amounts'} and $in{'status'} ne 'Applied' and $in{'tab'} eq '2' ){

		###
		### UPDATE AMOUNTS
		###

		my ($err);
		my ($orderamounttotal)=0;

		#my ($sthp2) = &Do_SQL("SELECT SUM( (SalePrice * Quantity) + Tax - Discount ) FROM sl_creditmemos_products WHERE ID_creditmemos = '$in{'id_creditmemos'}';");
		#my ($sthp2) = &Do_SQL("SELECT ROUND(SUM( (SalePrice * Quantity) + IFNULL(Shipping,0) + (IFNULL(Shipping,0) * IF(Tax_percent>0,(Tax_percent/100),0)) + Tax - Discount ), 2) FROM sl_creditmemos_products WHERE ID_creditmemos = '$in{'id_creditmemos'}';");
		#my $max_allowed = round($sthp2->fetchrow(),2);
		my $max_allowed = $in{'amount'};
		
		foreach my $key (sort keys %in){

			if ($key =~ /orderamount_(\d+)/){

				$in{$key} =~ s/\$|\,//;
				my $id_orders = $1;
				next if !$id_orders;

				my $this_amount = round($in{$key} - 0,2);
				my ($totals) = &check_ord_totals($id_orders);
				
				if ($totals =~ /Products|Payments|Tax|Shipping|Discount/){

					++$err;
					$error{'order'.$id_orders} = &trans_txt('invalid') . ' : ' . $totals ;

				}


				##################
				################## START -  Seccion con el mismo codigo que tab2 de creditmemos.cgi
				################## Si se mueve logica aqui, debe revisare el otro archivo
				##################
				my ($sth1) = &Do_SQL("SELECT SUM(SalePrice + Shipping + Tax + ShpTax - Discount), MAX(Tax_percent) FROM sl_orders_products WHERE ID_orders = '$id_orders' AND Status NOT IN('Order Cancelled','Inactive');");
				my ($sth2) = &Do_SQL("SELECT IFNULL(SUM(Amount),0) FROM sl_orders_payments WHERE ID_orders = '$id_orders' AND Reason='Sale' AND (Captured='No' OR Captured IS NULL OR Captured = '' OR CapDate IS NULL OR CapDate = '0000-00-00');");			
				my ($order_total, $tax_pct) = $sth1->fetchrow();
				my ($order_unpaid) = $sth2->fetchrow();
				my ($amt_increditmemos) = 0;#$sth3->fetchrow();
				(!$amt_increditmemos) and ($amt_increditmemos = 0);
				my $topay = round($order_unpaid - $amt_increditmemos,2);

				if($amt_increditmemos + $max_allowed > $order_unpaid){
					$max_allowed -= round($amt_increditmemos,2);
				}
				#$max_allowed -= round($amt_increditmemos,2);
				##################
				################## END -  Seccion con el mismo codigo que tab2 de creditmemos.cgi
				##################

				#Si hay devolucion pendiente en transito, permitir aplicar el monto sin validar saldo (el saldo ya se descontó previamente)
				my ($sth) = &Do_SQL("SELECT COUNT(DISTINCT ID_movements) FROM sl_movements WHERE tablerelated = 'sl_creditmemos' AND ID_tablerelated = '". $in{'id_creditmemos'} ."' AND Category = 'Cobranza' AND Status = 'Active';");
				my ($bol_pendiente_transito) = $sth->fetchrow();
				if($bol_pendiente_transito) {
					$topay = $this_amount;
				}

				## Debugging?
				$str_deb .= "IDO: $id_orders<br>OT: $order_total<br>UN: $order_unpaid<br>INC:$amt_increditmemos<br>MAX: $max_allowed<br>AMT: $this_amount<br>TOPAY: $topay<br>";
				#&cgierr($str_deb);

				if( $this_amount <= $topay ){

					if( $this_amount <= $max_allowed or abs($this_amount - $max_allowed) < 0.01 ){

						$orderamounttotal += $this_amount;
						my ($sth) = &Do_SQL("REPLACE INTO sl_creditmemos_payments SET ID_orders = '". $id_orders ."', Amount = ROUND($in{$key},2), ID_creditmemos = '". $in{'id_creditmemos'} ."', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
						$max_allowed -= $this_amount;

					}else{

						++$err;
						$error{'order'.$id_orders} = &trans_txt('invalid') . ' : ' . $max_allowed;

					}

				}else{

					++$err;
					$error{'order'.$id_orders} = &trans_txt('invalid') . ' : ' . $max_allowed;
					#&cgierr($str_deb . "<br>Fallo: $this_amount <= $max_allowed  and $this_amount <= $topay ");

				}


				###
				### Orden S/Tax ?
				###
				if($tax_pct == 0){
					&Do_SQL("UPDATE sl_creditmemos_products SET Saleprice = Saleprice, Tax = '0', Tax_percent = '0', Shipping = Shipping + ShpTax, ShpTax = '0', ShpTax_percent = '0' WHERE ID_creditmemos = '". $in{'id_creditmemos'} ."';");
				}

			}
		}
		#&cgierr($orderamounttotal);
		
		if (!$err){

			if (  $orderamounttotal >= $in{'amount'} and abs($orderamounttotal - $in{'amount'}) >= 0.01 ){
				$va{'message'} = &trans_txt('opr_creditmemos_amnts_exceeds').": ".&format_price($orderamounttotal)." > ".&format_price($in{'amount'});
				
			}else{

				$va{'message'} = &trans_txt('opr_creditmemos_amnts');

			}

		}else{

			$va{'message'} = &trans_txt('reqfields');

		}

	}

	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_creditmemos_payments WHERE ID_creditmemos=$in{'id_creditmemos'}");
	my ($total_amnt) = $sth->fetchrow();
    $in{'amount'} = &round($in{'amount'}, $sys{'fmt_curr_decimal_digits'});
    $total_amnt = &round($total_amnt, $sys{'fmt_curr_decimal_digits'});

    if ($total_amnt - $in{'amount'} == 0 and $in{'amount'} > 0){

		if  ($in{'chhto_new'} and $in{'status'} eq 'Approved'){

			my ($sth) = &Do_SQL("UPDATE sl_creditmemos SET Status='New' WHERE ID_creditmemos=$in{'id_creditmemos'}");
			$in{'status'} = 'New';
			&auth_logging('opr_creditmemos_new',$in{'id_creditmemos'});
			$va{'message'} = &trans_txt('opr_creditmemos_new');
			
		}elsif($in{'chhto_approved'} and $in{'status'} eq 'New' and &check_permissions('opr_creditmemos_approved','','')){

			
			### 							###
			###  Credit Memo To Approved    ###
			###								###
			
			##validation
			my ($sth) = &Do_SQL("SELECT 
									COUNT(DISTINCT AuthCode) 
								FROM 
									sl_orders_payments 
								WHERE 
									AuthCode = 'CM-". $in{'id_creditmemos'} ."';");
			my ($bol_pagos_aplicados) = $sth->fetchrow();

			if(!$bol_pagos_aplicados){

				## Change Status
				my ($sth) = &Do_SQL("UPDATE sl_creditmemos SET Status = 'Approved' WHERE ID_creditmemos = '". $in{'id_creditmemos'} ."';");
				&auth_logging('opr_creditmemos_approved',$in{'id_creditmemos'});
				$in{'status'} = 'Approved';
				$va{'message'} = &trans_txt('opr_creditmemos_approved')."\n<br>";

			}			

		}elsif ($in{'chhto_applied'} and $in{'status'} eq 'Approved' and &check_permissions('opr_creditmemos_applied','','')){

			###################################
			### 							###
			###  Credit Memo Application    ###
			### 							###
			###################################

			## Inicializa la transaccion
			$va{'this_accounting_time'} = time();
			my $flag_max_amount = 0;
			&Do_SQL("START TRANSACTION;");

			my ($err,$rec);			

			############
			############ 1.1) Validacion Currency / Exchange Rate
			############
			my $currency_exchange = 1; my $idexr = 0;
			$this_customer_currency = &load_name('sl_customers', 'ID_customers', $in{'id_customers'}, 'Currency');
			if( $cfg{'acc_default_currency'} ne '' and uc($this_customer_currency) ne uc($cfg{'acc_default_currency'})){

				my ($sth) =  &Do_SQL("SELECT ID_exchangerates, exchange_rate FROM sl_exchangerates WHERE UPPER(Currency) = '". uc($this_customer_currency) ."' AND Date_exchange_rate >= DATE_SUB(CURDATE(), INTERVAL 3 DAY) ORDER BY Date_exchange_rate DESC LIMIT 1;");
				($idexr, $currency_exchange) = $sth->fetchrow();
				$currency_exchange = 0 if !$currency_exchange;

				if($currency_exchange){
					&Do_SQL("UPDATE sl_creditmemos SET ID_exchangerates = '". $idexr ."' WHERE ID_creditmemos = '$in{'id_creditmemos'}';");
				}else{
					$add_msg .= qq|<br>No Exchange Rate Found|;
					++$err;
				}

			}

			############
			############ 1.2) Validacion Monto Pendiente en Orden
			############
			## Credit Memo aplicado anteriormente?
			my ($sth) = &Do_SQL("SELECT 
									COUNT(DISTINCT AuthCode) 
								FROM 
									sl_orders_payments 
								WHERE 
									AuthCode = 'CM-". $in{'id_creditmemos'} ."';");
			my ($bol_pagos_aplicados) = $sth->fetchrow();
			if(!$bol_pagos_aplicados) {
			
				###
				### 1.2.1) Validacion monto en orden(saldo)
				###
				my ($sth) = &Do_SQL("SELECT * FROM sl_creditmemos_payments WHERE ID_creditmemos = '". $in{'id_creditmemos'} ."';");
				while ($rec = $sth->fetchrow_hashref){
					
					my ($sth2) = &Do_SQL("SELECT 
											SUM(ROUND(Amount,2)) 
										FROM 
											sl_orders_payments 
										WHERE 
											ID_orders = '". $rec->{'ID_orders'} ."'
											AND ( sl_orders_payments.Captured != 'Yes' OR sl_orders_payments.Captured IS NULL ) 
											AND ( sl_orders_payments.CapDate IS NULL OR sl_orders_payments.CapDate ='0000-00-00')
										GROUP BY 
											ID_orders
										HAVING  
											SUM(ROUND(Amount,2)) >= '". $rec->{'Amount'} ."';");
					my ($tot_paym) = $sth2->fetchrow();
					++$err if (!$tot_paym);
				}

			}
			

			## Validacion NO se puede aplicar sin tener la devolucion previamente en el almacen
			my ($this_res, $this_message) = &creditmemos_return_validation($in{'id_creditmemos'});
			if ($this_res !~ /ok/i){

				$err++;
				$add_msg .= "<br>".&trans_txt('incomplete_return_in_cm') . "<br>" . $this_message;

			}
			$va{'old_process_flag'} = 1 if $this_message == 2;

			############
			############ 2) Aplicacion
			############
			if (!$err){

				my ($sth) = &Do_SQL("SELECT * FROM sl_creditmemos_payments WHERE ID_creditmemos = '". $in{'id_creditmemos'} ."';");
				while ( $rec = $sth->fetchrow_hashref() ){
					
					my ($cm_amount) = abs($rec->{'Amount'});
					my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '". $rec->{'ID_orders'} ."';");
					my($order_type, $ctype) = $sth->fetchrow();

					############
					############ 2.1) Products
					############
					my @ary_tax; my $cm_type; my $quantity = 1; my $total_sale = 0; my $total_saleprice = 0; my $total_discount = 0; my $total_tax = 0;
					my ($sth9) = &Do_SQL("SELECT 
											SUM(sl_creditmemos_products.SalePrice * sl_creditmemos_products.Quantity + sl_creditmemos_products.Shipping)
											, SUM(sl_creditmemos_products.Discount)
											, SUM(sl_creditmemos_products.Tax + sl_creditmemos_products.ShpTax)
											, SUM(IF(LEFT(ID_products,1) = 4,1,0)) AS Products
											, SUM(IF(LEFT(ID_products,1) = 6,1,0)) AS Services
											, Tax_percent
											FROM 
												sl_creditmemos_products 
											WHERE 
												ID_creditmemos = '". $in{'id_creditmemos'} ."'
											GROUP BY 
												Tax_percent;");
					
					while( my ($cm_saleprice, $cm_discount, $cm_tax, $cm_prod, $cm_ser, $tax_pct) = $sth9->fetchrow()){

						${'saleprice_' . $tax_pct}  = $cm_saleprice; 
						$total_saleprice += round($cm_saleprice,2);
						
						${'discount_' . $tax_pct}  = $cm_discount; 
						$total_discount += round($cm_discount,2);

						${'tax_' . $tax_pct}  = $cm_tax; 
						$total_tax += round($cm_tax,2);
						
						push(@ary_tax, $tax_pct);
						$cm_type = $cm_prod > 0 ? 'prod' : 'ser'; 
						
					}
					
					############
					############ 2.1.1) Calculamos porcentaje correspondiente
					############
					# 1 - Total Creditmemo = $total_sale
					# 2 - Total Amount by Order = $cm_amount
					# 3 - Percentage by Order = round( ($cm_amount / $total_sale) * 100,3)

					$total_saleprice -= $total_discount;
					$total_sale = $total_saleprice + $total_tax;
					my $this_order_pct = ($total_sale > 0) ? round( $cm_amount / $total_sale,6) : 0;

					for(0..$#ary_tax){

						############
						############ 2.1.1) Guardamos linea en sl_orders_products por cada tax diferente
						############

						my $tax_percent = $ary_tax[$_];
						my $this_saleprice = round( ${'saleprice_' . $tax_percent} * $this_order_pct,2);
						my $this_discount = round( ${'discount_' . $tax_percent} * $this_order_pct,2);
						my $this_tax = round( ${'tax_' . $tax_percent} * $this_order_pct,2);
						my $this_op_amount = $this_saleprice - $this_discount + $this_tax;
						my $this_diff = round(abs($cm_amount - $this_op_amount),2);

						if($this_diff > 0){

							if( $this_diff < 1 and $cm_amount > $this_op_amount ){
								$this_saleprice += $this_diff;
							}elsif( $this_diff < 1 and $cm_amount < $this_op_amount ){
								$this_tax -= $this_diff;
							}

						}						

						## Se inactiva el proceso que genera la contabilidad
						if(!$in{'transition'} and !$va{'old_process_flag'} ){

							my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_creditmemos_products WHERE ID_creditmemos = '". $in{'id_creditmemos'} ."' AND LEFT(sl_creditmemos_products.ID_products,1) = 6 AND sl_creditmemos_products.Status = 'Active';");
							my ($bol_service) = $sth->fetchrow();
							my $devol_type = $bol_service ? '' : 'PRODUCTO';

							############ 3) Mov. Contables
							if($bol_service){

								my @params = ($rec->{'ID_orders'},$this_saleprice,$this_tax,$currency_exchange,$cm_type,$in{'id_creditmemos'},$devol_type);
								&accounting_keypoints('order_credit_memos_'. $ctype .'_'. $order_type, \@params );

							}

						}	

					}
					&recalc_totals($rec->{'ID_orders'});


					if(!$bol_pagos_aplicados){

						############
						############ 2.2) Payments | Los pagos pueden haber sido aplicados en la aprobacion
						############
						my $i = 0;
						my $applied_payment = 0; my $new_applied_payment = 0;
						do{

							++$i;
							my ($sth_p) = &Do_SQL("SELECT ID_orders_payments, ABS(Amount) FROM sl_orders_payments WHERE ID_orders = '". $rec->{'ID_orders'} ."' AND ROUND(Amount, 2) > 0.1 AND (Captured IS NULL OR Captured = 'No' OR Captured = '') AND (CapDate IS NULL OR CapDate = '0000-00-00') AND Status IN('Approved','Financed','Denied','Pending','Insufficient Funds') ORDER BY Paymentdate, ID_orders_payments ;");
							my ($this_id, $this_amount) = $sth_p->fetchrow();

							if($this_id){
								
								$applied_payment = $this_id;
								#########
								######### 2.1.1) Order has Payments to Pay
								#########
								if($cm_amount >= $this_amount){

									#########
									######### 2.1.1.1) Return Amount is Greater or equal than debt
									#########
									&Do_SQL("UPDATE sl_orders_payments SET Status = 'Approved', Paymentdate = CURDATE(), CapDate = CURDATE(), Captured = 'Yes', AuthCode = 'CM-". $in{'id_creditmemos'} ."', Reason = 'Sale' WHERE ID_orders_payments = '". $this_id ."';");
									$cm_amount -= round($this_amount,2);

								}else{

									#########
									######### 2.1.1.2) Credit is greater than Return Amount
									#########
									&Do_SQL("UPDATE sl_orders_payments SET Amount = (Amount - ". $cm_amount .") WHERE ID_orders_payments = '". $this_id ."';");
									my (%overwrite) = ('amount' => $cm_amount, 'pmtfield8' => '1' ,'authcode' => 'CM-' . $in{'id_creditmemos'}, 'authdatetime' => 'NOW()', 'captured' => 'Yes', 'capdate' => 'CURDATE()', 'status' => 'Approved', 'reason' => 'Sale');
									$new_applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders_payments = '". $this_id ."'", "", "", %overwrite);
									$cm_amount = 0;
									
								}

							}else{
								
								#########
								######### 2.1.2) Order Has Not more Payments to Pay
								#########
								if($cm_amount < 1) {

									my (%overwrite) = ('amount' => $cm_amount, 'pmtfield8' => '1' ,'authcode' => 'CM-' . $in{'id_creditmemos'}, 'authdatetime' => 'NOW()', 'captured' => 'Yes', 'capdate' => 'CURDATE()', 'status' => 'Approved', 'reason' => 'Sale');
									$new_applied_payment = &Do_selectinsert('sl_orders_payments', "ID_orders = '". $id_orders ."' AND Status NOT IN('Void','Order Cancelled','Cancelled','Credit')", "ORDER BY CapDate DESC, Captured = 'Yes', AuthDateTime DESC, LENGTH(AuthCode) DESC, Paymentdate DESC, ID_orders_payments ", " LIMIT 1", %overwrite);
									&Do_SQL("UPDATE sl_orders_payments SET Paymentdate = CURDATE(), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}' WHERE ID_orders_payments = '". $new_applied_payment ."';");

								}else{

									$flag_max_amount = 1;

								}
								$cm_amount = 0;

							}

						}while($cm_amount > 0 or $i > 20);
						
						my ($sth2) = &Do_SQL("UPDATE sl_creditmemos_payments SET ID_orders_payments = '". $applied_payment ."', ID_orders_payments_added = '". $new_applied_payment ."', ID_orders_products_added = '". $idprod ."' WHERE ID_creditmemos_applied = '". $rec->{'ID_creditmemos_applied'} ."';");
						
					} ## if !bol_pagos_aplicados



					if($in{'transition'}){

						### Transition
						$txtTransition="\nMode: [Transition] ";
						&Do_SQL("INSERT INTO sl_creditmemos_notes SET ID_creditmemos = '". $in{'id_creditmemos'} ."', Notes = '".$txtTransition."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

					}


					&add_order_notes_by_type( $rec->{'ID_orders'},&trans_txt('opr_creditmemos_applied')."\nCredit Memo: $in{'id_creditmemos'}\nAmount: ".&format_price($rec->{'Amount'}).$txtTransition,"Low");
					
					$in{'db'} = 'sl_orders';
					&auth_logging('opr_creditmemos_applied',$rec->{'ID_orders'});		
					$in{'db'} = 'sl_creditmemos';		

				} ## while payments		

				my ($sth) = &Do_SQL("UPDATE sl_creditmemos SET Status = 'Applied' WHERE ID_creditmemos = '". $in{'id_creditmemos'} ."';");
				$in{'status'} = 'Applied';
				&auth_logging('opr_creditmemos_applied',"$in{'id_creditmemos'}");
				$va{'message'} = &trans_txt('opr_creditmemos_applied');

				# &payment_logging($id_banks_movements, $in{'id_customers'}, 'Apply', $invoices[$i]{'amount'}, 'cu_invoices', $invoices[$i]{'id_invoices'});
				##
				### Validaciones Finales para Commit
				##		
				if($flag_max_amount){

					## El pedido no tenia el monto que se queria aplicar
					$va{'message'} = &trans_txt('opr_creditmemos_ordermaxamount');
					&Do_SQL("ROLLBACK;");

				}else{

					&Do_SQL("COMMIT;");

				}

			}else{

				$va{'message'} = &trans_txt('opr_creditmemos_applied_err');
				$va{'message'} .= $add_msg;

				&Do_SQL("ROLLBACK;");

			}		
		}
		delete($va{'this_accounting_time'});
		
		if($in{'transition'}){

			$vTransition='&transition=1'; 
			$selTransition1='selected'; 
			$selTransition2='';

		}else{

			$vTransition='';
			$selTransition1='';
			$selTransition2='selected';

		}		

	}

	###
	### Opciones para Aplicar o Desaprobar el CM
	###
	if($in{'status'} eq 'Approved'){
		
		### 'desaprobación' de los CM
		### Solo se mostrará esta opción si es un CM de Servicios
		if( !$total_amt_prods or $total_amt_prods <= 0 ){
			$va{'action_status'} = qq|&nbsp;&nbsp;&nbsp;
			<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=$in{'id_creditmemos'}&tab=2&chhto_new=1" onclick="return Confirm_to_continue()">
				<img src="$va{'imgurl'}/$usr{'pref_style'}/b_drop.png" title='un Aprroved' alt='' border='0'>
			</a>|;
		}
		$va{'action_status'} .= qq|<span id="ok">
			<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=$in{'id_creditmemos'}&tab=2&chhto_applied=1"  onclick="return Confirm_to_continue()">
				<img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" title='Applied' alt='' border='0'>
			</a>
		</span>|;

	}else{
		$va{'view_transition'}='';
	}

	###
	### Opcion para aprobar el CM aún sin Orden ligada
	###	
	my $sql_cm_prod = "SELECT COUNT(*) FROM sl_creditmemos_products WHERE ID_creditmemos = ".$in{'id_creditmemos'}." AND `Status` = 'Active';";
	my $sth_cm_prod = &Do_SQL($sql_cm_prod);
	my $prod_cm_ok = $sth_cm_prod->fetchrow();

	if( $in{'status'} eq 'New' and &check_permissions('opr_creditmemos_approved','','') and ($prod_cm_ok) > 0 ){
		$va{'action_status'} = qq|&nbsp;&nbsp;&nbsp;
										<span id="ok"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_creditmemos&view=$in{'id_creditmemos'}&tab=2&chhto_approved=1" onclick="return Confirm_to_continue()">
											<img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" title='Approve' alt='' border='0'>
										</a></span>|;
	}
	
	## Customer
	$va{'customer_name'} = &load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[company_name]/[FirstName] [LastName1]');
	
	## Product
	if ($in{'id_products'} > 600000000){
		$va{'productname'} = &load_name('sl_services','ID_services',$in{'id_products'}-600000000,'Name');
		$va{'prodlink'}    = "/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=".($in{'id_products'}-600000000);
	}else{
		$va{'productname'} = &load_db_names('sl_parts','ID_parts',$in{'id_products'}-400000000,'[Name]/[Model]');
		$va{'prodlink'}    = "/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".($in{'id_products'}-400000000);
	}
	$in{'id_products'} = &format_sltvid($in{'id_products'});	
	

	## Recalc Amount
	if ($cfg{'shptax'}){
		my ($sth) = &Do_SQL("SELECT ROUND(SUM((SalePrice * Quantity) - Discount + Tax + IFNULL(Shipping,0) + (IFNULL(Shipping,0) * IF(ShpTax_percent>0,(ShpTax_percent/100),0))),2) FROM sl_creditmemos_products WHERE ID_creditmemos='$in{'id_creditmemos'}' GROUP BY ID_creditmemos;");
		$in{'amount'} = $sth->fetchrow();	
	}else{
		my ($sth) = &Do_SQL("SELECT ROUND(SUM((SalePrice * Quantity) - Discount + Tax + IF(Shipping IS NULL,0,Shipping)),2) FROM sl_creditmemos_products WHERE ID_creditmemos='$in{'id_creditmemos'}' GROUP BY ID_creditmemos;");
		$in{'amount'} = $sth->fetchrow();
	}

	$in{'amount'} = &format_price($in{'amount'});

}

#############################################################################
#############################################################################
#   Function: load_creditmemos_orders
#
#       Es: Genera un listado de ordenes asociados al Creditmemo
#       En: Generates a list of orders associated with the Creditmemo
#
#
#    Created on: 2013-07-02
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub load_creditmemos_orders{
	$output = "";
	
	my ($sth) = &Do_SQL("SELECT sl_orders.ID_orders, sl_orders.Date,sl_orders.OrderNet, sl_orders.Status, sl_creditmemos_payments.Amount FROM sl_creditmemos_payments LEFT JOIN sl_orders ON sl_creditmemos_payments.ID_orders=sl_orders.ID_orders WHERE ID_creditmemos='".&filter_values($in{'id_creditmemos'})."';");
	$va{'total'} = 0;
	my $recs=0;
	while ($rec = $sth->fetchrow_hashref){
		$recs++;
		$d = 1 - $d;
		$va{'total'} += $rec->{'Amount'};

		$output .= "<tr bgcolor='$c[$d]'>\n";
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>$recs</td>\n";
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>$rec->{'ID_orders'}</td>\n";
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".$rec->{'Date'}."</td>\n";
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($rec->{'OrderNet'})."</td>\n";
		my ($sth2) = &Do_SQL("SELECT SUM(Amount) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}' AND Amount>0 AND (Captured='No' OR Captured IS NULL);");
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($sth2->fetchrow())."</td>\n";
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&invoices_list($rec->{'ID_orders'})."</td>\n";
		$output .= "  <td class='smalltext' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".$rec->{'Status'}."</td>\n";
		$output .= "  <td class='smalltext' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($rec->{'Amount'})."</td>\n";
		$output .= "</tr>\n";
	}
	if ($va{'total'} > 0) {
		$d = 1 - $d;
		$output .= "<tr bgcolor='$c[$d]'>\n";
		$output .= "  <td class='smalltext' colspan='7' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>Total  </td>\n";
		$output .= "  <td class='smalltext' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($va{'total'})."</td>\n";
		$output .= "</tr>\n";
	}

	if ($recs==0){
		$output = qq|
			<tr>
				<td colspan='7' align='center'>|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

	return $output;
}

#############################################################################
#############################################################################
#   Function: load_creditmemos_items
#
#       Es: Genera un listado de productos y servicios asociados al Creditmemo
#       En: Generates a list of products and services associated with the Creditmemo
#
#
#    Created on: 2013-07-02
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#        - Modified on **: 
#
#   Parameters:
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <>
#
sub load_creditmemos_items {
#############################################################################
#############################################################################	
	my ($choices,$tot_qty,$total,$vendor_sku,$line,$name,$cmdlink,$unit,$output);
	$output = "";
	my (@c) = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_creditmemos_products WHERE ID_creditmemos='$in{'id_creditmemos'}'");
	if ($sth->fetchrow>0){
		my ($sth) = &Do_SQL("SELECT * 
			,(CASE 
			 	WHEN (if(ID_products is null,ID_products,ID_products)) >=400000000 and (if(ID_products is null,ID_products,ID_products)) < 500000000 
			 	THEN (SELECT Name FROM sl_parts WHERE ID_parts=((if(ID_products is null,ID_products,ID_products))-400000000)) 
			 	WHEN (if(ID_products is null,ID_products,ID_products)) >=500000000 and (if(ID_products is null,ID_products,ID_products)) < 600000000 
			 	THEN (SELECT Name FROM sl_noninventory WHERE ID_noninventory=((if(ID_products is null,ID_products,ID_products))-500000000)) 
			 	WHEN (if(ID_products is null,ID_products,ID_products)) >=600000000 
			 	THEN (SELECT Name FROM sl_services WHERE ID_services=((if(ID_products is null,ID_products,ID_products))-600000000)) 
			 	ELSE (SELECT Name FROM sl_products WHERE ID_products=((if(ID_products is null,ID_products,ID_products))-100000000)) 
			END)as Item_Description
			FROM sl_creditmemos_products WHERE ID_creditmemos='$in{'id_creditmemos'}' ORDER BY ID_creditmemos_products ASC;");
		while ($rec = $sth->fetchrow_hashref){
			$d = 1 - $d;
			++$line;
			
			## Choices
			my ($sth2) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_sku_products='$rec->{ID_products}' and Status='Active'");
			$tmp = $sth2->fetchrow_hashref;
			$choices = &load_choices('-',$rec->{'choice1'},$rec->{'choice2'},$rec->{'choice3'},$rec->{'choice4'});
			my $upc = $tmp->{'UPC'};
			
			$name = $rec->{'Item_Description'};
			## Name Model
			if ($rec->{'ID_products'} =~ /^5/){
				## Non Inventory
				$cmdlink = 'mer_noninventory';
				$unit = &load_db_names('sl_noninventory','ID_noninventory',($rec->{'ID_products'}-500000000),'[Units]');
			}elsif ($rec->{'ID_products'}  =~ /^4/){
				## Part
				$unit  = "Unit";
				$cmdlink = 'mer_parts';
			}
			
			$subtotal = ($rec->{'SalePrice'}*$rec->{'Quantity'})+$rec->{'Tax'}+$rec->{'Shipping'};
			

			$output .= "<tr bgcolor='$c[$d]'>\n";
			$output .= "   <td class='smalltext' valign='top' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>$line</td>\n";
			$output .= "   <td style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_sltvid($rec->{'ID_products'})."</td>";
			$output .= "   <td class='smalltext' valign='top' nowrap style='border-left:1px solid #555555;border-bottom:1px solid #555555;'> $name</td>\n";
			$output .= "   <td class='smalltext' valign='top' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_number($rec->{'Quantity'})."</td>\n";
			$output .= "   <td class='smalltext' valign='top' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($rec->{'SalePrice'})."</td>\n";
			$output .= "   <td class='smalltext' valign='top' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($rec->{'Shipping'})."</td>\n";			
			$output .= "   <td class='smalltext' valign='top' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($rec->{'Cost'})."</td>\n";			
			$output .= "   <td class='smalltext' valign='top' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($rec->{'Tax'})." ($rec->{'Tax_percent'} %)</td>\n";			
			$output .= "   <td class='smalltext' align='right' valign='top' nowrap style='border-left:1px solid #555555;border-bottom:1px solid #555555;'> ".&format_price($subtotal)."</td>\n";
			$output .= "</tr>\n";
			$tot_qty += $rec->{'Quantity'};
			$total  += $subtotal;
		}		
		
		if ($line > 0) {
			$d = 1 - $d;
			$output .= "<tr>\n";
			$output .= "  <td class='smalltext' colspan='8' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>Total  </td>\n";
			$output .= "  <td class='smalltext' align='right' style='border-left:1px solid #555555;border-bottom:1px solid #555555;'>".&format_price($total)."</td>\n";
			$output .= "</tr>\n";
		}
	}else{
		$output = qq| <tr>
					<td colspan='9' align="center">|.&trans_txt('search_nomatches').qq|</td>
				    </tr>\n|;
	}

	return $output;
}

##########################################################
##	OPERATIONS : DEBITMEMO
##########################################################
sub loaddefault_opr_debitmemos {
# --------------------------------------------------------
	$in{'status'} = 'New';
}

sub validate_opr_debitmemos {
# --------------------------------------------------------
	if ($in{'add'}){
		$in{'status'} = 'New';
	}
	return $err;
}




sub view_opr_debitmemos {
# --------------------------------------------------------
	## Validation
	$in{'addorder'} = int($in{'addorder'});
	$in{'delorder'} = int($in{'delorder'});

	if ($cfg{'shptax'}){
		my ($sth) = &Do_SQL("SELECT ROUND(SUM((SalePrice*Quantity)-Discount+Tax+Shipping),2) FROM `sl_debitmemos_products` WHERE `ID_debitmemos`=$in{'id_debitmemos'}");
		$in{'amount'} = $sth->fetchrow();	
			
	}else{
		my ($sth) = &Do_SQL("SELECT ROUND(SUM((SalePrice*Quantity)-Discount+Tax+Shipping),2) FROM `sl_debitmemos_products` WHERE `ID_debitmemos`=$in{'id_debitmemos'}");
		
		$in{'amount'} = $sth->fetchrow();
	}

	## Actions
	
	if ($in{'addorder'}>0 and $in{'status'} eq 'New'){
		my ($sth) = &Do_SQL("REPLACE INTO sl_debitmemos_payments SET ID_orders='$in{'addorder'}', ID_debitmemos='$in{'id_debitmemos'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'}");
	}elsif($in{'delorder'} and $in{'status'} eq 'New'){
		my ($sth) = &Do_SQL("DELETE FROM sl_debitmemos_payments WHERE ID_orders='$in{'delorder'}' AND ID_debitmemos='$in{'id_debitmemos'}'");
	}elsif($in{'delprod'} and $in{'status'} eq 'New'){
		my ($sth) = &Do_SQL("DELETE FROM sl_debitmemos_products WHERE ID_debitmemos_products='$in{'delprod'}'");
	}elsif($in{'addsku'}>0 and $in{'status'} eq 'New'){
		my ($tax_porc) = &load_name('sl_parts','ID_parts',$in{'addsku'},'Sale_Tax');
		my ($sth) = &Do_SQL("SELECT Cost FROM `sl_skus_cost` WHERE `ID_products`= 400000000+$in{'addsku'} ORDER BY Date DESC,Time DESC LIMIT 1;");
		my ($cost) = $sth->fetchrow();
		my ($sth) = &Do_SQL("INSERT INTO sl_debitmemos_products SET ID_debitmemos='$in{'id_debitmemos'}',Cost='$cost',Tax_percent='$tax_porc', ID_products=400000000+$in{'addsku'},Quantity=1,Status='Active',Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'}");
	}elsif($in{'addserv'}>0 and $in{'status'} eq 'New'){
		my ($tax) = &load_name('sl_services','ID_services',$in{'addserv'},'Tax');
		my ($sth) = &Do_SQL("INSERT INTO sl_debitmemos_products SET ID_debitmemos='$in{'id_debitmemos'}',Tax_percent='$tax', ID_products=600000000+$in{'addserv'},Quantity=1,Status='Active',Date=CURDATE(), Time=CURTIME(), ID_admin_users=$usr{'id_admin_users'}");
	}elsif($in{'update_prods'} and $in{'status'} eq 'New'){
		my ($err);
		foreach $key (keys %in){
			if ($key =~ /prods_qty_(\d+)/){
				if ($in{$key}>0){

					my ($sth) = &Do_SQL("SELECT * FROM sl_debitmemos_products WHERE ID_debitmemos_products='$1'");
					$rec = $sth->fetchrow_hashref;

					if ($rec->{'ID_products'} >= 400000000 and $rec->{'ID_products'} < 500000000){
						$taxxxx = &load_name('sl_parts','ID_parts',($rec->{'ID_products'} - 400000000),'Sale_Tax');
					}
					if ($rec->{'ID_products'} >= 600000000){

					}

					my $tax_percent = ($rec->{'Tax_percent'})? ($rec->{'Tax_percent'}/100):0;
					my $tax = ((($in{'prods_saleprice_'.$1}*$in{'prods_qty_'.$1})-$in{'prods_discount_'.$1}) * $tax_percent);
					
					my ($sth) = &Do_SQL("UPDATE sl_debitmemos_products SET Quantity='$in{'prods_qty_'.$1}',
						Saleprice='$in{'prods_saleprice_'.$1}',
						Shipping='$in{'prods_shipping_'.$1}', 
						Tax='$tax',
						Cost='$in{'prods_cost_'.$1}',
						Discount='$in{'prods_discount_'.$1}'
						WHERE ID_debitmemos_products=$1");
				}else{
					my ($sth) = &Do_SQL("DELETE FROM sl_debitmemos_products WHERE ID_debitmemos_products=$1");
				}
			}
		}
		if (!$err){
			$va{'message'} = &trans_txt('opr_debitmemos_amnts');
		}else{
			$va{'message'} = &trans_txt('reqfields');
		}
	
	}elsif($in{'update_amounts'} and $in{'status'} eq 'New'){
		my ($err);
		my ($orderamounttotal)=0;
		foreach $key (keys %in){
			if ($key =~ /orderamount_(\d+)/){
				$in{$key} =~ s/\$|\,//;
				$orderamounttotal += $in{$key};
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$1'
				AND ( sl_orders_payments.Captured != 'Yes' OR sl_orders_payments.Captured is null ) 
				AND ( sl_orders_payments.CapDate is null OR sl_orders_payments.CapDate ='0000-00-00')
				GROUP BY ID_orders
				HAVING  SUM(ROUND(Amount,2)) >= '".&filter_values($in{$key})."';");
				if ($sth2->fetchrow>0){
					my ($sth) = &Do_SQL("REPLACE INTO sl_debitmemos_payments SET ID_orders='$1', Amount=ROUND($in{$key},2), ID_debitmemos='$in{'id_debitmemos'}', Date=CURDATE(), Time=CURTIME(), ID_admin_users='$usr{'id_admin_users'}'");
				}else{
					++$err;
					$error{'order'.$1} = &trans_txt('invalid');
				}
			}
		}

		if (!$err){
			if ($orderamounttotal > $in{'amount'}){
				$va{'message'} = &trans_txt('opr_debitmemos_amnts_exceeds').": ".&format_price($orderamounttotal)." > ".&format_price($in{'amount'});
			}else{
				$va{'message'} = &trans_txt('opr_debitmemos_amnts');
			}
		}else{
			$va{'message'} = &trans_txt('reqfields');
			&cgierr($in{'update_amounts'} .'----'. $in{'status'});
		}
	}

	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_debitmemos_payments WHERE ID_debitmemos=$in{'id_debitmemos'}");
	my ($total_amnt) = $sth->fetchrow();
    $in{'amount'} = &round($in{'amount'}, $sys{'fmt_curr_decimal_digits'});
    $total_amnt = &round($total_amnt, $sys{'fmt_curr_decimal_digits'});
    if ($total_amnt - $in{'amount'} == 0 and $in{'amount'} > 0){
	
		if  ($in{'chhto_new'} and $in{'status'} eq 'Approved'){
			my ($sth) = &Do_SQL("UPDATE sl_debitmemos SET Status='New' WHERE ID_debitmemos=$in{'id_debitmemos'}");
			$in{'status'} = 'New';
			&auth_logging('opr_debitmemos_new',"$in{'id_debitmemos'}");
			$va{'message'} = &trans_txt('opr_debitmemos_new');
			
		}elsif($in{'chhto_approved'} and $in{'status'} eq 'New' and &check_permissions('opr_debitmemos_approved','','')){

			my ($sth) = &Do_SQL("UPDATE sl_debitmemos SET Status='Approved' WHERE ID_debitmemos=$in{'id_debitmemos'}");
			&auth_logging('opr_debitmemos_approved',"$in{'id_debitmemos'}");
			$va{'message'} = &trans_txt('opr_debitmemos_approved');
			$in{'status'} = 'Approved';			
			
		}elsif ($in{'chhto_applied'} and $in{'status'} eq 'Approved' and &check_permissions('opr_debitmemos_applied','','')){

			
			#####################################
			#####################################
			#####
			##### Aplicacion Debit Memo
			#####
			#####################################
			#####################################

			my ($err,$rec);

			############
			############ 1) Validacion Monto Pendiente en Orden
			############
			my ($sth) = &Do_SQL("SELECT * FROM sl_debitmemos_payments WHERE ID_debitmemos = '$in{'id_debitmemos'}';");
			while ($rec = $sth->fetchrow_hashref){
				my ($sth2) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_payments WHERE ID_orders='$rec->{'ID_orders'}'
										AND Reason!='Refund'
										/*AND ( sl_orders_payments.Captured != 'Yes' OR sl_orders_payments.Captured is null ) AND ( sl_orders_payments.CapDate is null OR sl_orders_payments.CapDate ='0000-00-00')*/
										GROUP BY ID_orders
										HAVING  SUM(ROUND(Amount,2)) >= '$rec->{'Amount'}';");
				my ($tot_paym) = $sth2->fetchrow();

				++$err if (!$tot_paym);
			}
			############
			############ 2) Aplicacion
			############
			if (!$err){
				my ($sth) = &Do_SQL("SELECT * FROM sl_debitmemos_payments WHERE ID_debitmemos = '$in{'id_debitmemos'}';");
				while ($rec = $sth->fetchrow_hashref){
					my ($idp_new);

					
					############
					############ 2.1) Products
					############
					my ($cm_saleprice, $cm_discount, $cm_tax);
					my ($sth9) = &Do_SQL("SELECT 
										SUM(sl_debitmemos_products.SalePrice*sl_debitmemos_products.Quantity )
										,SUM(sl_debitmemos_products.Discount)
										,SUM(sl_debitmemos_products.Tax) 
										FROM sl_debitmemos_products WHERE ID_debitmemos = '$in{'id_debitmemos'}';");
					
					my ($cm_saleprice, $cm_discount, $cm_tax) = $sth9->fetchrow_array();
					my $saleprice = $cm_saleprice;
					my $tax = $cm_tax;

					my ($sth4) = &Do_SQL("SELECT * FROM sl_debitmemos_products WHERE ID_debitmemos = '$in{'id_debitmemos'}' LIMIT 1;");

					$rec4 = $sth4->fetchrow_hashref;
					my $tax_percent = ($rec4->{'Tax_percent'})?$rec4->{'Tax_percent'}/100:0;	
					my $quantity = 1;

					my ($sth2) = &Do_SQL("INSERT INTO sl_orders_products SET 
										ID_products=800000002, 
										ID_orders='$rec->{'ID_orders'}', 
										Quantity='$quantity', 
										SalePrice='$saleprice', 
										Shipping='0', 
										Cost='0', 
										Tax='$tax', 
										Tax_percent='$tax_percent', 
										Status='Active', 
										Date=CURDATE(), 
										Time=CURTIME(), 
										PostedDate = CURDATE(), 
										ID_admin_users=$usr{'id_admin_users'};");
					

					my ($idprod) = $sth2->{'mysql_insertid'};
					
					&recalc_totals($rec->{'ID_orders'});
					

					############
					############ 2.2) Payments
					############ 

					#my ($sth2) = &Do_SQL("SELECT ID_orders_payments,Captured, Amount FROM sl_orders_payments WHERE ID_orders = '$rec->{'ID_orders'}'  AND Status!='Cancelled' 
					#					AND Reason!='Refund'
					#					/*AND ( sl_orders_payments.Captured != 'Yes' OR sl_orders_payments.Captured is null ) AND ( sl_orders_payments.CapDate is null OR sl_orders_payments.CapDate ='0000-00-00')*/
					#					ORDER BY Captured ASC, Date DESC, Amount ASC");
					#my ($cm_amount) =$rec->{'Amount'};
					#while (my ($idp_orig, $status, $payment_amount) = $sth2->fetchrow_array()){
					#	if($cm_amount>0){						
					#		if ($status eq 'Yes'){								
					#			my ($sth2) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$rec->{'ID_orders'}',Type='Deposit',Amount = '$cm_amount', Reason='Refund',Paymentdate = CURDATE(),Captured='Yes',CapDate=CURDATE(),Status='Approved',Date=CURDATE(), Time=CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
					#			$idp_new = $sth2->{'mysql_insertid'};
					#		}else{
					#			my ($sth2) = &Do_SQL("UPDATE sl_orders_payments SET Amount = Amount+$cm_amount WHERE ID_orders_payments = '$idp_orig';");
					#			$cm_amount+=$payment_amount;
					#			$idp_new = $idp_orig;
					#		}
					#	}
					#}
					
					my ($cm_amount) =$rec->{'Amount'};
					my ($sql) = &Do_SQL("INSERT INTO sl_orders_payments SET ID_orders='$rec->{'ID_orders'}',Type='Deposit',Amount = '$cm_amount', Reason='Refund',Paymentdate = CURDATE(),AuthCode='$idprod',Captured='Yes',CapDate=CURDATE(),Status='Approved',Date=CURDATE(), Time=CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");
					
					my ($sth2) = &Do_SQL("UPDATE sl_debitmemos_payments SET ID_orders_payments = '$idp_orig', ID_orders_payments_added = '$idp_new', ID_orders_products_added = '$idprod' WHERE ID_debitmemos_applied = '$rec->{'ID_debitmemos_applied'}';");
					


					if($in{'transition'}){
						$txtTransition="\nMode: [Transition] ";
						&Do_SQL("INSERT INTO sl_debitmemos_notes SET ID_debitmemos = '$in{'id_debitmemos'}', Notes = '".$txtTransition."', Type = 'Low', Date = CURDATE(), Time = CURTIME(), ID_admin_users = '$usr{'id_admin_users'}';");

					}

					&add_order_notes_by_type( $rec->{'ID_orders'},&trans_txt('opr_debitmemos_applied')."\nDebit Memo: $in{'id_debitmemos'}\nAmount: ".&format_price($rec->{'Amount'}).$txtTransition,"Low");
					$in{'db'} = 'sl_orders';
					&auth_logging('opr_debitmemos_applied',"$rec->{'ID_orders'}");		
					$in{'db'} = 'sl_debitmemos';

					
					if(!$in{'transition'}){
					#Verifica si se marco transiciÃ³n
						############
						############ 3) Mov. Contables
						############
						#my ($sth) = &Do_SQL("SELECT Ptype, Type FROM sl_orders INNER JOIN sl_customers USING(ID_customers) WHERE ID_orders = '$rec->{'ID_orders'}';");
						#my($order_type, $ctype) = $sth->fetchrow();
						#my @params = ($rec->{'ID_orders'},$saleprice,$tax,$in{'currency_exchange'});
						#&accounting_keypoints('order_credit_memos_'. $ctype .'_'. $order_type, \@params );

						#######Order Accounting######	
						sub get_account{
							my ($tVal) = @_;	
							my ($sth) = &Do_SQL("SELECT ID_accounts FROM sl_accounts WHERE Name='$tVal' order by ID_accounting DESC;");
							return $sth->fetchrow();
						}
						sub get_currency{
							my ($tVal) = @_;		
							my ($sth) = &Do_SQL("SELECT Currency FROM sl_customers WHERE ID_customers='$tVal';");
							return $sth->fetchrow();
						}
						sub get_customer{
							my ($tVal) = @_;		
							my ($sth) = &Do_SQL("SELECT ID_customers FROM sl_debitmemos WHERE ID_debitmemos='$tVal';");
							return $sth->fetchrow();
						}						
						$id_customer=&get_customer($in{'id_debitmemos'});
						my ($Currency) = &get_currency($id_customer);
						$valueAmount = $rec->{'Amount'};	
						$idOrder_New = $rec->{'ID_orders'};								
						##Debit (Cliente)
						if($Currency eq 'MX$'){
							$idAccount_debit="CLIENTES NACIONALES";
						}else{
							$idAccount_debit="CLIENTES EXTRANJEROS";	
						}
						$id_cd_debit = &get_account($idAccount_debit);						
						$sql_accounting_debit="INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,tablerelated,ID_tablerelated,Category,Credebit,Status,Date,Time  ,ID_admin_users ) 
								VALUES ('$id_cd_debit','$valueAmount', '', CURDATE(), 'sl_orders', '$idOrder_New', 'sl_debitmemos', '$in{'id_debitmemos'}', 'Anticipo Clientes', 'Debit','Active',CURDATE(), CURTIME(), '1');";
						&Do_SQL($sql_accounting_debit);						
						##Credit (Banco)
						$idAccount_credit=$in{'banks_accounts'};	
						$id_cd_credit = &get_account($idAccount_credit);
						$sql_accounting_credit="INSERT INTO sl_movements (ID_accounts,Amount,Reference,EffDate,tableused,ID_tableused,tablerelated,ID_tablerelated,Category,Credebit,Status,Date,Time  ,ID_admin_users )
 				         		VALUES ('$id_cd_credit','$valueAmount', '', CURDATE(), 'sl_orders', '$idOrder_New', 'sl_debitmemos', '$in{'id_debitmemos'}','Anticipo Clientes', 'Credit','Active',CURDATE(), CURTIME(), '1');";						 
						&Do_SQL($sql_accounting_credit);
						#update debitmemos
						my ($sth_bank) = &Do_SQL("UPDATE sl_debitmemos SET ID_accounts = '$id_cd_credit' WHERE ID_debitmemos = '$in{'id_debitmemos'}';");
					}						

				}

				my ($sth) = &Do_SQL("UPDATE sl_debitmemos SET Status='Applied' WHERE ID_debitmemos = '$in{'id_debitmemos'}';");
				$in{'status'} = 'Applied';
				&auth_logging('opr_debitmemos_applied',"$in{'id_debitmemos'}");
				$va{'message'} = &trans_txt('opr_debitmemos_applied');						
			}else{
				$va{'message'} = &trans_txt('opr_debitmemos_applied_err');	
			}		
		}
		
		if($in{'transition'}){
			$vTransition='&transition=1'; 
			$selTransition1='selected'; 
			$selTransition2='';
		}else{
			$vTransition='';
			$selTransition1='';
			$selTransition2='selected';
		}
	
		$va{'view_transition'}=qq|<tr>
				<td width="30%">Transition :  </td>
				<td>
					<span class="field switch">
						<label class="cb-enable $selTransition1"><span onclick="ok(1)">On</span></label>
						<label class="cb-disable $selTransition2"><span onclick="ok(0)">Off</span></label>
						<input type="checkbox" id="transition" class="checkbox" name="transition" style="display:none;"/><span id="txtTransition"></span>
					</span>
				</td>
			</tr>|;
		if ($in{'status'} eq 'New'){
		
				$va{'action_status'} = qq|&nbsp;&nbsp;&nbsp;
			<span id="ok"><a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_debitmemos&view=$in{'id_debitmemos'}&tab=2&chhto_approved=1">
				<img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" title='Approve' alt='' border='0'>
			</a></span>|;
		}elsif($in{'status'} eq 'Approved'){
			$va{'bank'} = qq|<select id='banks_accounts' name='banks_accounts' onFocus='focusOn( this )' onBlur='focusOff( this )' onChange='bank(this.value)'>
				   			<option value=''>---</option>
							[fc_build_select_banks_accounts_by_name]
						</select>|;
			$va{'action_status'} = qq|&nbsp;&nbsp;&nbsp;
			<a onclick="return Confirm_to_continue()" href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_debitmemos&view=$in{'id_debitmemos'}&tab=2&chhto_new=1">
				<img src="$va{'imgurl'}/$usr{'pref_style'}/b_drop.png" title='un Aprroved' alt='' border='0'>
			</a>
			<span id="ok"><a onclick="return Confirm_to_continue()" href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_debitmemos&view=$in{'id_debitmemos'}&tab=2&chhto_applied=1$vTransition">
				<img src="$va{'imgurl'}/$usr{'pref_style'}/b_ok.png" title='Applied' alt='' border='0'>
			</a></span>|;
		}else{
			$va{'view_transition'}='';
			my ($sth) = &Do_SQL("SELECT sl_accounts.Name FROM sl_debitmemos LEFT JOIN sl_accounts ON sl_debitmemos.ID_accounts=sl_accounts.ID_accounts WHERE ID_debitmemos='$in{'id_debitmemos'}';");
			my ($rec) = $sth->fetchrow_hashref();
			$va{'bank'} = $rec->{'Name'};
		}
	}
	
	## Customer
	$va{'customer_name'} = &load_db_names('sl_customers','ID_customers',$in{'id_customers'},'[company_name]/[FirstName] [LastName1]');
	
	## Product
	if ($in{'id_products'} > 600000000){
		$va{'productname'} = &load_name('sl_services','ID_services',$in{'id_products'}-600000000,'Name');
		$va{'prodlink'}    = "/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_services&view=".($in{'id_products'}-600000000);
	}else{
		$va{'productname'} = &load_db_names('sl_parts','ID_parts',$in{'id_products'}-400000000,'[Name]/[Model]');
		$va{'prodlink'}    = "/cgi-bin/mod/$usr{'application'}/dbman?cmd=mer_parts&view=".($in{'id_products'}-400000000);
	}
	$in{'id_products'} = &format_sltvid($in{'id_products'});	
	
	$in{'amount'} = &format_price($in{'amount'});

}

sub view_opr_locations{
	
}

sub validate_opr_locations{
	my($err);

	if( $in{'status'} eq 'Inactive' ){
		$sth = &Do_SQL("SELECT SUM(Quantity) 
						FROM sl_locations 
							INNER JOIN sl_warehouses_location ON sl_locations.Code = sl_warehouses_location.Location
						WHERE sl_locations.ID_locations = ".$in{'id_locations'}." 		
							AND Quantity > 0 
						GROUP BY sl_warehouses_location.Location;");
		my $quantity = $sth->fetchrow();

		if( $quantity > 0 ){
			++$err;
			$error{'status'} = &trans_txt('opr_locations_invalid_status');			
		}
	}else{
		my $id_warehouses_cur = &load_name('sl_locations','ID_locations',$in{'id_locations'},'ID_warehouses');
		if( $id_warehouses_cur and $id_warehouses_cur != $in{'id_warehouses'} ){			
			++$err;
			$error{'id_warehouses'} = &trans_txt('opr_locations_invalid_status');
		}
	}

	return $err;
}


#############################################################################
#############################################################################
#   Function: view_opr_customers_advances
#
#       Es: Vista de Customers Advances
#       En: 
#
#
#    Created on: 
#
#    Author: HC
#
#    Modifications:
#		- 
#
#   Parameters:
#      - 
#
#  Returns:
#      - 
#
#   See Also:
#
#
sub view_opr_customers_advances {
#############################################################################
#############################################################################

	$va{'customer_name'} = &load_name('sl_customers','ID_customers',$in{'id_customers'},'company_name');

	my ($sth) = &Do_SQL("SELECT
							sl_banks_movements.ID_banks_movements 
							, sl_banks.ID_banks
							, sl_banks.Name
							, sl_banks.Currency 
						FROM 
							sl_banks_movrel INNER JOIN sl_customers_advances ON sl_customers_advances.ID_customers_advances = sl_banks_movrel.tableid AND tablename = 'customers_advances' 
							INNER JOIN sl_banks_movements ON sl_banks_movrel.ID_banks_movements = sl_banks_movements.ID_banks_movements 
							INNER JOIN sl_banks USING (ID_banks) 
						WHERE 
							ID_customers_advances = ". $in{'id_customers_advances'} .";");
	($in{'id_banks_movements'},$va{'id_bank'}, $va{'bank_name'}, $va{'bank_currency'}) = $sth->fetchrow();

	# Obtiene el monto ya aplicado del Adelanto actual
	my ($sth) = &Do_SQL("	SELECT IF( SUM(Amount) is NULL, 0, SUM(Amount))
							FROM sl_customers_advances_payments 
							WHERE ID_customers_advances = '". $in{'id_customers_advances'} ."' AND status = 'Applied';");
	my ($total_applied) = $sth->fetchrow();



	## Validation
	$in{'addorder'} = int($in{'addorder'});
	$in{'delorder'} = int($in{'delorder'});

	my ($sth) = &Do_SQL("SELECT SUM(Amount) FROM sl_customers_advances_payments WHERE ID_customers_advances=$in{'id_customers_advances'}");
	my ($total_amnt) = $sth->fetchrow();


	$in{'amount'} = &round($in{'amount'}, $sys{'fmt_curr_decimal_digits'});
	$va{'amount_to_apply'} = &round( ($in{'amount'} - $total_applied), $sys{'fmt_curr_decimal_digits'});
	$total_amnt = &round($total_amnt, $sys{'fmt_curr_decimal_digits'});

	###
	### ADD | DELETE ORDERS
	###
	if($in{'status'} ne 'Applied'){

		if ($in{'addorder'}>0){

			# Busca si el Advance que desea ser añadido tiene un registro aun no aplicado a la orden  
			my ($sth) = &Do_SQL("SELECT COUNT(ID_orders)
								FROM sl_customers_advances_payments 
								WHERE ID_orders = '". $in{'addorder'} ."' AND Status='New';");

			my ($applied) = $sth->fetchrow();

			if( !$applied ){

				my ($sth) = &Do_SQL(" INSERT INTO sl_customers_advances_payments SET 
										ID_customers_advances = '". $in{'id_customers_advances'} ."', ID_orders = '". $in{'addorder'} ."',	
										Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."';");

			}else{

				$va{'message'} = 'Already added';

			}


		}elsif( $in{'deladvances'} ){

			##
			### DELETE ORDERS
			##

			# Busca si la porción del Advance que desea ser eliminado ya tiene registro en sl_orders_payments, es decir si ya esta aplicado
			my ($sth) = &Do_SQL("	SELECT IF( (ID_orders_payments IS NULL OR ID_orders_payments = '' ), 0, 1) applied
									FROM sl_customers_advances_payments 
									WHERE ID_customers_advances_payments = '". $in{'deladvances'} ."';");

			my ($applied) = $sth->fetchrow();

			# Si no esta aplicado lo borra
			if( !$applied ){
				my ($sth) = &Do_SQL("DELETE FROM sl_customers_advances_payments WHERE ID_customers_advances_payments = '". $in{'deladvances'} ."';");
			}else{
				$va{'message_error'} = &trans_txt('opr_customers_advances_apply_no_delete');
			}

		}

	}else{
		$va{'message_error'} = &trans_txt('opr_customers_advances_not_modify');
	}	

	if($in{'update_amounts'} and $in{'status'} ne 'Applied' and $in{'tab'} eq '2' ){

		##
		### UPDATE AMOUNTS
		##
		my ($err);
		my ($orderamounttotal)=0;

		my ($sth1) = &Do_SQL("SELECT SUM(amount) FROM sl_customers_advances_payments WHERE ID_customers_advances = '". $in{'id_customers_advances'} ."' AND Status = 'Applied';");
		my ($applied_amount) = $sth1->fetchrow();	
		my $max_allowed = round($in{'amount'}-$applied_amount,2);
		
		foreach my $key (sort keys %in){

			if ($key =~ /orderamount_(\d+)/){

				$in{$key} =~ s/\$|\,//;
				my $id_customers_advances_applied = $1; 
				my $this_amount = round($in{$key} - 0,2);

				my ($sth) = &Do_SQL("SELECT ID_orders FROM sl_customers_advances_payments WHERE ID_customers_advances_payments = '". $id_customers_advances_applied ."';");
				my ($id_orders) = $sth->fetchrow();


				my ($amounts) = &get_paid_unpaid($id_orders);

				if( $this_amount <= $amounts->{'calculated_unpaid'} and ($this_amount <= $max_allowed or abs($this_amount - $max_allowed) < 0.01)){

						$orderamounttotal += $this_amount;
						my ($sth) = &Do_SQL("UPDATE sl_customers_advances_payments SET Amount = ROUND($in{$key},2), Date = CURDATE(), Time = CURTIME(), ID_admin_users = '". $usr{'id_admin_users'} ."' WHERE ID_customers_advances_payments = '". $id_customers_advances_applied ."';");
						$max_allowed -= $this_amount;

				}else{

					++$err;
					$this_error .= $this_amount . ' > ' . $max_allowed;

				}
			}
		}

		if (!$err){
			if (  $orderamounttotal > $in{'amount'} and abs($orderamounttotal - $in{'amount'}) >= 0.01 ){
				$va{'message_error'} = &trans_txt('opr_creditmemos_amnts_exceeds').": ".&format_price($orderamounttotal)." > ".&format_price($in{'amount'});
			}else{
				$va{'message_good'} = &trans_txt('opr_customers_advances_amnts');
			}
		}else{
			$va{'message_error'} = $this_error;
		}
	}


	if ( $in{'apply'} ){

		#	###
		#	### APPLY ADVANCES
		#	###
		my ($this_error, $this_str) = &apply_customers_advances($in{'id_customers_advances'}, $total_applied, $in{'apply'}, 0, $in{'amount'});

		if($this_error){

			##
			### ERROR
			##
			&Do_SQL("ROLLBACK;");
			$va{'message'} = $this_str;

		}else{

			##
			### Everything OK | Commit Transaction
			###

			# Especifica si el Advance ha sido ocupado solo parcialmente o totalmente
			$in{'status'} = ($total_applied + $amount_to_apply) eq $this_amount ? 'Applied':'Partial';
			&Do_SQL("UPDATE sl_customers_advances SET Status = '". $in{'status'} ."' WHERE ID_customers_advances = '". $in{'id_customers_advances'} ."';");

			# Mensaje Final
			$va{'message'} = $in{'status'} eq 'Partial' ? &trans_txt('opr_customers_advances_partial') : &trans_txt('opr_customers_advances_applied');
			&Do_SQL("COMMIT;");

		}

	}

}


1;