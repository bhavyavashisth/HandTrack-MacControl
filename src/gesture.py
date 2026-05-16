"""
Gesture classification and detection for Gesture Control System.
"""

from src.config import TIP, PIP
from src.helpers import dist

# ═══════════════════════════════════════════════════════════
#  GESTURE CLASSIFICATION
# ═══════════════════════════════════════════════════════════
def finger_states(lm):
    """
    Determine which fingers are extended.
    Returns a list of booleans: [thumb, index, middle, ring, pinky]
    """
    up = [lm[4].x < lm[3].x]   # thumb
    for i in range(1, 5):
        up.append(lm[TIP[i]].y < lm[PIP[i]].y)
    return up

def classify_gesture(lm):
    """
    Classify the hand gesture based on landmarks.
    
    Returns one of:
        POINT, PINCH, THREE, TWO, FIST, PALM, THUMB, MIDDLE, 
        PINKY, IDX_RING, IDX_PINKY, UNKNOWN
    """
    up = finger_states(lm)
    n  = sum(up)
    thumb, index, middle, ring, pinky = up

    # pinch beats everything
    if dist(lm[4], lm[8]) < 0.06:
        return "PINCH"

    if n == 0:                                              return "FIST"
    if n == 5:                                              return "PALM"
    if thumb  and not index and not middle and not ring and not pinky: return "THUMB"
    if index  and not middle and not ring  and not pinky:              return "POINT"
    if not index and middle and not ring   and not pinky:              return "MIDDLE"
    if not index and not middle and not ring and pinky:                return "PINKY"
    if index  and middle and not ring and not pinky:                   return "TWO"
    if index  and middle and ring and not pinky:                       return "THREE"
    if index  and not middle and ring and not pinky:                   return "IDX_RING"
    if index  and not middle and not ring and pinky:                   return "IDX_PINKY"
    return "UNKNOWN"
