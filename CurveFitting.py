# -*- coding: utf-8 -*-
"""
This project analyzes the control approach for Optima pumps, based on the competitor's algorithm
It uses the data from the prototype tests, fits a curve with two different approach and plots them on a graph
"""


import Database as db
import math
import numpy as np
import matplotlib.pyplot as plt
import time


FLOW_INCREMENT_STEP = 0.1
EEI_CALCULATION_STEP = 0.1
GRAPH_STEP = 0.5

GROUP_1 = 1
GROUP_2 = 2
DOUBLE_POWER_CONTROL = True
DIRECT_LINE_CONTROL = False

# Group 1
MAX_FLOW_POINT_3_12 = (11.5, 1.77, "3/12", 4900, GROUP_1) 
MAX_FLOW_POINT_4_10 = (10, 1.4, "4/10", 4500, GROUP_1)  
MAX_FLOW_POINT_3_10 = (10, 1.31, "3/10", 4500, GROUP_1)  
MAX_FLOW_POINT_2_10 = (10, 1.31, "2/10", 4500, GROUP_1)  
MAX_FLOW_POINT_3_7 = (8.7, 0.95, "3/7", 3800, GROUP_1)    

# Group 2
MAX_FLOW_POINT_5_8 = (17.0, 1.1, "5/8", 4500, GROUP_2)  
MAX_FLOW_POINT_4_8 = (17.0, 1.11, "4/8", 4500, GROUP_2)  
MAX_FLOW_POINT_4_4 = (12.38, 0.60, "4/4", 3600, GROUP_2)  




def main():
   
    
    #findBestEEI(MAX_FLOW_POINT_3_12, True, 4.2, 6, 7.5)
    #findBestEEI(MAX_FLOW_POINT_4_10, False, 0, 0, 0)
    #findBestEEI(MAX_FLOW_POINT_3_10, False, 0, 0, 0)
    #findBestEEI(MAX_FLOW_POINT_2_10, True, 2.5, 4, 6)
    #findBestEEI(MAX_FLOW_POINT_3_7, True, 2.2, 4, 5.8)   
    
    #findBestEEI(MAX_FLOW_POINT_5_8, True, 5, 7.8, 10)
    #findBestEEI(MAX_FLOW_POINT_4_8, True, 5, 6, 10.5)
    findBestEEI(MAX_FLOW_POINT_4_4, DOUBLE_POWER_CONTROL, 4, 7, 8) 
  
    


# EFFECTS : Consumes a flow(float), head(float), groupNumber(integer)
#           and returns the calculated speed from the database's fitted curve
def calculateSpeedFromFlowAndHead(flow, head, groupNumber):
    
    parameters = [flow**3,             flow**2,             flow,                head**3, 
                  head**2,             head,                (flow**3)*head,      (flow**2)*head, 
                  flow*head,           (flow**3)*(head**2), (flow**2)*(head**2), flow*(head**2), 
                  (flow**3)*(head**3), (flow**2)*(head**3), flow*(head**3),      1]
    result = 0
    for i in range(16):
        if groupNumber == 1:
            result += parameters[i] * db.G1_Q_H_speed_curve_parameters[i]
        elif groupNumber == 2:
            result += parameters[i] * db.G2_Q_H_speed_curve_parameters[i]
    
    return result

# EFFECTS : Consumes a flow(float), input power(float), groupNumber(integer)
#           and returns the calculated head from the database's fitted curve
def calculateHeadFromFlowAndInputPower(flow, inputPower, groupNumber):
    
    parameters = [flow**3,                   flow**2,                   flow,                      inputPower**3, 
                  inputPower**2,             inputPower,                (flow**3)*inputPower,      (flow**2)*inputPower, 
                  flow*inputPower,           (flow**3)*(inputPower**2), (flow**2)*(inputPower**2), flow*(inputPower**2), 
                  (flow**3)*(inputPower**3), (flow**2)*(inputPower**3), flow*(inputPower**3),      1]
    result = 0
    for i in range(16):
        if groupNumber == 1:
            result += parameters[i] * db.G1_Q_Pelk_H_curve_parameters[i]
        elif groupNumber == 2:
            result += parameters[i] * db.G2_Q_Pelk_H_curve_parameters[i]
    
    return result

