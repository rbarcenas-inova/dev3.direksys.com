<?php



use Doctrine\ORM\Mapping as ORM;

/**
 * SlEntershipments
 *
 * @ORM\Table(name="sl_entershipments", indexes={@ORM\Index(name="Type", columns={"Type", "Date"}), @ORM\Index(name="Status", columns={"Status"}), @ORM\Index(name="ID_orders", columns={"ID_orders"}), @ORM\Index(name="Date", columns={"Date"})})
 * @ORM\Entity
 */
class SlEntershipments
{
    /**
     * @var integer
     *
     * @ORM\Column(name="ID_entershipments", type="integer", nullable=false)
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     */
    private $idEntershipments;

    /**
     * @var integer
     *
     * @ORM\Column(name="ID_orders", type="integer", nullable=false)
     */
    private $idOrders;

    /**
     * @var integer
     *
     * @ORM\Column(name="ID_warehouses_batches", type="integer", nullable=true)
     */
    private $idWarehousesBatches;

    /**
     * @var string
     *
     * @ORM\Column(name="Type", type="string", nullable=true)
     */
    private $type;

    /**
     * @var string
     *
     * @ORM\Column(name="PickDate", type="string", nullable=true)
     */
    private $pickdate;

    /**
     * @var string
     *
     * @ORM\Column(name="ScheduledDelivery", type="string", nullable=true)
     */
    private $scheduleddelivery;

    /**
     * @var string
     *
     * @ORM\Column(name="DeliveryDate", type="string", nullable=true)
     */
    private $deliverydate;

    /**
     * @var string
     *
     * @ORM\Column(name="Input", type="text", length=65535, nullable=false)
     */
    private $input;

    /**
     * @var string
     *
     * @ORM\Column(name="Output", type="text", length=65535, nullable=false)
     */
    private $output;

    /**
     * @var string
     *
     * @ORM\Column(name="Status", type="string", nullable=false)
     */
    private $status;

    /**
     * @var string
     *
     * @ORM\Column(name="Date", type="string", nullable=false)
     */
    private $date;

    /**
     * @var string
     *
     * @ORM\Column(name="Time", type="time", nullable=false)
     */
    private $time;

    /**
     * @var integer
     *
     * @ORM\Column(name="ID_admin_users", type="integer", nullable=false)
     */
    private $idAdminUsers;


    /**
     * Get idEntershipments
     *
     * @return integer 
     */
    public function getIdEntershipments()
    {
        return $this->idEntershipments;
    }

    public function setIdEntershipments($idEntershipments)
    {
        return $this->idEntershipments = $idEntershipments;
        return $this;
    }

    /**
     * Set idOrders
     *
     * @param integer $idOrders
     * @return SlEntershipments
     */
    public function setIdOrders($idOrders)
    {
        $this->idOrders = $idOrders;

        return $this;
    }

    /**
     * Get idOrders
     *
     * @return integer 
     */
    public function getIdOrders()
    {
        return $this->idOrders;
    }

    /**
     * Set idWarehousesBatches
     *
     * @param integer $idWarehousesBatches
     * @return SlEntershipments
     */
    public function setIdWarehousesBatches($idWarehousesBatches)
    {
        $this->idWarehousesBatches = $idWarehousesBatches;

        return $this;
    }

    /**
     * Get idWarehousesBatches
     *
     * @return integer 
     */
    public function getIdWarehousesBatches()
    {
        return $this->idWarehousesBatches;
    }

    /**
     * Set type
     *
     * @param string $type
     * @return SlEntershipments
     */
    public function setType($type)
    {
        $this->type = $type;

        return $this;
    }

    /**
     * Get type
     *
     * @return string 
     */
    public function getType()
    {
        return $this->type;
    }

    /**
     * Set pickdate
     *
     * @param string $pickdate
     * @return SlEntershipments
     */
    public function setPickdate($pickdate)
    {
        $this->pickdate = $pickdate;

        return $this;
    }

    /**
     * Get pickdate
     *
     * @return string 
     */
    public function getPickdate()
    {
        return $this->pickdate;
    }

    /**
     * Set scheduleddelivery
     *
     * @param string $scheduleddelivery
     * @return SlEntershipments
     */
    public function setScheduleddelivery($scheduleddelivery)
    {
        $this->scheduleddelivery = $scheduleddelivery;

        return $this;
    }

    /**
     * Get scheduleddelivery
     *
     * @return string 
     */
    public function getScheduleddelivery()
    {
        return $this->scheduleddelivery;
    }

    /**
     * Set deliverydate
     *
     * @param string $deliverydate
     * @return SlEntershipments
     */
    public function setDeliverydate($deliverydate)
    {
        $this->deliverydate = $deliverydate;

        return $this;
    }

    /**
     * Get deliverydate
     *
     * @return string 
     */
    public function getDeliverydate()
    {
        return $this->deliverydate;
    }

    /**
     * Set input
     *
     * @param string $input
     * @return SlEntershipments
     */
    public function setInput($input)
    {
        $this->input = $input;

        return $this;
    }

    /**
     * Get input
     *
     * @return string 
     */
    public function getInput()
    {
        return $this->input;
    }

    /**
     * Set output
     *
     * @param string $output
     * @return SlEntershipments
     */
    public function setOutput($output)
    {
        $this->output = $output;

        return $this;
    }

    /**
     * Get output
     *
     * @return string 
     */
    public function getOutput()
    {
        return $this->output;
    }

    /**
     * Set status
     *
     * @param string $status
     * @return SlEntershipments
     */
    public function setStatus($status)
    {
        $this->status = $status;

        return $this;
    }

    /**
     * Get status
     *
     * @return string 
     */
    public function getStatus()
    {
        return $this->status;
    }

    /**
     * Set date
     *
     * @param string $date
     * @return SlEntershipments
     */
    public function setDate($date)
    {
        $this->date = $date;

        return $this;
    }

    /**
     * Get date
     *
     * @return string 
     */
    public function getDate()
    {
        return $this->date;
    }

    /**
     * Set time
     *
     * @param string $time
     * @return SlEntershipments
     */
    public function setTime($time)
    {
        $this->time = $time;

        return $this;
    }

    /**
     * Get time
     *
     * @return string 
     */
    public function getTime()
    {
        return $this->time;
    }

    /**
     * Set idAdminUsers
     *
     * @param integer $idAdminUsers
     * @return SlEntershipments
     */
    public function setIdAdminUsers($idAdminUsers)
    {
        $this->idAdminUsers = $idAdminUsers;

        return $this;
    }

    /**
     * Get idAdminUsers
     *
     * @return integer 
     */
    public function getIdAdminUsers()
    {
        return $this->idAdminUsers;
    }
}
