//Control Asterisk
var namiLib = require('nami')
//Control MySQL
var _mysql = require('mysql')
var MySQL = _mysql.createConnection({
   user: 'root',
   password: 'HjsLIwhglOPqw1278',
   host: '172.20.27.78',
   port: '3306',
})

//Control del servidor para uso de puertos
var app = require('express')()
var server = require('http').Server(app)
var io = require('socket.io')(server)
server.listen(8080)

var namiConfig = {
	host: '192.168.11.200',
	port: '5038',
	username: 'inovaops',
	secret: 'vghfyfi7kn'
}

var nami = new namiLib.Nami(namiConfig)

process.on('SIGINT', function () {
	nami.close()
	process.exit()
})

nami.on('namiConnectionClose', function (data) {
	//console.log('Reconnecting...')
	setTimeout(function () { nami.open() }, 5000)
})

nami.on('namiInvalidPeer', function (data) {
	//logger.fatal('Invalid AMI Salute. Not an AMI?')
	process.exit()
})
nami.on('namiLoginIncorrect', function () {
	//logger.fatal('Invalid Credentials')
	process.exit()
})

//Definición de API
nami.on('namiEvent', function (event) {
	switch(event.event) {
		case 'Bridge':
	//NOTA *** En produccion se activa el IF y se reportan al reves los datos de cliente y destino
			if("Local" == event.channel1.substr(0,5)) {
				console.log("Llamada a extension " + event.callerid2)
				io.emit(event.callerid2, {
				 	destino: event.callerid2,
				 	cliente: event.callerid1,
				})
				if(event.callerid2.length < 5) {
					MySQL.query("INSERT INTO direksys2_e2.sl_crmcalls SET origen='" + event.callerid1 + "', destino='" + event.callerid2 + "', Date=CURDATE(), Time=CURTIME();",
						function(err, resp){
							console.log("Estadistica en direksys2_e2.sl_crmcalls " + resp.insertId + "\n")
					})
				}
			}
		break
	}
})

//Muestra los canales activos
function mostrarCanales() {
	action = new namiLib.Actions.CoreShowChannels()
	nami.send(action, function (response) {
		io.emit('apiInconcert::ATC::canales', response.events)
	})
}

nami.open()

//Control de socket
io.on('connection', function (socket) {
  socket.emit('general', { mensaje: 'Conectado a la api de asterisk' })
  socket.on('acciones', function (data) {
    switch(data.accion) {
			case 'mostrar_canales':
				mostrarCanales()
			break
  	}
  })
})