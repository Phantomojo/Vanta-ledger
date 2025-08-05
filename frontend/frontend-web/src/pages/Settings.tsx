import React, { useState, useEffect } from "react";
import PageMeta from "../components/common/PageMeta";
import api from '../api';

interface ConfigData {
  data_sources: {
    use_real_data: boolean;
    real_data_file: string;
    ocr_data_dir: string;
    analysis_results_file: string;
    companies_list_file: string;
    projects_list_file: string;
  };
  mock_data: {
    enable_mock_data: boolean;
    auto_generate: boolean;
    data_volume: 'small' | 'medium' | 'large';
    date_range: {
      start: string;
      end: string;
    };
  };
  settings: {
    currency: string;
    date_format: string;
    timezone: string;
    language: string;
    max_file_size: string;
    allowed_file_types: string[];
  };
  customization: {
    company_types: string[];
    project_categories: string[];
    document_types: string[];
    transaction_types: string[];
    subcontractor_specializations: string[];
  };
}

const Settings: React.FC = () => {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [activeTab, setActiveTab] = useState('data-sources');

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await api.get('/config/');
      setConfig(response.data);
    } catch (error) {
      console.error('Error fetching config:', error);
      setMessage({ type: 'error', text: 'Failed to load configuration' });
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async (updates: Partial<ConfigData>) => {
    if (!config) return;
    
    setSaving(true);
    try {
      const response = await api.put('/config/', updates);
      setConfig(response.data.config);
      setMessage({ type: 'success', text: 'Configuration updated successfully' });
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error updating config:', error);
      setMessage({ type: 'error', text: 'Failed to update configuration' });
    } finally {
      setSaving(false);
    }
  };

  const handleDataExport = async () => {
    try {
      const response = await api.post('/data/export');
      setMessage({ type: 'success', text: `Data exported to ${response.data.filename}` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to export data' });
    }
  };

  const handleDataImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/data/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage({ type: 'success', text: 'Data imported successfully' });
      fetchConfig(); // Refresh config
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to import data' });
    }
  };

  const handleRegenerateMockData = async () => {
    try {
      await api.post('/data/regenerate');
      setMessage({ type: 'success', text: 'Mock data regenerated successfully' });
      fetchConfig(); // Refresh config
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to regenerate mock data' });
    }
  };

  const addCustomizationItem = (category: keyof ConfigData['customization'], item: string) => {
    if (!config || !item.trim()) return;
    
    const updatedConfig = {
      ...config,
      customization: {
        ...config.customization,
        [category]: [...config.customization[category], item.trim()]
      }
    };
    updateConfig(updatedConfig);
  };

  const removeCustomizationItem = (category: keyof ConfigData['customization'], index: number) => {
    if (!config) return;
    
    const updatedConfig = {
      ...config,
      customization: {
        ...config.customization,
        [category]: config.customization[category].filter((_, i) => i !== index)
      }
    };
    updateConfig(updatedConfig);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="p-6">
        <div className="text-center text-red-500">
          Failed to load configuration
        </div>
      </div>
    );
  }

  return (
    <>
      <PageMeta title="Settings | Vanta Ledger Dashboard" description="Configure system settings, data sources, and customization options." />
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
          <p className="text-gray-600 dark:text-gray-400">Configure system settings and data management</p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8 border-b border-gray-200 dark:border-gray-700">
            {[
              { id: 'data-sources', label: 'Data Sources' },
              { id: 'mock-data', label: 'Mock Data' },
              { id: 'system-settings', label: 'System Settings' },
              { id: 'customization', label: 'Customization' },
              { id: 'data-management', label: 'Data Management' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Data Sources Tab */}
        {activeTab === 'data-sources' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Data Source Configuration</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Use Real Data</label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Load data from OCR analysis results</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.data_sources.use_real_data}
                      onChange={(e) => updateConfig({
                        data_sources: { ...config.data_sources, use_real_data: e.target.checked }
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Real Data File Path
                  </label>
                  <input
                    type="text"
                    value={config.data_sources.real_data_file}
                    onChange={(e) => updateConfig({
                      data_sources: { ...config.data_sources, real_data_file: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    OCR Data Directory
                  </label>
                  <input
                    type="text"
                    value={config.data_sources.ocr_data_dir}
                    onChange={(e) => updateConfig({
                      data_sources: { ...config.data_sources, ocr_data_dir: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mock Data Tab */}
        {activeTab === 'mock-data' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Mock Data Configuration</h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Enable Mock Data</label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Generate mock data for testing</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.mock_data.enable_mock_data}
                      onChange={(e) => updateConfig({
                        mock_data: { ...config.mock_data, enable_mock_data: e.target.checked }
                      })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Data Volume
                  </label>
                  <select
                    value={config.mock_data.data_volume}
                    onChange={(e) => updateConfig({
                      mock_data: { ...config.mock_data, data_volume: e.target.value as 'small' | 'medium' | 'large' }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="small">Small (3-5 items)</option>
                    <option value="medium">Medium (8-12 items)</option>
                    <option value="large">Large (15-25 items)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Start Date
                    </label>
                    <input
                      type="date"
                      value={config.mock_data.date_range.start}
                      onChange={(e) => updateConfig({
                        mock_data: { 
                          ...config.mock_data, 
                          date_range: { ...config.mock_data.date_range, start: e.target.value }
                        }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      End Date
                    </label>
                    <input
                      type="date"
                      value={config.mock_data.date_range.end}
                      onChange={(e) => updateConfig({
                        mock_data: { 
                          ...config.mock_data, 
                          date_range: { ...config.mock_data.date_range, end: e.target.value }
                        }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    />
                  </div>
                </div>

                <button
                  onClick={handleRegenerateMockData}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Regenerate Mock Data
                </button>
              </div>
            </div>
          </div>
        )}

        {/* System Settings Tab */}
        {activeTab === 'system-settings' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">System Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Currency
                  </label>
                  <select
                    value={config.settings.currency}
                    onChange={(e) => updateConfig({
                      settings: { ...config.settings, currency: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="KES">Kenyan Shilling (KES)</option>
                    <option value="USD">US Dollar (USD)</option>
                    <option value="EUR">Euro (EUR)</option>
                    <option value="GBP">British Pound (GBP)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Date Format
                  </label>
                  <select
                    value={config.settings.date_format}
                    onChange={(e) => updateConfig({
                      settings: { ...config.settings, date_format: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="%Y-%m-%d">YYYY-MM-DD</option>
                    <option value="%d/%m/%Y">DD/MM/YYYY</option>
                    <option value="%m/%d/%Y">MM/DD/YYYY</option>
                    <option value="%d-%m-%Y">DD-MM-YYYY</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Timezone
                  </label>
                  <select
                    value={config.settings.timezone}
                    onChange={(e) => updateConfig({
                      settings: { ...config.settings, timezone: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="Africa/Nairobi">Africa/Nairobi</option>
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="Europe/London">Europe/London</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Language
                  </label>
                  <select
                    value={config.settings.language}
                    onChange={(e) => updateConfig({
                      settings: { ...config.settings, language: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="en">English</option>
                    <option value="sw">Swahili</option>
                    <option value="fr">French</option>
                    <option value="es">Spanish</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max File Size
                  </label>
                  <select
                    value={config.settings.max_file_size}
                    onChange={(e) => updateConfig({
                      settings: { ...config.settings, max_file_size: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="5MB">5 MB</option>
                    <option value="10MB">10 MB</option>
                    <option value="25MB">25 MB</option>
                    <option value="50MB">50 MB</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Customization Tab */}
        {activeTab === 'customization' && (
          <div className="space-y-6">
            {Object.entries(config.customization).map(([category, items]) => (
              <div key={category} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 capitalize">
                  {category.replace('_', ' ')}
                </h3>
                
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder={`Add new ${category.replace('_', ' ').slice(0, -1)}`}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addCustomizationItem(category as keyof ConfigData['customization'], e.currentTarget.value);
                          e.currentTarget.value = '';
                        }
                      }}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    />
                    <button
                      onClick={(e) => {
                        const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                        addCustomizationItem(category as keyof ConfigData['customization'], input.value);
                        input.value = '';
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      Add
                    </button>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {items.map((item, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                      >
                        {item}
                        <button
                          onClick={() => removeCustomizationItem(category as keyof ConfigData['customization'], index)}
                          className="ml-2 inline-flex items-center justify-center w-4 h-4 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Data Management Tab */}
        {activeTab === 'data-management' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Data Management</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">Export Data</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                    Export all current data to a JSON file for backup or migration
                  </p>
                  <button
                    onClick={handleDataExport}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  >
                    Export Data
                  </button>
                </div>

                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <h4 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">Import Data</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                    Import data from a previously exported JSON file
                  </p>
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleDataImport}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-200"
                  />
                </div>

                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <h4 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-2">System Information</h4>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Current Data Source:</span>
                        <span className="ml-2 text-gray-600 dark:text-gray-400">
                          {config.data_sources.use_real_data ? 'Real Data' : 'Mock Data'}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Currency:</span>
                        <span className="ml-2 text-gray-600 dark:text-gray-400">{config.settings.currency}</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Timezone:</span>
                        <span className="ml-2 text-gray-600 dark:text-gray-400">{config.settings.timezone}</span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700 dark:text-gray-300">Language:</span>
                        <span className="ml-2 text-gray-600 dark:text-gray-400">{config.settings.language}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Save Button */}
        <div className="mt-8 flex justify-end">
          <button
            onClick={() => updateConfig(config)}
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </>
  );
};

export default Settings; 