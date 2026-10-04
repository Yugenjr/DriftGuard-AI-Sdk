export default function Footer() {
  return (
    <footer className="bg-[#111] text-white py-16 px-6 lg:px-12 border-t-4 border-black">
      <div className="max-w-[2000px] xl:px-24 mx-auto grid grid-cols-1 md:grid-cols-4 gap-10">
        <div className="md:col-span-1">
          <h2 className="text-3xl font-black tracking-tighter mb-3 text-[#a3e635]">DRIFTGUARD</h2>
          <p className="font-mono text-xs font-bold text-gray-500">Production intelligence for production models.</p>
        </div>
        
        <div>
          <h3 className="font-black mb-4 uppercase tracking-widest text-[10px] text-gray-600">Product</h3>
          <ul className="space-y-3 font-mono font-bold text-xs">
            <li><a href="#how-it-works" className="hover:text-[#a3e635] hover:underline underline-offset-4">How it works</a></li>
            <li><a href="#sdk" className="hover:text-[#a3e635] hover:underline underline-offset-4">SDK</a></li>
            <li><a href="#architecture" className="hover:text-[#a3e635] hover:underline underline-offset-4">Architecture</a></li>
            <li><a href="#" className="hover:text-[#a3e635] hover:underline underline-offset-4">Dashboard</a></li>
          </ul>
        </div>
        
        <div>
          <h3 className="font-black mb-4 uppercase tracking-widest text-[10px] text-gray-600">Developers</h3>
          <ul className="space-y-3 font-mono font-bold text-xs">
            <li><a href="#docs" className="hover:text-[#a3e635] hover:underline underline-offset-4">Documentation</a></li>
            <li><a href="#" className="hover:text-[#a3e635] hover:underline underline-offset-4">API</a></li>
            <li><a href="https://github.com/Yugenjr/DriftGuard-AI-Sdk" target="_blank" rel="noopener noreferrer" className="hover:text-[#a3e635] hover:underline underline-offset-4">GitHub</a></li>
            <li><a href="https://pypi.org/project/driftguard-ai-sdk/" target="_blank" rel="noopener noreferrer" className="hover:text-[#a3e635] hover:underline underline-offset-4">PyPI</a></li>
          </ul>
        </div>
        
        <div>
          <h3 className="font-black mb-4 uppercase tracking-widest text-[10px] text-gray-600">Project</h3>
          <ul className="space-y-3 font-mono font-bold text-xs">
            <li><a href="#" className="hover:text-[#a3e635] hover:underline underline-offset-4">About</a></li>
            <li><a href="#" className="hover:text-[#a3e635] hover:underline underline-offset-4">Contributing</a></li>
            <li><a href="#" className="hover:text-[#a3e635] hover:underline underline-offset-4">License</a></li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