# EFFECTS : Consumes a flow(float), head(float), groupNumber(integer)
#           and returns the calculated input power from the database's fitted curve
def calculateInputPowerFromFlowAndHead(flow, head, groupNumber):
    
    parameters = [flow**3,              flow**2,             flow,                head**3, 
                  head**2,              head,                (flow**3)*head,      (flow**2)*head, 
                  flow*head,            (flow**3)*(head**2), (flow**2)*(head**2), flow*(head**2), 
                  (flow**3)*(head**3),  (flow**2)*(head**3), flow*(head**3),      1]
    result = 0
    for i in range(16):
        if groupNumber == 1:
            result += parameters[i] * db.G1_Q_H_Pelk_curve_parameters[i]
        elif groupNumber == 2:
            result += parameters[i] * db.G2_Q_H_Pelk_curve_parameters[i]

    
    return result

# EFFECTS : Consumes a flow(float), speed(float), groupNumber(integer)
#           and returns the calculated head from the database's fitted curve
def calculateHeadFromFlowAndSpeed(flow, speed, groupNumber):
    
    parameters = [flow**3,              flow**2,              flow,                 speed**3, 
                  speed**2,             speed,                (flow**3)*speed,      (flow**2)*speed, 
                  flow*speed,           (flow**3)*(speed**2), (flow**2)*(speed**2), flow*(speed**2), 
                  (flow**3)*(speed**3), (flow**2)*(speed**3), flow*(speed**3),      1]
    result = 0
    for i in range(16):
        if groupNumber == 1:
            result += parameters[i] * db.G1_Q_Speed_H_curve_parameters[i]
        elif groupNumber == 2:
            result += parameters[i] * db.G2_Q_Speed_H_curve_parameters[i]
    
    return result

# EFFECTS : Consumes a flow(float), head(float)
#           and returns the calculated torque from the database's fitted curve
def calculateTorqueFromHeadAndFlow(flow, head, groupNumber):
    
    Input_Power = calculateInputPowerFromFlowAndHead(flow, head, groupNumber)
    rpm = calculateSpeedFromFlowAndHead(flow, head, groupNumber)
    
    parameters = [Input_Power**3,            Input_Power**2,            Input_Power,               rpm**3, 
                  rpm**2,                    rpm,                       (Input_Power**3)*rpm,      (Input_Power**2)*rpm, 
                  Input_Power*rpm,           (Input_Power**3)*(rpm**2), (Input_Power**2)*(rpm**2), Input_Power*(rpm**2), 
                  (Input_Power**3)*(rpm**3), (Input_Power**2)*(rpm**3), Input_Power*(rpm**3),      1]
    result = 0
    for i in range(16):

        result += parameters[i] * db.Pelk_Speed_Torque_curve_parameters[i]
    
    return result



