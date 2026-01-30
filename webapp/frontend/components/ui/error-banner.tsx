'use client';

interface ErrorBannerProps {
  title: string;
  message: string;
  hint?: string;
}

export function ErrorBanner({ title, message, hint }: ErrorBannerProps) {
  return (
    <div className="rounded-lg border border-amber-500/50 bg-amber-500/10 p-6 text-slate-200">
      <p className="font-medium">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{message}</p>
      {hint && (
        <p className="mt-2 text-sm text-slate-500">{hint}</p>
      )}
    </div>
  );
}
