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

    def entropy(self, mask, lookup):
        '''
        Calculates the current populations entropy for a given mask.

        Parameters:

        - ``mask``: The list of indices to examine
        - ``lookup``: A dictionary containing entropy values already found for
          this population.  Should be reset if the population changes.
        '''
        try:
            return lookup[mask]
        except KeyError:
            occurances = {}
            for individual in self.individuals:
                # extract the gene values for the cluster
                value = self.getMaskValue(individual, mask)
                try:
                    occurances[value] += 1
                except KeyError:
                    occurances[value] = 1
            total = float(len(self.individuals))
            result = -sum(x / total * math.log(x / total, 2)
                          for x in occurances.itervalues())
            lookup[mask] = result
            return result

    
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
            minVal = 3  # Max possible distance should be 2
            results = []
            for c1, c2 in combinations(clusters, 2):
                result = distance(c1, c2, lookup)
                if result < minVal:
                    minVal = result
                    results = [(c1, c2)]
                if result == minVal:
                    results.append((c1, c2))
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
        self.dimensions = config['dimensions']
        self.numOfShifts = config['numOfShifts']
        self.attractionRepulsionWeight = config['attractionRepulsionWeight'] # the relative
        self.matrixDistance = config.matrixDistanceQ

        self.individuals = initialPopulation
        distance = Util.classMethods(self)[config["distance"]]
        ordering = Util.classMethods(self)[config["ordering"]]
        crossover = Util.classMethods(self)[config["crossover"]]
        beforeGenerationSet = set(self.individuals)
        while True:
            subtrees = self.buildTree(distance)
            masks = ordering(subtrees)
            generator = crossover(masks)
            individual = generator.next()
            while True:
                fitness = yield individual
                try:
                    individual = generator.send(fitness)
                except StopIteration:
                    break
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

        for i in xrange(0, len(self.individuals)):
            p1 = self.individuals[i]
            for mask in masks:
                while True:
                    j = random.randint(0, len(self.individuals))
                    if j != i:
                        break
                d = self.individuals[j]

                p2 = self.applyMask(p1, d, mask)
                p2.fitness = yield p2
                
                if p2 < p1:
                    self.individuals[i] = p2

    def clusterDependencyDistance(self, c1, c2):
        '''
        Calculates the true entropic distance between two clusters of genes.

        Parameters:

        - ``c1``: The first cluster.
        - ``c2``: The second cluster.
        '''
        result = 0
        for n in c1:
            for m in c2:
                result += self.computeDependencyMeasure(n, m)
        return result
        
    def computeDependencyMeasure(self, n, m):
        # x_nm > P * pi_nm
        w = self.attractionRepulsionWeight
        if len(self.getSameShiftSchedules(n, m)) > len(self.individuals) / self.dimensions:
            return self.computeDepencencyStat(n, m) * (w + (1 - w) * self.computeIntervalDependency(n, m))
        else:
            return self.computeDepencencyStat(n, m) * (w + (1 - w) * self.computeExternalDependency(n, m))

    def getSameShiftSchedules(self, n, m):
        count = 0
        for individual in self.individuals:
            if math.floor(individual[n - 1]) == math.floor(individual[m - 1]):
                count += 1
        return count
    
    # Xác suất pi_nm 2 hoạt độn n và m được xếp chung 1 ca làm việc
    def calculateProbability(self, n, m):
        Cn = set(self.getFeasibleShifts(n))  
        Cm = set(self.getFeasibleShifts(m))  
        
        # Tính giao của hai tập
        intersection = Cn.intersection(Cm)
        
        probability = len(intersection) / (len(Cn) * len(Cm))
        
        return probability

    # Xác suất P(X_nm <= x_nm)
    def calculateProbability2(self, n, m):
        pi_nm = self.calculateProbability(n, m)
        x_nm = self.getSameShiftSchedules(n, m)
        count = 0
        for X_nm in range (x_nm + 1):
            count += math.comb(len(self.individuals), X_nm) * math.pow(pi_nm, X_nm) * math.pow(1 - pi_nm, len(self.individuals) - X_nm)
        return count
    
    # Xác suất P(X_nm <= P*pi_nm)
    def calculateProbability3(self, n, m):
        pi_nm = self.calculateProbability(n, m)
        count = 0
        for X_nm in range (len(self.individuals)*pi_nm + 1):
            count += math.comb(len(self.individuals), X_nm) * math.pow(pi_nm, X_nm) * math.pow(1 - pi_nm, len(self.individuals) - X_nm)
        return count

    def computeDependencyStat(self, n, m):
        if len(self.getSameShiftSchedules(n, m)) > len(self.individuals)*self.calculateProbability(n, m):
            return 1 - (1 - self.calculateProbability2(n, m)) / (1 - self.calculateProbability3(n, m))
        else:
            return 1 - self.calculateProbability2(n, m) / self.calculateProbability3(n, m)
        pass

    def computeIntervalDependency(self, n, m):
        sameShiftSchedules = self.getSameShiftSchedules(n, m)

        cnt1 = 0
        cnt2 = 0
        for individual in sameShiftSchedules:
            cnt1 += 1 if individual[n] < individual[m] else 0
            cnt2 += math.pow(individual[n] - individual[m], 2)

        p = cnt1 / len(sameShiftSchedules)
        relativeOrderingInfor = 1 - (-p * math.log(p, 2) - (1 - p) * math.log(1 - p, 2))
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
                    if math.floor(individual[activity - 1]) != shift:
                        check = False
                        break
                if check: count += 1
            return count
        
        score = 0
        min_c = min(len(self.getFeasibleShifts(n)), len(self.getFeasibleShifts(m)))
        for v in self.getFeasibleShifts(n):
            for w in self.getFeasibleShifts(m):
                q_nm = countSchedules([n, m], [v, w])
                q_n = countSchedules([n], [v])
                q_m = countSchedules([m], [w])
                score += q_nm * math.log(q_nm / (q_n * q_m), min_c)
        return score
    
    def getFeasibleShifts(self, n):
        return [i + 1 for i in range(self.numOfShifts)]