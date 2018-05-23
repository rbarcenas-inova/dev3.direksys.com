		
function chgtab(tab){	
		Spry.Utils.updateContent('a1','admin?cmd=[in_cmd]&xtabs=skustransfers&tab=1&id_skustransfers=[in_id_skustransfers]&[va_typeaction]=[in_id_skustransfers]&tbnow=[in_tab]&nh=[in_nh]');
		Spry.Utils.updateContent('a2','admin?cmd=[in_cmd]&xtabs=skustransfers&tab=2&id_skustransfers=[in_id_skustransfers]&[va_typeaction]=[in_id_skustransfers]&tbnow=[in_tab]&nh=[in_nh]&filter=[va_query]');
		Spry.Utils.updateContent('a3','admin?cmd=[in_cmd]&xtabs=skustransfers&tab=3&id_skustransfers=[in_id_skustransfers]&[va_typeaction]=[in_id_skustransfers]&tbnow=[in_tab]&nh=[in_nh]');
}

	<script type="text/javascript" language="JavaScript">
		Spry.Utils.onDOMReady(chgtab('[in_cmd]'));	
	</script>