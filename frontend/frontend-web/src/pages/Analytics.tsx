import React, { useState, useEffect } from "react";
import PageMeta from "../components/common/PageMeta";
import api from '../api';

interface AnalyticsData {
  financial_summary: {
    total_income: number;
    total_expenses: number;
    net_profit: number;
    profit_margin: number;
  };
  company_performance: {
    company_id: number;
    company_name: string;
    total_revenue: number;
    total_expenses: number;
    profit: number;
    project_count: number;
  }[];
  project_analytics: {
    project_id: number;
    project_name: string;
    budget: number;
    actual_cost: number;
    completion_percentage: number;
    status: string;
  }[];
  monthly_trends: {
    month: string;
    income: number;
    expenses: number;
    profit: number;
  }[];
  document_insights: {
    total_documents: number;
    processed_documents: number;
    analyzed_documents: number;
    document_types: { type: string; count: number }[];
  };
}

const Analytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedPeriod]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // For now, we'll use mock data since the backend might not have analytics endpoints yet
      // In a real implementation, you would call: api.get(`/analytics?period=${selectedPeriod}`)
      
      // Mock data
      const mockData: AnalyticsData = {
        financial_summary: {
          total_income: 2500000,
          total_expenses: 1800000,
          net_profit: 700000,
          profit_margin: 28.0
        },
        company_performance: [
          {
            company_id: 1,
            company_name: "Vanta Construction Ltd",
            total_revenue: 1500000,
            total_expenses: 1100000,
            profit: 400000,
            project_count: 8
          },
          {
            company_id: 2,
            company_name: "Nairobi Builders Co",
            total_revenue: 800000,
            total_expenses: 600000,
            profit: 200000,
            project_count: 5
          },
          {
            company_id: 3,
            company_name: "Mombasa Developers",
            total_revenue: 200000,
            total_expenses: 100000,
            profit: 100000,
            project_count: 2
          }
        ],
        project_analytics: [
          {
            project_id: 1,
            project_name: "Nairobi Office Complex",
            budget: 500000,
            actual_cost: 450000,
            completion_percentage: 85,
            status: "In Progress"
          },
          {
            project_id: 2,
            project_name: "Mombasa Hotel Renovation",
            budget: 300000,
            actual_cost: 280000,
            completion_percentage: 95,
            status: "Near Completion"
          },
          {
            project_id: 3,
            project_name: "Kisumu Shopping Mall",
            budget: 800000,
            actual_cost: 750000,
            completion_percentage: 70,
            status: "In Progress"
          }
        ],
        monthly_trends: [
          { month: "Jan", income: 200000, expenses: 150000, profit: 50000 },
          { month: "Feb", income: 250000, expenses: 180000, profit: 70000 },
          { month: "Mar", income: 300000, expenses: 200000, profit: 100000 },
          { month: "Apr", income: 280000, expenses: 190000, profit: 90000 },
          { month: "May", income: 320000, expenses: 220000, profit: 100000 },
          { month: "Jun", income: 350000, expenses: 240000, profit: 110000 }
        ],
        document_insights: {
          total_documents: 1250,
          processed_documents: 980,
          analyzed_documents: 750,
          document_types: [
            { type: "Invoice", count: 450 },
            { type: "Contract", count: 120 },
            { type: "Receipt", count: 300 },
            { type: "Bank Statement", count: 80 },
            { type: "Certificate", count: 100 },
            { type: "Other", count: 200 }
          ]
        }
      };

      setAnalyticsData(mockData);
    } catch (err: any) {
      setError('Failed to load analytics data.');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getProfitMarginColor = (margin: number) => {
    if (margin >= 25) return 'text-green-600 dark:text-green-400';
    if (margin >= 15) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getCompletionColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600 dark:text-green-400';
    if (percentage >= 70) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !analyticsData) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error || 'Failed to load analytics data'}</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <PageMeta
        title="Analytics | Vanta Ledger Dashboard"
        description="Comprehensive business analytics and insights for your construction business."
      />
      
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Analytics</h1>
              <p className="text-gray-600 dark:text-gray-400">Business insights and performance metrics</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                Export Report
              </button>
            </div>
          </div>
        </div>

        {/* Financial Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                <svg className="w-6 h-6 text-green-600 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Income</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-300">
                  {formatCurrency(analyticsData.financial_summary.total_income)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                <svg className="w-6 h-6 text-red-600 dark:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Expenses</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-300">
                  {formatCurrency(analyticsData.financial_summary.total_expenses)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Net Profit</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-300">
                  {formatCurrency(analyticsData.financial_summary.net_profit)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Profit Margin</p>
                <p className={`text-2xl font-bold ${getProfitMarginColor(analyticsData.financial_summary.profit_margin)}`}>
                  {analyticsData.financial_summary.profit_margin}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts and Detailed Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Company Performance */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Company Performance</h2>
            <div className="space-y-4">
              {analyticsData.company_performance.map((company) => (
                <div key={company.company_id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900 dark:text-white">{company.company_name}</h3>
                    <span className="text-sm text-gray-500 dark:text-gray-400">{company.project_count} projects</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Revenue</p>
                      <p className="font-medium text-green-600 dark:text-green-300">{formatCurrency(company.total_revenue)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Expenses</p>
                      <p className="font-medium text-red-600 dark:text-red-300">{formatCurrency(company.total_expenses)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Profit</p>
                      <p className="font-medium text-blue-600 dark:text-blue-300">{formatCurrency(company.profit)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Project Analytics */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Project Analytics</h2>
            <div className="space-y-4">
              {analyticsData.project_analytics.map((project) => (
                <div key={project.project_id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900 dark:text-white">{project.project_name}</h3>
                    <span className={`text-sm px-2 py-1 rounded-full ${
                      project.status === 'Completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                      project.status === 'Near Completion' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' :
                      'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Budget</p>
                      <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(project.budget)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Actual Cost</p>
                      <p className="font-medium text-gray-900 dark:text-white">{formatCurrency(project.actual_cost)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400">Completion</p>
                      <p className={`font-medium ${getCompletionColor(project.completion_percentage)}`}>
                        {project.completion_percentage}%
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${project.completion_percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Monthly Trends Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Monthly Financial Trends</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Month</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Income</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Expenses</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Profit</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Margin</th>
                </tr>
              </thead>
              <tbody>
                {analyticsData.monthly_trends.map((trend, index) => {
                  const margin = ((trend.profit / trend.income) * 100);
                  return (
                    <tr key={index} className="border-b border-gray-100 dark:border-gray-700">
                      <td className="py-3 px-4 text-sm text-gray-900 dark:text-white font-medium">{trend.month}</td>
                      <td className="py-3 px-4 text-sm text-green-600 dark:text-green-300">{formatCurrency(trend.income)}</td>
                      <td className="py-3 px-4 text-sm text-red-600 dark:text-red-300">{formatCurrency(trend.expenses)}</td>
                      <td className="py-3 px-4 text-sm text-blue-600 dark:text-blue-300">{formatCurrency(trend.profit)}</td>
                      <td className="py-3 px-4 text-sm">
                        <span className={getProfitMarginColor(margin)}>{margin.toFixed(1)}%</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Document Insights */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Document Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3">Document Processing Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Total Documents</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{analyticsData.document_insights.total_documents}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Processed</span>
                  <span className="text-sm font-medium text-blue-600 dark:text-blue-300">{analyticsData.document_insights.processed_documents}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Analyzed</span>
                  <span className="text-sm font-medium text-green-600 dark:text-green-300">{analyticsData.document_insights.analyzed_documents}</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-3">Document Types</h3>
              <div className="space-y-2">
                {analyticsData.document_insights.document_types.map((docType, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">{docType.type}</span>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">{docType.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Analytics; 