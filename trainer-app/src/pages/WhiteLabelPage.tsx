import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { UpgradePrompt } from '@/components/UpgradePrompt';
import { useSubscription } from '@/hooks/useSubscription';
import { Upload, X, Save } from 'lucide-react';
import { apiClient } from '@/api/client';

interface WhiteLabelSettings {
  id: number;
  remove_branding: boolean;
  custom_logo?: string;
  custom_favicon?: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  text_color: string;
  background_color: string;
  font_family: string;
}

export default function WhiteLabelPage() {
  const { canUse, isLoading: subLoading } = useSubscription();
  const [settings, setSettings] = useState<WhiteLabelSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [logoFile, setLogoFile] = useState<File | null>(null);

  useEffect(() => {
    if (!subLoading && canUse('white_label')) {
      fetchSettings();
    } else if (!subLoading) {
      setIsLoading(false);
    }
  }, [subLoading, canUse]);

  const fetchSettings = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get<WhiteLabelSettings>('/trainers/whitelabel/current/');
      setSettings(response);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // Create default settings
        setSettings({
          id: 0,
          remove_branding: false,
          primary_color: '#3b82f6',
          secondary_color: '#10b981',
          accent_color: '#f59e0b',
          text_color: '#1f2937',
          background_color: '#ffffff',
          font_family: 'Inter',
        });
      } else {
        console.error('Failed to load settings:', err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    try {
      setIsSaving(true);

      // Upload logo if changed
      if (logoFile) {
        const logoFormData = new FormData();
        logoFormData.append('logo', logoFile);
        await apiClient.post('/trainers/whitelabel/upload-logo/', logoFormData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      // Update settings
      const response = await apiClient.patch<WhiteLabelSettings>('/trainers/whitelabel/current/', settings);
      setSettings(response);
      alert('Settings saved successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 500 * 1024) {
        alert('Logo file size must be less than 500KB');
        return;
      }
      setLogoFile(file);
    }
  };

  const handleRemoveLogo = async () => {
    try {
      await apiClient.delete('/trainers/whitelabel/remove-logo/');
      setSettings((prev) => prev ? { ...prev, custom_logo: undefined } : null);
      setLogoFile(null);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to remove logo');
    }
  };

  if (subLoading || isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Loading...</p>
      </div>
    );
  }

  if (!canUse('white_label')) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <h1 className="text-3xl font-bold mb-8">White Label Settings</h1>
        <UpgradePrompt
          feature="white_label"
          requiredPlan="business"
          title="White-Label Branding"
          description="Customize your brand colors, logo, and remove TrainerHub branding from your pages."
        />
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p>Error loading settings. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">White Label Settings</h1>
      <p className="text-muted-foreground mb-6">
        Customize your brand appearance on all public-facing pages.
      </p>

      {/* Branding Options */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Branding Options</CardTitle>
          <CardDescription>Remove platform branding and add your own</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="remove-branding"
              checked={settings.remove_branding}
              onChange={(e) =>
                setSettings({ ...settings, remove_branding: e.target.checked })
              }
              className="h-4 w-4"
            />
            <Label htmlFor="remove-branding">
              Remove "Powered by TrainerHub" footer
            </Label>
          </div>
        </CardContent>
      </Card>

      {/* Logo Upload */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Custom Logo</CardTitle>
          <CardDescription>Upload your logo (max 500KB, PNG/SVG)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {(settings.custom_logo || logoFile) && (
            <div className="relative inline-block">
              <img
                src={
                  logoFile
                    ? URL.createObjectURL(logoFile)
                    : settings.custom_logo
                }
                alt="Logo preview"
                className="h-20 object-contain border rounded p-2"
              />
              <button
                onClick={handleRemoveLogo}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
          
          <div className="flex items-center gap-4">
            <Input
              type="file"
              accept="image/png,image/svg+xml"
              onChange={handleLogoChange}
              className="max-w-xs"
            />
            <Button variant="outline" size="sm" onClick={() => (document.querySelector('input[type="file"]') as HTMLElement)?.click()}>
              <Upload className="mr-2 h-4 w-4" />
              Choose File
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Brand Colors */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Brand Colors</CardTitle>
          <CardDescription>Customize your color scheme</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="primary-color">Primary Color</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  type="color"
                  id="primary-color"
                  value={settings.primary_color}
                  onChange={(e) =>
                    setSettings({ ...settings, primary_color: e.target.value })
                  }
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={settings.primary_color}
                  onChange={(e) =>
                    setSettings({ ...settings, primary_color: e.target.value })
                  }
                  placeholder="#3b82f6"
                  className="flex-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="secondary-color">Secondary Color</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  type="color"
                  id="secondary-color"
                  value={settings.secondary_color}
                  onChange={(e) =>
                    setSettings({ ...settings, secondary_color: e.target.value })
                  }
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={settings.secondary_color}
                  onChange={(e) =>
                    setSettings({ ...settings, secondary_color: e.target.value })
                  }
                  placeholder="#10b981"
                  className="flex-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="accent-color">Accent Color</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  type="color"
                  id="accent-color"
                  value={settings.accent_color}
                  onChange={(e) =>
                    setSettings({ ...settings, accent_color: e.target.value })
                  }
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={settings.accent_color}
                  onChange={(e) =>
                    setSettings({ ...settings, accent_color: e.target.value })
                  }
                  placeholder="#f59e0b"
                  className="flex-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="text-color">Text Color</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  type="color"
                  id="text-color"
                  value={settings.text_color}
                  onChange={(e) =>
                    setSettings({ ...settings, text_color: e.target.value })
                  }
                  className="w-16 h-10"
                />
                <Input
                  type="text"
                  value={settings.text_color}
                  onChange={(e) =>
                    setSettings({ ...settings, text_color: e.target.value })
                  }
                  placeholder="#1f2937"
                  className="flex-1"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Typography */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Typography</CardTitle>
          <CardDescription>Choose your font family</CardDescription>
        </CardHeader>
        <CardContent>
          <Label htmlFor="font-family">Font Family (Google Fonts)</Label>
          <Input
            type="text"
            id="font-family"
            value={settings.font_family}
            onChange={(e) =>
              setSettings({ ...settings, font_family: e.target.value })
            }
            placeholder="Inter"
            className="mt-1"
          />
          <p className="text-sm text-muted-foreground mt-2">
            Enter a Google Fonts family name (e.g., "Inter", "Roboto", "Poppins")
          </p>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isSaving} size="lg">
          <Save className="mr-2 h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
}

