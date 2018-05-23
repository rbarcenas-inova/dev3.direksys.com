#############################################################################
#############################################################################
#   Function: add_usrman
#
#       Es: Se ejecuta despues de agregar un nuevo usuario y lo asigna a los grupos 1 y 2
#-
#       En: 
#
#
#    Created on: 06/02/2013
#
#    Author: Alejandro Diaz
#
#    Modifications:
#
#        - 
#
#   Parameters:
#      - 
#
#   Returns:
#      - 
#
#   See Also:
#
#
sub add_usrman {

	&Do_SQL("INSERT INTO admin_users_groups (`ID_admin_users`,  `ID_admin_groups`) VALUES($in{'id_admin_users'}, 1); ");
	&Do_SQL("INSERT INTO admin_users_groups (`ID_admin_users`,  `ID_admin_groups`) VALUES($in{'id_admin_users'}, 2); ");
}

1;