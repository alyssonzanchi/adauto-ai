/**
 * Vehicle types
 */

export enum FuelType {
  GASOLINE = "gasoline",
  ETHANOL = "ethanol",
  DIESEL = "diesel",
  FLEX = "flex",
  ELECTRIC = "electric",
  HYBRID = "hybrid",
}

export enum TransmissionType {
  MANUAL = "manual",
  AUTOMATIC = "automatic",
  CVT = "cvt",
  DCT = "dct",
}

export enum BodyType {
  SEDAN = "sedan",
  HATCH = "hatch",
  SUV = "suv",
  PICKUP = "pickup",
  COUPE = "coupe",
  CONVERTIBLE = "convertible",
  VAN = "van",
  WAGON = "wagon",
}

export enum VehicleStatus {
  ACTIVE = "active",
  SOLD = "sold",
  PENDING = "pending",
  INACTIVE = "inactive",
}

export interface Vehicle {
  id: string;
  dealership_id: string;
  title: string;
  description: string | null;
  brand: string;
  model: string;
  year: number;
  model_year: number | null;
  version: string | null;
  color: string | null;
  mileage: number | null;
  plate: string | null;
  chassis: string | null;
  doors: number | null;
  seats: number | null;
  fuel_type: FuelType | null;
  transmission: TransmissionType | null;
  body_type: BodyType | null;
  price: number;
  price_market: number | null;
  price_score: number | null;
  price_position: string | null;
  images: string[];
  main_image: string | null;
  video_url: string | null;
  features: Record<string, string[] | string>;
  status: VehicleStatus;
  sold_at: string | null;
  sold_price: number | null;
  ai_analysis: AIAnalysis | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface AIAnalysis {
  score?: number;
  selling_points: string[];
  target_audience: string[];
  suggested_improvements: string[];
  estimated_ctr: number;
  estimated_conversion: number;
  model_version: string;
  price_market: number;
  price_score: number;
  price_position: string;
  analysis_version: string;
  analyzed_at: string;
}

export interface VehicleCreate {
  title: string;
  description?: string;
  brand: string;
  model: string;
  year: number;
  model_year?: number;
  version?: string;
  color?: string;
  mileage?: number;
  plate?: string;
  chassis?: string;
  doors?: number;
  seats?: number;
  fuel_type?: FuelType;
  transmission?: TransmissionType;
  body_type?: BodyType;
  price: number;
  video_url?: string;
  features?: Record<string, string[] | string>;
  status?: VehicleStatus;
}

export interface VehicleUpdate {
  title?: string;
  description?: string;
  brand?: string;
  model?: string;
  year?: number;
  model_year?: number;
  version?: string;
  color?: string;
  mileage?: number;
  plate?: string;
  chassis?: string;
  doors?: number;
  seats?: number;
  fuel_type?: FuelType;
  transmission?: TransmissionType;
  body_type?: BodyType;
  price?: number;
  video_url?: string;
  features?: Record<string, string[] | string>;
  status?: VehicleStatus;
}

export interface VehicleFilter {
  search?: string;
  brand?: string;
  model?: string;
  year_min?: number;
  year_max?: number;
  price_min?: number;
  price_max?: number;
  status?: VehicleStatus;
}

export interface VehicleAnalyzeResponse {
  price_market: number;
  price_score: number;
  price_position: string;
  ai_analysis: AIAnalysis;
}

export interface ImageUploadResponse {
  images: string[];
  main_image: string | null;
}

export interface PricePosition {
  value: string;
  label: string;
  color: string;
}

export const PRICE_POSITIONS: Record<string, PricePosition> = {
  great_deal: {
    value: "great_deal",
    label: "Ótimo Negócio",
    color: "text-green-600 bg-green-50",
  },
  good_price: {
    value: "good_price",
    label: "Bom Preço",
    color: "text-emerald-600 bg-emerald-50",
  },
  fair_price: {
    value: "fair_price",
    label: "Preço Justo",
    color: "text-blue-600 bg-blue-50",
  },
  above_market: {
    value: "above_market",
    label: "Acima do Mercado",
    color: "text-yellow-600 bg-yellow-50",
  },
  expensive: {
    value: "expensive",
    label: "Caro",
    color: "text-orange-600 bg-orange-50",
  },
  overpriced: {
    value: "overpriced",
    label: "Muito Caro",
    color: "text-red-600 bg-red-50",
  },
};

export const FUEL_TYPE_LABELS: Record<FuelType, string> = {
  [FuelType.GASOLINE]: "Gasolina",
  [FuelType.ETHANOL]: "Etanol",
  [FuelType.DIESEL]: "Diesel",
  [FuelType.FLEX]: "Flex",
  [FuelType.ELECTRIC]: "Elétrico",
  [FuelType.HYBRID]: "Híbrido",
};

export const TRANSMISSION_TYPE_LABELS: Record<TransmissionType, string> = {
  [TransmissionType.MANUAL]: "Manual",
  [TransmissionType.AUTOMATIC]: "Automático",
  [TransmissionType.CVT]: "CVT",
  [TransmissionType.DCT]: "DCT",
};

export const BODY_TYPE_LABELS: Record<BodyType, string> = {
  [BodyType.SEDAN]: "Sedã",
  [BodyType.HATCH]: "Hatch",
  [BodyType.SUV]: "SUV",
  [BodyType.PICKUP]: "Pickup",
  [BodyType.COUPE]: "Coupé",
  [BodyType.CONVERTIBLE]: "Conversível",
  [BodyType.VAN]: "Van",
  [BodyType.WAGON]: "Perua",
};

export const VEHICLE_STATUS_LABELS: Record<VehicleStatus, string> = {
  [VehicleStatus.ACTIVE]: "Ativo",
  [VehicleStatus.SOLD]: "Vendido",
  [VehicleStatus.PENDING]: "Pendente",
  [VehicleStatus.INACTIVE]: "Inativo",
};
