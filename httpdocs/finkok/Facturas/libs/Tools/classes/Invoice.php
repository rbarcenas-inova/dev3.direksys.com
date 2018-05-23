<?php
class Invoice extends MysqlBD{
	public static $id_invoices;
	public static function updateInvoice($id_invoices = 0, $changes){
		if(!is_int($id_invoices) || $id_invoices == 0)
			throw new \Exception("Debes definir una ID de Invoice");
		if(!is_array($changes) || count($changes) == 0)
			throw new \Exception("Debes definir Los campos a actualizar");
		$queryUpdate = "UPDATE cu_invoices SET ";
		foreach ($changes as $key => $value) {
			$queryUpdate .= " `$key` = :{$key} ,";
		}
		$queryUpdate = trim($queryUpdate, ',');
		$queryUpdate .= " WHERE `ID_invoices` = :ID_invoices ";
		$conn = self::getConexion();
		$sth = $conn->prepare($queryUpdate);
		$sth->execute(array_merge($changes, ['ID_invoices' => $id_invoices]));
		return TRUE;

	}
	public static function addNote($id_invoices = 0, $nota){
		if(!is_int($id_invoices) || $id_invoices == 0)
			throw new \Exception("Debes definir una ID de Invoice");
		if(!is_string($nota) || empty($nota))
			throw new \Exception("Debes definir la Nota");
		$queryNote = 'INSERT INTO cu_invoices_notes (`ID_invoices`, `Notes`, `Type`, `Date`, `Time`, `ID_admin_users`) VALUES (?, ?, ?, curdate(), curtime(), ?)';
		$conn = self::getConexion();
		$sth = $conn->prepare($queryNote);
		$sth->execute([$id_invoices, $nota, 'Error', 1]);
	}
}
