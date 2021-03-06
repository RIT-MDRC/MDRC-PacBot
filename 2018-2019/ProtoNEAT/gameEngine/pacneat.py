import os, sys, logging
import neat
import robomodules as rm
import time
from messages import *
from pacbot.variables import game_frequency, ticks_per_update
from pacbot import StateConverter, GameState


GHOST_LOCATIONS = []
GAME_SCORE = 10

ADDRESS = os.environ.get("BIND_ADDRESS","localhost")
PORT = os.environ.get("BIND_PORT", 11297)
FREQUENCY = game_frequency * ticks_per_update


num_generations = 300  # Number of generations


class PacEng(rm.ProtoModule):

    def __init__(self, addr, port):
        self.subscriptions = [MsgType.PACMAN_LOCATION]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        self.game = GameState()
        self.game.unpause()


    def _write_state(self):
        full_state = StateConverter.convert_game_state_to_full(self.game)
        self.write(full_state.SerializeToString(), MsgType.FULL_STATE)

        light_state = StateConverter.convert_game_state_to_light(self.game)
        self.write(light_state.SerializeToString(), MsgType.LIGHT_STATE)

    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.PACMAN_LOCATION:
            self.game.pacbot.update((msg.x, msg.y))

    def tick(self):
        if self.game.lives < 3:
            global GAME_SCORE
            GAME_SCORE = self.game.score
            global GHOST_LOCATIONS
            GHOST_LOCATIONS.extend((self.game.red.pos["current"][0], self.game.red.pos["current"][1], self.game.pink.pos["current"][0], self.game.pink.pos["current"][1], self.game.orange.pos["current"][0],self.game.orange.pos["current"][1], self.game.blue.pos["current"][0], self.game.blue.pos["current"][1]))
            self.game.respawnagents()
        # this function will get called in a loop with FREQUENCY frequency
        if self.game.play:
            # update_pacbot_pos
            # This will become asynchronous
            self.game.next_step()
        self._write_state()


class PacNeat():




    # Called to evaluate all genomes
    def eval_genomes(self,genomes, config):
        for genome_id, genome in genomes:
            genome.fitness = 10
            for attr in ('pacEng',0):
                self.__dict__.pop(attr, None)
            self.pacEng = PacEng(ADDRESS, PORT)
            self.pacEng.run()
            self.pacEng.quit()
            #g_net = neat.nn.FeedForwardNetwork()
            #g_output = g_net.activate(INPUT_POS)
            genome.fitness = GAME_SCORE
            test = GHOST_LOCATIONS
            pass





    def runa(self, config_file):
        # Get config_file and set up
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)

        # Creates the population
        pop = neat.Population(config)

        # Set Reporters
        pop.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        checkpoint = neat.Checkpointer(generation_interval=5, time_interval_seconds=500)
        pop.add_reporter(stats)
        pop.add_reporter(checkpoint)

        # Run through generations
        # Call function to evaluate genomes in a generation
        best_genome = pop.run(self.eval_genomes, num_generations)

        # Display the best genome among all num_generations
        print("(Best genome: {0})".format(best_genome))

        # Create a checkpoint

        # Best net
        best_net = neat.nn.FeedForwardNetwork.create(best_genome, config)

def main():
    module = PacNeat()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    module.runa(config_path)



if __name__ == "__main__":
    main()