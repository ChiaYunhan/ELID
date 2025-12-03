import { useState } from "react";
import { DeviceType, type DeviceCreate } from "../types/index";
import { apiClient } from "../api/client";

interface DeviceFormProps {
  onDeviceCreated: () => void;
}

export function DeviceForm({ onDeviceCreated }: DeviceFormProps) {
  const [formData, setFormData] = useState<DeviceCreate>({
    name: "",
    device_type: DeviceType.ACCESS_CONTROLLER,
    ip_address: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await apiClient.createDevice(formData);
      setFormData({
        name: "",
        device_type: DeviceType.ACCESS_CONTROLLER,
        ip_address: "",
      });
      onDeviceCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create device");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="device-form">
      <h2>Create New Device</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Device Name</label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            placeholder="e.g., Main Entrance Reader"
          />
        </div>

        <div className="form-group">
          <label htmlFor="device_type">Device Type</label>
          <select
            id="device_type"
            value={formData.device_type}
            onChange={(e) =>
              setFormData({
                ...formData,
                device_type: e.target.value as DeviceType,
              })
            }
            required
          >
            <option value={DeviceType.ACCESS_CONTROLLER}>
              Access Controller
            </option>
            <option value={DeviceType.FACE_READER}>Face Recognition Reader</option>
            <option value={DeviceType.ANPR}>ANPR</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="ip_address">IP Address</label>
          <input
            id="ip_address"
            type="text"
            value={formData.ip_address}
            onChange={(e) =>
              setFormData({ ...formData, ip_address: e.target.value })
            }
            required
            placeholder="e.g., 192.168.1.100"
            pattern="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create Device"}
        </button>
      </form>
    </div>
  );
}
