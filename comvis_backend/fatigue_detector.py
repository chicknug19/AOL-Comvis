from scipy.spatial import distance as dist

class FatigueDetector:
    def __init__(self, ear_threshold=0.25, consecutive_frames=30):
        # ear_threshold: Batas nilai EAR di mana mata dianggap tertutup
        # consecutive_frames: Batas jumlah frame berturut-turut (30 frame ~ 1 detik)
        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        
        # Variabel untuk mengingat status saat ini
        self.frame_counter = 0
        self.alarm_on = False

    def calculate_ear(self, eye):
        # Menghitung jarak euclidean (garis lurus) vertikal
        A = dist.euclidean(eye[1], eye[5]) # ||p2 - p6||
        B = dist.euclidean(eye[2], eye[4]) # ||p3 - p5||
        
        # Menghitung jarak euclidean horizontal
        C = dist.euclidean(eye[0], eye[3]) # ||p1 - p4||
        
        # Rumus utama EAR
        ear = (A + B) / (2.0 * C)
        return ear

    def check_drowsiness(self, left_eye, right_eye):
        # Hitung EAR kedua mata dan ambil rata-ratanya
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        # TEMPORAL THRESHOLDING LOGIC
        # Jika nilai EAR di bawah batas (mata tertutup)
        if avg_ear < self.ear_threshold:
            self.frame_counter += 1 # Tambah hitungan frame
            
            # Jika mata tertutup lebih lama dari batas waktu (misal 1 detik)
            if self.frame_counter >= self.consecutive_frames:
                self.alarm_on = True # Nyalakan alarm
        else:
            # Jika mata terbuka lagi, reset semua hitungan ke nol (ini berarti cuma kedip biasa)
            self.frame_counter = 0
            self.alarm_on = False

        return avg_ear, self.alarm_on