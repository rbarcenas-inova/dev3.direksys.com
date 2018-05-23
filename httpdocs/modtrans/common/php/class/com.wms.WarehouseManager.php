<?php

require_once 'db/DbHandler.php';
require_once 'dto.catalog.WarehousesDTO.php';
require_once 'dao.catalog.WarehousesDAO.php';
require_once 'dto.catalog.WarehousesLocationDTO.php';
require_once 'dao.catalog.WarehousesLocationDAO.php';
require_once 'dto.catalog.AdminLogsDTO.php';
require_once 'dao.catalog.AdminLogsDAO.php';

//-- se debe incluir la funcion previa para la carga de los costs

/**
 * Description
 *
 * @author L.C.I Cesar Cedillo
 */
class WarehouseManager {

    private $from_wh, $to_wh, $id_products, $qty;
    private $iD_admin_users;
    private $arr_process_status;
    private $arr_errors;

    function __construct() {

        $this->from_wh = "";
        $this->to_wh = "";
        $this->id_products = 0;
        $this->qty;
        $this->arr_process_status = array(); // $success =>   ; $msg =>
        $this->arr_errors = array();
    }

    public function getID_admin_users() {
        return $this->iD_admin_users;
    }

    public function setID_admin_users($iD_admin_users) {
        $this->iD_admin_users = $iD_admin_users;
    }

    public function transfer_warehouse($from_wh, $to_wh, $id_products, $qty, $id_orders = 0) {
        //if (!empty($this->arr_process_status))
        //    unset($this->arr_process_status);

        //if (!empty($this->arr_errors))
        //    unset($this->arr_errors);


        $this->from_wh = $from_wh;
        $this->to_wh = $to_wh;
        $this->id_products = $id_products;
        $this->qty = $qty;

        $this->deleteWarehousesLocation($from_wh, $to_wh, $id_products);
        $this->deleteSkusCost($from_wh, $to_wh, $id_products);
        $this->insert_temporary_wh_data($from_wh, $to_wh, $id_products, $qty);
        $this->processTransferWH($from_wh, $to_wh, $id_products, $qty, $id_orders);
        $this->processTransferWHSkusCost($from_wh, $to_wh, $id_products, $qty, $id_orders);

        return $this->processErrors();
    }

    private function insert_temporary_wh_data($from_wh, $to_wh, $id_products, $qty) {
        //-- id_product debe ser de 400000+id_part

        $sth = new DbHandler();

        $whLocationDAO = new WarehousesLocationDAO();
        $whLocationDTO = new WarehousesLocationDTO();
        //-- insertar los datos necesarios para el wh origen (virtual)
        $whLocationDTO->setIdWarehouses($from_wh);
        $whLocationDTO->setIdProducts($id_products);
        $whLocationDTO->setLocation('aa99zz');
        $whLocationDTO->setQuantity($qty);
        $whLocationDTO->setID_admin_users($this->iD_admin_users);
        $whLocationDAO->insertRecord($whLocationDTO);

        $sth->connect();
        $cost = load_sltvcost($id_products);
        $sth->executeSQLcommand("INSERT INTO sl_skus_cost SET ID_products=$id_products,ID_purchaseorders=0,ID_warehouses=$from_wh,Tblname='sl_returns', Quantity='$qty', Cost='$cost', Date=CURDATE(), Time=CURTIME(), ID_admin_users=" . $this->iD_admin_users . ";");
        $sth->disconnect();
    }

    private function deleteWarehousesLocation($from_wh, $to_wh, $id_products) {
        $exito = FALSE;

        $sth = new DbHandler();

        if ($sth->connect()) {
            $cadena_sql = "DELETE FROM sl_warehouses_location WHERE ID_products=" . $sth->cleanSqlValue($id_products) . " AND ID_warehouses = " . $sth->cleanSqlValue($from_wh) . " AND Quantity <= 0;";
            if ($sth->executeSQLcommand($cadena_sql) > -1) {
                $exito = TRUE;
            }

            $cadena_sql = "DELETE FROM sl_warehouses_location WHERE  ID_products=" . $sth->cleanSqlValue($id_products) . " AND ID_warehouses = " . $sth->cleanSqlValue($to_wh) . " AND Quantity <= 0;";
            if ($sth->executeSQLcommand($cadena_sql) > -1) {
                $exito = TRUE;
            } else {
                $exito = FALSE;
            }
        }
        $sth->disconnect();

        return $exito;
    }

