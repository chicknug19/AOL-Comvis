import cv2
import dlib
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from fatigue_detector import FatigueDetector

app = Flask(__name__)
CORS(app) # Mengizinkan React mengakses API ini

# Inisialisasi logika menggunakan versi terbaru yang memiliki fase Warning
detector_logic = FatigueDetector(ear_drowsy=0.23, consecutive_frames=5)
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({"error": "Tidak ada gambar yang diterima"}), 400

        # 1. Menerima gambar base64 dari React dan mengubahnya ke OpenCV
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # 2. Deteksi wajah dengan HOG
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray_frame, 0)

        status_text = "Aman (Alert)"
        ear_value = 0.0

        if len(faces) == 0:
            return jsonify({"ear": 0.0, "status": "Wajah tidak terdeteksi", "image": data['image']})

        for face in faces:
            # Prediksi 68 titik wajah
            shape = landmark_predictor(gray_frame, face)
            landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            # Ekstraksi area spesifik sesuai indeks Dlib
            rightEye = landmarks[36:42]
            leftEye = landmarks[42:48]
            mouth = landmarks[48:68]
            nose_bridge = landmarks[27] # Pangkal hidung
            nose_tip = landmarks[30]    # Ujung hidung
            chin = landmarks[8]         # Ujung dagu bawah

            # 3. Panggil logika pendeteksi dari fatigue_detector.py
            avg_ear, mar, head_ratio, status_code = detector_logic.check_drowsiness(
                leftEye, rightEye, mouth, nose_bridge, nose_tip, chin
            )

            # 4. Tentukan warna kotak (Visual Feedback) dan teks berdasarkan status
            color = (0, 255, 0) # BGR: Hijau (Alert)
            if status_code == 10:
                status_text = "BAHAYA: DROWSY! (Ngantuk)"
                color = (0, 0, 255) # BGR: Merah
            elif status_code == 5:
                status_text = "WARNING: Mulai Lelah / Menguap"
                color = (0, 255, 255) # BGR: Kuning

            # --- MENGGAMBAR KOTAK & TITIK UNTUK DEMO DOSEN ---
            # Menggambar kontur melingkari mata dan mulut
            cv2.drawContours(frame, [np.array(leftEye)], -1, color, 1)
            cv2.drawContours(frame, [np.array(rightEye)], -1, color, 1)
            cv2.drawContours(frame, [np.array(mouth)], -1, color, 1)
            
            # Menggambar titik dan garis untuk postur kepala
            cv2.circle(frame, nose_bridge, 3, color, -1)
            cv2.circle(frame, nose_tip, 3, color, -1)
            cv2.circle(frame, chin, 3, color, -1)
            cv2.line(frame, nose_bridge, nose_tip, color, 1)
            cv2.line(frame, nose_tip, chin, color, 1)

        # 5. Ubah frame yang sudah dicoret-coret kembali menjadi base64
        _, buffer = cv2.imencode('.jpg', frame)
        processed_image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

        # 6. Kirim semua data kembali ke React
        return jsonify({
            "ear": float(ear_value), 
            "status": status_text,
            "image": processed_image_base64 # Ini adalah frame baru bergaris
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7860)