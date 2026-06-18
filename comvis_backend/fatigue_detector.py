from scipy.spatial import distance as dist

class FatigueDetector:
    def __init__(self, 
                 ear_drowsy=0.23,     
                 ear_warning=0.25,    
                 mar_threshold=0.6,   
                 consecutive_frames=9):
        
        self.ear_drowsy = ear_drowsy
        self.ear_warning = ear_warning
        self.mar_threshold = mar_threshold
        self.consecutive_frames = consecutive_frames
        
        self.ear_counter = 0
        self.warning_counter = 0
        self.status = 0 

    def calculate_ear(self, eye):
        A = dist.euclidean(eye[1], eye[5]) 
        B = dist.euclidean(eye[2], eye[4]) 
        C = dist.euclidean(eye[0], eye[3]) 
        return (A + B) / (2.0 * C)

    def calculate_mar(self, mouth):
        A = dist.euclidean(mouth[2], mouth[10])
        B = dist.euclidean(mouth[4], mouth[8]) 
        C = dist.euclidean(mouth[0], mouth[6])  
        return (A + B) / (2.0 * C)

    def check_drowsiness(self, left_eye, right_eye, mouth):
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        mar = self.calculate_mar(mouth)

        if avg_ear < self.ear_drowsy:
            self.ear_counter += 1
            if self.ear_counter >= self.consecutive_frames:
                self.status = 10
                
        elif avg_ear < self.ear_warning or mar > self.mar_threshold:
            self.ear_counter = 0 
            self.warning_counter += 1
            if self.warning_counter >= self.consecutive_frames:
                self.status = 5
                
        else:
            self.ear_counter = 0
            self.warning_counter = 0
            self.status = 0

        return avg_ear, mar, self.status