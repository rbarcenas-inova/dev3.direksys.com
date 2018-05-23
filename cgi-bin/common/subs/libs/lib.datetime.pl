sub format_date {
# --------------------------------------------------------
# Created on: 11/15/2007 9:15AM
# Author: Rafael Sobrino
# Description : changes a date format from dd/mm/yyyy to yyyy-mm-dd
# Notes: 

	my ($mydate) = @_;
	my (@ary) = split('\/', $mydate);
	#$mydate =~ s/\//\-/g;
	foreach $value (@ary){
		if ($value < 10){
			$value = "0$value";
		}
	}
	
	return "$ary[2]-$ary[1]-$ary[0]";
}


sub format_shour {
	my ($shour) = @_;
	
	return $shour.":00";
}

1;