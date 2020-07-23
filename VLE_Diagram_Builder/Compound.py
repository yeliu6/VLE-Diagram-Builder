import numpy as np

class Compound:
    # create new method to change variables based on temperature range if applicable
    def __init__(self, name, tRange, aVal, bVal, cVal, boilP, *args, **kwargs):
        self.name = name
        self.tRange = tRange
        self.aVal = aVal
        self.bVal = bVal
        self.cVal = cVal
        self.boilP = boilP

    # Desription, instance method
    def description(self):
        strTempRange = "Temperature Range (K): {}".format(self.tRange)
        strAVal = "A: {}".format(self.aVal)
        strBVal = "B: {}".format(self.bVal)
        strCVal = "C: {}".format(self.cVal)
        strBoil = "Boiling Point (K): {}".format(self.boilP)
        strDesc = strTempRange + "\n" + strAVal + "\n" + strBVal + "\n" + strCVal + "\n" + strBoil
        return strDesc

    # Method calculates bubble curve of compound, edges should be boiling points, isobaric
    def bubbleIsoBar(self, xVals, compObjList, temp, pTot):
        # IsoBaric Calculation
        Temp = temp
        tempListBub = []
        xUse = []  # which x values actually succeeded in calculation

        # pressure iterative method
        for i in range(0, len(xVals)):
            if i == 0:
                xUse.append(0)
                tPure = self.tempAntoine(pTot, compObjList[1].aVal, compObjList[1].bVal, compObjList[1].cVal )
                tempListBub.append(tPure)  # adds basis component as x=0 Temp
            elif i == len(xVals) - 1:
                xUse.append(1)
                tPure = self.tempAntoine(pTot, compObjList[0].aVal, compObjList[0].bVal, compObjList[0].cVal)
                tempListBub.append(tPure) # adds other as x=1 Temp
            else:  # else calculates using chosen method: ideal or not
                # should go until error acceptable or give message if doesn't converge
                sentry, count = 0, 0
                while sentry != 1 and count <= 10000:  # checks for either condition
                    x1 = xVals[i]
                    x2 = 1 - x1
                    vapP1 = self.vapP(Temp, compObjList[0].aVal, compObjList[0].bVal, compObjList[0].cVal)
                    vapP2 = self.vapP(Temp, compObjList[1].aVal, compObjList[1].bVal, compObjList[1].cVal)
                    calcP = x1*vapP1 + x2*vapP2

                    #calc difference
                    z = pTot - calcP
                    if z < -0.01:
                        Temp -= .01
                        count += 1
                    elif z > 0.01:
                        Temp += .01
                        count += 1
                    else:
                        xUse.append(x1)
                        tempListBub.append(float(str(Temp)[0:5]))  # only certain significant figures
                        Temp = temp  # reset
                        sentry = 1
        return xUse, tempListBub

    # except:
    #     print("Error: Bubble Point did not converge within ___ interations")
    #

    # Method calculates dew curve of compound, isobaric
    def dewIsoBar(self, yVals, compObjList, temp, pTot):
        Temp = temp
        tempListDew = []
        yUse = []
        for i in range(0, len(yVals)):
            y1 = yVals[i]
            y2 = 1 - y1
            if i == 0:
                yUse.append(0)
                tPure = self.tempAntoine(pTot, compObjList[1].aVal, compObjList[1].bVal, compObjList[1].cVal)
                tempListDew.append(tPure)  # adds basis component as x=0 Temp
            elif i == len(yVals) - 1:
                yUse.append(1)
                tPure = self.tempAntoine(pTot, compObjList[0].aVal, compObjList[0].bVal, compObjList[0].cVal)
                tempListDew.append(tPure) # adds other as x=1 Temp
            else:  # else calculates using chosen method: ideal or not
                # should go until error acceptable or give message if doesn't converge
                sentry, count = 0, 0
                while (sentry != 1 and count <= 10000):  # checks for either condition
                    vapP1 = self.vapP(Temp, compObjList[0].aVal, compObjList[0].bVal, compObjList[0].cVal)
                    vapP2 = self.vapP(Temp, compObjList[1].aVal, compObjList[1].bVal, compObjList[1].cVal)
                    dewP = 1 / (y1 / vapP1 + y2 / vapP2)
                    z = pTot - dewP  # difference
                    # print(z)
                    if (z > 0.01):
                        count += 1
                        Temp += .01
                        pass
                    elif (z < -0.01):
                        count += 1
                        Temp -= .01
                        pass
                    else:  # if passes both tests, within error range and Temperature is on bubble curve
                        yUse.append(y1)
                        tempListDew.append(float(str(Temp)[0:5]))  # only certain significant figures
                        Temp = temp  # reset
                        sentry = 1
        return yUse, tempListDew

    #calculates bubble point for isothermal conditions
    def bubbleIsoTherm(self, zVals, compObjList, temp, startP):
        bubP = []
        for i in range(0, len(zVals)):
            comp1 = zVals[i]
            comp2 = 1 - comp1
            vapP1 = self.vapP(temp, compObjList[0].aVal, compObjList[0].bVal, compObjList[0].cVal)
            vapP2 = self.vapP(temp, compObjList[1].aVal, compObjList[1].bVal, compObjList[1].cVal)
            bubP.append(comp1*vapP1 + comp2*vapP2)
        return zVals, bubP

    # calculates dew point for isothermal conditions
    def dewIsoTherm(self, zVals, compObjList, temp):
        dewP = []
        for i in range(0, len(zVals)):
            y1 = zVals[i]
            y2 = 1 - y1
            vapP1 = self.vapP(temp, compObjList[0].aVal, compObjList[0].bVal, compObjList[0].cVal)
            vapP2 = self.vapP(temp, compObjList[1].aVal, compObjList[1].bVal, compObjList[1].cVal)
            dewP.append(1 / (y1 / vapP1 + y2 / vapP2))
        return zVals, dewP

    def vapP(self, T, A, B, C):  # Calculates Vapor Pressure based on Antoine Parameters from NIST
        Pvap = 10 ** (A - (B / (T + C)))
        return Pvap

    #calculates temperature based on Antoine Equation
    def tempAntoine(self, P, A, B, C):
        tempPure = B/(A-np.log10(P))-C
        return tempPure

    # solves for gas fraction of component in ideal mixture
    def yIdeal(self, x, Pvap, Ptot):
        y = x * Pvap / Ptot
        return y

    # solves for liquid fraction in ideal mixture
    def xIdeal(self, y, Pvap, Ptot):
        x = y * Ptot / Pvap
        return x

    # solves for nonideal case: fugacity, not done
    def yNonId(self):
        pass

