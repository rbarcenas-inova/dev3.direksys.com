<?php
	#if (!$sys_err){
	#	exit;
	#}
?>
<head>
<title>PHP - ERROR</title>
</head>

<body BGCOLOR="#FFFFFF" LINK="#FF0000" VLINK="#FF0000" ALINK="#FF0000">

<table BORDER="0" WIDTH="550" CELLPADDING="20" CELLSPACING="0">
  <tr>
    <td BGCOLOR="#FF0000" colspan="2"><font size="5" color="#FFFFFF" face="Arial"><b>PHP-Error</b></font></td>
  </tr>
</table>
<table BORDER="0" WIDTH="550" CELLPADDING="2" CELLSPACING="0">
	<tr>
	   <td valign='top' width='200'><font face='Arial' size='3'>Error Message</font></td>
	   <td><font face='Arial' size='3' color='#FF0000'><b><?=$sys_err?></b></font></td>
	</tr>
      <tr>
          <td colspan="2"><p>&nbsp</p><font face='Arial' size='2'>If the problem persists, please contact us with the above Information.</font><br>
		<font face='Arial' size='2'><a href="mailto:<?=$in['systememail']?>"><?=$in['systememail']?></a></font></td>
      </tr>
  </table>
<?php
	if ($in['debug_mode']){
		echo "<table border='0' width='550' cellpadding='2' cellspacing='0' bgcolor='#CACACA'>\n	<tr>\n	   <td><pre>\n";
		echo "\nForm Variables IN\n-------------------------------------------\n";
		foreach ($in as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\n_GET\n-------------------------------------------\n";
		foreach ($_GET as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\n_POST\n-------------------------------------------\n";
		foreach ($_POST as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\nForm Variables ERROR\n-------------------------------------------\n";
		foreach ($error as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\nForm Variables VA\n-------------------------------------------\n";
		foreach ($va as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\nEnvironment Variables\n-------------------------------------------\n";
		foreach ($_ENV as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\nCookies Variables\n-------------------------------------------\n";
		foreach ($_COOKIE as $key=>$value ) {
			echo "$key : ".htmlentities ($value)."\n";
		}
		echo "\nGlobals Variables\n-------------------------------------------\n";
		foreach ($GLOBALS as $key=>$value ) {
			echo "$key : $value\n";
		}

		echo "\n</pre></td></tr></table>";
	}
?>
<p>&nbsp;</p>
<p>&nbsp;</p>

</body>
</html>
<?php
	exit;
?>