
sub validate_opr_claims{
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/12/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	
	my ($err);
	if(!$in{'id_orders'}){
		$error{'id_orders'} = &trans_txt('required');
		$va{'message'} = &trans_txt('reqfields');
		++$err;
	}
	if(!$in{'id_products'}){
		$error{'id_products'} = &trans_txt('required');
		$va{'message'} = &trans_txt('reqfields');
		++$err;
	}
	if($in{'id_orders_products'} && $in{'id_orders'} && $in{'id_products'}){
		my ($sth) = &Do_SQL("SELECT COUNT(*) FROM sl_orders_products WHERE ID_orders='".$in{'id_orders'}."' AND ID_products='".$in{'id_products'}."' AND ID_orders_products='".$in{'id_orders_products'}."' ");
		if($sth->fetchrow!=1){
			$error{'id_orders'} = &trans_txt('invalid');
			$error{'id_products'} = &trans_txt('invalid');
			++$err;
		}
	}
	
	return $err;
	
}

sub view_opr_claims {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/12/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if ($in{'id_orders_products'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products='$in{'id_orders_products'}'");
		my ($rec) = $sth->fetchrow_hashref;
		my (@cols)= ('ID_orders','ID_products');
		for (0..$#cols){
			$in{lc($cols[$_])} = $rec->{$cols[$_]};
			$in{'orders_products.'.lc($cols[$_])} = $rec->{$cols[$_]};
		}
		
		# This condition is added to work for wholesale orders
		if ($rec->{Related_ID_products}) {
			$va{'id_products'} = substr($rec->{Related_ID_products},5,6);
			$va{'products_desc'} = '<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_parts&view='.$va{'id_products'}.'">'.$va{'id_products'}.' '.substr($in{'orders_products.related_id_products'},5,9)." (".&load_db_names('sl_parts','ID_parts',substr($rec->{Related_ID_products},5,6),'[Name] [Model]').")".'</a>';
		}else {
			$va{'id_products'} = substr($rec->{ID_products},3,6);
			$va{'products_desc'} = '<a href="/cgi-bin/mod/[ur_application]/dbman?cmd=mer_products&view='.$va{'id_products'}.'">'.$va{'id_products'}.' '.substr($in{'orders_products.id_products'},3,9)." (".&load_db_names('sl_products','ID_products',substr($rec->{ID_products},3,6),'[Name] [Model]')." ".&load_db_names('sl_skus','ID_sku_products',$rec->{ID_products},'[choice1] [choice1] [choice3] [choice4]').")".'</a>';
		}
	}
}

sub loading_opr_claims {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if ($in{'id_orders_products'}){
		my ($sth) = &Do_SQL("SELECT * FROM sl_orders_products WHERE ID_orders_products='$in{'id_orders_products'}'");
		my ($rec) = $sth->fetchrow_hashref;
		my (@cols)= ('ID_orders','ID_products');
		for (0..$#cols){
			$in{lc($cols[$_])} = $rec->{$cols[$_]};
			$in{'orders_products.'.lc($cols[$_])} = $rec->{$cols[$_]};
		}
	}
}

sub advsearch_opr_claims {
# --------------------------------------------------------

# Author: Jose Ramirez Garcia
# Created on: 12/15/2008
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if(($in{'id_orders'} || $in{'id_products'}) && !$in{'id_orders_products'}){
		my ($qry);
		if($in{'id_orders'}){
			$qry = " ID_orders='".$in{'id_orders'}."' ";
		}
		if($in{'id_products'}){
			$qry .= " ID_products='".$in{'id_products'}."' ";
		}
		my ($sth)	= &Do_SQL("SELECT ID_orders_products FROM sl_orders_products WHERE $qry");
		$in{'id_orders_products'} = $sth->fetchrow_array;
	}
	return &query('sl_claims');

}


#############################################################################
#############################################################################
# Function: restrict_status_on_add
#
# Es: Evita la seleccion de un status en la accion add
# En: Avoid status selection on add action
#
#
# Created on: 01/04/2013
#
# Author: Erik Osornio
#
# Modifications:
#
# - Modified on ** by *** :
#
# Parameters:
#
# - 
#
# Returns:
#
# String
#
# See Also:
#
# <>
#

sub restrict_status_on_add {
# --------------------------------------------------------

# Author: Erik Osornio
# Created on: 01/04/2013
# Last Modified on: 
# Last Modified by: 
# Description : 
# Forms Involved: 
# Parameters : 
	if ($in{'add'}) {
		$in{'status'}='New';
		return '<input type="hidden" name="status" value="'.$in{'status'}.'"  />'; 
	}
	else
	{
		return &build_page('func:claims_status.html');
	}
	
}


1;