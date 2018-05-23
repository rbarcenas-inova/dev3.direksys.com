[ip_header_blank]
[va_javascriptvar]

<form method="post" action="/cgi-bin/common/apps/ajaxbuild" name="sitform">
	<input type="hidden" name="id_customers" value="[in_id_customers]">
	<input type="hidden" name="ajaxbuild" value="change_cust_password">
	<input type="hidden" name="view" value="[in_id_customers]">
	<input type="hidden" name="action" value="1">
	<input type="hidden" name="cmd" value="[in_cmdo]">
	<table width="100%" border="0"  class="gborder" align="center">
		<tr>
			<td colspan="3" class="smallfieldterr">The password is about to be changed. Please review all the information before proceed<br />&nbsp;[va_tabmessages]</td>
		</tr>
		<tr>
			<td class="menu_bar_title" colspan="3">Change customer Password</td>
		</tr>	
		<tr>
			<td class="smalltext">Email: <span class="smallfieldterr">*</span></td>
			<td >
				<input name="email" value="[in_email]" type="text" size=35 onFocus='focusOn( this )' onBlur='focusOff( this )'>
			</td>
		</tr>
		<tr>
			<td class="smalltext">Are you sure you want to reset the customer password?: <span class="smallfieldterr">*</span></td>
			<td >
				<input type="radio" name="action_change" value="Yes">Yes
				<input type="radio" name="action_change" value="No">No
			</td>
		</tr>
		<tr>
			<td align="center" colspan="3"><input type="submit" value="Change" class="button"></td>
		</tr>
	</table>
</form>


<script language="javascript">
<!--

chg_radio('action_change','[in_action_change]');

//-->
</script>