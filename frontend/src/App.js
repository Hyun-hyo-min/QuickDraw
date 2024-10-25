import './App.css';
import RoomList from './components/RoomList';
import { GoogleLoginBtn } from './components/GoogleLoginBtn';
import { getToken, Logout } from './utils/Authenticate';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import RoomPage from './components/RoomPage';

function App() {
  const ACCESS_TOKEN = getToken();

  return (
    <Router>
      <div className="App">
        {!ACCESS_TOKEN && <GoogleLoginBtn />}
        {ACCESS_TOKEN && <button onClick={Logout}>로그아웃</button>}

        <Routes>
          <Route path="/" element={<RoomList />} />
          <Route path="/rooms/:roomId" element={<RoomPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