# EFFECTS : Consumes a max flow point tuple (size of 5), control approach (Boolean), three flow points (float)
#           and plots the graph or graphs to console based on the control approach.
def findBestEEI(maxFlowPoint, doublePowerControl, firstQ, secondQ, thirdQ):
    

    if doublePowerControl:
        
        """
             ************************************
             Double Power Control
             ************************************
        """
        speed = maxFlowPoint[3]
        groupNumber = maxFlowPoint[4]
        Qh = []
        Qh, maxPelk, maxPowerOutputPoint, EEI = createFlowHeadArrayWithDoublePowerControl(maxFlowPoint, 
                                                       firstQ, 
                                                       secondQ, 
                                                       thirdQ, 
                                                       groupNumber,
                                                       speed)
        
        firstPointOfLine = (0.0, calculateHeadFromFlowAndSpeed(0.0, speed, groupNumber), groupNumber)
        Q_H_Array, maxPower2 = createFlowHeadArray(firstPointOfLine, speed, maxFlowPoint, groupNumber)
        
        Alarko_x = []
        Alarko_y = []
        PhidList = []
        PelkList = []
        
        
        for e in Qh:
            Alarko_x.append(e[0])
            Alarko_y.append(e[1])
            PhidList.append(e[0] * e[1]* 2.72)

            PelkList.append(calculateInputPowerFromFlowAndHead(e[0], e[1], groupNumber))
                    
        
        Competitor_Excel = db.Competitor_4_4()
        
        Competitor_Flow_List = []
        Competitor_Head_List = []
        Competitor_Power_List = []
        
        for e in Competitor_Excel:
            Competitor_Flow_List.append(e[0])
            Competitor_Head_List.append(e[1])
            Competitor_Power_List.append(e[2])

        
        plt.figure(figsize = (15,5))
        
        """ SUBPLOT 1 """
        plt.subplot(1,2,1)
                    
        label = maxFlowPoint[2]
        plt.title('Flow - Head of '+label)
        plt.xlabel("Flow")
        plt.ylabel("Head")
        
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        plt.xlim(0, maxFlowPoint[0] + 0.5)
        plt.ylim(0, Competitor_Head_List[-1] + 2.5)

        plt.plot(Alarko_x, Alarko_y, 'r')

        
        plt.plot([0, maxPowerOutputPoint[0]],[maxPowerOutputPoint[1] / 2, maxPowerOutputPoint[1]], 'go-')

        QHtext = "Q= " + '%.2f'%maxPowerOutputPoint[0] + "\n" + "H= " + '%.2f'%maxPowerOutputPoint[1] + "\n" + "Pelk= " + '%.2f'%maxPelk + "\nEEI= " + '%.3f'%EEI  
        plt.text(maxPowerOutputPoint[0] - 0.5, maxPowerOutputPoint[1] - 3.5 , QHtext, fontsize = 12, weight = 'bold')
        
        """ Competitor"""
        plt.text(7, 8, "Competitor" + "\n" + "EEI: 0.194", fontsize = 12, weight = 'bold', color = 'blue')
        plt.plot(Competitor_Flow_List, Competitor_Head_List, 'b--')
        
        """ SUBPLOT 2 """
        plt.subplot(1,2,2)
        
        
        plt.title('Flow - Input Power of ' + label)
        plt.xlabel("Flow")
        plt.ylabel("Input")



        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

        plt.plot(Alarko_x, PelkList, 'r')
        plt.plot(Alarko_x, PhidList, 'orange')
        plt.plot([firstQ, firstQ], [0, 320], 'r--')
        plt.plot([secondQ, secondQ], [0, 320], 'r--')
        plt.plot([thirdQ, thirdQ], [0, 320], 'r--')
        plt.plot(maxPowerOutputPoint[0], calculateInputPowerFromFlowAndHead(maxPowerOutputPoint[0], maxPowerOutputPoint[1], groupNumber), 'go')
        plt.plot(maxPowerOutputPoint[0], maxPowerOutputPoint[0] * maxPowerOutputPoint[1] * 2.72, 'go')
        plt.xlim(0, maxFlowPoint[0] + 0.5)
        plt.ylim(0, maxPelk + 30)
        
        """ Competitor"""
        
        plt.plot(Competitor_Flow_List, Competitor_Power_List, 'b--')
        
        plt.show()
        
        

    else:
        """ 
            ************************************
            Direct Line Control
            ************************************
        """
        
        speed = maxFlowPoint[3]
        groupNumber = maxFlowPoint[4]
        
        EEI = 0.0

        firstPointOfLine = (0.0, calculateHeadFromFlowAndSpeed(0.0, speed, groupNumber), groupNumber)
    
        
        Qh = []
        
    
        Q_H_Array, maxPower = createFlowHeadArray(firstPointOfLine, speed, maxFlowPoint, groupNumber)
        
        QBreakPointList = []
        EEIList = []
        
        
        for Q_break_point in np.arange(firstPointOfLine[0], maxFlowPoint[0], FLOW_INCREMENT_STEP):
    
            (Qh, CTI_at_best_EEI, EEI) = findEEI([Q_break_point, calculateHeadFromFlowAndSpeed(Q_break_point, speed, groupNumber)], 
                                                  maxFlowPoint, 
                                                  speed, 
                                                  groupNumber)
            
            if Q_break_point % GRAPH_STEP == 0:
                
                x = []
                y = []
                PelkList = []
                
                QBreakPointList.append(Q_break_point)
                EEIList.append(EEI)
                
                
                
                for e in Qh:
                    x.append(e[0])
                    y.append(e[1])
                    PelkList.append(calculateInputPowerFromFlowAndHead(e[0], e[1], groupNumber))
                    
                def plotGraphs():
                    plt.figure(figsize=(15,5))
                    
                    
                    """ SUBPLOT 1"""
                    
                    plt.subplot(1,2,1)
                    
                    label = maxFlowPoint[2]
                    plt.title('Flow - Head of '+label)
                    plt.xlabel("Flow")
                    plt.ylabel("Head")
                    
                    
                    plt.plot(Q_H_Array[:,0], Q_H_Array[:,1], 'b--')
                    plt.plot([0, CTI_at_best_EEI[0]],[CTI_at_best_EEI[1] / 2, CTI_at_best_EEI[1]], 'go-')
                    
                    Pelk = calculateInputPowerFromFlowAndHead(CTI_at_best_EEI[0] , CTI_at_best_EEI[1], groupNumber)
                    
                    QHtext = "Q= " + '%.2f'%CTI_at_best_EEI[0] + "\n" + "H= " + '%.2f'%CTI_at_best_EEI[1] + "\n" + "Pelk= " + '%.2f'%Pelk + "\nEEI= " + '%.3f'%EEI
                    plt.text(CTI_at_best_EEI[0] + 0.5, CTI_at_best_EEI[1] + 0.5 , QHtext, fontsize = 12, weight = 'bold')
                    
        
                   
                    maxSpeedCurve = []
                    for q in np.arange(0.0, maxFlowPoint[0], 0.5):
                        maxSpeedCurve.append([q, calculateHeadFromFlowAndSpeed(q, speed, groupNumber)])
                    
                    plt.grid(b=True, which='major', color='#666666', linestyle='-')
                    plt.minorticks_on()
                    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        
                    plt.xlim(0, maxFlowPoint[0] + 0.5)
                    plt.ylim(0, firstPointOfLine[1] + 0.5)
                    plt.plot(x, y, 'r')
                                        
                    
                    """ SUBPLOT 2"""
                    
                    plt.subplot(1,2,2)
                    
                    plt.title('Flow - Input Power of ' + label)
                    plt.xlabel("Flow")
                    plt.ylabel("Input")

        
                    plt.xlim(0, maxFlowPoint[0] + 0.5)
                    plt.ylim(0, maxPower + 30)
                    plt.plot(x, PelkList, 'r')
                    plt.grid(b = True, which = 'major', color = '#666666', linestyle = '-')
                    plt.minorticks_on()
                    plt.grid(b = True, which = 'minor', color = '#999999', linestyle = '-', alpha = 0.2)
        
                    plt.show()
                    
                    print("The EEI: ", '%.3f'%EEI, " max power output at: ","(", '%.2f'%CTI_at_best_EEI[0], ",", '%.2f'%CTI_at_best_EEI[1], ",", '%.2f'%(CTI_at_best_EEI[0] * CTI_at_best_EEI[1] * 2.72),")")
                    time.sleep(0.5)
                    
                
                plotGraphs()
            
        plt.plot(QBreakPointList, EEIList, 'go-')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        
        plt.title("EEI values for max rpm:" + str(speed) + " to Qmax: " + str(maxFlowPoint[0]))
        plt.show()


