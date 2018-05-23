

#############################################################################
#############################################################################
#   Function: view_zones
#
#       Es: Maneja el View de sl_zones
#       En: 
#
#
#    Created on: 07/22/2013  16:20:10
#
#    Author: _RB_
#
#    Modifications:
#
#   Parameters:
#
#		
#  Returns:
#
#      - Error/table with data
#
#   See Also:
#
#	<view_zones>
#
sub view_opr_zones {
#############################################################################
#############################################################################
#&cgierr;

	if($in{'id_zones_bulk'}) {

		#&cgierr($in{'id_zones_bulk'});
		@ary = split(/\n|\s|,/,$in{'id_zones_bulk'});
		
		if(scalar @ary > 0) {

			my $x,$modified;
			my $id_zones_group;
			for (0..$#ary){

				my $zipcode = &filter_values($ary[$_]);
				if( $zipcode ne ''){
					$id_zones_group .= $zipcode.','; 
					$x++;
				}

				if( $x >= 900 ){
					chop($id_zones_group);
					my ($sth) = &Do_SQL("UPDATE sl_zipcodes SET ID_zones = '$in{'id_zones'}' WHERE ZipCode IN ($id_zones_group);");
					$modified += $sth->rows();
					$x = 0;
					$id_zones_group = '';
				}
			}


			if( $x > 0 ){
				chop($id_zones_group);
				my ($sth) = &Do_SQL("UPDATE sl_zipcodes SET ID_zones = '$in{'id_zones'}' WHERE ZipCode IN ($id_zones_group);");
				$modified += $sth->rows();
				$x = 0;
				$id_zones_group = '';
			}


			if($modified > 0){

				&auth_logging('opr_zones_zip_added',$in{'id_zones'});

			}


		}
		my ($sth) = &Do_SQL("UPDATE sl_orders 
								INNER JOIN( 
									SELECT ZipCode, ID_zones
									FROM sl_zipcodes
									WHERE sl_zipcodes.ID_zones = ".int($in{'id_zones'})."
									GROUP BY ZipCode
								)sl_zipcodes ON shp_Zip = ZipCode  
							 SET sl_orders.ID_zones = sl_zipcodes.ID_zones 
							 WHERE 1;");
		$va{'messages'} = $sth->rows() . trans_txt('opr_orders_zone_updated');

	}elsif($in{'add_new'} and $in{'newzip'}){		
		#busca el ZipCode tabla de zipcodes
		my ($sth) = &Do_SQL("SELECT ZipCode FROM sl_zipcodes WHERE ZipCode='$in{'newzip'}' "); 
		if (my($zipCode) = $sth->fetchrow){
			#busca que no existan registros previos con ese ZipCode en la tabla de zones_zipcodes
			my ($sth) = &Do_SQL("UPDATE sl_zipcodes SET ID_zones=$in{'id_zones'} WHERE ZipCode='$in{'newzip'}'");
			my ($sth) = &Do_SQL("UPDATE sl_orders INNER JOIN sl_zipcodes ON shp_Zip = ZipCode SET sl_orders.ID_zones = sl_zipcodes.ID_zones WHERE sl_zipcodes.ID_zones = '$in{'id_zones'}';");
			&auth_logging('opr_zones_zip_added',$in{'id_zones'});
			$va{'tabmessages'} = &trans_txt('opr_zones_zip_added');
		}
	}elsif($in{'del_zip'}){
		#busca el ZipCode tabla de zipcodes
		my ($sth) = &Do_SQL("SELECT ZipCode FROM sl_zipcodes WHERE ZipCode='$in{'del_zip'}' "); 
		if (my($zipCode) = $sth->fetchrow){
			#busca que no existan registros previos con ese ZipCode en la tabla de zones_zipcodes
			my ($sth) = &Do_SQL("UPDATE sl_zipcodes SET ID_zones=NULL WHERE ZipCode='$in{'del_zip'}'");
			&auth_logging('opr_zones_zip_deleted',$in{'id_zones'});
			$va{'tabmessages'} = &trans_txt('opr_zones_zip_deleted');
		}
	}
}





1;