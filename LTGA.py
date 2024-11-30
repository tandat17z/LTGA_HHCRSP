'''
This module contains the implementation of LTGA itself.  It includes
functionality for each of the variants
'''
import math
import random
from itertools import combinations
import Util
from Individual import Individual


class LTGA(object):
    '''
    Class containing all of the LTGA functionality.  Uses the coroutine
    design structure to interact with problems being optimized.  To use,
    create an LTGA object and then call the ``generate`` function.  This
    will send out individuals and expects their fitness to be sent back in.
    '''
    def getMaskValue(self, individual, mask):
        '''
        Gets the individual's gene values for the given mask

        Parameters:

        - ``individual``: The individual to get gene information from
        - ``mask``: The list of indices to get information from
        '''
        return tuple(individual.genes[g] for g in mask)

    def setMaskValues(self, individual, mask, value):
        '''
        Sets the individual's gene values for the given mask

        Parameters:

        - ``individual``: The individual who's genes are changing.
        - ``mask``: The list of indices to change.
        - ``value``: The list of values to change to.
        '''
        for valueIndex, geneIndex in enumerate(mask):
            individual.genes[geneIndex] = value[valueIndex]

    # def entropy(self, mask, lookup):
    #     '''
    #     Calculates the current populations entropy for a given mask.

    #     Parameters:

    #     - ``mask``: The list of indices to examine
    #     - ``lookup``: A dictionary containing entropy values already found for
    #       this population.  Should be reset if the population changes.
    #     '''
    #     try:
    #         return lookup[mask]
    #     except KeyError:
    #         occurances = {}
    #         for individual in self.individuals:
    #             # extract the gene values for the cluster
    #             value = self.getMaskValue(individual, mask)
    #             try:
    #                 occurances[value] += 1
    #             except KeyError:
    #                 occurances[value] = 1
    #         total = float(len(self.individuals))
    #         result = -sum(x / total * math.log(x / total, 2)
    #                       for x in occurances.itervalues())
    #         lookup[mask] = result
    #         return result

    # def clusterDistance(self, c1, c2, lookup):
    #     '''
    #     Calculates the true entropic distance between two clusters of genes.

    #     Parameters:

    #     - ``c1``: The first cluster.
    #     - ``c2``: The second cluster.
    #     - ``lookup``: A dictionary mapping cluster pairs to their previously
    #       found distances.  Should be reset if the population changes.
    #     '''
    #     try:
    #         return lookup[c1, c2]
    #     except KeyError:
    #         try:
    #             result = 2 - ((self.entropy(c1, lookup) +
    #                            self.entropy(c2, lookup))
    #                           / self.entropy(c1 + c2, lookup))
    #         except ZeroDivisionError:
    #             result = 2  # Zero division only happens in 0/0
    #         lookup[c1, c2] = result
    #         lookup[c2, c1] = result
    #         return result

    # def pairwiseDistance(self, c1, c2, lookup):
    #     '''
    #     Calculates the pairwise approximation of the entropic distance between
    #     two clusters of genes.

    #     Parameters:

    #     - ``c1``: The first cluster.
    #     - ``c2``: The second cluster.
    #     - ``lookup``: A dictionary mapping cluster pairs to their previously
    #       found distances.  Should be reset if the population changes.
    #     '''
    #     try:
    #         return lookup[c1, c2]
    #     except KeyError:
    #         # averages the pairwise distance between each cluster
    #         result = sum(self.clusterDistance((a,), (b,), lookup)
    #                      for a in c1 for b in c2) / float(len(c1) * len(c2))
    #         lookup[c1, c2] = result
    #         lookup[c2, c1] = result
    #         return result

    def buildTree(self, distance):
        '''
        Given a method of calculating distance, build the linkage tree for the
        current population.  The tree is built by finding the two clusters with
        the minimum distance and merging them into a single cluster.  The
        process is initialized with all possible clusters of size 1 and ends
        when only a single cluster remains.  Returns the subtrees in the order
        they were created.

        Parameters:

        - ``distance``: The method of calculating distance.  Current options
          are ``self.clusterDistance`` and ``self.pairwiseDistance``
        '''
        clusters = [(i,) for i in xrange(len(self.individuals[0].genes))]
        subtrees = [(i,) for i in xrange(len(self.individuals[0].genes))]
        random.shuffle(clusters)
        random.shuffle(subtrees)
        lookup = {}

        def allLowest():
            '''
            Internal function used to find the list of all clusters pairings
            with the current smallest distances.
            '''
            # minVal = 3  # Max possible distance should be 2
            # results = []
            # for c1, c2 in combinations(clusters, 2):
            #     result = distance(c1, c2, lookup)
            #     if result < minVal:
            #         minVal = result
            #         results = [(c1, c2)]
            #     if result == minVal:
            #         results.append((c1, c2))
            results = []
            maxVal = None
            for c1, c2 in combinations(clusters, 2):
                result = distance(c1, c2, lookup)
                if maxVal == None or result > maxVal:
                    maxVal = result
                    results = [(c1, c2)]

            return results

        while len(clusters) > 1:
            c1, c2 = random.choice(allLowest())
            clusters.remove(c1)
            clusters.remove(c2)
            combined = c1 + c2
            clusters.append(combined)
            # Only add it as a subtree if it is not the root
            if len(clusters) != 1:
                subtrees.append(combined)
        return subtrees

    def leastLinkedFirst(self, subtrees):
        '''
        Reorders the subtrees such that the cluster pairs with the least
        linkage appear first in the list.  Assumes incoming subtrees are
        ordered by when they were created by the ``self.buildTree`` function.

        Parameters:

        - ``subtrees``: The list of subtrees ordered by how they were
          originally created.
        '''
        return list(reversed(subtrees))

    def smallestFirst(self, subtrees):
        '''
        Reorders the subtrees such that the cluster pairs with the smallest
        number of genes appear first in the list.  Assumes incoming subtrees
        are ordered by when they were created by the ``self.buildTree``
        function.

        Parameters:

        - ``subtrees``: The list of subtrees ordered by how they were
          originally created.
        '''
        return sorted(subtrees, key=len)

    def applyMask(self, p1, p2, mask):
        '''
        Used by two parent crossover to create an individual by coping the
        genetic information from p2 into a clone of p1 for all genes in the
        given mask.  Returns the newly created individual.

        Parameters:

        - ``p1``: The first parent.
        - ``p2``: The second parent.
        - ``mask``: The list of indices used in this crossover.
        '''
        maskSet = set(mask)
        return Individual([p2.genes[g] if g in maskSet else p1.genes[g]
                           for g in range(len(p1.genes))])

    # def twoParentCrossover(self, masks):
    #     '''
    #     Creates individual generator using the two parent crossover variant.
    #     Uses coroutines to send out individuals and receive their fitness
    #     values.  Terminates when a complete evolutionary generation has
    #     finished.

    #     Parameters:

    #     - ``masks``: The list of crossover masks to be used when generating
    #       individuals, ordered based on how they should be applied.
    #     '''
    #     offspring = []
    #     # Does the following twice in order to make enough children
    #     for _ in [0, 1]:
    #         random.shuffle(self.individuals)
    #         # pairs off parents with their neighbor
    #         for i in xrange(0, len(self.individuals) - 1, 2):
    #             p1 = self.individuals[i]
    #             p2 = self.individuals[i + 1]
    #             for mask in masks:
    #                 c1 = self.applyMask(p1, p2, mask)
    #                 c2 = self.applyMask(p2, p1, mask)
    #                 # Duplicates are caught higher up
    #                 c1.fitness = yield c1
    #                 c2.fitness = yield c2
    #                 # if the best child is better than the best parent
    #                 if max(p1, p2) < max(c1, c2):
    #                     p1, p2 = c1, c2
    #             # Overwrite the parents with the modified version
    #             self.individuals[i] = p1
    #             self.individuals[i + 1] = p2
    #             # The offspring is the best individual created during the cross
    #             offspring.append(max(p1, p2))
    #     self.individuals = offspring

    # def globalCrossover(self, masks):
    #     '''
    #     Creates individual generator using the global crossover variant.
    #     Uses coroutines to send out individuals and receive their fitness
    #     values.  Terminates when a complete evolutionary generation has
    #     finished.

    #     Parameters:

    #     - ``masks``: The list of crossover masks to be used when generating
    #       individuals, ordered based on how they should be applied.
    #     '''
    #     # Creates a dictionary to track individual's values for each mask
    #     values = {mask: [] for mask in masks}
    #     for mask in masks:
    #         for individual in self.individuals:
    #             value = self.getMaskValue(individual, mask)
    #             values[mask].append(value)
    #     # each individual creates a single offspring, which replaces itself
    #     for individual in self.individuals:
    #         for mask in masks:
    #             startingValue = self.getMaskValue(individual, mask)
    #             # Find the list of values in the population that differ from
    #             # the current individual's values for this mask
    #             options = [value for value in values[mask]
    #                        if value != startingValue]
    #             if len(options) > 0:
    #                 value = random.choice(options)
    #                 self.setMaskValues(individual, mask, value)
    #                 newFitness = yield individual
    #                 # if the individual improved, update fitness
    #                 if individual.fitness < newFitness:
    #                     individual.fitness = newFitness
    #                 # The individual did not improve, revert changes
    #                 else:
    #                     self.setMaskValues(individual, mask, startingValue)

    def generate(self, initialPopulation, config):
        '''
        The individual generator for the LTGA population.  Sends out
        individuals that need to be evaluated and receives fitness information.
        Will continue sending out individuals until the population contains
        only one unique individual or a generation passes without the set of
        unique individuals changing.

        Parameters:

        - ``initialPopulation``: The list of individuals to be used as the
          basis for LTGA's evolution.  These individuals should already have
          fitness values set.  If local search is to be performed on the
          initial population, it should be done before sending to this
          function.
        - ``config``: A dictionary containing all configuration information
          required by LTGA to generate individuals.  Should include values
          for:

          - ``distance``: The method used to determine the distance between
            clusters, for instance ``clusterDistance`` and
            ``pairwiseDistance``.
          - ``ordering``: The method used to determine what order subtrees
            should be used as crossover masks, for instance
            ``leastLinkedFirst`` and ``smallestFirst``.
          - ``crossover``: The method used to generate new individuals, for
            instance ``twoParentCrossover`` and ``globalCrossover``.
        '''
        self.hhcrsp = config['hhcrsp']

        self.individuals = initialPopulation
        distance = Util.classMethods(self)[config["distance"]]
        ordering = Util.classMethods(self)[config["ordering"]]
        crossover = Util.classMethods(self)[config["crossover"]]
        beforeGenerationSet = set(self.individuals)
        while True:
            subtrees = self.buildTree(distance)
            masks = ordering(subtrees)
            generator = crossover(masks)
            print("--> tree", masks)
            individual = generator.next()
            while True:
                fitness = yield individual
                try:
                    individual = generator.send(fitness)
                except StopIteration:
                    break
            print('----- finish 1 round----------------')
            # If all individuals are identical
            currentSet = set(self.individuals)
            if (len(currentSet) == 1 or
                currentSet == beforeGenerationSet):
                break
            beforeGenerationSet = currentSet
    
    def recombination(self, masks):
        '''
        Recombining two solutions for a given subset of activities
        
        Using a linkage tree for subsets of activities
        '''
        random.shuffle(self.individuals)
        beforeIndividuals = self.individuals
        for i in xrange(0, len(self.individuals)):
            p1 = self.individuals[i]
            for mask in masks:
                candidates = [_ for _ in xrange(0, len(self.individuals)) if _ != i]
                d = beforeIndividuals[random.choice(candidates)]

                p2 = self.applyMask(p1, d, mask)
                p2.fitness = yield p2
                
                if p2 < p1:
                    self.individuals[i] = p2

    def clusterDependencyDistance(self, c1, c2, lookup):
        '''
        Calculates the distance between two clusters of genes.

        Parameters:

        - ``c1``: The first cluster.
        - ``c2``: The second cluster.
        '''
        result = 0
        for n in c1:
            for m in c2:
                try:
                    pi = self.calculatePi(n, m) 
                except:# len(c) == 0
                    continue
                result += self.computeDependencyMeasure(n, m)
        return result
        
    # -----------------------------------------------
    def computeDependencyMeasure(self, n, m):
        '''
        Tinh dependency measure giua 2 activities: n, m
        '''
        # x_nm > P * pi_nm
        w = self.hhcrsp.w_dependency
        pi = self.calculatePi(n, m)
        if len(self.getSameShiftSchedules(n, m)) > len(self.individuals) * pi :
            return self.computeDependencyStat(n, m) * (w + (1 - w) * self.computeIntervalDependency(n, m))
        else:
            return self.computeDependencyStat(n, m) * (w + (1 - w) * self.computeExternalDependency(n, m))

    def computeDependencyStat(self, n, m):
        def calculateP1(self, n, m):
            '''
            probality P(X_nm <= x_nm)
            '''
            pi_nm = self.calculatePi(n, m)
            x_nm = len(self.getSameShiftSchedules(n, m))
            count = 0 # = sum(C_n_k * pi ^ k * (1 - p) * ( n - k))
            for k in range (x_nm + 1):
                count += Util.comb(len(self.individuals), k) * math.pow(pi_nm, k) * math.pow(1 - pi_nm, len(self.individuals) - k)
            return count
        
        def calculateP2(self, n, m):
            '''
            probality P(X_nm <= P*pi_nm)
            '''
            pi_nm = self.calculatePi(n, m)
            count = 0 # = sum(C_n_k * pi ^ k * (1 - p) * ( n - k))
            for k in range (int(len(self.individuals)*pi_nm) + 1):
                count += Util.comb(len(self.individuals), k) * math.pow(pi_nm, k) * math.pow(1 - pi_nm, len(self.individuals) - k)
            return count
        
        pi = self.calculatePi(n, m)
        try:
            if len(self.getSameShiftSchedules(n, m)) > len(self.individuals) * pi:
                return 1 - (1 - calculateP1(self, n, m)) / (1 - calculateP2(self, n, m))
            else:
                return 1 - calculateP1(self, n, m) / calculateP2(self, n, m)
        except:
            return 1

    def computeIntervalDependency(self, n, m):
        sameShiftSchedules = self.getSameShiftSchedules(n, m)

        cnt1 = 0
        cnt2 = 0
        for individual in sameShiftSchedules:
            cnt1 += 1 if individual.genes[n] < individual.genes[m] else 0
            cnt2 += math.pow(individual.genes[n] - individual.genes[m], 2)

        p = float(cnt1) / len(sameShiftSchedules)
        
        try:
            relativeOrderingInfor = 1 - (-p * math.log(p, 2) - (1 - p) * math.log(1 - p, 2))
        except:
            relativeOrderingInfor = 1
        adjacencyInfor = 1 - cnt2 / len(sameShiftSchedules)

        return adjacencyInfor * relativeOrderingInfor
    
    def computeExternalDependency(self, n, m):
        def countSchedules(listActivity, listShift):
            assert len(listActivity) == len(listShift), "--ERROR---------------"
            count = 0
            for individual in self.individuals:
                check = True
                for i in range(len(listActivity)):
                    activity = listActivity[i]
                    shift = listShift[i]
                    if math.floor(individual.genes[activity - 1]) != shift:
                        check = False
                        break
                if check: count += 1
            return count
        
        score = 0
        c1 = self.hhcrsp.getFeasibleShifts(n)
        c2 = self.hhcrsp.getFeasibleShifts(m)
        min_c = min(len(c1), len(c2))

        for v in c1:
            for w in c2:
                q_nm = countSchedules([n, m], [v, w])
                q_n = countSchedules([n], [v])
                q_m = countSchedules([m], [w])
                try:
                    score += q_nm * math.log(q_nm / (q_n * q_m), min_c)
                except:
                    pass
        return score
    
    # ----------------- Cac ham ho tro tinh dependency measure ------------------
    def getSameShiftSchedules(self, n, m):
        '''
        So luong individual ma hoat dong n, m co ca giong nhau
        '''
        schedules = []
        for individual in self.individuals:
            if math.floor(individual.genes[n - 1]) == math.floor(individual.genes[m - 1]):
                schedules.append(individual)
        return schedules
    
    def calculatePi(self, n, m):
        '''
        xac suat pi_nm 2 activities n, m duoc xep chung vao 1 shift
        '''
        c1 = self.hhcrsp.getFeasibleShifts(n)
        c2 = self.hhcrsp.getFeasibleShifts(m) 
        return float(len(list(set(c1) & set(c2)))) / (len(c1) * len(c2))