import React from 'react';
import PageMeta from "../../components/common/PageMeta";
import AccountBalancesWidget from './AccountBalancesWidget';
import RecentTransactionsWidget from './RecentTransactionsWidget';
import ProjectStatusWidget from './ProjectStatusWidget';
import DocumentComplianceWidget from './DocumentComplianceWidget';
import VantaLedgerVideosWidget from './VantaLedgerVideosWidget';

export default function Home() {
  const title = "Dashboard | Vanta Ledger Dashboard";
  const description = "This is the main dashboard page for the Vanta Ledger Dashboard.";

  return (
    <>
      <PageMeta
        title={title}
        description={description}
      />
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3 md:gap-4 lg:gap-6">
        {/* Account Balances Widget */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-4">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <AccountBalancesWidget />
          </div>
        </div>

        {/* Recent Transactions Widget */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-8">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <RecentTransactionsWidget />
          </div>
        </div>

        {/* Project Status Widget */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <ProjectStatusWidget />
          </div>
        </div>

        {/* Document Compliance Widget */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <DocumentComplianceWidget />
          </div>
        </div>

        {/* Tender Pipeline Widget - Placeholder for now */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Tender Pipeline</h2>
              <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                View All
              </button>
            </div>
            <div className="text-center py-8">
              <div className="text-gray-400 mb-2">
                <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-400">Tender tracking coming soon</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Active tenders, deadlines, win/loss rates
              </p>
            </div>
          </div>
        </div>

        {/* Analytics & KPIs Widget - Placeholder for now */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Analytics & KPIs</h2>
              <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                View Details
              </button>
            </div>
            <div className="text-center py-8">
              <div className="text-gray-400 mb-2">
                <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-400">Analytics dashboard coming soon</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Cash flow, profitability, custom reports
              </p>
            </div>
          </div>
        </div>

        {/* Company Overview Widget - Placeholder for now */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Company Overview</h2>
              <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                Manage Companies
              </button>
            </div>
            <div className="text-center py-8">
              <div className="text-gray-400 mb-2">
                <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-400">Company management coming soon</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Summary of all companies, quick links
              </p>
            </div>
          </div>
        </div>

        {/* Vanta Ledger Videos Widget */}
        <div className="col-span-1 sm:col-span-2 lg:col-span-12 xl:col-span-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 md:p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <VantaLedgerVideosWidget />
          </div>
        </div>
      </div>
    </>
  );
}
