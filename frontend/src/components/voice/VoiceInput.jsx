import React, { useState } from 'react';

const VoiceInput = ({ onVoiceInput }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setAudioChunks(chunks);
      setIsRecording(true);
      setError('');
    } catch (err) {
      setError('无法访问麦克风，请检查权限');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch('/voice/speech-to-text', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.success) {
        onVoiceInput(data.text);
      } else {
        setError(data.error || '语音识别失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="voice-input">
      <h3>语音输入</h3>
      {error && <div className="error-message">{error}</div>}
      <div className="voice-controls">
        <button 
          className={`record-button ${isRecording ? 'recording' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={loading}
        >
          {loading ? '处理中...' : isRecording ? '停止录音' : '开始录音'}
        </button>
        {isRecording && (
          <div className="recording-indicator">
            <div className="recording-dot"></div>
            <span>正在录音...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceInput;