#Uses RobotModules to turn input from the robot/server into data for NEAT
import os
from robomodules import ProtoModule
from messages import *

SERVER_ADDRESS = os.environ.get("BIND_ADDRESS","localhost")
SERVER_PORT = os.environ.get("BIND_PORT", 11295)

LOCAL_ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
LOCAL_PORT = os.environ.get("LOCAL_PORT", 11295)

SERVER_FREQUENCY = 0
LOCAL_FREQUENCY = 30


class PacbotServerClient(ProtoModule):
    def __init__(self, addr, port, loop):
        self.subscriptions = [MsgType.LIGHT_STATE]
        super().__init__(addr, port, message_buffers, MsgType, SERVER_FREQUENCY, self.subscriptions, loop)
        self.state = None

    def msg_received(self, msg, msg_type):
        # This gets called whenever any message is received
        # This module will connect to server and receive the game state
        if msg_type == MsgType.LIGHT_STATE:
            self.state = msg

    def tick(self):
        return

    def get_state(self):
        return self.state


class PacbotCommsModule(ProtoModule):
    def __init__(self, server_addr, server_port, local_addr, local_port):
        self.subscriptions = [MsgType.PACMAN_LOCATION]
        super().__init__(local_addr, local_port, message_buffers, MsgType, LOCAL_FREQUENCY, self.subscriptions)
        self.server_module = PacbotServerClient(server_addr, server_port, self.loop)
        self.server_module.connect()

    def msg_received(self, msg, msg_type):
        # This gets called whenever any message is received
        if msg_type == MsgType.PACMAN_LOCATION:
            self.server_module.write(msg.SerializeToString(), MsgType.PACMAN_LOCATION)
            print("test")

    def tick(self):
        # Get state from the server
        state = self.server_module.get_state()
        if state != None:
            # Broadcast state to local modules
            self.write(state.SerializeToString(), MsgType.LIGHT_STATE)


def main():
    module = PacbotCommsModule("localhost", "11927", "localhost", "11925")
    module.run()


if __name__ == "__main__":
    main()