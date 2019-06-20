import cv2
import numpy as np
import datetime
import time

# tracker
from rubikscubetracker import RubiksVideo, RubiksImage, merge_two_dicts
import json
import logging
import os
import sys
from math import sqrt
import subprocess

# color resolve_colors
from rubikscolorresolver import resolve_colors


import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H


#camera fix
# sudo nano /etc/environment
# QT_X11_NO_MITSHM=1


FT232H.use_FT232H()

ft232h = FT232H.FT232H()


# Configure digital inputs and outputs using the setup function.
# Note that pin numbers 0 to 15 map to pins D0 to D7 then C0 to C7 on the board.
ft232h.setup(7, GPIO.IN)   # Make pin D7 a digital input.
ft232h.setup(8, GPIO.OUT)   # C0 S0  Make pin C0 a digital output.
ft232h.setup(9, GPIO.OUT)   # C1 S1
ft232h.setup(10, GPIO.OUT)  # C2 S2
ft232h.setup(11, GPIO.OUT)  # C3 S3
ft232h.setup(12, GPIO.OUT)  # C4 Flag

cmd_desc = ["NOP", "Turn CW","Turn CCW","Turn 180","Right->Top","Left->Top","Front->Top","Back->Top"]
def command_to_str(command):
    if command < len(cmd_desc):
        return cmd_desc[command]
    elif command == 11:
        return "SCAN"
    else:
        return "NOP"

def is_robot_ready():
    return ft232h.input(7) == GPIO.HIGH # READY FLAG FROM ROBO


def send_command(value):
    while not is_robot_ready():
        time.sleep(.100)

    ft232h.output(11, GPIO.HIGH if (value >> 3) % 2 == 1 else GPIO.LOW)
    ft232h.output(10, GPIO.HIGH if (value >> 2) % 2 == 1 else GPIO.LOW)
    ft232h.output(9, GPIO.HIGH if (value >> 1) % 2 == 1 else GPIO.LOW)
    ft232h.output(8, GPIO.HIGH if value % 2 == 1 else GPIO.LOW)
    time.sleep(.100)
    print "COMMAND: {} (ID {})".format(command_to_str(value),value)

    ft232h.output(12, GPIO.HIGH) # ENABLE FLAG = 1
    #print "enable = 1"

    while is_robot_ready(): # READY FLAG FROM ROBO
        time.sleep(.100)
    ft232h.output(12, GPIO.LOW) # ENABLE FLAG = 0
    print "COMMAND OK"

    ft232h.output(11, GPIO.LOW)
    ft232h.output(10, GPIO.LOW)
    ft232h.output(9, GPIO.LOW)
    ft232h.output(8, GPIO.LOW)

#while True:
#    send_command(0b0100) #left to top

#Class for cube orientation
class cube_ori(object):
    def __init__(self):
        self.orientation = {}
        #KEY is cube face position, VALUE is which face is there
        for idx,side in enumerate(['F','R','B','L','U','D']):
            self.orientation[side] = side

    def __str__(self):
        #return str(self.orientation)
        return self.unwrap()

    def unwrap(self):
        # - U - -
        # L F R B
        # - D - -
        ret = ''
        for side in "ULFRBD":
            if side == 'U' or side == 'D':
                ret += '  {}\n'.format(self.orientation[side])
            elif side == 'B':
                ret += '{}\n'.format(self.orientation[side])
            else:
                ret += '{} '.format(self.orientation[side])
        return ret

    def getActualSide(self, side, debug = False):
        if side not in self.orientation.keys():
            #an invalid face was requested, this is not an exception-worthy error
            return ''
        elif side not in self.orientation.values():
            #something has gone terribly, terribly wrong:
            #our cube is missing one or more sides
            print "Current Cube Status:"
            print self.unwrap()
            raise LookupError , "Cube face '{}' went missing!".format(side)
        else:
            if debug: print "Before:\n{}".format(self.unwrap())
            #get position of requested face
            for heading, face in self.orientation.iteritems():
                if face == side:
                    #and update orientation appropriately
                    for case in switch(heading):
                        if case('U'):
                            break
                        if case('F'):
                            self.rot_y(3)
                            break
                        if case('D'):
                            self.rot_y(2)
                            break
                        if case('B'):
                            self.rot_y(1)
                            break
                        if case('L'):
                            self.rot_x(3)
                            break
                        if case('R'):
                            self.rot_x(1)
                            break
                    if debug: print "After:\n{}".format(self.unwrap())
                    return heading
    #--- end method getActualSide(side)

    def rot_x(self, turns=1, debug=False): #RIGHT TO TOP
        for _ in range(turns):
            if debug: print 'Before: ' + str(self.orientation)
            tmp = self.orientation['U']
            self.orientation['U']=self.orientation['R']
            self.orientation['R']=self.orientation['D']
            self.orientation['D']=self.orientation['L']
            self.orientation['L']=tmp
            if debug: print 'After' + str(self.orientation)

    def rot_y(self, turns=1, debug=False): # BACK TO TOP
        for _ in range(turns):
            if debug: print 'Before: ' + str(self.orientation)
            tmp = self.orientation['U']
            self.orientation['U']=self.orientation['B']
            self.orientation['B']=self.orientation['D']
            self.orientation['D']=self.orientation['F']
            self.orientation['F']=tmp
            if debug: print 'After' + str(self.orientation)
