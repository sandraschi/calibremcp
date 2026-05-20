'use client';

import { useState, useRef, useEffect } from 'react';
import { ExternalLink, Code2, BookOpen, RefreshCw } from 'lucide-react';

type DocsView = 'swagger' | 'redoc';

// Dark theme CSS injected into the Swagger iframe via postMessage / srcdoc trick.
// We load /docs proxied through Next.js, then override the default white Swagger theme.
const SWAGGER_DARK_CSS = `
  body { background: #09090b !important; }
  .swagger-ui { background: #09090b !important; color: #e4e4e7 !important; }
  .swagger-ui .topbar { background: #18181b !important; border-bottom: 1px solid #3f3f46 !important; }
  .swagger-ui .topbar .download-url-wrapper .select-label select { background: #27272a !important; color: #e4e4e7 !important; border-color: #3f3f46 !important; }
  .swagger-ui .info .title { color: #f59e0b !important; }
  .swagger-ui .info { background: #09090b !important; }
  .swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info table { color: #a1a1aa !important; }
  .swagger-ui .scheme-container { background: #18181b !important; border-color: #3f3f46 !important; box-shadow: none !important; }
  .swagger-ui section.models { background: #18181b !important; border-color: #3f3f46 !important; }
  .swagger-ui section.models.is-open h4 { background: #27272a !important; border-color: #3f3f46 !important; color: #e4e4e7 !important; }
  .swagger-ui .model-box { background: #09090b !important; }
  .swagger-ui .model { color: #a1a1aa !important; }
  .swagger-ui .opblock-tag { border-color: #3f3f46 !important; color: #e4e4e7 !important; }
  .swagger-ui .opblock-tag:hover { background: #27272a !important; }
  .swagger-ui .opblock { border-color: #3f3f46 !important; background: #18181b !important; }
  .swagger-ui .opblock .opblock-summary { border-color: #3f3f46 !important; }
  .swagger-ui .opblock .opblock-summary-path { color: #e4e4e7 !important; }
  .swagger-ui .opblock .opblock-summary-description { color: #a1a1aa !important; }
  .swagger-ui .opblock.opblock-get { border-color: #3b82f6 !important; background: rgba(59,130,246,0.08) !important; }
  .swagger-ui .opblock.opblock-get .opblock-summary { border-color: #3b82f6 !important; background: rgba(59,130,246,0.05) !important; }
  .swagger-ui .opblock.opblock-post { border-color: #22c55e !important; background: rgba(34,197,94,0.08) !important; }
  .swagger-ui .opblock.opblock-post .opblock-summary { border-color: #22c55e !important; background: rgba(34,197,94,0.05) !important; }
  .swagger-ui .opblock.opblock-put { border-color: #f59e0b !important; background: rgba(245,158,11,0.08) !important; }
  .swagger-ui .opblock.opblock-delete { border-color: #ef4444 !important; background: rgba(239,68,68,0.08) !important; }
  .swagger-ui .opblock .opblock-body { background: #09090b !important; }
  .swagger-ui .opblock-description-wrapper p, .swagger-ui .opblock-external-docs-wrapper p { color: #a1a1aa !important; }
  .swagger-ui table thead tr td, .swagger-ui table thead tr th { border-color: #3f3f46 !important; color: #a1a1aa !important; background: #18181b !important; }
  .swagger-ui .parameters-col_description input[type=text], .swagger-ui .parameters-col_description select, .swagger-ui .parameters-col_description textarea { background: #27272a !important; border-color: #3f3f46 !important; color: #e4e4e7 !important; }
  .swagger-ui .btn { background: #27272a !important; color: #e4e4e7 !important; border-color: #3f3f46 !important; }
  .swagger-ui .btn.execute { background: #f59e0b !important; color: #09090b !important; border-color: #f59e0b !important; font-weight: 600 !important; }
  .swagger-ui .btn.execute:hover { background: #fbbf24 !important; }
  .swagger-ui .btn.authorize { background: #22c55e !important; color: #09090b !important; border-color: #22c55e !important; }
  .swagger-ui .responses-wrapper { background: #09090b !important; }
  .swagger-ui .response-col_status { color: #a1a1aa !important; }
  .swagger-ui .microlight { background: #18181b !important; color: #e4e4e7 !important; }
  .swagger-ui .highlight-code { background: #18181b !important; }
  .swagger-ui .markdown p, .swagger-ui .markdown li { color: #a1a1aa !important; }
  .swagger-ui select { background: #27272a !important; color: #e4e4e7 !important; border-color: #3f3f46 !important; }
  .swagger-ui input[type=text], .swagger-ui input[type=password], .swagger-ui textarea { background: #27272a !important; color: #e4e4e7 !important; border-color: #3f3f46 !important; }
  .swagger-ui .dialog-ux .modal-ux { background: #18181b !important; border-color: #3f3f46 !important; }
  .swagger-ui .dialog-ux .modal-ux-header { background: #27272a !important; border-color: #3f3f46 !important; }
  .swagger-ui .dialog-ux .modal-ux-header h3 { color: #e4e4e7 !important; }
  .swagger-ui .dialog-ux .modal-ux-content p, .swagger-ui .dialog-ux .modal-ux-content h4 { color: #a1a1aa !important; }
  .swagger-ui .filter .operation-filter-input { background: #27272a !important; border-color: #3f3f46 !important; color: #e4e4e7 !important; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #18181b; }
  ::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 3px; }
`;

