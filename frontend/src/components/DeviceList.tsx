import { useEffect, useState } from "react";
import { type Device, DeviceStatus, DeviceType } from "../types/index";
import { apiClient } from "../api/client";

interface DeviceListProps {
  refreshTrigger: number;
}

export function DeviceList({ refreshTrigger }: DeviceListProps) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [togglingDevice, setTogglingDevice] = useState<string | null>(null);

  const fetchDevices = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getDevices();
      setDevices(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load devices");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, [refreshTrigger]);

  const handleToggleStatus = async (deviceId: string) => {
    setTogglingDevice(deviceId);
    try {
      const updatedDevice = await apiClient.toggleDeviceStatus(deviceId);
      setDevices((prev) =>
        prev.map((device) =>
          device.id === deviceId ? updatedDevice : device
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle device status");
    } finally {
      setTogglingDevice(null);
    }
  };

  const getDeviceTypeLabel = (type: DeviceType): string => {
    const labels: Record<DeviceType, string> = {
      [DeviceType.ACCESS_CONTROLLER]: "Access Controller",
      [DeviceType.FACE_READER]: "Face Recognition Reader",
      [DeviceType.ANPR]: "ANPR",
    };
    return labels[type];
  };

  if (loading) {
    return <div className="loading">Loading devices...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (devices.length === 0) {
    return <div className="empty-state">No devices found. Create one to get started!</div>;
  }

  return (
    <div className="device-list">
      <h2>Devices ({devices.length})</h2>
      <div className="devices-grid">
        {devices.map((device) => (
          <div key={device.id} className="device-card">
            <div className="device-header">
              <h3>{device.name}</h3>
              <span
                className={`status-badge ${
                  device.status === DeviceStatus.ACTIVE ? "active" : "inactive"
                }`}
              >
                {device.status === DeviceStatus.ACTIVE ? "Active" : "Inactive"}
              </span>
            </div>

            <div className="device-details">
              <div className="detail-row">
                <span className="detail-label">Type:</span>
                <span>{getDeviceTypeLabel(device.device_type)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">IP Address:</span>
                <span>{device.ip_address}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">ID:</span>
                <span className="device-id">{device.id}</span>
              </div>
            </div>

            <button
              className={`toggle-button ${
                device.status === DeviceStatus.ACTIVE ? "deactivate" : "activate"
              }`}
              onClick={() => handleToggleStatus(device.id)}
              disabled={togglingDevice === device.id}
            >
              {togglingDevice === device.id
                ? "Processing..."
                : device.status === DeviceStatus.ACTIVE
                ? "Deactivate"
                : "Activate"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
