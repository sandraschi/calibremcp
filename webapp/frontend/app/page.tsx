export default function Home() {
  return (
    <main className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Calibre Webapp</h1>
      <p className="text-lg mb-4">Modern web interface for your Calibre library.</p>
      <div className="space-x-4">
        <a href="/books" className="text-blue-600 hover:underline">
          Browse
        </a>
        <a href="/search" className="text-blue-600 hover:underline">
          Search
        </a>
        <a href="/libraries" className="text-blue-600 hover:underline">
          Libraries
        </a>
      </div>
    </main>
  );
}
