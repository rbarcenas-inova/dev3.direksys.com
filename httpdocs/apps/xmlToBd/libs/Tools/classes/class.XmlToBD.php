<?php
class XmlToBD{
	public static function init(){
		$con = MysqlBD::getConexion();
		$query = "select ID_invoices,doc_serial,doc_num,concat(doc_serial,'_',doc_num) invoice_file from cu_invoices where doc_serial !='' and doc_num !=0 limit 10;";
		$res = $con->query($query);
		$all = $res->fetchAll(PDO::FETCH_ASSOC);
		// show(ftp_get_recursive_paths('/CMU060119UI7',3));
		// foreach ($all as $key => $value) {
		// 	// echo SERVER.'<br>';
		// 	// exit;
		// 	// show($file);
		// }
	}
}