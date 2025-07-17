// ChatWidget.jsx
import { useState, useRef, useEffect } from "react";
import { FiMessageSquare, FiX, FiSend } from "react-icons/fi";
import axios from "axios";
import "./ChatWidget.css";
import { loginWithMicrosoft, msalInstance } from "../authService";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRightFromBracket, faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { faEnvelope, faPhone, faReply } from "@fortawesome/free-solid-svg-icons";

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [role, setRole] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [username, setUsername] = useState("");
  const [loginError, setLoginError] = useState("");
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [companyName, setCompanyName] = useState("");
  const [personName, setPersonName] = useState("");
  const [problemInput, setProblemInput] = useState("");
  const [selectedOption, setSelectedOption] = useState("");
  const [salesOutput, setSalesOutput] = useState("");

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chat, isLoading]);

  const handleEmployeeClick = async () => {
    const result = await loginWithMicrosoft();
    if (result.success) {
      setRole("employee");
      setUserRole("employee");
      setUsername(result.account.username || "");
      setLoginError("");
    } else {
      setLoginError("❌ Microsoft login failed.");
    }
  };

  const handleLogout = async () => {
    try {
      await msalInstance.logoutPopup();
    } catch (error) {
      console.error("Logout failed", error);
    } finally {
      setRole(null);
      setUsername("");
      setLoginError("");
      setUserRole(null);
      setChat([]);
      setMessage("");
    }
  };

  const handleBack = () => {
    setRole(null);
    setUsername("");
    setLoginError("");
    setUserRole(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setChat((prev) => [...prev, { sender: "user", text: message, isList: false }]);
    setMessage("");
    setIsLoading(true);

    try {
      const res = await axios.post("http://localhost:5000/ask", {
        question: message,
        user_type: userRole || "customer", // ✅ Include user type
      });

      let reply = res.data.answer || "No response.";
      const lines = reply.split("\n").map((line) => line.trim()).filter(Boolean);
      const shouldBeBullets = lines.length >= 2 && lines.every((line) => line.length < 200 && /^[-*•\dA-Z]/.test(line));

      if (shouldBeBullets) {
        setChat((prev) => [...prev, { sender: "bot", text: lines, isList: true }]);
      } else {
        setChat((prev) => [...prev, { sender: "bot", text: reply, isList: false }]);
      }
    } catch (err) {
      setChat((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Failed to fetch response.", isList: false },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSalesGenerate = async () => {
    if (!companyName && !problemInput) return;

    const question = `
Company: ${companyName || "N/A"}
Person: ${personName || "N/A"}
Problem & Solution: ${problemInput}
Request: ${selectedOption || "General Info"}
    `.trim();

    try {
      const res = await axios.post("http://localhost:5000/ask", {
        question,
        user_type: "employee", // ✅ Required
        selectedOptions: selectedOption ? [selectedOption] : [], // ✅ Must be an array
      });
      setSalesOutput(res.data.answer || "No response.");
    } catch (err) {
      setSalesOutput("❌ Failed to generate response.");
    }
  };

  return (
    <>
      {!isOpen && (
        <button className="chat-toggle-button" onClick={() => setIsOpen(true)}>
          <FiMessageSquare size={28} />
        </button>
      )}

      {isOpen && (
        <div className={`chat-popup ${userRole === "employee" ? "sales-tool-popup" : ""}`}>
          <div className="chat-header">
            <div className="chat-title">
              {role && (
                <button className="back-icon" onClick={handleBack}>
                  <FontAwesomeIcon icon={faArrowLeft} />
                </button>
              )}
              <h3>{userRole === "employee" ? "📊 Alli Sales Tool" : "💬 Alliance GPT"}</h3>
            </div>
            <div className="header-actions">
              {userRole === "employee" && (
                <button className="logout-btn" onClick={handleLogout}>
                  <FontAwesomeIcon icon={faRightFromBracket} />
                </button>
              )}
              <button className="close-btn" onClick={() => setIsOpen(false)}>
                <FiX size={20} />
              </button>
            </div>
          </div>

          {!role && (
            <div className="role-selection">
              <button onClick={handleEmployeeClick}>Employee</button>
              <button onClick={() => setRole("customer")}>Customer</button>
            </div>
          )}

          {role === "employee" && userRole !== "employee" && (
            <div className="login-section">
              <p>🔐 Logging in via Microsoft...</p>
              {loginError && <p className="error-msg">{loginError}</p>}
            </div>
          )}

          {userRole === "employee" && (
            <div className="chatbox-wrapper">
              <div className="sales-form">
                <div className="name-fields-vertical">
                  <input
                    type="text"
                    placeholder="Company Name *"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Person Name (optional)"
                    value={personName}
                    onChange={(e) => setPersonName(e.target.value)}
                  />
                </div>

                <textarea
                  placeholder="Describe the problem and your solution..."
                  value={problemInput}
                  onChange={(e) => setProblemInput(e.target.value)}
                  className="problem-textarea"
                ></textarea>

                <div className="icon-options">
                  <FontAwesomeIcon
                    icon={faEnvelope}
                    onClick={() => setSelectedOption("Email")}
                    className={selectedOption === "Email" ? "icon-selected" : ""}
                  />
                  <FontAwesomeIcon
                    icon={faPhone}
                    onClick={() => setSelectedOption("Telephonic Pitch")}
                    className={selectedOption === "Telephonic Pitch" ? "icon-selected" : ""}
                  />
                  <FontAwesomeIcon
                    icon={faReply}
                    onClick={() => setSelectedOption("Follow-up Email")}
                    className={selectedOption === "Follow-up Email" ? "icon-selected" : ""}
                  />
                </div>

                <button className="generate-btn" onClick={handleSalesGenerate}>
                  Generate
                </button>

                {salesOutput && (
                  <div className="chat-message bot-msg" style={{ marginTop: "1rem" }}>
                    {salesOutput}
                  </div>
                )}
              </div>
            </div>
          )}

          {role === "customer" && (
            <div className="chatbox-wrapper">
              <div className="chat-messages">
                {chat.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`chat-message ${msg.sender === "user" ? "user-msg" : "bot-msg"}`}
                  >
                    {msg.isList ? (
                      <ul className="bot-list">
                        {msg.text.map((item, i) => (
                          <li key={i}>{item.replace(/^[-*•\d.]+\s*/, "")}</li>
                        ))}
                      </ul>
                    ) : (
                      msg.text
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="chat-message bot-msg">
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              <form className="chat-form" onSubmit={handleSubmit}>
                <input
                  className="chat-input"
                  type="text"
                  placeholder="Type your message..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                />
                <button type="submit" className="send-icon-btn" aria-label="Send">
                  <FiSend size={20} />
                </button>
              </form>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default ChatWidget;
