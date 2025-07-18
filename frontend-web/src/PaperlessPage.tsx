import React, { useEffect, useState } from 'react';

interface Document {
  id: number;
  title: string;
  tags: string[];
  path: string;
}

const PaperlessPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);

  useEffect(() => {
    // TODO: Replace with real API call
    fetch('/api/paperless/documents')
      .then(res => res.json())
      .then(setDocuments);
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Paperless Document Library</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 24 }}>
        <thead>
          <tr style={{ background: '#f5f5f5' }}>
            <th style={{ padding: 8, border: '1px solid #eee' }}>Title</th>
            <th style={{ padding: 8, border: '1px solid #eee' }}>Tags</th>
            <th style={{ padding: 8, border: '1px solid #eee' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map(doc => (
            <tr key={doc.id}>
              <td style={{ padding: 8, border: '1px solid #eee' }}>{doc.title}</td>
              <td style={{ padding: 8, border: '1px solid #eee' }}>{doc.tags.join(', ')}</td>
              <td style={{ padding: 8, border: '1px solid #eee' }}>
                <a href={doc.path} target="_blank" rel="noopener noreferrer">Preview/Download</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PaperlessPage; 