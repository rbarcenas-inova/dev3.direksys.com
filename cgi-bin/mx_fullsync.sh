#!/bin/bash

scp direksysmx@172.20.27.77:/home/www/domains/upload/dev2.direksys.com.tar.gz ./

tar -zxf dev2.direksys.com.tar.gz

rm -rf dev2.direksys.com/.dropbox 
rm -rf dev2.direksys.com/.git 
rm -rf dev2.direksys.com/.gitignore 

chown -R www-data:www-data /home/direksysmx/dev2.direksys.com/

chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/earcalls

chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/admin/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/admin/dbman
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/sales/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/sales/dbman
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/wms/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/wms/dbman
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/crm/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/crm/dbman
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/setup/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/setup/dbman
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/ecom/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/ecom/dbman
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/rep/admin
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/mod/rep/dbman

chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/ajaxbuild
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/ajaxfinance
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/ajaxorder
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/ajaxpayment
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/barcode
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/certegy
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/cybersource
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/pauth
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/img
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/schid
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/showimages
chmod 755 /home/direksysmx/dev2.direksys.com/cgi-bin/common/apps/upfile

##  Traspaso de General
rm -rf /home/direksysmx/dev2.direksys.com/cgi-bin/common/general*
cp -rf /home/www/domains/direksys.com/cgi-bin/common/general.e* /home/direksysmx/dev2.direksys.com/cgi-bin/common/


##  Manejo sesiones Files  (no deberian haber)
cp -rf /home/www/domains/direksys.com/cgi-bin/sessions /home/direksysmx/dev2.direksys.com/cgi-bin/sessions
chmod -R 777 /home/direksysmx/dev2.direksys.com/cgi-bin/sessions


## Instalacion
mv /home/www/domains/direksys.com /home/direksysmx/direksys.com_bak
mv /home/direksysmx/dev2.direksys.com /home/www/domains/direksys.com
mkdir /home/www/domains/direksys.com/logs/

