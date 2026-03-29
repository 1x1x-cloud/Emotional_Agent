import { useMemo, useState } from "react";
import "./App.css";

// 获取情绪对应的emoji
function getEmotionEmoji(emotion) {
  const emojiMap = {
    // 正向情绪
    "joy": "😊",
    "gratitude": "🙏",
    "contentment": "😌",
    "love": "❤️",
    "pride": "🌟",
    // 负向情绪
    "sadness": "😢",
    "anger": "😠",
    "anxiety": "😰",
    "loneliness": "🥺",
    "disappointment": "😞",
    "fatigue": "😴",
    // 中性情绪
    "curiosity": "🤔",
    "confusion": "😕",
    "reflection": "💭",
    "neutral": "😐"
  };
  return emojiMap[emotion] || (emotion ? "😶" : "😐");
}

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "你好呀，我是你的情感陪伴 AI。今天过得怎么样？",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [backendMessage, setBackendMessage] = useState("");
  const [showProfile, setShowProfile] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [emotionTrend, setEmotionTrend] = useState(null);
  const [emotionMonitor, setEmotionMonitor] = useState(null);

  // 测试后端连接
  const testBackend = async () => {
    try {
      const response = await fetch('http://localhost:8000/hello');
      const data = await response.json();
      setBackendMessage(data.text);
    } catch (error) {
      console.error('Error:', error);
      setBackendMessage('连接后端失败：' + error.message);
    }
  };

  // 加载用户画像
  const loadUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/profile/demo_user');
      const data = await response.json();
      setUserProfile(data.profile);
      setShowProfile(true);
    } catch (error) {
      console.error('Error:', error);
      alert('加载用户画像失败：' + error.message);
    }
  };

  // 加载情感趋势
  const loadEmotionTrend = async () => {
    try {
      const response = await fetch('http://localhost:8000/profile/trend/demo_user?days=7');
      const data = await response.json();
      setEmotionTrend(data.trend);
    } catch (error) {
      console.error('Error:', error);
      alert('加载情感趋势失败：' + error.message);
    }
  };

  // 加载情感监测
  const loadEmotionMonitor = async () => {
    try {
      const response = await fetch('http://localhost:8000/emotion/monitor/demo_user');
      const data = await response.json();
      setEmotionMonitor(data);
    } catch (error) {
      console.error('Error:', error);
      alert('加载情感监测失败：' + error.message);
    }
  };

  // 重置情感监测
  const resetEmotionMonitor = async () => {
    try {
      const response = await fetch('http://localhost:8000/emotion/reset/demo_user', {
        method: 'POST'
      });
      const data = await response.json();
      alert(data.message);
      loadEmotionMonitor();
    } catch (error) {
      console.error('Error:', error);
      alert('重置情感监测失败：' + error.message);
    }
  };

  const canSend = useMemo(() => input.trim().length > 0 && !isSending, [input, isSending]);

  async function send() {
    const text = input.trim();
    if (!text || isSending) return;

    setInput("");
    setIsSending(true);

    try {
      // 调用聊天接口（后端已集成情感分析）
      const r = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await r.json();
      console.log("聊天接口返回:", data);

      // 添加用户消息（包含情感标签，从后端返回）
      setMessages((prev) => [...prev, { 
        role: "user", 
        content: text,
        sentiment: data.sentiment
      }]);

      // 添加AI回复
      setMessages((prev) => [...prev, { 
        role: "assistant", 
        content: data.reply ?? "（后端未返回 reply）",
        conversation_id: data.conversation_id
      }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: "发送失败：" + String(e) }]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="App">
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: 24 }}>
        <div style={{ display: "flex", gap: 24 }}>
          {/* 左侧聊天区域 */}
          <div style={{ flex: 1 }}>
            <h2 style={{ marginTop: 0 }}>情感陪伴 AI</h2>
            
            {/* 测试后端连接按钮 */}
            <div style={{ marginBottom: 16, padding: 12, backgroundColor: "#f0f9ff", borderRadius: 8, border: "1px solid #e0f2fe" }}>
              <button 
                onClick={testBackend} 
                style={{
                  padding: "8px 12px",
                  borderRadius: 6,
                  border: "1px solid #3b82f6",
                  backgroundColor: "#3b82f6",
                  color: "white",
                  cursor: "pointer",
                  marginRight: 12
                }}
              >
                测试后端连接
              </button>
              <button 
                onClick={() => { loadUserProfile(); loadEmotionTrend(); loadEmotionMonitor(); }} 
                style={{
                  padding: "8px 12px",
                  borderRadius: 6,
                  border: "1px solid #10b981",
                  backgroundColor: "#10b981",
                  color: "white",
                  cursor: "pointer",
                  marginRight: 12
                }}
              >
                查看画像
              </button>
              <button 
                onClick={loadEmotionMonitor} 
                style={{
                  padding: "8px 12px",
                  borderRadius: 6,
                  border: "1px solid #f59e0b",
                  backgroundColor: "#f59e0b",
                  color: "white",
                  cursor: "pointer",
                  marginRight: 12
                }}
              >
                情感监测
              </button>
              <button 
                onClick={resetEmotionMonitor} 
                style={{
                  padding: "8px 12px",
                  borderRadius: 6,
                  border: "1px solid #ef4444",
                  backgroundColor: "#ef4444",
                  color: "white",
                  cursor: "pointer"
                }}
              >
                重置监测
              </button>
              {backendMessage && (
                <span style={{ marginLeft: 12, color: "#1e40af" }}>
                  {backendMessage}
                </span>
              )}
            </div>

            <div
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                padding: 16,
                height: "60vh",
                overflowY: "auto",
                background: "#fafafa",
              }}
            >
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                    marginBottom: 10,
                  }}
                >
                  <div
                    style={{
                      maxWidth: "75%",
                      padding: "10px 12px",
                      borderRadius: 12,
                      whiteSpace: "pre-wrap",
                      textAlign: "left",
                      background: m.role === "user" ? "#dbeafe" : "#ffffff",
                      border: "1px solid #e5e7eb",
                    }}
                  >
                    {m.content}
                    {/* 显示情感标签 */}
                    {m.role === "user" && m.sentiment && (
                      <div style={{ 
                        marginTop: 6, 
                        fontSize: 12, 
                        color: m.sentiment.sentiment === true ? "#10b981" : m.sentiment.sentiment === false ? "#ef4444" : "#6b7280",
                        display: "flex",
                        alignItems: "center",
                        gap: 4
                      }}>
                        <span>{getEmotionEmoji(m.sentiment.emotion)}</span>
                        <span>{m.sentiment.label}</span>
                        <span style={{ fontSize: 10, opacity: 0.7 }}>({Math.round(m.sentiment.confidence * 100)}%)</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") send();
                }}
                placeholder="输入你想说的话，然后按 Enter 发送…"
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid #e5e7eb",
                  outline: "none",
                }}
              />
              <button
                onClick={send}
                disabled={!canSend}
                style={{
                  padding: "10px 14px",
                  borderRadius: 10,
                  border: "1px solid #e5e7eb",
                  background: canSend ? "#111827" : "#9ca3af",
                  color: "#fff",
                  cursor: canSend ? "pointer" : "not-allowed",
                }}
              >
                {isSending ? "发送中…" : "发送"}
              </button>
            </div>
          </div>

          {/* 右侧用户画像和情感趋势 */}
          {showProfile && (
            <div style={{ width: 350, marginLeft: 24 }}>
              {/* 用户画像 */}
              {userProfile && (
                <div style={{ 
                  border: "1px solid #e5e7eb", 
                  borderRadius: 12, 
                  padding: 16, 
                  marginBottom: 16,
                  backgroundColor: "#fff"
                }}>
                  <h3 style={{ marginTop: 0, marginBottom: 12 }}>用户画像</h3>
                  <div style={{ marginBottom: 12 }}>
                    <strong>总消息数：</strong> {userProfile.total_messages}
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>常用话题：</strong>
                    <div style={{ marginTop: 8 }}>
                      {userProfile.common_topics.map((topic, idx) => (
                        <span key={idx} style={{ 
                          display: "inline-block",
                          padding: "4px 8px",
                          margin: "4px",
                          backgroundColor: "#f0f9ff",
                          borderRadius: 4,
                          fontSize: 12
                        }}>
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>情绪分布：</strong>
                    <div style={{ marginTop: 8 }}>
                      {Object.entries(userProfile.emotion_distribution).map(([emotion, count]) => (
                        <div key={emotion} style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
                          <span>{getEmotionEmoji(emotion)}</span>
                          <span style={{ marginLeft: 8 }}>{emotion}: {count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <strong>活跃时段：</strong>
                    <div style={{ marginTop: 8 }}>
                      {userProfile.peak_hours.map((hour, idx) => (
                        <div key={idx} style={{ fontSize: 12, color: "#6b7280" }}>
                          {hour.hour}:00 - {hour.count} 条消息
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* 情感趋势 */}
              {emotionTrend && (
                <div style={{ 
                  border: "1px solid #e5e7eb", 
                  borderRadius: 12, 
                  padding: 16, 
                  backgroundColor: "#fff"
                }}>
                  <h3 style={{ marginTop: 0, marginBottom: 12 }}>情感趋势</h3>
                  <div style={{ marginBottom: 12 }}>
                    <strong>趋势方向：</strong>
                    <span style={{ 
                      marginLeft: 8,
                      color: emotionTrend.trend === "improving" ? "#10b981" : 
                             emotionTrend.trend === "declining" ? "#ef4444" : "#6b7280"
                    }}>
                      {emotionTrend.trend === "improving" ? "📈 改善中" : 
                       emotionTrend.trend === "declining" ? "📉 下降中" : "➡️ 稳定"}
                    </span>
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>正向比例：</strong> {(emotionTrend.positive_ratio * 100).toFixed(1)}%
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>负向比例：</strong> {(emotionTrend.negative_ratio * 100).toFixed(1)}%
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>主导情绪：</strong> {getEmotionEmoji(emotionTrend.dominant_emotion)} {emotionTrend.dominant_emotion}
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>情绪变化：</strong> {emotionTrend.emotion_changes} 次
                  </div>
                  {emotionTrend.recommendations && emotionTrend.recommendations.length > 0 && (
                    <div>
                      <strong>个性化建议：</strong>
                      <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                        {emotionTrend.recommendations.map((rec, idx) => (
                          <li key={idx} style={{ marginBottom: 4, fontSize: 13 }}>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* 情感监测 */}
              {emotionMonitor && (
                <div style={{ 
                  border: "1px solid #e5e7eb", 
                  borderRadius: 12, 
                  padding: 16, 
                  marginTop: 16,
                  backgroundColor: "#fff"
                }}>
                  <h3 style={{ marginTop: 0, marginBottom: 12 }}>情感监测</h3>
                  <div style={{ marginBottom: 12 }}>
                    <strong>当前趋势：</strong>
                    <span style={{ 
                      marginLeft: 8,
                      color: emotionMonitor.trend.trend === "improving" ? "#10b981" : 
                             emotionMonitor.trend.trend === "declining" ? "#ef4444" : "#6b7280"
                    }}>
                      {emotionMonitor.trend.trend === "improving" ? "📈 改善中" : 
                       emotionMonitor.trend.trend === "declining" ? "📉 下降中" : "➡️ 稳定"}
                    </span>
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>当前情绪：</strong> {getEmotionEmoji(emotionMonitor.trend.current_emotion)} {emotionMonitor.trend.current_emotion}
                  </div>
                  <div style={{ marginBottom: 12 }}>
                    <strong>负面情绪连续：</strong> {emotionMonitor.trend.negative_streak} 次
                  </div>
                  {emotionMonitor.alert && (
                    <div style={{ 
                      marginBottom: 12, 
                      padding: 12, 
                      backgroundColor: emotionMonitor.alert.level === "intervention" ? "#fef2f2" : "#fef3c7",
                      border: emotionMonitor.alert.level === "intervention" ? "1px solid #fee2e2" : "1px solid #fde68a",
                      borderRadius: 6
                    }}>
                      <strong>⚠️ {emotionMonitor.alert.level === "intervention" ? "干预提醒" : "预警提醒"}</strong>
                      <p style={{ marginTop: 4, marginBottom: 4 }}>{emotionMonitor.alert.message}</p>
                      <p style={{ marginTop: 4, fontSize: 13, color: "#6b7280" }}>{emotionMonitor.alert.recommendation}</p>
                    </div>
                  )}
                  {emotionMonitor.suggestion && (
                    <div style={{ 
                      marginBottom: 12, 
                      padding: 12, 
                      backgroundColor: "#f0fdf4",
                      border: "1px solid #dcfce7",
                      borderRadius: 6
                    }}>
                      <strong>💡 干预建议</strong>
                      <p style={{ marginTop: 4, fontSize: 13 }}>{emotionMonitor.suggestion}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
