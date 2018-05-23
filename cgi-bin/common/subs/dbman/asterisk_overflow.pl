
#############################################################################
#############################################################################
#   Function: validate_asterisk_overflow
#
#       Es: Validacion de datos para el desbordamiento de asterisk
#       En: Validation for asterisk overflow
#
#
#    Created on: 2017-0612
#
#    Author: Jonathan Alcantara
#
#    Modifications:
#
#    Parameters:
#
#    Returns:
#
#    See Also:
#
sub validate_asterisk_overflow {
#############################################################################
#############################################################################

	my ($err, $temp_ini, $temp_fin, $tot_porc);

	$in{'porcentaje_trk1'} = $in{'porcentaje_trk1'} + 0;
	$in{'porcentaje_trk2'} = $in{'porcentaje_trk2'} + 0;
	$in{'porcentaje_trk3'} = $in{'porcentaje_trk3'} + 0;

	####
	#### 1) Permisos de edicion
	####
	if(!&check_permissions($in{'cmd'},'','')){ 
		$error{'message'} = trans_txt('not_auth');
		++$err;
		return $err;
	}
	####
	#### 2) Total de Porcentajes debe sumar siempre 100
	####
	$tot_porc = $in{'porcentaje_trk1'} + $in{'porcentaje_trk2'} + $in{'porcentaje_trk3'};
	if ($tot_porc > 100 || $tot_porc < 100){
		$error{'message'} = &trans_txt("asterisk_overflow_exceed");
		$error{'porcentaje_trk1'} = &trans_txt("asterisk_overflow_error_exceed");
		$error{'porcentaje_trk2'} = &trans_txt("asterisk_overflow_error_exceed");
		$error{'porcentaje_trk3'} = &trans_txt("asterisk_overflow_error_exceed");
		++$err;
		return $err;
	}
	####
	#### 3) Los porcentajes deben ser multiplos de 100
	####
	if ($in{'porcentaje_trk1'}%10 > 0){
		$error{'message'} = &trans_txt("asterisk_overflow_exceed");
		$error{'porcentaje_trk1'} = &trans_txt("asterisk_overflow_error_multiples");
		$error{'porcentaje_trk2'} = &trans_txt("asterisk_overflow_error_multiples");
		$error{'porcentaje_trk3'} = &trans_txt("asterisk_overflow_error_multiples");
		++$err;
		return $err;
	}
	if ($in{'porcentaje_trk2'}%10 > 0){
		$error{'message'} = &trans_txt("asterisk_overflow_exceed");
		$error{'porcentaje_trk1'} = &trans_txt("asterisk_overflow_error_multiples");
		$error{'porcentaje_trk2'} = &trans_txt("asterisk_overflow_error_multiples");
		$error{'porcentaje_trk3'} = &trans_txt("asterisk_overflow_error_multiples");
		++$err;
		return $err;
	}
	if ($in{'porcentaje_trk3'}%10 > 0){
		$error{'message'} = &trans_txt("asterisk_overflow_exceed");
		$error{'porcentaje_trk1'} = &trans_txt("asterisk_overflow_error_multiples");
		$error{'porcentaje_trk2'} = &trans_txt("asterisk_overflow_error_multiples");
		$error{'porcentaje_trk3'} = &trans_txt("asterisk_overflow_error_multiples");
		++$err;
		return $err;
	}
	$temp_ini = ($in{'hora_ini'}.$in{'min_ini'}).".00"+0;
	$temp_fin = ($in{'hora_fin'}.$in{'min_fin'}).".00"+0;

	if ($temp_ini > $temp_fin){
		$error{'message'} = &trans_txt("invalid");
		$error{'hora_ini'} = &trans_txt("invalid");
		$error{'hora_fin'} = &trans_txt("invalid");
		++$err;
		return $err;
	}
	return $err;

}


#############################################################################
#############################################################################
#   Function: updated_asterisk_overflow
#
#       Es: Se replica desbordamiento para las DIDs repetidas
#       En: Overflow replicates for repeated DIDs
#
#
#    Created on: 2017-0612
#
#    Author: Jonathan Alcantara
#
#    Modifications:
#
#    Parameters:
#
#    Returns:
#
#    See Also:
#
sub updated_asterisk_overflow {
#############################################################################
#############################################################################

	#REPLICAMOS MISMA CONFIGURACION PARA LAS DIDs IGUALES
	&Do_SQL("UPDATE sl_asterisk_overflow
			SET Porcentaje_trk1 = ".$in{'porcentaje_trk1'}.",
			Porcentaje_trk2 = ".$in{'porcentaje_trk2'}.",
			Porcentaje_trk3 = ".$in{'porcentaje_trk3'}.",
			Fecha = '".$in{'fecha'}."',
			Hora_ini = '".$in{'hora_ini'}.":".$in{'min_ini'}.":00',
			Hora_fin = '".$in{'hora_fin'}.":".$in{'min_fin'}.":00'
			WHERE did = '".$in{'did'}."'
			;");
	if ($cfg{'memcached'} == 1) {
		#BORRAMOS DEL MEMCACHE EL DID MODIFICADO
		&memcached_delete('Asterisk_Overflow_'.$in{'did'});
	}
}

1;