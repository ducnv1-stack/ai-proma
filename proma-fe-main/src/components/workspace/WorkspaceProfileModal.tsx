'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Stack,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Avatar,
  Chip,
  InputAdornment,
  Divider
} from '@mui/material';
import {
  Close as CloseIcon,
  Business as BusinessIcon,
  Language as LanguageIcon,
  LocationOn as LocationIcon,
  Description as DescriptionIcon,
  Link as LinkIcon,
  Image as ImageIcon,
  AutoAwesome as SparklesIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { workspaceService } from '../../services/workspace.service';
import { UpdateWorkspaceProfileRequest, Workspace, WorkspaceProfile } from '@/libs/types';

interface WorkspaceProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  workspace: Workspace;
  onProfileUpdated: (workspace: Workspace) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function WorkspaceProfileModal({ 
  isOpen, 
  onClose, 
  workspace, 
  onProfileUpdated 
}: WorkspaceProfileModalProps) {
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [isLoadingWorkspace, setIsLoadingWorkspace] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Profile form fields
  const [brandName, setBrandName] = useState('');
  const [businessType, setBusinessType] = useState('');
  const [defaultLanguageCode, setDefaultLanguageCode] = useState('en');
  const [defaultLocationCode, setDefaultLocationCode] = useState('US');
  const [brandDescription, setBrandDescription] = useState('');
  const [brandProductsServices, setBrandProductsServices] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [brandLogoUrl, setBrandLogoUrl] = useState('');

  // URL scraping
  const [scrapUrl, setScrapUrl] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadWorkspaceDetails();
    }
  }, [isOpen, workspace.id]);

  const loadWorkspaceDetails = async () => {
    setIsLoadingWorkspace(true);
    setError('');
    
    try {
      // Fetch detailed workspace information
      const response = await workspaceService.getWorkspaceById(workspace.id);
      const detailedWorkspace = response;
      
      // Fill form fields directly from workspace data (flat structure)
      setBrandName(detailedWorkspace.brand_name || detailedWorkspace.name || '');
      setBusinessType(detailedWorkspace.business_type || '');
      setDefaultLanguageCode(detailedWorkspace.default_language_code || 'en');
      setDefaultLocationCode(detailedWorkspace.default_location_code || 'US');
      setBrandDescription(detailedWorkspace.brand_description || '');
      setBrandProductsServices(detailedWorkspace.brand_products_services || '');
      setWebsiteUrl(detailedWorkspace.website_url || '');
      setBrandLogoUrl(detailedWorkspace.brand_logo_url || '');
      
    } catch (error) {
      console.error('Failed to load workspace details:', error);
      setError('Failed to load workspace details');
      
      // Fallback to existing workspace data
      setBrandName(workspace.name || '');
      if (workspace.profile) {
        loadProfileData(workspace.profile);
      }
    } finally {
      setIsLoadingWorkspace(false);
    }
  };

  const loadProfileData = (profile: WorkspaceProfile) => {
    // Keep workspace name as brand name if profile doesn't have one
    setBrandName(profile.brand_name || workspace.name || '');
    setBusinessType(profile.business_type || '');
    setDefaultLanguageCode(profile.default_language_code || 'en');
    setDefaultLocationCode(profile.default_location_code || 'US');
    setBrandDescription(profile.brand_description || '');
    setBrandProductsServices(profile.brand_products_services || '');
    setWebsiteUrl(profile.website_url || '');
    setBrandLogoUrl(profile.brand_logo_url || '');
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const profileData: UpdateWorkspaceProfileRequest = {
        brand_name: brandName.trim() || undefined,
        business_type: businessType.trim() || undefined,
        default_language_code: defaultLanguageCode || undefined,
        default_location_code: defaultLocationCode || undefined,
        brand_description: brandDescription.trim() || undefined,
        brand_products_services: brandProductsServices.trim() || undefined,
        website_url: websiteUrl.trim() || undefined,
        brand_logo_url: brandLogoUrl.trim() || undefined
      };

      await workspaceService.updateWorkspaceProfile(workspace.id, profileData);
      
      // Update workspace object with new profile
      const updatedWorkspace = {
        ...workspace,
        profile: { ...workspace.profile, ...profileData }
      };
      
      onProfileUpdated(updatedWorkspace);
      setSuccess('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      setError(error instanceof Error ? error.message : 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleScrapWebsite = async () => {
    if (!scrapUrl.trim()) {
      setError('Please enter a website URL to scrape');
      return;
    }

    setIsScraping(true);
    setError('');
    setSuccess('');

    try {
      const response = await workspaceService.scrapCompanyProfile(workspace.id, {
        website_url: scrapUrl.trim()
      });

      // Load scraped data into form
      loadProfileData(response);
      setSuccess('Company profile scraped successfully!');
      setActiveTab(0); // Switch to profile tab
    } catch (error) {
      console.error('Failed to scrape website:', error);
      setError(error instanceof Error ? error.message : 'Failed to scrape website');
    } finally {
      setIsScraping(false);
    }
  };

  const businessTypes = [
    'Technology', 'E-commerce', 'Healthcare', 'Finance', 'Education', 
    'Real Estate', 'Food & Beverage', 'Fashion', 'Travel', 'Entertainment',
    'Automotive', 'Sports & Fitness', 'Beauty & Cosmetics', 'Home & Garden',
    'Professional Services', 'Non-profit', 'Other'
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'vi', name: 'Vietnamese' }
  ];

  const countries = [
    { code: 'US', name: 'United States' },
    { code: 'CA', name: 'Canada' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'DE', name: 'Germany' },
    { code: 'FR', name: 'France' },
    { code: 'ES', name: 'Spain' },
    { code: 'IT', name: 'Italy' },
    { code: 'AU', name: 'Australia' },
    { code: 'JP', name: 'Japan' },
    { code: 'VN', name: 'Vietnam' }
  ];

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          p: 0,
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ p: 0 }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          p: 3,
          pb: 1
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: 'primary.main'
              }}
            >
              {workspace.name.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                Workspace Profile
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Configure your brand and business information
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 3, pt: 1 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            aria-label="profile tabs"
          >
            <Tab 
              icon={<BusinessIcon />} 
              label="Profile" 
              iconPosition="start"
            />
            <Tab 
              icon={<SparklesIcon />} 
              label="Auto-Fill from Website" 
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
            {success}
          </Alert>
        )}

        {/* Profile Tab */}
        <TabPanel value={activeTab} index={0}>
          {isLoadingWorkspace ? (
            <Box 
              sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center', 
                justifyContent: 'center',
                py: 8
              }}
            >
              <CircularProgress size={48} sx={{ mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Loading workspace details...
              </Typography>
            </Box>
          ) : (
            <Box component="form" onSubmit={handleSaveProfile}>
              <Grid container spacing={3}>
                {/* Basic Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                    Basic Information
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Brand Name"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    placeholder="Your company or brand name"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <BusinessIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Business Type"
                    value={businessType}
                    onChange={(e) => setBusinessType(e.target.value)}
                    placeholder="Select or enter your business type"
                    select
                    SelectProps={{ native: true }}
                  >
                    <option value="">Select Business Type</option>
                    {businessTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </TextField>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Default Language"
                    value={defaultLanguageCode}
                    onChange={(e) => setDefaultLanguageCode(e.target.value)}
                    select
                    SelectProps={{ native: true }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LanguageIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  >
                    {languages.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </TextField>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Default Location"
                    value={defaultLocationCode}
                    onChange={(e) => setDefaultLocationCode(e.target.value)}
                    select
                    SelectProps={{ native: true }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LocationIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  >
                    {countries.map((country) => (
                      <option key={country.code} value={country.code}>
                        {country.name}
                      </option>
                    ))}
                  </TextField>
                </Grid>

                {/* Brand Details */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
                    Brand Details
                  </Typography>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Brand Description"
                    value={brandDescription}
                    onChange={(e) => setBrandDescription(e.target.value)}
                    multiline
                    rows={3}
                    placeholder="Describe your brand, mission, and values..."
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                          <DescriptionIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Products & Services"
                    value={brandProductsServices}
                    onChange={(e) => setBrandProductsServices(e.target.value)}
                    multiline
                    rows={3}
                    placeholder="List your main products and services..."
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Website URL"
                    value={websiteUrl}
                    onChange={(e) => setWebsiteUrl(e.target.value)}
                    placeholder="https://yourwebsite.com"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LinkIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Brand Logo URL"
                    value={brandLogoUrl}
                    onChange={(e) => setBrandLogoUrl(e.target.value)}
                    placeholder="https://yourwebsite.com/logo.png"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <ImageIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      disabled={isLoading}
                      startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
                      sx={{ borderRadius: 2 }}
                    >
                      {isLoading ? 'Saving...' : 'Save Profile'}
                    </Button>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={onClose}
                      disabled={isLoading}
                      sx={{ borderRadius: 2 }}
                    >
                      Cancel
                    </Button>
                  </Stack>
                </Grid>
              </Grid>
            </Box>
          )}
        </TabPanel>

        {/* Auto-Fill Tab */}
        <TabPanel value={activeTab} index={1}>
          <Stack spacing={3}>
            <Box sx={{ textAlign: 'center' }}>
              <SparklesIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" fontWeight="bold" sx={{ mb: 1 }}>
                Auto-Fill from Website
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Enter your website URL and we'll automatically extract your company information
              </Typography>
            </Box>

            <TextField
              fullWidth
              label="Website URL"
              value={scrapUrl}
              onChange={(e) => setScrapUrl(e.target.value)}
              placeholder="https://yourcompany.com"
              disabled={isScraping}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LinkIcon color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2
                }
              }}
            />

            <Button
              variant="contained"
              size="large"
              onClick={handleScrapWebsite}
              disabled={isScraping || !scrapUrl.trim()}
              startIcon={isScraping ? <CircularProgress size={20} /> : <RefreshIcon />}
              sx={{
                py: 1.5,
                borderRadius: 2,
                fontSize: '1rem',
                fontWeight: 600
              }}
            >
              {isScraping ? 'Extracting Information...' : 'Extract Company Info'}
            </Button>

            <Card variant="outlined" sx={{ p: 2, bgcolor: 'info.light', color: 'info.contrastText' }}>
              <Typography variant="body2" sx={{ textAlign: 'center' }}>
                💡 We'll automatically extract your company name, description, business type, and other details from your website
              </Typography>
            </Card>
          </Stack>
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
}
