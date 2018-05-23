<html>
<head>
	<style type="text/css">
	textarea{
		font-family: arial;
		font-size: 11pt;
		width: 800px;
		height: 500px;
	}
	</style>

	<script type="text/javascript">
	    window.onbeforeunload = function() {
	        return "Se perderán los datos si continúa con esta acción, está seguro de continuar?";
	    }
	</script>

</head>
<body>
	<form method="POST" action="<?php $_SERVER[PHP_SELF]?>">
		<textarea name="texto"> <?php echo (isset($_POST['texto'])) ? $_POST['texto'] : ''; ?> </textarea>
	</form>
</body>