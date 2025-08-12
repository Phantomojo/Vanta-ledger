import React, { useEffect, useState } from 'react';
import api from '../../api';

interface Company {
  id: number;
  name: string;
}

interface LedgerEntry {
  id: number;
  type: string; // 'income' | 'expense' | 'withdrawal'
  amount: number;
}

const AccountBalancesWidget: React.FC = () => {
  const [balances, setBalances] = useState<{ company: Company; balance: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalances = async () => {
      setLoading(true);
      setError(null);
      try {
        const companiesRes = await api.get<Company[]>('/companies');
        const companies = companiesRes.data;
        const balancesData: { company: Company; balance: number }[] = [];
        for (const company of companies) {
          const ledgerRes = await api.get<LedgerEntry[]>(`/ledger/company/${company.id}`);
          const ledger = ledgerRes.data;
          let income = 0, expense = 0, withdrawal = 0;
          for (const entry of ledger) {
            if (entry.type === 'income') income += entry.amount;
            else if (entry.type === 'expense') expense += entry.amount;
            else if (entry.type === 'withdrawal') withdrawal += entry.amount;
          }
          const balance = income - expense - withdrawal;
          balancesData.push({ company, balance });
        }
        setBalances(balancesData);
      } catch (err: any) {
        setError('Failed to load account balances.');
      } finally {
        setLoading(false);
      }
    };
    fetchBalances();
  }, []);

  if (loading) return <div>Loading account balances...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      {balances.length === 0 ? (
        <div>No companies found.</div>
      ) : (
        <ul className="space-y-2">
          {balances.map(({ company, balance }) => (
            <li key={company.id} className="flex justify-between items-center bg-gray-100 dark:bg-gray-800 rounded p-3">
              <span className="font-medium">{company.name}</span>
              <span className="font-mono text-lg">{balance.toLocaleString(undefined, { style: 'currency', currency: 'KES' })}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AccountBalancesWidget; 