import type { Device, DeviceCreate, Transaction } from "../types/index";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      throw new Error(error.detail || "An error occurred");
    }

    return response.json();
  }

  // Device endpoints
  async getDevices(): Promise<Device[]> {
    return this.request<Device[]>("/devices/list");
  }

  async createDevice(device: DeviceCreate): Promise<Device> {
    return this.request<Device>("/devices/create", {
      method: "POST",
      body: JSON.stringify(device),
    });
  }

  async toggleDeviceStatus(deviceId: string): Promise<Device> {
    return this.request<Device>(`/devices/${deviceId}`, {
      method: "PUT",
    });
  }

  async getWorkersStatus(): Promise<{ active_worker_count: number; message: string }> {
    return this.request("/devices/workers/status");
  }

  // Transaction endpoints
  async getTransactions(
    limit: number = 100,
    offset: number = 0
  ): Promise<Transaction[]> {
    return this.request<Transaction[]>(
      `/transactions/list?limit=${limit}&offset=${offset}`
    );
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
