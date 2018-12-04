import os
import neat
from helper import *

num_generations = 300  # Number of generations


# Called to evaluate all genomes
def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        pass


def run(config_file):
    # Get config_file and set up
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Add custom activation function to config file
    config.genome_config.add_activation('softmax_custom', softmax)

    # Creates the population
    pop = neat.Population(config)

    # Set Reporters
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    checkpoint = neat.Checkpointer(5, 500)
    pop.add_reporter(stats)
    pop.add_reporter(checkpoint)

    # Run through generations
    # Call function to evaluate genomes in a generation
    best_genome = pop.run(eval_genomes, num_generations)

    # Display the best genome among all num_generations
    print("(Best genome: {0})".format(best_genome))

    # Best net
    best_net = neat.nn.FeedForwardNetwork.create(best_genome, config)
    # Get the inputs and outputs form the game and feed it in the network
    for inp, point in zip(inputs, points):
        # Prediction
        output = best_net.activate(inp)
        # Display the output and error
        print("input: {:20}\nexpected output: {:20}\noutput: {:20}\nerror: {:20}".format(input, point, output,
                                                                                         calc_error(input, output)))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    run(config_path)
