// file: src/components/layout/AppLayout.tsx
'use client';

import { useState, ReactNode } from 'react';
import { Box, Toolbar, IconButton, Typography, AppBar, useTheme } from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import { useAppContext } from '@/contexts/AppContext';
import Sidebar from './sidebar/Sidebar'; 
import PageHeader from './PageHeader';

interface AppLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  headerActions?: React.ReactNode;
}

const DRAWER_WIDTH = 280; 

export default function AppLayout({ children, title, subtitle, headerActions }: AppLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isSidebarHidden, toggleSidebar } = useAppContext();
  const theme = useTheme();
  
  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'grey.100' }}>
      <Sidebar mobileOpen={mobileOpen} onDrawerToggle={handleDrawerToggle} />

      {/* Backdrop mờ khi sidebar mở */}
      {!isSidebarHidden && (
        <Box 
          onClick={toggleSidebar}
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'rgba(0, 0, 0, 0.1)',
            backdropFilter: 'blur(2px)',
            zIndex: theme.zIndex.drawer - 1, // Nằm dưới sidebar
            display: { xs: 'none', md: 'block' }
          }}
        />
      )}

      {/* Nút Toggle Sidebar cho Desktop */}
      <IconButton 
        onClick={toggleSidebar}
        sx={{
          position: 'fixed',
          top: 16,
          left: isSidebarHidden ? 16 : DRAWER_WIDTH - 24, 
          zIndex: theme.zIndex.drawer + 1,
          bgcolor: 'primary.main',
          color: 'white',
          display: { xs: 'none', md: 'inline-flex' },
          transition: theme.transitions.create('left', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          '&:hover': { bgcolor: 'primary.dark' }
        }}
      >
        <MenuIcon />
      </IconButton>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%', // Luôn chiếm 100% chiều rộng
          mt: { xs: 8, md: 0 },
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Mobile Header */}
        <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1, display: { md: 'none' } }}>
          <Toolbar>
            <IconButton color="inherit" edge="start" onClick={handleDrawerToggle} sx={{ mr: 2 }}>
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap>{title || 'Famarex'}</Typography>
          </Toolbar>
        </AppBar>

        <PageHeader title={title} subtitle={subtitle} headerActions={headerActions} />
        
        <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}