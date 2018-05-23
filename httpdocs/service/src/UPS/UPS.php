<?php
namespace Service\UPS;
use Service\Tools\CurlClient;
class UPS extends CurlClient{
	protected $conf;
	public function __construct($conf = array()){
		if(count($conf)> 0){
			$this->conf = (object)$conf;
		}else{
			$this->conf = (object)array(
				'username' 	=>  $GLOBALS['cfg']['ups_user'],
				'password'	=>  $GLOBALS['cfg']['ups_pass'],
				'token'		=>  $GLOBALS['cfg']['ups_token'],
				'url'		=>  $GLOBALS['cfg']['ups_url']
			);
		}
	}
	public function get($tracking = ''){
		if($tracking == '')
			return (object)[];
		$delivery_date = '';
		$entregado = FALSE;
		$shipment_date = '';
		$scheduled_date = '';
		$service = '';
		$params = [
			'UPSSecurity' => [
				'UsernameToken' => [
					'Username' => $this->conf->username,
					'Password' => $this->conf->password
				],
				'ServiceAccessToken' => [
					'AccessLicenseNumber' => $this->conf->token
				]
			],
			'TrackRequest' => [
				'InquiryNumber' => $tracking
			]
		];

		$conf = array(
			'method' => 'POST',
			'header' => array('Content-Type: application/json; charset="utf-8"'),
			'url' => $this->conf->url,
			'params'=> is_array( $params ) ? json_encode($params) : '',
			'parseFrom'=>'json'
		);
		$response = self::request($conf);

		if(isset($response->TrackResponse)){
			if(isset($response->TrackResponse->Shipment->PickupDate))
				$shipment_date = preg_replace("/(\d{4})(\d{2})(\d{2})/", "$1-$2-$3", $response->TrackResponse->Shipment->PickupDate);

			$service = $response->TrackResponse->Shipment->Service->Description;
			$service = strtolower(str_replace(' ', '_', $service));
			$scheduled_date = preg_replace("/(\d{4})(\d{2})(\d{2})/", "$1-$2-$3", @$response->TrackResponse->Shipment->DeliveryDetail->Date);

			$primer = $response->TrackResponse->Shipment->Package->Activity->Status->Description;

			if($primer == 'DELIVERED'){
				$delivery_date = preg_replace("/(\d{4})(\d{2})(\d{2})/", "$1-$2-$3", $response->TrackResponse->Shipment->Package->Activity->Date);
				$entregado = TRUE;
			}
		}

		return (object)	array(
			'delivery'				 => $entregado,
			'delivery_date'			 => $delivery_date,
			'shipment_date'			 => $shipment_date,
			'expected_delivery_date' => $scheduled_date,
			'service_type'			 => $service,
			'tracking_number'		 => $tracking
		);

	}

}
