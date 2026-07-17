import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { BrandMark, brandAssetPaths } from '../BrandMark';

vi.mock('next-themes', () => ({
  useTheme: () => ({ resolvedTheme: 'dark', theme: 'dark' }),
}));

describe('BrandMark', () => {
  it('renders icon mark by default', () => {
    render(<BrandMark />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', brandAssetPaths.icon);
    expect(img.getAttribute('alt') || '').toContain('如意金股');
  });

  it('renders horizontal dark logo under dark theme', () => {
    render(<BrandMark layout="horizontal" size="lg" />);
    expect(screen.getByRole('img')).toHaveAttribute('src', brandAssetPaths.logoDark);
  });

  it('renders horizontal light logo when forceTheme=light', () => {
    render(<BrandMark layout="horizontal" forceTheme="light" />);
    expect(screen.getByRole('img')).toHaveAttribute('src', brandAssetPaths.logoLight);
  });

  it('shows Chinese wordmark beside icon when requested', () => {
    render(<BrandMark showWordmark />);
    expect(screen.getByText('如意金股')).toBeInTheDocument();
  });
});
