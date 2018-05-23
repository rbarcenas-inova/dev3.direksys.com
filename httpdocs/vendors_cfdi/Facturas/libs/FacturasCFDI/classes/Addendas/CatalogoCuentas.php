<?php
namespace FacturasCFDI\Addendas;
use MysqlBD;
class CatalogoCuentas{
	public static function getAddendaStruct(){
		global $cfg;
		$data = array(
			'catalogocuentas:Ctas'=>array()
		);
		
		$conn = MysqlBD::getConexion();
		$query = "select codigoAgrupador, id_accounts, sl_accounts.Name, levelAccount, 'D' n from sl_accounts inner join sl_agrupadorsat using(id_agrupadorsat) where status='Active'";
		$res = $conn->query($query);
		while ($row = $res->fetch(\PDO::FETCH_OBJ)) {
			$data['catalogocuentas:Ctas'][] = array(
				'@CodAgrup'	=> $row->codigoAgrupador,
				'@NumCta'	=> $row->id_accounts,
				'@Desc'		=> $row->Name,
				'@Nivel'	=> $row->levelAccount,
				'@Natur'	=> $row->n
			);
		}
		return $data;
	}
}