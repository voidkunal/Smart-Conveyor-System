import cv2
import numpy as np
import math
from ultralytics import YOLO

# Importing from your config mapping
from config_mapping import PRODUCT_CATALOG, HAZARD_ITEMS, OVERLOAD_THRESHOLD

class ConveyorMonitor:
    def __init__(self):
        self.model = YOLO("yolov8s.pt")
        
        # CUSTOM CENTROID TRACKER STATE
        self.tracked_objects = {} 
        self.next_object_id = 0
        
        # TUNING PARAMETERS
        self.MAX_DISTANCE = 150  # Max pixels an object can move between frames
        self.MAX_MISSED_FRAMES = 5 # Forgive the AI if it blinks for 5 frames
        self.VOTING_FRAMES = 5 # Votes required to confirm a product
        
        # WARMUP PROTOCOL (Stops instant Admin Locks when USB camera turns on)
        self.warmup_frames = 0
        self.WARMUP_REQUIRED = 30

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def process_frame(self, frame):
        height, width = frame.shape[:2]
        current_state = {"products": [], "alerts": []}
        
        # --- CAMERA WARMUP ---
        self.warmup_frames += 1
        if self.warmup_frames < self.WARMUP_REQUIRED:
            cv2.rectangle(frame, (0, 0), (width, height), (0, 165, 255), 4)
            cv2.putText(frame, "SYSTEM WARMING UP - CALIBRATING OPTICS", (50, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 3)
            return frame, current_state

        # --- WIDE BILLING ZONE ---
        scan_zone_x1 = int(width * 0.35)
        scan_zone_x2 = int(width * 0.65)
        scan_zone_y1 = int(height * 0.20)
        scan_zone_y2 = int(height * 0.80)
        
        cv2.rectangle(frame, (scan_zone_x1, scan_zone_y1), (scan_zone_x2, scan_zone_y2), (0, 255, 255), 2)
        cv2.putText(frame, "TRACKING ZONE", (scan_zone_x1, scan_zone_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # --- AI INFERENCE ---
        # imgsz=480 forces it to run faster on the M1 CPU
        results = self.model.predict(frame, verbose=False, conf=0.35, imgsz=480)
        
        current_centroids = []
        items_in_frame = 0

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                class_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                items_in_frame += 1

                # 1. INSTANT SAFETY LOCK (Overrides everything)
                if class_id in HAZARD_ITEMS and conf > 0.30: 
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.putText(frame, "HAZARD LOCK!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                    current_state["alerts"].append(f"CRITICAL: {HAZARD_ITEMS[class_id]}")
                    return frame, current_state 

                # Store products for the tracking math
                if class_id in PRODUCT_CATALOG:
                    current_centroids.append((cx, cy, class_id, (x1, y1, x2, y2)))

        # --- CENTROID TRACKING MATH ---
        updated_object_ids = set()
        
        for cx, cy, class_id, bbox in current_centroids:
            matched_id = None
            min_dist = float('inf')
            
            # Find the closest existing object
            for obj_id, obj_data in self.tracked_objects.items():
                dist = self.calculate_distance((cx, cy), obj_data['centroid'])
                if dist < self.MAX_DISTANCE and dist < min_dist:
                    min_dist = dist
                    matched_id = obj_id
            
            if matched_id is not None:
                # Update existing object
                self.tracked_objects[matched_id]['centroid'] = (cx, cy)
                self.tracked_objects[matched_id]['missed_frames'] = 0
                self.tracked_objects[matched_id]['history'].append(class_id)
                self.tracked_objects[matched_id]['bbox'] = bbox
                updated_object_ids.add(matched_id)
            else:
                # Register new object
                self.tracked_objects[self.next_object_id] = {
                    'centroid': (cx, cy),
                    'history': [class_id],
                    'billed': False,
                    'missed_frames': 0,
                    'bbox': bbox
                }
                updated_object_ids.add(self.next_object_id)
                self.next_object_id += 1

        # --- BILLING LOGIC ---
        for obj_id in list(self.tracked_objects.keys()):
            obj = self.tracked_objects[obj_id]
            
            # If the AI lost sight of the object, count missed frames. Delete if it's gone too long.
            if obj_id not in updated_object_ids:
                obj['missed_frames'] += 1
                if obj['missed_frames'] > self.MAX_MISSED_FRAMES:
                    del self.tracked_objects[obj_id]
                continue
            
            # Voting Logic: Look at what it was identified as recently
            recent_history = obj['history'][-self.VOTING_FRAMES:]
            if len(recent_history) > 0:
                stable_class_id = max(set(recent_history), key=recent_history.count)
                product_info = PRODUCT_CATALOG[stable_class_id]
                
                cx, cy = obj['centroid']
                x1, y1, x2, y2 = obj['bbox']
                
                # BILLING TRIGGER: Must be in the zone, have enough votes, and not billed yet
                if (scan_zone_x1 < cx < scan_zone_x2 and scan_zone_y1 < cy < scan_zone_y2):
                    if len(obj['history']) >= self.VOTING_FRAMES and not obj['billed']:
                        
                        obj['billed'] = True
                        current_state["products"].append(product_info)
                        cv2.rectangle(frame, (0, 0), (width, height), (0, 255, 0), 10) 
                        
                
                if obj['billed']:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 100, 100), 2)
                    cv2.putText(frame, f"BILLED: {product_info['name']}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    vote_count = min(len(obj['history']), self.VOTING_FRAMES)
                    cv2.putText(frame, f"Voting ({vote_count}/{self.VOTING_FRAMES}): {product_info['name']}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        
        if items_in_frame >= OVERLOAD_THRESHOLD:
            current_state["alerts"].append("CRITICAL: Belt Overload / System Jam")
            cv2.putText(frame, "JAM DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)

        return frame, current_state