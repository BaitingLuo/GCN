#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2020 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import math 
import numpy
import copy

from msg import *
from vehicle import *
from channel import *
from manager import *

import xml.etree.ElementTree as ET
# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

ch = Channel()
def generate_routefile(Vehicles, Malicious, normal, mali, sybi):
    random.seed(44)  # make tests reproducible
    N = 6000  # number of time steps
    # demand per second from different directions
    self_resource_type = [0.3,0.5,0.8]
  
    with open("rou.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="strong" accel="4" decel="4.5" sigma="0.5" length="5" minGap="10" maxSpeed="31.38" guiShape="passenger"/>
        <vType id="weak" accel="4" decel="4.5" sigma="0.5" length="5" minGap="10" maxSpeed="31.38" guiShape="passenger"/>
        <vType id="malicious" accel="4" decel="4.5" sigma="0.5" length="5" minGap="10" maxSpeed="31.38" guiShape="passenger"/>
        <vType id="sybil" accel="4" decel="4.5" sigma="0.5" length="5" minGap="10" maxSpeed="31.38" guiShape="passenger"/>
        <route id="main_in_main_out" edges="A1 A2 A3 A4 A5 A6 A7 A8 A9 A10" />

        <route id="main_in_side_out" edges="A1 A2 A3 A4 A5 A6 A7 A8 A9 A10" />""", file=routes)
        vehNr = 0
        type_weak = Vtype("weak", 4, 4.5, 0.5, 5, 10, 31.38, "passenger")
        type_strong = Vtype("strong", 4, 4.5, 0.5, 5, 10, 31.38, "passenger")
        type_malicious = Vtype("malicious", 4, 4.5, 0.5, 5, 10, 31.38, "passenger")
        type_sybil = Vtype("sybil", 4, 4.5, 0.5, 5, 10, 31.38, "passenger")
        for i in range(N):
            #departLane = random.randint(0,2)
            if i < 5329:
                if ((i % 5) == 0):
                    launch = random.uniform(0, 1)
                    if  0 <= launch < 0.25:
                    #elif (30/80) < random.uniform(0, 1) <= (60/80):
                    #elif (30/80) < random.uniform(0, 1) <= (65/80):
                    #elif (3/8) < random.uniform(0, 1) <= (7/8):
                    #elif (30/80) < random.uniform(0, 1) <= (75/80):
                        depart = random.randint(0,1)
                        print('<vehicle id="%s" type="strong" route="%s" depart="%f" departSpeed="0" color="1,0,0" departLane="%d" tau = "2"/>' % (
                        "MIMO"+str(vehNr), "main_in_main_out", i, depart), file = routes)
                        
                        v = Vehicle("MIMO"+str(vehNr), type_strong, "main_in_main_out", i, 10, "A0_"+str(depart), 1)
                        Vehicles["MIMO"+str(vehNr)] = v
                        normal += 1
                        vehNr += 1
                    
                    elif 0.25 <= launch <= 0.45:
                        depart = random.randint(0,1)
                        #num_sybil = random.randint(1,5)
                        num_sybil = 5
                        index = random.randint(0,2)
                        self_resource = self_resource_type[index]
                        print('<vehicle id="%s" type="malicious" route="%s" depart="%f" departSpeed="0" color="204, 153, 255" departLane="%d" tau = "2"/>' % (
                        "mali"+str(vehNr), "main_in_main_out", i, random.randint(0,1)), file = routes)
                        v = Vehicle("mali"+str(vehNr), type_malicious, "main_in_main_out", i, 10, "A0_"+str(depart), self_resource)
                        Malicious["mali"+str(vehNr)] = []
                        Vehicles["mali"+str(vehNr)] = v
                        #strategy["mali"+str(vehNr)] = random.randint(0,8)
                        name = "mali"+str(vehNr)
                        vehNr += 1
                        mali += 1
                        for j in range(num_sybil):
                            self_resource = self_resource_type[0]
                            v = Vehicle("sybi"+str(vehNr), type_sybil, "main_in_main_out", i+j+1, 10, "A0_"+str(depart), self_resource)
                            Malicious[name].append("sybi"+str(vehNr))
                            Vehicles["sybi"+str(vehNr)] = v   
                            #strategy["sybi"+str(vehNr)] = random.randint(0,8)
                            vehNr += 1
                            sybi += 1
                        '''
                        for j in range(num_sybil): 
                            index = random.randint(0,2)
                            depart = random.randint(0,1)
                            self_resource = self_resource_type[index]
                            print('<vehicle id="%s" type="sybil" route="%s" depart="%f" departSpeed="0" color="51, 153, 255" departLane="%d" tau = "2"/>' % (
                            "sybi"+str(vehNr), "main_in_main_out", i+j+1, random.randint(0,1)), file = routes)                        
                            v = Vehicle("sybi"+str(vehNr), type_sybil, "main_in_main_out", i+j+1, 10, "A0_"+str(depart), self_resource)
                            Malicious[name].append("sybi"+str(vehNr))
                            Vehicles["sybi"+str(vehNr)] = v                        
                            vehNr += 1
                        '''
                   
                    elif 0.45 < launch <= 1:
                    #elif (60/80) < random.uniform(0, 1) <= 1:
                    #elif (65/80) < random.uniform(0, 1) <= 1:
                    #elif (7/8) < random.uniform(0, 1) <= 1:
                    #elif (75/80) < random.uniform(0, 1) <= 1:
                        depart = random.randint(0,1)
                        index = random.randint(0,2)
                        print('<vehicle id="%s" type="weak" route="%s" depart="%f" departSpeed="0" color="1,1,0" departLane="%d" tau = "2"/>' % (
                        "MIMO"+str(vehNr), "main_in_main_out", i, depart), file = routes)
                        self_resource = self_resource_type[index]
                        v = Vehicle("MIMO"+str(vehNr), type_weak, "main_in_main_out", i, 10, "A0_"+str(depart), self_resource)
                        Vehicles["MIMO"+str(vehNr)] = v
                        vehNr += 1
                        normal += 1
            else:
                if ((i % 5) == 0):
                    launch = random.uniform(0, 1)
                    if  0 <= launch < 0.25:
                    #elif (30/80) < random.uniform(0, 1) <= (60/80):
                    #elif (30/80) < random.uniform(0, 1) <= (65/80):
                    #elif (3/8) < random.uniform(0, 1) <= (7/8):
                    #elif (30/80) < random.uniform(0, 1) <= (75/80):
                        depart = random.randint(0,1)
                        print('<vehicle id="%s" type="strong" route="%s" depart="%f" departSpeed="0" color="1,0,0" departLane="%d" tau = "2"/>' % (
                        "MIMO"+str(vehNr), "main_in_main_out", i, depart), file = routes)
                        
                        v = Vehicle("MIMO"+str(vehNr), type_strong, "main_in_main_out", i, 10, "A0_"+str(depart), 1)
                        Vehicles["MIMO"+str(vehNr)] = v
                        normal += 1
                        vehNr += 1
                    
                    elif 0.25 <= launch <= 0.28:
                        depart = random.randint(0,1)
                        #num_sybil = random.randint(1,5)
                        num_sybil = 5
                        index = random.randint(0,2)
                        self_resource = self_resource_type[index]
                        print('<vehicle id="%s" type="malicious" route="%s" depart="%f" departSpeed="0" color="204, 153, 255" departLane="%d" tau = "2"/>' % (
                        "mali"+str(vehNr), "main_in_main_out", i, random.randint(0,1)), file = routes)
                        v = Vehicle("mali"+str(vehNr), type_malicious, "main_in_main_out", i, 10, "A0_"+str(depart), self_resource)
                        Malicious["mali"+str(vehNr)] = []
                        Vehicles["mali"+str(vehNr)] = v
                        #strategy["mali"+str(vehNr)] = random.randint(0,8)
                        name = "mali"+str(vehNr)
                        vehNr += 1
                        mali += 1
                        for j in range(num_sybil):
                            self_resource = self_resource_type[0]
                            v = Vehicle("sybi"+str(vehNr), type_sybil, "main_in_main_out", i+j+1, 10, "A0_"+str(depart), self_resource)
                            Malicious[name].append("sybi"+str(vehNr))
                            Vehicles["sybi"+str(vehNr)] = v   
                            #strategy["sybi"+str(vehNr)] = random.randint(0,8)
                            vehNr += 1
                            sybi += 1
                        '''
                        for j in range(num_sybil): 
                            index = random.randint(0,2)
                            depart = random.randint(0,1)
                            self_resource = self_resource_type[index]
                            print('<vehicle id="%s" type="sybil" route="%s" depart="%f" departSpeed="0" color="51, 153, 255" departLane="%d" tau = "2"/>' % (
                            "sybi"+str(vehNr), "main_in_main_out", i+j+1, random.randint(0,1)), file = routes)                        
                            v = Vehicle("sybi"+str(vehNr), type_sybil, "main_in_main_out", i+j+1, 10, "A0_"+str(depart), self_resource)
                            Malicious[name].append("sybi"+str(vehNr))
                            Vehicles["sybi"+str(vehNr)] = v                        
                            vehNr += 1
                        '''
                   
                    elif 0.28 < launch <= 1:
                    #elif (60/80) < random.uniform(0, 1) <= 1:
                    #elif (65/80) < random.uniform(0, 1) <= 1:
                    #elif (7/8) < random.uniform(0, 1) <= 1:
                    #elif (75/80) < random.uniform(0, 1) <= 1:
                        depart = random.randint(0,1)
                        index = random.randint(0,2)
                        print('<vehicle id="%s" type="weak" route="%s" depart="%f" departSpeed="0" color="1,1,0" departLane="%d" tau = "2"/>' % (
                        "MIMO"+str(vehNr), "main_in_main_out", i, depart), file = routes)
                        self_resource = self_resource_type[index]
                        v = Vehicle("MIMO"+str(vehNr), type_weak, "main_in_main_out", i, 10, "A0_"+str(depart), self_resource)
                        Vehicles["MIMO"+str(vehNr)] = v
                        vehNr += 1
                        normal += 1
        print("</routes>", file=routes)
    return normal, mali, sybi
# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>


#def carx():
			#car1x=change_lane_x(mat_c1(1),mat_c1(3),mat_c1(5),vec11(loop1),loop2,loop3,t_pre,delay1);
            #mat_c1=[px_c1(i-1) py_c1(i-1) vx_c1(i-1) vy_c1(i-1) ax_c1(i-1) ay_c1(i-1)];

#uniform randomDeceleration from [0, sigma * min(accel, currentSpeed)]

def getSystemInfo(vehicles_requested, current_step):
    
    warm_up_lane = ["A1_0","A1_1"]
    for lane in warm_up_lane:
        
        vlist = traci.lane.getLastStepVehicleIDs(lane)
        if len(vlist) > 0:
            for i in vlist:
                if i not in vehicles_requested and traci.vehicle.getTypeID(i) == "weak" and traci.vehicle.getDistance(i) >= 500: 
                    vehicles_requested.append(i)
                elif i not in vehicles_requested and traci.vehicle.getTypeID(i) == "malicious" and traci.vehicle.getDistance(i) >= 500:  
                    vehicles_requested.append(i)
                #elif i not in vehicles_requested and traci.vehicle.getTypeID(i) == "sybil" and traci.vehicle.getDistance(i) >= 500:
                #    vehicles_requested.append(i)
                #vlist[0].send_request()
    
def right_drive_turnoff(ID_list):
    if ID_list != sorted(traci.vehicle.getIDList(), key=lambda v: int(v[4::])):
        ID_list = sorted(traci.vehicle.getIDList(), key=lambda v: int(v[4::]))
        traci.vehicle.setLaneChangeMode(ID_list[-1], 1557)
        
def count_vehicles(Vehicles, record_density, vehicles_arrived):
    ending_lanes = ["A4_2", "A4_1", "A4_0", "B2_0"]
    v_on_lane = []
    for lane in ending_lanes:
        v_on_lane = traci.lane.getLastStepVehicleIDs(lane)
        for vehicle in v_on_lane:
            if Vehicles[vehicle].current_lane != lane:
                Vehicles[vehicle].current_lane = lane
        
def construct_graph(v_list,graph,time, label, Vehicles, Malicious, sybil_dis, strategy, V_change):
    max_density = 130/1000
    
    for i in v_list:
        i_dis = traci.vehicle.getDistance(i)
        i_pos = traci.vehicle.getPosition(i)
        #print(i,i_pos)
        i_edge = traci.vehicle.getRoute(i)
        i_index = traci.vehicle.getRouteIndex(i)
        num_neighbor = 0
        #print(i, traci.vehicle.getRouteIndex(i))
        #print(i_edge)
        #print(i,i_pos)
        if i_dis >= 1000 and i_dis <= 10000:
            #print(i, i_dis, i_index, i_edge)
            if i[4::] not in label.keys():
                if Vehicles[i].vtype.name == "strong":
                    label[i[4::]] = [0, time]
                elif Vehicles[i].vtype.name == "weak":
                    label[i[4::]] = [0, time]
                #elif Vehicles[i].vtype.name == "sybil":
                #    label[i[4::]] = [1, time]
                elif Vehicles[i].vtype.name == "malicious":
                    label[i[4::]] = [1, time]
                    for j in Malicious[i]:
                        label[j[4::]] = [1, time]            
            if i_dis < 2000:
                search_area = [i_index,i_index+1]
            elif 8995 < i_dis < 10000:
                search_area = [i_index,i_index-1]
            else:
                search_area = [i_index-1,i_index,i_index+1]
            #print(i,traci.vehicle.getLeader(i,500))
            legitimatelist = [] 
            if Vehicles[i].vtype.name != "1":
                for index in search_area:
                    for j in traci.edge.getLastStepVehicleIDs(i_edge[index]):
                        if j == i:
                            continue
                        elif Vehicles[j].vtype.name == "1":
                            continue
                        j_pos = traci.vehicle.getPosition(j)
                        distance_diff = math.sqrt(((j_pos[0] - i_pos[0])*10)**2 + (j_pos[1] - i_pos[1])**2)
                        #print("x:",j,i,j_pos[0],i_pos[0])
                        #print("y",j,i, j_pos[1],i_pos[1])
                        if distance_diff <= 300:
                            legitimatelist.append(j)
                            if i[4::] not in graph[time].keys():
                                graph[time][i[4::]] = [[j[4::],distance_diff]]  
                                    
                                num_neighbor += 1
                            else:
                                graph[time][i[4::]].append([j[4::],distance_diff])
                                num_neighbor += 1 
            chec_list = [i] 
            sybil_cluster = []
        
            if i in Malicious.keys():
     
              
                #num_neighbor += len(Malicious[i])
                for j in Malicious[i]:
                    chec_list.append(j)
                   
                    #graph[time][j[4::]] = [[i[4::],0]]
                    if num_neighbor == 0:
                        #graph[time][j[4::]] = [[i[4::],0]]

                        if j[4::] not in sybil_dis:
                            distance = random.randint(20, 180)
                            sybil_y_pos = random.choice([58.4, 55.2])
                            sybil_x_pos = math.sqrt(distance**2 - (sybil_y_pos-i_pos[1])**2)/10
                            sybil_x_pos = random.choice([sybil_x_pos+i_pos[0],i_pos[0]-sybil_x_pos])
                            sybil_dis[j[4::]] = [distance,sybil_x_pos,sybil_y_pos]
                            V_change[j[4::]] = traci.vehicle.getSpeed(i)
                        else:
                            change = random.uniform(-2, 2)
                            sybil_dis[j[4::]][0] += change 
                            sybil_x_pos = math.sqrt(abs(sybil_dis[j[4::]][0]**2 - (sybil_dis[j[4::]][2]-i_pos[1])**2))/10
                            if sybil_dis[j[4::]][1] > i_pos[0]:
                                sybil_x_pos = sybil_x_pos + i_pos[0]
                            else:
                                sybil_x_pos = i_pos[0] - sybil_x_pos 
                            #V_change[j[4::]] = (sybil_x_pos - sybil_dis[j[4::]][1]) * 10
                           
                            sybil_dis[j[4::]][1] = sybil_x_pos
                        
                        if j[4::] not in strategy[i[4::]].keys():
                            report_choice = random.randint(0,1)
                            if report_choice == 1:
                                graph[time][i[4::]] = [[j[4::],sybil_dis[j[4::]][0]]]
                                strategy[i[4::]][j[4::]] = 1
                                #strategy[j[4::]][i[4::]] = 1
                                num_neighbor += 1
                            else:
                                strategy[i[4::]][j[4::]] = 0
                        elif strategy[i[4::]][j[4::]] == 1:
                            graph[time][i[4::]] = [[j[4::],sybil_dis[j[4::]][0]]]
                            num_neighbor += 1
                      
                        sybil_cluster.append([j[4::],sybil_dis[j[4::]]])
                        #print(j[4::], sybil_dis[j[4::]])
                        #num_neighbor += 1
                    else:
                        #graph[time][j[4::]] = graph[time][i[4::]]
                        #graph[time][j[4::]].append([i[4::],0])
                        if j[4::] not in sybil_dis:
                            distance = random.randint(20, 180)
                            sybil_y_pos = random.choice([58.4, 55.2])
                            sybil_x_pos = math.sqrt(distance**2 - (sybil_y_pos-i_pos[1])**2)/10
                           
                            sybil_x_pos = random.choice([sybil_x_pos+i_pos[0],i_pos[0]-sybil_x_pos])
                            sybil_dis[j[4::]] = [distance,sybil_x_pos,sybil_y_pos]
                            V_change[j[4::]] = traci.vehicle.getSpeed(i)
                        else:
                            change = random.uniform(-2, 2)
                            sybil_dis[j[4::]][0] += change 
                            sybil_x_pos = math.sqrt(abs(sybil_dis[j[4::]][0]**2 - (sybil_dis[j[4::]][2]-i_pos[1])**2))/10
                            if sybil_dis[j[4::]][1] > i_pos[0]:
                                sybil_x_pos = sybil_x_pos + i_pos[0]
                            else:
                                sybil_x_pos = i_pos[0] - sybil_x_pos 
                            #V_change[j[4::]] = (sybil_x_pos - sybil_dis[j[4::]][1]) * 10
                           
                            sybil_dis[j[4::]][1] = sybil_x_pos
                        if j[4::] not in strategy[i[4::]].keys():
                            report_choice = random.randint(0,1)
                            if report_choice == 1:
                                graph[time][i[4::]].append([j[4::],sybil_dis[j[4::]][0]])
                                strategy[i[4::]][j[4::]] = 1
                                #strategy[j[4::]][i[4::]] = 1
                                num_neighbor += 1
                            else:
                                strategy[i[4::]][j[4::]] = 0
                        elif strategy[i[4::]][j[4::]] == 1:
                            graph[time][i[4::]].append([j[4::],sybil_dis[j[4::]][0]])
                            num_neighbor += 1
                        #report_choice = random.randint(0,1)
                        #if report_choice == 1:
                        #    graph[time][i[4::]] = [[j[4::],sybil_dis[j[4::]][0]]]                       
                        #graph[time][i[4::]].append([j[4::],sybil_dis[j[4::]][0]])
                        #print( graph[time][i[4::]])
                        sybil_cluster.append([j[4::],sybil_dis[j[4::]]])
                        #print(j[4::], sybil_dis[j[4::]])
                        #num_neighbor += 1
                #print (i,graph[time][i[4::]])
                #print(V_change)
                for j in Malicious[i]:
                 
                    graph[time][j[4::]] = copy.deepcopy(sybil_cluster)
                    #print(j[4::],sybil_dis[j[4::]],graph[time][j[4::]])
                    graph[time][j[4::]].remove([j[4::],sybil_dis[j[4::]]])
                    removelist= []
                    for k in graph[time][j[4::]]:
                        
                        distance_diff = math.sqrt(((k[1][1] - sybil_dis[j[4::]][1])*10)**2 + (k[1][2] - sybil_dis[j[4::]][2])**2)
                        k[1] = distance_diff
                        if distance_diff > 300:
                            removelist.append(k)
                       
                    for r in removelist:
                        graph[time][j[4::]].remove(r)
                    #print(sybil_dis[i[4::]])
                    #if strategy[j[4::]][i[4::]] == None:
                    if i[4::] not in strategy[j[4::]].keys():
                        report_choice = random.randint(0,1)
                        if report_choice == 1:
                            graph[time][j[4::]].append([i[4::],sybil_dis[j[4::]][0]])
                            strategy[j[4::]][i[4::]] = 1
                            if strategy[i[4::]][j[4::]] == 0:
                                #strategy[i[4::]][j[4::]] = 1
                                if i[4::] in graph[time].keys():
                                    graph[time][i[4::]].append([j[4::],sybil_dis[j[4::]][0]])
                                else:
                                    graph[time][i[4::]] = [j[4::],sybil_dis[j[4::]][0]]
                        else:
                            strategy[j[4::]][i[4::]] = 0
                            if strategy[i[4::]][j[4::]] == 1:
                                #strategy[i[4::]][j[4::]] = 1
                                if j[4::] in graph[time].keys():
                                    graph[time][j[4::]].append([i[4::],sybil_dis[j[4::]][0]])
                                else:
                                    graph[time][j[4::]] = [i[4::],sybil_dis[j[4::]][0]]                            
                    elif strategy[j[4::]][i[4::]] == 1:
                        graph[time][j[4::]].append([i[4::],sybil_dis[j[4::]][0]])
                        
               
                    #graph[time][j[4::]].append([i[4::],sybil_dis[j[4::]][0]])
                    
                    for k in legitimatelist:
                        k_pos = traci.vehicle.getPosition(k)
                        distance_diff = math.sqrt(((k_pos[0] - sybil_dis[j[4::]][1])*10)**2 + (k_pos[1] - sybil_dis[j[4::]][2])**2)
                        if distance_diff != -1:
                            #if strategy[j[4::]][k[4::]] == None:
                            if k[4::] not in strategy[j[4::]].keys():
                                report_choice = random.randint(0,1)
                                if report_choice == 1:
                                    graph[time][j[4::]].append([k[4::],distance_diff])
                                    if k[4::] in graph[time].keys():
                                        graph[time][k[4::]].append([j[4::],distance_diff]) 
                                    else:
                                        graph[time][k[4::]] = [[j[4::],distance_diff]]
                                    strategy[j[4::]][k[4::]] = 1
                                    #strategy[k[4::]][j[4::]] = 1
                                    #strategy[j[4::]][k[4::]] = 1
                                else:
                                    strategy[j[4::]][k[4::]] = 0
                            elif strategy[j[4::]][k[4::]] == 1:
                                graph[time][j[4::]].append([k[4::],distance_diff])
                                if k[4::] in graph[time].keys():
                                    graph[time][k[4::]].append([j[4::],distance_diff]) 
                                else:
                                    graph[time][k[4::]] = [[j[4::],distance_diff]]                                
                                
                            #graph[time][j[4::]].append([k[4::],distance_diff])
                            #print([j[4::],distance_diff])
 
                            #if k[4::] in graph[time].keys():
                            #    graph[time][k[4::]].append([j[4::],distance_diff]) 
                            #else:
                            #    graph[time][k[4::]] = [[j[4::],distance_diff]]
                    
                    #print("sybil:",j[4::],graph[time][j[4::]])
                    #print(j, k[0], k[1])
                    #print(graph[time][j[4::]])
                    #print(j,graph[time][j[4::]])
            #weak = 0 strong = 0
                #print("i:",i[4::],graph[time][i[4::]])
                #print("ggggggggg")
            density_own = num_neighbor/1000
            avgSpeed_own = 31.38 - density_own/max_density * 31.38
            flow_own = avgSpeed_own * density_own
            i_speed = traci.vehicle.getSpeed(i)
            for j in chec_list:
                self_resource = Vehicles[j].self_resource
                V_type = Vehicles[j].vtype.name
                #print("sybil" == "weak" or "malicious")
                if V_type != "sybil":
                    
                    #if Vehicles[j].currentState.name == "ApproachingConfirmed":
                    #    self_resource = 1
                    self_resource = 1 - self_resource
                    if num_neighbor == 0:
                        if Vehicles[j].vtype.name == "weak":
                            graph[time][j[4::]]=[[0, self_resource, flow_own, i_speed, num_neighbor]]
                        elif Vehicles[j].vtype.name == "strong":
                            graph[time][j[4::]]=[[0, self_resource, flow_own, i_speed, num_neighbor]]
                        elif Vehicles[j].vtype.name == "malicious":
                            graph[time][j[4::]]=[[1, self_resource, flow_own, i_speed, num_neighbor]]
                    else:
                        if Vehicles[j].vtype.name == "weak":
                            graph[time][j[4::]].append([0, self_resource, flow_own, i_speed, num_neighbor])
                        elif Vehicles[j].vtype.name == "strong":
                            graph[time][j[4::]].append([0, self_resource, flow_own, i_speed, num_neighbor])
                        elif Vehicles[j].vtype.name == "malicious":
                            graph[time][j[4::]].append([1, self_resource, flow_own, i_speed, num_neighbor])
                elif "sybil" == V_type:
                    #num_neighbor = len(graph[time][j[4::]])
                    num_neighbor = 0
                    #print(strategy[j[4::]])
                    for k in strategy[j[4::]].keys():
                        if strategy[j[4::]][k] == 1:
                            num_neighbor += 1
                    #num_neighbor = len(strategy[j[4::]])
                    density_own = num_neighbor/1000
                    avgSpeed_own = 31.38 - density_own/max_density * 31.38
                    flow_own = avgSpeed_own * density_own
                    V_change[j[4::]] += random.uniform(-0.5, 0.5)
                    #if Vehicles[j].currentState.name == "ApproachingConfirmed":
                    #    self_resource = 1     
                    self_resource = 1 - self_resource
                    graph[time][j[4::]].append([1, self_resource, flow_own, V_change[j[4::]], num_neighbor])

                        #print(j,traci.vehicle.getTypeID(j))
                        
                        #graph[time][i].append([j, j.type])

                #getPosition
                #if i != j:
                    #graph[i].append(j) 
    #print(graph)

def run(Vehicles, Malicious):                                                          
    """execute the TraCI control loop"""
    step = 0
    flag = 0
    ID_list = []
    vehicles_requested = []
    record_time = {}
    record_density = {"A4_2":0, "A4_1":0, "A4_0":0, "B2_0":0}
    resource = []
    manager = Manager("manager", 1000000)
    num_weak = 0
    num_strong = 0
    num_vehicles = []
    dataset = defaultdict(list)
    graph = defaultdict(dict)
    label = {}
    sybil_dis = {}
    strategy = defaultdict(dict)
    V_change = {}
    while traci.simulation.getMinExpectedNumber() > 0:
        getSystemInfo(vehicles_requested, step)
        traci.simulationStep()
        v_list = traci.vehicle.getIDList()
        #print(vehicles_requested)
        #print(vehicles)
        if (traci.simulation.getTime().is_integer()):
            construct_graph(v_list, graph, traci.simulation.getTime(), label, Vehicles, Malicious, sybil_dis, strategy, V_change)
            
        #print(graph)
            #print(graph[traci.simulation.getTime()])
        #print(label)
      
        #print(vehicles)
        #right_drive_turnoff(ID_list)
        temp = []
        #print(traci.lane.getIDList())
        check = 0
        for i in v_list:
            if (Vehicles[i].vtype.name == "weak") or (Vehicles[i].vtype.name == "malicious"):
                if Vehicles[i].currentState.name == "ApproachingConfirmed":
                    check += Vehicles[i].request 
                if Vehicles[i].vtype.name == "malicious":
                    for j in Malicious[i]:
                        #print(j, Vehicles[j].currentState.name)
                        if Vehicles[j].currentState.name == "ApproachingConfirmed":
                            check += Vehicles[j].request
        #print("step", step, check, manager.occupied_resource)
        #print(check, manager.occupied_resource)     
        #print(vehicles_requested)
        for i in vehicles_requested:
            if Vehicles[i].vtype.name != "sybil": 
                if i not in v_list:
                    continue
            
            try:
                if Vehicles[i].runStateMachine(step, ch) == True:
                    temp.append(i)
                    #print(i)
                    '''
                    if i == "MIMO1":
                        traci.vehicle.setStop(i,"A3",pos=500)
                    if i == "MIMO4":
                        traci.vehicle.setStop(i,"A3",pos=500,laneIndex=1)
                    '''
        
                if Vehicles[i].vtype.name == "malicious":
                    #print(i,Vehicles[i].currentState.name)
                    for j in Malicious[i]:
                        #print(Vehicles[j].currentState.name)
                        if Vehicles[j].runStateMachine(step, ch) == False:
                            if (Vehicles[i].currentState == "NotConfirmed") or (Vehicles[i].currentState == "ApproachingNotConfirmed"):
                                traci.vehicle.setMaxSpeed(Vehicles[i].name, Vehicles[i].vtype.maxSpeed)
                                Vehicles[i].helped = True
                        else:
                            if j not in temp:
                                temp.append(j)
                   
            except traci.exceptions.TraCIException:
                continue   
        vehicles_requested = temp
        '''
        for i in Malicious.keys():
            if i in v_list:
                i_pos = traci.vehicle.getPosition(i)
                flag = False
                for j in Malicious[i]:
                    j_pos = traci.vehicle.getPosition(j)
                    leader = traci.vehicle.getLeader(j,50)
                    distance_diff = math.sqrt(((j_pos[0] - i_pos[0])*10)**2 + (j_pos[1] - i_pos[1])**2)
                    if (i_pos[0] - j_pos[0] > 0):
                        if distance_diff >= 450:
                            if (not leader) or (leader[1] > 10):
                                traci.vehicle.setSpeed(j, 31.38)
                                traci.vehicle.setSpeedMode(j, 30)
                            elif leader[1] <= 30:
                                traci.vehicle.setSpeed(j, -1)
                                traci.vehicle.setSpeedMode(j, 31)
                        elif 100 <= distance_diff < 450:
                            if leader and leader[1] <= 30:
                                traci.vehicle.setSpeed(j, -1)
                                traci.vehicle.setSpeedMode(j, 31)                            
                        elif distance_diff < 100:
                            traci.vehicle.setSpeed(j, -1)
                            traci.vehicle.setSpeedMode(j, 31)
                    else:
                        traci.vehicle.setSpeedMode(j, 31)
                        if distance_diff >= 450:
                                traci.vehicle.setSpeed(j, traci.vehicle.getSpeed(i)- 3)
                        elif 100 <= distance_diff < 450:
                                traci.vehicle.setSpeed(j, traci.vehicle.getSpeed(i)- 2)
                        elif distance_diff < 100:
                            traci.vehicle.setSpeed(j, -1)                  
                    #print(i,j,distance_diff,traci.vehicle.getSpeed(j))
        '''       
        for i in ["A1","A2","A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]:
            temp = []
            temp.append(i)
            road_occupancy = (traci.lane.getLastStepVehicleNumber(i+"_0")
            + traci.lane.getLastStepVehicleNumber(i+"_1"))/1000
            #maximum occupancy for 500 meters is 66 vehicles, density 66/500
            #print(i,":",road_occupancy)
            temp.append(road_occupancy)
            num_vehicle = (traci.lane.getLastStepVehicleNumber(i+"_0")+traci.lane.getLastStepVehicleNumber(i+"_1"))
            if num_vehicle == 0:
                road_segmen_speed = 0
                temp.append(road_segmen_speed)
            else:
                road_segmen_speed = (traci.lane.getLastStepMeanSpeed(i+"_0")*traci.lane.getLastStepVehicleNumber(i+"_0")
                + traci.lane.getLastStepMeanSpeed(i+"_1")*traci.lane.getLastStepVehicleNumber(i+"_1"))/num_vehicle
                #print(i,":",road_segmen_speed)
                temp.append(road_segmen_speed)
            #print(temp)
            dataset[step].append(temp)
        manager.runStateMachine(step,ch)
        vehicles_arrived = traci.simulation.getArrivedIDList()
        #print("arriced:", vehicles_arrived)
        #vehicles_departed = traci.simulation.getDepartedIDList()
        #if len(vehicles_departed) > 0:
        #    for i in vehicles_departed:
        #        if Vehicles[i].vtype.name == "weak":
        #            record_time[i] = [traci.simulation.getTime()] 
        #            num_weak += 1 
        #        else:
        #            num_strong += 1
        #print(manager.occupied_resource)     
        if len(vehicles_arrived) > 0:
            for i in vehicles_arrived:
                #print(traci.vehicle.getLaneIndex(i))
                #print(traci.vehicle.getDistance(i))
                #if Vehicles[i].vtype.name == "weak" or "sybil" or "malicious":
                #    manager.release(Vehicles[i])
               
                typename = Vehicles[i].vtype.name
                if (typename == "malicious") or (typename == "weak"):
                   
                    #print(i, Vehicles[i].currentState.name)
                    if Vehicles[i].currentState.name == "ApproachingConfirmed":
                        
                        manager.release(Vehicles[i])
                    if typename == "malicious":
                        for j in Malicious[i]:
                            #print(j, Vehicles[j].currentState.name, Vehicles[j].request)
                            if Vehicles[j].currentState.name == "ApproachingConfirmed":            
                                manager.release(Vehicles[j])
                            else:
                                vehicles_requested.remove(j)
                    #print(manager.occupied_resource)
                if len(label[i[4::]]) == 2:
                    label[i[4::]].append(traci.simulation.getTime())
                if i in Malicious.keys():
                    for j in Malicious[i]:
                        label[j[4::]].append(traci.simulation.getTime())
       
                  
        #            record_time[i].append(Vehicles[i].time_get)
        #            record_time[i].append(traci.simulation.getTime())
        #            record_time[i].append(Vehicles[i].request)
        #            num_weak -= 1
        #        else:
        #            num_strong -= 1
        #num_vehicles.append((traci.simulation.getTime(),num_weak, num_strong))
        #resource.append((traci.simulation.getTime(),manager.occupied_resource))
        #count_vehicles(Vehicles,record_density, vehicles_arrived)
        #print(graph)
        step += 1
    total_time = 0
    total_time_weak = 0
    total_time_strong = 0
    num_weak = 0
    num_strong = 0
    '''
    for key in record_time:
        total_time += (record_time[key][1]-record_time[key][0])
        if Vehicles[key].vtype.name == "weak":
            total_time_weak += (record_time[key][1]-record_time[key][0])
            num_weak += 1
        else:
            total_time_strong += (record_time[key][1]-record_time[key][0])
            num_strong += 1
    
    print("average travel time:", total_time/(len(record_time.keys())))
    print("weak average travel time:", total_time_weak/num_weak)
    print("strong average travel time:", total_time_strong/num_strong)
    '''
    #print("vehicle:", key, " time in:", record_time[key][0], " time out:", record_time[key][1])
    #with open("travel_time.txt", "w") as travel:
    #    for key in dataset:
    #        for i in dataset[key]:
    #            print("%d %s %.3f %.3f" %(key, i[0], i[1], i[2]), file = travel)

    #    for i in num_vehicles:
    #        print("%d %d %d" %(i[0],i[1], i[2]), file = travel)
    #for key in Vehicles:
    #    record_density[Vehicles[key].current_lane] += 1
    #for key in record_density:
    #    print("lane:", key, "traffic volume", record_density[key])
    #print("maximum resource occupied: ", manager.max_occupied)

    with open("label.txt", "w") as l:
        for i in label.keys():
            print("%s %s %d %d" %(i, label[i][0], label[i][1], label[i][2]), file = l)
    with open("edges.txt", "w") as e, open("feats.txt", "w") as f: 
        for i in graph.keys():
            for j in graph[i].keys(): 
                for k in graph[i][j]:
            
                    if len(k) == 2:
                        print("%s %s %.3f %d" %(j,k[0],float(k[1]),i), file = e)
                    elif len(k) == 5:
                        print("%s %d %.2f %.5f %.2f %d %d" %(j,i,k[1],k[2], k[3], k[4], k[0]), file = f)

                



    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    #generate_routefile()
    N = 0
    M = 0
    S = 0
    Vehicles = {}
    Malicious = {}
    N,M,S = generate_routefile(Vehicles, Malicious, N, M, S)
    print(N,M,S)
    precision = 0.1
    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "demo.sumocfg", "--step-length", str(precision),
                             "--tripinfo-output", "tripinfo.xml"])
                             
  
    run(Vehicles, Malicious)
