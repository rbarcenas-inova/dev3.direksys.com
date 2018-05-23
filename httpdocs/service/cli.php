<?php

require_once 'bootstrap.php';

switch ($cli['option']) {
	case 'updateUPS':
		$rsm = new Doctrine\ORM\Query\ResultSetMapping();
		$conn = Service\Tools\DB::getConnection();
		$em = Service\Tools\DB::getEntityManager();
		$query = "select 
				sl_orders_products.Tracking
				, sl_orders_products.ID_orders
				, sl_entershipments.ID_entershipments 
				, sl_entershipments.DeliveryDate
			from 
				sl_orders_products 
			inner join 
				(
					select 
						sl_entershipments.ID_orders
						, sl_entershipments.ID_entershipments
						, sl_entershipments.Input 
						, sl_entershipments.DeliveryDate
					from sl_entershipments
					where 1
						and sl_entershipments.`Status` = 'ok'
						and sl_entershipments.Date >= DATE_ADD(NOW(), INTERVAL -30 DAY)
						and sl_entershipments.Input like '%1Z%'
						and ( 
							sl_entershipments.PickDate is null
							or sl_entershipments.ScheduledDelivery is null
							or sl_entershipments.DeliveryDate is null
							or sl_entershipments.DeliveryDate = '0000-00-00'
						)
				)sl_entershipments on sl_entershipments.ID_orders = sl_orders_products.ID_orders
			where 1
				and sl_entershipments.Input like concat('%', sl_orders_products.Tracking, '%')
				and sl_orders_products.ShpProvider = 'UPS'
				and sl_entershipments.DeliveryDate is null
				and sl_orders_products.Tracking is not null
				and sl_orders_products.Status != 'Inactive'
			group by sl_orders_products.Tracking;";
		$rs = $conn->query($query);
		$batchSize = 100;
		$i = 0;
		$ups = new Service\UPS\UPS();
		while($row = $rs->fetch(PDO::FETCH_OBJ)){
			$entershipment = $em->find('SlEntershipments', $row->ID_entershipments);
			$result = $ups->get($row->Tracking);
			$entershipment->setPickdate($result->shipment_date)
			->setScheduledDelivery($result->expected_delivery_date)
			->setDeliveryDate($result->delivery_date);

			$em->persist($entershipment);
			if (($i % $batchSize) == 0) {
		         $em->flush();
		    }
		    $i++;
			
		}

		echo 'Se actualiaron estatus de Tracking de UPS' . PHP_EOL;

		break;
	case 'tracking':
		if($cli['number']){
			$ups = new \Service\UPS\UPS();
			echo json_encode($ups->get($cli['number']));
		}
		break;
	default:
		echo 'OPCION INVALIDA';
		break;
}