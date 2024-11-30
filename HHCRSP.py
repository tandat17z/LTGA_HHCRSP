import random
import json

class HHCRSP(object):
    def __init__(self, config):
        self.numActivities = config['dimensions']
        self.numShifts = config['numberOfShifts']
        
        threshold = config['THRESHOLD']
        max_d = config['MAX_D']
        max_p = config['MAX_P']

        max_start = config['MAX_START']
        max_window = config['MAX_WINDOW_SIZE']
        maxDuration = config['MAX_DURATION']

        self.matrixQ = [[int(random.random() > threshold) for j in range(self.numShifts)] for i in range(self.numActivities)]
        self.matrixD = [[random.randint(1, max_d) if i != j else 0 for j in range(self.numActivities)] for i in range(self.numActivities)]

        self.tStart = [random.randint(0, max_start) for _ in range(self.numActivities)]
        self.tEnd = [self.tStart[i] + random.randint(1, max_window) for i in range(self.numActivities)]
        self.p = [random.randint(1, max_p) for _ in range(self.numActivities)]
        self.u = [random.randint(1, maxDuration) for _ in range(self.numShifts)]

        self.w_x = config['w_x']
        self.w_y = config['w_y']
        self.w_z = config['w_z']

        self.lookUpFeasibleShifts = {}

        self.w_dependency = config['w_dependency']

    def __str__(self):
        s = '--------------DESCRIPTION HHCRSP-----------------------------------\n'
        s += "n = %d, v = %d  \n" % (self.numActivities, self.numShifts)
        s += "matrixQ: " + str(self.matrixQ) + '\n'
        s += "matrixD: " + str(self.matrixD) + '\n'
        s += '--------\n'
        for i in range(self.numActivities):
            activity_id = (i + 1)
            str_activity = "activity %d: " % (activity_id)

            for j in self.getFeasibleShifts(activity_id):
                str_activity += str(j) + " "
            str_activity += '\n'

            str_activity += "\t p = %d  \n\t s = %d --> e = %d \n" % (self.p[i], self.tStart[i], self.tEnd[i])
            s += str_activity

        s += '--------\n'
        for i in range(self.numShifts):
            s += "shift %d -- u = %d \n" % (i + 1, self.u[i])

        # weights
        s += "weights: \n"
        s += "\t w_x = %f , w_y = %f , w_z = %f , w_dependency = %f" % (self.w_x, self.w_y, self.w_z, self.w_dependency)
        s += "\n------------------------------------------------------------------" * 3
        return s
    
    def getFeasibleShifts(self, n):
        shifts = []
        for v in range(self.numShifts):
            if self.matrixQ[n - 1][v] == 1:
                shifts.append(v + 1)
        return shifts
    
    def save(self, num):
        data = {
            'N': self.numActivities,
            'V': self.numShifts,
            'matrixQ': self.matrixQ,
            'matrixD': self.matrixD,
            'tStart': self.tStart,
            'eEnd': self.tEnd,
            'p': self.p,
            'u': self.u,

            'w_x': self.w_x,
            'w_y': self.w_y,
            'w_z': self.w_z,
            'w_dependency': self.w_dependency
        }

        output_file = "hhcrsp/problem_%d.json" % num
        with open(output_file, "w") as f:
            json.dump(data, f)