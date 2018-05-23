
sub view_mer_noninventory {
# --------------------------------------------------------
	if ($in{'action'} and $in{'tab'} eq 4){
		my ($query);
		$in{'newpurchaseid_accounts'} = int($in{'newpurchaseid_accounts'});
		$in{'newsaleid_accounts'} = int($in{'newsaleid_accounts'});
		if ($in{'newpurchaseid_accounts'}){
			$query .= "PurchaseID_accounts=$in{'newpurchaseid_accounts'}," ;
			$in{'purchaseid_accounts'} = $in{'newpurchaseid_accounts'};
		}
		if ($in{'newassetid_accounts'}){
			$query .= "AssetID_accounts=$in{'newassetid_accounts'}," ;
			$in{'assetid_accounts'} = $in{'newassetid_accounts'};
		}
		if ($in{'newtax'}){
			$query .= "Tax='".&filter_values($in{'newtax'})."',";
			$in{'tax'} = $in{'newtax'};
		}
		chop($query);
		if ($query){
			my ($sth) = &Do_SQL("UPDATE sl_noninventory SET $query WHERE id_noninventory='$in{'id_noninventory'}'");
			&auth_logging('mer_noninventory_accounting',$in{'id_noninventory'});
		}
	}

	my ($id_accounting, $name) = &Do_SQL(qq|SELECT id_accounting, name from sl_accounts where ID_accounts = '$in{'purchaseid_accounts'}'|)->fetchrow();
	$va{'paccount_name'} = format_account($id_accounting)." $name";

	$va{'aaccount_name'} = &load_name('sl_accounts','ID_accounts',$in{'assetid_accounts'},'Name');

}
sub loading_mer_noninventory{
	my ($id_accounting, $name) = &Do_SQL(qq|SELECT id_accounting, name from sl_accounts where ID_accounts = '$in{'purchaseid_accounts'}'|)->fetchrow();
	$va{'paccount_name'} = format_account($id_accounting)." $name";
}

1;