    private function deleteSkusCost($from_wh, $to_wh, $id_products) {
        $exito = FALSE;

        $sth = new DbHandler();
        if ($sth->connect()) {
            $cadena_sql = "DELETE FROM sl_skus_cost WHERE 1 AND  ID_products=" . $sth->cleanSqlValue($id_products) . "  AND ID_warehouses = " . $sth->cleanSqlValue($from_wh) . " AND Quantity <= 0;";
            if ($sth->executeSQLcommand($cadena_sql) > -1) {
                $exito = TRUE;
            }

            $cadena_sql = "DELETE FROM sl_skus_cost WHERE 1 AND  ID_products=" . $sth->cleanSqlValue($id_products) . "  AND ID_warehouses = " . $sth->cleanSqlValue($to_wh) . " AND Quantity <= 0;";
            if ($sth->executeSQLcommand($cadena_sql) > -1) {
                $exito = TRUE;
            } else {
                $exito = FALSE;
            }
        }
        $sth->disconnect();

        return $exito;
    }

    private function processTransferWH($from_wh, $to_wh, $id_products, $qty, $id_orders) {
        //  $from_wh : chofer
        //  $to_wh : almacen fisico

        $sth = new DbHandler();
        $sth2 = new DbHandler();
        $sth3 = new DbHandler();

        if ($sth->connect()) {
            $cadena_sql = "SELECT sum(Quantity) as Quantity,sum(if(Isset='Y',1,0)) as SumY 
                FROM sl_warehouses_location 
                inner join sl_skus on(sl_warehouses_location.ID_products=sl_skus.ID_sku_products)
                WHERE sl_warehouses_location.ID_products=" . $sth->cleanSqlValue($id_products) . " 
                AND ID_warehouses = " . $sth->cleanSqlValue($from_wh) . "
                ORDER BY sl_warehouses_location.Date ASC;";

            $sth->selectSQLcommand($cadena_sql);

            if ($result = $sth->fetchAssocNextRow()) {

                $amountavail = $result['Quantity'];
                $sumy = $result['SumY'];

                if (($qty <= $amountavail) && $sumy == 0) {

                    $sth2->connect();
                    $qtytoadjust = $qty;

                    $cadena_sql = "SELECT *
                        FROM sl_warehouses_location 
                        WHERE ID_products=" . $sth2->cleanSqlValue($id_products) . "
                        AND ID_warehouses = " . $sth2->cleanSqlValue($from_wh) . "
                        AND Quantity > 0 
                        ORDER BY Date ASC;";

                    $sth2->selectSQLcommand($cadena_sql);
                    while (($result2 = $sth2->fetchAssocNextRow()) && $qtytoadjust > 0) {

                        if ($qtytoadjust < $result2['Quantity']) {
                            //- Se ajusta fila en Wareouse FROM
                            $sth3->connect();
                            $cadena_sql = "UPDATE sl_warehouses_location SET Quantity = Quantity - " . $qtytoadjust . " WHERE ID_warehouses_location = " . $sth3->cleanSqlValue($result2['ID_warehouses_location']) . " AND ID_warehouses = '" . $sth3->cleanSqlValue($from_wh) . "';";

                            if ($sth3->executeSQLcommand($cadena_sql) < 1) {
                                $this->arr_errors[] = array(
                                    "success" => FALSE,
                                    "msg" => " Error al actualizar el registro sl_warehouses_location  Quantity = Quantity - " . $qtytoadjust . " " . $result2['ID_warehouses_location']
                                );
                            }
                            $qtytoadjust = 0;

                            $sth3->disconnect();
                        } else {
                            //- Se elimina la fila en Wareouse FROM
                            $sth3->connect();
                            $cadena_sql = "DELETE FROM sl_warehouses_location WHERE ID_warehouses_location = " . $sth3->cleanSqlValue($result2['ID_warehouses_location']) . " AND ID_warehouses = '" . $sth3->cleanSqlValue($from_wh) . "';";

                            if ($sth3->executeSQLcommand($cadena_sql) < 0) {
                                $this->arr_errors[] = array(
                                    "success" => FALSE,
                                    "msg" => " Error al eliminar el registro sl_warehouses_location  ID_warehouses_location: " . $result2['ID_warehouses_location']
                                );
                            }
                            $qtytoadjust -= $result2['Quantity'];

                            $sth3->disconnect();
                        }
                    }
                    $sth2->dbFreeResult();

                    if ($qtytoadjust > 0) {
                        $this->arr_process_status[] = array(
                            "success" => false,
                            "msg" => "Error, processTransferWH, Quantity to adjust $qtytoadjust > 0"
                        );
                    }

                    #Se ajusta/inserta fila en Warehouse To
                    $sth2->connect();
                    $cadena_sql = "SELECT COUNT(*) as cnt FROM sl_warehouses_location WHERE ID_warehouses = '" . $sth2->cleanSqlValue($from_wh) . "' AND ID_products=" . $sth2->cleanSqlValue($id_products) . " AND Quantity > 0;";
                    $sth2->selectSQLcommand($cadena_sql);


                    if ($result3 = $sth2->fetchAssocNextRow()) {

                        if ($result3['cnt'] > 0) {
                            $sth3->connect();
                            $cadena_sql = "UPDATE sl_warehouses_location SET Quantity = Quantity + " . $sth3->cleanSqlValue($qty) . " WHERE ID_warehouses = " . $sth3->cleanSqlValue($to_wh) . "  AND ID_products= " . $sth3->cleanSqlValue($id_products) . "  AND Quantity > 0 ORDER BY Date ASC LIMIT 1;";
                            if ($sth3->executeSQLcommand($cadena_sql) < 1) {
                                $this->arr_errors[] = array(
                                    "success" => FALSE,
                                    "msg" => " Error al actualizar el registro sl_warehouses_location  Quantity = Quantity + " . $qty . ";  ID_warehouses: " . $to_wh
                                );
                            }

                            $sth3->disconnect();
                        } else {
                            //-- inserta el registro en el warehouse destino en caso de que no exista registro previo con ese ID de warehouse y producto.
                            $sth3->connect();
                            $cadena_sql = "INSERT INTO sl_warehouses_location SET ID_products='" . $sth3->cleanSqlValue($id_products) . "', ID_warehouses='" . $sth3->cleanSqlValue($to_wh) . "',Location='aa99zz', Quantity='" . $sth3->cleanSqlValue($qty) . "', Date=CURDATE(), Time=CURTIME(), ID_admin_users=" . $this->iD_admin_users . ";";

                            if ($sth3->executeSQLcommand($cadena_sql) < 1) {
                                $this->arr_errors[] = array(
                                    "success" => FALSE,
                                    "msg" => " Error al insertar  el registro sl_warehouses_location  ID_products='" . $id_products . "', ID_warehouses='" . $to_wh
                                );
                            }
                            $sth3->disconnect();
                        }
                    }
                    $sth2->dbFreeResult();
                    $sth2->disconnect();
                } else {
                    //- Error
                    $whDTO = new WarehousesDTO();
                    $whDAO = new WarehousesDAO;

                    $whDTO->setName('Conciliation');
                    $arr_result = $whDAO->selectRecords($whDTO);
                    if (!empty($arr_result)) {
                        $to_wh = $arr_result[0]->getID_warehouses();

                        $whLocationDTO = new WarehousesLocationDTO();
                        $whLocationDAO = new WarehousesLocationDAO();

                        $whLocationDTO->setIdWarehouses($to_wh);
                        $whLocationDTO->setIdProducts($id_products);
                        $whLocationDTO->setLocation('999999');
                        $whLocationDTO->setQuantity($qty);
                        $whLocationDTO->setID_admin_users($this->iD_admin_users);

                        $whLocationDAO->insertRecord($whLocationDTO);
                        $id_warehouse_location = $whLocationDAO->getLastInsertId();

                        //-- inserta la informacion de los logs
                        $adminLogsDTO = new AdminLogsDTO();
                        $adminLogsDAO = new AdminLogsDAO();

                        $tblName = 'sl_warehouses_location';
                        $logCmd = '';
                        $type = 'Application';
                        $action = $id_warehouse_location;
                        $message = "bad_wlocation";

                        $adminLogsDTO->setTblName($tblName);
                        $adminLogsDTO->setLogCmd($logCmd);
                        $adminLogsDTO->setType($type);
                        $adminLogsDTO->setAction($action);
                        $adminLogsDTO->setMessage($message);

                        $adminLogsDAO->insertRecord($adminLogsDTO);
                    }

                    $this->arr_process_status[] = array(
                        "success" => false,
                        "msg" => "Invalid Warehouse Location Quantity. Origen: " . $from_wh . "  Destino: " . $to_wh . "  Producto: " . $to_wh . "  Order: " . $id_orders
                    );
                }
            }
        }
        $sth->disconnect();
    }

