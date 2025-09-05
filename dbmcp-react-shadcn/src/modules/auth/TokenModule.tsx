import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';
import { apiService, ApiError } from '@/lib/api';
import { 
  Loader2, 
  Key, 
  Copy, 
  Check, 
  Plus, 
  ArrowLeft, 
  Info,
  Clock,
  User
} from 'lucide-react';
import { toast } from 'sonner';

interface TokenData {
  token: string;
  expires_at: string;
  username: string;
}

export default function TokenModule() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [tokenData, setTokenData] = useState<TokenData | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const generateToken = async () => {
    if (!user?.token) {
      setError('Authentication required');
      return;
    }

    setError('');
    setIsGenerating(true);

    try {
      const response = await apiService.generateToken(user.token);
      
      if (response.success && response.data) {
        setTokenData(response.data);
        toast.success('Token generated successfully!');
      } else {
        throw new Error(response.errors?.[0]?.msg || 'Failed to generate token');
      }
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Failed to generate token';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToken = async () => {
    if (!tokenData?.token) return;

    try {
      await navigator.clipboard.writeText(tokenData.token);
      setCopied(true);
      toast.success('Token copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy token');
    }
  };

  const generateAnother = () => {
    setTokenData(null);
    setError('');
  };

  const formatDateTime = (dateTimeString: string) => {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short'
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Generate New API Key</h1>
        <p className="text-gray-600">Create a new JWT token for API access</p>
      </div>

      {/* Info Alert */}
      <Alert className="mb-6">
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>About API Tokens:</strong> API tokens provide secure access to the DMCP API. 
          Each token is valid for a limited time and contains your user information. 
          Keep your tokens secure and never share them publicly. You can generate a new token at any time.
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Token Generation
          </CardTitle>
          <CardDescription>
            Click the button below to generate a new JWT token. The token will be displayed for you to copy.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {!tokenData ? (
            <div className="space-y-4">
              <div className="flex gap-4">
                <Button 
                  onClick={generateToken}
                  disabled={isGenerating}
                  className="flex items-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Key className="h-4 w-4" />
                      Generate Token
                    </>
                  )}
                </Button>
                <Button variant="outline" onClick={() => window.history.back()}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <Alert>
                <Check className="h-4 w-4" />
                <AlertDescription>
                  Token generated successfully! Copy the token below.
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium text-gray-700 mb-2 block">
                    Token
                  </Label>
                  <div className="relative">
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm break-all pr-20">
                      {tokenData.token}
                    </div>
                    <Button
                      size="sm"
                      onClick={copyToken}
                      className="absolute top-2 right-2"
                      variant={copied ? "default" : "outline"}
                    >
                      {copied ? (
                        <>
                          <Check className="h-3 w-3 mr-1" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3 mr-1" />
                          Copy
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-700 mb-2 block">
                      Expires At
                    </Label>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="h-4 w-4" />
                      {formatDateTime(tokenData.expires_at)}
                    </div>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-700 mb-2 block">
                      User
                    </Label>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User className="h-4 w-4" />
                      {tokenData.username}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-4">
                <Button onClick={generateAnother} className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Generate Another Token
                </Button>
                <Button variant="outline" onClick={() => window.history.back()}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
