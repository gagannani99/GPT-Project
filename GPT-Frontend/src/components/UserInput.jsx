import { useState } from "react";
import axios from "axios";
import "./UserInput.css";

const UserInput = ({ apiUrl, role, username }) => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      const response = await axios.post(apiUrl, { question });
      setAnswer(response.data.answer);
    } catch (err) {
      console.error("Error:", err);
      setAnswer("Error getting response from server.");
    }
  };

  return (
    <div className="chatbox">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          required
        />
        <button type="submit">Send</button>
      </form>
      {answer && <div className="answer-box">💡 {answer}</div>}
    </div>
  );
};

export default UserInput;