    private function processTransferWHSkusCost($from_wh, $to_wh, $id_products, $qty, $id_orders) {
        $cost = 0;
        $sth = new DbHandler();
        $sth2 = new DbHandler();
        $sth3 = new DbHandler();

        if ($sth->connect()) {
            $cadena_sql = "SELECT sum(Quantity) as Quantity,sum(if(Isset='Y',1,0)) as SumY 
                FROM sl_skus_cost 
                inner join sl_skus on(sl_skus_cost.ID_products=sl_skus.ID_sku_products)
                WHERE sl_skus_cost.ID_products = " . $sth->cleanSqlValue($id_products) . " 
                AND ID_warehouses = " . $sth->cleanSqlValue($from_wh) . " 
                ORDER BY sl_skus_cost.Date ASC;";

            $sth->selectSQLcommand($cadena_sql);
            if ($sth->getNumRows() > 0) {
                list($amountavail, $sumy) = $sth->fetchNextRow();

                if (($qty <= $amountavail) && $sumy == 0) {
                    $qtytoadjust = $qty;

                    $cadena_sql = "SELECT * FROM sl_skus_cost 
                        WHERE ID_warehouses = " . $sth->cleanSqlValue($from_wh) . "  
                        AND ID_products= " . $sth->cleanSqlValue($id_products) . " 
                        AND Quantity > 0
                        ORDER BY Date ASC;";

                    $sth->selectSQLcommand($cadena_sql);

                    while (($result = $sth->fetchAssocNextRow()) && $qtytoadjust > 0) {

                        if ($qtytoadjust < $result['Quantity']) {
                            //Se ajusta fila en Warehouse From
                            $sth2->connect();
                            $cadena_sql = "UPDATE sl_skus_cost SET Quantity = Quantity - " . $sth2->cleanSqlValue($qtytoadjust) . "  WHERE 1 AND  ID_skus_cost = " . $result['ID_skus_cost'] . " AND ID_warehouses = '" . $sth2->cleanSqlValue($from_wh) . "' ;";

                            if ($sth2->executeSQLcommand($cadena_sql) >= 0) {
                                //Se ajusta/inserta fila en Warehouse To
                                $cadena_sql = "SELECT ID_skus_cost,Cost FROM sl_skus_cost 
                                   WHERE ID_warehouses = " . $sth2->cleanSqlValue($to_wh) . " 
                                       AND ID_products= " . $sth2->cleanSqlValue($id_products) . " 
                                       AND Quantity > 0 
                                       ORDER BY Date DESC LIMIT 1;";

                                $sth2->selectSQLcommand($cadena_sql);
                                if ($sth2->getNumRows() > 0) {
                                    list($idscost, $scost) = $sth2->fetchNextRow();
                                    if ($scost == $result['Cost']) {
                                        $sth3->connect();
                                        $cadena_sql = "UPDATE sl_skus_cost SET Quantity = Quantity + " . $qtytoadjust . " WHERE 1 AND ID_skus_cost = " . $idscost . " AND ID_warehouses = " . $to_wh . " AND ID_products= " . $id_products . ";";

                                        if ($sth3->executeSQLcommand($cadena_sql) < 1) {
                                            $this->arr_process_status[] = array(
                                                "success" => FALSE,
                                                "msg" => "Error al Actualizar el registro: sl_skus_cost; Quantity: $qtytoadjust"
                                            );
                                        }
                                        $sth3->disconnect();
                                    } else {
                                        $sth3->connect();
                                        $cadena_sql = "INSERT INTO sl_skus_cost SET ID_products=$id_products,ID_purchaseorders=0,ID_warehouses=$to_wh,Tblname='transfer', Quantity='$qtytoadjust', Cost='" . $result['Cost'] . "', Date=CURDATE(), Time=CURTIME(), ID_admin_users=" . $this->iD_admin_users . ";";
                                        if ($sth3->executeSQLcommand($cadena_sql) < 1) {
                                            $this->arr_process_status[] = array(
                                                "success" => FALSE,
                                                "msg" => "Error al insertar el registro: sl_skus_cost; Quantity: $qtytoadjust   ID_products=$id_products"
                                            );
                                        }

                                        $sth3->disconnect();
                                    }
                                } else {
                                    $sth3->connect();
                                    $cadena_sql = "INSERT INTO sl_skus_cost SET ID_products=$id_products,ID_purchaseorders=0,ID_warehouses=$to_wh,Tblname='transfer', Quantity='$qtytoadjust', Cost='" . $result['Cost'] . "', Date=CURDATE(), Time=CURTIME(), ID_admin_users=" . $this->iD_admin_users . ";";
                                    if ($sth3->executeSQLcommand($cadena_sql) < 1) {
                                        $this->arr_process_status[] = array(
                                            "success" => FALSE,
                                            "msg" => "Error al insertar el registro: sl_skus_cost; Quantity: $qtytoadjust   ID_products:$id_products"
                                        );
                                    }
                                    $sth3->disconnect();
                                }
                            } else {
                                //Error del query
                                $this->arr_errors[] = array(
                                    "success" => false,
                                    "msg" => "Error al actualizar el registro sl_skus_cost SET Quantity = Quantity - " . $qtytoadjust . "  ;  ID_skus_cost = " . $result['ID_skus_cost'] . "  ID_warehouses = " . $from_wh . " "
                                );
                            }
                            $qtytoadjust = 0;
                        } else {
                            //Se Actualiza fila en Warehouse From
                            $sth2->connect();
                            $cadena_sql = "UPDATE sl_skus_cost SET ID_warehouses = '$to_wh' WHERE 1 AND  ID_skus_cost = " . $result['ID_skus_cost'] . " AND ID_warehouses = '$from_wh';";
                            if($sth2->executeSQLcommand($cadena_sql) < 0){
                                        $this->arr_process_status[] = array(
                                            "success" => FALSE,
                                            "msg" => "Error al actualizar el registro: sl_skus_cost; SET ID_warehouses = '$to_wh' WHERE 1 AND  ID_skus_cost = " . $result['ID_skus_cost'] . " AND ID_warehouses = '$from_wh';"
                                        );                                
                            }
                            $qtytoadjust -= $result['Quantity'];
                            $sth2->disconnect();
                            
                        }
                    } //While
                    if ($qtytoadjust > 0) {
                        //- Error
                        $this->arr_process_status[] = array(
                            "success" => false,
                            "msg" => "Error, Quantity to adjust: $qtytoadjust > 0"
                        );
                    }
                } else {
                    //- Error
                    $whDTO = new WarehousesDTO();
                    $whDAO = new WarehousesDAO;

                    $whDTO->setName('Conciliation');
                    $arr_result = $whDAO->selectRecords($whDTO);

                    if (!empty($arr_result)) {
                        $to_wh = $arr_result[0]->getID_warehouses();

                        $sth3->connect();

                        $cadena_sql = "INSERT INTO sl_skus_cost SET ID_products=$id_products,ID_purchaseorders=0,ID_warehouses=$to_wh,Tblname='transfer', Quantity='$qty', Cost='$cost', Date=CURDATE(), Time=CURTIME(), ID_admin_users=" . $this->iD_admin_users;
                        $sth3->executeSQLcommand($cadena_sql);

                        $last_insertid = $sth3->getInsertId();

                        //-- inserta la informacion de los logs
                        $adminLogsDTO = new AdminLogsDTO();
                        $adminLogsDAO = new AdminLogsDAO();

                        $tblName = 'sl_warehouses_location';
                        $logCmd = '';
                        $type = 'Application';
                        $action = $last_insertid;
                        $message = "bad_scost";

                        $adminLogsDTO->setTblName($tblName);
                        $adminLogsDTO->setLogCmd($logCmd);
                        $adminLogsDTO->setType($type);
                        $adminLogsDTO->setAction($action);
                        $adminLogsDTO->setMessage($message);

                        $adminLogsDAO->insertRecord($adminLogsDTO);

                        $this->arr_process_status[] = array(
                            "success" => false,
                            "msg" => "Invalid scost. ID_products=$id_products,ID_purchaseorders=0,ID_warehouses=$to_wh,Tblname='transfer', Quantity='$qty', Cost='$cost'"
                        );
                    }
                }
            }
        }
        $sth->disconnect();
    }

    private function processErrors() {
        $strProcessErrors = "";
        $strErrors = "";
        
        $successTransfer = TRUE;
        $successErrors = TRUE;

        
        if (!empty($this->arr_process_status)) {
            $successTransfer = FALSE;
            foreach ($this->arr_process_status as $process_status) {
                $strProcessErrors .= $process_status['msg'] . "|";
            }
        }

        if (!empty($this->arr_errors)) {
            $successErrors = FALSE;
            foreach ($this->arr_errors as $errors) {
                $strErrors .= $errors['msg'] . "|";
            }
        }

        $arr_response = array(
            "successTransfer" => $successTransfer,
            "successProcess" => $successErrors,
            "msgProcessErrors" => $strProcessErrors,
            "msgErrors" => $strErrors
        );
        
        return $arr_response;
    }

}

?>