
import os
import sys
import random
import math
from msg import *
from xml.dom import minidom
import traci
#PORT = 8873

class Vtype(object):
    """defines the vehicle types"""
    def __init__(self, name, accel, decel, sigma, length, minGap, maxSpeed, guiShape):
        self.name = name
        self.accel = accel
        self.decel = decel
        self.sigma = sigma
        self.length = length
        self.minGap = minGap
        self.maxSpeed = maxSpeed
        self.guiShape = guiShape



#state classes defined for vehicle
class ApproachingNotConfirmed(object):
    """vehicle is approaching the intersection but does not receive confirmation"""
    def __init__(self, currentTime):
        self.name = 'ApproachingNotConfirmed'
        self.enteringTime = currentTime
        #self.timeDiff = setting.resend_timeout

    def estimateArrTime(self, vehicle, currentTime, position, laneLength, speed):
        if speed == 0:
            return float("inf")
        result = ((laneLength - position) / speed + currentTime)
        if result <= currentTime:
            vehicle.arrived == True
            vehicle.arriveTime = currentTime
        return ((laneLength - position) / speed + currentTime)
        
    #calculte the requested recource
    def request_resource(self,vehicle):
        #index = random.randint(0,2)
        #self_resource_type = [0.3,0.5,0.8]
        sr = vehicle.self_resource
        if vehicle.vtype.name != "sybil":
            V_curr = traci.vehicle.getSpeed(vehicle.name)
            V_max = traci.vehicle.getMaxSpeed(vehicle.name)
            N = max((V_max - V_max*sr)/V_max,0)
        else:
            N = 1 - sr
        #N = max((V_curr - V_max*sr)/V_max,0)
        
        return N
        
    def run(self, vehicle):
        pass        
        #approaching the intersection
        #controlled by SUMO

        
    def next(self, currentTime, ch, vehicle):
        if vehicle.vtype.name != "sybil":
            #trueTime = traci.simulation.getCurrentTime() * 0.001
            #if current > vehicle.departTime + setting.precision and traci.vehicle.getLaneID(vehicle.getName()) != '':
                #estimate the arriving time for this state
            position = traci.vehicle.getDistance(vehicle.name)
                #laneID = traci.vehicle.getLaneID(vehicle.getName())
           
            laneLength = 1000
            #laneSpeedMax = traci.lane.getMaxSpeed(laneID) 
            speed = traci.vehicle.getSpeed(vehicle.name) 
                #crossPos = laneLength - vehicle.vtype.minGap - laneSpeedMax * laneSpeedMax / (2 * vehicle.vtype.decel)
            estArrTime = self.estimateArrTime(vehicle, currentTime, position, laneLength, speed)

            if vehicle.arrived == False:
                t_est = estArrTime
            else:
                t_est = vehicle.arriveTime 

            if ((laneLength - position)  > 0) and (vehicle.sent == False):
                resource = self.request_resource(vehicle)
           
                vehicle.request = resource
                vehicle.sendRequest(currentTime, ch, resource, t_est)
                vehicle.sent = True
                       
                #receiving confirmation
            if vehicle.receiveConfirm(currentTime, ch):
                #vehicle.approachingConfirmed.enteringTime = currentTime
                vehicle.time_get = traci.simulation.getTime()
                if vehicle.vtype.name == "sybil":
                    traci.vehicle.setColor(vehicle.name,(0, 0, 204)) #dark blue
                elif vehicle.vtype.name == "malicious":
                    traci.vehicle.setColor(vehicle.name,(153, 0, 204)) #dark purple
                else:
                    traci.vehicle.setColor(vehicle.name,(60, 179, 113)) #green rgb value
                return vehicle.approachingConfirmed
            else:
                if laneLength - position <= 0:
                    return vehicle.NotConfirmed
                else:
                    return vehicle.approachingNotConfirmed
        else:
            if vehicle.sent == False:
                resource = self.request_resource(vehicle)
                vehicle.request = resource
                vehicle.sendRequest(currentTime, ch, resource, 0)
                vehicle.sent = True               

            if vehicle.receiveConfirm(currentTime, ch):
                vehicle.time_get = traci.simulation.getTime()
                return vehicle.approachingConfirmed
            else:
                return vehicle.NotConfirmed
                

