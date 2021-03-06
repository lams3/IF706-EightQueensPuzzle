from abc import ABC
from typing import Type
from random import gauss
from math import sqrt

from genetic_framework.fitness import FitnessComputer
from genetic_framework.recombiner import Recombiner
from ackley.chromosomes import FloatChromosome, AdaptiveStepFloatChromosome, CovarianceFloatChromosome
from ackley.util import lerp, clamp


class MidPointRecombiner(Recombiner[FloatChromosome], ABC):
    @classmethod
    def recombine(cls: Type, chromosome1: FloatChromosome,
                  chromosome2: FloatChromosome) -> FloatChromosome:
        new_chromosome = FloatChromosome(chromosome1.custom_data)
        new_genes = new_chromosome.genotypes
        genes1 = chromosome1.genotypes
        genes2 = chromosome2.genotypes

        for i in range(len(new_genes)):
            new_genes[i].data = (genes1[i].data + genes2[i].data) / 2

        new_chromosome.genotypes = new_genes
        return new_chromosome


class AdaptiveStepMidPointRecombiner(Recombiner[AdaptiveStepFloatChromosome],
                                     ABC):
    @classmethod
    def recombine(
        cls: Type, chromosome1: AdaptiveStepFloatChromosome,
        chromosome2: AdaptiveStepFloatChromosome
    ) -> AdaptiveStepFloatChromosome:
        lower_bound: float = cls.custom_data['lower_bound']
        upper_bound: float = cls.custom_data['upper_bound']
        fitness_computer_cls: Type[FitnessComputer] = cls.custom_data[
            'fitness_computer']

        new_chromosome = AdaptiveStepFloatChromosome(chromosome1.custom_data)
        new_genes = new_chromosome.genotypes
        genes1 = chromosome1.genotypes
        genes2 = chromosome2.genotypes
        fitness1, fitness2 = fitness_computer_cls.fitness(
            chromosome1), fitness_computer_cls.fitness(chromosome2)

        t = fitness1 / (fitness1 + fitness2)
        t += gauss(0, .1)
        t = clamp(t, 0, 1)
        for i in range(len(new_genes)):
            new_value = lerp(t, genes1[i].data[0], genes2[i].data[0])
            new_value = clamp(new_value, lower_bound, upper_bound)

            new_delta = lerp(t, genes1[i].data[1], genes2[i].data[1])

            new_genes[i].data = (new_value, new_delta)

        new_chromosome.genotypes = new_genes
        return new_chromosome


class CovarianceMidPointRecombiner(Recombiner[CovarianceFloatChromosome], ABC):
    @classmethod
    def recombine(
            cls: Type, chromosome1: CovarianceFloatChromosome,
            chromosome2: CovarianceFloatChromosome
    ) -> CovarianceFloatChromosome:
        lower_bound: float = cls.custom_data['lower_bound']
        upper_bound: float = cls.custom_data['upper_bound']
        fitness_computer_cls: Type[FitnessComputer] = cls.custom_data[
            'fitness_computer']

        new_chromosome = CovarianceFloatChromosome(chromosome1.custom_data)
        new_genes = new_chromosome.genotypes
        genes1 = chromosome1.genotypes
        genes2 = chromosome2.genotypes
        fitness1, fitness2 = fitness_computer_cls.fitness(
            chromosome1), fitness_computer_cls.fitness(chromosome2)

        t = fitness1 / (fitness1 + fitness2)
        t += gauss(0, 0.1)
        t = clamp(t, 0, 1)
        for i in range(len(new_genes)):
            new_genes[i].data = lerp(t, genes1[i].data, genes2[i].data)

        new_chromosome.genotypes = new_genes
        return new_chromosome
