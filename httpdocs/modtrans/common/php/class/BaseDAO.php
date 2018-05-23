<?php

/**
 * Description of BaseDAO
 *
 * @author L.C.I Eduardo Cesar Cedillo Jimenez
 */
class BaseDAO {

    protected $dbConn;
    protected $resultSet;
    protected $numRows;
    protected $pagerPage;
    protected $pagerLimit;
    protected $operationSuccess;
    protected $lastInsertId;
    protected $orderBy;
    protected $onlyCountRows;
    protected $groupBy;

    function __construct() {
        $this->dbConn = new DbHandler();
        $this->groupBy = "";
        $this->orderBy = "";
    }

    /**
     * Conecta con la base de datos configurada
     * @return <boolean> TRUE: Si se conecto correctamente, FALSE: si no se establecio la conexion
     */
    protected function connectDB() {
        return $this->dbConn->connect();
    }

    /**
     * Desconecta y libera los resultados de la base de datos
     */
    protected function disconnectDB() {
        $this->dbConn->disconnect();
    }

    protected function executeSQLcommand($cadena_sql) {
        return $this->dbConn->executeSQLcommand($cadena_sql);
    }

    protected function selectSQLcommand($cadena_sql) {
        $this->resultSet = $this->dbConn->selectSQLcommand($cadena_sql);
        $this->numRows = $this->dbConn->getNumRows();
        return $this->resultSet;
    }

    protected function dbFreeResult() {
        $this->dbConn->dbFreeResult();
    }

    /**
     * Obtiene un Array con los resultados de la siguiente fila de una consulta SELECT
     * @return <Array>
     */
    protected function fetchNextRow() {
        return $this->dbConn->fetchNextRow();
    }

    /**
     * Obtiene un Array Asociativo con los resultados de la siguiente fila de una consulta SELECT
     * @return <Array>  Array asociativo
     */
    protected function fetchAssocNextRow() {
        return $this->dbConn->fetchAssocNextRow();
    }

    /**
     * Regresa el ID insertado de la ultima consulta.
     * @return <numeric>
     */
    protected function getInsertId() {
        return $this->dbConn->getInsertId();
    }

    /**
     * Obtiene el numero de filas afectadas por la consulta SQL
     * @return <numeric>
     */
    public function getNumRows() {
        return $this->numRows;
    }

    /**
     * Cambia el numero de la pagina para el paginador de consultae
     * @param <integer> $pagerPage
     */
    public function setPagerStart($pagerPage) {
        $this->pagerPage = $pagerPage;
    }

    /**
     * Cambia el numero de Resultados por pagina para la consulta
     * @param <integer> $pagerLimit
     */
    public function setPagerPerPage($pagerLimit) {
        $this->pagerLimit = $pagerLimit;
    }

    protected function cleanSqlValue($value, $useSingleQuote = true) {
        if (is_null($value)) {
            return "NULL";
        } else if (is_string($value)) {
            if ($useSingleQuote) {                
                return "'" . $this->dbConn->cleanSqlValue($value) . "'";
            } else {
                return $this->dbConn->cleanSqlValue($value);
            }
        } else {
            return $this->dbConn->cleanSqlValue($value);
        }
    }

    /**
     * Obtiene el ultimo ID del registro insertado
     * @return <integer>
     */
    public function getLastInsertId() {
        return $this->lastInsertId;
    }

    /**
     * Agrega la clausula OrderBy para la consulta
     * @param <string> $orderby
     */
    public function setOrderBy($orderby = '') {
        $this->orderBy = $orderby;
    }

    /**
     * Indica si unicamente se cuentan los resultados de la consulta
     * @param <boolean> $bool
     */
    public function onlyCountRows($bool = TRUE) {
        $this->onlyCountRows = $bool;
    }

    /**
     * Agrega la clausula GROUP BY para la consulta
     * @param <string> $orderby
     */
    public function setGroupBy($groupBy) {
        $this->groupBy = $groupBy;
    }

}

?>