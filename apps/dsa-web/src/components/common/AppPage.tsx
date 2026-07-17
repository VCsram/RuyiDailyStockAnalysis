import type React from 'react';
import { cn } from '../../utils/cn';

interface AppPageProps {
  children: React.ReactNode;
  className?: string;
}

export const AppPage: React.FC<AppPageProps> = ({ children, className = '' }) => {
  return (
    <main className={cn('min-h-full w-full max-w-none px-3 pb-8 pt-4 sm:px-4 md:px-5 lg:px-6 xl:px-8', className)}>
      {children}
    </main>
  );
};
