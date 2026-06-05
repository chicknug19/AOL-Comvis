from scipy.spatial import distance as dist

class FatigueDetector:
    def __init__(self, 
                 ear_drowsy=0.23,     # Threshold EAR Kritis (Bahaya)
                 ear_warning=0.25,    # Threshold EAR Peringatan (Mulai lelah)
                 mar_threshold=0.6,   # Threshold Mulut (Menguap)
                 head_threshold=1.5,  # Threshold Kepala menunduk
                 consecutive_frames=5):
        
        self.ear_drowsy = ear_drowsy
        self.ear_warning = ear_warning
        self.mar_threshold = mar_threshold
        self.head_threshold = head_threshold
        self.consecutive_frames = consecutive_frames
        
        # Counter untuk masing-masing pemicu
        self.ear_counter = 0
        self.warning_counter = 0
        self.yawn_counter = 0
        
        # Status utama (0: Alert, 5: Warning, 10: Drowsy)
        self.status = 0 

    def calculate_ear(self, eye):
        # Euclidean vertikal
        A = dist.euclidean(eye[1], eye[5]) 
        B = dist.euclidean(eye[2], eye[4]) 
        # Euclidean horizontal
        C = dist.euclidean(eye[0], eye[3]) 
        
        ear = (A + B) / (2.0 * C)
        return ear

    def calculate_mar(self, mouth):
        # Menghitung jarak vertikal bibir atas dan bawah
        A = dist.euclidean(mouth[2], mouth[10]) # 51, 59
        B = dist.euclidean(mouth[4], mouth[8])  # 53, 57
        # Menghitung jarak horizontal ujung bibir
        C = dist.euclidean(mouth[0], mouth[6])  # 49, 55
        
        mar = (A + B) / (2.0 * C)
        return mar

    def calculate_head_drop(self, nose_bridge, nose_tip, chin):
        # Menghitung rasio hidung bagian atas ke ujung hidung, vs ujung hidung ke dagu.
        # Saat kepala menunduk, jarak hidung-ke-dagu akan menyempit di kamera (2D).
        upper_face = dist.euclidean(nose_bridge, nose_tip)
        lower_face = dist.euclidean(nose_tip, chin)
        
        # Menghindari pembagian dengan nol
        if lower_face == 0:
            return 0
            
        ratio = upper_face / lower_face
        return ratio

    def check_drowsiness(self, left_eye, right_eye, mouth, nose_bridge, nose_tip, chin):
        # 1. Hitung Semua Metrik
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        mar = self.calculate_mar(mouth)
        head_ratio = self.calculate_head_drop(nose_bridge, nose_tip, chin)

        # 2. LOGIKA EVALUASI (Prioritas dari Bahaya ke Aman)
        
        # KONDISI MERAH (DROWSY - LABEL 10)
        # Terjadi jika: Mata sangat tertutup ATAU kepala menunduk tajam
        if avg_ear < self.ear_drowsy or head_ratio > self.head_threshold:
            self.ear_counter += 1
            if self.ear_counter >= self.consecutive_frames:
                self.status = 10
                
        # KONDISI KUNING (WARNING / HALF-DROWSY - LABEL 5)
        # Terjadi jika: Mata mulai menyipit di area abu-abu ATAU terdeteksi menguap
        elif avg_ear < self.ear_warning or mar > self.mar_threshold:
            self.ear_counter = 0 # Reset bahaya karena mata belum benar-benar tertutup
            self.warning_counter += 1
            if self.warning_counter >= self.consecutive_frames:
                self.status = 5
                
        # KONDISI HIJAU (ALERT - LABEL 0)
        else:
            self.ear_counter = 0
            self.warning_counter = 0
            self.status = 0

        # Kembalikan semua metrik untuk kebutuhan print/log dan statusnya
        return avg_ear, mar, head_ratio, self.status