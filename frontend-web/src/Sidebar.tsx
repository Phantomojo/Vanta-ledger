import React from 'react';

const SECTIONS = [
  { key: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { key: 'paperless', label: 'Paperless', icon: '📄' },
  { key: 'admin', label: 'Admin', icon: '💼' },
  { key: 'documents', label: 'Documents', icon: '📄' },
  { key: 'ledger', label: 'Ledger', icon: '💰' },
  { key: 'projects', label: 'Projects', icon: '📁' },
  { key: 'companies', label: 'Companies', icon: '🏢' },
  { key: 'subcontractors', label: 'Subcontractors', icon: '🤝' },
  { key: 'analytics', label: 'Analytics', icon: '📊' },
  { key: 'review', label: 'Review Tools', icon: '📝' },
  { key: 'force_scan', label: 'Force Scan', icon: '🔍' },
  { key: 'settings', label: 'Settings', icon: '⚙️' },
];

type SidebarProps = {
  section: string;
  setSection: (key: string) => void;
};

const Sidebar: React.FC<SidebarProps> = ({ section, setSection }) => (
  <nav style={{ width: 220, background: '#18191a', color: '#fff', display: 'flex', flexDirection: 'column', padding: '2rem 0' }}>
    {SECTIONS.map(({ key, label, icon }) => (
      <button
        key={key}
        onClick={() => setSection(key)}
        style={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          background: key === section ? '#232526' : 'none',
          color: '#fff',
          border: 'none',
          outline: 'none',
          padding: '0.75rem 2rem',
          fontSize: 17,
          fontWeight: key === section ? 700 : 400,
          cursor: 'pointer',
          transition: 'background 0.2s',
        }}
      >
        <span style={{ fontSize: 22, marginRight: 16 }}>{icon}</span>
        {label}
      </button>
    ))}
    <div style={{ flex: 1 }} />
  </nav>
);

export default Sidebar; 