# EFFECTS : Consumes the first of the line and max flow point and
#           produces flow/head values for every EEI calculation step interval, 
#           max. hydraulic power and the EEI of the curve
def findEEI(firstPointOfLine, maxFlowPoint, speed, groupNumber):
    QandH = []
    maxPowerOutPutPoint = (0,0)
    maxPowerOutput = 0.0
    # the points from the curve
    for point in np.arange(0.0, firstPointOfLine[0], EEI_CALCULATION_STEP):
        QandH.append([point, calculateHeadFromFlowAndSpeed(point, speed, groupNumber)])
    
    # the points from the line 
    for point in np.arange(firstPointOfLine[0] + EEI_CALCULATION_STEP, maxFlowPoint[0] - EEI_CALCULATION_STEP, EEI_CALCULATION_STEP):
        QandH.append([point, calculateYValueFromXInALine(point, firstPointOfLine, maxFlowPoint)])
    
    for e in QandH:
        maxPowerOutput = e[0] * e[1]
        if maxPowerOutput > maxPowerOutPutPoint[0] * maxPowerOutPutPoint[1]:
            maxPowerOutPutPoint = (e[0], e[1])
    
    return (QandH, maxPowerOutPutPoint, calculateEEI(maxPowerOutPutPoint, groupNumber))
    

# EFFECTS: consumes a QHmax point (list), groupNumber and calculates the EEI
#          The EEI calculation is based on EN 16297-2
def calculateEEI(max_Q_H_Points, groupNumber):
    
    EEI = 0.0
    
    flow = max_Q_H_Points[0]
    head = max_Q_H_Points[1]
    Pmax = flow * head * 2.72
    P2 = 1.7 * Pmax + 17 * (1 - math.exp(-0.3 * Pmax))
    
    Q100Pelk = calculateInputPowerFromFlowAndHead(flow, head, groupNumber)
    Q75Pelk = calculateInputPowerFromFlowAndHead(flow*3/4, head*7/8, groupNumber)
    Q50Pelk = calculateInputPowerFromFlowAndHead(flow*2/4, head*6/8, groupNumber)
    Q25Pelk = calculateInputPowerFromFlowAndHead(flow*1/4, head*5/8, groupNumber)

    
    P1 = 0.06 * Q100Pelk + 0.15 * Q75Pelk + 0.35 * Q50Pelk + 0.44 * Q25Pelk
    EEI = P1/P2*0.49
    
    return EEI
    



