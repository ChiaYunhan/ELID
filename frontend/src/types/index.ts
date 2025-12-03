export enum DeviceType {
  ACCESS_CONTROLLER = "access_controller",
  FACE_READER = "face_reader",
  ANPR = "anpr",
}

export enum DeviceStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
}

export interface Device {
  id: string;
  name: string;
  device_type: DeviceType;
  ip_address: string;
  status: DeviceStatus;
  created_at: string;
  updated_at: string;
}

export interface DeviceCreate {
  name: string;
  device_type: DeviceType;
  ip_address: string;
}

export interface Transaction {
  transaction_id: string;
  device_id: string;
  username: string;
  event_type: string;
  timestamp: string;
  payload: Record<string, any>;
  created_at: string;
}
