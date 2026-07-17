import React, { useEffect, useState } from 'react';
import {
  Activity,
  BarChart3,
  Bell,
  BriefcaseBusiness,
  Gauge,
  Home,
  LogOut,
  MessageSquareQuote,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Settings2,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { ALPHASIFT_CONFIG_CHANGED_EVENT, SYSTEM_CONFIG_CHANGED_EVENT, alphasiftApi } from '../../api/alphasift';
import { useAuth } from '../../contexts/AuthContext';
import { useAgentChatStore } from '../../stores/agentChatStore';
import { useUiLanguage } from '../../contexts/UiLanguageContext';
import type { UiTextKey } from '../../i18n/uiText';
import { cn } from '../../utils/cn';
import { ConfirmDialog } from '../common/ConfirmDialog';
import { StatusDot } from '../common/StatusDot';
import { BrandMark } from '../brand/BrandMark';
import { UiLanguageToggle } from '../i18n/UiLanguageToggle';
import { ThemeToggle } from '../theme/ThemeToggle';
import { BRAND_ZH } from '../../brand';

type SidebarNavProps = {
  collapsed?: boolean;
  onNavigate?: () => void;
  variant?: 'default' | 'rail';
  onToggleCollapse?: () => void;
};

type NavItem = {
  key: string;
  labelKey: UiTextKey;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  exact?: boolean;
  badge?: 'completion';
};

const NAV_ITEMS: NavItem[] = [
  { key: 'home', labelKey: 'layout.nav.home', to: '/', icon: Home, exact: true },
  { key: 'chat', labelKey: 'layout.nav.chat', to: '/chat', icon: MessageSquareQuote, badge: 'completion' },
  { key: 'screening', labelKey: 'layout.nav.screening', to: '/screening', icon: Search },
  { key: 'portfolio', labelKey: 'layout.nav.portfolio', to: '/portfolio', icon: BriefcaseBusiness },
  { key: 'decision-signals', labelKey: 'layout.nav.decisionSignals', to: '/decision-signals', icon: Activity },
  { key: 'backtest', labelKey: 'layout.nav.backtest', to: '/backtest', icon: BarChart3 },
  { key: 'alerts', labelKey: 'layout.nav.alerts', to: '/alerts', icon: Bell },
  { key: 'usage', labelKey: 'layout.nav.usage', to: '/usage', icon: Gauge },
  { key: 'settings', labelKey: 'layout.nav.settings', to: '/settings', icon: Settings2 },
];

export const SidebarNav: React.FC<SidebarNavProps> = ({
  collapsed = false,
  onNavigate,
  variant = 'default',
  onToggleCollapse,
}) => {
  const { authEnabled, logout } = useAuth();
  const { t } = useUiLanguage();
  const completionBadge = useAgentChatStore((state) => state.completionBadge);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showAlphaSiftNav, setShowAlphaSiftNav] = useState(false);

  useEffect(() => {
    let active = true;

    const refreshAlphaSiftStatus = async () => {
      try {
        const status = await alphasiftApi.getStatus();
        if (active) {
          setShowAlphaSiftNav(status.enabled);
        }
      } catch {
        if (active) {
          setShowAlphaSiftNav(false);
        }
      }
    };

    void refreshAlphaSiftStatus();
    window.addEventListener(ALPHASIFT_CONFIG_CHANGED_EVENT, refreshAlphaSiftStatus);
    window.addEventListener(SYSTEM_CONFIG_CHANGED_EVENT, refreshAlphaSiftStatus);

    return () => {
      active = false;
      window.removeEventListener(ALPHASIFT_CONFIG_CHANGED_EVENT, refreshAlphaSiftStatus);
      window.removeEventListener(SYSTEM_CONFIG_CHANGED_EVENT, refreshAlphaSiftStatus);
    };
  }, []);

  const navItems = showAlphaSiftNav ? NAV_ITEMS : NAV_ITEMS.filter((item) => item.key !== 'screening');
  const isRail = variant === 'rail';
  const itemBaseClass = cn(
    'group relative flex h-[var(--nav-item-height)] w-full items-center overflow-hidden rounded-2xl border border-transparent text-sm leading-none text-secondary-text transition-all',
    isRail
      ? 'justify-center gap-2.5 px-2'
      : collapsed
        ? 'justify-center px-0'
        : 'gap-3 px-[var(--nav-item-padding-x)]'
  );
  const itemInteractiveClass = cn(
    itemBaseClass,
    'hover:bg-[var(--nav-hover-bg)] hover:text-foreground'
  );
  const itemActiveClass = 'border-[var(--nav-active-border)] bg-[var(--nav-active-bg)] font-medium text-[hsl(var(--primary))]';
  const itemIconClass = cn(isRail ? 'h-[18px] w-[18px]' : 'h-5 w-5', 'shrink-0');
  const itemLabelClass = cn('truncate', isRail ? 'text-center' : '');

  return (
    <div className="flex h-full min-h-0 w-full flex-col">
      <div
        className={cn(
          'mb-4 flex shrink-0 items-center gap-1',
          isRail || collapsed ? 'justify-center pt-1' : 'justify-between px-0.5 pt-0.5'
        )}
      >
        {isRail || collapsed ? (
          <button
            type="button"
            onClick={onToggleCollapse}
            className={cn(
              'inline-flex items-center justify-center rounded-2xl transition-colors',
              onToggleCollapse ? 'hover:bg-[var(--nav-hover-bg)]' : 'pointer-events-none'
            )}
            aria-label={onToggleCollapse ? t('layout.expandSidebar') : BRAND_ZH}
            title={BRAND_ZH}
          >
            <BrandMark
              layout="mark"
              size="md"
              className="shadow-[0_12px_28px_var(--nav-brand-shadow)]"
              alt={BRAND_ZH}
            />
          </button>
        ) : (
          <>
            <BrandMark
              layout="horizontal"
              size="md"
              className="h-10 w-auto max-w-[188px] object-left"
              alt={BRAND_ZH}
            />
            {onToggleCollapse ? (
              <button
                type="button"
                onClick={onToggleCollapse}
                className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-transparent text-secondary-text transition-colors hover:bg-[var(--nav-hover-bg)] hover:text-foreground"
                aria-label={t('layout.collapseSidebar')}
              >
                <PanelLeftClose className="h-4 w-4" />
              </button>
            ) : null}
          </>
        )}
      </div>

      <nav className={cn('flex min-h-0 flex-1 flex-col gap-1.5 overflow-y-auto', isRail ? '' : '')} aria-label={t('layout.mainNav')}>
        {navItems.map(({ key, labelKey, to, icon: Icon, exact, badge }) => {
          const label = t(labelKey);
          return (
          <NavLink
            key={key}
            to={to}
            end={exact}
            onClick={onNavigate}
            aria-label={label}
            className={({ isActive }) =>
              cn(
                itemInteractiveClass,
                isActive ? itemActiveClass : ''
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={cn(itemIconClass, isActive ? 'text-[var(--nav-icon-active)]' : 'text-current')} />
                {!collapsed ? <span className={itemLabelClass}>{label}</span> : null}
                {badge === 'completion' && completionBadge ? (
                  <StatusDot
                    tone="info"
                    data-testid="chat-completion-badge"
                    className={cn(
                      'absolute right-3 border-2 border-background shadow-[0_0_10px_var(--nav-indicator-shadow)]',
                      collapsed ? 'right-2 top-2' : ''
                    )}
                    aria-label={t('layout.newChatMessage')}
                  />
                ) : null}
              </>
            )}
          </NavLink>
        );
        })}

        <ThemeToggle
          variant={isRail ? 'rail' : 'nav'}
          collapsed={collapsed}
          wrapperClassName="w-full"
          triggerClassName={itemInteractiveClass}
          triggerActiveClassName={itemActiveClass}
          iconClassName={itemIconClass}
          labelClassName={itemLabelClass}
        />
        <UiLanguageToggle
          variant={isRail ? 'rail' : 'nav'}
          collapsed={collapsed}
          wrapperClassName="w-full"
          triggerClassName={itemInteractiveClass}
          triggerActiveClassName={itemActiveClass}
          iconClassName={itemIconClass}
          labelClassName={itemLabelClass}
        />
      </nav>

      <div className="mt-auto flex shrink-0 flex-col gap-1.5 pt-3">
        {authEnabled ? (
          <button
            type="button"
            onClick={() => setShowLogoutConfirm(true)}
            aria-label={t('layout.logout')}
            className={itemInteractiveClass}
          >
            <LogOut className={itemIconClass} />
            {!collapsed && !isRail ? <span className={itemLabelClass}>{t('layout.logout')}</span> : null}
          </button>
        ) : null}

        {(isRail || collapsed) && onToggleCollapse ? (
          <button
            type="button"
            onClick={onToggleCollapse}
            className={itemInteractiveClass}
            aria-label={t('layout.expandSidebar')}
          >
            <PanelLeftOpen className={itemIconClass} />
          </button>
        ) : null}
      </div>

      <ConfirmDialog
        isOpen={showLogoutConfirm}
        title={t('layout.logoutTitle')}
        message={t('layout.logoutMessage')}
        confirmText={t('layout.logoutConfirm')}
        cancelText={t('common.cancel')}
        isDanger
        onConfirm={() => {
          setShowLogoutConfirm(false);
          onNavigate?.();
          void logout();
        }}
        onCancel={() => setShowLogoutConfirm(false)}
      />
    </div>
  );
};
