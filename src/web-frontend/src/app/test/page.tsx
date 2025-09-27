export default function TestPage() {
  return (
    <div className="min-h-screen bg-blue-50 p-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        ✅ Next.js is Working!
      </h1>
      <p className="text-lg text-gray-600 mb-4">
        This is a test page to verify that Next.js routing is functioning correctly.
      </p>
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-xl font-semibold mb-3">System Status:</h2>
        <ul className="space-y-2">
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✅</span>
            Next.js App Router
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✅</span>
            Tailwind CSS
          </li>
          <li className="flex items-center">
            <span className="text-green-500 mr-2">✅</span>
            TypeScript
          </li>
        </ul>
      </div>
    </div>
  );
}