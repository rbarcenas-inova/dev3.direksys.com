#!/usr/bin/perl


	### Auto Get Home_dir
	use Cwd;
	my $dir = getcwd;
	my($b_cgibin,$a_cgibin) = split(/cgi-bin/,$dir);
	my $home_dir = $b_cgibin.'cgi-bin/common';
	
	require "$home_dir/reports/rep_orders.cgi" if ($in{'cmd'} =~ /^rep_orders/);
	require "$home_dir/reports/rep_cdr.cgi" if ($in{'cmd'} =~ /^rep_cdr/);
	require "$home_dir/reports/rep_bi.cgi" if ($in{'cmd'} =~ /^rep_bi/);
	require "$home_dir/reports/rep_cod.cgi" if ($in{'cmd'} =~ /^rep_cod/);
	#require "$home_dir/reports/rep_pp.cgi" if ($in{'cmd'} =~ /^rep_pp/);
	require "$home_dir/reports/rep_returns.cgi" if ($in{'cmd'} =~ /^rep_ret/);
	require "$home_dir/reports/rep_fin.cgi" if ($in{'cmd'} =~ /^rep_fin/);
	require "$home_dir/reports/rep_mm.cgi" if ($in{'cmd'} =~ /^rep_mm/);
	require "$home_dir/reports/rep_bills.cgi" if ($in{'cmd'} =~ /^rep_bills/);
	require "$home_dir/reports/rep_parts.cgi" if ($in{'cmd'} =~ /^rep_parts/);
	require "$home_dir/reports/rep_typify.cgi" if ($in{'cmd'} =~ /^rep_typify/);
	require "$home_dir/reports/rep_accounting.cgi";


# Funcion temporal para ocultar informacion
# By Alejandro Diaz
# 19/01/2017
sub temp_hide_data{
	my ($data,$type) = @_;

	if ($data eq ''){
		return '';
	}elsif ($type eq 'phone'){
		return '******'.substr $data, -4;
	}else{
		return '---';
	}
}

1;
