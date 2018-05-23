
sub repman_cust_totalorders{
# --------------------------------------------------------
	my (@in_data) = @_;
	if ($in_data[0]>0){
		my ($sth) = &Do_SQL("SELECT SUM(OrderNet) FROM sl_orders WHERE ID_customers=$in_data[0]");
		return $sth->fetchrow();
	}
	return '';
}



sub repman_cust_percentcontact{
# --------------------------------------------------------
	my (@in_data) = @_;
	$vars = scalar(@in_data);
	$where = $in_data[$vars - 1];
	$query = "SELECT (CAST($in_data[1] AS DECIMAL(10,2))/CAST(COUNT(DISTINCT ID_customers) AS DECIMAL(10,2)))*100.00 FROM sl_orders WHERE 1 ".$where;
	#print $query;
	my ($sth) = &Do_SQL($query);
	return $sth->fetchrow();
}

sub repman_cust_channels{
# --------------------------------------------------------
	my (@in_data) = @_;
	my ($ids) = $in_data[9];
	$query = "SELECT group_concat(sl_salesorigins.Channel ) FROM sl_salesorigins WHERE sl_salesorigins.Status='Active'";
	
	if ($ids ne ''){
		$query .= " AND sl_salesorigins.ID_salesorigins IN (".$ids.")";
	}
	
	my ($sth) = &Do_SQL($query);
	
	return $sth->fetchrow();
}

1;