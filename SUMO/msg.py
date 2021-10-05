"""
@file    msg.py
@author  Bowen Zheng
@University of California Riverside
@date    2016-10-27

This file defines messages for intersection management
"""

class Message(object):
    """The base calss for all messages"""
    def __init__(self, sender, sendTime, resource, time_range, send_type):
        self.sender = sender
        self.sendTime = sendTime
        self.resource = resource
        self.time_range = time_range
        self.send_type = send_type
    '''
    def isValid(self, currentTime) :
        if self.sendTime + self.timeout > currentTime :
            return True
        else:
            return False
    '''        
    def getSender(self):
        return self.sender
        
    def getresource(self):
        return self.resource
        
    def getSendTime(self):
        return self.sendTime
        
    def gettime_range(self):
        return self.time_range


class Request(Message):
    """The Request message sent by vehicles"""
    #def __init__(self, id, sender, receiver, sendTime, timeout, expArrTime, isFront, roadID, destRoad, location, routeID):
    def __init__(self, sender, sendTime, resource, time_range, send_type):
        Message.__init__(self, sender, sendTime, resource, time_range, send_type)
        #self.expArrTime = expArrTime #expected arriving time
        #self.isFront = isFront
        #self.destRoad = destRoad #add 06-13-2017
        #self.location = location #add 06-13-2017
        #self.routeID = routeID
        

        
        
class Confirm(Message):
    """The Confirm message sent ty intersection manager"""
    def __init__(self, sender, sendTime, send_type):
        #Message.__init__(self, id, sender, receiver, sendTime, timeout)
        self.sender = sender
        self.sendTime = sendTime 
        self.send_type = send_type
        
        