import pandas as pd
import numpy as np
import pickle

class allotment(object):
    """An allotment class"""
    def __init__(self, studentCount, courseCount, times):
        super(allotment, self).__init__()
        self.studentCount = studentCount
        self.courseCount = courseCount
        self.times = times
        self.data = np.eye(studentCount)
        self.squeeze()
    
    def squeeze(self):
        dataHolder = np.zeros((self.studentCount, self.courseCount))
        start = 0
        for i in range(self.courseCount):
            stop = start + self.times[i]
            dataHolder[:,i] = (np.sum(self.data[:,start:stop], 1)).ravel()
            start = stop
        self.data = np.array(dataHolder, dtype=np.int64)

    def calcGoodness(self, choiceWeights, cpiArray):
        a = self.data*choiceWeights
        b = np.ma.masked_where(a == 0, a)
        choiceGoodness = np.array(np.nanmean(b, 1), dtype=np.float)
        cpiRepeated = (np.array([cpiArray, ]*self.courseCount)).transpose()
        SvC_cpi = self.data * cpiRepeated
        b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
        cpiGoodness = np.array(np.nanmean(b, 0), dtype=np.float)
        return choiceGoodness, cpiGoodness

    def swapRows(self):
        swapId1 = np.random.randint(0, self.studentCount-1)
        swapId2 = np.random.randint(0, self.studentCount-1)
        temp = self.data.copy()
        tempVar = temp[swapId1,:].copy()
        temp[swapId1,:] = temp[swapId2,:]
        temp[swapId2,:] = tempVar
        return temp

def makeArray(studentCount, studentsDF, courseCount, coursesDF, weights):
    Array = np.zeros((studentCount, courseCount), dtype=np.int64) + weights[0]
    for i in np.arange(0,courseCount):
        for j in np.arange(0,studentCount):
            if coursesDF['CourseCode'][i] == studentsDF['Choice1'][j]:
                Array[j][i] = weights[1]
            elif coursesDF['CourseCode'][i] == studentsDF['Choice2'][j]:
                Array[j][i] = weights[2]
            elif coursesDF['CourseCode'][i] == studentsDF['Choice3'][j]:
                Array[j][i] = weights[3]
            elif coursesDF['CourseCode'][i] == studentsDF['Choice4'][j]:
                Array[j][i] = weights[4]
            elif coursesDF['CourseCode'][i] == studentsDF['Choice5'][j]:
                Array[j][i] = weights[5]
    return Array

def calcChoiceCost(anAllotment, SvCarray3):
    cost1 = (np.sum(anAllotment * SvCarray3))
    return cost1

def calculateVariance(cpiArray, allotment, courseCount):
    cpiRepeated = (np.array([cpiArray, ]*courseCount)).transpose()
    SvC_cpi = allotment * cpiRepeated
    b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
    a = np.array(np.nanmean(b, 0), dtype=np.float)
    variance = np.var(a)
    return variance

def allottedCourseGrade(studentCount, courseCount, studentsDF, anAllotment, SvCarray3):
    allotmentMatrix = anAllotment * SvCarray3
    temp = np.zeros((studentCount, 1))
    for i in range(studentCount):
        for j in range(courseCount):
            if(allotmentMatrix[i,j] != 0):
                if(allotmentMatrix[i,j] == 10):
                    temp[i] = 0;
                    break
                else:
                    temp[i] = studentsDF.loc[i][str("Grade"+str(allotmentMatrix[i,j]))]
                    break

    return sum(temp)

def calculateUtility(anAllotment, costWeights, SvCarray2, SvCarray3, courseCount, studentCount, studentsDF, cpiArray):
    choiceSum = calcChoiceCost(anAllotment, SvCarray3)
    cost1 = costWeights[0]*choiceSum
    cost2 = costWeights[1]*allottedCourseGrade(studentCount, courseCount, studentsDF, anAllotment, SvCarray3)
    var = calculateVariance(cpiArray, anAllotment, courseCount)
    cost3 = costWeights[2]/var
    totalUtility = cost1 + cost2 + cost3
    return totalUtility

def runMCMC(currentAllotment, nIters, studentCount, courseCount, costWeights, SvCarray2, SvCarray3, studentsDF, cpiArray):
    beta = 10*np.log10(1+studentCount)
    utility = np.zeros((nIters,1))
    for i in range(nIters):
        print(i)
        newAllotmentData = currentAllotment.swapRows()

        u1 = calculateUtility(newAllotmentData, costWeights, SvCarray2, SvCarray3, courseCount, studentCount, studentsDF, cpiArray)
        u2 = calculateUtility(currentAllotment.data, costWeights, SvCarray2, SvCarray3, courseCount, studentCount, studentsDF, cpiArray)
        utility[i] = u1;
        print(u1)
        if u1 >= u2:
            currentAllotment.data = newAllotmentData
        else:
            beta = 10*np.log10(1+i)
            probVar = np.exp(beta*(u1 - u2))
            randNum = np.random.uniform()
            if randNum < probVar:
                currentAllotment.data = newAllotmentData
            else:
                currentAllotment.data = currentAllotment.data
    return currentAllotment, utility

def writePerformance(allotment, choiceGoodnessOld, cpiGoodnessOld, choiceGoodnessNew, cpiGoodnessNew, utility):
    with open('objsWithUtility.pickle', 'wb') as f:
        pickle.dump([allotment, choiceGoodnessOld, cpiGoodnessOld, choiceGoodnessNew, cpiGoodnessNew, utility], f)