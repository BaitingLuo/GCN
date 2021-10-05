from msg import *

class Channel(object):
    """The tranmission of messages"""
    def __init__(self):
        self.messageList = []
    
    def send(self, msg, delay): 
        #the message and the correponding tranmission delay to it
        #assert issubclass(type(msg), Message), "msg is not of class Message"
        self.messageList.append((msg, delay))
        
    def vReceive(self, currentTime, vehicle):
        #the message can be delivered at this time for vehicle
        outlist = []
        received = []
      
        for i in self.messageList:

            if(i[0].sendTime + i[1] <= currentTime and vehicle.name == i[0].sender and i[0].send_type == "manager"):
                outlist.append(i[0])
                received.append(i)
        a = [x for x in self.messageList if x not in received]
        self.messageList = a
       
        return outlist
        
    def imReceive(self, currentTime, manager):
        #the message can be delivered at this time for manager
        outlist = []
        received = []
        for i in self.messageList:
            if(i[0].sendTime + i[1] <= currentTime and i[0].send_type == "vehicle"):
                outlist.append(i[0])
                received.append(i)
        a = [x for x in self.messageList if x not in received]
        self.messageList = a
        
        return outlist       
        
    def printMessageList():
        print (self.messageList)