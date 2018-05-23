[ip_header_blank]
[va_javascriptvar]

<form method="post" action="/cgi-bin/common/apps/ajaxbuild" name="sitform">
	<input type="hidden" name="id_customers" value="[in_id_customers]">
	<input type="hidden" name="ajaxbuild" value="ajax_cupon_window">
	<input type="hidden" name="view" value="[in_id_customers]">
	<input type="hidden" name="action" value="1">
	<input type="hidden" name="cmd" value="[in_cmdo]">
	<table width="100%" border="0"  class="gborder" align="center">
		<tr>
			<td colspan="3" class="smallfieldterr"><P style='font-size:14'>[va_tabmessages]</P></td>
		</tr>
		<tr>
			<td class="menu_bar_title" colspan="3"><P style='font-size:14'>Elegir uno de los productos e ingresar email del cliente.</P><P style='font-size:10;'><span class="smallfieldterr">El email será validado, si el cliente no tiene email no se puede dar esta oferta</span></P></td>
		</tr>
		<tr>
			<td class="smalltext"><span class="smallfieldterr">[er_id_products]</span></td>
			<td >
				<input name="id_products" value="988639" class="radio" type="radio"> Algafit (988639)<br>
				<input name="id_products" value="151903" class="radio" type="radio"> Rejuvital (151903)<br>
				<input name="id_products" value="156483" class="radio" type="radio"> Green Marvel (156483)<br>
				<input name="id_products" value="469900" class="radio" type="radio"> Charakani (469900)<br>
			</td>
		</tr>
		<tr>
			<td class="smalltext">Email: <span class="smallfieldterr">*[er_email]</span></td>
			<td >
				<input name="email" value="[in_email]" type="text" size=35 onFocus='focusOn( this )' onBlur='focusOff( this )'>
			</td>
		</tr>
		
		
		<tr>
			<td align="center" colspan="3"><input type="submit" value="Aceptar" class="button"></td>
		</tr>
	</table>
</form>


<script language="javascript">
<!--

chg_radio('id_products','[in_id_products]');

//-->
</script>