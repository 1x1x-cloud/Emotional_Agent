import { useMemo, useState, useEffect } from "react";
import "./App.css";
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';
import Register from './components/auth/Register';
import Login from './components/auth/Login';
import DiaryEditor from './components/diary/DiaryEditor';
import DiaryList from './components/diary/DiaryList';
import VoiceInput from './components/voice/VoiceInput';
import RecommendationPanel from './components/recommendation/RecommendationPanel';

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
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // 用户认证状态
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  
  // 情绪状态
  const [currentEmotion, setCurrentEmotion] = useState('neutral');
  
  // UI状态
  const [activeTab, setActiveTab] = useState('chat'); // chat, diary, voice, recommendation
  
  // 检查本地存储中的用户信息
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setCurrentUser(user);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('解析用户信息失败:', error);
        localStorage.removeItem('user');
      }
    }
  }, []);

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
  
  // 处理用户登录
  const handleLogin = (userData) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    setShowLogin(false);
    localStorage.setItem('user', JSON.stringify(userData));
  };
  
  // 处理用户注册
  const handleRegister = (userData) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    setShowRegister(false);
    localStorage.setItem('user', JSON.stringify(userData));
  };
  
  // 处理用户登出
  const handleLogout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
  };
  
  // 处理语音输入
  const handleVoiceInput = (text) => {
    setInput(text);
  };
  
  // 处理日记保存
  const handleDiarySave = () => {
    // 日记保存后可以刷新日记列表
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

      // 更新当前情绪状态
      if (data.sentiment) {
        setCurrentEmotion(data.sentiment.sentiment === true ? 'positive' : data.sentiment.sentiment === false ? 'negative' : 'neutral');
      }

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

  // 主题样式
  const theme = isDarkMode ? {
    background: "#1f2937",
    text: "#f9fafb",
    card: "#374151",
    border: "#4b5563",
    button: {
      primary: "#3b82f6",
      success: "#10b981",
      warning: "#f59e0b",
      danger: "#ef4444",
      info: "#6366f1"
    },
    message: {
      user: "#1e40af",
      assistant: "#374151"
    },
    input: "#374151",
    inputText: "#f9fafb"
  } : {
    background: "#ffffff",
    text: "#111827",
    card: "#ffffff",
    border: "#e5e7eb",
    button: {
      primary: "#3b82f6",
      success: "#10b981",
      warning: "#f59e0b",
      danger: "#ef4444",
      info: "#6366f1"
    },
    message: {
      user: "#dbeafe",
      assistant: "#ffffff"
    },
    input: "#ffffff",
    inputText: "#111827"
  };

  return (
    <div className="App" style={{ 
      minHeight: "100vh",
      backgroundColor: theme.background,
      color: theme.text
    }}>
      <div style={{ 
        maxWidth: 1200, 
        margin: "0 auto", 
        padding: "16px",
        paddingTop: "24px",
        paddingBottom: "24px",
        boxSizing: "border-box"
      }}>
        {/* 标题和用户状态 */}
        <div style={{ marginBottom: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ marginTop: 0, marginBottom: 0 }}>情感陪伴 AI</h2>
          
          {/* 用户状态区域 */}
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            {isAuthenticated ? (
              <>
                <span style={{ fontSize: "14px" }}>欢迎，{currentUser?.username}</span>
                <button 
                  onClick={handleLogout} 
                  style={{
                    padding: "6px 10px",
                    borderRadius: 6,
                    border: "1px solid #ef4444",
                    backgroundColor: "#ef4444",
                    color: "white",
                    cursor: "pointer",
                    fontSize: "14px"
                  }}
                >
                  登出
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={() => setShowLogin(true)} 
                  style={{
                    padding: "6px 10px",
                    borderRadius: 6,
                    border: "1px solid #3b82f6",
                    backgroundColor: "#3b82f6",
                    color: "white",
                    cursor: "pointer",
                    fontSize: "14px"
                  }}
                >
                  登录
                </button>
                <button 
                  onClick={() => setShowRegister(true)} 
                  style={{
                    padding: "6px 10px",
                    borderRadius: 6,
                    border: "1px solid #10b981",
                    backgroundColor: "#10b981",
                    color: "white",
                    cursor: "pointer",
                    fontSize: "14px"
                  }}
                >
                  注册
                </button>
              </>
            )}
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)} 
              style={{
                padding: "6px 10px",
                borderRadius: 6,
                border: "1px solid #6366f1",
                backgroundColor: "#6366f1",
                color: "white",
                cursor: "pointer",
                fontSize: "14px"
              }}
            >
              {isDarkMode ? "浅色" : "深色"}
            </button>
          </div>
        </div>

        {/* 导航栏 */}
        <div style={{ 
          marginBottom: 24, 
          borderBottom: `1px solid ${theme.border}`,
          paddingBottom: 12
        }}>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
            <button 
              onClick={() => setActiveTab('chat')} 
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: `1px solid ${theme.border}`,
                backgroundColor: activeTab === 'chat' ? (isDarkMode ? "#374151" : "#f3f4f6") : theme.background,
                color: theme.text,
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: activeTab === 'chat' ? "bold" : "normal"
              }}
            >
              💬 聊天
            </button>
            <button 
              onClick={() => setActiveTab('diary')} 
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: `1px solid ${theme.border}`,
                backgroundColor: activeTab === 'diary' ? (isDarkMode ? "#374151" : "#f3f4f6") : theme.background,
                color: theme.text,
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: activeTab === 'diary' ? "bold" : "normal"
              }}
            >
              📝 情感日记
            </button>
            <button 
              onClick={() => setActiveTab('voice')} 
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: `1px solid ${theme.border}`,
                backgroundColor: activeTab === 'voice' ? (isDarkMode ? "#374151" : "#f3f4f6") : theme.background,
                color: theme.text,
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: activeTab === 'voice' ? "bold" : "normal"
              }}
            >
              🎤 语音交互
            </button>
            <button 
              onClick={() => setActiveTab('recommendation')} 
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: `1px solid ${theme.border}`,
                backgroundColor: activeTab === 'recommendation' ? (isDarkMode ? "#374151" : "#f3f4f6") : theme.background,
                color: theme.text,
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: activeTab === 'recommendation' ? "bold" : "normal"
              }}
            >
              📋 智能推荐
            </button>
          </div>
        </div>

        {/* 主内容区域 */}
        <div style={{ minHeight: "60vh" }}>
          {/* 登录模态框 */}
          {showLogin && (
            <div style={{ 
              position: "fixed", 
              top: 0, 
              left: 0, 
              right: 0, 
              bottom: 0, 
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 1000
            }}>
              <div style={{ 
                backgroundColor: theme.card,
                border: `1px solid ${theme.border}`,
                borderRadius: 12,
                padding: 24,
                width: "90%",
                maxWidth: 400
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <h3 style={{ marginTop: 0, marginBottom: 0 }}>用户登录</h3>
                  <button 
                    onClick={() => setShowLogin(false)} 
                    style={{ 
                      background: "none", 
                      border: "none", 
                      fontSize: "20px", 
                      cursor: "pointer",
                      color: theme.text
                    }}
                  >
                    ×
                  </button>
                </div>
                <Login onLogin={handleLogin} onClose={() => setShowLogin(false)} />
              </div>
            </div>
          )}

          {/* 注册模态框 */}
          {showRegister && (
            <div style={{ 
              position: "fixed", 
              top: 0, 
              left: 0, 
              right: 0, 
              bottom: 0, 
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 1000
            }}>
              <div style={{ 
                backgroundColor: theme.card,
                border: `1px solid ${theme.border}`,
                borderRadius: 12,
                padding: 24,
                width: "90%",
                maxWidth: 400
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <h3 style={{ marginTop: 0, marginBottom: 0 }}>用户注册</h3>
                  <button 
                    onClick={() => setShowRegister(false)} 
                    style={{ 
                      background: "none", 
                      border: "none", 
                      fontSize: "20px", 
                      cursor: "pointer",
                      color: theme.text
                    }}
                  >
                    ×
                  </button>
                </div>
                <Register onRegister={handleRegister} onClose={() => setShowRegister(false)} />
              </div>
            </div>
          )}

          {/* 聊天界面 */}
          {activeTab === 'chat' && (
            <div style={{ display: "flex", gap: 24, flexDirection: "column" }}>
              <div
                style={{
                  border: `1px solid ${theme.border}`,
                  borderRadius: 12,
                  padding: 16,
                  height: "60vh",
                  minHeight: 400,
                  overflowY: "auto",
                  background: isDarkMode ? "#111827" : "#fafafa",
                }}
              >
                {messages.map((m, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                      marginBottom: 10,
                      animation: "messageSlideIn 0.3s ease-out forwards",
                      opacity: 0,
                      transform: m.role === "user" ? "translateX(20px)" : "translateX(-20px)"
                    }}
                  >
                    <div
                      style={{
                        maxWidth: "85%",
                        padding: "10px 12px",
                        borderRadius: 12,
                        whiteSpace: "pre-wrap",
                        textAlign: "left",
                        background: m.role === "user" ? theme.message.user : theme.message.assistant,
                        border: `1px solid ${theme.border}`,
                        color: isDarkMode ? "#f9fafb" : "#111827",
                        animation: "messageFadeIn 0.3s ease-out forwards"
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
                    border: `1px solid ${theme.border}`,
                    outline: "none",
                    backgroundColor: theme.input,
                    color: theme.inputText,
                    placeholderColor: isDarkMode ? "#9ca3af" : "#6b7280"
                  }}
                />
                <button
                  onClick={send}
                  disabled={!canSend}
                  style={{
                    padding: "10px 14px",
                    borderRadius: 10,
                    border: `1px solid ${theme.border}`,
                    background: canSend ? (isDarkMode ? "#374151" : "#111827") : (isDarkMode ? "#4b5563" : "#9ca3af"),
                    color: "#fff",
                    cursor: canSend ? "pointer" : "not-allowed",
                    minWidth: 80
                  }}
                >
                  {isSending ? "发送中…" : "发送"}
                </button>
              </div>
            </div>
          )}

          {/* 情感日记界面 */}
          {activeTab === 'diary' && (
            <div style={{ display: "flex", gap: 24, flexDirection: "column" }}>
              <DiaryEditor onSave={handleDiarySave} user_id={currentUser?.user_id} />
              <DiaryList user_id={currentUser?.user_id} />
            </div>
          )}

          {/* 语音交互界面 */}
          {activeTab === 'voice' && (
            <div style={{ display: "flex", gap: 24, flexDirection: "column" }}>
              <VoiceInput onVoiceInput={handleVoiceInput} />
              <div style={{ 
                border: `1px solid ${theme.border}`,
                borderRadius: 12,
                padding: 16,
                backgroundColor: theme.card
              }}>
                <h3 style={{ marginTop: 0, marginBottom: 16 }}>语音转文字结果</h3>
                <div style={{ 
                  padding: 12, 
                  borderRadius: 8,
                  backgroundColor: isDarkMode ? "#374151" : "#f3f4f6",
                  minHeight: 100
                }}>
                  {input || "点击开始录音，语音会自动转成文字显示在这里..."}
                </div>
                <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
                  <button
                    onClick={() => send()}
                    disabled={!input.trim()}
                    style={{
                      padding: "10px 14px",
                      borderRadius: 10,
                      border: `1px solid ${theme.border}`,
                      background: input.trim() ? (isDarkMode ? "#374151" : "#111827") : (isDarkMode ? "#4b5563" : "#9ca3af"),
                      color: "#fff",
                      cursor: input.trim() ? "pointer" : "not-allowed",
                      minWidth: 80
                    }}
                  >
                    发送消息
                  </button>
                  <button
                    onClick={() => setInput("")}
                    style={{
                      padding: "10px 14px",
                      borderRadius: 10,
                      border: `1px solid ${theme.border}`,
                      background: theme.background,
                      color: theme.text,
                      cursor: "pointer",
                      minWidth: 80
                    }}
                  >
                    清空
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* 智能推荐界面 */}
          {activeTab === 'recommendation' && (
            <div style={{ display: "flex", gap: 24, flexDirection: "column" }}>
              <RecommendationPanel currentEmotion={currentEmotion} />
              <div style={{ 
                border: `1px solid ${theme.border}`,
                borderRadius: 12,
                padding: 16,
                backgroundColor: theme.card
              }}>
                <h3 style={{ marginTop: 0, marginBottom: 16 }}>当前情绪状态</h3>
                <div style={{ 
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: 16,
                  borderRadius: 8,
                  backgroundColor: currentEmotion === 'positive' ? "#f0fdf4" : 
                                  currentEmotion === 'negative' ? "#fef2f2" : "#f3f4f6"
                }}>
                  <div style={{ fontSize: "48px" }}>
                    {currentEmotion === 'positive' ? "😊" : 
                     currentEmotion === 'negative' ? "😢" : "😐"}
                  </div>
                  <div>
                    <h4 style={{ marginTop: 0, marginBottom: 8 }}>
                      {currentEmotion === 'positive' ? "开心" : 
                       currentEmotion === 'negative' ? "难过" : "平静"}
                    </h4>
                    <p style={{ marginTop: 0, color: "#6b7280" }}>
                      {currentEmotion === 'positive' ? "你现在心情不错，继续保持！" : 
                       currentEmotion === 'negative' ? "希望我的推荐能让你感觉好一些" : 
                       "保持平静的心态，享受当下"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
