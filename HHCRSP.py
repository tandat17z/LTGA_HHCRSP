import random
import json
import os

class HHCRSP(object):
    def __init__(self, config):
        self.numActivities = config['numActivities']
        self.numShifts = config['numShifts']

        id = int(config['problemId'])
        data_file = self.getDataJsonFile(id)
        if os.path.exists(data_file):
            self.load(data_file)
            return
        
        #----------------random problem----------------------------------------------------
        THRESHOLD = config['THRESHOLD']
        MAX_D = config['MAX_D']
        MAX_P = config['MAX_P']

        MAX_START = config['MAX_START']
        MAX_WINDOW = config['MAX_WINDOW_SIZE']
        MAX_DURATION = config['MAX_DURATION']

        self.matrixQ = [[int(random.random() > THRESHOLD) for j in range(self.numShifts + 1)] for i in range(self.numActivities + 1)]
        self.matrixD = [[random.randint(1, MAX_D) if i != j else 0 for j in range(self.numActivities + 1)] for i in range(self.numActivities + 1)]

        self.tStart = [random.randint(0, MAX_START) for _ in range(self.numActivities + 1)]
        self.tEnd = [self.tStart[i] + random.randint(1, MAX_WINDOW) for i in range(self.numActivities + 1)]
        self.p = [random.randint(1, MAX_P) for _ in range(self.numActivities + 1)]
        self.u = [random.randint(1, MAX_DURATION) for _ in range(self.numShifts + 1)]

        self.w_x = config['w_x']
        self.w_y = config['w_y']
        self.w_z = config['w_z']

        self.lookUpFeasibleShifts = {}

        self.w_dependency = config['w_dependency']

        #--------------save problem ----------------------------------------------------------
        self.save(id)
        with open(self.getDataTxtFile(id), 'w') as file:
            file.write(str(self))

    def __str__(self):
        s = '--------------DESCRIPTION HHCRSP-----------------------------------\n'
        s += "n = %d, v = %d  \n" % (self.numActivities, self.numShifts)
        s += "matrixQ: " + str(self.matrixQ) + '\n'
        s += "matrixD: " + str(self.matrixD) + '\n'
        s += '--------\n'
        for i in range(self.numActivities):
            activity_id = (i + 1)
            str_activity = "activity %d: " % (activity_id)

            for j in self.getFeasibleShifts(activity_id - 1):
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
            # if self.matrixQ[n][v] == 1:
                shifts.append(v + 1)
        return shifts
    
    def getDataJsonFile(self, problemId):
        return 'dataset/hhcrsp_%d_%d_%d.json' % (self.numActivities, self.numShifts, problemId)
    
    def getDataTxtFile(self, problemId):
        return 'dataset/hhcrsp_%d_%d_%d.txt' % (self.numActivities, self.numShifts, problemId)
    
    #-----------------------------------------------------------------------------------------------
    def load(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        self.numActivities = data['N']
        self.numShifts = data['V']
        self.matrixQ = data['matrixQ']
        self.matrixD = data['matrixD']
        self.tStart = data['tStart']
        self.tEnd = data['eEnd']
        self.p = data['p']
        self.u = data['u']

        self.w_x = data['w_x']
        self.w_y = data['w_y']
        self.w_z = data['w_z']
        self.w_dependency = data['w_dependency']

    def save(self, id):
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

        output_file = self.getDataJsonFile(id)
        with open(output_file, "w") as f:
            json.dump(data, f)