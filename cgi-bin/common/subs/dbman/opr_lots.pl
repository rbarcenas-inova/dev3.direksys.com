#########################################################	
#	Function: 
#   	view_opr_lots
#	Description:
#		Es: Agrega o elimina items a un lote con sus respectivas validaciones
#		En: Add or drop items to the lots, with their respective validations
#	Created by:
#		Josue Miranda
#
#	Modified By:
#
#   	Parameters:
#
#   	Returns:
#
#   	See Also:
#
sub view_opr_lots {

	if($in{'status'}){
		if($in{'status'} eq "New"){
			$va{"menu_edit"}="<select name='status'><option value='New'>New</option><option value='Processed'>Processed</option><option value='Inactive'>Inactive</option><select>";
		}else{
			$va{"menu_edit"}="<select name='status'><option value='Processed'>Processed</option><option value='Inactive'>Inactive</option><select>";
		}
	}

	if ($in{'action'}) { 

			############################
			####### Tab2: Add Lot
			############################

			if($in{'additem'}) {
				
						my $query = "SELECT COUNT(*) FROM sl_lots_items WHERE ID_lots=$in{'id_lots'} AND ID_lots_children=$in{'additem'} AND Status='Active';";
						my ($exist_active) = &Do_SQL($query);

						$query = "SELECT COUNT(*) FROM sl_lots_items WHERE ID_lots=$in{'id_lots'} AND ID_lots_children=$in{'additem'} AND Status='Inactive';";
						my ($exist_inactive) = &Do_SQL($query);

						if ($exist_active->fetchrow() > 0) {
							$va{'message_error'} = &trans_txt('opr_lots_error');
						}elsif($exist_inactive->fetchrow() > 0){
							$query = "UPDATE sl_lots_items SET Status='Active' WHERE ID_lots=$in{'id_lots'} AND ID_lots_children=$in{'additem'};";
						my ($sth) = &Do_SQL($query);
						$va{'message_good'} = &trans_txt('opr_lots_added');
						}else{
						$query = "INSERT INTO sl_lots_items(ID_lots,ID_lots_children, Status, Date, Time, ID_admin_users) Values ($in{'id_lots'},$in{'additem'}, 'Active', CURDATE(), CURTIME(), '$usr{'id_admin_users'}');";
						my ($sth) = &Do_SQL($query);
						my ($t) = $sth->rows();
						$va{'message_good'} = &trans_txt('opr_lots_added');
						}
						
					}elsif($in{'dropitem'}) {
				
						my $query = "UPDATE sl_lots_items SET Status='Inactive' WHERE ID_lots=$in{'id_lots'} AND ID_lots_children= $in{'dropitem'}";
						my ($sth) = &Do_SQL($query);
						my ($t) = $sth->rows();
						$va{'message_good'} = &trans_txt('opr_lots_deleted');
					} 
			}
		}


1;