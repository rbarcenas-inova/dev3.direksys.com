<?php

function select_language(){
	global $cfg;
	$list = preg_split("/,/", $cfg['langs']);
	$output = "<select name='pref_language' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	for ($i = 0; $i < sizeof($list)/2; $i++) {
		$output .= "<option value='".$list[$i*2+1]."'>".$list[$i*2]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}

function table_width(){
	global $cfg;
	$list = preg_split("/,/", $cfg['screenres']);
	$output = "<select name='table_width' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	for ($i = 0; $i < sizeof($list);$i++) {
		$output .= "<option value='".$list[$i]."'>".$list[$i]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}

function select_style(){
	global $cfg;
	$list = preg_split("/,/", $cfg['styles']);
	$output = "<select name='pref_style' onFocus='focusOn( this )' onBlur='focusOff( this )'><option value=''>---</option>";
	$output .= "<option value='default'>Default</option>\n";
	for ($i = 0; $i < sizeof($list); $i++) {
		$output .= "<option value='".$list[$i]."'>".$list[$i]."</option>\n";
	}
	$output .= "</select>";
	return $output;
}


##############################################################
##############################################################
#Function: load_db_names
#	Extract specific field values from a table

#Created by:
#_Carlos Haas_
#
#Modified By:
#
#
#Parameters:
#- db: Table name
#- id_name: Field to look for
#- id_value: Value of the field
#- str_out: Names of the field to be returned
#
#Returns:
#A string with one or more field values concateated
#
#See Also:
#- load_name
#
function multicompany(){
##############################################################
##############################################################

	global $cfg,$def_e,$max_e;

	for ($i = 1; $i <= $cfg['max_e']; $i++) {
		
		unset($selected);
		$selected='';
		($i == 1) and ($selected='selected="selected"');
		
		if(!empty($cfg['app_e'.$i])) {
			$output .= "<option value='$i' $selected>".$cfg['app_e'.$i]."</option>\n";
		}
	}
	if ($output) {
		$output = "
		<select name='e' onFocus='focusOn( this )' onBlur='focusOff( this )'>
			<option value=''>---</option>
			<!--<option value='0'>". $cfg['app_e'.$i] ."</option>-->
			$output
		</select>";
		
	}
	
	return $output;
}	

function load_others_ses($ses,$username,$passwd,$passwdsha1) {
#---------------------------------------------------------
#---------------------------------------------------------
# Last Modified by RB on 11/08/2010: Shoplatino access blocked		
//Last modified on 16 Dec 2010 12:23:54
//Last modified by: MCC C. Gabriel Varela S. :Se incorpora Sha1
# Last Modified by RB on 05/04/2011 08:55:11 PM : Se activa la session de SOSL para que pueda entrar Bernardo
//Last modified on 11 May 2011 16:29:50
//Last modified by: MCC C. Gabriel Varela S. : Se hace ip global
	
	global $cfg,$path_sessions,$usr,$ip;

	## Others Sessions
	for ($e = 1; $e <= $cfg['max_e']; $e++) {
		if ($cfg['emp.'.$e.'.dbi_db']){
			#mysql_pconnect ($cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw']) or die(mysql_error());
			#mysql_select_db ($cfg['emp.'.$e.'.dbi_db']) or die(mysql_error());
			
			mysql_pconnect ($cfg['emp.'.$e.'.dbi_host'], $cfg['emp.'.$e.'.dbi_user'], $cfg['emp.'.$e.'.dbi_pw']) or die(mysql_error());
			mysql_select_db ($cfg['emp.'.$e.'.dbi_db']) or die(mysql_error());

			$result = mysql_query("SELECT * FROM admin_users WHERE UserName='$username' AND Status='Active'  AND ((length(Password)=13 and Password='$passwd')or(length(Password)=40 and Password='$passwdsha1'))"); // AND (expiration>NOW() or isNULL(expiration) or expiration = '0000-00-00' )");
			$rec = mysql_fetch_assoc($result);

			if ($rec['ID_admin_users'] and ($rec['expiration'] >= date('Y-m-d') or $rec['expiration'] == NULL or $rec['expiration'] == '0000-00-00')){
				if ($rec['IPFilter'] and checkip($rec['IPFilter'])){
					$sdata = '';
					foreach ($rec as $key=>$value){
						$sdata[strtolower($key)] = $value;
					}

					### Update User Info
					if ($in['pref_language']){
						$sdata['pref_language'] = $in['pref_language'];
						$result = mysql_query("UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip',pref_language='".$in['pref_language']."' WHERE ID_admin_users='".$usr['id_admin_users']."'");
					}else{
						$result = mysql_query("UPDATE admin_users SET LastLogin=NOW(),LastIP='$ip' WHERE ID_admin_users='".$usr['id_admin_users']."'");
					}
					(!$sdata['maxhits']) and ($sdata['maxhits'] = 20);
					(!$sdata['pref_style']) and ($sdata['pref_style'] = $cfg['default_style']);
					(!$sdata['pref_language'])  and ($sdata['pref_lang']  = $cfg['default_lang']);

					$path_sessions     = $cfg['emp.'.$e.'.auth_dir'];
//print "<pre>";
//print "sesion : $path_sessions \n";
//print_r($sdata);					
					### Save Session & Log
					save_auth_data($ses,$sdata);
					save_logs('login','');
//exit;
				}
			}
		}
	}
//	exit;
}

