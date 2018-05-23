#!/usr/bin/perl

####################################################################
########              Home Page                     ########
####################################################################
sub load_loginpage {
# --------------------------------------------------------
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_operpages WHERE Type='ccinbound-Login Page' AND Status='Active'");
	if ($sth->fetchrow()>0){
		my ($sth) = &Do_SQL("SELECT Speech FROM sl_operpages WHERE Type='ccinbound-Login Page' AND Status='Active' ORDER BY ID_operpages DESC");
		return $sth->fetchrow() . "<p align='right' class='smalltxt'>ccinbound-Login Page</p>";
	}else{
		return "<p align='right' class='smalltxt'>ccinbound-Login Page</p>";
	}
}


sub build_select_brands {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM sl_brands WHERE Status='Active' ORDER BY Name;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_brands'}'>$rec->{'Name'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}


sub build_cc_users {
# --------------------------------------------------------
	my ($output);
	my ($sth) = &Do_SQL("SELECT * FROM admin_users WHERE Status='Active' AND application like 'cc-%' AND ID_admin_users<>'$usr{'id_admin_users'}'ORDER BY LastName;");
	while ($rec = $sth->fetchrow_hashref){
		$output .= "<option value='$rec->{'ID_admin_users'}'>($rec->{'ID_admin_users'}) $rec->{'FirstName'} $rec->{'LastName'}</option>\n";
	}
	(!$output) and ($output .= "<option value='---'>".&trans_txt('none')."</option>\n");
	return $output;
}

sub customer_header {
# --------------------------------------------------------
# Last Modified on: 11/06/08 14:06:29
# Last Modified by: MCC C. Gabriel Varela S: Se muestra con una estrella cuando el cliente tiene membresía
# Last Modified on: 08/27/09 13:20:40
# Last Modified by: MCC C. Gabriel Varela S: Se cambia Number por DNIS en sl_mediadids
# Last Modified by RB on 2011/01/10: Se agrega el zipcode a la sesion
#Last modified on 7 Jun 2011 12:48:34
#Last modified by: MCC C. Gabriel Varela S. :the in address_chosen is considered

	if ($in{'did'}){
		$in{'didname'} = &load_name('sl_mediadids','didmx',$in{'did'},'num800')
	}
	

#	&load_callsession();
	#GV Inicia modificación 11jun2008: Asigna a $in{'id_customers'} el valor de $cses{"id_customers"} siempre que exista
	$in{'id_customers'} = $cses{"id_customers"} if ($cses{"id_customers"});
	#GV Termina modificación 11jun2008

	if($cses{'zip'}) {

		#### Customer Info
		$in{'customers.id_customers'} = ($cses{'id_customers'})? $cses{'id_customers'}:$cses{'customers.id_customers'};
		$in{'customers.firstname'} = ($cses{'firstname'})? $cses{'firstname'}:$cses{'customers.firstname'};
		$in{'customers.lastname1'} = ($cses{'lastname1'})? $cses{'lastname1'}:$cses{'customers.lastname1'};
		$in{'customers.lastname2'} = ($cses{'lastname2'})? $cses{'lastname2'}:$cses{'customers.lastname2'};

		$in{'customers.phone1'} = ($cses{'phone1'})? $cses{'phone1'}:$cses{'customers.phone1'};
		$in{'customers.phone2'} = ($cses{'phone2'})? $cses{'phone2'}:$cses{'customers.phone2'};
		$in{'customers.cellphone'} = ($cses{'cellphone'})? $cses{'cellphone'}:$cses{'customers.cellphone'};


		#### Address
		$in{'customers.address1'} = ($cses{'address1'})? $cses{'address1'}:$cses{'customers.address1'};
		$in{'customers.address2'} = ($cses{'address2'})? $cses{'address2'}:$cses{'customers.address2'};
		$in{'customers.address3'} = ($cses{'address3'})? $cses{'address3'}:$cses{'customers.address3'};
		$in{'customers.urbanization'} = ($cses{'urbanization'})? $cses{'urbanization'}:$cses{'customers.urbanization'};
		$in{'customers.city'} = ($cses{'city'})? $cses{'city'}:$cses{'customers.city'};
		$in{'customers.state'} = ($cses{'state'})? $cses{'state'}:$cses{'customers.state'};
		$in{'customers.zip'} = ($cses{'zip'})? $cses{'zip'}:$cses{'customers.zip'};


		$cses{'zipcode'} = $in{'customers.zip'};
		return &build_page("customer_header.html");

	}elsif ($in{'id_customers'} ){

		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
		if ($sth->fetchrow() >0){
			my ($sth) = &Do_SQL("SELECT * FROM sl_customers WHERE id_customers='$in{'id_customers'}'");
			my ($tmp) = $sth->fetchrow_hashref();
			foreach my $key (keys %{$tmp}){
# 				if!($in{"customers.".lc($key)}=~/address/ and $in{'address_chosen'}==1 and $in{"customers.".lc($key)}=~/city/ and $in{"customers.".lc($key)}=~/state/ and $in{"customers.".lc($key)}=~/zip/)
				if(!($in{'address_chosen'}==1 and ($key=~/address/gi or $key=~/zip/gi or $key=~/city/gi or $key=~/state/gi)))
				{
					$in{"customers.".lc($key)} = $tmp->{$key};
				}	
			} 		
			if($in{"customers.type"}eq"Membership" or $cses{'type'}eq"Membership")
			{
				$va{'membership'}="<img src='$va{'imgurl'}/app_bar/small_bookmarks.gif' title='Membership' alt='Member' border='0'>";
			}
			$cses{'zipcode'} = $in{'customers.zip'};
			return &build_page("customer_header.html");
		}

	}else{
	    delete($cses{'zipcode'}) if $cses{'zipcode'};
		return &build_page("customer_header_n.html");
	}
}

sub build_origins_list{
#-----------------------------------------
# Created on: 07/06/09  17:26:07 By  Roberto Barcenas
# Forms Involved: 
# Description : Crea los links para iniciar consola de acuerdo a los canales de venta creados
# Parameters : 	
	
	my ($strout);
	
	my ($sth) = &Do_SQL("SELECT ID_salesorigins,Channel FROM sl_salesorigins WHERE Status='Active' ORDER BY ID_salesorigins;");
	while(my ($id_origins,$channel) = $sth->fetchrow()){

			$strout .=qq|<a href="/cgi-bin/mod/pos/admin?cmd=console&origin=$id_origins"	class=acormenu><li> &nbsp; $channel</a>|;
	}
	return $strout;
}

sub build_menu_transfer{
#-----------------------------------------
# Created on: 20/10/14  17:26:07 By  Arturo Hernandez
# Forms Involved: 
# Description : Crea el Link de Warehouse
# Parameters : 	
	
	#my $data = &loadDataPos;
	#&cgierr($data);
	
	my ($id_warehouses) = $data{'warehouse'};
	
	$strout .=qq|&nbsp;&nbsp;&nbsp;<a href="/cgi-bin/mod/pos/dbman?cmd=opr_manifests&search=advSearch&action=1&id_warehouses=1082&ST=and&so=asc" class=acormenu>Transferencias</a><br>\n|;
	return $strout;
}



#########################################################################################
#########################################################################################
#   Function: load_areacodes
#
#       Es: Función que extrae los codigos de area del setup para ser usados para validacion de numeros de telefono.
#
#       En: Function that extracts the setup area codes to be used for validation of phone numbers.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the area codes
#
#   See Also:
#
#      ---
#
sub load_areacodes {
	my($areacodes) = $cfg{'areacodes'};
	$areacodes =~ s/\|/\'\,\'/g;

	if(substr($areacodes, 1) != "'") {
	
		$areacodes = "'" . $areacodes;
	
	}
	if(substr($areacodes, -1) != "'") {
	
		$areacodes = $areacodes . "'";
	
	}
	
	return $areacodes;
}

#########################################################################################
#########################################################################################
#   Function: tel_lenght
#
#       Es: Función que extrae la longitud valida para un numero de telefono del setup para ser usados para validacion de numeros de telefono.
#
#       En: Function that extracts the length valid for a phone number of the setup to be used for validation of phone numbers.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the lenght set for phone numbers or default 10
#
#   See Also:
#
#      ---
#
sub tel_lenght {

	if($cfg{'tel_lenght'}) {
		
		return $cfg{'tel_lenght'};

	}else {
		
		return 10;

	}

}

#########################################################################################
#########################################################################################
#   Function: tel_prefix_lenght
#
#       Es: Función que extrae la longitud valida de "lada" de un numero de telefono del setup para ser usados para validacion de numeros de telefono.
#
#       En: Function that extracts validates the length of "Lada" a phone number of the setup to be used for validation of phone numbers.
#
#
#
#   Created on: 01/11/2012
#
#   Author: Alejandro Diaz
#
#   Modifications:
#
#      - Modified on 
#
#   Parameters:
#
#   Returns:
#
#      - Returns the lenght set for prefix phone numbers or default 3
#
#   See Also:
#
#      ---
#
sub tel_prefix_lenght {

	if($cfg{'tel_prefix_lenght'}) {
		
		return $cfg{'tel_prefix_lenght'};

	}else {
		
		return 3;

	}
}


sub passdownsale{
#-----------------------------------------
# Created on: 09/08/09  13:39:29 By  Roberto Barcenas
# Forms Involved: 
# Description : Revisa si un authcode es valido para activar precios de downsale
# Parameters :
# Last Modified RB: 09/23/09  10:29:46 -- Se cambia la respuesta "Invalid" por "".
 
 	my ($authcode) = @_;
	
	my $response = -1;
	my ($sth) = &Do_SQL("SELECT IF(VValue !='',VValue,0) FROM sl_vars WHERE VName LIKE 'Downsale Price%' AND RIGHT(VValue,4)='".&filter_values($authcode)."'");
	my ($id_admin,$authorization) = split(/,/,$sth->fetchrow());
	
	if ($authorization > 0){

		$response = $id_admin;
		## Reinitialize the Value
		#$my ($sth) = &Do_SQL("UPDATE sl_vars SET VValue = '' WHERE VName LIKE 'Downsale Price%' AND RIGHT(VValue,4)='".&filter_values($authcode)."';");
	}

	return $response;

}


#############################################################################
#############################################################################
#   Function: get_shipping_data
#
#       Es: Recibe un zipcode y devuelve el shp_city y shp_state. Llamdo por step 4 y 5 de sales. Tambien genera el id_zones
#       En: 
#
#
#    Created on: 10/08/2013
#
#    Author: Roberto Barcenas
#
#    Modifications:
#
#
#   Parameters:
#
#      - $in{'shp_zip'}
#
#
#  Returns:
#
#      - 
#
#   See Also:
#
#      <accounting_keypoints>
#      <accounting_order_deposit>
#
sub get_shipping_data{
#############################################################################
#############################################################################


	if ($in{'shp_zip'} or $in{'zipcode'}){

		########
		######## Cargado de Datos de Envio
		########

		$in{'shp_zip'}  =  '00'.$in{'shp_zip'}  if  length($in{'shp_zip'}) == 3;
		$in{'shp_zip'}  =  '0'.$in{'shp_zip'}  if  length($in{'shp_zip'}) == 4;

		my ($query);
		if ($cfg{'state_exclude'}){
			$query = "AND State!='$cfg{'state_exclude'}'";
		}elsif	($cfg{'state_only'}){
			$query = "AND State='$cfg{'state_only'}'";
		}

		my ($sth) = &Do_SQL("SELECT * FROM sl_zipcodes WHERE ZipCode='$in{'shp_zip'}' /*AND PrimaryRecord='P'*/ $query group by City;");
		$in{'city_to_show'} ='';

		while($tmp = $sth->fetchrow_hashref){

			if ($tmp->{'ZipCode'}>0){

				if(uc($cfg{'country'}) !~ /MX|CO/)  {

					if(!$cses{'country_tab'} || $in{'country_tab'} eq "us" || $in{'country_tab'} eq "pr" || !$in{'country_tab'}){ #JRG if condition added

						$in{'shp_city'} = $tmp->{'City'};
						$in{'city_to_show'} .= $tmp->{'City'}.' | ';
						$in{'shp_state'} = $tmp->{'State'}."-".$tmp->{'StateFullName'};

					}
				}

			}else{
				$error{'shp_zip'} = &trans_txt('required');
				++$err;
			}
		}

		$cses{'id_zones'} = get_zone_by_zipcode($in{'zip'});
		$cses{'id_zones_express_delivery'} = &load_name('sl_zones', 'ID_zones', $cses{'id_zones'}, 'ExpressShipping');

	}

}




1;