import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Switch } from '../../components/ui/switch';
import { useToast } from '../../hooks/use-toast';
import adminService from '../../services/adminService';
import { Settings, DollarSign, TrendingUp, Lock, Coins, Shield, FileCheck } from 'lucide-react';

const AdminSettings = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const data = await adminService.getSettings();
      setSettings(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch system settings',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await adminService.updateSettings(settings);
      toast({
        title: 'Success',
        description: 'System settings updated successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to update settings',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Are you sure you want to reset all settings to defaults?')) {
      return;
    }
    
    try {
      await adminService.resetSettings();
      fetchSettings();
      toast({
        title: 'Success',
        description: 'Settings reset to defaults',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to reset settings',
        variant: 'destructive',
      });
    }
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: parseFloat(value) || value
    }));
  };

  const updateArraySetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value.split(',').map(v => v.trim()).filter(v => v)
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">System Settings</h1>
          <p className="text-slate-600 mt-1">Configure platform fees, limits, KYC, and parameters</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleReset}>
            Reset to Defaults
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="fees" className="space-y-4">
        <TabsList>
          <TabsTrigger value="fees">
            <DollarSign className="w-4 h-4 mr-2" />
            Fees
          </TabsTrigger>
          <TabsTrigger value="limits">
            <Lock className="w-4 h-4 mr-2" />
            Limits
          </TabsTrigger>
          <TabsTrigger value="kyc">
            <Shield className="w-4 h-4 mr-2" />
            KYC Configuration
          </TabsTrigger>
          <TabsTrigger value="staking">
            <Coins className="w-4 h-4 mr-2" />
            Staking
          </TabsTrigger>
          <TabsTrigger value="investment">
            <TrendingUp className="w-4 h-4 mr-2" />
            Investment
          </TabsTrigger>
          <TabsTrigger value="web3">
            <Settings className="w-4 h-4 mr-2" />
            Web3
          </TabsTrigger>
        </TabsList>

        <TabsContent value="fees">
          <Card>
            <CardHeader>
              <CardTitle>Fee Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="transaction_fee_percentage">Transaction Fee (%)</Label>
                  <Input
                    id="transaction_fee_percentage"
                    type="number"
                    step="0.1"
                    value={settings?.transaction_fee_percentage || 0}
                    onChange={(e) => updateSetting('transaction_fee_percentage', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="withdrawal_fee_fixed">Fixed Withdrawal Fee</Label>
                  <Input
                    id="withdrawal_fee_fixed"
                    type="number"
                    step="0.1"
                    value={settings?.withdrawal_fee_fixed || 0}
                    onChange={(e) => updateSetting('withdrawal_fee_fixed', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="withdrawal_fee_percentage">Withdrawal Fee (%)</Label>
                  <Input
                    id="withdrawal_fee_percentage"
                    type="number"
                    step="0.1"
                    value={settings?.withdrawal_fee_percentage || 0}
                    onChange={(e) => updateSetting('withdrawal_fee_percentage', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="limits">
          <Card>
            <CardHeader>
              <CardTitle>Deposit & Withdrawal Limits</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="min_deposit_amount">Min Deposit Amount</Label>
                  <Input
                    id="min_deposit_amount"
                    type="number"
                    step="1"
                    value={settings?.min_deposit_amount || 0}
                    onChange={(e) => updateSetting('min_deposit_amount', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="max_deposit_amount">Max Deposit Amount</Label>
                  <Input
                    id="max_deposit_amount"
                    type="number"
                    step="1"
                    value={settings?.max_deposit_amount || 0}
                    onChange={(e) => updateSetting('max_deposit_amount', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="min_withdrawal_amount">Min Withdrawal Amount</Label>
                  <Input
                    id="min_withdrawal_amount"
                    type="number"
                    step="1"
                    value={settings?.min_withdrawal_amount || 0}
                    onChange={(e) => updateSetting('min_withdrawal_amount', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="max_withdrawal_amount">Max Withdrawal Amount</Label>
                  <Input
                    id="max_withdrawal_amount"
                    type="number"
                    step="1"
                    value={settings?.max_withdrawal_amount || 0}
                    onChange={(e) => updateSetting('max_withdrawal_amount', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="daily_withdrawal_limit">Daily Withdrawal Limit</Label>
                  <Input
                    id="daily_withdrawal_limit"
                    type="number"
                    step="1"
                    value={settings?.daily_withdrawal_limit || 0}
                    onChange={(e) => updateSetting('daily_withdrawal_limit', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="kyc">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-blue-600" />
                KYC Auto-Verification Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Auto Approval Settings */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">Auto-Approval Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                    <div>
                      <Label htmlFor="kyc_auto_approval_enabled">Enable Auto-Approval</Label>
                      <p className="text-sm text-slate-500">Automatically approve high-quality submissions</p>
                    </div>
                    <Switch
                      id="kyc_auto_approval_enabled"
                      checked={settings?.kyc_auto_approval_enabled || false}
                      onCheckedChange={(checked) => updateSetting('kyc_auto_approval_enabled', checked)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                    <div>
                      <Label htmlFor="kyc_require_face_detection">Require Face Detection</Label>
                      <p className="text-sm text-slate-500">Require valid face in ID photos</p>
                    </div>
                    <Switch
                      id="kyc_require_face_detection"
                      checked={settings?.kyc_require_face_detection || false}
                      onCheckedChange={(checked) => updateSetting('kyc_require_face_detection', checked)}
                    />
                  </div>
                </div>
              </div>

              {/* Quality Thresholds */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">Quality Thresholds</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="kyc_auto_approval_threshold">Auto-Approval Score Threshold (%)</Label>
                    <Input
                      id="kyc_auto_approval_threshold"
                      type="number"
                      step="1"
                      min="0"
                      max="100"
                      value={settings?.kyc_auto_approval_threshold || 80}
                      onChange={(e) => updateSetting('kyc_auto_approval_threshold', e.target.value)}
                    />
                    <p className="text-xs text-slate-500 mt-1">Minimum validation score for auto-approval (recommended: 80)</p>
                  </div>
                  <div>
                    <Label htmlFor="kyc_quality_threshold">Minimum Quality Score (%)</Label>
                    <Input
                      id="kyc_quality_threshold"
                      type="number"
                      step="1"
                      min="0"
                      max="100"
                      value={settings?.kyc_quality_threshold || 60}
                      onChange={(e) => updateSetting('kyc_quality_threshold', e.target.value)}
                    />
                    <p className="text-xs text-slate-500 mt-1">Minimum image quality score (recommended: 60)</p>
                  </div>
                  <div>
                    <Label htmlFor="kyc_max_file_size_mb">Max File Size (MB)</Label>
                    <Input
                      id="kyc_max_file_size_mb"
                      type="number"
                      step="0.5"
                      min="1"
                      max="50"
                      value={settings?.kyc_max_file_size_mb || 10}
                      onChange={(e) => updateSetting('kyc_max_file_size_mb', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Requirements */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">KYC Requirements</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                    <div>
                      <Label htmlFor="kyc_required_for_withdrawal">KYC Required for Withdrawal</Label>
                      <p className="text-sm text-slate-500">Users must complete KYC to withdraw</p>
                    </div>
                    <Switch
                      id="kyc_required_for_withdrawal"
                      checked={settings?.kyc_required_for_withdrawal || false}
                      onCheckedChange={(checked) => updateSetting('kyc_required_for_withdrawal', checked)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="kyc_required_amount_threshold">KYC Required Above Amount</Label>
                    <Input
                      id="kyc_required_amount_threshold"
                      type="number"
                      step="100"
                      value={settings?.kyc_required_amount_threshold || 1000}
                      onChange={(e) => updateSetting('kyc_required_amount_threshold', e.target.value)}
                    />
                    <p className="text-xs text-slate-500 mt-1">Threshold amount for mandatory KYC</p>
                  </div>
                </div>
              </div>

              {/* Allowed ID Types */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">Allowed ID Types</h3>
                <div>
                  <Label htmlFor="kyc_allowed_id_types">Accepted Document Types</Label>
                  <Input
                    id="kyc_allowed_id_types"
                    type="text"
                    value={(settings?.kyc_allowed_id_types || []).join(', ')}
                    onChange={(e) => updateArraySetting('kyc_allowed_id_types', e.target.value)}
                    placeholder="passport, national_id, driver_license"
                  />
                  <p className="text-xs text-slate-500 mt-1">Comma-separated list of accepted ID types</p>
                </div>
              </div>

              {/* Info Box */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
                <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                  <FileCheck className="w-4 h-4" />
                  Auto-Verification Features
                </h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• <strong>Image Quality Analysis:</strong> Resolution, brightness, sharpness, contrast</li>
                  <li>• <strong>Document Type Detection:</strong> Automatic ID type recognition</li>
                  <li>• <strong>Face Detection:</strong> Validates presence of face in photo IDs</li>
                  <li>• <strong>Blur Detection:</strong> Ensures document clarity</li>
                  <li>• <strong>Edge Detection:</strong> Validates document boundaries</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="staking">
          <Card>
            <CardHeader>
              <CardTitle>Staking Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="staking_basic_apy">Basic Plan APY (%)</Label>
                  <Input
                    id="staking_basic_apy"
                    type="number"
                    step="0.1"
                    value={settings?.staking_basic_apy || 0}
                    onChange={(e) => updateSetting('staking_basic_apy', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="staking_premium_apy">Premium Plan APY (%)</Label>
                  <Input
                    id="staking_premium_apy"
                    type="number"
                    step="0.1"
                    value={settings?.staking_premium_apy || 0}
                    onChange={(e) => updateSetting('staking_premium_apy', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="staking_vip_apy">VIP Plan APY (%)</Label>
                  <Input
                    id="staking_vip_apy"
                    type="number"
                    step="0.1"
                    value={settings?.staking_vip_apy || 0}
                    onChange={(e) => updateSetting('staking_vip_apy', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="min_staking_amount">Min Staking Amount</Label>
                  <Input
                    id="min_staking_amount"
                    type="number"
                    step="1"
                    value={settings?.min_staking_amount || 0}
                    onChange={(e) => updateSetting('min_staking_amount', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="staking_lock_period_days">Lock Period (Days)</Label>
                  <Input
                    id="staking_lock_period_days"
                    type="number"
                    step="1"
                    value={settings?.staking_lock_period_days || 0}
                    onChange={(e) => updateSetting('staking_lock_period_days', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="investment">
          <Card>
            <CardHeader>
              <CardTitle>Investment Packages</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="investment_starter_return">Starter Return (%)</Label>
                  <Input
                    id="investment_starter_return"
                    type="number"
                    step="0.1"
                    value={settings?.investment_starter_return || 0}
                    onChange={(e) => updateSetting('investment_starter_return', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="investment_growth_return">Growth Return (%)</Label>
                  <Input
                    id="investment_growth_return"
                    type="number"
                    step="0.1"
                    value={settings?.investment_growth_return || 0}
                    onChange={(e) => updateSetting('investment_growth_return', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="investment_premium_return">Premium Return (%)</Label>
                  <Input
                    id="investment_premium_return"
                    type="number"
                    step="0.1"
                    value={settings?.investment_premium_return || 0}
                    onChange={(e) => updateSetting('investment_premium_return', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="min_investment_amount">Min Investment Amount</Label>
                  <Input
                    id="min_investment_amount"
                    type="number"
                    step="1"
                    value={settings?.min_investment_amount || 0}
                    onChange={(e) => updateSetting('min_investment_amount', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="investment_period_days">Investment Period (Days)</Label>
                  <Input
                    id="investment_period_days"
                    type="number"
                    step="1"
                    value={settings?.investment_period_days || 0}
                    onChange={(e) => updateSetting('investment_period_days', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="web3">
          <Card>
            <CardHeader>
              <CardTitle>Web3 Network Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="eth_network">Ethereum Network</Label>
                  <Input
                    id="eth_network"
                    value={settings?.eth_network || 'mainnet'}
                    onChange={(e) => updateSetting('eth_network', e.target.value)}
                    placeholder="mainnet, goerli, sepolia"
                  />
                </div>
                <div>
                  <Label htmlFor="bsc_network">BSC Network</Label>
                  <Input
                    id="bsc_network"
                    value={settings?.bsc_network || 'mainnet'}
                    onChange={(e) => updateSetting('bsc_network', e.target.value)}
                    placeholder="mainnet, testnet"
                  />
                </div>
                <div>
                  <Label htmlFor="polygon_network">Polygon Network</Label>
                  <Input
                    id="polygon_network"
                    value={settings?.polygon_network || 'mainnet'}
                    onChange={(e) => updateSetting('polygon_network', e.target.value)}
                    placeholder="mainnet, mumbai"
                  />
                </div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Changes to network settings will affect crypto deposit and withdrawal functionality.
                  Make sure to update platform wallet addresses accordingly.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminSettings;