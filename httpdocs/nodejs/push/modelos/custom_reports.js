//llamamos al paquete mysql que hemos instalado
var mysql = require('mysql'),
//creamos la conexion a nuestra base de datos con los datos de acceso de cada uno
connection = mysql.createConnection({ 
    user: 'root',
    password: 'HjsLIwhglOPqw1278',
    host: '172.20.27.78',
    port: '3306' });
//creamos un objeto para ir almacenando todo lo que necesitemos
var ModeloCustomReports = {};
//obtenemos la info del reporte
ModeloCustomReports.getReportInfo = function(id,callback) {
    if (connection) {
        connection.query('select name,max_rows,sql_from,sql_where,sql_order,sql_order_type,sql_group from direksys2_e11.admin_reports where id_admin_reports=' + connection.escape(id), function(error, rows) {
            if(error) {
                throw error;
            } else {
                callback(null, rows);
            }
        });
    }
}
//exportamos el objeto para tenerlo disponible en la zona de rutas
module.exports = ModeloCustomReports;