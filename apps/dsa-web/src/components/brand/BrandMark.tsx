import { useTheme } from 'next-themes';
import type React from 'react';
import { BRAND_EN, BRAND_ZH } from '../../brand';
import { cn } from '../../utils/cn';

export type BrandMarkLayout = 'mark' | 'horizontal';
export type BrandMarkSize = 'sm' | 'md' | 'lg' | 'xl';

export type BrandMarkProps = {
  /** mark = 仅图标；horizontal = 主题自适应横版 Logo */
  layout?: BrandMarkLayout;
  size?: BrandMarkSize;
  className?: string;
  /** 侧栏展开时在图标旁显示中文名（不依赖横版 SVG） */
  showWordmark?: boolean;
  /** 强制浅/深色横版资源；默认跟随主题 */
  forceTheme?: 'light' | 'dark';
  alt?: string;
};

const SIZE_PX: Record<BrandMarkSize, number> = {
  sm: 28,
  md: 40,
  lg: 64,
  xl: 80,
};

const ICON_SRC = '/brand/icon.svg';
const LOGO_LIGHT_SRC = '/brand/logo-light.svg';
const LOGO_DARK_SRC = '/brand/logo-dark.svg';

export const BrandMark: React.FC<BrandMarkProps> = ({
  layout = 'mark',
  size = 'md',
  className,
  showWordmark = false,
  forceTheme,
  alt,
}) => {
  const { resolvedTheme } = useTheme();
  const theme = forceTheme ?? (resolvedTheme === 'light' ? 'light' : 'dark');
  const px = SIZE_PX[size];
  const label = alt ?? `${BRAND_ZH} ${BRAND_EN}`;

  if (layout === 'horizontal') {
    const src = theme === 'light' ? LOGO_LIGHT_SRC : LOGO_DARK_SRC;
    const height = px;
    const width = Math.round(height * (720 / 160));
    return (
      <img
        src={src}
        alt={label}
        width={width}
        height={height}
        className={cn('select-none object-contain object-left', className)}
        draggable={false}
      />
    );
  }

  return (
    <span className={cn('inline-flex items-center gap-2', className)}>
      <img
        src={ICON_SRC}
        alt={showWordmark ? '' : label}
        width={px}
        height={px}
        className="select-none object-contain"
        draggable={false}
      />
      {showWordmark ? (
        <span className="min-w-0 truncate text-sm font-semibold leading-none text-foreground">{BRAND_ZH}</span>
      ) : null}
    </span>
  );
};

// Shared path constants live beside the component for consumers/tests.
// eslint-disable-next-line react-refresh/only-export-components -- asset path map, not a component
export const brandAssetPaths = {
  icon: ICON_SRC,
  logoLight: LOGO_LIGHT_SRC,
  logoDark: LOGO_DARK_SRC,
  faviconSvg: '/favicon.svg',
  faviconIco: '/favicon.ico',
} as const;
