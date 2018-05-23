sub validate_opr_coverages {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 02/03/2009
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
# Last Modified on: 02/18/09 16:05:28
# Last Modified by: MCC C. Gabriel Varela S: Se cambia la validación

	#if(($in{'country'} eq "USA" && $in{'state'} !~ /-/ && $in{'state'}) || ($in{'country'} ne "USA" && $in{'state'} =~ /-/ && $in{'state'})){
	if(($in{'country'} eq "" && $in{'state'} =~ /-/ && $in{'state'})){
		$error{'country'} = &trans_txt('invalid');
		$error{'state'} = &trans_txt('invalid');
		$va{'message'} = &trans_txt('reqfields');
		++$err;
	}
}

sub view_opr_coverages{
# --------------------------------------------------------
# Forms Involved: 
# Created on: 03/09/09 12:23:31
# Author: MCC C. Gabriel Varela S.
# Description :   
# Parameters :
	$va{'warehouses_name'}=&load_name('sl_warehouses','ID_warehouses',$in{'id_warehouses'},'Name');
}


1;