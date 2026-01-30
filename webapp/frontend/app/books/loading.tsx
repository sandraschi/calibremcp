export default function BooksLoading() {
  return (
    <div className="container mx-auto p-6">
      <div className="animate-pulse">
        <div className="h-9 bg-slate-700 rounded w-32 mb-6" />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="bg-slate-800 rounded-lg border border-slate-600 overflow-hidden">
              <div className="aspect-[2/3] bg-slate-700" />
              <div className="p-2 space-y-2">
                <div className="h-4 bg-slate-700 rounded w-full" />
                <div className="h-3 bg-slate-700/70 rounded w-2/3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
