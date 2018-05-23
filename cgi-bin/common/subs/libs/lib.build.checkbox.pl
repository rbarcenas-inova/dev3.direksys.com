##### Func Revisadas
#################################
sub build_checkbox_mapps {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($output);
	@fields = &load_enum_toarray('admin_users','application');
	if ($#fields == -1) {
		return $output;
	}

	for (0..$#fields){
		$output .= qq|
		<span style='white-space:nowrap'>
			<input type="checkbox" name="multiapp" value="$fields[$_]" class="checkbox"> 
		$fields[$_] </span>\n|;
	}
	return $output;
}

sub build_checkbox_kitproducts {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($output);

	my ($sth) = &Do_SQL("SELECT * FROM sl_skus WHERE ID_products='$in{'id_products'}'"); 
	while ($rec = $sth->fetchrow_hashref){
		$output .= qq|<span class='checa'><input type="checkbox" name="validkits" value="$rec->{'ID_sku_products'}" class="checkbox" checked>$rec->{'choice1'} $rec->{'choice2'} $rec->{'choice3'} $rec->{'choice4'}</span>&nbsp;&nbsp;&nbsp;\n| if ($rec->{'choice1'} or $rec->{'choice2'} or $rec->{'choice3'} or $rec->{'choice4'});
	}
	$output = "---" if (!$output);
#	if ($#fields == -1) {
#		return $output;
#	}

	return $output;
}


##### Func Revisadas
#################################

sub build_checkbox_order_status {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('status','sl_orders');	
}

sub build_checkbox_cdr_status{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/29/09 15:41:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	return build_checkbox_from_enum('status','cdr');	
}

sub build_checkbox_cdr_statusf{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 09/29/09 15:41:32
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	return build_checkbox_from_enum('statusf','cdr');	
}

sub build_checkbox_order_paystatus {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('statuspay','sl_orders');	
}

sub build_checkbox_order_prdstatus {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('statusprd','sl_orders');	
}

sub build_checkbox_ptype{
# --------------------------------------------------------
# Created on: 2/9/10 12:04 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds checkboxes based on sl_orders.ptype row values
# Parameters :
# Forms Involved: All Order Reports

	return build_checkbox_from_enum('ptype','sl_orders');

}

sub build_checkbox_cust_type{
# --------------------------------------------------------
# Created on: 2/9/10 12:04 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds checkboxes based on sl_orders.ptype row values
# Parameters :
# Forms Involved: All Order Reports

	return build_checkbox_from_enum('type','sl_customers');

}


sub build_checkbox_usertype {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
# Last Time Modified by RB on 02/06/2012: Se cambia temporalmente debido a que se deben excluir algunos tipos

	#my $column='user_type';
	#my @fields = &load_enum_toarray('admin_users','user_type');
	#foreach $field (sort @fields) {
	#	$output .= qq|<span style='white-space:nowrap'><input type="checkbox" name="$column" value="$fields[$_]" class="checkbox"> $fields[$_] </span>\n| if $field !~ /IN|Mexico|Hermosillo|Puerto|Distribuidor|cc/;
	#}
	return build_checkbox_from_enum('user_type','admin_users');
}

sub build_checkbox_dids {
# --------------------------------------------------------
# Created by: RB
# Created on: 
# Description : 

	my ($strin,$st);
	$st = 'readonly' if $in{'view'};
	my ($sth) = &Do_SQL("SELECT didmx,product FROM sl_mediadids WHERE Status='Active' AND didmx>0 ORDER BY didmx"); #DNIS-NUMBER
	while(my($number,$name) = $sth->fetchrow()){
		$strin .= qq|<span style='white-space:nowrap'><input type="checkbox" name="dids" value="$number" class="checkbox" $st>($number) $name </span>&nbsp;&nbsp;&nbsp;\n|;
	}
	
	if($in{'id_products'}){
			my ($sth) = &Do_SQL("SELECT GROUP_CONCAT(ID_dids SEPARATOR '|') FROM sl_products_dids WHERE ID_products = '$in{'id_products'}'");
			$in{'dids'} = $sth->fetchrow;	
	}
	
	return $strin;	
}