export default function ApiDocsPage() {
  const [view, setView] = useState<DocsView>('swagger');
  const [loading, setLoading] = useState(true);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Inject dark CSS into the iframe once it loads
  const handleIframeLoad = () => {
    setLoading(false);
    try {
      const iframe = iframeRef.current;
      if (!iframe?.contentDocument) return;
      const doc = iframe.contentDocument;
      // Remove existing style overrides if any
      const existing = doc.getElementById('fleet-dark-override');
      if (existing) existing.remove();
      const style = doc.createElement('style');
      style.id = 'fleet-dark-override';
      style.textContent = SWAGGER_DARK_CSS;
      doc.head.appendChild(style);
    } catch {
      // Cross-origin fallback — if proxy isn't working, the iframe loads direct
      // and we can't inject CSS. The direct link still works.
    }
  };

  const src = view === 'swagger' ? '/docs' : '/redoc';
  const directSrc = view === 'swagger'
    ? 'http://localhost:10720/docs'
    : 'http://localhost:10720/redoc';

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* Header bar */}
      <div className="flex items-center gap-4 px-5 py-3 border-b border-zinc-800 shrink-0">
        <Code2 size={18} className="text-amber-400" />
        <h1 className="text-sm font-semibold text-zinc-100">API Docs</h1>

        {/* View toggle */}
        <div className="flex items-center bg-zinc-900 border border-zinc-700 rounded-lg p-0.5 ml-2">
          <button
            onClick={() => { setView('swagger'); setLoading(true); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              view === 'swagger'
                ? 'bg-amber-500 text-zinc-950'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Code2 size={12} />
            Swagger UI
          </button>
          <button
            onClick={() => { setView('redoc'); setLoading(true); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              view === 'redoc'
                ? 'bg-amber-500 text-zinc-950'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <BookOpen size={12} />
            ReDoc
          </button>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          {/* Reload */}
          <button
            onClick={() => { setLoading(true); if (iframeRef.current) { iframeRef.current.src = src; } }}
            className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-2 py-1.5 rounded-md hover:bg-zinc-800"
          >
            <RefreshCw size={13} />
            Reload
          </button>
          {/* Open in new tab — direct to backend, no proxy needed */}
          <a
            href={directSrc}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-amber-400 hover:text-amber-300 transition-colors px-2 py-1.5 rounded-md hover:bg-zinc-800"
          >
            <ExternalLink size={13} />
            Open in browser
          </a>
        </div>
      </div>

      {/* Endpoint quick-ref strip */}
      <div className="flex items-center gap-2 px-5 py-2 border-b border-zinc-800 shrink-0 overflow-x-auto">
        <span className="text-xs text-zinc-600 shrink-0">Backend:</span>
        <code className="text-xs text-amber-400 font-mono shrink-0">http://localhost:10720</code>
        <span className="text-zinc-700 mx-1">·</span>
        {[
          ['GET', '/api/books', 'blue'],
          ['GET', '/api/search', 'blue'],
          ['POST', '/api/rag', 'green'],
          ['GET', '/api/libraries', 'blue'],
          ['GET', '/api/authors', 'blue'],
          ['GET', '/api/series', 'blue'],
        ].map(([method, path, color]) => (
          <a
            key={path}
            href={directSrc}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 shrink-0 hover:opacity-80 transition-opacity"
          >
            <span className={`text-xs font-mono font-bold ${color === 'green' ? 'text-green-400' : 'text-blue-400'}`}>
              {method}
            </span>
            <span className="text-xs font-mono text-zinc-500">{path}</span>
          </a>
        ))}
        <span className="text-zinc-700 mx-1">·</span>
        <span className="text-xs text-zinc-600 shrink-0 italic">+{20 - 6} more — see Swagger</span>
      </div>

      {/* Iframe */}
      <div className="flex-1 relative min-h-0">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-950 z-10">
            <div className="flex flex-col items-center gap-3">
              <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-zinc-500">Loading {view === 'swagger' ? 'Swagger UI' : 'ReDoc'}…</span>
            </div>
          </div>
        )}
        <iframe
          ref={iframeRef}
          src={src}
          onLoad={handleIframeLoad}
          className="w-full h-full border-0"
          title={view === 'swagger' ? 'Swagger UI' : 'ReDoc'}
        />
      </div>
    </div>
  );
}
