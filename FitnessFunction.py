'''
This module provides an interface for how fitness functions should interact
with solvers, as well as the definitions for a few benchmark problems
'''
import random
import os
import math
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


class FitnessFunction_HHCRSP(FitnessFunction):
    def __init__(self, config, runNumber):
        self.config = config
        hhcrsp = config['hhcrsp']

        self.numActivities = hhcrsp.numActivities
        self.numShifts = hhcrsp.numShifts

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
        result = self.fitness_function(genes, self.w_x, self.w_y, self.w_z, self.matrixD, self.tStart, self.tEnd, self.p, self.u)
        return result
    
    def subProblemsSolved(self, genes):
        return [0]
    
    def fitness_function(self, gene, w_x, w_y, w_z, d, s, e, p, u):
        """
        Args:
            p: .
            w_x: weight of travel time.
            w_y: weight of shift over time.
            w_z: weight of waiting time.
            t_v0: Thoi gian bat dau moi ca truc.
            d: Ma tran khoang cach giua cac hoat dong.
            s: Thoi gian bat dau som nhat cua moi hoat dong.
            e: Thoi gian ket thuc du tinh cua moi hoat dong.
            u: Thoi gian lam viec du tinh cua moi ca truc.

        Returns:
            fitness.
        """

        shifts = {}  # tao mot dictionary de luu cac hoat dong trong tung ca truc

        # Giai ma lich trinh
        for i, activity in enumerate(gene):
            shift = math.floor(activity)
            priority = activity - shift
            activity_id = i + 1
            shifts.setdefault(shift, []).append((activity_id, priority))

        # sap xep cac hoat dong trong moi ca truc theo muc do uu tien tang dan
        for shift in shifts:
            shifts[shift].sort(key=lambda x: x[1])

        if self.config['verbose']:
            print("--->>> Schedule --------------------------")
            for shift in shifts:
                print(shifts[shift])
            print("------------------------------------------\n")
        
        # --- Thay doi o day ---
        # num_shifts = len(shifts) + 1  # lay so luong ca truc tu dictionary shifts
        t_v0 = [0 for _ in range(self.numShifts + 1)] # khoi tao mang t_v0
        for shift in shifts:
            first_activity_in_shift = shifts[shift][0][0]  # lay hoat dong dau tien cua moi ca
            # print(first_activity_in_shift)
            t_v0[int(shift)] = max(0, s[first_activity_in_shift] - d[0][first_activity_in_shift]) 
        # --- ket thuc thay doi ---


        total_travel_time = 0
        total_overtime = 0
        total_waiting_time = 0

        for shift, activities in shifts.items():
            start_time = t_v0[int(shift)]

            first_activity = activities[0][0]
            activity = first_activity
            next_activity = first_activity
            arrival_time = max(start_time, s[first_activity] - d[0][first_activity])

            for i in range(len(activities)):
                if i == 0 : continue
                activity = activities[i-1][0]
                next_activity = activities[i][0]

                total_travel_time += d[activity ][next_activity]
                arrival_time = max(s[next_activity], arrival_time + p[activity] + d[activity][next_activity])

                wait_time = max(0, arrival_time - d[activity][next_activity] - e[activity])
                total_waiting_time += wait_time

            overtime = max(0, arrival_time + p[next_activity] + d[next_activity][0] - (start_time + u[int(shift)]))
            total_overtime += overtime

        # tinh gia tri fitness
        fitness = w_x * total_travel_time + w_y * total_overtime + w_z * total_waiting_time
        return fitness