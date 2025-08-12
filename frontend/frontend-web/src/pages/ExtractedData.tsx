import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Progress } from '../components/ui/progress';
import { Download, Filter, TrendingUp, DollarSign, Calendar, Building } from 'lucide-react';
import api from '../api';

interface ExtractedDataItem {
  id: number;
  document_id: number;
  filename: string;
  company_name?: string;
  transaction_date?: string;
  amount?: number;
  currency: string;
  transaction_type?: string;
  category?: string;
  description?: string;
  reference_number?: string;
  vendor_name?: string;
  invoice_number?: string;
  tax_amount?: number;
  payment_method?: string;
  confidence_score: number;
  extraction_method: string;
  extracted_at: string;
}

interface AnalyticsData {
  total_documents: number;
  confidence_stats: {
    average: number;
    minimum: number;
    maximum: number;
    high_confidence_count: number;
  };
  amount_stats: {
    documents_with_amounts: number;
    total_amount: number;
    average_amount: number;
    minimum_amount: number;
    maximum_amount: number;
  };
  transaction_types: Array<{ type: string; count: number }>;
  categories: Array<{ category: string; count: number }>;
}

const ExtractedData: React.FC = () => {
  const [data, setData] = useState<ExtractedDataItem[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit] = useState(50);
  const [filters, setFilters] = useState({
    min_confidence: 0.0,
    has_amount: undefined as boolean | undefined,
    transaction_type: '',
    category: '',
  });
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchData();
    fetchAnalytics();
  }, [page, filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        min_confidence: filters.min_confidence.toString(),
        ...(filters.has_amount !== undefined && { has_amount: filters.has_amount.toString() }),
        ...(filters.transaction_type && { transaction_type: filters.transaction_type }),
        ...(filters.category && { category: filters.category }),
      });

      const response = await api.get(`/extracted-data/?${params}`);
      setData(response.data.data);
      setTotalCount(response.data.total);
    } catch (error) {
      console.error('Failed to fetch extracted data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/extracted-data/analytics');
      setAnalytics(response.data.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const params = new URLSearchParams({
        format,
        min_confidence: filters.min_confidence.toString(),
      });

      if (format === 'csv') {
        const response = await api.get(`/extracted-data/export?${params}`, {
          responseType: 'blob',
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `extracted_data.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } else {
        const response = await api.get(`/extracted-data/export?${params}`);
        const dataStr = JSON.stringify(response.data.data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'extracted_data.json');
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const formatCurrency = (amount: number, currency: string = 'KES') => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-KE');
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Extracted Financial Data</h1>
          <p className="text-muted-foreground">
            AI-powered financial data extraction and analysis
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => handleExport('json')} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export JSON
          </Button>
          <Button onClick={() => handleExport('csv')} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_documents.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Successfully extracted
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Financial Documents</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.amount_stats.documents_with_amounts.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                With amounts: {formatCurrency(analytics.amount_stats.total_amount)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Confidence</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(analytics.confidence_stats.average * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {analytics.confidence_stats.high_confidence_count} high confidence
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Amount</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(analytics.amount_stats.average_amount)}
              </div>
              <p className="text-xs text-muted-foreground">
                Per transaction
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium">Min Confidence</label>
              <Input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={filters.min_confidence}
                onChange={(e) => setFilters({ ...filters, min_confidence: parseFloat(e.target.value) })}
                placeholder="0.0"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Has Amount</label>
              <Select
                value={filters.has_amount?.toString() || ''}
                onValueChange={(value) => setFilters({ ...filters, has_amount: value === 'true' ? true : value === 'false' ? false : undefined })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All</SelectItem>
                  <SelectItem value="true">Yes</SelectItem>
                  <SelectItem value="false">No</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Transaction Type</label>
              <Select
                value={filters.transaction_type}
                onValueChange={(value) => setFilters({ ...filters, transaction_type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All types</SelectItem>
                  <SelectItem value="income">Income</SelectItem>
                  <SelectItem value="expense">Expense</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium">Category</label>
              <Input
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                placeholder="Filter by category"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Extracted Data</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{item.filename}</div>
                          {item.company_name && (
                            <div className="text-sm text-muted-foreground">{item.company_name}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {item.amount ? (
                          <div className="font-medium">{formatCurrency(item.amount, item.currency)}</div>
                        ) : (
                          <span className="text-muted-foreground">No amount</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {item.transaction_type && (
                          <Badge variant={item.transaction_type === 'income' ? 'default' : 'secondary'}>
                            {item.transaction_type}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {item.category && (
                          <Badge variant="outline">{item.category}</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {item.transaction_date ? (
                          formatDate(item.transaction_date)
                        ) : (
                          <span className="text-muted-foreground">No date</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={item.confidence_score * 100} className="w-16" />
                          <span className="text-sm">{(item.confidence_score * 100).toFixed(0)}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-muted-foreground">
                  Showing {((page - 1) * limit) + 1} to {Math.min(page * limit, totalCount)} of {totalCount} results
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page * limit >= totalCount}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ExtractedData; 