#!/bin/bash

NOW="$(date +"%d-%m-%Y")"

scp direksysmx@172.20.27.77:/home/www/domains/upload/cgi-bin.tar.gz ./

tar -zxf cgi-bin.tar.gz


chown -R www-data:www-data /home/direksysmx/cgi-bin/

chmod 755 /home/direksysmx/cgi-bin/common/apps/earcalls

chmod 755 /home/direksysmx/cgi-bin/mod/admin/admin
chmod 755 /home/direksysmx/cgi-bin/mod/admin/dbman
chmod 755 /home/direksysmx/cgi-bin/mod/sales/admin
chmod 755 /home/direksysmx/cgi-bin/mod/sales/dbman
chmod 755 /home/direksysmx/cgi-bin/mod/wms/admin
chmod 755 /home/direksysmx/cgi-bin/mod/wms/dbman
chmod 755 /home/direksysmx/cgi-bin/mod/crm/admin
chmod 755 /home/direksysmx/cgi-bin/mod/crm/dbman
chmod 755 /home/direksysmx/cgi-bin/mod/setup/admin
chmod 755 /home/direksysmx/cgi-bin/mod/setup/dbman
chmod 755 /home/direksysmx/cgi-bin/mod/ecom/admin
chmod 755 /home/direksysmx/cgi-bin/mod/ecom/dbman
chmod 755 /home/direksysmx/cgi-bin/mod/rep/admin
chmod 755 /home/direksysmx/cgi-bin/mod/rep/dbman

chmod 755 /home/direksysmx/cgi-bin/common/apps/ajaxbuild
chmod 755 /home/direksysmx/cgi-bin/common/apps/ajaxfinance
chmod 755 /home/direksysmx/cgi-bin/common/apps/ajaxorder
chmod 755 /home/direksysmx/cgi-bin/common/apps/ajaxpayment
chmod 755 /home/direksysmx/cgi-bin/common/apps/barcode
chmod 755 /home/direksysmx/cgi-bin/common/apps/certegy
chmod 755 /home/direksysmx/cgi-bin/common/apps/cybersource
chmod 755 /home/direksysmx/cgi-bin/common/apps/pauth
chmod 755 /home/direksysmx/cgi-bin/common/apps/img
chmod 755 /home/direksysmx/cgi-bin/common/apps/schid
chmod 755 /home/direksysmx/cgi-bin/common/apps/showimages
chmod 755 /home/direksysmx/cgi-bin/common/apps/upfile

##  Traspaso de General
rm -rf /home/direksysmx/cgi-bin/common/general*
cp -rf /home/www/domains/direksys.com/cgi-bin/common/general.e* /home/direksysmx/cgi-bin/common/


##  Manejo sesiones Files  (no deberian haber)
cp -rf /home/www/domains/direksys.com/cgi-bin/sessions /home/direksysmx/cgi-bin/sessions
chmod -R 777 /home/direksysmx/cgi-bin/sessions


## Instalacion
mv /home/www/domains/direksys.com/cgi-bin /home/direksysmx/cgi-bin_$NOW
mv /home/direksysmx/cgi-bin /home/www/domains/direksys.com/cgi-bin

tar zcf cgi-bin_$NOW.tar.gz /home/direksysmx/cgi-bin_$NOW
rm -rf /home/direksysmx/cgi-bin_$NOW

