var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var file = require('fs');
var CustomReports = require('./modelos/custom_reports.js');

function Imprime_Fila (row) {
  file.appendFile('custom.csv', row+'\n\r', function (err) {
    conexion.resume();
  });
}

function Registro_Array (row) {
  var respuesta=[];
  for (var i in row) {
    //console.log(i+'::'+row[i]);
    respuesta[i] = row[i];
  }
  return respuesta;
}

function Registro_CSV (row) {
  var respuesta='';
  for (var i in row) {
    if(respuesta == '') {
      respuesta = row[i];
    } else {
      respuesta = respuesta + ',' + row[i];
    }
  }
  return respuesta;
}

app.get('/', function(req, res) {
  var url = req.url.split('?')[0];
  var pars = req.url.split('?')[1];
  if(req.url.split('?').length > 1)
    var param = req.url.split('?')[1].split('&');
  else
    var param = '';
  CustomReports.getReportInfo('11',function(error, data) {
    if (typeof data !== 'undefined') {
      console.log(data);
    } else {
      console.log("ERROR");
    }
  });
  res.sendFile('/home/www/node/push/vacio.html');
});

io.on('conexion', function(socket){
  socket.on('direksys_general', function(msg){
    var tmp = msg.split(":");
        io.emit('direksys_general', msg);
  });
});

http.listen(8003, function(){
  console.log('listening on *:8003');
});
