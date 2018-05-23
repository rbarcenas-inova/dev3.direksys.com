var mysql = require('mysql');

var dbConfig = {
   user: 'root',
   password: 'HjsLIwhglOPqw1278',
   host: '172.20.27.78',
   port: '3306',
};

//Ejecuta una consulta
var exec = function(Query,Data,callback) {
   var connection = mysql.createConnection(dbConfig);
   connection.connect(function(err) {
      if (err) throw err;
   });
   
   connection.query(Query,Data,function(err, res) {
         if (err) throw err;
         if (callback){
            callback(res);
         }
      }
   );
   connection.end();
}

// module
var DB = function(config){
   config = config || {};
}

DB.prototype.query = function(query,callback) {
   var Data  = null;
   exec(query,Data,function(res) {
      callback(res);
   });
}

DB.prototype.saveSingleData = function(data) {
   var Query = queries.SQLSAVESINGLEDATA;
   var Data  = data;
   exec(Query,Data);
}

module.exports = DB;