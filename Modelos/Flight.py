class Flight:
    """
    Flight class representing a flight node in an AVL tree structure.
    This class encapsulates all flight-related information and contains tree node properties
    for integration into an AVL (Adelson-Velsky and Landis) balanced binary search tree.
    Attributes:
        _id (int): Unique identifier for the flight.
        _origin (str): Departure airport or city.
        _destiny (str): Destination airport or city.
        _departureTime (datetime): Scheduled departure time.
        _basePrice (float): Base price of the flight ticket.
        _finalPrice (float): Final price after promotions or adjustments.
        _passengers (int): Number of passengers on the flight.
        _promotion (float): Active promotion discount or offer.
        _alert (bool): Flag indicating if there are any alerts for this flight.
        _parent (Flight): Reference to the parent node in the AVL tree.
        _leftChild (Flight): Reference to the left child node in the AVL tree.
        _rightChild (Flight): Reference to the right child node in the AVL tree.
    Methods:
        Getters: Retrieve values for all flight attributes and tree node references.
        Setters: Modify values for all flight attributes and tree node references.
    """
    def __init__(self, id, origin, destiny, departureTime, basePrice, finalPrice, passengers, promotion, alert):
        self._id = id
        self._origin = origin
        self._destiny = destiny
        self._departureTime = departureTime
        self._basePrice = basePrice
        self._finalPrice = finalPrice
        self._passengers = passengers
        self._promotion = promotion
        self._alert = alert
        self._parent = None
        self._leftChild = None
        self._rightChild = None

    def getId(self):
        return self._id
    
    def getValue(self):
        return self._id

    def getOrigin(self):
        return self._origin

    def getDestiny(self):
        return self._destiny

    def getDepartureTime(self):
        return self._departureTime

    def getBasePrice(self):
        return self._basePrice

    def getFinalPrice(self):
        return self._finalPrice

    def getPassengers(self):
        return self._passengers

    def getPromotion(self):
        return self._promotion

    def getAlert(self):
        return self._alert

    def getParent(self):
        return self._parent
    
    def getLeftChild(self):
        return self._leftChild
    
    def getRightChild(self):
        return self._rightChild
    
    def setId(self, id):
        self._id = id

    def setOrigin(self, origin):
        self._origin = origin

    def setDestiny(self, destiny):
        self._destiny = destiny

    def setDepartureTime(self, departureTime):
        self._departureTime = departureTime

    def setBasePrice(self, basePrice):
        self._basePrice = basePrice

    def setFinalPrice(self, finalPrice):
        self._finalPrice = finalPrice

    def setPassengers(self, passengers):
        self._passengers = passengers

    def setPromotion(self, promotion):
        self._promotion = promotion

    def setAlert(self, alert):
        self._alert = alert

    def setParent(self, parent):
        self._parent = parent

    def setLeftChild(self, leftChild):
        self._leftChild = leftChild

    def setRightChild(self, rightChild):
        self._rightChild = rightChild