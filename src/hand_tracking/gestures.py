"""
Gesture Recognition - FIXED VERSION
Enhanced gesture recognition with consistent gesture names
"""

import numpy as np
import time
import math
import logging

class GestureRecognizer:
    def __init__(self, threshold=0.7, cooldown=1.0):
        """Initialize gesture recognizer"""
        self.threshold = threshold
        self.cooldown = cooldown
        self.last_gesture_time = 0
        self.last_gesture = None
        self.logger = logging.getLogger('GestureRecognizer')
        
        # Gesture confidence tracking
        self.gesture_buffer = []
        self.buffer_size = 3
        
    def recognize_gesture(self, landmarks):
        """Main gesture recognition method"""
        try:
            if not landmarks or len(landmarks) < 21:
                return None
            
            current_time = time.time()
            
            if current_time - self.last_gesture_time < self.cooldown:
                return self.last_gesture
            
            points = np.array(landmarks)
            
            gesture = self._classify_gesture(points)
            
            gesture = self._smooth_gesture(gesture)
            
            if gesture:
                self.last_gesture_time = current_time
                self.last_gesture = gesture
                self.logger.debug(f"Gesture recognized: {gesture}")
            
            return gesture
            
        except Exception as e:
            self.logger.error(f"Error in gesture recognition: {e}")
            return None
    
    def _smooth_gesture(self, gesture):
        """Smooth gesture recognition to reduce false positives"""
        self.gesture_buffer.append(gesture)
        
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        
        if len(self.gesture_buffer) >= 2:
            if self.gesture_buffer[-1] == self.gesture_buffer[-2] and gesture:
                return gesture
        
        return None
    
    def _classify_gesture(self, points):
        """Classify hand gesture based on landmarks"""
        try:
           
            if len(points) < 21:
                return None
            
            fingers_up = self._get_fingers_up(points)
            
            total_fingers = sum(fingers_up)
            
            gesture = self._determine_gesture(fingers_up, total_fingers, points)
            
            return gesture
            
        except Exception as e:
            self.logger.error(f"Error classifying gesture: {e}")
            return None
    
    def _get_fingers_up(self, points):
        """Determine which fingers are up"""
        fingers_up = []
        
        tip_ids = [4, 8, 12, 16, 20]  
        pip_ids = [3, 6, 10, 14, 18] 
        
        try:
           
            if points[tip_ids[0]][0] > points[pip_ids[0]][0]:  
                fingers_up.append(1)
            else:
                fingers_up.append(0)
            
            for i in range(1, 5):
                if points[tip_ids[i]][1] < points[pip_ids[i]][1]:
                    fingers_up.append(1)
                else:
                    fingers_up.append(0)
            
            return fingers_up
            
        except Exception as e:
            self.logger.error(f"Error determining finger states: {e}")
            return [0, 0, 0, 0, 0]
    
    def _determine_gesture(self, fingers_up, total_fingers, points):
        """Determine gesture based on finger states and positions"""
        try:
            
            if total_fingers == 5:
                return "membuka_tangan"
            
            elif total_fingers == 0:
                return "menutup_tangan"
            
            elif fingers_up == [1, 0, 0, 0, 0]:
                
                thumb_tip = points[4]
                thumb_mcp = points[2]
                if thumb_tip[1] < thumb_mcp[1]: 
                    return "suka"
            
            elif fingers_up == [1, 0, 0, 0, 0]:
                thumb_tip = points[4]
                thumb_mcp = points[2]
                if thumb_tip[1] > thumb_mcp[1]: 
                    return "tidak_suka"
            
            elif fingers_up == [0, 1, 1, 0, 0]:
                index_tip = points[8]
                middle_tip = points[12]
                distance = self._calculate_distance(index_tip, middle_tip)
                
                if distance > 30: 
                    return "peace_sign"
                
            elif fingers_up == [0, 1, 0, 0, 0]:
                index_tip = points[8]
                index_mcp = points[5]
                if index_tip[1] < index_mcp[1]: 
                    return "point_up"
            
            elif total_fingers == 1 and fingers_up[1] == 1:
                return "point_up"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error determining gesture: {e}")
            return None
    
    def _calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        try:
            return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        except:
            return 0
    
    def _get_angle(self, p1, p2, p3):
        """Calculate angle between three points"""
        try:
            v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except:
            return 0
    
    def get_gesture_info(self, gesture):
        """Get human-readable gesture information"""
        gesture_info = {
            "membuka_tangan": {
                "name": "Open Palm",
                "action": "Play",
                "description": "All fingers extended"
            },
            "menutup_tangan": {
                "name": "Closed Fist", 
                "action": "Pause",
                "description": "All fingers closed"
            },
            "suka": {
                "name": "Thumbs Up",
                "action": "Volume Up", 
                "description": "Thumb pointing upward"
            },
            "tidak_suka": {
                "name": "Thumbs Down",
                "action": "Volume Down",
                "description": "Thumb pointing downward"
            },
            "peace_sign": {
                "name": "Peace Sign",
                "action": "Next Track",
                "description": "Index and middle fingers up"
            },
            "point_up": {
                "name": "Point Up", 
                "action": "Previous Track",
                "description": "Index finger pointing up"
            }
        }
        
        return gesture_info.get(gesture, {
            "name": "Unknown",
            "action": "None", 
            "description": "Gesture not recognized"
        })