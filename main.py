import pandas as pd
import numpy as np
import mcmcAllotter as mca
import argparse

parser = argparse.ArgumentParser(description='MCMC based teaching assistant allocation')
parser.add_argument('-coursesRequirements', type=str, default='data/courseFile.csv', help='Path to courses requirements file')
parser.add_argument('-studentPreferences', type=str, default='data/studentsFile.csv', help='Path to student preferences file')
parser.add_argument('-costWeights', nargs='+', type=float, default=[-1.0, 1.0, 1.0], help='Weightages for [Preference, Previous grade for the preference, CPI distribution]')
parser.add_argument('-choiceIndices', nargs='+', type=float, default=[0, 1, 2, 3, 4, 5],help='Indices of preference; 1-First, 2-Second...')
parser.add_argument('-choiceWeights', nargs='+', type=float, default=[10, 1, 2, 3, 4, 5], help='Weightages for preferences; 1-Most desired, 10-least desired')
parser.add_argument('-seed', type=float, default=2**13 - 1, help='Path to student preferences file')
parser.add_argument('-iterations', type=int, default=100, help='Path to student preferences file')
args = parser.parse_args()

np.random.seed(args.seed)

coursesDF = pd.read_csv(args.coursesRequirements)
studentsDF = pd.read_csv(args.studentPreferences)

courseCount = len(coursesDF.index)
studentCount = len(studentsDF.index)
cpiArray = studentsDF['CPI']
times = np.array(coursesDF['CourseNeeds'])

choiceIdx = mca.makeArray(studentCount, studentsDF, courseCount, coursesDF, args.choiceIndices)
choiceWeights = mca.makeArray(studentCount, studentsDF, courseCount, coursesDF, args.choiceWeights)

initialAllotment = mca.allotment(studentCount, courseCount, times)

choiceGoodnessOld, cpiGoodnessOld = initialAllotment.calcGoodness(choiceWeights, cpiArray)

finalAllottment, utility = mca.runMCMC(initialAllotment, args.iterations, studentCount, courseCount, args.costWeights, choiceIdx, choiceWeights, studentsDF, cpiArray)

choiceGoodnessNew, cpiGoodnessNew = finalAllottment.calcGoodness(choiceWeights, cpiArray)

mca.writePerformance(finalAllottment, choiceGoodnessOld, cpiGoodnessOld, choiceGoodnessNew, cpiGoodnessNew, utility)