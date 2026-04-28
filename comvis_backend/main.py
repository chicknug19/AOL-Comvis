import cv2
import dlib
from flask import Flask, Response
from flask_cors import CORS
from fatigue_detector import FatigueDetector

# Membuat aplikasi server Flask
app = Flask(__name__)
CORS(app) # Sangat penting: agar React diizinkan mengambil video dari Python

# Inisialisasi logika dan dlib
detector_logic = FatigueDetector(ear_threshold=0.25, consecutive_frames=30)
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Index titik mata dari dlib
(lStart, lEnd) = (42, 48)
(rStart, rEnd) = (36, 42)

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Preprocessing
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray_frame, 0)

        for face in faces:
            shape = landmark_predictor(gray_frame, face)
            landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            leftEye = landmarks[lStart:lEnd]
            rightEye = landmarks[rStart:rEnd]

            # Cek status ngantuk
            ear, alarm_status = detector_logic.check_drowsiness(leftEye, rightEye)

            # Gambar visualisasi di atas frame
            for (x, y) in leftEye + rightEye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            if alarm_status:
                cv2.putText(frame, "WARNING: DROWSY!", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        # BAGIAN PALING PENTING UNTUK WEB:
        # Mengubah frame gambar menjadi format byte JPEG untuk dikirim ke React
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Memancarkan (streaming) gambar ke URL
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Membuat jalur (URL) untuk diambil oleh React
@app.route('/video_feed')
def video_feed():
    # Mengembalikan hasil streaming tanpa henti
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # Menjalankan server di port 5000 (tidak memunculkan popup cv2.imshow)
    app.run(host='0.0.0.0', port=5000, debug=True)