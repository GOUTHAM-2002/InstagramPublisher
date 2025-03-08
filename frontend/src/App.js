import React from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation } from 'react-router-dom';

const LoginPage = () => {
  const handleLogin = async () => {
    const response = await fetch('http://localhost:8001/');
    const data = await response.json();
    window.location.href = data.auth_url;
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '100px' }}>
      <h1>Instagram Reel Publisher</h1>
      <p>Please login with your Instagram Business Account</p>
      <button 
        onClick={handleLogin}
        style={{
          padding: '10px 20px',
          backgroundColor: '#0095f6',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Login with Instagram
      </button>
    </div>
  );
};

const UploadPage = () => {
  const [accountData, setAccountData] = React.useState({
    success: true,
    access_token: "IGAAQtkXDflpRBZAE5LMlhhaGxkUmh5TXJ6cWNqV0tDd0FuTmxsZAWtvd25MSk1YaWdaMGh6RDFlSDJIRzV2aEhQbHZAwampjVlNOakRaMnRtMGRWbXNFX19JazdNUVZApTXFMckNFZAy1fblg1QTdLT3dSTXdR",
    account_id: "28788706554108902",
    username: "gouthamjarvis",
    account_type: "MEDIA_CREATOR"
  });
  const [uploadStatus, setUploadStatus] = React.useState('');

  const handleUpload = async (event) => {
    event.preventDefault();
    setUploadStatus('Uploading...');
    
    try {
      const response = await fetch('http://localhost:8001/upload', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(event.target),
      });
      
      const result = await response.json();
      setUploadStatus(result.error ? 
        `Error: ${result.error}` : 
        `Success! Media ID: ${result.media_id}`
      );
    } catch (err) {
      setUploadStatus('Upload failed');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Publish Reel</h1>
      <p>Welcome, {accountData.username}!</p>
      <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <input
          type="text"
          name="video_url"
          placeholder="Enter video URL"
          required
          style={{ padding: '8px' }}
        />
        <textarea
          name="caption"
          placeholder="Enter caption"
          style={{ padding: '8px', minHeight: '100px' }}
        />
        <input type="hidden" name="access_token" value={accountData.access_token} />
        <input type="hidden" name="ig_account_id" value={accountData.account_id} />
        <button
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#0095f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Publish Reel
        </button>
      </form>
      
      {uploadStatus && (
        <p style={{ 
          marginTop: '20px',
          color: uploadStatus.includes('Error') ? 'red' : 'green'
        }}>
          {uploadStatus}
        </p>
      )}
    </div>
  );
};

const CallbackPage = () => {
  const location = useLocation();

  React.useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const data = urlParams.get('data');
    if (data) {
      const parsedData = JSON.parse(data);
      localStorage.setItem('instagramAccountData', JSON.stringify(parsedData));
      window.location.href = '/upload';
    }
  }, [location]);

  return <div>Processing login...</div>;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/callback" element={<CallbackPage />} />
        <Route path="/" element={<LoginPage />} />
      </Routes>
    </Router>
  );
}

export default App;