#####################################################################
########                   Zones               		    #########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq 4){
		## Notes Tab
		$va{'tab_type'}  = 'notes';
		$va{'tab_title'} = &trans_txt('notes');
		$va{'tab_table'} = 'sl_zones_notes';
	}elsif($in{'tab'} eq 5){
		## Notes Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_zones';
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs1
#
#       Es: Muestra los Zip Codes que estan relacionados con la zona
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Peña
#
#    Modifications:
#
#        - Modified on *01/11/2012* by _Enrique Peña_ : Se agrego el proceso para procesar batch de zipCodes
#        - Modified on *04/12/2012* by _Cesar Cedillo_ : Se agregaron los querys para la tabla modificada de zones_zipcodes
#
#   Parameters:
#
#      - id_zones Id de la zona a visualizar
#      - action	  Accion a realizar en el tab	
#      - add_new  Indicador para isnertar la relacion entre zona y zip code
#      - id_zip_code Id del Zip code
#      - id_zones_bulk Zip Codes a ingresar
#
#  Returns:
#
#      - Inserta la relacion entre zona y codigos postales
#      - Inserta varios Zip Codes a la vez
#      - Elimina la relacion entre zona y codigos postales
#      - Muestra los zip codes relacionados con la zona
#
#   See Also:
#
#
#
sub load_tabs1 {
#############################################################################
#############################################################################		

	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zipcodes WHERE ID_zones='$in{'id_zones'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){

			my (@c)   = split(/,/,$cfg{'srcolors'});
			(!$in{'nh'}) and ($in{'nh'}=1);
			$first = ($in{'nh'} - 1) * $usr{'pref_maxh'};
			($va{'pageslist'},$qs) = &pages_list($in{'nh'},"/cgi-bin/mod/$usr{'application'}/dbman",$va{'matches'},$usr{'pref_maxh'});
			my ($sth) = &Do_SQL("SELECT * FROM sl_zipcodes WHERE ID_zones='$in{'id_zones'}' LIMIT $first,$usr{'pref_maxh'};");
			while ($rec = $sth->fetchrow_hashref){					
				$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
				$va{'searchresults'} .= "  <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&view=$in{'view'}&tab=1&del_zip=$rec->{'ZipCode'}#initab'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'ZipCode'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'State'}-$rec->{'StateFullName'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'CountyName'}</td>\n";
				$va{'searchresults'} .= "   <td class='smalltext'>$rec->{'City'}</td>\n";				
				$va{'searchresults'} .= "</tr>\n";								
			}
	}else{
		$va{'pageslist'} = 1;
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}
}

#############################################################################
#############################################################################
#   Function: load_tabs2
#
#       Es: Muestra listado de los choferes asociados a esta zona
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Peña
#
#    Modifications:
#
#        - Modified on *01/11/2012* by _Enrique Peña_ : Se agrego el formulario para procesar batch de zipCodes
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
#
sub load_tabs2 {
#############################################################################
#############################################################################
	$va{'messages'} = "";
	## update
	if ($in{'action'}){		
		if($in{'add_new'}){						
			if (int($in{'id_warehouses'}) > 0 && int($in{'id_zones'}) > 0) {											
				my ($sthi) = &Do_SQL("SELECT COUNT(*) FROM sl_warehouses WHERE ID_warehouses = $in{'id_warehouses'} ");
				if (int($sthi->fetchrow) == 1){									
					my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_warehouses WHERE ID_zones = $in{'id_zones'} AND ID_warehouses = $in{'id_warehouses'}");
					if ($sth->fetchrow ==0){
						my ($qry_insert) = &Do_SQL("INSERT INTO sl_zones_warehouses (ID_zones,ID_warehouses,Status,Date,Time,ID_admin_users) VALUES ('$in{'id_zones'}','$in{'id_warehouses'}','Active',CURDATE(),CURTIME(),$usr{'id_admin_users'}) ");
						&auth_logging('zones_add_warehouse',$in{'id_warehouses'});
						$va{'tabmessages'} = &trans_txt($in{'cmd'}.'_warehouse_added');
					}
				}
			}
		}# End if add_new	
		
		if($in{'del_item'}){
			if (int($in{'id_zone_warehouses'}) > 0) {
				my ($qry_delete) = &Do_SQL("DELETE FROM sl_zones_warehouses WHERE ID_zones_warehouses = $in{'id_zone_warehouses'};");
				&auth_logging('zones_delete_warehouse',$in{'id_zone_warehouses'});
				$va{'tabmessages'} = &trans_txt($in{'cmd'}.'_id_warehouse_deleted');
			}
		}
	}
	
	my (@c)   = split(/,/,$cfg{'srcolors'});
	my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_zones_warehouses WHERE ID_zones ='$in{'id_zones'}'");
	$va{'matches'} = $sth->fetchrow;
	if ($va{'matches'}>0){
		my ($sth) = &Do_SQL("SELECT sl_w.ID_warehouses,sl_w.Name, sl_z.ID_zones_warehouses FROM sl_warehouses sl_w 
					INNER JOIN sl_zones_warehouses sl_z ON sl_z.ID_warehouses = sl_w.ID_warehouses
					WHERE sl_z.ID_zones = $in{'id_zones'} AND sl_w.Type = \"Virtual\" ");					
		# my ($sth) = &Do_SQL("SELECT * FROM sl_zones_warehouses WHERE ID_zones ='$in{'id_zones'}' ");				
		while ($rec = $sth->fetchrow_hashref){
			$va{'searchresults'} .= "<tr bgcolor='$c[$d]' onmouseover='m_over(this)' onmouseout='m_out(this)'>\n";
			$va{'searchresults'} .= " <td class='smalltext'><a href='/cgi-bin/mod/$usr{'application'}/dbman?cmd=$in{'cmd'}&action=1&view=$in{'view'}&tab=$in{'tab'}&tabs1=$in{'tab'}&del_item=1&id_zone_warehouses=$rec->{'ID_zones_warehouses'}'><img src='$va{'imgurl'}/$usr{'pref_style'}/b_drop.png' title='Drop' alt='' border='0'></a></td>\n";
			$va{'searchresults'} .= " <td class='smalltext'> <a href=\"/cgi-bin/mod/$usr{'application'}/dbman?cmd=opr_warehouse&view=$rec->{'ID_warehouses'}\">$rec->{'ID_warehouses'}</a></td>";
			$va{'searchresults'} .= " <td class='smalltext' >$rec->{'Name'} </td>\n";
			$va{'searchresults'} .= "</tr>\n";
		 }
		
	}else{
		$va{'searchresults'} = qq|
			<tr>
				<td colspan='5' align="center">|.&trans_txt('search_nomatches').qq|</td>
			</tr>\n|;
	}

}

#############################################################################
#############################################################################
#   Function: load_tabs3
#
#       Es: Muestra el formulario para ingresar varios zip codes de una sola vez
#       En: English description if possible
#
#
#    Created on: 26/10/2012  13:20:10
#
#    Author: Enrique Peña
#
#    Modifications:
#
#        - Modified on *01/11/2012* by _Enrique Peña_ : Se agrego el formulario para procesar batch de zipCodes
#
#   Parameters:
#
#  Returns:
#
#   See Also:
#
#
#
sub load_tabs3 {
#############################################################################
#############################################################################

}

1;