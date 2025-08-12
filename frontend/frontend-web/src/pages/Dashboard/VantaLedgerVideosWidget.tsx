import React from 'react';

const VantaLedgerVideosWidget: React.FC = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Vanta Ledger Videos</h2>
        <span className="text-sm text-gray-500 dark:text-gray-400">Product Overview</span>
      </div>
      
      <div className="space-y-4">
        {/* First Video */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-2">
            Deconstructing Vanta Ledger
          </h3>
          <div className="relative">
            <video 
              className="w-full rounded-lg shadow-sm" 
              controls
              preload="metadata"
              poster="/banner.png"
            >
              <source src="/Deconstructing_Vanta_Ledger.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            An in-depth look at the Vanta Ledger system architecture and features.
          </p>
        </div>

        {/* Second Video */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h3 className="text-md font-medium text-gray-900 dark:text-white mb-2">
            AI-Powered Financial Document Management
          </h3>
          <div className="relative">
            <video 
              className="w-full rounded-lg shadow-sm" 
              controls
              preload="metadata"
              poster="/banner.png"
            >
              <source src="/Vanta_Ledger__AI-Powered_Financial_Document_Management.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            See how AI transforms financial document processing and management.
          </p>
        </div>
      </div>
    </div>
  );
};

export default VantaLedgerVideosWidget;
