import type React from 'react';
import { useEffect, useState } from 'react';
import { Menu } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import { Drawer } from '../common/Drawer';
import { BrandMark } from '../brand/BrandMark';
import { SidebarNav } from './SidebarNav';
import { cn } from '../../utils/cn';
import { ThemeToggle } from '../theme/ThemeToggle';
import { UiLanguageToggle } from '../i18n/UiLanguageToggle';
import { useUiLanguage } from '../../contexts/UiLanguageContext';
import { BRAND_ZH } from '../../brand';

type ShellProps = {
  children?: React.ReactNode;
};

const SIDEBAR_COLLAPSED_KEY = 'dsa.shell.sidebarCollapsed';

export const Shell: React.FC<ShellProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const { t } = useUiLanguage();

  useEffect(() => {
    try {
      const raw = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
      if (raw === '1') {
        setCollapsed(true);
      }
    } catch {
      // ignore storage failures
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed ? '1' : '0');
    } catch {
      // ignore storage failures
    }
  }, [collapsed]);

  useEffect(() => {
    if (!mobileOpen) {
      return undefined;
    }

    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [mobileOpen]);

  return (
    <div className="min-h-screen w-full bg-background text-foreground">
      {/* Mobile top bar: menu + brand */}
      <div className="fixed inset-x-0 top-0 z-40 flex h-12 items-center justify-between gap-2 border-b border-border/60 bg-background/90 px-3 backdrop-blur-md lg:hidden">
        <div className="flex min-w-0 items-center gap-2">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-border/70 bg-card/85 text-secondary-text transition-colors hover:bg-hover hover:text-foreground"
            aria-label={t('layout.openNav')}
          >
            <Menu className="h-5 w-5" />
          </button>
          <BrandMark layout="mark" size="sm" showWordmark alt={BRAND_ZH} className="min-w-0" />
        </div>
        <div className="flex shrink-0 items-center gap-1.5">
          <UiLanguageToggle />
          <ThemeToggle />
        </div>
      </div>

      <div className="flex min-h-screen w-full">
        <aside
          className={cn(
            'sticky top-0 z-40 hidden h-screen shrink-0 flex-col overflow-visible border-r border-[var(--shell-sidebar-border)] bg-card/80 p-3 backdrop-blur-sm transition-[width] duration-200 lg:flex',
            collapsed ? 'w-[76px]' : 'w-[248px]'
          )}
          aria-label={t('layout.desktopSidebar')}
        >
          <SidebarNav
            collapsed={collapsed}
            variant={collapsed ? 'rail' : 'default'}
            onNavigate={() => setMobileOpen(false)}
            onToggleCollapse={() => setCollapsed((value) => !value)}
          />
        </aside>

        <main className="min-h-screen min-w-0 flex-1 pt-12 lg:pt-0 touch-pan-y">
          {children ?? <Outlet />}
        </main>
      </div>

      <Drawer
        isOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        title={t('layout.navMenu')}
        width="max-w-xs"
        zIndex={90}
        side="left"
      >
        <SidebarNav onNavigate={() => setMobileOpen(false)} />
      </Drawer>
    </div>
  );
};
