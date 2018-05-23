<?php
/**
 * Description of DbHandler
 *
 * @author Cesar Cedillo
 */
include_once 'config.db.php';

class DbHandler {

    private $host, $user, $password, $db;
    private $conID, $isConnected;
    private $resultSet;
    private $DEBUG_MODE;
    private $isPersistentConnection;

    public function __construct(/*$host = '', $user = '', $password = '', $db = ''*/) {
        //if (empty($host) && empty($user) && empty($password) && empty($db)) {
            global $User;
            global $Password;
            global $Server;
            global $DataBase;
            
            $host = $Server;
            $user = $User;
            $password = $Password;
            $db = $DataBase;
        //}

        $this->host = $host;
        $this->user = $user;
        $this->password = $password;
        $this->db = $db;
        $this->conID = NULL;
        $this->isConnected = FALSE;
        $this->resultSet = NULL;
        $this->isPersistentConnection = TRUE;   //--- Crea conexiones persistentes
        $this->DEBUG_MODE = TRUE;   //-- Habilita o deshabilita el modo de depuracion
    }

    /**
     * Conecta con la base de datos configurada
     * @return <boolean> TRUE: Si se conecto correctamente, FALSE: si no se establecio la conexion
     */
    public function connect() {
        $this->conID = mysqli_connect($this->host, $this->user, $this->password, $this->db);
        if($this->conID){
            $this->isConnected = true;
            return true;
        }else{
            exit("dbHandler->connect(): No se pudo conectar con la base de datos : " . mysqli_error($this->conID));
        }

    }

    /**
     * Ejecuta una consulta de tipo SELECT en la base de datos
     * @param <string> $strSQL  Cadena SQL a ejectuar
     * @return <Resultset> Resultado de la consulta ejecutada
     */
    public function selectSQLcommand($strSQL) {
        if ($this->isConnected) {
            $this->resultSet = mysqli_query($this->conID, $strSQL );
            if ($this->DEBUG_MODE) {
                if (!$this->resultSet) {
                    die("Error al ejecutar la consulta: " . $strSQL . "  | " . mysql_error());
                }
            }
            return $this->resultSet;
        }
    }

    /**
     * Ejecuta una consulta de tipo INSERT, UPDATE, DELETE en la base de datos
     * @param <type> $strSQL Cadena SQL a ejectuar
     * @return <integer> Numero de filas afectadas por la consulta
     */
    public function executeSQLcommand($strSQL) {
        if ($this->isConnected) {
            $result = mysqli_query($this->conID, $strSQL );
            if ($this->DEBUG_MODE) {
                if (!$result) {
                    die("Error al ejecutar la consulta: " . $strSQL . "  | " . mysqli_error($this->conID));
                }
            }
            return mysqli_affected_rows($this->conID);
        }
    }

    /**
     * Obtiene un Array con los resultados de la siguiente fila de una consulta SELECT
     * @return <Array>
     */
    public function fetchNextRow() {
        return mysqli_fetch_row($this->resultSet);
    }

    /**
     * Obtiene un Array Asociativo con los resultados de la siguiente fila de una consulta SELECT
     * @return <Array>  Array asociativo
     */
    public function fetchAssocNextRow() {
        return mysqli_fetch_assoc($this->resultSet);
    }

    /**
     * Regresa el Numero de Filas despues de haber ejecutado una consulta SELECT
     * @return <integer>
     */
    public function getNumRows() {
        return mysqli_num_rows($this->resultSet);
    }

    /**
     * Libera el Resultset de la ultima consulta ejecutada
     */
    public function dbFreeResult() {
        mysqli_free_result($this->resultSet);
    }

    /**
     * Comprueba si existe una conexion activa en la base de datos
     * @return <boolean> TRUE: Se encuentra la conexion activa, FALSE: se cerro la conexion
     */
    public function isConnected() {
        if ($this->conID) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * Desconecta y libera los resultados de la base de datos
     */
    public function disconnect() {
        if ($this->conID) {
            mysqli_close($this->conID);
            $this->isConnected = false;
            $this->conID = NULL;
        }
    }

    /**
     * Escapa un valor para poder ejecutarlo en la consulta SQL
     * @param <mixed> $value Valor a ser escapado
     * @return <mixed> Valor escapado
     */
    public function cleanSqlValue($value) {
        $clean_value = NULL;
        if ($this->isConnected) {
            $clean_value = mysqli_real_escape_string($this->conID, $value);
        }
        return $clean_value;
    }

    /**
     * Regresa el ID insertado de la ultima consulta.
     * @return <numeric> 
     */
    public function getInsertId() {
        return mysqli_insert_id($this->conID);
    }

    /**
     *
     * @param <type> $persistent
     */
    public function forcePersistentConnection($persistent = TRUE) {
        $this->isPersistentConnection = $persistent;
    }

}

?>