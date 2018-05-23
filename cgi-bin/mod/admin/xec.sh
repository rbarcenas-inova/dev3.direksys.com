#!/bin/sh
MyDate=""
echo "Se ha iniciado el programa. Presione Ctrl+C para terminar."
while :
do
	if [ -e processC0.was  ];then
		MyDate=`date`
		echo "$MyDate: Comenzando a procesar captura por lotes"
		rm processC0.was
		for i in processC*
		do
			MyDate=`date`
			echo "$MyDate: Procesando archivo $i para captura"
			perl file1.pl $i C
			MyDate=`date`
			echo "$MyDate: $i hecho"
			rm $i
		done
		MyDate=`date`
		echo "$MyDate: Proceso de Captura por lotes completado"
	elif [ -e processS0.was ];then
		MyDate=`date`
		echo "$MyDate: Comenzando a procesar venta por lotes"
		rm processS0.was
		for i in processS*
		do
			echo "$MyDate: Procesando archivo $i para venta"
			perl file1.pl $i V
			echo "$MyDate: $i hecho"
			rm $i
		done
		echo "$MyDate: Proceso de Venta por lotes completado"
	else
		sleep 300
	fi
done
