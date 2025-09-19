// file: src/contexts/AppContext.tsx
'use client';

import { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { User } from '@/libs/types';
import { authService } from '@/services/auth.service';

interface AppContextType {
  currentUser: User | null;
  isSidebarHidden: boolean;
  toggleSidebar: () => void;
  logout: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isSidebarHidden, setSidebarHidden] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Lấy trạng thái sidebar từ localStorage
    const savedState = localStorage.getItem('famarex_sidebar_hidden');
    if (savedState) {
      setSidebarHidden(JSON.parse(savedState));
    }

    // Lấy thông tin user
    const fetchUser = async () => {
      try {
        // Ưu tiên lấy từ cache trước
        const cachedUser = localStorage.getItem('famarex_user');
        if (cachedUser) setCurrentUser(JSON.parse(cachedUser));
        
        // Sau đó gọi API để lấy dữ liệu mới nhất (nếu cần)
        // const freshUser = await userService.getMyProfile();
        // setCurrentUser(freshUser);
        // localStorage.setItem('famarex_user', JSON.stringify(freshUser));

      } catch (error) {
        console.error('Session invalid, redirecting to login.', error);
        router.push('/login');
      }
    };

    if (authService.isAuthenticated()) {
      fetchUser();
    }
  }, [router]);

  const toggleSidebar = () => {
    setSidebarHidden(prevState => {
      const newState = !prevState;
      localStorage.setItem('famarex_sidebar_hidden', JSON.stringify(newState));
      return newState;
    });
  };

  const logout = async () => {
    await authService.logout();
    // authService.logout đã xử lý redirect
  };

  const value = { currentUser, isSidebarHidden, toggleSidebar, logout };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Custom hook để dễ dàng sử dụng context
export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}