class ApproachingConfirmed(object):
    """vehicle is approaching the intersection and received confirmation"""
    def __init__(self):
        #self.enteringTime = 0
        #self.timeDiff = setting.resend_timeout
        self.name = "ApproachingConfirmed"
    def run(self, vehicle):
        if vehicle.vtype.name != "sybil":
            traci.vehicle.setMaxSpeed(vehicle.name, vehicle.vtype.maxSpeed)
            pass
        #approaching the intersection
        #controlled by SUMO
        else:
            pass
        

class NotConfirmed(object):
    """vehicle does not receive confirmation"""
    def __init__(self):
        self.name = "NotConfirmed"
    def run(self, vehicle):
        #traci.vehicle.setMaxSpeed(vehicle.name, vehicle.self_resource * vehicle.vtype.maxSpeed)
        if vehicle.vtype.name == "weak":
            traci.vehicle.setColor(vehicle.name,(238, 130, 238))
        elif vehicle.vtype.name == "malicious":
            traci.vehicle.setColor(vehicle.name,(229, 204, 255))
        if (vehicle.vtype.name != "sybil") and (vehicle.helped == False):
            traci.vehicle.slowDown(vehicle.name, vehicle.self_resource * vehicle.vtype.maxSpeed, 3)
            #purple 
            pass
        pass
        #approaching the intersection
        #controlled by SUMO
    def next(self, currentTime, ch, vehicle):
        if vehicle.vtype.name != "sybil":
            if vehicle.receiveConfirm(currentTime, ch):
                #vehicle.approachingConfirmed.enteringTime = currentTime
                vehicle.time_get = traci.simulation.getTime()
                if vehicle.vtype.name == "malicious":
                    traci.vehicle.setColor(vehicle.name,(153, 0, 204))
                else:
                    traci.vehicle.setColor(vehicle.name,(60, 179, 113)) #green rgb value
                return vehicle.approachingConfirmed
                #potential issue: not confirm until leaving
            else:
                return vehicle.NotConfirmed
        else:
            #print("check",vehicle.name)
            if vehicle.receiveConfirm(currentTime, ch):
                #print("check finish",vehicle.name)
                #vehicle.approachingConfirmed.enteringTime = currentTime
                vehicle.time_get = traci.simulation.getTime()            
                return vehicle.approachingConfirmed
            else:
                return vehicle.NotConfirmed

class Vehicle(object):
    """defines the vehicles in the system"""
    def __init__(self, name, vtype, route, departTime, departSpeed, departLane, self_resource):
        assert type(vtype) is Vtype, "vtype is not class Vtype"
        self.name = name
        self.self_resource = self_resource
        self.request = 0
        self.time_get = float('inf')
        self.vtype = vtype #class Vtype
        self.route = route
        self.departTime = departTime
        self.departSpeed = departSpeed
        self.departLane = departLane
        self.arrived = False
        self.arriveTime = 0
        self.approachingNotConfirmed = ApproachingNotConfirmed(departTime)
        self.sent = False
        self.approachingConfirmed = ApproachingConfirmed()
        self.NotConfirmed = NotConfirmed()
        #self.enterIntersection = EnterIntersection()
        self.currentState = self.approachingNotConfirmed
        self.current_lane = "no"
        self.helped = False
        
    '''    
    def getName(self):
        return self.name
        
    def getVtype(self):
        return self.vtype.name
        
    def getRoute(self):
        return self.route
        
    def getDepartTime(self):
        return self.departTime
    
    def getDepartSpeed(self):
        return self.departSpeed
    '''    
    
    #sending messages    
    def sendRequest(self, currentTime, ch, resource, time_range): #ch: channel
        r = Request(self.name, currentTime, resource, time_range, "vehicle")
        ch.send(r,0)
        #self.mID = self.mID + 1

    def receiveConfirm(self, currentTime, ch):
        mList = []
        #assert type(ch) is Channel, "ch is not of class Channel"
        mList = ch.vReceive(currentTime, self)
        if len(mList) > 0:
            return True
        else:
            return False
 
    
    def runStateMachine(self, currentTime, ch):
        if self.currentState.name != "ApproachingConfirmed":
            self.currentState = self.currentState.next(currentTime, ch, self)
            #print(self.currentState.name)
            self.currentState.run(self)
            return True
        else:
            return False
        
        
        
    