# EFFECTS : Consumes an X and two points and returns the Y value based on the line drawn between points
def calculateYValueFromXInALine(x, firstXYPair, secondXYPair):
    
    a  = (firstXYPair[1] - secondXYPair[1])/(firstXYPair[0] - secondXYPair[0])
    b = (firstXYPair[1] - a * firstXYPair[0]) 
    
    return a*x+b



# EFFECTS : Consumes head & flow values the curve's first point, a speed value, 
#           maximum flow point tuple, group number and returns an array of points derived 
#           from the speed value
def createFlowHeadArray(firstPointOfLine, speed, maxFlowPoint, groupNumber):
    
    Speed_Q_H_Tuple = []
    maxPower = 0
    
    # for every FLOW_INCREMENT_STEP from zero to max flow on the curve, 
    # we will draw a line to maxFlowPoint and calculate EEI from there
    
    for Q_break_point in np.arange(firstPointOfLine[0], maxFlowPoint[0], FLOW_INCREMENT_STEP):

        Speed_Q_H_Tuple.append((Q_break_point, calculateHeadFromFlowAndSpeed(Q_break_point, speed, groupNumber)))
        Power = calculateInputPowerFromFlowAndHead(Speed_Q_H_Tuple[-1][0], Speed_Q_H_Tuple[-1][1], groupNumber)
        
        if maxPower < Power:
            maxPower = Power

    array = np.array(Speed_Q_H_Tuple)
    
    return array, maxPower

# EFFECTS : Consumes a maximum flow point tuple, three different flow values, group number, speed
#           and returns
#               - an array of flow & head points which has 4 different parts
#               - maximum input power 
#               - maximum output power (Q * H * 2.72)
#               - and EEI value of the curve
def createFlowHeadArrayWithDoublePowerControl(maxFlowPoint, firstQ, secondQ, thirdQ, groupNumber, speed):
    
    QandH = []
    maxPowerOutputPoint = (0, 0)
    maxPowerOutput = 0.0
    
    """ First Part """
    # the first part: from Q = 0 to  firstQ 
    # follow the maximum speed curve
    
    for point in np.arange(0.0, firstQ, EEI_CALCULATION_STEP):
        QandH.append([point, calculateHeadFromFlowAndSpeed(point, speed, groupNumber)])

    """ Second Part """        
    # the second part: from Q = firstQ to secondQ
    # keep the Pelk constant
    
    firstConstantPelk = calculateInputPowerFromFlowAndHead(QandH[-1][0], QandH[-1][1], groupNumber)
    
    for point in np.arange(firstQ, secondQ, EEI_CALCULATION_STEP):
        QandH.append([point, calculateHeadFromFlowAndInputPower(point, firstConstantPelk, groupNumber)])
    
    """ Third Part """ 
    # the third part: from Q = secondQ to thirdQ
    # linearly increase power from the last QandH point to a point where its Pelk is the max.
    
    # the maximum output power for this pump
    maxPelk = calculateInputPowerFromFlowAndHead(maxFlowPoint[0], maxFlowPoint[1], groupNumber)
    # head at 3rd flow point
    headAtThirdFlowPoint = calculateHeadFromFlowAndInputPower(thirdQ, maxPelk, groupNumber)
    
    # create tuples for the points
    firstPointOfLine = (QandH[-1][0], QandH[-1][1])
    secondPointOfLine = (thirdQ, headAtThirdFlowPoint)
    
    for point in np.arange(secondQ, thirdQ, EEI_CALCULATION_STEP):
        QandH.append([point, calculateYValueFromXInALine(point, firstPointOfLine, secondPointOfLine)])
    
    
    """ Fourth Part """
    # the last part: from Q = thirdQ to maxFlow
    # keep the Pelk constant
    
    for point in np.arange(thirdQ, maxFlowPoint[0], EEI_CALCULATION_STEP):
        QandH.append([point, calculateHeadFromFlowAndInputPower(point, maxPelk, groupNumber)])
    
    for e in QandH:
        maxPowerOutput = e[0] * e[1]
        if maxPowerOutput > maxPowerOutputPoint[0] * maxPowerOutputPoint[1]:
            maxPowerOutputPoint = (e[0], e[1])
    
    return (QandH, maxPelk, maxPowerOutputPoint, calculateEEI(maxPowerOutputPoint, groupNumber))
    

if __name__ == '__main__':
    main()


