import React, { useState } from 'react';

const DiaryEditor = ({ onSave, user_id }) => {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    emotion: 'neutral',
    intensity: 5,
    notes: '',
    tags: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.notes) {
      setError('日记内容不能为空');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await fetch('/diary/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, user_id })
      });
      const data = await response.json();
      if (data.success) {
        setSuccess('保存成功');
        setFormData({
          date: new Date().toISOString().split('T')[0],
          emotion: 'neutral',
          intensity: 5,
          notes: '',
          tags: ''
        });
        onSave();
      } else {
        setError(data.message || '保存失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="diary-editor">
      <h3>写情感日记</h3>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>日期：</label>
          <input 
            type="date" 
            name="date" 
            value={formData.date} 
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>情绪：</label>
          <select 
            name="emotion" 
            value={formData.emotion} 
            onChange={handleChange}
            required
          >
            <option value="positive">开心</option>
            <option value="neutral">平静</option>
            <option value="negative">难过</option>
          </select>
        </div>
        <div className="form-group">
          <label>强度：</label>
          <input 
            type="range" 
            name="intensity" 
            min="1" 
            max="10" 
            value={formData.intensity} 
            onChange={handleChange}
          />
          <span>{formData.intensity}</span>
        </div>
        <div className="form-group">
          <label>内容：</label>
          <textarea 
            name="notes" 
            value={formData.notes} 
            onChange={handleChange}
            placeholder="记录你的心情..."
            rows={5}
            required
          ></textarea>
        </div>
        <div className="form-group">
          <label>标签：</label>
          <input 
            type="text" 
            name="tags" 
            value={formData.tags} 
            onChange={handleChange}
            placeholder="用逗号分隔多个标签"
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? '保存中...' : '保存日记'}
        </button>
      </form>
    </div>
  );
};

export default DiaryEditor;