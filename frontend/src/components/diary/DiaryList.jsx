import React, { useState, useEffect } from 'react';

const DiaryList = ({ user_id }) => {
  const [diaries, setDiaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user_id) {
      fetchDiaries();
    }
  }, [user_id]);

  const fetchDiaries = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/diary/list/${user_id}`);
      const data = await response.json();
      if (data.success) {
        setDiaries(data.diaries || []);
      } else {
        setError(data.message || '获取日记失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const getEmotionColor = (emotion) => {
    switch (emotion) {
      case 'positive': return '#4CAF50';
      case 'negative': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const getEmotionText = (emotion) => {
    switch (emotion) {
      case 'positive': return '开心';
      case 'negative': return '难过';
      default: return '平静';
    }
  };

  return (
    <div className="diary-list">
      <h3>情感日记列表</h3>
      {error && <div className="error-message">{error}</div>}
      {loading ? (
        <div className="loading">加载中...</div>
      ) : diaries.length === 0 ? (
        <div className="empty">还没有日记，开始写第一篇吧！</div>
      ) : (
        <div className="diary-cards">
          {diaries.map((diary) => (
            <div key={diary.id} className="diary-card">
              <div className="diary-header">
                <h4>{diary.date}</h4>
                <span 
                  className="emotion-tag" 
                  style={{ backgroundColor: getEmotionColor(diary.emotion) }}
                >
                  {getEmotionText(diary.emotion)} (强度: {diary.intensity})
                </span>
              </div>
              <div className="diary-content">
                <p>{diary.notes}</p>
              </div>
              {diary.tags && (
                <div className="diary-tags">
                  {diary.tags.split(',').map((tag, index) => (
                    <span key={index} className="tag">{tag.trim()}</span>
                  ))}
                </div>
              )}
              <div className="diary-footer">
                <small>{new Date(diary.created_at).toLocaleString()}</small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DiaryList;