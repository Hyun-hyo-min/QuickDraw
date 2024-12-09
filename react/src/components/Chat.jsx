function Chat({ chatMessages, newMessage, setNewMessage, onSendMessage }) {
    return (
        <div className="chat-container">
            <div className="chat-messages">
                {chatMessages.map((msg, index) => (
                    <div key={index} className="chat-message">
                        {msg}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                onKeyDown={(e) => e.key === 'Enter' && onSendMessage()}
            />
            <button onClick={onSendMessage}>Send</button>
        </div>
    );
}

export default Chat
