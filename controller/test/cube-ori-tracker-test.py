
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

tracker = cube_ori()
#tracker2 = cube_ori()

#print tracker.getRotateSteps('F')
#print tracker2.getRotateSteps('R')

for req in "UFRDRLBU":
    print "Request:" + req
    print "Actual:" + tracker.getActualSide(req,debug=True)
    print ""

"""
print 'rotate on x'
tracker.rot_x()
print '\nrotate on y'
tracker2.rot_y()
print 'Tracker 1:{}'.format(tracker.unwrap())
#print 'Tracker 2:{}'.format(tracker2.unwrap())
print ''

print 'RtT'
tracker.rot_x()
print 'Tracker 1:{}'.format(tracker.unwrap())
print 'BtT'
tracker.rot_y()
print 'Tracker 1:{}'.format(tracker.unwrap())
"""
#print 'Tracker 2:{}'.format(tracker2.unwrap())
#print ''
