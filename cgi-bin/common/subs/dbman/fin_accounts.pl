##########################################################
##	ACCOUNTING
##  BDMAN fin_accounts
##########################################################

#############################################################################
#############################################################################
#   Function: view_fin_accounts
#
#       Es: View de Cuentas Contables
#       En: 
#
#
#    Created on: 2016-01-01
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub view_fin_accounts{
#############################################################################
#############################################################################

	if($in{'flagstatus'}==1){
		&Do_SQL("UPDATE sl_accounts SET status='".$in{'chgstatus'}."' WHERE ID_accounts=".$in{'view'});
	}

	my ($sth) = &Do_SQL("SELECT Status, ID_parent, Segment FROM sl_accounts WHERE ID_accounts='".$in{'view'}."'");
	($va{'status'}, $va{'segment'}, $id_parent)=$sth->fetchrow_array();
	
	if($va{'status'} eq "Active"){
		$va{'changestatus'} .= qq|	
									<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_accounts&view=$in{'view'}&chgstatus=Inactive&flagStatus=1">Inactive</a> 
								 |;
	}else{
		$va{'changestatus'} .= qq|	
									<a href="/cgi-bin/mod/$usr{'application'}/dbman?cmd=fin_accounts&view=$in{'view'}&chgstatus=Active&flagStatus=1">Active</a> 
								 |;
	}


	my ($sth2) = &Do_SQL("SELECT ID_accounting, Name FROM sl_accounts WHERE ID_accounts='".$id_parent."'");
	my $rec2=$sth2->fetchrow_hashref;

	$va{'id_parent_accounting'}=&format_account($rec2->{'ID_accounting'}).' '.$rec2->{'Name'};

}

#############################################################################
#############################################################################
#   Function: view_fin_accounts
#
#       Es: Previo a la busqueda de Cuentas Contables
#       En: 
#
#
#    Created on: 2016-06-23
#
#    Author: ISC Alejandro Diaz
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub presearch_fin_accounts{
#############################################################################
#############################################################################
	# Se eliminan variables para que funcione search
	delete($in{'description'});
	delete($in{'taxline'});
	delete($in{'id_accategories'});
}



#############################################################################
#############################################################################
#   Function: validate_fin_accounts
#
#       Es: Validacion previa a guardar Info
#       En: 
#
#
#    Created on: 2016-07-18
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub validate_fin_accounts{
#############################################################################
#############################################################################
	$in{'level'} = &get_level_account($in{'id_parent'});
	return 0;
}


#############################################################################
#############################################################################
#   Function: get_level_account
#
#       Es: Obtiene el nivel de una cuenta
#       En: 
#
#
#    Created on: 2016-07-18
#
#    Author: Fabian Cañaveral
#
#    Modifications:
#
#
#   Parameters:
#
#      -   
#
#  Returns:
#
#      - 
#
#   See Also:
#
#
sub get_level_account{
#############################################################################
#############################################################################
	$id_parent = shift;
	if($id_parent){
		return &Do_SQL("SELECT level+1 FROM sl_accounts where ID_accounts = '$id_parent' LIMIT 1")->fetchrow();
	}
	return 0;
}



1;