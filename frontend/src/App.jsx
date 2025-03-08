import React, { useState, useEffect } from 'react';

function App() {
  const [authUrl, setAuthUrl] = useState('');
  const [uploadData, setUploadData] = useState(null);

  useEffect(() => {
    // Get auth URL when component mounts
    fetch('http://localhost:8001/')
      .then(res => res.json())
      .then(data => setAuthUrl(data.auth_url));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      const response = await fetch('http://localhost:8001/upload', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      console.log(result);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // If we have upload data (after successful auth), show upload form
  if (uploadData) {
    return (
      <div>
        <h1>Upload Video</h1>
        <form onSubmit={handleSubmit}>
          <input type="text" name="video_url" placeholder="Enter video URL" required />
          <input type="text" name="caption" placeholder="Caption" />
          <input type="hidden" name="access_token" value={uploadData.access_token} />
          <input type="hidden" name="ig_account_id" value={uploadData.account_id} />
          <button type="submit">Upload</button>
        </form>
      </div>
    );
  }

  // Otherwise show login button
  return (
    <div>
      <h1>Instagram Login</h1>
      <button onClick={() => window.location.href = authUrl}>
        Login with Instagram Business Account
      </button>
    </div>
  );
}

export default App;