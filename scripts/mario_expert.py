"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random
import time

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent


class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 10,   ###########################
        emulation_speed: int = 0,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
                                            #in_list value      #required input index
            WindowEvent.PRESS_ARROW_DOWN,   #      -                     0
            WindowEvent.PRESS_ARROW_LEFT,   #      4                     1
            WindowEvent.PRESS_ARROW_RIGHT,  #      3                     2
            WindowEvent.PRESS_ARROW_UP,     #      -                     5
            WindowEvent.PRESS_BUTTON_A,     #      5                     4
            WindowEvent.PRESS_BUTTON_B,     #      -                     3
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, action: int) -> None:
        """
        This is a very basic example of how this function could be implemented

        As part of this assignment your job is to modify this function to better suit your needs

        You can change the action type to whatever you want or need just remember the base control of the game is pushing buttons
        """

        # Simply toggles the buttons being on or off for a duration of act_freq
        # print("In func run_action")
        # print("the pass in action is: " + str(action))

        self.pyboy.send_input(self.valid_actions[action])
        # print("run action: " + str(self.valid_actions[action]))

        for _ in range(self.act_freq):
            self.pyboy.tick()

        self.pyboy.send_input(self.release_button[action])


class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None

        self.action_queue = []
        self.action_queue_index = 0
        self.air_timeout = 0
        self.skip_count = 0

    def choose_action(self):
        # print("In func choose_action")
        state = self.environment.game_state()
        frame = self.environment.grab_frame()
        game_area = self.environment.game_area()
        print("===============================================")
        print(game_area)
        print("----------------------------------------------")
        print(state)
        print("===============================================")


        mario_position = self.get_mario_position(game_area)
        if(mario_position == [0,0]):
            return 0

        time.sleep(0.05)

        if(self.check_position_object(game_area,mario_position,[[0,-1],[0,-1]],0) and (self.check_position_object(game_area,mario_position,[[1,-1],[1,-1]],0))):
            self.air_timeout = self.air_timeout + 1
            # if (game_area[14][11] == 0) or (game_area[14][12] == 0):
            if (self.if_colume_void(game_area,mario_position,3) or self.if_colume_void(game_area,mario_position,4)):
                print("void miss")
                return 1
            elif(self.air_timeout < 6):
                print("in air, wait")
                return 0
            else:
                self.air_timeout = 0
                print("in air, time out")
                return 2
        elif(mario_position == [8,1]):
            print("1-1 final go")
            return 2
        elif(self.check_position_object(game_area,mario_position,[[2,0],[2,1]],15)):
            if(self.check_position_object(game_area,mario_position,[[0,3],[1,3]],12) or self.check_position_object(game_area,mario_position,[[0,3],[1,3]],13) or self.check_position_object(game_area,mario_position,[[0,3],[1,3]],10)):
                print("15 frount blocked back")
                self.action_queue = [1,1]
                return 1 #back
            else:
                print("15 frount weit jump")
                self.action_queue = [0,4]
                return 0
        elif(self.check_position_object(game_area,mario_position,[[2,2],[2,3],[3,2],[3,3]],15)):
            print("15 up close, back")
            return 1 #back
        elif(self.check_position_object(game_area,mario_position,[[5,0],[5,0]],15)):
            if(self.check_position_object(game_area,mario_position,[[0,3],[1,3]],12) or self.check_position_object(game_area,mario_position,[[0,3],[1,3]],13) or self.check_position_object(game_area,mario_position,[[0,3],[1,3]],10)):
                print("15 frount blocked back")
                return 1 #jump
            else:
                print("15 frount jump")
                return 4 #jump
        elif(self.check_position_object(game_area,mario_position,[[5,0],[5,0]],16)):
            print("16 frount jump")
            return 4 #jump
        elif(self.check_position_object(game_area,mario_position,[[2,0],[2,1],[3,0],[3,1]],18)):
            print("18 frount jump")
            return 4 #jump
        elif(self.check_position_object(game_area,mario_position,[[3,2],[3,3]],18)):
            print("18 frount up back")
            self.action_queue = [1,1,2]
            return 1 #back
        elif(self.check_position_object(game_area,mario_position,[[2,-1],[2,-2],[3,-1],[3,-2]],15)):
            print("15 down wati")
            return 0 #jump
        elif (self.check_position_object(game_area,mario_position,[[3,0],[3,1],[4,0],[4,1],[4,2],[4,3],[4,4],[5,3],[5,4],[6,3],[6,4]],15)):
            print("15 up wait")
            return 0 #wait
        elif(self.check_position_object_AllMatch(game_area,mario_position,[[3,-1],[4,-1],[5,-1]],0) and self.check_position_object_AllMatch(game_area,mario_position,[[6,0],[6,1]], 10)):
            self.handle_void_jump(game_area,mario_position,2)
            return 0
        elif(self.check_position_object_AllMatch(game_area,mario_position,[[6,-1],[4,-1],[5,-1]],0) and self.check_position_object_AllMatch(game_area,mario_position,[[7,0],[7,1]], 10)):
            self.handle_void_jump(game_area,mario_position,2)
            return 0
        elif(self.check_position_object(game_area,mario_position,[[1,-1],[2,-1],[3,-1]],0) and (mario_position[1] == 13)):
            self.handle_void_jump(game_area,mario_position,1)
            return 0
        elif(self.check_position_object_AllMatch(game_area,mario_position,[[0,-1],[0,-2],[0,-3],[0,-4]],10) and self.check_position_object_AllMatch(game_area,mario_position,[[2,-1],[2,-2],[2,-3],[2,-4]],0) and (self.skip_count == 0)):
            print("high void jump")
            return 4
        elif (self.check_position_object(game_area,mario_position,[[0,4],[1,4]],13)):
            print("13 top stop jump")
            self.action_queue = [1,0,4]
            return 4 #jump
        elif (self.check_position_object(game_area,mario_position,[[0,5],[0,6],[1,5],[1,6]],6)):
            print("wait 6")
            return 0 #wati
        elif (self.check_position_object(game_area,mario_position,[[3,0],[2,0]],14)):
            print("14 frount go jump")
            self.action_queue = [2,2,4,2,2]
            return 4 #jump
        elif (self.check_position_object(game_area,mario_position,[[3,0],[2,0],[1,0]],10)):
            print("10 frount jump")
            self.action_queue = [2,4,2,2] #bug
            return 4 #jump
        elif (self.check_position_object(game_area,mario_position,[[3,0],[2,0],[1,0],[3,1],[2,1],[1,1]],12)):
            print("12 frount jump")
            self.action_queue = [2,4,2,2] #bug
            return 4 #jump
        elif (state['stage'] == 2):
            actions = self.one_two_optimise(game_area,mario_position)
            if (len(actions) != 1):
                self.action_queue = actions
                return 0
            else:
                return actions[0]
        else:
            print("empty go")
            return 2 #frount

        # Implement your code here to choose the best action

    def step(self):
        """
        Modify this function as required to implement the Mario Expert agent's logic.

        This is just a very basic example
        """

        # Choose an action - button press or other...

        action = self.choose_action()
        
        if (self.action_queue != []):
            action = self.action_queue[self.action_queue_index]
            print("in queue, now doing: " + str(action))
            if (self.action_queue_index == (len(self.action_queue) - 1)):
                self.action_queue = []
                self.action_queue_index = 0
            else:
                self.action_queue_index = self.action_queue_index + 1

        # Run the action on the environment
        self.environment.run_action(action)

    def handle_void_jump(self,game_area,mario_position,void_type):
        if(void_type == 1):
            print("void, jump")
            self.environment.run_action(1)
            time.sleep(0.1)
            self.environment.run_action(0)
            time.sleep(0.1)
            self.environment.run_action(2)
            time.sleep(0.1)
            self.environment.run_action(2)
            time.sleep(0.1)
            self.environment.run_action(4)
            time.sleep(0.1)
            self.environment.run_action(2)
            time.sleep(0.1)
            self.environment.run_action(2)
            time.sleep(0.1)
            self.environment.run_action(2)
        elif(void_type == 2):
            print("big void, jump")
            while (self.check_position_object(game_area,mario_position,[[1,-1],[2,-1],[3,-1],[4,-1],[5,-1],[6,-1]],0)):
                print(game_area)
                self.environment.run_action(1)
                time.sleep(0.1)
                game_area = self.environment.game_area()
                mario_position = self.get_mario_position(game_area)
            while (self.check_position_object(game_area,mario_position,[[2,-1],[2,-1]],10)):
                self.environment.run_action(2)
                time.sleep(0.1)
                game_area = self.environment.game_area()
                mario_position = self.get_mario_position(game_area)
            self.environment.run_action(3)
            time.sleep(0.1)
            self.environment.run_action(4)
            time.sleep(0.1)
            game_area = self.environment.game_area()
            mario_position = self.get_mario_position(game_area)
            while (self.check_position_object(game_area,mario_position,[[0,-1],[0,-1]],10) == 0):
                self.environment.run_action(2)
                time.sleep(0.1)
                game_area = self.environment.game_area()
                mario_position = self.get_mario_position(game_area)

    def one_two_optimise(self,game_area,mario_position):
        if (self.check_position_object(game_area,mario_position,[[3,-1],[3,-1]],0)):
            return [2,4]
        elif (self.check_position_object(game_area,mario_position,[[3,2],[3,3]],10)):
            return [2,4]
        else:
            return [2]
        
    def if_colume_void(self,game_area,mario_position,colume):
        for ii in range(mario_position[1],15):
            if (game_area[(ii+1)][(colume+mario_position[0])] != 0):
                return False
        
        return True

    def check_position_object(self, Game_Area,mario_position, target_positions, target_object):
        #this function will return true if target object appears on ANY of the input positions
        #target position using mario's local coordinate！！！！
        #        +Y
        #         ^   (local coodinate)
        #         |
        #       mario ---------> +x

        print("search " + str(target_object) + " ", end="")
        self.skip_count = 0

        for Tpos_id in range(0,len(target_positions)):
            target_position_global = [mario_position[1]-target_positions[Tpos_id][1],mario_position[0]+target_positions[Tpos_id][0]]
            print(" " + str(target_position_global), end="")
            if (target_position_global[0] < 0 or target_position_global[0] > 15 or target_position_global[1] < 0 or target_position_global[1] > 19):
                print("skip")
                self.skip_count = self.skip_count + 1
            elif (Game_Area[target_position_global[0]][target_position_global[1]] == target_object):
                print("")
                return True
        print("")
        return False
    
    def check_position_object_AllMatch(self, Game_Area,mario_position, target_positions, target_object):
        #this function will return true when all the target position is the target object
        for Tpos_ID in range(0,len(target_positions)):
            if(self.check_position_object(Game_Area,mario_position,[target_positions[Tpos_ID],target_positions[Tpos_ID]],target_object) == 0):
                return False
        
        return True
    
    def get_mario_position(self, Game_Area):
        # this function returns the position of mario   1  1
        objects_position = []  #  return position  ->  (1) 1

        #Traverse all the coordinates in the area and find the 4 mario pixels
        for row_y in range(0,16):
            for column_x in range(0,20):
                if (Game_Area[row_y][column_x] == 1):
                    objects_position = [column_x,(row_y + 1)]
                    print(str(objects_position))
                    return objects_position
        
        if(objects_position == []):
            return [0,0]
    

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()
