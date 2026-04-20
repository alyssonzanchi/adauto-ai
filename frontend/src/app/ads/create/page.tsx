/**
 * Create Ad Page
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { AdCreate, AdPlatform, AD_PLATFORM_LABELS } from "@/types/ad";

export default function CreateAdPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState<any[]>([]);
  const [formData, setFormData] = useState<Partial<AdCreate>>({
    platform: AdPlatform.FACEBOOK,
  });

  const totalSteps = 3;

  const fetchVehicles = async () => {
    try {
      const response = await axios.get("/api/v1/vehicles?page=1&page_size=100");
      setVehicles(response.data.items || []);
    } catch (error) {
      console.error("Error fetching vehicles:", error);
    }
  };

  // Fetch vehicles on mount
  useState(() => {
    fetchVehicles();
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value ? parseFloat(value) : undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post("/api/v1/ads", formData);
      router.push("/ads");
    } catch (error: any) {
      console.error("Error creating ad:", error);
      const errorMessage = error.response?.data?.detail || "Erro ao criar anúncio";
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    // Validate current step before proceeding
    if (step === 1) {
      if (!formData.vehicle_id) {
        alert("Selecione um veículo");
        return;
      }
      if (!formData.platform) {
        alert("Selecione uma plataforma");
        return;
      }
    }
    if (step === 2) {
      if (!formData.title) {
        alert("Digite o título do anúncio");
        return;
      }
    }
    setStep(step + 1);
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Criar Anúncio</h1>
              <p className="mt-1 text-sm text-gray-500">
                Passo {step} de {totalSteps}:{" "}
                {step === 1
                  ? "Veículo e Plataforma"
                  : step === 2
                  ? "Conteúdo do Anúncio"
                  : "Orçamento e Agendamento"}
              </p>
            </div>
            <button
              type="button"
              className="text-sm text-gray-500 hover:text-gray-700"
              onClick={() => router.push("/ads")}
            >
              Cancelar
            </button>
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
              <div
                style={{ width: `${(step / totalSteps) * 100}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600 transition-all duration-300"
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span className={step >= 1 ? "text-blue-600 font-semibold" : ""}>
                Veículo
              </span>
              <span className={step >= 2 ? "text-blue-600 font-semibold" : ""}>
                Conteúdo
              </span>
              <span className={step >= 3 ? "text-blue-600 font-semibold" : ""}>
                Orçamento
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {step === 1 && (
            <div className="bg-white shadow rounded-lg p-6 space-y-6">
              {/* Vehicle Selection */}
              <div>
                <label
                  htmlFor="vehicle_id"
                  className="block text-sm font-medium text-gray-700"
                >
                  Veículo *
                </label>
                <select
                  id="vehicle_id"
                  name="vehicle_id"
                  required
                  value={formData.vehicle_id || ""}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                >
                  <option value="">Selecione um veículo</option>
                  {vehicles.map((vehicle) => (
                    <option key={vehicle.id} value={vehicle.id}>
                      {vehicle.title} ({vehicle.brand} {vehicle.model} {vehicle.year})
                    </option>
                  ))}
                </select>
              </div>

              {/* Platform Selection */}
              <div>
                <label
                  htmlFor="platform"
                  className="block text-sm font-medium text-gray-700"
                >
                  Plataforma *
                </label>
                <select
                  id="platform"
                  name="platform"
                  required
                  value={formData.platform || AdPlatform.FACEBOOK}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                >
                  {Object.entries(AD_PLATFORM_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Vehicle Preview */}
              {formData.vehicle_id && (
                <div className="border-t pt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">
                    Veículo Selecionado
                  </h3>
                  {(() => {
                    const vehicle = vehicles.find((v) => v.id === formData.vehicle_id);
                    return vehicle ? (
                      <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                        {vehicle.main_image && (
                          <img
                            src={vehicle.main_image}
                            alt={vehicle.title}
                            className="w-20 h-20 object-cover rounded"
                          />
                        )}
                        <div>
                          <p className="font-medium text-gray-900">{vehicle.title}</p>
                          <p className="text-sm text-gray-500">
                            {vehicle.brand} {vehicle.model} • {vehicle.year}
                          </p>
                          <p className="text-sm font-semibold text-blue-600">
                            R$ {vehicle.price?.toLocaleString("pt-BR")}
                          </p>
                        </div>
                      </div>
                    ) : null;
                  })()}
                </div>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="bg-white shadow rounded-lg p-6 space-y-6">
              {/* Title */}
              <div>
                <label
                  htmlFor="title"
                  className="block text-sm font-medium text-gray-700"
                >
                  Título do Anúncio *
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  required
                  maxLength={500}
                  value={formData.title || ""}
                  onChange={handleChange}
                  placeholder="Ex: Honda Civic 2021 - Impecável!"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  {formData.title?.length || 0}/500 caracteres
                </p>
              </div>

              {/* Headline */}
              <div>
                <label
                  htmlFor="headline"
                  className="block text-sm font-medium text-gray-700"
                >
                  Manchete
                </label>
                <input
                  type="text"
                  id="headline"
                  name="headline"
                  maxLength={255}
                  value={formData.headline || ""}
                  onChange={handleChange}
                  placeholder="Ex: Oferta Imperdível!"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Texto curto e impactante para chamar atenção
                </p>
              </div>

              {/* Description */}
              <div>
                <label
                  htmlFor="description"
                  className="block text-sm font-medium text-gray-700"
                >
                  Descrição
                </label>
                <textarea
                  id="description"
                  name="description"
                  rows={4}
                  value={formData.description || ""}
                  onChange={handleChange}
                  placeholder="Descreva os principais diferenciais do veículo..."
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
              </div>

              {/* Call to Action */}
              <div>
                <label
                  htmlFor="call_to_action"
                  className="block text-sm font-medium text-gray-700"
                >
                  Call to Action (CTA)
                </label>
                <input
                  type="text"
                  id="call_to_action"
                  name="call_to_action"
                  maxLength={100}
                  value={formData.call_to_action || ""}
                  onChange={handleChange}
                  placeholder="Ex: Agendar Test-Drive"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Texto para o botão de ação
                </p>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="bg-white shadow rounded-lg p-6 space-y-6">
              {/* Daily Budget */}
              <div>
                <label
                  htmlFor="budget_daily"
                  className="block text-sm font-medium text-gray-700"
                >
                  Orçamento Diário (R$)
                </label>
                <input
                  type="number"
                  id="budget_daily"
                  name="budget_daily"
                  min="0"
                  step="0.01"
                  value={formData.budget_daily || ""}
                  onChange={handleNumberChange}
                  placeholder="50.00"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Valor máximo a ser gasto por dia
                </p>
              </div>

              {/* Total Budget */}
              <div>
                <label
                  htmlFor="budget_total"
                  className="block text-sm font-medium text-gray-700"
                >
                  Orçamento Total (R$)
                </label>
                <input
                  type="number"
                  id="budget_total"
                  name="budget_total"
                  min="0"
                  step="0.01"
                  value={formData.budget_total || ""}
                  onChange={handleNumberChange}
                  placeholder="1500.00"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Valor máximo total da campanha
                </p>
              </div>

              {/* Start Date */}
              <div>
                <label
                  htmlFor="start_date"
                  className="block text-sm font-medium text-gray-700"
                >
                  Data de Início
                </label>
                <input
                  type="date"
                  id="start_date"
                  name="start_date"
                  value={formData.start_date || ""}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
              </div>

              {/* End Date */}
              <div>
                <label
                  htmlFor="end_date"
                  className="block text-sm font-medium text-gray-700"
                >
                  Data de Término (Opcional)
                </label>
                <input
                  type="date"
                  id="end_date"
                  name="end_date"
                  value={formData.end_date || ""}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Deixe em branco para campanha contínua
                </p>
              </div>

              {/* Bid Amount */}
              <div>
                <label
                  htmlFor="bid_amount"
                  className="block text-sm font-medium text-gray-700"
                >
                  Lance Máximo (R$)
                </label>
                <input
                  type="number"
                  id="bid_amount"
                  name="bid_amount"
                  min="0"
                  step="0.01"
                  value={formData.bid_amount || ""}
                  onChange={handleNumberChange}
                  placeholder="2.50"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Valor máximo por clique ou impressão
                </p>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-4">
            <button
              type="button"
              onClick={prevStep}
              disabled={step === 1}
              className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Anterior
            </button>

            {step < totalSteps ? (
              <button
                type="button"
                onClick={nextStep}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              >
                Próximo →
              </button>
            ) : (
              <button
                type="submit"
                disabled={loading}
                className="rounded-md bg-green-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Criando..." : "Criar Anúncio"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
