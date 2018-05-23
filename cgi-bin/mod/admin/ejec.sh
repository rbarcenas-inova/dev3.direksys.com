#!/bin/sh
MyDate=""
MyFiles=""
MyFormatD=""
echo "Se ha iniciado el programa. Presione Ctrl+C para terminar."
cd /home/www/domains/dev.shoplatinotv_new.com/docs/shpfiles
while :
do
	if [ -e processC0.was  ];then
		MyDate=`date`
		echo "$MyDate: Comenzando a procesar captura por lotes"
		rm processC0.was
		MyFormatD=`date +%m%d%y%H%M`
		for i in processC*
		do
			MyDate=`date`
			echo "$MyDate: Procesando archivo $i para captura"
			./file1.pl $i C $MyFormatD
			MyDate=`date`
			echo "$MyDate: $i hecho"
			rm $i
		done
		MyDate=`date`
		echo "$MyDate: Proceso de Captura por lotes completado"
	elif [ -e processS0.was ];then
		MyDate=`date`
		MyFormatD=`date +%m%d%y%H%M`
		echo "$MyDate: Comenzando a procesar venta por lotes"
		rm processS0.was
		for i in processS*
		do
			MyDate=`date`
			echo "$MyDate: Procesando archivo $i para venta"
			./file1.pl $i V $MyFormatD
			MyDate=`date`
			echo "$MyDate: $i hecho"
			rm $i
		done
		MyDate=`date`
		echo "$MyDate: Proceso de Venta por lotes completado"
	else
		sleep 300
	fi
done
