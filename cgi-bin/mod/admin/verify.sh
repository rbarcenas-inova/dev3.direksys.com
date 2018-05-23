#!/bin/sh
MyGrep=""
top -n 1 -b > top.log
MyGrep=`grep ejec.sh top.log`
if [ -z "$MyGrep"  ];then
	echo "El programa no se esta ejecutando, se procede al lanzamiento..."
	cd /home/www/domains/dev.shoplatinotv_new.com/docs/shpfiles/
	./ejec.sh &
	echo "Hecho."
else
	echo "El programa se esta ejecutando. Status: $MyGrep"
fi
