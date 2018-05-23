//Control Asterisk
var namiLib = require('nami')

//Control del servidor para uso de puertos
var app = require('express')()
var server = require('http').Server(app)
var io = require('socket.io')(server)
server.listen(8081)

var namiConfig = {
	host: '172.20.27.58',
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
		case 'Newstate':
			io.emit('general', {evento: 'NUEVA', 
				datos: {
					cid: event.calleridnum,
					canal: event.channel,
					cidname: event.calleridname,
					uid: event.uniqueid
				}
			})
		break
		case 'Hangup':
			io.emit('general', {evento: 'TERMINANDO',
				datos: {
					uid: event.uniqueid,
					cid: event.calleridnum,
					clienum: event.connectedlinenum
				}
			})
		break
		case 'Newchannel':
			//console.log('CANAL',event)
		break
		case 'Bridge':
			io.emit('general', {evento: 'ENLAZANDO',
				datos: {
					cid1: event.callerid1,
					uid1: event.uniqueid1,
					cid2: event.callerid2,
					uid2: event.uniqueid2
				}
			})
		break
		case 'NewAccountCode':
			//console.log(event.event,event)
		break
		case 'Dial':
			switch(event.subevent) {
				case 'Begin':
					io.emit('general', {evento: 'LLAMANDO',
						datos: {
							cid: event.calleridnum,
							ext: event.dialstring,
						}
					})
				break
				default:
					console.log(event.event,event.subevent)
				break
			}
		break
		case 'ExtensionStatus':
		case 'VarSet':
		case 'Newexten':
		case 'HangupRequest':
		case 'SoftHangupRequest':
		case 'RTCPSent':
		case 'RTCPReceived':
		case 'AgentCalled':
		break
		default:
			console.log('Got Event: ' + event.event)
	}
})

//Muestra los canales activos
function mostrarCanales() {
	action = new namiLib.Actions.CoreShowChannels()
	nami.send(action, function (response) {
	//console.log(response.events)
	//if(response.events.length > 1)
		io.emit('canales', response.events)
	})
}

//Hace una llamada
function llamada(destino, extension, cola) {
//Parametros no pasados
	canal = 'SIP/bMCM/' + destino
	extension = extension || 801
	cola = cola || 'ext-queues'

	action = new namiLib.Actions.Originate()
	action.Channel = canal
	action.Exten = extension
	action.Priority = 1
	action.Context = cola
	//action.Timeout = 10000
	nami.send(action, function (response) {
		console.log(' ---- LLAMADA:',response.message)
	})
}

//Enlaza dos llamadas
function enlazar(canal1, canal2) {
//Parametros no pasados
	action = new namiLib.Actions.Bridge()
	action.Channel1 = canal1
	action.Channel2 = canal2
	action.Tone = 'no'
	nami.send(action, function (response) {
		console.log(' ---- ENLAZANDO LLAMADA:',response.message)
	})
}

nami.open()

//Control de socket
io.on('connection', function (socket) {
  socket.emit('general', { mensaje: 'Conectado a la api de asterisk' })
  socket.on('acciones', function (data) {
    //console.log(data)
    switch(data.accion) {
    	case 'llamada_salida':
    		llamada(data.datos.destino, data.datos.origen)
			break
			case 'mostrar_canales':
				mostrarCanales()
			break
			case 'enlazar':
				enlazar(data.datos.canal1, data.datos.canal2)
			break
  	}
  })
})