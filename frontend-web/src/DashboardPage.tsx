import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import PaperlessPage from './PaperlessPage';

const DashboardPage: React.FC = () => {
  const [section, setSection] = useState('dashboard');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Topbar />
      <div style={{ display: 'flex', flex: 1 }}>
        <Sidebar section={section} setSection={setSection} />
        <main style={{ flex: 1, padding: '2rem', background: '#fafbfc' }}>
          <h2>{section.charAt(0).toUpperCase() + section.slice(1)}</h2>
          {section === 'paperless' ? (
            <PaperlessPage />
          ) : (
            <div style={{ marginTop: '2rem', color: '#888' }}>
              [Placeholder for {section} section]
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default DashboardPage; 