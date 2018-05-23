#############################################################################
#############################################################################
# Function: detail_movements_auxiliary
#
# Es: Muestra los registros de sl_movements_auxiliary
# En:
#
# Created on: 19/12/2016
#
# Author: Jonathan Alcantara
#
# Modifications:
#
# Parameters:
#
# Returns:
#
# See Also:
#
sub detail_movements_auxiliary {
	use Data::Dumper;

	$va{'searchresults'} = "";

	my $sth = &Do_SQL(" SELECT
						movements.ID_movements
						,sl_movements_auxiliary.FieldName
						,sl_movements_auxiliary.FieldValue
						#,sl_accounting_periods.Short_Name
						FROM (
							SELECT sl_movements.ID_movements
							FROM sl_movements
							WHERE ID_tableused = '$in{'id_orders'}'
							AND tableused = 'sl_orders'
							AND Status = 'Active'
							UNION
							SELECT sl_movements.ID_movements
							FROM sl_movements
							WHERE ID_tablerelated = '$in{'id_orders'}'
							AND tablerelated = 'sl_orders'
							AND Status = 'Active'
						) movements
						INNER JOIN sl_movements_auxiliary ON sl_movements_auxiliary.ID_movements = movements.ID_movements
						INNER JOIN sl_accounting_periods ON sl_accounting_periods.ID_accounting_periods = sl_movements_auxiliary.FieldValue
						ORDER BY movements.ID_movements ASC"
	);
	$row_cont = 1;
	$prev_mov = 0;
	$style_extra = '';

	@$tr_class_arr;
	@$border_invisible;

	$tr_class_arr[0] = 'active';
	$tr_class_arr[1] = 'info';
	$tr_class_arr[2] = 'success';
	$tr_class_arr[3] = 'warning';
	$tr_class_arr[4] = 'danger';

	$border_invisible[0] = 'border:1px solid #f0f3f5';
	$border_invisible[1] = 'border:1px solid #dbf0f7';
	$border_invisible[2] = 'border:1px solid #cee';
	$border_invisible[3] = 'border:1px solid #fdebd1';
	$border_invisible[3] = 'border:1px solid #ffdedd';

	while ($rec=$sth->fetchrow_hashref){
		if ($row_cont >= 4) {
			$row_cont = 0;
		}
		$style_extra = '';
		if ($prev_mov != 0 && $prev_mov != $rec->{'ID_movements'}) {
			$row_cont++;
		} else {
			$style_extra = $border_invisible[$row_cont];
		}
		$va{'searchresults'} .= "<tr class='$tr_class_arr[$row_cont]' >\n";

		if ($prev_mov != $rec->{'ID_movements'}) {
			$va{'searchresults'} .= "	<td style='white-space:nowrap; $style_extra'>$rec->{'ID_movements'}</td>\n";
		} else {
			$va{'searchresults'} .= "	<td style='white-space:nowrap; $style_extra'></td>\n";
		}
		$va{'searchresults'} .= "	<td style='white-space:nowrap; $style_extra'>$rec->{'FieldName'}</td>\n";
		$va{'searchresults'} .= "	<td style='white-space:nowrap; $style_extra'>$rec->{'FieldValue'}</td>\n";
		$va{'searchresults'} .= "</tr>\n";

		$prev_mov = $rec->{'ID_movements'};
	}
	print "Content-type: text/html\n\n";
	print &build_page('movements_auxiliary.html');
}

1;
