"""
@file    manager.py
@author  Bowen Zheng
@University of California Riverside
@date    2016-10-27

This file defines the transmission delay to each of the message
""" 

from msg import *
from channel import *
import os
import sys
import random
import math

from collections import defaultdict
import traci



class Idle(object):
    def run(self):
        pass
    
    def next(self, im, currentTime, ch):

        im.manageInbox(currentTime, ch)
        #im.manageIntersection(currentTime)
        #print(im.occupied_resource)
        temp = []
        #print(im.requestInbox)
        #print(im.occupied_resource)
        for i in im.requestInbox:
            
            if im.occupied_resource + i.resource <= im.total_resource:
                msg = Confirm(i.sender,currentTime,"manager")
                ch.send(msg,0)
                im.occupied_resource += i.resource
                if im.occupied_resource > im.max_occupied:
                    im.max_occupied = im.occupied_resource
            else:
                temp.append(i) 
        im.requestInbox = temp
        return im.idle       
 
        

class Manager(object):
    def __init__(self, name, total_resource):
        self.name = name
        self.total_resource = total_resource
 
        self.requestInbox = []
        self.occupied_resource = 0
        self.idle = Idle()
        self.currentState = self.idle
        self.max_occupied = 0
        
    def getName(self):
        return self.name
        
    def manageInbox(self, currentTime, ch):
        mList = ch.imReceive(currentTime,self)
        for c in mList:
            if type(c) is Request:
                self.requestInbox.append(c)
    def release(self, vehicle):
        
        self.occupied_resource -= vehicle.request
       
    def runStateMachine(self, currentTime, ch):
        self.currentState = self.currentState.next(self, currentTime, ch)
        self.currentState.run()
    
        
        
        
    