sub build_checkbox_famprod {
# --------------------------------------------------------
# Created by: Product Family
# Created on: 
# Description : 

	my ($strin,$st);
	my ($sth) = &Do_SQL("SELECT FamProd FROM sl_mediacontracts_stats WHERE 1 GROUP BY FamProd"); #DNIS-NUMBER
	while(my($name) = $sth->fetchrow()){
		$strin .= qq|<span class='checa'><input type="checkbox" name="famprod" value="$name" class="checkbox">$name</span>&nbsp;&nbsp;&nbsp;\n|;
	}
	return $strin;	
}

sub build_checkbox_pricelevels {
# --------------------------------------------------------
# Created by: RB
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($strin,$st);
	$st = 'readonly' if $in{'view'};
	my ($sth) = &Do_SQL("SELECT ID_pricelevels,Name FROM sl_pricelevels WHERE Status='Active' ORDER BY Name");
	while(my($value,$name) = $sth->fetchrow()){
		$strin .= qq|<span class='checa'><input type="checkbox" name="id_pricelevels" value="$value" class="checkbox" $st> $name </span>\n|;
	}
	return $strin;	
}

sub build_checkbox_saleoriginsall {
# --------------------------------------------------------
# Created by: RB
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($strin,$st);
	$st = 'readonly' if $in{'view'};
	my ($sth) = &Do_SQL("SELECT ID_salesorigins,Channel FROM sl_salesorigins ORDER BY Channel");
	my $i=0;
	while(my($value,$name) = $sth->fetchrow()){
		$i++;
		$strin .= qq|<span class="checa"><input type="checkbox" id="salesorigins_$i" name="id_salesorigins" value="$value" class="checkbox" $st> <label for="salesorigins_$i">$name</label> </span>\n|;
	}
	return $strin;	
}

sub build_checkbox_saleorigins {
# --------------------------------------------------------
# Created by: RB
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($strin,$st);
	$st = 'readonly' if $in{'view'};
	my ($sth) = &Do_SQL("SELECT ID_salesorigins,Channel FROM sl_salesorigins WHERE Status='Active' ORDER BY Channel");
	my $i=0;
	while(my($value,$name) = $sth->fetchrow()){
		$i++;
		$strin .= qq|<span class="checa"><input type="checkbox" id="salesorigins_$i" name="id_salesorigins" value="$value" class="checkbox" $st> <label for="salesorigins_$i">$name</label> </span>\n|;
	}
	return $strin;	
}

sub build_checkbox_saleorigins_view {
# --------------------------------------------------------
# Created by: Fabian Cañaveral
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($strin,$st);
	$st = 'readonly' if $in{'view'};
	my ($sth) = &Do_SQL("SELECT ID_salesorigins,Channel FROM sl_salesorigins WHERE Status='Active' ORDER BY Channel");
	my $i=0;
	while(my($value,$name) = $sth->fetchrow()){
		$i++;
		$strin .= qq|<span class="checa"><input type="checkbox" id="salesorigins_view_$i" name="id_salesorigins_view" value="$value" class="checkbox" $st> <label for="salesorigins_view_$i">$name</label> </span>\n|;
	}
	return $strin;	
}



sub build_checkbox_firstcall{
# --------------------------------------------------------
# Created on: 09/09/2010 13:40 PM
# Author: L.I. Roberto Barcenas.
# Description :  Builds radio buttons for sl_orders.first_call
# Parameters :
# Forms Involved: All Order Reports

	return build_checkbox_from_enum('first_call','sl_orders');

}


sub build_checkbox_return_type{
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('type','sl_returns');	
}

sub build_checkbox_return_status{
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('status','sl_returns');	
}

sub build_checkbox_return_meraction{
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('meraction','sl_returns');	
}

sub build_checkbox_dids7_type {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	$in{'second_conn'}=1;
	&connect_db_w($cfg{'dbi_db_pbx'},$cfg{'dbi_host_pbx'},$cfg{'dbi_user_pbx'},$cfg{'dbi_pw_pbx'});
	return build_checkbox_from_enum('type','cdr_s7_notes');	
}

sub build_checkbox_avs_response{
# --------------------------------------------------------
# Created by: Roberto Barcenas
# Created on:
# Description : Busca las ordenes basandose en el Response de AVS
# Notes : (Modified on : Modified by :)

    my @avs_res = ("A","B","C","D","E","F","G","H","I","J","K","L",
                   "N","P","R","S","U","W","X","Y","Z");
             
    my $strout = "";
   
    if($in{'e'} !~ /0|1|3/){
        @avs_res = ("A","B","E","G","N","O","P","R","S","T","U","V","W","X","Y","Z");
    }
   
    for my $i(0..$#avs_res){   
        $strout .= qq|<span class='checa'><input name="avs_response" value="$avs_res[$i]" class="checkbox" type="checkbox">$avs_res[$i]</span>&nbsp;&nbsp;&nbsp;|;
        $strout .= "<br>"    if ($i > 0 and $i%8==0);
    }
    return $strout;   
}

