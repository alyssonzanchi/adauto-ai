/**
 * Ad types
 */

export enum AdPlatform {
  FACEBOOK = "facebook",
  GOOGLE = "google",
  INSTAGRAM = "instagram",
  TIKTOK = "tiktok",
  LINKEDIN = "linkedin",
}

export enum AdStatus {
  DRAFT = "draft",
  SCHEDULED = "scheduled",
  ACTIVE = "active",
  PAUSED = "paused",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
}

export interface Ad {
  id: string;
  vehicle_id: string;
  platform: AdPlatform;
  platform_ad_id: string | null;
  status: AdStatus;
  title: string;
  description: string | null;
  headline: string | null;
  call_to_action: string | null;
  images: string[] | null;
  video_url: string | null;
  target_audience: Record<string, any> | null;
  budget_daily: number | null;
  budget_total: number | null;
  bid_amount: number | null;
  bid_strategy: string | null;
  start_date: string | null;
  end_date: string | null;
  ai_generated: boolean;
  ai_suggestions: AISuggestions | null;
  total_impressions: number;
  total_clicks: number;
  total_spend: number;
  total_conversions: number;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface AISuggestions {
  headlines: string[];
  descriptions: string[];
  ctas: string[];
  estimated_ctr: {
    min: number;
    max: number;
  };
  estimated_impressions: number;
}

export interface AdCreate {
  vehicle_id: string;
  platform: AdPlatform;
  title: string;
  description?: string;
  headline?: string;
  call_to_action?: string;
  images?: string[];
  video_url?: string;
  target_audience?: Record<string, any>;
  budget_daily?: number;
  budget_total?: number;
  bid_amount?: number;
  bid_strategy?: string;
  start_date?: string;
  end_date?: string;
}

export interface AdUpdate {
  title?: string;
  description?: string;
  headline?: string;
  call_to_action?: string;
  status?: AdStatus;
  images?: string[];
  target_audience?: Record<string, any>;
  budget_daily?: number;
  budget_total?: number;
  bid_amount?: number;
  start_date?: string;
  end_date?: string;
}

export interface AdStatusUpdate {
  status: AdStatus;
  reason?: string;
}

export interface AdFilter {
  search?: string;
  platform?: AdPlatform;
  status?: AdStatus;
  vehicle_id?: string;
  start_date_min?: string;
  start_date_max?: string;
  ai_generated?: boolean;
}

export interface AdPreviewRequest {
  title: string;
  description?: string;
  headline?: string;
  call_to_action?: string;
  images?: string[];
  platform: AdPlatform;
}

export interface AdPreviewResponse {
  preview_url: string;
  preview_html: string;
  estimated_ctr?: {
    min: number;
    max: number;
  };
  estimated_impressions?: number;
}

export const AD_PLATFORM_LABELS: Record<AdPlatform, string> = {
  [AdPlatform.FACEBOOK]: "Facebook",
  [AdPlatform.GOOGLE]: "Google Ads",
  [AdPlatform.INSTAGRAM]: "Instagram",
  [AdPlatform.TIKTOK]: "TikTok",
  [AdPlatform.LINKEDIN]: "LinkedIn",
};

export const AD_STATUS_LABELS: Record<AdStatus, string> = {
  [AdStatus.DRAFT]: "Rascunho",
  [AdStatus.SCHEDULED]: "Agendado",
  [AdStatus.ACTIVE]: "Ativo",
  [AdStatus.PAUSED]: "Pausado",
  [AdStatus.COMPLETED]: "Concluído",
  [AdStatus.CANCELLED]: "Cancelado",
};

export const AD_STATUS_COLORS: Record<AdStatus, string> = {
  [AdStatus.DRAFT]: "bg-gray-100 text-gray-800",
  [AdStatus.SCHEDULED]: "bg-blue-100 text-blue-800",
  [AdStatus.ACTIVE]: "bg-green-100 text-green-800",
  [AdStatus.PAUSED]: "bg-yellow-100 text-yellow-800",
  [AdStatus.COMPLETED]: "bg-purple-100 text-purple-800",
  [AdStatus.CANCELLED]: "bg-red-100 text-red-800",
};
