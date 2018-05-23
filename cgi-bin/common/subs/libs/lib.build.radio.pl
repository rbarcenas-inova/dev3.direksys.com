##### Func Revisadas
#################################
sub build_radio_mapps {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($output,$checked);
	@fields = split(/\|/, $usr{'multiapp'});
	if ($#fields == -1) {
		return $output;
	}

	for (0..$#fields){
		($usr{'application'} eq $fields[$_])?
			($checked = 'checked'):($checked = '');
		$output .= qq|
		<span style='white-space:nowrap'>
			<input id="multiapp$fields[$_]" type="radio" name="multiapp" value="$fields[$_]" class="checkbox" $checked> 
			<label for="multiapp$fields[$_]">$fields[$_]</label></span>\n|;
	}
	return $output;

}

##### Func Revisadas
#################################

sub build_radio_saleorigins {
# --------------------------------------------------------
# Created by: Pablo H. Hdez.
# Created on: 09/05/2012 
# Description : Builds radio the origins of sale
# Notes : (Modified on : Modified by :)
    my ($strin,$st);
    $st = 'readonly' if $in{'view'};
    my ($sth) = &Do_SQL("SELECT ID_salesorigins,Channel FROM sl_salesorigins WHERE Status='Active' ORDER BY Channel");
    while(my($value,$name) = $sth->fetchrow()){
        $strin .= qq|<span style='white-space:nowrap'><input type="radio" name="id_salesorigins" value="$value" class="radio" $st> $name </span>\n|;
    }
    return $strin;  
}

sub build_radio_order_status {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('status','sl_orders');	
}

sub build_radio_ptype{
# --------------------------------------------------------
# Created on: 2/9/10 12:04 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds checkboxes based on sl_orders.ptype row values
# Parameters :
# Forms Involved: All Order Reports

	return build_radio_from_enum('ptype','sl_orders');

}

sub build_radio_firstcall{
# --------------------------------------------------------
# Created on: 09/09/2010 13:40 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds radio buttons for sl_orders.first_call
# Parameters :
# Forms Involved: All Order Reports

	return build_radio_from_enum('first_call','sl_orders');

}

sub build_radio_eco_dbcampaign{
# --------------------------------------------------------
# Created on: 09/23/2010 18:40 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds radio buttons for nsc_campaigns.database_campaign
# Parameters :
# Forms Involved: All Order Reports

	return build_radio_from_enum('database_campaign','nsc_campaigns');

}


sub build_radio_eco_campaignuser{
# --------------------------------------------------------
# Created on: 09/28/2010 13:40 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds radio buttons for nsc_campaigns.campaign_user
# Parameters :
# Forms Involved: All Order Reports

	return build_radio_from_enum('campaign_user','nsc_campaigns');

}

sub build_radio_prd_shptable{
# --------------------------------------------------------
# Created on: 11/15/2010 16:40 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds radio buttons for sl_products.shipping_table
# Parameters :
# Forms Involved: products_form

	return build_radio_from_enum('shipping_table','sl_products');

}



sub build_radio_return_type {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on :jun/16/08 Modified by :Roberto Barcenas)

	return build_radio_from_enum('Type','sl_returns');	
}




sub build_radio_return_meraction {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('merAction','sl_returns');	
}

sub build_radio_return_generalpckgcondition {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('generalpckgcondition','sl_returns');	
}

sub build_radio_return_returnfees {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('ReturnFees','sl_returns');	
}

sub build_radio_return_restockfees {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('RestockFees','sl_returns');	
}

sub build_radio_return_processed {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('Processed','sl_returns');	
}


sub build_select_return_notes_type {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_select_from_enum('Type','sl_returns_notes');	
}


sub build_radio_order_paystatus {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('statuspay','sl_orders');	
}

sub build_radio_order_prdstatus {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('statusprd','sl_orders');	
}


sub build_radio_famprod{
#-----------------------------------------
	my (@files,$file,$output,$fname,$n);
	%error = %cfg;
	opendir (IMGDIR, "$cfg{'path_imgman'}prodfam") || &cgierr("Unable to open directory $cfg{'path_imgman'}prodfam",704,$!);
		@files = readdir(IMGDIR);		# Read in list of files in directory..
	closedir (IMGDIR);
	@files = sort @files;
	FILE: foreach my $file (@files) {
		next if ($file =~ /^\./);		# Skip "." and ".." entries..
		next if ($file =~ /^index/);		# Skip index.htm type files..
		$file =~ /(\w+)\./;
		my $pvalue = $1;
		my $pname = $1;
		$pname =~ s/_/ /g;
		$output .= qq|<input name="products" value="$pvalue" type="radio" class="radio">|.ucfirst($pname).qq|&nbsp;&nbsp;&nbsp;|;
		++$n;
		if ($n>4){
			$n=0;
			$output .= "<br>";
		}
	}

	return $output;
}

#GV Inicia 28abr2008
sub build_radio_return_genpckgcond{
# --------------------------------------------------------
# Created by: MCC C Gabriel Varela S
# Created on: 28abr2008
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('generalpckgcondition','sl_returns');	
}
#GV Termina 28abr2008

#############################################################################
#############################################################################
#   Function: build_radio_sales_terms
#
#       Es: Genera radio buttons con terminos de pago para Ventas
#       En: Build radio buttons with payment terms for Sales
#
#
#    Created on: 03/05/2013  13:20:10
#
#    Author: RB
#    Modifications:
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
sub build_radio_sales_terms {
#############################################################################
#############################################################################

    my ($strin,$st);
    $st = 'readonly' if $in{'view'};
    my ($sth) = &Do_SQL("SELECT ID_terms,Name FROM sl_terms WHERE Type='Sales' AND Status='Active' ORDER BY Name");
   	my $i=0; 
    while(my($id,$name) = $sth->fetchrow()){
    	 my $sel = $i==0 ? 'checked = "checked"' : '';
        $strin .= qq|<span style='white-space:nowrap'><input type="radio" id="pterms_$id" name="pterms" value="$name" class="radio" $st $sel> $name </span>\n|;
        $i++;
    }
    return $strin;  
}

sub build_radio_locations_status {
# --------------------------------------------------------
# Created by: Oscar Maldonado
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('Status','sl_locations');	
}

sub build_radio_packing_type {
# --------------------------------------------------------
# Created by: Oscar Maldonado
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_radio_from_enum('packing_type','cu_invoices_lines');	
}
1;