sub build_checkbox_cdr_calification {
# --------------------------------------------------------
# Created by: Carlos Haas
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)

	return build_checkbox_from_enum('Calif','sl_leads_calls');	
}

sub build_checkbox_contracts_status {
# --------------------------------------------------------
# Created by: Pablo Hdez. H.
# Created on: 03/29/2012 10:30:28 AM
# Description : 
# Notes : (Modified on : Modified by :)

    return build_checkbox_from_enum('status','sl_mediacontracts');  
}


sub build_checkbox_famprod{
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
		$output .= qq|<input name="products" value="$pvalue" type="checkbox" class="radio">|.ucfirst($pname).qq|&nbsp;&nbsp;&nbsp;|;
		++$n;
		if ($n>4){
			$n=0;
			$output .= "<br>";
		}
	}

	return $output;
}


sub build_checkbox_shippingoptions {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#


	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_shpopt'});
	
	for (0..$#ary){
		#$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		$output .= "<input type='checkbox' name='shippingoptions' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_checkbox_returnpolicy {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_rpolicy'});
	
	for (0..$#ary){
		#$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		$output .= "<input type='checkbox' name='returnpolicy' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_checkbox_discounts {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_disc'});
	
	for (0..$#ary){
		#$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		$output .= "<input type='checkbox' name='discounts' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_checkbox_merchandiseformat {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_mformat'});
	
	for (0..$#ary){
		#$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		$output .= "<input type='checkbox' name='merchandiseformat' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_checkbox_paymentterms {
# --------------------------------------------------------
# Created :  Carlos Haas 01/01/2007 6:47:28 PM
# Last Update : 
# Locked by : 
# Description :
#
#

	my ($output);
	my (@ary) = split(/,/,$cfg{'vendor_popt'});
	
	for (0..$#ary){
		#$output .= "<option value='$ary[$_]'>$ary[$_]</option>\n";
		$output .= "<input type='checkbox' name='paymentterms' value='$ary[$_]' class='checkbox'>$ary[$_]\n";
	}
	#(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub build_checkbox_zones {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT ID_zones,Name FROM sl_zones WHERE Status='Active' ORDER BY Name;");
	while(my($value,$name) = $sth->fetchrow()){
		#$output .= qq|<span style='white-space:nowrap'><input type="radio" name="id_zones" value="$value" class="radio" $st> $name </span>\n|;
		$output .= qq|<span class='checa'><input type="checkbox" name="id_zones" value="$value" class="checkbox" $st> $name </span>\n|;
	}
	return $output;
}

sub build_checkbox_warehouses {
# --------------------------------------------------------
# Created by: Pablo H. Hdez.
# Created on: 09/05/2012 
# Description : Builds radio the origins of sale
# Notes : (Modified on : Modified by :)
    my ($strin,$st);
    $st = 'readonly' if $in{'view'};
    my ($sth) = &Do_SQL("SELECT ID_warehouses, Name FROM sl_warehouses WHERE Status='Active' ORDER BY Name;");
    while(my($value,$name) = $sth->fetchrow()){
        $strin .= qq|<span class='checa'><input type="checkbox" name="id_warehouses" value="$value" class="radio" $st> $name </span>\n|;
    }
    return $strin;  
}

sub build_checkbox_accounts_segments {
# --------------------------------------------------------
# Created by: GQ
# Created on: 
# Description : 
# Notes : (Modified on : Modified by :)
	my ($strin,$st);
	$st = 'readonly' if $in{'view'};
	my ($sth) = &Do_SQL("SELECT ID_accounts_segments, Name FROM sl_accounts_segments WHERE Status='Active' ORDER BY Name");
	my $i=0;
	while(my($value,$name) = $sth->fetchrow()){
		$i++;
		$strin .= qq|<span class="checa"><input type="checkbox" id="id_accounts_segments_$i" name="id_accounts_segments" value="$value" class="checkbox" $st> <label for="id_accounts_segments_$i">$name</label> </span>\n|;
	}
	return $strin;	
}

1;