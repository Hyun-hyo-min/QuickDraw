import './App.css';
import { GoogleLoginBtn } from './components/GoogleLoginBtn';
import { getToken, Logout } from './utils/Authenticate';

function App() {

  const ACCESS_TOKEN = getToken()
  return (
    <div className="App">
      {!ACCESS_TOKEN &&
        <GoogleLoginBtn />
      }
      {ACCESS_TOKEN &&
        <button onClick={Logout}>로그아웃</button>
      }
    </div>
  );
}

export default App;