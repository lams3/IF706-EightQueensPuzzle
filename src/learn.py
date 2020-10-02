"""Module responsible for the learning process of the eight queen problem.

This module instantiate genetic algorithm framework to find solutions for the
eight queen problem.
"""
from argparse import ArgumentParser, Action
from typing import Type, Any
from enum import Enum

from genetic_framework.experiment import Experiment
from eight_queens.chromosomes import *
from eight_queens.fitness import *
from eight_queens.mutators import *
from eight_queens.recombiners import *
from eight_queens.selectors import *
from eight_queens.utils import *


PROGRAM_DESCRIPTION = "Learns eight queens puzzle through genetic algorithm"

""" Enums for choosing classes for tunning the algorithm
If new classes are implemented, add them in the corresponding enum
to make it available as CLI argument.
"""
class FitnessComputerEnum(Enum):
    QUEEN_ATTACK_COUNT = QueenAttackCountFitnessComputer


class ChromosomeEnum(Enum):
    BIT_STRING = BitStringChromosome


class MutatorEnum(Enum):
    RANDOMIZE_GENE = RandomizeGeneMutator
    SWAP_GENE = SwapGeneMutator


class RecombinerEnum(Enum):
    CUT_CROSS_FILL = CutCrossFillRecombiner


class SurvivorSelectorEnum(Enum):
    BEST_FITNESS = BestFitnessSurvivorSelector


class MatingSelectorEnum(Enum):
    BEST_FITNESS = BestFitnessMatingSelector    


class SolutionSelectorEnum(Enum):
    K_BEST_FITNESS = KBestFitnessSolutionSelector


class CLIArgumentDescription:
    # Class designed to model the fields that an CLI Argument should define

    def __init__(self, _type: Type, default_value: Any, short_name: str, 
        full_name: str, value_name: str, help_message: str, action_cls: Type[Action]) -> None:
        self.type = _type
        self.default_value = default_value
        self.short_name = '-{}'.format(short_name)
        self.full_name = '--{}'.format(full_name)
        self.value_name = value_name
        self.help_message = help_message.replace('\n', '').replace('\td', '') + \
            " (default={})".format(default_value)
        self.action_cls = action_cls


# argparse.Actions for validating CLI arguments.
class EnumConstraintAction(Action):
    """Class responsible for sanitizing enum CLI inputs 
    (making sure value is a valid enum)"""

    def __init__(self, **kwargs):
        enum = kwargs.pop("type", None)
        kwargs['type'] = str

        if enum is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum, Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.name for e in enum))

        super().__init__(**kwargs)

        self._enum = enum

    def __call__(self, parser, namespace, values, option_string = None) -> None:
        setattr(namespace, self.dest, self._enum[values].value)


class CheckProbabilityConstraintAction(Action):
    """Class responsible for sanitizing probability CLI inputs' range [0, 1]"""

    def __call__(self, parser, namespace, values, option_string = None) -> None:
        if values < 0 or values > 1.0:
            raise ValueError(
                "{} flag has a value out of probability boundaries [0, 1.0]: {}"
                    .format(option_string, values))
        setattr(namespace, self.dest, values)


class CheckPositiveIntegerConstraintAction(Action):
    """Class responsible for sanitizing positive integers"""
    
    def __call__(self, parser, namespace, values, option_string = None) -> None:
        if values <= 0:
            raise ValueError(
                "{} flag has non positive value which is not allowed: {}"
                    .format(option_string, values))
        setattr(namespace, self.dest, values)

class NoConstraintAction(Action):
    """Dummy Action for arguments with no constraints"""
    
    def __call__(self, parser, namespace, values, option_string = None) -> None:
        setattr(namespace, self.dest, values)


