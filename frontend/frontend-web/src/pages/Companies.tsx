import React, { useEffect, useState } from 'react';
import { vantaApi } from '../api';

interface Company {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

const Companies: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompanies = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await vantaApi.getCompanies();
        setCompanies(res.data.companies);
      } catch (err: any) {
        setError('Failed to load companies.');
      } finally {
        setLoading(false);
      }
    };
    fetchCompanies();
  }, []);

  return (
  <div className="p-8">
    <h1 className="text-2xl font-bold mb-4">Companies</h1>
      {loading && <div>Loading companies...</div>}
      {error && <div className="text-red-500">{error}</div>}
      {!loading && !error && companies.length === 0 && (
        <div>No companies found.</div>
      )}
      {!loading && !error && companies.length > 0 && (
        <table className="min-w-full bg-white dark:bg-gray-900 rounded shadow">
          <thead>
            <tr>
              <th className="py-2 px-4 text-left">Name</th>
              <th className="py-2 px-4 text-left">Description</th>
              <th className="py-2 px-4 text-left">Created</th>
              <th className="py-2 px-4 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((company) => (
                              <tr key={company.id || `company-${company.name}`} className="border-t border-gray-200 dark:border-gray-800">
                <td className="py-2 px-4 font-medium">{company.name}</td>
                <td className="py-2 px-4">{company.description || '-'}</td>
                <td className="py-2 px-4">{company.created_at ? new Date(company.created_at).toLocaleDateString() : '-'}</td>
                <td className="py-2 px-4">
                  {/* Future: Add detail, edit, delete buttons here */}
                  <button className="text-blue-600 hover:underline mr-2" disabled>View</button>
                  <button className="text-green-600 hover:underline mr-2" disabled>Edit</button>
                  <button className="text-red-600 hover:underline" disabled>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
  </div>
);
};

export default Companies; 