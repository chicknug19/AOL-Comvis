import React, { useRef, useState, useEffect, useCallback } from 'react';
import Webcam from 'react-webcam';
import iconSafety from './assets/Iconsafety.png';
import bgMorningRide from './assets/morningride.jpg';
import alarmSound from './assets/drowsy.mpeg'; 

const DrowsinessDetector = () => {
  const webcamRef = useRef(null);
  const audioRef = useRef(typeof Audio !== "undefined" ? new Audio(alarmSound) : null);
  const [status, setStatus] = useState('Menunggu koneksi...');
  const [earValue, setEarValue] = useState(0.0);
  const [isDetecting, setIsDetecting] = useState(false);
  const [isLoadingCam, setIsLoadingCam] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [processedImage, setProcessedImage] = useState(null);

  const isDetectingRef = useRef(false);

  const HF_API_URL = "https://chicknug19-aol-comvis.hf.space/api/predict"; 

  useEffect(() => {
    isDetectingRef.current = isDetecting;
  }, [isDetecting]);

  const captureAndSendFrame = useCallback(async () => {
    if (webcamRef.current && isDetectingRef.current && !isLoadingCam) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        try {
          const response = await fetch(HF_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageSrc }),
          });
          if (!response.ok) throw new Error('Jaringan bermasalah');
          const data = await response.json();
          
          if (isDetectingRef.current) {
            setEarValue(data.ear);
            setStatus(data.status);
            if (data.image) {
               setProcessedImage(data.image);
            }
          }
        } catch (error) {
          console.error("Gagal mengirim frame:", error);
          if (isDetectingRef.current) {
            setStatus("Error koneksi API");
          }
        }
      }
    }
  }, [isLoadingCam]);

  useEffect(() => {
    let interval;
    if (isDetecting && !isLoadingCam) {
      interval = setInterval(captureAndSendFrame, 150); 
    } else {
      clearInterval(interval);
      if (!isDetecting) {
        setStatus('Menunggu koneksi...');
        setEarValue(0.0);
        setProcessedImage(null);
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        }
      }
    }
    return () => clearInterval(interval);
  }, [isDetecting, isLoadingCam, captureAndSendFrame]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.loop = true; 
      
      const isDrowsy = status.toLowerCase().includes('drowsy') || status.toLowerCase().includes('ngantuk') || status.toLowerCase().includes('warning') || status.toLowerCase().includes('lelah');
      
      if (isDrowsy && isDetectingRef.current) {
        audioRef.current.play().catch((err) => console.log("Audio diblokir browser:", err));
      } else {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    }
  }, [status]);
  
  const getStatusColor = () => {
    if (status.toLowerCase().includes('drowsy') || status.toLowerCase().includes('ngantuk')) return '#ef4444';
    if (status.toLowerCase().includes('warning') || status.toLowerCase().includes('lelah')) return '#eab308';
    if (status.toLowerCase().includes('alert') || status.toLowerCase().includes('aman')) return '#22c55e';
    return '#3b82f6'; 
  };
  
  const statusColor = getStatusColor();
  
  const handleToggleCamera = () => {
    if (!isDetecting) {
      setIsLoadingCam(true); 
    } else {
      setStatus('Menunggu koneksi...');
      setEarValue(0.0);
      setProcessedImage(null);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    }
    setIsDetecting(!isDetecting);
  };

  const getButtonBgColor = () => {
    if (isDetecting) {
      return isHovered ? '#dc2626' : '#ef4444'; 
    }
    return isHovered ? '#2563eb' : '#3b82f6'; 
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
      backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.9)), url(${bgMorningRide})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      color: '#f8fafc'
    }}>   
      <div style={{
        backgroundColor: 'rgba(30, 41, 59, 0.6)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '24px',
        padding: '30px',
        width: '100%',
        maxWidth: '800px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
      }}>
        
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <img src={iconSafety} alt="Safety Icon" style={{ width: '80px', marginBottom: '10px' }} /> 
          <h2 style={{ 
            margin: '0', 
            fontSize: '28px', 
            fontWeight: 'bold',
            background: `linear-gradient(to right, #60a5fa, ${statusColor})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            transition: 'all 0.3s ease'
          }}>
            Driver Drowsiness Detection System
          </h2>
          <p style={{ color: '#94a3b8', marginTop: '8px', fontSize: '14px' }}>
            Real-time EAR & Facial Landmarks Analysis
          </p>
        </div>
        
        <div style={{ 
          marginBottom: '25px', 
          position: 'relative',
          borderRadius: '16px',
          overflow: 'hidden',
          border: `4px solid ${isDetecting && !isLoadingCam ? statusColor : '#334155'}`,
          boxShadow: isDetecting && !isLoadingCam ? `0 0 20px ${statusColor}40` : 'none',
          transition: 'all 0.3s ease',
          backgroundColor: '#0f172a',
          aspectRatio: '16/9',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          
          {/* WEBCAM ASLI */}
          {isDetecting && (
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.5}
              videoConstraints={{ 
                 facingMode: "user",
                 width: 640,
                 height: 480 
              }}
              onUserMedia={() => setIsLoadingCam(false)}
              style={{ 
                position: 'absolute',
                width: '100%', 
                height: '100%',
                objectFit: 'cover',
                opacity: processedImage ? 0 : (isLoadingCam ? 0.3 : 1), 
                transition: 'opacity 0.2s ease-in-out'
              }}
            />
          )}

          {/* GAMBAR DARI FLASK (Titik dan Garis Wajah) */}
          {isDetecting && !isLoadingCam && processedImage && (
             <img 
               src={processedImage} 
               alt="Processed Frame"
               style={{
                 position: 'absolute',
                 width: '100%',
                 height: '100%',
                 objectFit: 'cover',
                 zIndex: 10
               }}
             />
          )}

          {!isDetecting && (
            <div style={{ position: 'absolute', color: '#64748b', fontSize: '18px', fontWeight: '500' }}>
              Kamera Nonaktif
            </div>
          )}
          {isLoadingCam && (
            <div style={{ position: 'absolute', color: '#f8fafc', fontSize: '18px', fontWeight: '500', zIndex: 20 }}>
              Meminta izin akses kamera...
            </div>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignItems: 'center' }}>
          <button 
            onClick={handleToggleCamera}
            disabled={isLoadingCam}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onMouseDown={(e) => !isLoadingCam && (e.currentTarget.style.transform = 'scale(0.98)')}
            onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
            style={{ 
              padding: '16px 24px', 
              fontSize: '16px', 
              fontWeight: 'bold',
              cursor: isLoadingCam ? 'not-allowed' : 'pointer',
              backgroundColor: getButtonBgColor(),
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              transition: 'background-color 0.2s, transform 0.1s, opacity 0.2s',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              width: '100%',
              opacity: isLoadingCam ? 0.7 : 1
            }}
          >
            {isLoadingCam ? '⏳ Memuat Kamera...' : (isDetecting ? '⏹ Hentikan Sistem' : '▶ Aktifkan Kamera')}
          </button>
          
          <div style={{ 
            padding: '15px 20px', 
            backgroundColor: 'rgba(15, 23, 42, 0.8)', 
            borderRadius: '12px',
            borderLeft: `5px solid ${statusColor}`,
            transition: 'all 0.3s ease'
          }}>
            <p style={{ margin: '0 0 5px 0', fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px' }}>
              Status Pengemudi
            </p>
            <p style={{ margin: '0 0 10px 0', fontSize: '22px', fontWeight: 'bold', color: statusColor, transition: 'color 0.3s ease' }}>
              {status}
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '10px' }}>
              <span style={{ fontSize: '13px', color: '#cbd5e1' }}>Nilai EAR Terkini:</span>
              <strong style={{ fontSize: '18px', color: '#f8fafc', fontFamily: 'monospace' }}>
                {earValue.toFixed(3)}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default DrowsinessDetector;
