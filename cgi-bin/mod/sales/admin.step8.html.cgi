#!/usr/bin/perl
##################################################################
############      CONSOLE STEP 8           #################
##################################################################

# Forms Involved: 
# Created on: CH @ 26/may/2008 11:48AM GMT -0600
# Last Modified on: 7/10/2008 11:25:09 AM
# Last Modified by:CH
# Author: CH
# Description : Show the payment options for a product
# Parameters : idproduct,flexipays,type[30 days, 15 days] 

# Last Modified on: 07/22/08 13:37:21
# Last Modified by: MCC C. Gabriel Varela S y Lic. Roberto C. Bárcenas A.: Se corrige cuando se agrega un producto relacionado, sugerido y especial
# Last Modified on: 11/03/08 11:42:35
# Last Modified by: MCC C. Gabriel Varela S: Se modifica para contemplar lo de servicio Membership
# Last Modified RB: 03/12/09  11:33:45 -- Se resolcio el problema al agregar y dar de baja items y services y se agrego el &save_callsession().
# Last Modified on: 05/12/09 15:42:32
# Last Modified by: MCC C. Gabriel Varela S: Se agrega variable para determinar si existe membresía en la orden
# Last Modified on: 05/14/09 12:20:18
# Last Modified by: MCC C. Gabriel Varela S: Se hace que al borrar un producto y si tiene promoción se borre su relacionado.
# Last Modified RB: 07/08/09  17:12:28 -- Se soluciona problema de cambio de choice
# Last Modified RB: 07/09/09  12:32:41 -- Se configura costo minimo de garantia de acuerdo a parametro en setup.cfg


    #&show_shipments;
    #&pay_type_verification;
    #$va{'pdmaxdays'} = $cfg{'postdateddays'};
    #&cgierr(1);
  #&show_shipments;
    &pay_type_verification;
    $va{'pdmaxdays'} = $cfg{'postdateddays'}; 

    if($in{'days'} and $in{'days'} =~ /^\d{4}-\d{2}-\d{2}$/ ){
        my ($sth) = &Do_SQL("SELECT DATEDIFF('".$in{'days'}."',curdate());");        
        $in{'days'} = $sth->fetchrow();
    }

    
    for my $i(1..$cses{'items_in_basket'}){
        
        if ($in{"fpago$i".$cses{'items_'.$i.'_id'}}){
            $cses{'items_'.$i.'_payments'} = $in{"fpago$i".$cses{'items_'.$i.'_id'}};
            ($tot_fp < $in{"fpago$i".$cses{'items_'.$i.'_id'}}) and ($tot_fp =  $in{"fpago$i".$cses{'items_'.$i.'_id'}})
            
        }
    }

    if($in{'postdated'} and $cfg{'postdatedfesprice'} >= 0 and (!$cses{'postdated'} or int($in{'days'}) != int($cses{'days'}))){

        my $this_origin = lc(&load_name('sl_salesorigins', 'ID_salesorigins', $cses{'id_salesorigins'}, 'Channel'));
        my $pd_price = ($this_origin and $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}} and $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}} >= 0) ? $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}} : $cfg{'postdatedfesprice'};
        #&cgierr("$this_origin - $cses{'pay_type'} - " . $cfg{'postdatedfesprice_' . $this_origin . '_' . $cses{'pay_type'}});
        #&cgierr($pd_price);

        if (!$cses{'postdated'}){
            ++$cses{'servis_in_basket'};
            $cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = "60000".$cfg{'postdatedfeid'};
            $cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
            $cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
            $cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $pd_price;
            $cses{'postdated'}=1;
            $cses{'days'}=$in{'days'};
        }else{
            $cses{'days'}=$in{'days'};
        }

    }
    
    if ($cses{'sameshipping'}){
        $va{'billingshipping'} = &trans_txt('samebillshp');
    }else{
        $va{'billingshipping'} = &trans_txt('difbillshp');
    }
    $va{'shippingtype'} = &trans_txt('shp_type_'.$cses{'shp_type'});
    $in{'op'}=int($in{'op'});
   
    my (@c) = split(/,/,$cfg{'srcolors'});
       
    ##################################
    ### Agrega producto
    ##################################
    if($in{'addrelprod'}==1){

        ## Load Promo
        my ($sth) = &Do_SQL("SELECT VValue FROM sl_vars WHERE VName='promo$in{'id_products'}';");
        $cfg{'promo'.$in{'id_products'}} = $sth->fetchrow;
    	
    	if ($cfg{'promo'.substr($in{'id_sku_products'},3,6)}){
				$va{'msg_sku'} =1;
				my (@pary) = split(/\|/,$cfg{'promo'.substr($in{'id_sku_products'},3,6)});
				for (0..$#pary){
					if ($in{'idp'.$pary[$_]}){
						++$cses{'items_in_basket'};							
						$cses{'items_'.$cses{'items_in_basket'}.'_id'} = $in{'idp'.$pary[$_]};
						$cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;
						$cses{'items_'.$cses{'items_in_basket'}.'_relid'} = substr($in{'id_sku_products'},3,6);
						delete($va{'msg_sku'});
					}
				}
		}else{
	        ++$cses{'items_in_basket'};           
	        $cses{'items_'.$cses{'items_in_basket'}.'_qty'} = 1;
	        $cses{'items_'.$cses{'items_in_basket'}.'_id'} = $in{'id_sku_products'};
		}
        
        
        
        #fpago
        $cses{'items_'.$cses{'items_in_basket'}.'_fpago'} = &load_name('sl_products','ID_products',substr($cses{'items_'.$cses{'items_in_basket'}.'_id'},3,9),'Flexipago')if($cses{'items_'.$cses{'items_in_basket'}.'_pnum'}<=1); 
        #fpprice
        $cses{'items_'.$cses{'items_in_basket'}.'_fpprice'} = &load_name('sl_products','ID_products',substr($cses{'items_'.$cses{'items_in_basket'}.'_id'},3,9),'FPPrice'); 
        #insurance
        $cses{'items_'.$cses{'items_in_basket'}.'_insurance'} = &load_name('sl_products','ID_products',substr($cses{'items_'.$cses{'items_in_basket'}.'_id'},3,9),'Insurance'); 
        #Duties
        $cses{'items_'.$cses{'items_in_basket'}.'_duties'} = &load_name('sl_products','ID_products',substr($cses{'items_'.$cses{'items_in_basket'}.'_id'},3,9),'Duties'); 
        
        if($in{'relid'} > 0){
        	$cses{'items_'.$cses{'items_in_basket'}.'_relid'} = $in{'relid'};
      	} elsif($in{'relid'} eq -1) {
      		$highestvalue=0;
      		for my $i(1..$cses{'items_in_basket'}){
            if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
            	if($cses{'items_'.$i.'_price'}>$highestvalue){
            		$highestvalue=$cses{'items_'.$i.'_price'};
            		$cses{'items_'.$cses{'items_in_basket'}.'_relid'} = $cses{'items_'.$i.'_id'};
            	}
            }
          }
      	}
        $price=&load_name('sl_products','ID_products',substr($cses{'items_'.$cses{'items_in_basket'}.'_id'},3,9),'SPrice');
        $cses{'items_'.$cses{'items_in_basket'}.'_price'} = $price;
        &calculate_shipping;
        &service_bydefault();
        &save_callsession();
    }
       
    #RB Start - Change the choice - may0208
    if($in{'ajaxresp'}){
        # Change the choice
        for my $i(1..$cses{'items_in_basket'}){
            ($cses{'items_'.$i.'_qty'}>0 and $i == $in{'drop'}) and ($cses{'items_'.$i.'_id'} = $in{'ajaxresp'});
        }
        #Change the services related to
        for my $i(1..$cses{'servis_in_basket'}){
            ($cses{'servis_'.$i.'_qty'}>0 and $cses{'servis_'.$i.'_relid'} == $in{'idchoiceold'}) and ($cses{'servis_'.$i.'_relid'} = $in{'ajaxresp'});
        }
    }
    #RB End           
       
    #Drop Product
    if($in{'drop'} and !$in{'ajaxresp'}){
        #Recorre los servicios
        for my $i(1..$cses{'servis_in_basket'}){
            if ($cses{'servis_'.$i.'_qty'}>0 and $cses{'servis_'.$i.'_id'}>0){
                #Verifica si tiene servicio ligado
                if($cses{'items_'.$in{'drop'}.'_id'}==$cses{'servis_'.$i.'_relid'} || $cses{'servis_'.$i.'_id'} eq "60000".$cfg{'duties'} || $cses{'servis_'.$i.'_id'} eq "60000".$cfg{'insurance'}){ #RB Modify
					delete($cses{'servis_dut'});
					delete($cses{'servis_ins'});
                    delete($cses{'servis_'.$i.'_id'});
                    delete($cses{'servis_'.$i.'_qty'});
                    delete($cses{'servis_'.$i.'_ser'});
                    delete($cses{'servis_'.$i.'_relid'});
                    delete($cses{'servis_'.$i.'_desc'});
                    delete($cses{'servis_'.$i.'_fpago'});
                    delete($cses{'servis_'.$i.'_payments'});
                    delete($cses{'servis_'.$i.'_price'});
                    delete($cses{'servis_'.$i.'_discount'});
                    delete($cses{'servis_'.$i.'_shp1'});
			        delete($cses{'servis_'.$i.'_shp2'});
			        delete($cses{'servis_'.$i.'_tax'});
                }
            }
        }
        
        #Recorre los productos
        for my $i(1..$cses{'items_in_basket'}){
        	if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
        		#Verifica si tiene producto ligado
        		if(($cses{'items_'.$in{'drop'}.'_id'}!=$cses{'items_'.$i.'_id'})and($cses{'items_'.$in{'drop'}.'_relid'}==$cses{'items_'.$i.'_relid'})){
        			
        			#Recorre los servicios
			        for my $j(1..$cses{'servis_in_basket'}){
			            if ($cses{'servis_'.$j.'_qty'}>0 and $cses{'servis_'.$j.'_id'}>0){
			                #Verifica si tiene servicio ligado
			                if($cses{'items_'.$i.'_id'}==$cses{'servis_'.$j.'_relid'} || $cses{'servis_'.$j.'_id'} eq "60000".$cfg{'duties'} || $cses{'servis_'.$j.'_id'} eq "60000".$cfg{'insurance'}){ #RB Modify
								delete($cses{'servis_dut'});
								delete($cses{'servis_ins'});
			                    delete($cses{'servis_'.$j.'_id'});
			                    delete($cses{'servis_'.$j.'_qty'});
			                    delete($cses{'servis_'.$j.'_ser'});
			                    delete($cses{'servis_'.$j.'_relid'});
			                    delete($cses{'servis_'.$j.'_desc'});
			                    delete($cses{'servis_'.$j.'_fpago'});
			                    delete($cses{'servis_'.$j.'_payments'});
			                    delete($cses{'servis_'.$j.'_price'});
			                    delete($cses{'servis_'.$j.'_discount'});
			                    delete($cses{'servis_'.$j.'_shp1'});
						        delete($cses{'servis_'.$j.'_shp2'});
						        delete($cses{'servis_'.$j.'_tax'});
			                }
			            }
			        }
        			delete($cses{'items_'.$i.'_desc'});
			        delete($cses{'items_'.$i.'_downpayment'});
			        delete($cses{'items_'.$i.'_id'});
			        delete($cses{'items_'.$i.'_duties'});
					delete($cses{'items_'.$i.'_fpprice'});
					delete($cses{'items_'.$i.'_insurance'});
					delete($cses{'items_'.$i.'_msprice'});
        			delete($cses{'items_'.$i.'_price'});
			        delete($cses{'items_'.$i.'_qty'});
			        delete($cses{'items_'.$i.'_fpago'});
			        delete($cses{'items_'.$i.'_payments'});
			        delete($cses{'items_'.$i.'_discount'});
			        delete($cses{'items_'.$i.'_tax'});
        		}
        	}
        }
        
        
		delete($cses{'items_'.$in{'drop'}.'_desc'});
		delete($cses{'items_'.$in{'drop'}.'_downpayment'});
		delete($cses{'items_'.$in{'drop'}.'_id'});
		delete($cses{'items_'.$in{'drop'}.'_duties'});
		delete($cses{'items_'.$in{'drop'}.'_fpprice'});
		delete($cses{'items_'.$in{'drop'}.'_insurance'});
		delete($cses{'items_'.$in{'drop'}.'_msprice'});
		delete($cses{'items_'.$in{'drop'}.'_price'});
		delete($cses{'items_'.$in{'drop'}.'_qty'});
		delete($cses{'items_'.$in{'drop'}.'_fpago'});
		delete($cses{'items_'.$in{'drop'}.'_payments'});
		delete($cses{'items_'.$in{'drop'}.'_discount'});
		delete($cses{'items_'.$in{'drop'}.'_tax'});
        &service_bydefault(); #JRG 10-06-2008
        &save_callsession();
    }
	&show_shipments;
    
    #Agrega servicio
    if($in{'ser'} ){
    	if(substr($in{'id_services'},5)==$cfg{'membershipservid'}){
    		++$cses{'servis_in_basket'};
    		$cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = $in{'id_services'};
    		$cses{'servis_'.$cses{'servis_in_basket'}.'_discount'} = 0;
    		$cses{'servis_'.$cses{'servis_in_basket'}.'_fpago'} = 1;
    		$cses{'servis_'.$cses{'servis_in_basket'}.'_payments'} = 1;
    		$cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
		    $cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
            $price=&load_name('sl_services','ID_services',substr($in{'id_services'},5,4),'SPrice');
		    		    
            ## 08102013:AD::Tax in Services
            if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
                ($price, $tax_serv, $tax_rate) = &services_tax(substr($in{'id_services'},5,4));
                $cses{'servis_'.$cses{'servis_in_basket'}.'_tax'} = $tax_serv;
                $cses{'servis_'.$cses{'servis_in_basket'}.'_tax_percent'} = $tax_rate;
            }

            $cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $price;
		    $cses{'type'} = "Membership";
		    $cses{'membershipinorder'} = "1";
    	}else{
            if (!$cfg{'one_service_by_order'}){
                #GV Modificación: Se hace que se agregue un servicio por cada producto en el carrito.
                for my $i(1..$cses{'items_in_basket'}){
                    $flagser = 0;    #RB Start - Add one Extended Warranty/Product - may0208
                    if ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'}>0){
                        ++$cses{'servis_in_basket'};
                        #GV Modifica 21abr2008 Se cambia id_services por id_services
                        if ($in{'id_services'}){
                            (substr($in{'id_services'},5) == $cfg{'extwarrid'}) and  ($cses{'items_'.$i.'_ew'}) and ($flagser = 1);
                            if($flagser == 0){
                                    #&cgierr(substr($in{'id_services'},5) . "$cfg{'extwarrid'}");
                                #GV Modifica 21abr2008 Se cambia id_services por id_services
                                $cses{'servis_'.$cses{'servis_in_basket'}.'_id'} = $in{'id_services'};
                                $cses{'servis_'.$cses{'servis_in_basket'}.'_qty'} = 1;
                                $cses{'servis_'.$cses{'servis_in_basket'}.'_ser'} = 1;
                                $cses{'servis_'.$cses{'servis_in_basket'}.'_relid'} = $cses{'items_'.$i.'_id'};
                                #GV Modifica 21abr2008 Se cambia sl_services por sl_services #GV Modifica 21abr2008 Se cambia ID_services por ID_services
                                (substr($in{'id_services'},5) == $cfg{'extwarrid'}) and ($cses{'items_'.$i.'_ew'} = 1);
                                $price=&load_name('sl_services','ID_services',substr($in{'id_services'},5,4),'SPrice');
                                
                                ## 08102013:AD::Tax in Services
                                if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
                                    ($price, $tax_serv, $tax_rate) = &services_tax(substr($in{'id_services'},5,4));
                                    $cses{'servis_'.$cses{'servis_in_basket'}.'_tax'} = $tax_serv;
                                    $cses{'servis_'.$cses{'servis_in_basket'}.'_tax_percent'} = $tax_rate;
                                }

                                $price = $cses{'items_'.$i.'_price'} * ($cfg{'extwarrpctsfp'}/100) if substr($in{'id_services'},5) == $cfg{'extwarrid'};
                                $price = $cfg{'extwarminprice'} if (substr($in{'id_services'},5) == $cfg{'extwarrid'} and $price < $cfg{'extwarminprice'});
                                $cses{'servis_'.$cses{'servis_in_basket'}.'_price'} = $price;
                                #&cgierr($cses{'servis_'.$cses{'servis_in_basket'}.'_price'} . " $i") if $cses{'items_'.$i.'_price'} eq '39.99';
                            }
                        }
                    }
                }
                #GV Inicia 17abr2008 Si hay flexipagos agregar un porcentaje
                #&calculatetotal;
                #&flexiservice;
                #GV Termina 17abr2008 Si hay flexipagos agregar un porcentaje
            }else{
                my ($id_next) =  $cses{'servis_in_basket'}+1;
                if ($in{'id_services'}){
                    $cses{'servis_'.$id_next.'_id'} = $in{'id_services'};
                    $cses{'servis_'.$id_next.'_qty'} = 1;
                    $cses{'servis_'.$id_next.'_ser'} = 1;
                    $cses{'servis_'.$id_next.'_relid'} = $cses{'items_'.$i.'_id'};
                    ++$cses{'servis_in_basket'};
                    $price=&load_name('sl_services','ID_services',substr($in{'id_services'},5,4),'SPrice');
                    
                    ## 08102013:AD::Tax in Services
                    if ($cfg{'calc_tax_in_services'} and $cfg{'calc_tax_in_services'}==1){
                        ($price, $tax_serv, $tax_rate) = &services_tax(substr($in{'id_services'},5,4));
                        $cses{'servis_'.$id_next.'_tax'} = $tax_serv;
                        $cses{'servis_'.$id_next.'_tax_percent'} = $tax_rate;
                    }

                    $price = $cses{'items_'.$i.'_price'} * ($cfg{'extwarrpctsfp'}/100) if substr($in{'id_services'},5) == $cfg{'extwarrid'};
                    $price = $cfg{'extwarminprice'} if (substr($in{'id_services'},5) == $cfg{'extwarrid'} and $price < $cfg{'extwarminprice'});
                    $cses{'servis_'.$id_next.'_price'} = $price;
                }
            }
        }
    }
    &save_callsession();  
    #Elimina servicio
    if($in{'dropser'}){
        #RB Start - Delete '_ew' session if the service is deleted
        if(substr($cses{'servis_'.$in{'dropser'}.'_id'},5) == $cfg{'extwarrid'}){
            for my $i(1..$cses{'items_in_basket'}){
                ($cses{'items_'.$i.'_qty'}>0 and $cses{'items_'.$i.'_id'} == $cses{'servis_'.$in{'dropser'}.'_relid'}) and (delete($cses{'items_'.$i.'_ew'}));
            }
        }
        if(substr($cses{'servis_'.$in{'dropser'}.'_id'},5) == $cfg{'postdatedfeid'}){
            $cses{'days'}=1;
        	delete($cses{'postdated'});	
        }elsif(substr($cses{'servis_'.$in{'dropser'}.'_id'},5) == $cfg{'membershipservid'}){
        	$cses{'type'} = "Retail";
        	delete($cses{'membershipinorder'});
        	$cses{'type'}=&load_name('sl_customers','ID_customers',$cses{'id_customers'},'Type') if($cses{'id_customers'} and !$cses{'type'});
        }
        delete($cses{'servis_'.$in{'dropser'}.'_id'});
        delete($cses{'servis_'.$in{'dropser'}.'_qty'});
        delete($cses{'servis_'.$in{'dropser'}.'_ser'});
        delete($cses{'servis_'.$in{'dropser'}.'_relid'});
        delete($cses{'servis_'.$in{'dropser'}.'_desc'});
        delete($cses{'servis_'.$in{'dropser'}.'_fpago'});
        delete($cses{'servis_'.$in{'dropser'}.'_payments'});
        delete($cses{'servis_'.$in{'dropser'}.'_price'});
        delete($cses{'servis_'.$in{'dropser'}.'_discount'});
        delete($cses{'servis_'.$in{'dropser'}.'_shp1'});
        delete($cses{'servis_'.$in{'dropser'}.'_shp2'});
        delete($cses{'servis_'.$in{'dropser'}.'_tax'});
        delete($cses{'servis_'.$in{'dropser'}.'_tax_percent'});
        &save_callsession();
    }
    #GVTermina
	$va{'paytype'} = &trans_txt('pay_type_'.$cses{'pay_type'});

1;

