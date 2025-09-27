/**
 * Provider Status Monitoring Utilities
 * Handles monitoring of LLM provider health and status
 */

import { ProviderStatus, ProvidersStatusResponse } from '../types';
import { api } from '../api';

export interface ProviderStatusWithHistory extends ProviderStatus {
  lastChecked: string;
  uptime: number; // percentage
  responseTime: number; // average in ms
  errorCount: number;
  successCount: number;
  history: StatusCheck[];
}

export interface StatusCheck {
  timestamp: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime: number;
  error?: string;
}

export interface ProviderMonitorConfig {
  checkInterval: number; // ms
  maxHistorySize: number;
  alertThreshold: number; // error percentage
}

const DEFAULT_CONFIG: ProviderMonitorConfig = {
  checkInterval: 30000, // 30 seconds
  maxHistorySize: 100,
  alertThreshold: 10 // 10% error rate
};

export class ProviderStatusMonitor {
  private providers = new Map<string, ProviderStatusWithHistory>();
  private config: ProviderMonitorConfig;
  private monitoringTimer?: NodeJS.Timeout;
  private callbacks = new Set<(providers: ProviderStatusWithHistory[]) => void>();

  constructor(config: Partial<ProviderMonitorConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.loadFromStorage();
  }

  // Monitoring lifecycle
  start(): void {
    if (this.monitoringTimer) {
      return; // Already running
    }

    // Initial check
    this.checkAllProviders();

    // Set up periodic checks
    this.monitoringTimer = setInterval(() => {
      this.checkAllProviders();
    }, this.config.checkInterval);

    console.log('Provider monitoring started');
  }

  stop(): void {
    if (this.monitoringTimer) {
      clearInterval(this.monitoringTimer);
      this.monitoringTimer = undefined;
      console.log('Provider monitoring stopped');
    }
  }

