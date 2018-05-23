#!/usr/bin/perl
#####################################################################
########                   Accounting Periods	        		           		#########
#####################################################################
sub load_tabsconf {
# --------------------------------------------------------
	if ($in{'tab'} eq '1'){
		## Logs Tab
		$va{'tab_type'}  = 'logs';
		$va{'tab_title'} = &trans_txt('logs');
		$va{'tab_table'} = 'sl_accounting_periods';
	}
}

1;