<?php
$ch = curl_init('https://via.banorte.com');
curl_setopt($ch, CURLOPT_SSLVERSION,3);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$salida =  curl_exec($ch);
if($salida === false)
{
    echo 'Curl error: ' . curl_error($ch);
}
else
{
    echo 'Operación completada sin errores';
	print_r(curl_getinfo($ch));
	echo $salida;
}
curl_close($ch);
?>