function load_name($db,$id_name,$id_value,$field) {
// --------------------------------------------------------
if($id_value!='NOW()' or $id_value!='CURDATE()')
	$id_value="'$id_value'";
$sth = mysql_query("SELECT ".$field." FROM ".$db." WHERE ".$id_name."=".$id_value.";") or die("Query failed : " . mysql_error());
return mysql_result($sth,0);
}


#############################################################################
#############################################################################
#   Function: encrip
#
#       Es: encrip. Codifica una cadena
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - this_string: cadena para codificar 
#
#  Returns:
#
#      - xs: cadena codificada
#
#
#   See Also:
#
#      <decrip>
#
function encrip ($this_string){
#############################################################################
#############################################################################


	$xs = "";
	$xc = "";
	$xn = 0;
	$xn2 = 0;
	
	for ($i = 1; $i <= strlen($this_string); $i++)
	{
		$xc = substr ($this_string, ($i - 1), 1);
		$xn = ord ($xc);

		$xn2 = $xn;

		if (($xn >= 48) && ($xn < 58))
		{
			if (($xn + $i) > 57)
				$xn2 = (48 + ((($xn + $i) - 58) % 10));
			else
				$xn2 = ($xn + $i);
		}

		if (($xn >= 65) && ($xn < 91))
		{
			if (($xn + $i) > 90)
				$xn2 = (65 + ((($xn + $i) - 91) % 26));
			else
				$xn2 = ($xn + $i);
		}

		if (($xn >= 97) && ($xn < 123))
		{
			if (($xn + $i) > 122)
				$xn2 = (97 + ((($xn + $i) - 123) % 26));
			else
				$xn2 = ($xn + $i);
		}
		$xs = $xs . chr($xn2);
	}
	return($xs);
}

#############################################################################
#############################################################################
#   Function: decrip
#
#       Es: Invrsa a decrip. Decodifica una cadena codificada con la funcion encrip previamente
#       En: 
#
#
#    Created on: 
#
#    Author: _Roberto Barcenas_
#
#    Modifications:
#
#        - Modified on ** by _Roberto Barcenas_ : 
#
#   Parameters:
#
#      - this_string: cadena codificada 
#
#  Returns:
#
#      - xs: cadena decodificada
#
#
#   See Also:
#
#      <encrip>
#
function decrip ($this_string){
#############################################################################
#############################################################################


	$xs = "";
	$xc = "";
	$xn = 0;
	$xn2 = 0;
	
	for ($i = 1; $i <= strlen($this_string); $i++)
	{
		$xc = substr ($this_string, ($i - 1), 1);
		$xn = ord ($xc);

		$xn2 = $xn;

		if (($xn >= 48) && ($xn < 58))
		{
			if (($xn - $i) < 48)
				$xn2 = 57 - ((58 - ($xn - ($i - 1))) % 10);
			else
				$xn2 = ($xn - $i);
		}

		if (($xn >= 65) && ($xn < 91))
		{
			if (($xn - $i) < 65)
				$xn2 = 90 - ((91 - ($xn - ($i - 1))) % 26);
			else
				$xn2 = ($xn - $i);
		}

		if (($xn >= 97) && ($xn < 123))
		{
			if (($xn - $i) < 97)
				$xn2 = 122 - ((123 - ($xn - ($i - 1))) % 26);
			else
				$xn2 = ($xn - $i);
		}
		$xs = $xs . chr($xn2);
	}
	return($xs);
}

?>
