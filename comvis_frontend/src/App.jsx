import React from 'react';

function App() {
  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h1 style={{ color: '#333' }}>Automated Driver Fatigue Detection</h1>
      <p style={{ color: '#666' }}>Live Webcam Monitoring System</p>
      
      {/* Container untuk Video */}
      <div style={{ 
        border: '5px solid #222', 
        display: 'inline-block', 
        borderRadius: '15px', 
        overflow: 'hidden',
        boxShadow: '0px 10px 20px rgba(0,0,0,0.3)',
        marginTop: '20px'
      }}>
        {/* Mengambil streaming video dari server Flask Backend */}
        <img 
          src="http://127.0.0.1:5000/video_feed" 
          alt="Video Feed Offline - Pastikan Backend Python Menyala" 
          width="720" 
        />
      </div>
    </div>
  );
}

export default App;