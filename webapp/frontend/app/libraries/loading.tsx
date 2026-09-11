export default function LibrariesLoading() {
  return (
    <div className="container mx-auto p-6">
      <div className="animate-pulse">
        <div className="h-9 bg-slate-700 rounded w-48 mb-6" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <div className="h-7 bg-slate-700 rounded w-40 mb-4" />
            <div className="bg-slate-800 rounded-lg border border-slate-600 p-4 space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-20 bg-slate-700/50 rounded" />
              ))}
            </div>
          </div>
          <div>
            <div className="h-7 bg-slate-700 rounded w-40 mb-4" />
            <div className="bg-slate-800 rounded-lg border border-slate-600 p-4 h-64" />
          </div>
        </div>
      </div>
    </div>
  );
}
