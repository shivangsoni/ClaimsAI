import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ArrowLeft, Search, FileText, CheckCircle2, Clock, XCircle, DollarSign, TrendingUp, AlertCircle, RotateCcw } from 'lucide-react';
import { claimsAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

function StatusBadge({ status }) {
  // Map the new 5-stage status system - only show actual claim status
  const statusConfig = {
    open: { label: "Open", style: "bg-blue-500 text-white", icon: <FileText className="h-3 w-3" /> },
    validation_complete: { label: "Validation Complete", style: "bg-orange-500 text-white", icon: <Clock className="h-3 w-3" /> },
    verified: { label: "Verified", style: "bg-purple-500 text-white", icon: <CheckCircle2 className="h-3 w-3" /> },
    approved: { label: "Approved", style: "bg-green-500 text-white", icon: <CheckCircle2 className="h-3 w-3" /> },
    denied: { label: "Denied", style: "bg-red-500 text-white", icon: <XCircle className="h-3 w-3" /> },
    need_more_info: { label: "Need More Info", style: "bg-yellow-500 text-white", icon: <AlertCircle className="h-3 w-3" /> },
    
    // Legacy status mapping for backward compatibility
    submitted: { label: "Open", style: "bg-blue-500 text-white", icon: <FileText className="h-3 w-3" /> },
    pending: { label: "Validation Complete", style: "bg-orange-500 text-white", icon: <Clock className="h-3 w-3" /> },
    "under-review": { label: "Verified", style: "bg-purple-500 text-white", icon: <CheckCircle2 className="h-3 w-3" /> },
    rejected: { label: "Denied", style: "bg-red-500 text-white", icon: <XCircle className="h-3 w-3" /> },
  };

  const config = statusConfig[status] || statusConfig.open;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.style}`}>
      {config.icon}
      {config.label}
    </span>
  );
}

export default function ClaimsDashboard() {
  const [claims, setClaims] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    validation_complete: 0,
    verified: 0,
    approved: 0,
    denied: 0,
    need_more_info: 0,
    // Legacy support
    pending: 0,
    rejected: 0
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { toast } = useToast();

  const loadClaimsData = useCallback(async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 10,
        ...(statusFilter !== 'all' && { status: statusFilter }),
        ...(searchTerm && { search: searchTerm })
      };
      
      const response = await claimsAPI.getAllClaims(params);
      setClaims(response.claims || []);
      setTotalPages(response.pagination?.pages || 1);
    } catch (error) {
      console.error('Error loading claims:', error);
      toast({
        title: "Error",
        description: "Failed to load claims data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter, searchTerm, toast]);

  const loadStatsData = useCallback(async () => {
    try {
      const response = await claimsAPI.getClaimsStats();
      const statusDist = response.status_distribution || {};
      setStats({
        total: response.total_claims || 0,
        open: statusDist.open || 0,
        validation_complete: statusDist.validation_complete || 0,
        verified: statusDist.verified || 0,
        approved: statusDist.approved || 0,
        denied: statusDist.denied || 0,
        need_more_info: statusDist.need_more_info || 0,
        // Legacy support
        pending: statusDist.pending || statusDist.submitted || 0,
        rejected: statusDist.rejected || 0
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }, []);

  // Load claims data from backend
  useEffect(() => {
    loadClaimsData();
    loadStatsData();
  }, [loadClaimsData, loadStatsData]);

  // Refresh data when window regains focus (user comes back from new claim page)
  useEffect(() => {
    const handleFocus = () => {
      loadClaimsData();
      loadStatsData();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [loadClaimsData, loadStatsData]);

  // Filter and sort claims - backend now handles filtering, so this is just for local display
  const filteredClaims = claims;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm">Back to Home</span>
          </Link>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => {
                loadClaimsData();
                loadStatsData();
              }}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RotateCcw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Link to="/claims/new">
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90">+ New Claim</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Title Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Claims Dashboard</h1>
          <p className="text-muted-foreground">Monitor and manage all medical claims in one place</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex flex-col gap-2">
                <p className="text-sm text-muted-foreground">Total Claims</p>
                <p className="text-4xl font-bold text-foreground">{stats.total}</p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                  <FileText className="h-4 w-4" />
                  <span>All submissions</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex flex-col gap-2">
                <p className="text-sm text-muted-foreground">Open Claims</p>
                <p className="text-4xl font-bold text-blue-600">{stats.open || 0}</p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                  <FileText className="h-4 w-4" />
                  <span>New submissions</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex flex-col gap-2">
                <p className="text-sm text-muted-foreground">In Progress</p>
                <p className="text-4xl font-bold text-orange-600">
                  {(stats.validation_complete || 0) + (stats.verified || 0) + (stats.need_more_info || 0)}
                </p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                  <Clock className="h-4 w-4" />
                  <span>Under review</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardContent className="p-6">
              <div className="flex flex-col gap-2">
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-4xl font-bold text-green-600">
                  {(stats.approved || 0) + (stats.denied || 0)}
                </p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Final decisions</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter */}
        <Card className="border-border mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Search by patient name, claim ID, or patient ID..." 
                  className="pl-10" 
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full md:w-[200px]">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="validation_complete">Validation Complete</SelectItem>
                  <SelectItem value="verified">Verified</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="denied">Denied</SelectItem>
                  <SelectItem value="need_more_info">Need More Info</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Claims List */}
        <div className="space-y-4">
          {loading ? (
            <Card className="border-border">
              <CardContent className="p-6 text-center">
                <p className="text-muted-foreground">Loading claims...</p>
              </CardContent>
            </Card>
          ) : (
            filteredClaims.map((claim) => (
              <Card key={claim.claim_id || claim.id} className="border-border hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-foreground">{claim.patient_name}</h3>
                        <StatusBadge status={claim.status} />
                        {claim.is_valid === false && (
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <AlertCircle className="h-3 w-3" />
                            {claim.total_issues} Issues
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-4">
                        Claim ID: {claim.claim_id} • Patient ID: {claim.patient_id}
                      </p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Type</p>
                          <p className="text-sm font-medium text-foreground">{claim.service_type || 'Medical'}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Provider</p>
                          <p className="text-sm font-medium text-foreground">{claim.provider_name}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Amount</p>
                          <p className="text-sm font-medium text-primary">
                            <DollarSign className="inline h-3 w-3" />
                            {parseFloat(claim.amount_billed || 0).toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Service Date</p>
                          <p className="text-sm font-medium text-foreground">
                            {new Date(claim.service_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      {claim.confidence && (
                        <div className="mt-3 flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">
                            AI Confidence: {claim.confidence}% | Overall Score: {claim.overall_score || 'N/A'}
                          </span>
                        </div>
                      )}
                    </div>
                    <div>
                      <Link to={`/claims/${claim.claim_id || claim.id}`}>
                        <Button variant="outline">View Details</Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {filteredClaims.length === 0 && (
          <Card className="border-border">
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground">No claims found matching your search criteria.</p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}