  // Status checking
  async checkAllProviders(): Promise<void> {
    try {
      const startTime = Date.now();
      const response = await api.getProviderStatus();
      const responseTime = Date.now() - startTime;

      // Update provider statuses
      for (const providerStatus of response.providers) {
        this.updateProviderStatus(providerStatus, responseTime);
      }

      this.notifyCallbacks();
      this.saveToStorage();

    } catch (error) {
      console.error('Failed to check provider status:', error);

      // Mark all providers as unknown on error
      for (const [providerId, provider] of this.providers) {
        this.addStatusCheck(providerId, {
          timestamp: new Date().toISOString(),
          status: 'unknown',
          responseTime: 0,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }

      this.notifyCallbacks();
    }
  }

  private updateProviderStatus(status: ProviderStatus, responseTime: number): void {
    const providerId = status.provider;

    if (!this.providers.has(providerId)) {
      // Initialize new provider
      this.providers.set(providerId, {
        ...status,
        lastChecked: new Date().toISOString(),
        uptime: status.status === 'healthy' ? 100 : 0,
        responseTime,
        errorCount: status.status !== 'healthy' ? 1 : 0,
        successCount: status.status === 'healthy' ? 1 : 0,
        history: []
      });
    }

    const provider = this.providers.get(providerId)!;

    // Add status check to history
    this.addStatusCheck(providerId, {
      timestamp: new Date().toISOString(),
      status: status.status,
      responseTime,
      error: status.status !== 'healthy' ? status.details : undefined
    });

    // Update provider data
    provider.status = status.status;
    provider.details = status.details;
    provider.lastChecked = new Date().toISOString();
    provider.responseTime = this.calculateAverageResponseTime(provider);
    provider.uptime = this.calculateUptime(provider);

    if (status.status === 'healthy') {
      provider.successCount++;
    } else {
      provider.errorCount++;
    }
  }

  private addStatusCheck(providerId: string, check: StatusCheck): void {
    const provider = this.providers.get(providerId);
    if (!provider) {
      return;
    }

    provider.history.push(check);

    // Limit history size
    if (provider.history.length > this.config.maxHistorySize) {
      provider.history.shift();
    }
  }

  private calculateAverageResponseTime(provider: ProviderStatusWithHistory): number {
    const recentChecks = provider.history.slice(-10); // Last 10 checks
    if (recentChecks.length === 0) {
      return provider.responseTime;
    }

    const total = recentChecks.reduce((sum, check) => sum + check.responseTime, 0);
    return Math.round(total / recentChecks.length);
  }

  private calculateUptime(provider: ProviderStatusWithHistory): number {
    if (provider.history.length === 0) {
      return provider.status === 'healthy' ? 100 : 0;
    }

    const healthyChecks = provider.history.filter(check => check.status === 'healthy').length;
    return Math.round((healthyChecks / provider.history.length) * 100);
  }

  // Getters
  getProviders(): ProviderStatusWithHistory[] {
    return Array.from(this.providers.values());
  }

  getProvider(providerId: string): ProviderStatusWithHistory | null {
    return this.providers.get(providerId) || null;
  }

  getHealthyProviders(): ProviderStatusWithHistory[] {
    return this.getProviders().filter(p => p.status === 'healthy');
  }

  getUnhealthyProviders(): ProviderStatusWithHistory[] {
    return this.getProviders().filter(p => p.status === 'unhealthy');
  }

  // Analytics
  getOverallHealth(): {
    status: 'healthy' | 'degraded' | 'unhealthy';
    healthyCount: number;
    totalCount: number;
    averageUptime: number;
  } {
    const providers = this.getProviders();
    const healthyCount = providers.filter(p => p.status === 'healthy').length;
    const totalCount = providers.length;

    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    if (healthyCount === 0) {
      status = 'unhealthy';
    } else if (healthyCount < totalCount) {
      status = 'degraded';
    }

    const averageUptime = totalCount > 0
      ? Math.round(providers.reduce((sum, p) => sum + p.uptime, 0) / totalCount)
      : 0;

    return {
      status,
      healthyCount,
      totalCount,
      averageUptime
    };
  }

  getProviderAlerts(): {
    provider: string;
    alert: string;
    severity: 'low' | 'medium' | 'high';
  }[] {
    const alerts: {
      provider: string;
      alert: string;
      severity: 'low' | 'medium' | 'high';
    }[] = [];

    for (const provider of this.getProviders()) {
      // Check error rate
      const totalChecks = provider.successCount + provider.errorCount;
      if (totalChecks > 10) { // Only alert after sufficient data
        const errorRate = (provider.errorCount / totalChecks) * 100;

        if (errorRate > this.config.alertThreshold * 2) {
          alerts.push({
            provider: provider.provider,
            alert: `High error rate: ${errorRate.toFixed(1)}%`,
            severity: 'high'
          });
        } else if (errorRate > this.config.alertThreshold) {
          alerts.push({
            provider: provider.provider,
            alert: `Elevated error rate: ${errorRate.toFixed(1)}%`,
            severity: 'medium'
          });
        }
      }

      // Check uptime
      if (provider.uptime < 90) {
        alerts.push({
          provider: provider.provider,
          alert: `Low uptime: ${provider.uptime}%`,
          severity: provider.uptime < 70 ? 'high' : 'medium'
        });
      }

      // Check if provider is currently down
      if (provider.status === 'unhealthy') {
        alerts.push({
          provider: provider.provider,
          alert: 'Provider is currently unhealthy',
          severity: 'high'
        });
      }

      // Check response time
      if (provider.responseTime > 5000) { // 5 seconds
        alerts.push({
          provider: provider.provider,
          alert: `High response time: ${provider.responseTime}ms`,
          severity: 'medium'
        });
      }
    }

    return alerts;
  }

  // Event handling
  onStatusChange(callback: (providers: ProviderStatusWithHistory[]) => void): void {
    this.callbacks.add(callback);
  }

  offStatusChange(callback: (providers: ProviderStatusWithHistory[]) => void): void {
    this.callbacks.delete(callback);
  }

  private notifyCallbacks(): void {
    const providers = this.getProviders();
    for (const callback of this.callbacks) {
      try {
        callback(providers);
      } catch (error) {
        console.error('Error in provider status callback:', error);
      }
    }
  }

  // Persistence
  private saveToStorage(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const data = {
          providers: Array.from(this.providers.entries()),
          lastSaved: new Date().toISOString()
        };
        localStorage.setItem('promptyour_provider_status', JSON.stringify(data));
      } catch (error) {
        console.error('Failed to save provider status to localStorage:', error);
      }
    }
  }

  private loadFromStorage(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const stored = localStorage.getItem('promptyour_provider_status');
        if (stored) {
          const data = JSON.parse(stored);
          if (data.providers) {
            this.providers = new Map(data.providers);
          }
        }
      } catch (error) {
        console.error('Failed to load provider status from localStorage:', error);
      }
    }
  }

  // Reset data
  clearHistory(): void {
    for (const provider of this.providers.values()) {
      provider.history = [];
      provider.errorCount = 0;
      provider.successCount = 0;
      provider.uptime = provider.status === 'healthy' ? 100 : 0;
    }
    this.saveToStorage();
  }
}

// Singleton instance
let providerStatusMonitor: ProviderStatusMonitor | null = null;

export const getProviderStatusMonitor = (config?: Partial<ProviderMonitorConfig>): ProviderStatusMonitor => {
  if (!providerStatusMonitor || config) {
    providerStatusMonitor = new ProviderStatusMonitor(config);
  }
  return providerStatusMonitor;
};