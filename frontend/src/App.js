import { useMemo, useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "你好呀，我是你的情感陪伴 AI。今天过得怎么样？",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const canSend = useMemo(() => input.trim().length > 0 && !isSending, [input, isSending]);

  async function send() {
    const text = input.trim();
    if (!text || isSending) return;

    setInput("");
    setIsSending(true);
    setMessages((prev) => [...prev, { role: "user", content: text }]);

    try {
      const r = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await r.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply ?? "（后端未返回 reply）" }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", content: "发送失败：" + String(e) }]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="App">
      <div style={{ maxWidth: 820, margin: "0 auto", padding: 24 }}>
        <h2 style={{ marginTop: 0 }}>情感陪伴 AI - Demo</h2>

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
    </div>
  );
}

export default App;