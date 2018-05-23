var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
app.get('/', function(req, res){
        var url = req.url.split('?')[0];
        var pars = req.url.split('?')[1];
        if(req.url.split('?').length > 1)
                var param = req.url.split('?')[1].split('&');
        else
                var param = '';
        if(param.length > 0){
          var extension = param[0].split('=');
          var cliente = param[1].split('=');
          var origen = param[2].split('=');
          if(cliente[1] != 'CONTACTADDRESS' && cliente[1] != 'CALLERID') {
            var fecha = new Date();
            console.log('[RECIBIDA]::' + cliente[1] + '::' + extension[1] + '::' + fecha.toString());
            var mysql = require('mysql');
            try {
              var conexion = mysql.createConnection({
                user: 'root',
                password: 'HjsLIwhglOPqw1278',
                host: '172.20.27.78',
                port: '3306',
              });
              var html = '';
              conexion.query('USE direksys2_e2;');
          		conexion.query("SELECT cus.ID_customers, cus.FirstName, cus.LastName1, cus.LastName2, cus.Phone1, cus.Phone2, cus.Cellphone, date_format(ord.Date,'%d/%m%Y') Date " +
                "FROM sl_customers cus " +
                "INNER JOIN sl_orders ord using(ID_customers) "+
                "WHERE cus.Status='Active' AND (cus.CID='"+cliente[1]+"' OR cus.Phone1='"+cliente[1]+"' OR cus.Phone2='"+cliente[1]+"' OR cus.Cellphone='"+cliente[1]+"') "+
                "ORDER BY cus.Date DESC LIMIT 5;", function(error, customers){
                  if(error){
                  //No es un cliente registrado
                    var clientes = -1;
                    html = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><br/>" +
                      "<input type=\"button\" href=\"/cgi-bin/mod/sales/admin?cmd=console_order&step=2&id_customers=0&cid="+cliente[1]+"&did="+origen[1]+"\" " +
                      "onclick=\";window.location.href=this.getAttribute('href');return false;\" value=\"Tomar Llamada\" class=\"button\"></center>";
                  }else{
                    if(customers.length > 0){
                      var customer;
                      html = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><h3>Estos clientes han llamado desde ese numero</h3><table width=\"100%\" border=\"0\" cellpadding=\"4\"><tr style=\"background-color:silver;\"><th>NOMBRE</th><th>APELLIDOS</th><th>TELEFONO</th><th>FECHA DE ULTIMA COMPRA</th></tr>\n";
                      customers.forEach(function(customer){
                        //if(customer.FirstName != null) {
                          html = html + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\" href=\"?cmd=console_order&amp;step=2&amp;id_customers="+customer.ID_customers+"&cid="+cliente[1]+"&did="+origen[1]+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">\n";
                          html = html + "<td>"+customer.FirstName+"</td><td>"+customer.LastName1+" "+customer.LastName2+"</td><td>"+cliente[1]+"</td><td>"+customer.Date+"</td></tr>\n";
                        //}
                      });
                      html = html + "</table>\n";
                      var clientes = customers.length;
                    }else{
                      html = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><br/>" +
                      "<input type=\"button\" href=\"/cgi-bin/mod/sales/admin?cmd=console_newcall&amp;id_origins=1\" " +
                      "onclick=\";window.location.href=this.getAttribute('href');return false;\" value=\"Tomar Llamada\" class=\"button\"></center>";
                      var clientes = 0;
                    }
                  }
                  html = html + "<br /><br /><input type=\"button\" href=\"/cgi-bin/mod/sales/admin?cmd=console_order&step=2&id_customers=0&cid="+cliente[1]+"&did="+origen[1]+"\" " +
                      "onclick=\";window.location.href=this.getAttribute('href');return false;\" value=\"Nuevo cliente\" class=\"button\"></center>\n";
                  var fecha = new Date();
                  console.log('[RESUELTA]::' + cliente[1] + '::' + extension[1] + '::'  + clientes + ' clientes de ese numero en BD :: ' + fecha.toString());
                  io.emit('generico',extension[1] + '|' + html);
                });
              res.sendFile('/home/www/node/push/vacio.html');
            } catch (err) {
                console.log(err);
            }
          }
          else {
            var fecha = new Date();
                console.log('[Descartado] Reenvio de llamada :: ' + fecha.toString());
            res.sendFile('/home/www/node/push/vacio.html');
          }
        }else{
          res.sendFile('/home/www/node/push/index.html');
        }
});

io.on('connection', function(socket){
  socket.on('generico', function(msg){
    io.emit('generico', msg);
  });
});

http.listen(8000, function(){
  console.log('listening on *:8000');
});
