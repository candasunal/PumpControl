# -*- coding: utf-8 -*-
"""
The test suite of the pump control analysis. The actual values are compared with calculated values

It has accuracy values from 1%, up 10%
The best accuracy so far is 3%


"""

import CurveFitting as cf
import Database as db
import unittest
import pytest as pt
import numpy as np
import scipy.optimize as optimize

ACCURACY_01_PERCENT = 0.01
ACCURACY_02_PERCENT = 0.02
ACCURACY_03_PERCENT = 0.03
ACCURACY_05_PERCENT = 0.05
ACCURACY_10_PERCENT = 0.1

class TestCurveFitting(unittest.TestCase):
    
    def testG1_5000rpmHeadFromLine(self):
        self.assertEqual(cf.calculateYValueFromXInALine(2.5, [0,5], [5,0]), 2.5)
        self.assertEqual(cf.calculateYValueFromXInALine(1, [0,5], [5,0]), 4)
        self.assertEqual(cf.calculateYValueFromXInALine(7.5, [6.5, -1.5], [10.5, 1.5]), -0.75)
        
        
    def testG1_5000rpmHeadFromCurve(self):
        assert G1_5000rpmHeadFromCurve(8.329) == pt.approx(8.081, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(0.00) == pt.approx(12.40, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(3.02) == pt.approx(11.41, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(9.30) == pt.approx(6.91, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(7.04) == pt.approx(9.26, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(10.36) == pt.approx(5.45, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(2.14) == pt.approx(11.66, ACCURACY_01_PERCENT)
        assert G1_5000rpmHeadFromCurve(4.07) == pt.approx(11.07, ACCURACY_01_PERCENT)
        
        
    
    def testG1_Speed(self):
        assert cf.calculateSpeedFromFlowAndHead(5.2, 10.11, 1) == pt.approx(4900, ACCURACY_01_PERCENT)
        assert cf.calculateSpeedFromFlowAndHead(8.5, 0.95, 1) == pt.approx(3400, ACCURACY_01_PERCENT)
        assert cf.calculateSpeedFromFlowAndHead(7.284, 5.393, 1) == pt.approx(4200, ACCURACY_01_PERCENT)
        assert cf.calculateSpeedFromFlowAndHead(9.08, 6.56, 1) == pt.approx(4870, ACCURACY_01_PERCENT)

        
    def testG1_Pelk(self):
        assert cf.calculateInputPowerFromFlowAndHead(7.28, 5.39, 1) == pt.approx(231, ACCURACY_01_PERCENT)    # 4200 rpm
        assert cf.calculateInputPowerFromFlowAndHead(0.86, 9.46, 1) == pt.approx(150, ACCURACY_02_PERCENT)    # 4450 rpm
        assert cf.calculateInputPowerFromFlowAndHead(7.61, 1.23, 1) == pt.approx(107, ACCURACY_03_PERCENT)    # 3200 rpm
        assert cf.calculateInputPowerFromFlowAndHead(4.92, 4.51, 1) == pt.approx(129.2, ACCURACY_01_PERCENT)  # 3500 rpm
        
    def testG1_calculateEEI(self):
        assert cf.calculateEEI([8.329 , G1_5000rpmHeadFromCurve(8.329)], 1) == pt.approx(0.228, ACCURACY_01_PERCENT)
        assert cf.calculateEEI([7.967 , 7.508], 1) == pt.approx(0.227, ACCURACY_01_PERCENT)



"""
************************************** HELPER FUNCTIONS ****************************************
"""

# Consumes a flow value and returns the head at point Q from Group1 5000rpm points
def G1_5000rpmHeadFromCurve(Q):
    
    result = 0
    i = len(Q_H_5000rpm_curve_parameters) - 1

    for parameter in Q_H_5000rpm_curve_parameters:
        result += parameter * (Q**i)
        i -= 1

    return result

# Consumes a flow value and returns the head at point Q from Group1 4900rpm points
def G1_4900rpmHeadFromCurve(Q):
    
    result = 0
    i = len(db.Q_H_4900rpm_curve_parameters) - 1

    for parameter in db.Q_H_4900rpm_curve_parameters:
        result += parameter * (Q**i)
        i -= 1

    return result

"""
    Finding the head by given flow at 5000 rpm
"""
G1_Q_H_5000rpm = np.array(db.G1_Q_H_Pelk_5000rpm)

G1_Q_H_5000rpm_guess = (1, 1, 1, 1, 1, 1)

Q_H_5000rpm_curve_parameters, popt = optimize.curve_fit(db.Q_H_curve_fit, G1_Q_H_5000rpm[:,:1], G1_Q_H_5000rpm[:,1], G1_Q_H_5000rpm_guess)




        
if __name__ == '__main__':
    unittest.main()