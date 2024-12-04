'''
This module provides an interface for how fitness functions should interact
with solvers, as well as the definitions for a few benchmark problems
'''
import random
import os
import math
import numpy as np
from Util import binaryCounter, loadConfiguration, saveConfiguration


class FitnessFunction(object):
    '''
    An interface for a fitness function provided to ensure all required
    functions of a fitness function object are implemented
    '''
    def __init__(self, config, runNumber):
        '''
        Empty constructor, useful for fitness functions that are configuration
        and run independent
        '''
        pass

    def evaluate(self, genes):
        '''
        Empty function handle that throws an exception if not overridden.
        Given a list of genes, should return the fitness of those genes.
        '''
        raise Exception("Fitness function did not override evaluate")

    def subProblemsSolved(self, genes):
        '''
        Empty function handle that throws an exception if not overridden.
        Given a list of genes, returns a list of zeros and ones indicating
        which sub problems have been solved.  If this fitness function cannot
        be described as having subproblems, should return a list containing a
        single 1 or 0 indicating if these genes represent the global optimum.
        '''
        raise Exception("Fitness function did not override subProblemsSolved")

class TestFitnessFunction(FitnessFunction):
    def __init__(self, config, runNumber):
        hhcrsp = config['hhcrsp']

        self.w_x = hhcrsp.w_x
        self.w_y = hhcrsp.w_y
        self.w_z = hhcrsp.w_z

        self.matrixD = hhcrsp.matrixD
        self.tStart = hhcrsp.tStart
        self.tEnd = hhcrsp.tEnd
        self.p = hhcrsp.p
        self.u = hhcrsp.u

        pass

    def evaluate(self, genes):
        result = self.fitness_function(genes, self.w_x, self.w_y, self.w_z, self.matrixD, self.tStart, self.tEnd, self.u)
        return result
    
    def subProblemsSolved(self, genes):
        return [0]
    
    def fitness_function(p, w_x, w_y, w_z, d, s, e, u):
        """
        Tính toán hàm fitness của một lịch trình.

        Args:
            p: Mã hóa lịch trình.
            w_x: Trọng số của thời gian di chuyển.
            w_y: Trọng số của thời gian làm thêm.
            w_z: Trọng số của thời gian chờ đợi.
            t_v0: Thời gian bắt đầu của mỗi ca trực.
            d: Ma trận khoảng cách giữa các hoạt động.
            s: Thời gian bắt đầu sớm nhất của mỗi hoạt động.
            e: Thời gian kết thúc sớm nhất của mỗi hoạt động.
            u: Thời gian làm việc tối đa của mỗi ca trực.

        Returns:
            Giá trị fitness của lịch trình.
        """

        shifts = {}  # Tạo một dictionary để lưu các hoạt động trong từng ca trực

        # Giải mã lịch trình
        for i, activity in enumerate(p):
            shift = math.floor(activity)
            priority = activity - shift
            shifts.setdefault(shift, []).append((i, priority))

        # Sắp xếp các hoạt động trong mỗi ca trực theo mức độ ưu tiên tăng dần
        for shift in shifts:
            shifts[shift].sort(key=lambda x: x[1])

        for shift in shifts:
            print(shifts[shift])
            print("\n")
        
        # --- Thay đổi ở đây ---
        num_shifts = len(shifts) + 1  # Lấy số lượng ca trực từ dictionary shifts
        t_v0 = np.zeros(num_shifts)  # Khởi tạo mảng t_v0
        for shift in shifts:
            first_activity_in_shift = shifts[shift][0][0]  # Lấy hoạt động đầu tiên trong ca
            print(first_activity_in_shift)
            t_v0[shift] = max(0, s[first_activity_in_shift] - d[0][first_activity_in_shift]) 
        # --- Kết thúc thay đổi ---


        total_travel_time = 0
        total_overtime = 0
        total_waiting_time = 0

        for shift, activities in shifts.items():
            start_time = t_v0[shift]

            first_activity = activities[0][0]
            activity = first_activity
            next_activity = first_activity
            arrival_time = max(start_time, s[first_activity] - d[0][first_activity])

            for i in range(len(activities)):
                if i == 1 : continue
                activity = activities[i-1][0]
                next_activity = activities[i][0]

                total_travel_time += d[activity][next_activity]
                arrival_time = max(s[next_activity], arrival_time + p[activity] + d[activity][next_activity])

                wait_time = max(0, arrival_time - d[activity][next_activity] - e[activity])
                total_waiting_time += wait_time

            overtime = max(0, arrival_time + p[next_activity] + d[next_activity][0] - (start_time + u[shift]))
            total_overtime += overtime

        # Tính giá trị fitness
        fitness = w_x * total_travel_time + w_y * total_overtime + w_z * total_waiting_time
        return fitness