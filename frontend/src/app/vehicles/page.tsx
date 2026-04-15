/**
 * Vehicles List Page
 */

"use client";

import { useState } from "react";
import { useVehicles } from "@/lib/hooks/use-vehicles";
import { Vehicle, VehicleStatus, VehicleFilter } from "@/types/vehicle";
import {
  FUEL_TYPE_LABELS,
  TRANSMISSION_TYPE_LABELS,
  BODY_TYPE_LABELS,
  VEHICLE_STATUS_LABELS,
  PRICE_POSITIONS,
} from "@/types/vehicle";

export default function VehiclesPage() {
  const [filters, setFilters] = useState<VehicleFilter>({});
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data, isLoading, error } = useVehicles(filters, page, pageSize);

  const handleSearchChange = (value: string) => {
    setFilters({ ...filters, search: value });
    setPage(1);
  };

  const handleBrandChange = (value: string) => {
    setFilters({ ...filters, brand: value || undefined });
    setPage(1);
  };

  const handleStatusChange = (value: string) => {
    setFilters({ ...filters, status: (value as VehicleStatus) || undefined });
    setPage(1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Veículos</h1>
              <p className="mt-1 text-sm text-gray-500">
                Gerencie o estoque de veículos da sua concessionária
              </p>
            </div>
            <button
              type="button"
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              onClick={() => (window.location.href = "/vehicles/new")}
            >
              Adicionar Veículo
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
            {/* Search */}
            <div className="sm:col-span-2">
              <label
                htmlFor="search"
                className="block text-sm font-medium text-gray-700"
              >
                Buscar
              </label>
              <input
                type="text"
                id="search"
                placeholder="Título, marca, modelo, placa..."
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                value={filters.search || ""}
                onChange={(e) => handleSearchChange(e.target.value)}
              />
            </div>

            {/* Brand */}
            <div>
              <label
                htmlFor="brand"
                className="block text-sm font-medium text-gray-700"
              >
                Marca
              </label>
              <input
                type="text"
                id="brand"
                placeholder="Filtrar por marca"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                value={filters.brand || ""}
                onChange={(e) => handleBrandChange(e.target.value)}
              />
            </div>

            {/* Status */}
            <div>
              <label
                htmlFor="status"
                className="block text-sm font-medium text-gray-700"
              >
                Status
              </label>
              <select
                id="status"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                value={filters.status || ""}
                onChange={(e) => handleStatusChange(e.target.value)}
              >
                <option value="">Todos</option>
                <option value={VehicleStatus.ACTIVE}>Ativo</option>
                <option value={VehicleStatus.PENDING}>Pendente</option>
                <option value={VehicleStatus.SOLD}>Vendido</option>
                <option value={VehicleStatus.INACTIVE}>Inativo</option>
              </select>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-red-800">
              Erro ao carregar veículos. Tente novamente mais tarde.
            </p>
          </div>
        )}

        {/* Vehicles Grid */}
        {!isLoading && !error && data && (
          <>
            <div className="mb-4 text-sm text-gray-700">
              Mostrando {data.items.length} de {data.total} veículos
            </div>

            <div className="bg-white shadow overflow-hidden rounded-lg">
              <ul className="divide-y divide-gray-200">
                {data.items.map((vehicle: Vehicle) => (
                  <VehicleListItem key={vehicle.id} vehicle={vehicle} />
                ))}
                {data.items.length === 0 && (
                  <li className="px-4 py-12 text-center">
                    <p className="text-sm text-gray-500">
                      Nenhum veículo encontrado
                    </p>
                  </li>
                )}
              </ul>
            </div>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="mt-6 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Página {page} de {data.total_pages}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() =>
                      setPage((p) => Math.min(data.total_pages, p + 1))
                    }
                    disabled={page === data.total_pages}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function VehicleListItem({ vehicle }: { vehicle: Vehicle }) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  };

  const pricePosition = PRICE_POSITIONS[vehicle.price_position || ""];

  return (
    <li className="px-4 py-4 sm:px-6 hover:bg-gray-50 cursor-pointer">
      <div className="flex items-center">
        {/* Image */}
        <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
          {vehicle.main_image ? (
            <img
              src={vehicle.main_image}
              alt={vehicle.title}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center">
              <svg
                className="h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="ml-4 flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {vehicle.title}
              </h3>
              <p className="text-sm text-gray-500">
                {vehicle.brand} {vehicle.model} • {vehicle.year}
                {vehicle.model_year && `/${vehicle.model_year}`}
              </p>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-gray-900">
                {formatCurrency(vehicle.price)}
              </p>
              {vehicle.price_score && (
                <span
                  className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                    pricePosition?.color || "text-gray-600 bg-gray-50"
                  }`}
                >
                  {pricePosition?.label || "Sem análise"}
                </span>
              )}
            </div>
          </div>

          <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
            {vehicle.mileage && (
              <span>{vehicle.mileage.toLocaleString("pt-BR")} km</span>
            )}
            {vehicle.transmission && (
              <span>{TRANSMISSION_TYPE_LABELS[vehicle.transmission]}</span>
            )}
            {vehicle.fuel_type && (
              <span>{FUEL_TYPE_LABELS[vehicle.fuel_type]}</span>
            )}
            {vehicle.body_type && (
              <span>{BODY_TYPE_LABELS[vehicle.body_type]}</span>
            )}
          </div>

          <div className="mt-2 flex items-center gap-2">
            <span
              className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ${
                vehicle.status === VehicleStatus.ACTIVE
                  ? "bg-green-50 text-green-700"
                  : vehicle.status === VehicleStatus.PENDING
                    ? "bg-yellow-50 text-yellow-700"
                    : vehicle.status === VehicleStatus.SOLD
                      ? "bg-blue-50 text-blue-700"
                      : "bg-gray-50 text-gray-700"
              }`}
            >
              {VEHICLE_STATUS_LABELS[vehicle.status]}
            </span>
            {vehicle.images && vehicle.images.length > 0 && (
              <span className="text-xs text-gray-500">
                {vehicle.images.length}{" "}
                {vehicle.images.length === 1 ? "foto" : "fotos"}
              </span>
            )}
          </div>
        </div>
      </div>
    </li>
  );
}
