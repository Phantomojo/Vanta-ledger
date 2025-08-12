import React, { useState, useEffect } from "react";
import PageMeta from "../components/common/PageMeta";
import api from '../api';

interface Subcontractor {
  id: number;
  name: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  specialization: string;
  rating: number;
  status: 'active' | 'inactive' | 'pending';
  total_projects: number;
  completed_projects: number;
  total_value: number;
  average_rating: number;
  created_at: string;
  last_project_date?: string;
}

interface SubcontractorProject {
  id: number;
  project_name: string;
  project_value: number;
  start_date: string;
  end_date?: string;
  status: 'ongoing' | 'completed' | 'cancelled';
  rating?: number;
  feedback?: string;
}

const Subcontractors: React.FC = () => {
  const [subcontractors, setSubcontractors] = useState<Subcontractor[]>([]);
  const [selectedSubcontractor, setSelectedSubcontractor] = useState<Subcontractor | null>(null);
  const [subcontractorProjects, setSubcontractorProjects] = useState<SubcontractorProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedSpecialization, setSelectedSpecialization] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('name');

  // Form states
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    company_name: '',
    contact_person: '',
    email: '',
    phone: '',
    specialization: ''
  });

  useEffect(() => {
    fetchSubcontractors();
  }, []);

  const fetchSubcontractors = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock data for now - replace with actual API call
      const mockSubcontractors: Subcontractor[] = [
        {
          id: 1,
          name: "John Kamau",
          company_name: "Kamau Construction Ltd",
          contact_person: "John Kamau",
          email: "john@kamauc Construction.com",
          phone: "+254 700 123 456",
          specialization: "Electrical",
          rating: 4.5,
          status: 'active',
          total_projects: 15,
          completed_projects: 12,
          total_value: 2500000,
          average_rating: 4.5,
          created_at: '2023-01-15T10:30:00Z',
          last_project_date: '2024-01-20T14:30:00Z'
        },
        {
          id: 2,
          name: "Sarah Muthoni",
          company_name: "Muthoni Plumbing Services",
          contact_person: "Sarah Muthoni",
          email: "sarah@muthoniplumbing.com",
          phone: "+254 711 234 567",
          specialization: "Plumbing",
          rating: 4.8,
          status: 'active',
          total_projects: 22,
          completed_projects: 20,
          total_value: 1800000,
          average_rating: 4.8,
          created_at: '2023-02-10T09:15:00Z',
          last_project_date: '2024-02-01T16:45:00Z'
        },
        {
          id: 3,
          name: "David Ochieng",
          company_name: "Ochieng Roofing Co",
          contact_person: "David Ochieng",
          email: "david@ochiengroofing.com",
          phone: "+254 722 345 678",
          specialization: "Roofing",
          rating: 4.2,
          status: 'active',
          total_projects: 8,
          completed_projects: 7,
          total_value: 1200000,
          average_rating: 4.2,
          created_at: '2023-03-05T11:20:00Z',
          last_project_date: '2024-01-15T12:00:00Z'
        },
        {
          id: 4,
          name: "Grace Wanjiku",
          company_name: "Wanjiku Painting Services",
          contact_person: "Grace Wanjiku",
          email: "grace@wanjikupainting.com",
          phone: "+254 733 456 789",
          specialization: "Painting",
          rating: 4.6,
          status: 'inactive',
          total_projects: 18,
          completed_projects: 16,
          total_value: 900000,
          average_rating: 4.6,
          created_at: '2023-01-20T14:45:00Z',
          last_project_date: '2023-12-10T10:30:00Z'
        }
      ];

      setSubcontractors(mockSubcontractors);
    } catch (err: any) {
      setError('Failed to load subcontractors.');
      console.error('Error fetching subcontractors:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubcontractorProjects = async (subcontractorId: number) => {
    try {
      // Mock data for subcontractor projects
      const mockProjects: SubcontractorProject[] = [
        {
          id: 1,
          project_name: "Nairobi Office Complex - Electrical",
          project_value: 500000,
          start_date: '2024-01-01',
          end_date: '2024-03-15',
          status: 'completed',
          rating: 4.5,
          feedback: 'Excellent work quality and timely completion.'
        },
        {
          id: 2,
          project_name: "Mombasa Hotel - Electrical Systems",
          project_value: 750000,
          start_date: '2024-02-01',
          end_date: '2024-04-30',
          status: 'ongoing',
          rating: undefined,
          feedback: undefined
        }
      ];

      setSubcontractorProjects(mockProjects);
    } catch (err: any) {
      console.error('Error fetching subcontractor projects:', err);
    }
  };

  const handleSubcontractorSelect = (subcontractor: Subcontractor) => {
    setSelectedSubcontractor(subcontractor);
    fetchSubcontractorProjects(subcontractor.id);
  };

  const handleAddSubcontractor = async () => {
    try {
      // Mock API call - replace with actual API call
      const newSubcontractor: Subcontractor = {
        id: subcontractors.length + 1,
        ...formData,
        rating: 0,
        status: 'pending',
        total_projects: 0,
        completed_projects: 0,
        total_value: 0,
        average_rating: 0,
        created_at: new Date().toISOString()
      };

      setSubcontractors([...subcontractors, newSubcontractor]);
      setShowAddForm(false);
      setFormData({
        name: '',
        company_name: '',
        contact_person: '',
        email: '',
        phone: '',
        specialization: ''
      });
    } catch (err: any) {
      setError('Failed to add subcontractor.');
      console.error('Error adding subcontractor:', err);
    }
  };

  const getFilteredSubcontractors = () => {
    return subcontractors.filter(subcontractor => {
      // Status filter
      if (selectedStatus !== 'all' && subcontractor.status !== selectedStatus) {
        return false;
      }
      
      // Specialization filter
      if (selectedSpecialization !== 'all' && subcontractor.specialization !== selectedSpecialization) {
        return false;
      }
      
      // Search term filter
      if (searchTerm && !subcontractor.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !subcontractor.company_name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
      
      return true;
    }).sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'rating':
          return b.rating - a.rating;
        case 'projects':
          return b.total_projects - a.total_projects;
        case 'value':
          return b.total_value - a.total_value;
        default:
          return 0;
      }
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300';
      case 'inactive': return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300';
      case 'pending': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getProjectStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300';
      case 'ongoing': return 'text-blue-600 bg-blue-100 dark:bg-blue-900 dark:text-blue-300';
      case 'cancelled': return 'text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-1 text-sm text-gray-600 dark:text-gray-400">({rating})</span>
      </div>
    );
  };

  const filteredSubcontractors = getFilteredSubcontractors();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <>
      <PageMeta
        title="Subcontractors | Vanta Ledger Dashboard"
        description="Manage subcontractors, track performance, and handle contracts."
      />
      
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Subcontractors</h1>
              <p className="text-gray-600 dark:text-gray-400">Manage subcontractors and track their performance</p>
            </div>
            <button
              onClick={() => setShowAddForm(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Add Subcontractor
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Subcontractors List */}
          <div className="lg:col-span-2 space-y-6">
            {/* Filters */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
                  <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Specialization</label>
                  <select
                    value={selectedSpecialization}
                    onChange={(e) => setSelectedSpecialization(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="all">All Specializations</option>
                    <option value="Electrical">Electrical</option>
                    <option value="Plumbing">Plumbing</option>
                    <option value="Roofing">Roofing</option>
                    <option value="Painting">Painting</option>
                    <option value="Carpentry">Carpentry</option>
                    <option value="Masonry">Masonry</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="name">Name</option>
                    <option value="rating">Rating</option>
                    <option value="projects">Projects</option>
                    <option value="value">Total Value</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Search</label>
                  <input
                    type="text"
                    placeholder="Search subcontractors..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
            </div>

            {/* Subcontractors Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredSubcontractors.length === 0 ? (
                <div className="col-span-full text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">No subcontractors found</p>
                </div>
              ) : (
                filteredSubcontractors.map((subcontractor) => (
                  <div
                    key={subcontractor.id}
                    onClick={() => handleSubcontractorSelect(subcontractor)}
                    className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 cursor-pointer hover:shadow-md transition-shadow ${
                      selectedSubcontractor?.id === subcontractor.id ? 'ring-2 ring-indigo-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white">{subcontractor.name}</h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{subcontractor.company_name}</p>
                      </div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(subcontractor.status)}`}>
                        {subcontractor.status.charAt(0).toUpperCase() + subcontractor.status.slice(1)}
                      </span>
                    </div>

                    <div className="space-y-2 mb-3">
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 dark:text-gray-400 mr-2">Specialization:</span>
                        <span className="font-medium text-gray-900 dark:text-white">{subcontractor.specialization}</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 dark:text-gray-400 mr-2">Rating:</span>
                        {renderStars(subcontractor.rating)}
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 dark:text-gray-400 mr-2">Projects:</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {subcontractor.completed_projects}/{subcontractor.total_projects}
                        </span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 dark:text-gray-400 mr-2">Total Value:</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {formatCurrency(subcontractor.total_value)}
                        </span>
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      <button className="flex-1 px-3 py-1 text-xs bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-300 dark:hover:bg-indigo-800">
                        View Details
                      </button>
                      <button className="flex-1 px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 dark:bg-green-900 dark:text-green-300 dark:hover:bg-green-800">
                        Contact
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Subcontractor Details */}
          <div className="space-y-6">
            {selectedSubcontractor ? (
              <>
                {/* Subcontractor Info */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Subcontractor Details</h2>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
                      <p className="text-sm text-gray-900 dark:text-white">{selectedSubcontractor.name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Company</label>
                      <p className="text-sm text-gray-900 dark:text-white">{selectedSubcontractor.company_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Contact Person</label>
                      <p className="text-sm text-gray-900 dark:text-white">{selectedSubcontractor.contact_person}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
                      <p className="text-sm text-gray-900 dark:text-white">{selectedSubcontractor.email}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Phone</label>
                      <p className="text-sm text-gray-900 dark:text-white">{selectedSubcontractor.phone}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Specialization</label>
                      <p className="text-sm text-gray-900 dark:text-white">{selectedSubcontractor.specialization}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Rating</label>
                      <div className="mt-1">{renderStars(selectedSubcontractor.rating)}</div>
                    </div>
                  </div>

                  <div className="mt-6 flex space-x-2">
                    <button className="flex-1 px-3 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700">
                      Edit
                    </button>
                    <button className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700">
                      Contact
                    </button>
                  </div>
                </div>

                {/* Projects */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Projects</h2>
                  
                  <div className="space-y-3">
                    {subcontractorProjects.length === 0 ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400">No projects found</p>
                    ) : (
                      subcontractorProjects.map((project) => (
                        <div key={project.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                          <div className="flex items-start justify-between mb-2">
                            <h3 className="font-medium text-gray-900 dark:text-white text-sm">{project.project_name}</h3>
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getProjectStatusColor(project.status)}`}>
                              {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                            </span>
                          </div>
                          <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                              <span className="text-gray-500 dark:text-gray-400">Value:</span>
                              <span className="text-gray-900 dark:text-white">{formatCurrency(project.project_value)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500 dark:text-gray-400">Duration:</span>
                              <span className="text-gray-900 dark:text-white">
                                {new Date(project.start_date).toLocaleDateString()} - 
                                {project.end_date ? new Date(project.end_date).toLocaleDateString() : 'Ongoing'}
                              </span>
                            </div>
                            {project.rating && (
                              <div className="flex justify-between">
                                <span className="text-gray-500 dark:text-gray-400">Rating:</span>
                                <div className="flex items-center">
                                  {[1, 2, 3, 4, 5].map((star) => (
                                    <svg
                                      key={star}
                                      className={`w-3 h-3 ${
                                        star <= project.rating! ? 'text-yellow-400' : 'text-gray-300'
                                      }`}
                                      fill="currentColor"
                                      viewBox="0 0 20 20"
                                    >
                                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                    </svg>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="text-center">
                  <div className="text-gray-400 mb-4">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">Select a subcontractor to view details</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Add Subcontractor Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Add New Subcontractor</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Company Name</label>
                  <input
                    type="text"
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contact Person</label>
                  <input
                    type="text"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Specialization</label>
                  <select
                    value={formData.specialization}
                    onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="">Select Specialization</option>
                    <option value="Electrical">Electrical</option>
                    <option value="Plumbing">Plumbing</option>
                    <option value="Roofing">Roofing</option>
                    <option value="Painting">Painting</option>
                    <option value="Carpentry">Carpentry</option>
                    <option value="Masonry">Masonry</option>
                  </select>
                </div>
              </div>

              <div className="mt-6 flex space-x-3">
                <button
                  onClick={handleAddSubcontractor}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  Add Subcontractor
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Subcontractors; 