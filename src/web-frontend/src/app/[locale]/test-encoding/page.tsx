
'use client';

import { useState } from 'react';

export default function TestEncodingPage() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch('/api/test-encoding', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input }),
    });

    const data = await res.json();
    setResponse(data.output);
  };

  return (
    <div>
      <h1>Test Encoding</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">Submit</button>
      </form>
      <h2>Response:</h2>
      <p>{response}</p>
    </div>
  );
}