#--- end class cube_ori

#Class for switch command
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

def command_switcher(argument, tracker=None):
    face = argument[0]
    print 'Requested command is {}'.format(argument)
    if tracker != None:
        argument = tracker.getActualSide(face) + argument[1:]
        print 'Actual command is {}'.format(argument)
    for case in switch(argument):
            if case('R'):
                right(direction='cw', tracker=tracker)
                break
            if case("R'"):
                right(direction='ccw', tracker=tracker)
                break
            if case("R2"):
                right(turn_180=1, tracker=tracker)
                break
            if case('L'):
                left(direction='cw', tracker=tracker)
                break
            if case("L'"):
                left(direction='ccw', tracker=tracker)
                break
            if case("L2"):
                left(turn_180=1, tracker=tracker)
                break
            if case('U'):
                up(direction='cw', tracker=tracker)
                break
            if case("U'"):
                up(direction='ccw', tracker=tracker)
                break
            if case("U2"):
                up(turn_180=1, tracker=tracker)
                break
            if case('D'):
                down(direction='cw', tracker=tracker)
                break
            if case("D'"):
                down(direction='ccw', tracker=tracker)
                break
            if case("D2"):
                down(turn_180=1, tracker=tracker)
                break
            if case('F'):
                front(direction='cw', tracker=tracker)
                break
            if case("F'"):
                front(direction='ccw', tracker=tracker)
                break
            if case("F2"):
                front(turn_180=1, tracker=tracker)
                break
            if case('B'):
                back(direction='cw', tracker=tracker)
                break
            if case("B'"):
                back(direction='ccw', tracker=tracker)
                break
            if case("B2"):
                back(turn_180=1, tracker=tracker)
                break



def right(direction=None, turn_180=None, tracker=None):
    send_command(0b0100) #right to top
    if direction == 'cw':
        send_command(0b0001) #turn cw
    elif direction == 'ccw':
        send_command(0b0010) #turn ccw
    elif turn_180:
        send_command(0b0011) #turn 180
    if tracker == None: send_command(0b0101) #right to top

def left(direction=None, turn_180=None, tracker=None):
    send_command(0b0101) #left to top
    if direction == 'cw':
        send_command(0b0001) #turn cw
    elif direction == 'ccw':
        send_command(0b0010) #turn ccw
    elif turn_180:
        send_command(0b0011) #turn 180
    if tracker == None: send_command(0b0100) #right to top

def front(direction=None, turn_180=None, tracker=None):
    send_command(0b0110) #front to top
    if direction == 'cw':
        send_command(0b0001) #turn cw
    elif direction == 'ccw':
        send_command(0b0010) #turn ccw
    elif turn_180:
        send_command(0b0011) #turn 180
    if tracker == None: send_command(0b0111) #back to top

def back(direction=None, turn_180=None, tracker=None):
    send_command(0b0111) #back to top
    if direction == 'cw':
        send_command(0b0001) #turn cw
    elif direction == 'ccw':
        send_command(0b0010) #turn ccw
    elif turn_180:
        send_command(0b0011) #turn 180
    if tracker == None: send_command(0b0110) #front to top

def down(direction=None, turn_180=None, tracker=None):
    send_command(0b0111) #back to top
    send_command(0b0111) #back to top
    if direction == 'cw':
        send_command(0b0001) #turn cw
    elif direction == 'ccw':
        send_command(0b0010) #turn ccw
    elif turn_180:
        send_command(0b0011) #turn 180
    if tracker == None:
        send_command(0b0110) #front to top
        send_command(0b0110) #front to top

