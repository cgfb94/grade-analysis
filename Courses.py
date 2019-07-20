import json
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Course(object):
    """
    Hold information about single course taken from file for further analysis
    """

    def __init__(self, code, name, grade, ects, date, passed):
        self.code = code
        self.name = name
        self.grade = grade
        self.ects = int(ects)
        self.date = date
        self.passed = passed


class Student(object):
    """
    Reads data from JSON file and creates instances of Course objects to hold relevant data

    Methods:
    rolling_average(time_list) : average grade so far returned in list
    plot_grades : plots series of grades and some trend lines
    plot_dist : plots distribution of grades in histogram
    plot_subjects: parses course codes to separate subjects, plots histogram
    """
    def __init__(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.name = filename
        self.courses = [
            Course(g['course']['code'], g['course']['nameEn'], g['results'][0]['grade'], g['results'][0]['ects'],
                   g['results'][0]['examDate'], g['results'][0]['isPassed']) for g in data['grades']]

    def rolling_average(self, time_list):
        averages = []
        for i in range(len(time_list)):
            averages.append(sum(time_list[:i + 1]) / (i + 1))

        return averages

    def plot_grades(self):
        x, y = [], []
        for course in self.courses:
            try:
                if course.passed:
                    for _ in range(course.ects):
                        y.append(float(course.grade))
                        x.append(dt.datetime.strptime(course.date, '%Y-%m-%d').date())
            except:
                pass
        xx = mdates.date2num(x)
        m, a = np.polyfit(xx, y, 1)

        datetime = pd.to_datetime(x)
        series = pd.Series(y, index=datetime)
        series.sort_index(inplace=True)
        # monthly = series.groupby(series.index.map(lambda t: t.month))
        monthly = series.resample('3M').mean()
        rollingaverage = self.rolling_average(series.values)
        print(self.name)
        print(np.mean(y))

        linx = np.linspace(min(xx), max(xx), len(xx))
        plt.figure(figsize=(10, 10))
        plt.ylim([0, 10])
        plt.grid()
        plt.plot(series.index.values, rollingaverage, label='Rolling Average')
        # plt.plot(x, xx * m + a, label='Straight Fit: %2.6f' % m)
        plt.plot(monthly, label='3 Month Average')
        plt.scatter(x, y, s=100, alpha=0.2, label='Course: %s' % self.name)
        plt.xlabel('Date')
        plt.ylabel('Grade out of 10')
        plt.title('Grade Time Series')
        plt.legend()
        plt.show()

    def plot_dist(self):
        grades = []
        for course in self.courses:
            try:
                if course.passed:
                    for _ in range(course.ects):
                        grades.append(float(course.grade))
            except:
                pass

        plt.hist(grades, np.arange(6, 11, 0.5), align='left', alpha=0.5, label="Grades of %s" % self.name)

    def hist(self, grade_list):
        grades = []
        for course in grade_list:
            try:
                if course.passed:
                    for _ in range(course.ects):
                        grades.append(float(course.grade))
            except:
                pass

        return grades

    def plot_subjects(self):
        physics = []
        maths = []
        honours = []
        other = []
        sub_dict = {'Physics': physics, 'Math': maths, 'Honours': honours, 'Other': other}

        for course in self.courses:
            print(course.code + ': ' + course.name)
            if course.code[:2] == 'HC':
                honours.append(course)
            elif course.code[:2] == 'WI' or course.code[:4] == 'WPMA':
                maths.append(course)
            elif course.code[:2] == 'NA' or course.code[:4] == 'WBPH' or course.code[:4] == 'WPPH':
                physics.append(course)
                # print(course.name)
            else:
                other.append(course)

        xhist = []
        labels = []
        for name, subject in sub_dict.items():
            subjectx = self.hist(subject)
            xhist.append(subjectx)
            labels.append(name)
        plt.figure(figsize=(10, 10))
        plt.hist(xhist, np.arange(6, 11, 0.5), align='left', alpha=0.5)
        plt.xticks(np.arange(6, 11, 0.5))
        plt.xlabel('Grade out of 10')
        plt.ylabel('ECTS')
        plt.legend(labels)
        plt.show()


def getPoints(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    # pp.pprint(data['grades'])
    grades = [(g['course'], g['results']) for g in data['grades']]

    grades_test = [Course(g['course']['code'], g['course']['nameEn'], g['results'][0]['grade'], g['results'][0]['ects'],
                          g['results'][0]['examDate'], g['results'][0]['isPassed']) for g in data['grades']]
    # print(grades_test)
    results = []
    # pp.pprint(grades)
    for g in grades:
        results.extend(g[1])

    y = []
    x = []

    for r in results:
        # print(r)
        try:
            if r['isPassed']:
                y.append(float(r['grade']))
                x.append(dt.datetime.strptime(r['examDate'], '%Y-%m-%d').date())
        except:
            pass

    return x, y


def main():
    filenames = [
        'callum_new'
    ]

    for filename in filenames:
        student = Student(filename)
        student.plot_grades()
        plt.show()
        student.plot_dist()
        plt.show()
        student.plot_subjects()


if __name__ == '__main__':
    main()
