import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import { getMe, rotateApiKey } from '../lib/api';
import { useAuth, withAuth } from '../hooks/useAuth';
import { toast } from 'react-hot-toast';
import { User, Key, AlertTriangle, CheckCircle2, Copy, Eye, EyeOff, Shield, RefreshCw } from 'lucide-react';

function Settings() {
  const { apiKey, setApiKey } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [showKey, setShowKey] = useState(false);
  const [rotating, setRotating] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getMe();
      setProfile(data);
    } catch (err) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleRotateKey = async () => {
    if (!confirm("WARNING: Rotating your API Key will immediately invalidate your old key. All active SDK deployments using the old key will fail to authenticate until you update them. Are you sure you want to proceed?")) {
      return;
    }

    setRotating(true);
    try {
      const data = await rotateApiKey();
      setApiKey(data.api_key);
      toast.success('API Key rotated successfully!');
      setShowKey(true); // Automatically show the new key so they can copy it
    } catch (err) {
      toast.error(err.message || 'Failed to rotate API Key');
    } finally {
      setRotating(false);
    }
  };

  const copyToClipboard = () => {
    if (navigator.clipboard && apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      toast.success('API Key copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="w-8 h-8 border-4 border-[#24b47e] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>Settings - DriftGuard</title>
      </Head>

      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-[#ededed] mb-8 flex items-center">
          <User className="w-6 h-6 mr-3 text-[#24b47e]" />
          Account Settings
        </h1>

        <div className="space-y-8">
          {/* Profile Section */}
          <section className="bg-[#09090b] border border-white/10 rounded-xl overflow-hidden shadow-sm transition-all hover:shadow-md">
            <div className="border-b border-white/10 px-6 py-4 bg-gradient-to-r from-[#1c2128] to-[#161b22]">
              <h2 className="text-lg font-semibold text-[#ededed]">Profile Information</h2>
            </div>
            <div className="p-6">
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-[#a1a1aa]">Full Name</dt>
                  <dd className="mt-1 text-sm text-[#ededed] font-semibold">{profile?.name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-[#a1a1aa]">Email Address</dt>
                  <dd className="mt-1 text-sm text-[#ededed] font-semibold">{profile?.email}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-[#a1a1aa]">Account Created</dt>
                  <dd className="mt-1 text-sm text-[#ededed]">{new Date(profile?.created_at).toLocaleDateString()}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-[#a1a1aa]">Status</dt>
                  <dd className="mt-1">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#238636]/20 text-[#3fb950] border border-[#238636]/30">
                      Active
                    </span>
                  </dd>
                </div>
              </dl>
            </div>
          </section>

          {/* API Key Management */}
          <section className="bg-[#09090b] border border-white/10 rounded-xl overflow-hidden shadow-sm transition-all hover:shadow-md">
            <div className="border-b border-white/10 px-6 py-4 flex items-center justify-between bg-gradient-to-r from-[#1c2128] to-[#161b22]">
              <div className="flex items-center space-x-2">
                <Key className="w-5 h-5 text-[#a371f7]" />
                <h2 className="text-lg font-semibold text-[#ededed]">API Key Management</h2>
              </div>
            </div>
            <div className="p-6 space-y-6">
              <p className="text-sm text-[#a1a1aa]">
                Your API key is used to authenticate requests from your SDK deployments to the DriftGuard backend. 
                Keep this key secret and do not expose it in client-side code.
              </p>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-[#8b949e] uppercase tracking-wider">Current Secret Key</label>
                <div className="flex items-center space-x-3">
                  <div className="relative flex-1 group">
                    <input
                      type={showKey ? "text" : "password"}
                      value={apiKey || ''}
                      readOnly
                      className="block w-full pl-3 pr-10 py-2.5 border border-white/10 rounded-xl leading-5 bg-[#09090b] text-[#ededed] font-mono text-sm focus:outline-none focus:ring-1 focus:ring-[#58a6ff] transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowKey(!showKey)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#a1a1aa] hover:text-[#ededed] transition-colors"
                    >
                      {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center space-x-2 px-4 py-2.5 bg-[#2e2e2e] border border-white/10 hover:bg-[#30363d] hover:border-[#8b949e] rounded-xl font-medium text-sm text-[#ededed] transition-all active:scale-95"
                  >
                    {copied ? <CheckCircle2 className="w-4 h-4 text-[#3fb950]" /> : <Copy className="w-4 h-4" />}
                    <span>{copied ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Danger Zone */}
          <section className="bg-[#09090b] border border-[#f85149]/30 rounded-xl overflow-hidden shadow-sm">
            <div className="border-b border-[#f85149]/20 px-6 py-4 bg-[#f85149]/5">
              <h2 className="text-lg font-semibold text-[#f85149] flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Danger Zone
              </h2>
            </div>
            <div className="p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between">
                <div className="mb-4 sm:mb-0">
                  <h3 className="text-sm font-semibold text-[#ededed]">Rotate API Key</h3>
                  <p className="text-sm text-[#a1a1aa] mt-1 max-w-xl">
                    Instantly invalidate your current API Key and generate a new one. 
                    Any running applications using the old key will lose access immediately.
                  </p>
                </div>
                <button
                  onClick={handleRotateKey}
                  disabled={rotating}
                  className="flex items-center justify-center px-4 py-2 bg-transparent border border-[#f85149]/50 text-[#f85149] hover:bg-[#f85149] hover:text-white rounded-xl font-semibold text-sm transition-all whitespace-nowrap disabled:opacity-50 active:scale-95"
                >
                  {rotating ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Shield className="w-4 h-4 mr-2" />
                  )}
                  {rotating ? 'Rotating...' : 'Rotate Key'}
                </button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </Layout>
  );
}

export default withAuth(Settings);
