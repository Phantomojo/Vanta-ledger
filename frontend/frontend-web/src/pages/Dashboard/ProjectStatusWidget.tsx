import React, { useEffect, useState } from 'react';
import { vantaApi } from '../../api';

interface Project {
  id: string;
  name: string;
  company_id: string;
  status: 'active' | 'planning' | 'completed' | 'on_hold' | 'cancelled';
  start_date?: string;
  end_date?: string;
  budget?: number;
  description?: string;
}

interface Company {
  id: string;
  name: string;
}

const ProjectStatusWidget: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [projectsRes, companiesRes] = await Promise.all([
          vantaApi.getProjects(),
          vantaApi.getCompanies()
        ]);

        setProjects(projectsRes.data);
        setCompanies(companiesRes.data.companies);
      } catch (err: any) {
        setError('Failed to load project status.');
        console.error('Error fetching projects:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusStats = () => {
    const stats = {
      active: 0,
      planning: 0,
      completed: 0,
      on_hold: 0,
      cancelled: 0
    };

    projects.forEach(project => {
      if (stats.hasOwnProperty(project.status)) {
        stats[project.status as keyof typeof stats]++;
      }
    });

    return stats;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'planning':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-purple-500';
      case 'on_hold':
        return 'bg-yellow-500';
      case 'cancelled':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'planning':
        return 'Planning';
      case 'completed':
        return 'Completed';
      case 'on_hold':
        return 'On Hold';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  };

  const getCompanyName = (companyId: string): string => {
    const company = companies.find(c => c.id === companyId);
    return company?.name || 'Unknown Company';
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const calculateProgress = (project: Project): number => {
    if (!project.start_date || !project.end_date) return 0;
    
    const start = new Date(project.start_date).getTime();
    const end = new Date(project.end_date).getTime();
    const now = new Date().getTime();
    
    if (now < start) return 0;
    if (now > end) return 100;
    
    return Math.round(((now - start) / (end - start)) * 100);
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 60) return 'bg-blue-500';
    if (progress >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const stats = getStatusStats();
  const totalProjects = projects.length;

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={`skeleton-stat-${i}`} className="space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
              </div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={`skeleton-project-${i}`} className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-gray-600 dark:text-gray-400">{error}</p>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 mb-2">
          <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <p className="text-gray-600 dark:text-gray-400">No projects found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Project Status Overview</h3>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(stats).map(([status, count]) => (
            <div key={status} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`}></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {getStatusLabel(status)}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {count} {count === 1 ? 'project' : 'projects'}
                </p>
              </div>
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {totalProjects > 0 ? Math.round((count / totalProjects) * 100) : 0}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Projects */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">Active Projects</h3>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {projects.filter(p => p.status === 'active').length} projects
          </span>
        </div>
        
        <div className="space-y-3">
          {projects
            .filter(project => project.status === 'active')
            .slice(0, 3)
            .map(project => {
              const progress = calculateProgress(project);
              return (
                <div key={project.id} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {project.name}
                    </h4>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {progress}%
                    </span>
                  </div>
                  
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                    {getCompanyName(project.company_id)}
                  </p>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500 dark:text-gray-400">Budget</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {project.budget ? formatCurrency(project.budget) : 'N/A'}
                      </span>
                    </div>
                    
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${getProgressColor(progress)} transition-all duration-300`}
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>
                        {project.start_date ? new Date(project.start_date).toLocaleDateString('en-KE', { month: 'short', day: 'numeric' }) : 'N/A'}
                      </span>
                      <span>
                        {project.end_date ? new Date(project.end_date).toLocaleDateString('en-KE', { month: 'short', day: 'numeric' }) : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
        
        {projects.filter(p => p.status === 'active').length > 3 && (
          <div className="mt-3 text-center">
            <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
              View All Active Projects
            </button>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {totalProjects}
            </div>
            <div className="text-gray-500 dark:text-gray-400">Total Projects</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {formatCurrency(projects.reduce((sum, p) => sum + (p.budget || 0), 0))}
            </div>
            <div className="text-gray-500 dark:text-gray-400">Total Budget</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectStatusWidget; 