# Every CLI Argument this script takes
ARGS = [
    CLIArgumentDescription(_type=int, default_value=8, 
        short_name='cs', full_name='chess_size', value_name='CHESS_SIZE',
        help_message="""Specify the size of the chess board in which the puzzle 
            takes place.""", action_cls=CheckPositiveIntegerConstraintAction),

    CLIArgumentDescription(_type=int, default_value=100, 
        short_name='ps', full_name='population_size', value_name='POP_SIZE',
        help_message="""Specify the size of the population that the algorithm 
            will evolve to find solutions.""",
        action_cls=CheckPositiveIntegerConstraintAction),
        
    CLIArgumentDescription(_type=int, default_value=50, 
        short_name='mg', full_name='max_generations', value_name='MAX_GENS',
        help_message="""Specify the maximum number of generations the 
            algorithm should evolve to find solutions.""",
        action_cls=CheckPositiveIntegerConstraintAction),

    CLIArgumentDescription(_type=int, default_value=5, 
        short_name='ns', full_name='number_solutions', value_name='NUM_SOLUTIONS',
        help_message="""Specify the number of solutions the algorithm should 
            find.""",
        action_cls=CheckPositiveIntegerConstraintAction),

    CLIArgumentDescription(_type=int, default_value=2, 
        short_name='bs', full_name='breed_size', value_name='BREED_SIZE',
        help_message="""Specify the number of children that should be created 
            for each pair or parents.""",
        action_cls=CheckPositiveIntegerConstraintAction),

    CLIArgumentDescription(_type=int, default_value=10000, 
        short_name='mfc', full_name='max_fitness_comp', value_name='MAX_FIT_COMPS',
        help_message="""Maximum number of fitness computations allowed to be 
            done before algorithm stops.""",
        action_cls=CheckPositiveIntegerConstraintAction),

    CLIArgumentDescription(_type=float, default_value=None, 
        short_name='tf', full_name='target_fitness', value_name='TARGET_FITNESS',
        help_message="""Specify the fitness of a good enough solution, so that 
            the algorithm can stop.""",
        action_cls=NoConstraintAction),

    CLIArgumentDescription(_type=float, default_value=0.4, 
        short_name='mp', full_name='mutation_probability', value_name='MUTATION_PROB',
        help_message="""Specify the probability that a mutation will occur 
            when new individual is generated.""",
        action_cls=CheckProbabilityConstraintAction),

    CLIArgumentDescription(_type=float, default_value=0.9, 
        short_name='cp', full_name='crossover_probability', value_name='CROSS_PROB',
        help_message="""Specify the probability that two given individuals 
            will recombine.""",
        action_cls=CheckProbabilityConstraintAction),

    CLIArgumentDescription(_type=FitnessComputerEnum, 
        default_value=FitnessComputerEnum.QUEEN_ATTACK_COUNT.value, 
        short_name='fc', full_name='fitness_computer', value_name='FITNESS_COMPUTER',
        help_message="""Specify the class responsible for computing individuals 
            fitness.""",
        action_cls=EnumConstraintAction),

    CLIArgumentDescription(_type=ChromosomeEnum, 
        default_value=ChromosomeEnum.BIT_STRING.value, 
        short_name='chr', full_name='chromosome', value_name='CHROMOSOME',
        help_message="""Specify the chromosome class. Will define how solutions
            are encoded and manipulated.""",
        action_cls=EnumConstraintAction),

    CLIArgumentDescription(_type=MutatorEnum, 
        default_value=MutatorEnum.RANDOMIZE_GENE.value, 
        short_name='mut', full_name='mutator', value_name='MUTATOR',
        help_message="""Specify the mutator class. Will define how solutions
            are mutated during evolution.""",
        action_cls=EnumConstraintAction),

    CLIArgumentDescription(_type=RecombinerEnum, 
        default_value=RecombinerEnum.CUT_CROSS_FILL.value, 
        short_name='rec', full_name='recombiner', value_name='RECOMBINER',
        help_message="""Specify the recombiner class. Will define how solutions
            are recombined together to generate new ones during evolution.""",
        action_cls=EnumConstraintAction),

    CLIArgumentDescription(_type=SurvivorSelectorEnum, 
        default_value=SurvivorSelectorEnum.BEST_FITNESS.value, 
        short_name='susel', full_name='survivor_selector', value_name='SURVIVOR_SEL',
        help_message="""Specify Survivor Selector class. Will define how 
            individuals are chosen to go on to next generation.""",
        action_cls=EnumConstraintAction),

    CLIArgumentDescription(_type=MatingSelectorEnum, 
        default_value=MatingSelectorEnum.BEST_FITNESS.value, 
        short_name='msel', full_name='mating_selector', value_name='MATING_SEL',
        help_message="""Specify Mating Selector class. Will define how 
            individuals are chosen to generate children for next generation.""",
        action_cls=EnumConstraintAction),

    CLIArgumentDescription(_type=SolutionSelectorEnum, 
        default_value=SolutionSelectorEnum.K_BEST_FITNESS.value, 
        short_name='sosel', full_name='solution_selector', value_name='SOLUTION_SEL',
        help_message="""Specify Solution Selector class. Will define how 
            best individuals are chosen as solution to the problem after the
            experiment.""",
        action_cls=EnumConstraintAction),
]


def main(**kwargs) -> None:
    print('Using these CLI arguments: {}\n'.format(kwargs))
    experiment = Experiment(kwargs['population_size'], kwargs['max_generations'], 
        kwargs['crossover_probability'], kwargs['mutation_probability'],
        kwargs['target_fitness'], kwargs['number_solutions'], kwargs['breed_size'], 
        kwargs['max_fitness_comp'], kwargs['chromosome'], kwargs['fitness_computer'], 
        kwargs['mutator'], kwargs['recombiner'],
        kwargs['mating_selector'], kwargs['survivor_selector'], 
        kwargs['solution_selector'], dict(chess_size=kwargs['chess_size']))
    best_individuals = experiment.run_experiment()

    print('\nSolutions:')
    for individual in best_individuals:
        print('Gen: {}, Fitness: {}'.format(individual.generation, individual.fitness()))
        print_chess_board(individual.chromosome)
        print('\n')


if __name__ == '__main__':
    parser = ArgumentParser(description=PROGRAM_DESCRIPTION)

    for arg in ARGS:
        parser.add_argument(arg.short_name, arg.full_name, 
            help=arg.help_message, action=arg.action_cls, type=arg.type, 
            metavar=arg.value_name, default=arg.default_value)
    args = parser.parse_args()

    main(**args.__dict__)