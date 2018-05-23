sub view_opr_customers{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 10 Nov 2010 17:12:55
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	##if($in{'password'}ne'')	{
	my ($custSth)	= &Do_SQL("SELECT sl_accounts.Name, sl_accounts.ID_accounts
								FROM sl_customers 
								JOIN sl_accounts ON sl_accounts.ID_accounts=sl_customers.ID_accounts_debit
								WHERE sl_customers.ID_customers=".$in{'view'});
	my ($accName,$accId)=$custSth->fetchrow();
	$va{'accountname'}=$accName;
	$va{'idaccount'}=$accId;


	$va{'pass_chg_button'}=qq|<a href="javascript:return false;" onClick="change_cust_pass();"><img src='[va_imgurl]/[ur_pref_style]/chpas.jpg' title='Change Pass' alt='Change Pass' border='0'></a><a name='change_cust_pass' id='change_cust_pass'>&nbsp;</a>|;
	##}else{
	##	$va{'pass_chg_button'}="";
	##}
	if ($in{'chgstatusto'} and &check_permissions('opr_customers_chgstatus','','')){
		my ($sth)	= &Do_SQL("UPDATE sl_customers SET Status='".&filter_values($in{'chgstatusto'})."' WHERE ID_customers='$in{'id_customers'}'");
		&auth_logging('opr_customers_chgstatus',$in{'id_customers'});
		$in{'status'} = $in{'chgstatusto'};
	}
	$in{'phone1'} = (!$cfg{'disable_format_phone_number'})? &format_phone($in{'phone1'},$in{'id_customers'}) : $in{'phone1'};
	$in{'phone2'} = (!$cfg{'disable_format_phone_number'})? &format_phone($in{'phone2'},$in{'id_customers'}) : $in{'phone2'};
	$in{'cellphone'} = (!$cfg{'disable_format_phone_number'})? &format_phone($in{'cellphone'},$in{'id_customers'}) : $in{'cellphone'};
	
	if (!&check_permissions('opr_customers_chgstatus','','')){
		$va{'chgstatus'} = qq| <span class="smallfieldterr">|.&trans_txt('unauth_action').qq|</span>|;
	}else{
		my (@ary) = &load_enum_toarray('sl_customers','Status');
		for (0..$#ary){
			if ($ary[$_] ne $in{'status'}){
				$va{'chgstatus'} .= qq| <a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_customers&view=$in{'id_customers'}&chgstatusto=$ary[$_]">$ary[$_]</a> &nbsp;&nbsp;&nbsp;|;
			}
		}
	}
}



#############################################################################
#############################################################################
#   Function: validate_opr_customers
#
#       Es: validacion extra para agregar o editar customers
#       En: 
#
#
#    Created on: 14/05/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
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
sub validate_opr_customers{
#############################################################################
#############################################################################
	my $err;
	$in{'status'} = 'Active' if(!$in{'status'});
	if ($in{'edit'}){
		# Revisar si tiene Ordenes no podra  editar el Currency
		# Check if you could not edit the Currency
		my ($sth)	= &Do_SQL("SELECT count(*) FROM sl_orders WHERE ID_customers='$in{'id_customers'}';");
		my $orders = $sth->fetchrow_array;
		if ($orders > 0){
			$currency = &load_name('sl_customers','ID_customers',$in{'id_customers'},'Currency');
			if ($in{'currency'} ne $currency){
				$error{'currency'} = &trans_txt('currency_no_editable');
				++$err;
			}
		}

	}
	if ( ! $in{'type'} or $in{'type'} eq '') {
		$error{'type'} = &trans_txt('required');
		++$err;
	}

	return $err;
}

#############################################################################
#############################################################################
#   Function: loaddefault_opr_customers
#
#       Es: validacion extra para agregar o editar customers
#       En: 
#
#
#    Created on: 14/05/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - Modified on 
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
sub loaddefault_opr_customers{
#############################################################################
#############################################################################
	$in{'status'} = 'Active';
}

1;