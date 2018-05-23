<style> 
	html{
		margin:0px;
		height:100%;
	}
	body{
		padding:0px;
		margin:0px;
		height:100%;
		background-image: url( ); 
		background-repeat: no-repeat; 
		background-attachment:fixed;
		background-position: bottom left;
		background-color:#ffffff;
		font-family: arial;
		font-size:14px;
		line-height:23px;
		color:#333333;
	}
	font.texto {
	    font-size: 14px;
	    font-family: century gothic, Arial;
	    font-weight: normal;
	    color: #111111; 
	}
	A.buttonbig:link		{
		background-color: #90ba2b;
		background-image: url(/sitimages/app_bar/mod/button3.png);
		background-position: center bottom;
		background-repeat: repeat;
		color:#ffffff;
		cursor: pointer;
		font-family: Arial;
		font-weight: bold;
		font-size: 16px;
		border: 1px solid #77ac07;
		padding: 19px 35px;
		text-align:center;
		text-shadow:#888888 1px 1px 1px;
		-moz-border-radius: 7px;
		border-radius: 7px;text-decoration: none;
		-moz-box-shadow: 0 0px 6px #cccccc;
		-webkit-box-shadow: 0 0px 6px #cccccc;
		box-shadow: 0 0px 6px #cccccc;
	}
	A.buttonbig:visited		{
		background-color: #90ba2b;
		background-image: url(/sitimages/app_bar/mod/button3.png);
		color:#ffffff;
		border: 1px solid #77ac07;text-decoration: none;
	}
	A.buttonbig:hover		{
		background-color: #90ba2b;
		background-image: url(/sitimages/app_bar/mod/button4.png);
		color:#ffffff;
		border: 1px solid #8ec012;text-decoration: none;
	}
</style>

<img src="/sitimages/password.png" style="width:100%;"><br> 

<table border=0 width=100% cellpadding=25px>
	<td> 
		<font class=texto>
		<font size=5>Actualiza tu Password</font><br><br>
		Tu password expirar&aacute; en <span id="number_days"> - </span> d&iacute;as. <b>Por favor actualiza tu password</b>. <br><br><br>
			<p align=right>
		<a id="btn_update_pswd" href="/cgi-bin/mod/admin/admin?cmd=myprefs_mypass" target="_parent"  class="buttonbig">Ir a Actualizar</a>
		<!--onclick="javascript:parent.jQuery.fancybox.close();"-->
	</td>
</table> 