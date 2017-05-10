"""
Here we want to load in the csv of values, specified in the command line argument. 
We will use the data to analy
"""

import csv
import sys

if len(sys.argv) != 2:
    print("Usage: python run.py <csv_file>")

file = sys.argv[1]
scalar_cat = ['DistanceFromHome','DailyRate','HourlyRate','\xef\xbb\xbfAge','MonthlyRate','PercentSalaryHike']
categories = ['\xef\xbb\xbfAge','Attrition','DailyRate','DistanceFromHome',
    'EnvironmentSatisfaction','Gender','HourlyRate','JobLevel','JobSatisfaction',
    'MaritalStatus','MonthlyRate','NumCompaniesWorked','OverTime','PercentSalaryHike',
    'PerformanceRating','RelationshipSatisfaction','StockOptionLevel','TotalWorkingYears',
    'YearsAtCompany','YearsInCurrentRole','YearsSinceLastPromotion','YearsWithCurrManager']
mapping = {'No':0,'Yes':1,'Male':0,'Female':1,'Single':0,'Married':1,'Divorced':2}

class ProbModel():

    def convert(self):
        """
        Changes some of the fields we are interested into scalars for calculations. There are some fields
        that don't have intuitive scalings, like work department and education field
        (and I think would have to be represented with multiple binary RVs), 
        so they are left out.
        """
        for row in self.data:
            for category in row:
                if row[category] in mapping:
                    row[category] = mapping[row[category]]

    def covariance(self):
        """
        The covariance is calculated by 1/(size N)(size K)* sum N(sum K(n-E[N])(k-E[K])))
        The expectation should already be calculated as the (sum (p*x))
        Expectation method should already be run, otherwise an error will appear.
        Variance should also be run.
        """
        for cat in self.probabilities:
            if cat != 'Attrition':
                self.covariances[cat] = 0
                for x in [0,1]:
                    for sub_cat in self.probabilities[cat]:
                        self.covariances[cat] += ((float(x)-self.expectations['Attrition'])*(float(sub_cat)-self.expectations[cat])*(self.probabilities['Attrition'][x])*(self.probabilities[cat][sub_cat]))
                        #print(cat,(float(x)-self.expectations['Attrition'])*(float(sub_cat)-self.expectations[cat])*(self.probabilities['Attrition'][x])*(self.probabilities[cat][sub_cat]),self.covariances[cat])

            else:
                self.covariances[cat] = self.variances[cat]

            self.rho[cat] = self.covariances[cat]/((self.variances['Attrition']*self.variances[cat])**0.5)


    def expectation(self):
        """
        Calculates the expected value, variance, and standard deviationss for the various
        attributes
        """
        for cat in self.probabilities:
            self.expectations[cat] = 0
            self.variances[cat] = 0
            for field in self.probabilities[cat]:
                self.expectations[cat] += float(field)*self.probabilities[cat][field]

            #This is where the variance will be calculated. As of now, the variance is kind of high.
            for field in self.probabilities[cat]:
                self.variances[cat] += (float(field)**2)*self.probabilities[cat][field]
            self.variances[cat] -= self.expectations[cat]**2
            self.std_devs[cat] = self.variances[cat]**0.5

    def probability(self):
        """
        To calculate the probabilities of each possible result in an RV, we find
        the total instances of a case and divide by self.N
        """
        #The individual probabilities
        for category in categories:
            self.probabilities[category] = {}
            for row in self.data:
                try:
                    self.probabilities[category][row[category]] += 1
                except Exception:
                    self.probabilities[category][row[category]] = 1.0
            for sub_category in self.probabilities[category]:
                self.probabilities[category][sub_category] /= self.N

        #Conditional Probabilities for attrition; will be the probability of attrition given
        for category in categories:
            self.attr_cond_single[category] = {}
            for sub_category in self.probabilities[category]:
                self.attr_cond_single[category][sub_category] = 0.0
                for row in self.data:
                    if row[category] is sub_category:
                        self.attr_cond_single[category][sub_category] += row['Attrition']
                self.attr_cond_single[category][sub_category] /= self.N
                self.attr_cond_single[category][sub_category] /= self.probabilities[category][sub_category]


    def __init__(self,file):
        self.probabilities = {}
        self.attr_cond_single = {}
        self.expectations = {}
        self.variances = {}
        self.std_devs = {}
        self.covariances = {}
        self.rho = {}

        with open(file,'r') as f:
            r = csv.DictReader(f)
            self.data = [x for x in r]
            self.N = len(self.data)
            print("Categories: " + str([x for x in self.data[0]]))
            print("Mapping Reference: "+ str(mapping))

            self.convert()
            self.probability()
            self.expectation()
            self.covariance()
            

if __name__ == '__main__':
    """
    If you want to use the model for stuff like 
    """
    p = ProbModel(file)
    print("\nSome Probabilities:")
    for x in categories:
        if x not in scalar_cat:
            print(str(x),str(p.probabilities[x]))

    print("\nSome Conditionals:")
    for x in categories:
        if x not in scalar_cat:
            print(str(x),str(p.attr_cond_single[x]))

    print("\nExpectations:")
    for x in categories:
        print(str(x),str(p.expectations[x]))

    print("\nVariances:")
    for x in categories:
        print(str(x),str(p.variances[x]))

    print("\nStandard Deviations:")
    for x in categories:
        print(str(x),str(p.std_devs[x]))
        
    print("\nCovariances:")
    for x in categories:
        print(str(x),str(p.covariances[x]))

    print("\nRho:")
    for x in categories:
        print(str(x),str(p.rho[x]))