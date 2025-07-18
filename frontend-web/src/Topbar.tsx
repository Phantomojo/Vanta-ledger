import React from 'react';

const Topbar: React.FC = () => (
  <header style={{ display: 'flex', alignItems: 'center', height: 64, background: '#fff', borderBottom: '1px solid #eee', padding: '0 2rem', gap: 32 }}>
    <div style={{ fontSize: 28, fontWeight: 700, color: '#18191a', flex: '0 0 220px' }}>Vanta Ledger</div>
    <input
      type="text"
      placeholder="Search..."
      style={{ flex: 1, fontSize: 18, padding: '0.5rem 1rem', borderRadius: 8, border: '1px solid #ddd', background: '#fafbfc' }}
    />
    <div style={{ display: 'flex', gap: 24 }}>
      <button style={{ background: 'none', border: 'none', fontSize: 22, cursor: 'pointer' }}>🔔</button>
      <button style={{ background: 'none', border: 'none', fontSize: 22, cursor: 'pointer' }}>🤖</button>
      <button style={{ background: 'none', border: 'none', fontSize: 22, cursor: 'pointer' }}>👤</button>
    </div>
  </header>
);

export default Topbar; 