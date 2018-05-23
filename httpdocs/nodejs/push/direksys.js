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
          var mysql = require('mysql');
          var conexion = mysql.createConnection({
            user: 'root',
            password: 'D01NksjIw283hsl',
            host: '172.16.1.55',
            port: '3306',
          });
        //Obtener datos de TMK
          var html_e2 = '';
          var count = 0;
          conexion.query('USE direksys2_e2;');
      		conexion.query("SELECT cus.ID_customers, cus.FirstName, cus.LastName1, cus.LastName2, cus.Phone1, cus.Phone2, cus.Cellphone, ord.ID_orders, date_format(ord.Date,'%d/%m%Y') Date, ord.Status " +
            "FROM sl_customers cus " +
            "INNER JOIN sl_orders ord using(ID_customers) "+
            "WHERE cus.CID='"+cliente[1]+"' AND cus.Status='Active' OR cus.Phone1='"+cliente[1]+"' OR cus.Phone2='"+cliente[1]+"' OR cus.Cellphone='"+cliente[1]+"' "+
            "ORDER BY ord.Date DESC LIMIT 3;", function(error, customers){
              if(!error){
                if(customers.length > 0){
                  var customer;
                  html_e2 = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><h3>Estos clientes han llamado desde ese numero</h3><table width=\"100%\" border=\"0\" cellpadding=\"4\"><tr style=\"background-color:silver;\"><th>NOMBRE</th><th>APELLIDOS</th><th>ORDEN</th><th>FECHA</th><th>STATUS</th></tr>\n";
                  customers.forEach(function(customer){
                    if(customer.FirstName != null) {
                      if(customer.Status == 'Cancelled') {
                        var color = "<span style=\"color:red;\">"+customer.Status+"</span>";
                      }
                      if(customer.Status == 'Processed') {
                        var color = "<span style=\"color:blue;\">"+customer.Status+"</span>";
                      }
                      if(customer.Status == 'Shipped') {
                        var color = "<span style=\"color:green;\"><strong>"+customer.Status+"</strong></span>";
                      }
                      html_e2 = html_e2 + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+customer.ID_orders+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">\n";
                      html_e2 = html_e2 + "<td>"+customer.FirstName+"</td><td>"+customer.LastName1+" "+customer.LastName2+"</td><td>"+customer.ID_orders+"</td><td>"+customer.Date+"</td><td>"+color+"</td></tr>\n";
                      count++;
                    }
                  });
                  html_e2 = html_e2 + "</table></center>\n";
                }
              }
              if(count == 0) {
                html_e2 = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><br/></center>";
                html_e2 = html_e2 + "<center><br /><input type=\"button\" value=\"Tomar llamada\" class=\"button\" onclick=\";window.location.href=this.getAttribute('href');return false;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"\" />\n</center>\n";
              } else {
                html_e2 = html_e2 + "<center><br /><input type=\"button\" value=\"Orden no listada\" class=\"button\" onclick=\";window.location.href=this.getAttribute('href');return false;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"\" />\n</center>\n";
              }
              io.emit('atc_cia2',extension[1] + '|' + html_e2);
            });
        //Obtener datos de MOW
          var html_e4 = '';
          conexion.query('USE direksys2_e4;');
          conexion.query("SELECT cus.ID_customers, cus.FirstName, cus.LastName1, cus.LastName2, cus.Phone1, cus.Phone2, cus.Cellphone, ord.ID_orders, date_format(ord.Date,'%d/%m%Y') Date " +
            "FROM sl_customers cus " +
            "INNER JOIN sl_orders ord using(ID_customers) "+
            "WHERE cus.CID='"+cliente[1]+"' AND cus.Status='Active' OR cus.Phone1='"+cliente[1]+"' OR cus.Phone2='"+cliente[1]+"' OR cus.Cellphone='"+cliente[1]+"' "+
            "ORDER BY ord.Date DESC LIMIT 3;", function(error, customers){
              if(!error){
                if(customers.length > 0){
                  var customer;
                  html_e4 = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><h3>Estos clientes han llamado desde ese numero</h3><table width=\"100%\" border=\"0\" cellpadding=\"4\"><tr style=\"background-color:silver;\"><th>NOMBRE</th><th>APELLIDOS</th><th>ORDEN</th><th>FECHA</th><th>STATUS</th></tr>\n";
                  customers.forEach(function(customer){
                    if(customer.FirstName != null) {
                      if(customer.Status == 'Cancelled') {
                        var color = "<span style=\"color:red;\">"+customer.Status+"</span>";
                      }
                      if(customer.Status == 'Processed') {
                        var color = "<span style=\"color:blue;\">"+customer.Status+"</span>";
                      }
                      if(customer.Status == 'Shipped') {
                        var color = "<span style=\"color:green;\"><strong>"+customer.Status+"</strong></span>";
                      }
                      html_e4 = html_e4 + "<tr style=\"background-color:#e3e8e8;cursor:pointer;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"&amp;id_ref="+customer.ID_orders+"\" onclick=\";window.location.href=this.getAttribute('href');return false;\">\n";
                      html_e4 = html_e4 + "<td>"+customer.FirstName+"</td><td>"+customer.LastName1+" "+customer.LastName2+"</td><td>"+customer.ID_orders+"</td><td>"+customer.Date+"</td><td>"+color+"</td></tr>\n";
                      count++;
                    }
                  });
                  html_e4 = html_e4 + "</table></center>\n";
                }
              }
              if(count == 0) {
                html_e4 = "<center><h1>Tienes una nueva llamada de " + cliente[1] + "</h1><br/></center>";
                html_e4 = html_e4 + "<center><br /><input type=\"button\" value=\"Tomar llamada\" class=\"button\" onclick=\";window.location.href=this.getAttribute('href');return false;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"\" />\n</center>\n";
              } else {
                html_e4 = html_e4 + "<center><br /><input type=\"button\" value=\"Orden no listada\" class=\"button\" onclick=\";window.location.href=this.getAttribute('href');return false;\" href=\"dbman?cmd=opr_crmtickets&amp;add=1&amp;caller_id="+cliente[1]+"\" />\n</center>\n";
              }
              io.emit('atc_cia4',extension[1] + '|' + html_e4);
            });
          res.sendFile('/home/www/node/push/vacio.html');
        }else{
                res.sendFile('/home/www/node/push/index.html');
        }
});

io.on('connection', function(socket){
  socket.on('crm', function(msg){
    var tmp = msg.split(":");
        io.emit('crm', msg);
  });
  socket.on('sales', function(msg){
    var tmp = msg.split(":");
        io.emit('sales', msg);
  });
  socket.on('admin', function(msg){
    var tmp = msg.split(":");
        io.emit('admin', msg);
  });
  socket.on('wms', function(msg){
    var tmp = msg.split(":");
        io.emit('wms', msg);
  });
  socket.on('user', function(msg){
    var tmp = msg.split(":");
        io.emit('user', msg);
  });
});

http.listen(8002, function(){
  console.log('listening on *:8002');
});
