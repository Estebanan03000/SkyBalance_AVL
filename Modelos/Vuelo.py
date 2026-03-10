class Vuelo:
    def __init__(self, id, origin, destiny, departureTime, basePrice, finalPrice, passengers, promotion, alert, height):
        self._id = id
        self._origin = origin
        self._destiny = destiny
        self._departureTime = departureTime
        self._basePrice = basePrice
        self._finalPrice = finalPrice
        self._passengers = passengers
        self._promotion = promotion
        self._alert = alert
        self._height = height
        self._parent = None
        self._leftChild = None
        self._rightChild = None

    def getId(self):
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

    def getHeight(self):
        return self._height
    
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

    def setHeight(self, height):
        self._height = height

    def setParent(self, parent):
        self._parent = parent

    def setLeftChild(self, leftChild):
        self._leftChild = leftChild

    def setRightChild(self, rightChild):
        self._rightChild = rightChild