<?php
namespace FacturasCFDI\Addendas;
use MysqlBD;
class Balanza{
	public static function getAddendaStruct(){
		global $cfg;
		$data = array(
			'BCE:Ctas'=>array()
		);
		
		$conn = MysqlBD::getConexion();
		$query = "select
			count(*) movimientos, 
			ID_accounts Cuenta,
			(Select Amount from sl_movements where
				ID_accounts = m.ID_accounts
				and date = Date_sub('2016-03-01', INTERVAL 1 DAY)
			--	and date <= Date_sub('2016-03-01', INTERVAL 1 DAY)
			order by id_movements desc
			limit 1)
			SaldoInicial,
			sum( if( credebit = 'Debit', Amount, 0)) Debe,
			sum( if( credebit = 'Credit', Amount, 0)) Haber,
			sum( if( credebit = 'Debit', Amount, -1 * Amount)) TotalMov
		from sl_movements m where 
		date >= concat('2016', '-',month(m.date), '-','01' )
		-- and ID_accounts = 1174
		and date >= '2016-03-01'
		and date < '2016-04-01'
		group by ID_accounts
		order by date, time asc";
		$res = $conn->query($query);
		while ($row = $res->fetch(\PDO::FETCH_OBJ)) {
			$data['BCE:Ctas'][] = array(
				'@NumCta'	=> $row->Cuenta,
				'@SaldoIni'	=> number_format($row->SaldoInicial, 2, '.', ''),
				'@Debe'		=> number_format($row->Debe, 2, '.', ''),
				'@Haber'	=> number_format($row->Haber, 2, '.', ''),
				'@SaldoFin'	=> number_format($row->TotalMov, 2, '.', ''),
			);
		}
		return $data;
	}
}