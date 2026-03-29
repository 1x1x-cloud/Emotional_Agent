import React, { useState, useEffect } from 'react';

const RecommendationPanel = ({ currentEmotion }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (currentEmotion) {
      fetchRecommendations(currentEmotion);
    }
  }, [currentEmotion]);

  const fetchRecommendations = async (emotion) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`/recommendations/${emotion}`);
      const data = await response.json();
      if (data.success) {
        setRecommendations(data.data);
      } else {
        setError(data.message || '获取推荐失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (!currentEmotion) {
    return (
      <div className="recommendation-panel">
        <h3>智能推荐</h3>
        <div className="empty">开始聊天后将根据您的情绪提供推荐</div>
      </div>
    );
  }

  return (
    <div className="recommendation-panel">
      <h3>智能推荐</h3>
      {error && <div className="error-message">{error}</div>}
      {loading ? (
        <div className="loading">加载中...</div>
      ) : recommendations ? (
        <div className="recommendation-content">
          <div className="recommendation-message">
            <p>{recommendations.message}</p>
          </div>
          
          {recommendations.music && recommendations.music.length > 0 && (
            <div className="recommendation-section">
              <h4>🎵 推荐音乐</h4>
              <ul>
                {recommendations.music.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {recommendations.articles && recommendations.articles.length > 0 && (
            <div className="recommendation-section">
              <h4>📖 推荐文章</h4>
              <ul>
                {recommendations.articles.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {recommendations.activities && recommendations.activities.length > 0 && (
            <div className="recommendation-section">
              <h4>🏃 推荐活动</h4>
              <ul>
                {recommendations.activities.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="empty">暂无推荐内容</div>
      )}
    </div>
  );
};

export default RecommendationPanel;