def up(direction=None, turn_180=None, tracker=None):
    if direction == 'cw':
        send_command(0b0001) #turn cw
    elif direction == 'ccw':
        send_command(0b0010) #turn ccw
    elif turn_180:
        send_command(0b0011) #turn 180





# initialize the camera
cam = cv2.VideoCapture(4)
#cam.set(15, 0.1) #

# Start SCAN 1011
print "Acquiring cube..."
send_command(0b1011)


#cv2.namedWindow("CAM 04")
for idx,side in enumerate(['F', 'B', 'L', 'R', 'U', 'D']):
#        if idx == 3:
#            time.sleep(1)
        print "cam on"
        cnt = 0
        while True:
            ret, frame = cam.read()
            if not ret:
                print "Cam Error!"
                break
            #cnt = cnt + 1
            #cv2.imshow("CAM 04", frame)

            #k = cv2.waitKey(1)

            #if k%256 == 27:
            #    # ESC pressed
            #    print "Escape hit, closing..."
            #    break
            #elif k%256 == 32:
                # SPACE pressed
            if is_robot_ready():
                img_name = 'rubiks-side-' + side + '.png'
                print "Applying masking tape..."
                height,width,depth=frame.shape
                mask = np.full((height,width),255,np.uint8)
                mask[0:100,:] = 0 # top border
                mask[-110:height,:] = 0 #bottom border
                mask[:,0:180] = 0 #right border
                mask[:,-180:width] = 0 #left border
                mask[180:195,:] = 0 #upper horizontal
                mask[270:285,:] = 0 #lower horizontal
                mask[:,265:280] = 0 #right vertical
                mask[:,370:385] = 0 #left vertical
                img_masked = cv2.bitwise_and(frame,frame,mask=mask)
                if side=='U':
                    m = cv2.getRotationMatrix2D((width/2,height/2),180,1)
                    img_masked = cv2.warpAffine(img_masked,m,(width,height))
                cv2.imwrite(img_name, img_masked)
                print "Image #{}/6 ({}) written!".format(idx+1,img_name)
                #print idx
                send_command(0b0000) # pseudo tetrade for enable
                break

#cv2.destroyAllWindows()
cam.release()

print "Interpreting faces..."
def get_cube(debug_flag=False, directory='/home/jan/rubiks-cube-NxNxN-solver'): #PRODUCTION
#def get_cube(debug_flag=False, directory='/home/jan/rubiks-cube-tracker/test-data/3x3x3-random-01'): #TEST
    data = {}

    if not os.path.isdir(directory):
        sys.stderr.write("ERROR: directory %s does not exist\n", directory)
        sys.exit(1)
    cube_size = None

    for (side_index, side_name) in enumerate(('U', 'L', 'F', 'R', 'B', 'D')):
        filename = os.path.join(directory, "rubiks-side-%s.png" % side_name)

        if os.path.exists(filename):
            #log.info("filename %s, side_index %s, side_name %s" % (filename, side_index, side_name))

            #log.info("filename %s, side_index %s, side_name %s" % (filename, side_index, side_name))
            rimg = RubiksImage(side_index, side_name, debug=debug_flag)
            rimg.analyze_file(filename, cube_size)

            if cube_size is None:
                side_square_count = len(rimg.data.keys())
                cube_size = int(sqrt(side_square_count))

            data = merge_two_dicts(data, rimg.data)
            # log.info("cube_size %d" % cube_size)

        else:
            sys.stderr.write("ERROR: %s does not exist\n" % filename)
            sys.exit(1)

    return json.dumps(data, sort_keys=True)

cube_json = get_cube()
print cube_json
#input("Press Enter")

sub = subprocess.check_output(["/home/jan/cube_img/rubiks-color-resolver.py", "--rgb", get_cube()])

print sub
#input("Press Enter")

sub2 = subprocess.check_output(["/home/jan/rubiks-cube-NxNxN-solver/usr/bin/rubiks-cube-solver.py", "--state", sub])
print sub2
commands = sub2.split(": ")[1][:-1].split(" ")
print commands
#input("Press Enter")

#up(direction='cw')
n_commands = len(commands)
cube_tracker = cube_ori()
for command in commands:
    n_commands -= 1
    print "Next move: {} ({} more remaining)".format(command,n_commands)
    command_switcher(command,cube_tracker)

print "CUBE SOLVED"
