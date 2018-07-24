#!/bin/bash

NOW="$(date +"%d-%m-%Y")"

tar -zxf cgi-bin.tar.gz

chown -R direksysmxftp:www-data /home/www/domains/upload/cgi-bin/

chmod 755 /home/www/domains/upload/cgi-bin/common/apps/earcalls

chmod 755 /home/www/domains/upload/cgi-bin/mod/admin/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/admin/dbman
chmod 755 /home/www/domains/upload/cgi-bin/mod/sales/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/sales/dbman
chmod 755 /home/www/domains/upload/cgi-bin/mod/wms/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/wms/dbman
chmod 755 /home/www/domains/upload/cgi-bin/mod/crm/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/crm/dbman
chmod 755 /home/www/domains/upload/cgi-bin/mod/setup/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/setup/dbman
chmod 755 /home/www/domains/upload/cgi-bin/mod/ecom/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/ecom/dbman
chmod 755 /home/www/domains/upload/cgi-bin/mod/rep/admin
chmod 755 /home/www/domains/upload/cgi-bin/mod/rep/dbman

chmod 755 /home/www/domains/upload/cgi-bin/common/apps/ajaxbuild
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/ajaxfinance
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/ajaxorder
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/ajaxpayment
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/barcode
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/certegy
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/cybersource
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/pauth
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/img
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/schid
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/showimages
chmod 755 /home/www/domains/upload/cgi-bin/common/apps/upfile

##  Traspaso de General
rm -rf /home/www/domains/upload/cgi-bin/common/general*.cfg
cp -rf /home/www/domains/upload/cgi-bin/common/general_mxD04/general.e* /home/www/domains/upload/cgi-bin/common/
#cp -rf /home/www/domains/direksys.com/cgi-bin/common/general.e* /home/www/domains/upload/cgi-bin/common/
rm -rf /home/www/domains/upload/cgi-bin/common/general_*


##  Manejo sesiones Files  (no deberian haber)
cp -rf /home/www/domains/direksys.com/cgi-bin/sessions /home/www/domains/upload/cgi-bin/sessions
chmod -R 777 /home/www/domains/upload/cgi-bin/sessions/


## Instalacion
mv /home/www/domains/direksys.com/cgi-bin/ /home/www/domains/upload/cgi-bin_$NOW
mv /home/www/domains/upload/cgi-bin/ /home/www/domains/direksys.com/cgi-bin

tar zcf cgi-bin_$NOW.tar.gz /home/www/domains/upload/cgi-bin_$NOW
rm -rf /home/www/domains/upload/cgi-bin_$NOW




