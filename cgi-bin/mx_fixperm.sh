#!/bin/bash




chown -R direksysmxftp:www-data /home/www/domains/direksys.com/

chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/earcalls

chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/admin/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/admin/dbman
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/sales/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/sales/dbman
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/wms/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/wms/dbman
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/crm/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/crm/dbman
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/setup/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/setup/dbman
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/ecom/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/ecom/dbman
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/rep/admin
chmod 755 /home/www/domains/direksys.com/cgi-bin/mod/rep/dbman

chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/ajaxbuild
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/ajaxfinance
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/ajaxorder
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/ajaxpayment
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/barcode
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/certegy
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/cybersource
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/pauth
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/img
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/schid
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/showimages
chmod 755 /home/www/domains/direksys.com/cgi-bin/common/apps/upfile

##  Manejo sesiones Files  (no deberian haber)
chmod -R 777 /home/www/domains/direksys.com/cgi-bin/sessions

