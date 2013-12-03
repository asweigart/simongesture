"""
"MooseGesture 0.1.4" a mouse gestures recognition library.
Al Sweigart al@coffeeghost.net
http://coffeeghost.net/2011/05/09/moosegesture-python-mouse-gestures-module

Usage:
    import moosegesture
    gesture = moosegesture.getGesture(points)

Where "points" is a list of x, y coordinate tuples, e.g. [(100, 200), (1234, 5678), ...]
getGesture returns a list of integers for the recognized mouse gesture. The integers
correspond to the 8 cardinal and diagonal directions:

  up-left    up   up-right
         7   8   9

    left 4       6 right

         1   2   3
down-left   down  down-right

Second usage:
    strokes  = [2, 4, 6]
    gestures = [[2, 4, 2], [2, 6, 9]]
    gesture = moosegesture.findClosestMatchingGesture(strokes, gestures)

    gesture == [2, 4, 2]

Where "strokes" is a list of the directional integers that are returned from
getGesture(). This returns the closest resembling gesture from the list of
gestures that is passed to the function.

The optional "tolerance" parameter can ensure that the "closest" identified
gesture isn't too different.


Explanation of the nomenclature in this module:
    A "point" is a 2D tuple of x, y values. These values can be ints or floats,
    MooseGesture supports both.

    A "point pair" is a point and its immediately subsequent point, i.e. two
    points that are next to each other.

    A "segment" is two or more ordered points forming a series of lines.

    A "stroke" is a segment going in a single direction (one of the 8 cardinal or
    diagonal directions: up, upright, left, etc.)

    A "gesture" is one or more strokes in a specific pattern, e.g. up then right
    then down then left.


# Copyright (c) 2011, Al Sweigart
# All rights reserved.
#
# BSD-style license:
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the MooseGesture nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Al Sweigart "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Al Sweigart BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from math import sqrt, atan, pi
from sys import maxsize

# This is the minimum distance the mouse must travel (in pixels) before a
# segment will be considered for stroke interpretation.
_MIN_SEG_LEN = 60

_MIN_P2P_DISTANCE = 10

# The integers-to-directions mapping matches the keypad:
#   7 8 9
#   4   6
#   1 2 3
DOWNLEFT = 1
DOWN = 2
DOWNRIGHT = 3
LEFT = 4
RIGHT = 6
UPLEFT = 7
UP = 8
UPRIGHT = 9

_strokesStrings = {DOWNLEFT:'DL', DOWN:'D', DOWNRIGHT:'DR', LEFT:'L', RIGHT:'R', UPLEFT:'UL', UP:'U', UPRIGHT:'UR'}


def getGesture(points, mode='all'):
    """Returns a gesture as a list of directional integers, i.e. [2,6,4] for
    the down-left-right gesture.

    The points parameter is a list of tuples of XY points that make up the
    user's mouse gesture.

    The mode parameter is set to 'all' by default. The mode determines which
    directions the function will identify. It can be set to one of:
        'all' - Recognize all 8 cardinal directions.
        'cross' - Recognize the 4 horizontal & vertical directions.
        'diagonal' - Recognize the 4 diagonal directions."""
    return _identifyStrokes(points, mode)[0]


def getSegments(points, mode='all'):
    """Returns a list of tuples of integers. The tuples are the start and end
    indexes of the points that make up a consistent stroke.

    The points parameter is a list of tuples of XY points that make up the
    user's mouse gesture.

    The mode parameter is set to 'all' by default. The mode determines which
    directions the function will identify. It can be set to one of:
        'all' - Recognize all 8 cardinal directions.
        'cross' - Recognize the 4 horizontal & vertical directions.
        'diagonal' - Recognize the 4 diagonal directions."""
    return _identifyStrokes(points, mode)[1]


def getGestureAndSegments(points, mode='all'):
    """Returns a list of tuples. The first item in the tuple is the directional
    integer, and the second item is a tuple of integers for the start and end
    indexes of the points that make up the stroke.

    The points parameter is a list of tuples of XY points that make up the
    user's mouse gesture.

    The mode parameter is set to 'all' by default. The mode determines which
    directions the function will identify. It can be set to one of:
        'all' - Recognize all 8 cardinal directions.
        'cross' - Recognize the 4 horizontal & vertical directions.
        'diagonal' - Recognize the 4 diagonal directions."""
    strokes, strokeSegments = _identifyStrokes(points, mode)
    return list(zip(strokes, strokeSegments))


def getGestureStr(strokes):
    """Returns a string of space-delimited text characters that represent the
    strokes passed in. For example, getGestureStr([2, 6, 4]) returns "D R L".

    The strokes parameter is a list of directional integers, like the kind
    returned by getGesture()."""
    if len(strokes) and type(strokes[0]) == int:
        # points is a list of directional integers, returned from getGesture()
        return ' '.join(_strokesStrings[x] for x in strokes)


def findClosestMatchingGesture(strokes, gestureList, tolerance=maxsize):
    """Returns the gesture in gestureList that closest matches the gesture in
    strokes. The tolerance is how many differences there can be and still
    be considered a match."""
    if len(gestureList) == 0:
        return None

    strokes = ''.join(strokes)
    gestureList = [''.join(x) for x in gestureList]
    gestureList = list(frozenset(gestureList)) # make a unique list
    distances = {}
    for g in gestureList:
        dist = levenshteinDistance(strokes, g)
        if dist in distances:
            distances[dist].append(g)
        else:
            distances[dist] = [g]
    smallestKey = min(distances.keys())
    if len(distances[smallestKey]) == 1 and smallestKey <= tolerance:
        return [int(x) for x in distances[min(distances.keys())]]
    else:
        return None


def levenshteinDistance(s1, s2):
    """Returns the Levenshtein Distance (aka "edit distance") between two
    strings as an integer.

    http://en.wikipedia.org/wiki/Levenshtein_getDistance
    The Levenshtein Distance (aka edit distance) is how many changes (i.e.
    insertions, deletions, substitutions) have to be made to convert one
    string into another.

    For example, the Levenshtein distance between "kitten" and "sitting" is
    3, since the following three edits change one into the other, and there
    is no way to do it with fewer than three edits:
      kitten -> sitten -> sittin -> sitting"""
    len1 = len(s1)
    len2 = len(s2)

    matrix = list(range(len1 + 1)) * (len2 + 1)
    for i in range(len2 + 1):
        matrix[i] = list(range(i, i + len1 + 1))
    for i in range(len2):
        for j in range(len1):
            if s1[j] == s2[i]:
                matrix[i+1][j+1] = min(matrix[i+1][j] + 1, matrix[i][j+1] + 1, matrix[i][j])
            else:
                matrix[i+1][j+1] = min(matrix[i+1][j] + 1, matrix[i][j+1] + 1, matrix[i][j] + 1)
    return matrix[len2][len1]

editDistance = levenshteinDistance # I just realized that people might not like typing out "levenshtein"


def setMinStrokeLen(val):
    """Set the length (in pixels) a stroke must be to be recognized as a
    stroke. This is a global value"""
    global _MIN_SEG_LEN, _MIN_P2P_DISTANCE
    _MIN_SEG_LEN = val
    if val < _MIN_P2P_DISTANCE:
        _MIN_P2P_DISTANCE = val


def getMinStrokeLen():
    """Get the minimum segment length."""
    return _MIN_SEG_LEN




# Private Functions:

def _identifyStrokes(points, mode='all'):
    strokes = []
    strokeSegments = []

    # calculate lengths between each sequential points
    distances = []
    for i in range(len(points)-1):
        distances.append( _getDistance(points[i], points[i+1]) )
    # keeps getting points until we go past the min. segment length
    #startSegPoint = 0
    #while startSegPoint < len(points)-1:
    for startSegPoint in range(len(points)-1):
        segmentDist = 0
        curDir = None
        consistent = True
        direction = None
        for curSegPoint in range(startSegPoint, len(points)-1):
            segmentDist += distances[curSegPoint]
            if segmentDist >= _MIN_SEG_LEN:
                # check if all points are going the same direction.
                i = startSegPoint
                pointToPointDistance = 0
                nextPoint = 0
                while i < curSegPoint+1:
                #for i in range(startSegPoint, curSegPoint+1):
                    nextPoint += 1
                    if i + nextPoint >= len(points):
                        break
                    pointToPointDistance += distances[i]
                    if pointToPointDistance < _MIN_P2P_DISTANCE:
                        i += 1
                        continue
                    direction = _getDirection(points[i], points[i+nextPoint], mode)
                    if curDir is None:
                        curDir = direction
                    elif direction != curDir:
                        consistent = False
                        break
                    i += nextPoint
                    pointToPointDistance = 0
                    nextPoint = 0
                break
        if not consistent:
            continue
        elif (direction is not None and ( (not len(strokes)) or (len(strokes) and strokes[-1] != direction) )):
            strokes.append(direction)
            strokeSegments.append( [startSegPoint, curSegPoint] )
        elif len(strokeSegments):
            # update and lengthen the latest stroke since this stroke is being lengthened.
            strokeSegments[-1][1] = curSegPoint
    return strokes, strokeSegments

def _getDirection(pos1, pos2, mode='all'):
    """Return the integer of one of the 8 directions this line is going in.
    pos1 and pos2 are (x, y) integers coordinates."""
    assert mode in ('all', 'cross', 'diagonal'), "mode parameter must be one of 'all', 'cross', or 'diagonal', not %s'" % (mode)

    angle = getAngle(pos1, pos2)

    if mode == 'all':
        if angle >= 337.5 or angle < 22.5:
            return RIGHT
        elif angle >= 22.5 and angle < 67.5:
            return UPRIGHT
        elif angle >= 67.5 and angle < 112.5:
            return UP
        elif angle >= 112.5 and angle < 157.5:
            return UPLEFT
        elif angle >= 157.5 and angle < 202.5:
            return LEFT
        elif angle >= 202.5 and angle < 247.5:
            return DOWNLEFT
        elif angle >= 247.5 and angle < 292.5:
            return DOWN
        elif angle >= 292.5 and angle < 337.5:
            return DOWNRIGHT
    elif mode == 'cross':
        if angle >= 315 or angle < 45:
            return RIGHT
        elif angle >= 45 and angle < 135:
            return UP
        elif angle >= 135 and angle < 225:
            return LEFT
        elif angle >= 225 and angle < 315:
            return DOWN
    elif mode == 'diagonal':
        if angle >= 0 and angle < 90:
            return UPRIGHT
        elif angle >= 90 and angle < 180:
            return UPLEFT
        elif angle >= 180 and angle < 270:
            return DOWNLEFT
        elif angle >= 270:
            return DOWNRIGHT

def _getDistance(pos1, pos2):
    """Return distance between two points. This is a basic pythagorean theorem calculation.
    pos1 and pos2 are (x, y) integers coordinates."""
    xdist = pos1[0] - pos2[0]
    ydist = pos1[1] - pos2[1]
    return sqrt(xdist*xdist + ydist*ydist)


def getAngle(origin, pos):
    x = pos[0] - origin[0]
    y = pos[1] - origin[1]

    if x == 0:
        if y <= 0: # (0, 0) for (x, y) will result in UP
            return 90.0
        else:
            return 270.0

    slope = (y) / float(x) # rise over run
    angle = atan( slope ) * (180 / pi)

    # make adjustments for which quadrant the event is in.
    if y >= 0 and x >= 0: # if lower right quadrant
        angle = (90 - angle) + 270
    elif y >= 0 and x < 0: # if lower left quadrant
        angle = -angle + 180
    elif y < 0 and x < 0: # if upper left quadrant
        angle = (90 - angle) + 90
    elif y < 0 and x >= 0: # if upper right quadrant
        angle = -angle

    if angle == 360.0:
        return 0.0
    else:
        return angle