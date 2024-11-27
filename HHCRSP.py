import random

class HHCRSP(object):
    def __init__(self, config):
        threshold = config['THRESHOLD']
        max_d = config['MAX_D']
        max_p = config['MAX_P']

        max_start = config['MAX_START']
        max_window = config['MAX_WINDOW_SIZE']
        maxDuration = config['MAX_DURATION']

        self.n = config['dimensions']
        self.v = config['numberOfShifts']

        self.matrixQ = [[int(random.random() > threshold) for j in range(self.v)] for i in range(self.n)]
        self.matrixD = [[random.randint(0, max_d) for j in range(self.n)] for i in range(self.n)]

        self.tStart = [random.randint(0, max_start) for _ in range(self.n)]
        self.tEnd = [self.tStart[i] + random.randint(1, max_window) for i in range(self.n)]
        self.p = [random.randint(1, max_p) for _ in range(self.n)]
        self.u = [random.randint(1, maxDuration) for _ in range(self.v)]

        self.w_x = config['w_x']
        self.w_y = config['w_y']
        self.w_z = config['w_z']

        self.lookUpFeasibleShifts = {}

    def __str__(self):
        s = "n = %d, v = %d  \n" % (self.n, self.v)
        s += "matrixQ: " + str(self.matrixQ) + '\n'
        s += '------------------------------\n'
        for i in range(self.n):
            str_activity = "activity %d: " % (i + 1)

            for j in self.getFeasibleShifts(i):
                str_activity += str(j) + " "
            str_activity += '\n'

            str_activity += "\t p = %d  s = %d -->  e = %d \n" % (self.p[i], self.tStart[i], self.tEnd[i])
            s += str_activity

        s += '------------------------------\n'
        for i in range(self.v):
            s += "shift %d -- u = %d \n" % (i + 1, self.u[i])
        return s
    
    def getFeasibleShifts(self, n):
        shifts = []
        for v in range(self.v):
            if self.matrixQ[n - 1][v] == 1:
                shifts.append(v)
        return shifts