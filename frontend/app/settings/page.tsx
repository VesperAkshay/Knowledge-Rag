"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { motion } from 'framer-motion';
import { Settings, Key, Database, Save, AlertCircle, CheckCircle, Eye, EyeOff, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, hasCredentials, saveCredentials, checkAuth } = useAuth();
  const [googleApiKey, setGoogleApiKey] = useState('');
  const [chromadbApiKey, setChromadbApiKey] = useState('');
  const [chromadbTenant, setChromadbTenant] = useState('default-tenant');
  const [chromadbDatabase, setChromadbDatabase] = useState('default_database');
  const [showKeys, setShowKeys] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingCreds, setLoadingCreds] = useState(true);
  const [hasExistingCreds, setHasExistingCreds] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Load existing credentials metadata (for tenant/database defaults)
    const loadCredentials = async () => {
      try {
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_BASE}/api/auth/credentials`, {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          if (data.has_credentials) {
            setHasExistingCreds(true);
            // Only load non-sensitive defaults (tenant and database)
            // Don't pre-fill API keys with masked values
            setChromadbTenant(data.chromadb_tenant);
            setChromadbDatabase(data.chromadb_database);
            // Leave API key fields empty - user must enter them
          }
        }
      } catch (err) {
        console.error('Failed to load credentials:', err);
      } finally {
        setLoadingCreds(false);
      }
    };

    loadCredentials();
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation: API keys must be provided
    if (!googleApiKey || !chromadbApiKey) {
      setError('Both API keys are required');
      return;
    }

    setIsLoading(true);

    try {
      await saveCredentials({
        google_api_key: googleApiKey,
        chromadb_api_key: chromadbApiKey,
        chromadb_tenant: chromadbTenant,
        chromadb_database: chromadbDatabase
      });

      setSuccess('Credentials saved successfully!');
      await checkAuth(); // Refresh auth state
      
      // Redirect to main app after a delay
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to save credentials');
    } finally {
      setIsLoading(false);
    }
  };

  if (loadingCreds) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 py-12">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link href="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-4 mb-2">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/10 rounded-xl border border-primary/20">
              <Settings className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">API Configuration</h1>
              <p className="text-muted-foreground">Configure your Google Gemini and ChromaDB credentials</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-card backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-border"
        >
          {/* User Info */}
          <div className="mb-8 p-4 bg-muted rounded-lg border border-border">
            <p className="text-muted-foreground text-sm">Logged in as</p>
            <p className="text-foreground font-semibold">{user?.username}</p>
            <p className="text-muted-foreground text-xs mt-1">{user?.user_id}</p>
          </div>

          {/* Info Box */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8 p-4 bg-primary/10 border border-primary/30 rounded-lg"
          >
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <div>
                <p className="text-foreground text-sm font-medium mb-1">Why do I need these?</p>
                <p className="text-muted-foreground text-xs leading-relaxed">
                  This is a multi-user system. Each user provides their own API keys to ensure data isolation and billing control. 
                  Your credentials are stored securely and only accessible by you.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Existing Credentials Notice */}
          {hasExistingCreds && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-6 p-4 bg-muted border border-border rounded-lg flex items-center gap-3"
            >
              <CheckCircle className="w-5 h-5 text-primary shrink-0" />
              <div>
                <p className="text-foreground text-sm font-medium">Credentials Already Saved</p>
                <p className="text-muted-foreground text-xs mt-1">
                  Your API keys are securely stored. Enter new keys below to update them.
                </p>
              </div>
            </motion.div>
          )}

          {/* Success/Error Messages */}
          {error && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-6 p-4 bg-destructive/10 border border-destructive/50 rounded-lg flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-destructive shrink-0" />
              <p className="text-destructive text-sm">{error}</p>
            </motion.div>
          )}

          {success && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-6 p-4 bg-green-500/20 border border-green-500/50 rounded-lg flex items-center gap-3"
            >
              <CheckCircle className="w-5 h-5 text-green-400 shrink-0" />
              <p className="text-green-200 text-sm">{success}</p>
            </motion.div>
          )}

          {/* Credentials Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Google API Key */}
            <div>
              <label htmlFor="googleApiKey" className="block text-sm font-medium text-foreground mb-2">
                Google Gemini API Key
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  id="googleApiKey"
                  type={showKeys ? "text" : "password"}
                  value={googleApiKey}
                  onChange={(e) => setGoogleApiKey(e.target.value)}
                  required={!hasExistingCreds}
                  className="w-full pl-11 pr-12 py-3 bg-background border border-input rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
                  placeholder={hasExistingCreds ? "Enter new API key to update..." : "AIza..."}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(!showKeys)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showKeys ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              <p className="text-muted-foreground text-xs mt-1">
                Get your API key from{' '}
                <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:opacity-80">
                  Google AI Studio
                </a>
              </p>
            </div>

            {/* ChromaDB API Key */}
            <div>
              <label htmlFor="chromadbApiKey" className="block text-sm font-medium text-foreground mb-2">
                ChromaDB API Key
              </label>
              <div className="relative">
                <Database className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  id="chromadbApiKey"
                  type={showKeys ? "text" : "password"}
                  value={chromadbApiKey}
                  onChange={(e) => setChromadbApiKey(e.target.value)}
                  required={!hasExistingCreds}
                  className="w-full pl-11 pr-4 py-3 bg-background border border-input rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
                  placeholder={hasExistingCreds ? "Enter new API key to update..." : "chroma_..."}
                  disabled={isLoading}
                />
              </div>
              <p className="text-muted-foreground text-xs mt-1">
                Get your API key from{' '}
                <a href="https://www.trychroma.com/" target="_blank" rel="noopener noreferrer" className="text-primary hover:opacity-80">
                  ChromaDB Cloud
                </a>
              </p>
            </div>

            {/* ChromaDB Tenant */}
            <div>
              <label htmlFor="chromadbTenant" className="block text-sm font-medium text-foreground mb-2">
                ChromaDB Tenant
              </label>
              <input
                id="chromadbTenant"
                type="text"
                value={chromadbTenant}
                onChange={(e) => setChromadbTenant(e.target.value)}
                required
                className="w-full px-4 py-3 bg-background border border-input rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
                placeholder="default-tenant"
                disabled={isLoading}
              />
            </div>

            {/* ChromaDB Database */}
            <div>
              <label htmlFor="chromadbDatabase" className="block text-sm font-medium text-foreground mb-2">
                ChromaDB Database
              </label>
              <input
                id="chromadbDatabase"
                type="text"
                value={chromadbDatabase}
                onChange={(e) => setChromadbDatabase(e.target.value)}
                required
                className="w-full px-4 py-3 bg-background border border-input rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
                placeholder="default_database"
                disabled={isLoading}
              />
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full"
                  />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Save Credentials
                </>
              )}
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
