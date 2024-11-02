import './App.css';
import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { GoogleLoginBtn } from './components/GoogleLoginBtn';
import { getToken, Logout } from './utils/Authenticate';
import { getCurrentRoomId, clearCurrentRoomId } from './utils/RoomUtils';
import { RoomList, RoomPage } from './pages';

function AppContent() {
  const navigate = useNavigate();
  const ACCESS_TOKEN = getToken();

  useEffect(() => {
    const roomId = getCurrentRoomId();
    if (ACCESS_TOKEN && roomId) {
      navigate(`/rooms/${roomId}`);
    } else if (!ACCESS_TOKEN) {
      navigate('/');
    }
  }, [ACCESS_TOKEN, navigate]);

  const handleLogout = () => {
    Logout();
    clearCurrentRoomId();
  };

  return (
    <div className="App">
      {!ACCESS_TOKEN && <GoogleLoginBtn />}
      {ACCESS_TOKEN && <button onClick={handleLogout}>로그아웃</button>}

      <Routes>
        <Route path="/" element={<RoomList />} />
        <Route path="/rooms/:roomId" element={<RoomPage />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
