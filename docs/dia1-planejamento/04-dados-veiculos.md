# Dados dos Veículos - Estrutura e Especificações

**Data**: 16/03/2026
**Versão**: 1.0

---

## 1. Visão Geral

Este documento define todos os tipos de dados necessários para representar veículos no sistema, incluindo estrutura de banco de dados, validações e integrações.

---

## 2. Estrutura de Dados do Veículo

### 2.1 Dados Básicos (Obrigatórios)

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `id` | UUID | Identificador único do veículo | Auto-generated | `uuid-v4` |
| `revenda_id` | UUID | ID da revenda proprietária | Foreign key | |
| `titulo` | String | Título/do anúncio | 5-100 chars | "Honda Civic Touring 2022" |
| `descricao` | Text | Descrição detalhada | 50-5000 chars | Veículo completo... |
| `marca` | String | Fabricante | Enum ou lista | "Honda" |
| `modelo` | String | Modelo do veículo | Required | "Civic" |
| `versao` | String | Versão/Edição | Required | "Touring Turbo" |
| `ano_fabricacao` | Integer | Ano de fabricação | 1980-Atual | 2022 |
| `ano_modelo` | Integer | Ano do modelo | 1980-Atual+1 | 2023 |
| `cor` | String | Cor predominante | Required | "Branco Pérola" |
| `placa` | String | Placa do veículo | Regex: `[A-Z]{3}\d{4}` | "ABC1234" ou padrão Mercosul |
| `chassi` | String | Número do chassi | 17 chars alfanumérico | "9BWZZZ..." |
| `renavam` | String | Código RENAVAM | 11 dígitos | "12345678901" |
| `created_at` | Timestamp | Data de cadastro | Auto | 2026-03-16 |
| `updated_at` | Timestamp | Última atualização | Auto | 2026-03-16 |
| `status` | Enum | Status do veículo | disponível, vendido, reservado, pendente | "disponível" |

---

### 2.2 Dados Técnicos

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `tipo_veiculo` | Enum | Categoria do veículo | hatch, sedan, suv, pickup, coupe, conversível, minivan, esportivo | "suv" |
| `tipo_combustivel` | Enum[] | Tipo(s) de combustível | gasolina, etanol, flex, diesel, elétrico, híbrido | ["flex"] |
| `motor` | String | Especificação do motor | 2-100 chars | "2.0 Turbo 16V" |
| `potencia` | Decimal | Potência do motor (CV) | 50-800 | 173 |
| `torque` | Decimal | Torque (kgfm) | 5-100 | 22.4 |
| `cilindradas` | Integer | Cilindradas (cc) | 800-8000 | 1998 |
| `cilindros` | Integer | Número de cilindros | 3-16 | 4 |
| `valvulas` | Integer | Válvulas por cilindro | 2-5 | 4 |
| `transmissao` | Enum | Tipo de câmbio | manual, automatico, automatizado, cvt, dct | "automatico" |
| `marchas` | Integer | Número de marchas | 4-10 | 6 |
| `tracao` | Enum | Tipo de tração | dianteira, tras, 4x4, 4x4_todas | "dianteira" |
| `km` | Integer | Quilometragem | 0-500000 | 28500 |
| `portas` | Integer | Número de portas | 2-5 | 4 |
| `lugares` | Integer | Número de lugares | 2-8 | 5 |
| `consumo_urbano` | Decimal | km/l na cidade | 3-30 | 9.5 |
| `consumo_rodoviario` | Decimal | km/l na estrada | 5-45 | 13.2 |
| `tanque` | Integer | Capacidade do tanque (litros) | 20-150 | 50 |
| `portas_mala` | Integer | Capacidade porta-malas (litros) | 100-2000 | 420 |

---

### 2.3 Dados de Segurança

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `airbags` | Enum[] | Localização dos airbags | motorista, passageiro, laterais, cortina | ["motorista", "passageiro", "laterais", "cortina"] |
| `abs` | Boolean | Freios ABS | true/false | true |
| `ebd` | Boolean | Distribuição eletrônica de frenagem | true/false | true |
| `esc` | Boolean | Controle de estabilidade | true/false | true |
| `tc` | Boolean | Controle de tração | true/false | true |
| `freio_estacionamento` | Enum | Tipo de freio de mão | manual, eletrico | "eletrico" |
| `alarme` | Boolean | Sistema de alarme | true/false | true |
| `imobilizador` | Boolean | Imobilizador de motor | true/false | true |
| `controle_pneumatico` | Boolean | Controle de pressão dos pneus | true/false | true |
| `camera_re` | Boolean | Câmera de ré | true/false | true |
| `sensores_estacionamento` | Enum[] | Sensores de estacionamento | frontal, traseiro | ["frontal", "traseiro"] |
| `isofix` | Boolean | Fixação ISOFIX para cadeirinhas | true/false | true |
| `farol_auto` | Boolean | Farol automático | true/false | true |
| `farol_neblina` | Boolean | Farol de neblina | true/false | true |

---

### 2.4 Dados de Conforto e Tecnologia

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `ar_condicionado` | Enum | Tipo de ar condicionado | manual, digital, dual_zone, tri_zone | "digital" |
| `direcao` | Enum | Tipo de direção | mecanica, hidraulica, eletrica, eletroassistida | "eletrica" |
| `vidros` | Enum | Vidros elétricos | nenhum, dianteiros, todos | "todos" |
| `travas` | Enum | Travas elétricas | nenhum, dianteiras, todas | "todas" |
| `bancos` | Enum[] | Tipo dos bancos | comuns, ajustavel_altura, aquecido, ventilado, massagem, couro | ["ajustavel_altura", "couro"] |
| `ajuste_banco_motorista` | Integer | Ajustes do banco motorista | 0-12 | 8 |
| `ajuste_banco_passageiro` | Integer | Ajustes do banco passageiro | 0-12 | 4 |
| `volante` | Enum[] | Ajustes do volante | altura, profundidade | ["altura", "profundidade"] |
| `computador_bordo` | Boolean | Computador de bordo | true/false | true |
| `piloto_automatico` | Boolean | Piloto automático (cruise control) | true/false | true |
| `piloto_adaptativo` | Boolean | Controlador de velocidade adaptativo | true/false | true |
| `sensor_chuva` | Boolean | Sensor de chuva | true/false | true |
| `tachografia_frota` | Boolean | Tachógrafo para frota | true/false | true |

---

### 2.5 Dados de Entretenimento e Conectividade

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `tela_central` | Boolean | Tela central multimídia | true/false | true |
| `tamanho_tela` | Decimal | Tamanho da tela (polegadas) | 0-15 | 8.0 |
| `android_auto` | Boolean | Android Auto | true/false | true |
| `apple_carplay` | Boolean | Apple CarPlay | true/false | true |
| `mirrorlink` | Boolean | MirrorLink | true/false | false |
| `gps_nativo` | Boolean | GPS integrado | true/false | true |
| `bluetooth` | Boolean | Bluetooth | true/false | true |
| `radio` | Enum | Tipo de rádio | am_fm, cd, mp3, digital, sem | "am_fm" |
| `usb` | Integer | Portas USB | 0-4 | 2 |
| `sd_card` | Boolean | Leitor de cartão SD | true/false | true |
| `entrada_auxiliar` | Boolean | Entrada auxiliar (P2) | true/false | true |
| `carregador_wireless` | Boolean | Carregador sem fio | true/false | true |
| `wifi` | Boolean | Wi-Fi integrado | true/false | true |
| `sound_system` | String | Sistema de som premium | 2-100 chars | "Bose Premium Sound System" |
| `alto_falantes` | Integer | Número de alto-falantes | 0-20 | 8 |
| `subwoofer` | Boolean | Subwoofer | true/false | true |

---

### 2.6 Dados de Mercado e Venda

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `preco_fipe` | Decimal | Preço tabela FIPE | 0-1000000 | 105000.00 |
| `preco_fipe_data` | Date | Data da consulta FIPE | YYYY-MM-DD | "2026-03-16" |
| `preco_venda` | Decimal | Preço de venda | 0-1000000 | 115000.00 |
| `preco_promocional` | Decimal | Preço promocional (opcional) | 0-1000000 | 108000.00 |
| `desconto_maximo` | Decimal | Desconto máximo negociável | 0-1000000 | 5000.00 |
| `entrada_minima` | Decimal | Entrada mínima para financiamento | 0-1000000 | 15000.00 |
| `parcela_maxima` | Integer | Número máximo de parcelas | 0-84 | 60 |
| `taxa_juros` | Decimal | Taxa de juros informada | 0-30 | 1.99 |
| `aceita_troca` | Boolean | Aceita troca de veículo | true/false | true |
| `financiamento_proprio` | Boolean | Financiamento próprio da loja | true/false | true |
| `garantia_fabrica` | Boolean | Ainda na garantia de fábrica | true/false | true |
| `garantia_loja` | Boolean | Garantia da revenda | true/false | true |
| `garantia_meses` | Integer | Meses de garantia loja | 0-36 | 12 |
| `garantia_km` | Integer | Quilometragem da garantia | 0-100000 | 50000 |
| `ipva_pago` | Boolean | IPVA do ano pago | true/false | true |
| `multas` | Boolean | Possui multas em aberto | true/false | false |
| `licenciado_ate` | Date | Licenciamento válido até | YYYY-MM-DD | "2026-03-30" |
| `veiculo_unico_dono` | Boolean | Único dono | true/false | true |
| `veiculo_nunca_batido` | Boolean | Nunca foi batido | true/false | true |
| `todas_revisoes_agenda` | Boolean | Todas revisões em concessionária | true/false | true |
| `manual_proprio` | Boolean | Manual do proprietário | true/false | true |
| `chave_reserva` | Boolean | Chave reserva | true/false | true |

---

### 2.7 Dados Visuais (Mídias)

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `fotos` | Array | Lista de fotos do veículo | JSON array | [Foto Object] |
| `foto_principal` | String | URL da foto principal | Required | "https://..." |
| `video` | String | URL do vídeo do veículo (opcional) | URL válida | "https://youtube.com/..." |
| `video360` | String | URL tour 360° (opcional) | URL válida | "https://..." |
| `galeria_interna` | Array | Fotos do interior | JSON array | [Foto Object] |
| `galeria_externa` | Array | Fotos do exterior | JSON array | [Foto Object] |
| `galeria_mecanica` | Array | Fotos do motor/mecânica | JSON array | [Foto Object] |

**Objeto Foto**:
```json
{
  "url": "https://cdn.revenda.com/veiculo/123/foto1.jpg",
  "url_thumbnail": "https://cdn.revenda.com/veiculo/123/foto1-thumb.jpg",
  "ordem": 1,
  "tipo": "externa", // externa, interna, mecanica
  "descricao": "Vista frontal do veículo",
  "tags": ["frontal", "perfil", "traseira", "interior", "motor"],
  "upload_date": "2026-03-16T10:30:00Z"
}
```

---

### 2.8 Dados de Histórico e Documentação

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `historico_manutencao` | Array | Histórico de manutenções | JSON array | [Manutenção Object] |
| `historico_proprietarios` | Integer | Número de proprietários anteriores | 0-20 | 1 |
| `uf_placa` | String | Estado de emplacamento | 2 letras UF | "SP" |
| `cidade_placa` | String | Cidade de emplacamento | 2-100 chars | "São Paulo" |
| `blindado` | Boolean | Veículo blindado | true/false | false |
| `nível_blindagem` | Enum | Nível de blindagem | nivel_IIA, nivel_II, nivel_III | null |
| `pneu_fabrica` | Boolean | Pneus de fábrica | true/false | false |
| `kit_gas` | Boolean | Possui kit GNV | true/false | false |
| `adaptado_deficiente` | Boolean | Adaptado para PCD | true/false | false |
| `adaptado_gasolina` | Boolean | Adaptado para gasolina (era álcool) | true/false | false |
| `remarcado` | Boolean | Veículo remarcado | true/false | false |
| `sinistro_seguro` | Boolean | Já sofreu sinistro com seguro | true/false | false |
| `aliennacao` | Boolean | Veículo alienado | true/false | false |
| `reservado_dominio` | Boolean | Reservado domínio | true/false | false |
| `arrendado` | Boolean | Veículo arrendado | true/false | false |

**Objeto Manutenção**:
```json
{
  "data": "2025-08-15",
  "tipo": "revisao_periodica", // revisao_periodica, corretiva, preventiva
  "descricao": "Revisão de 30.000km",
  "km": 30000,
  "concessionaria": "Honda Center São Paulo",
  "valor": 1200.00,
  "comprovante_url": "https://..."
}
```

---

### 2.9 Dados de Localização

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `localizacao_disponivel` | String | Cidade onde veículo está disponível | 2-100 chars | "São Paulo, SP" |
| `latitude` | Decimal | Latitude para mapa | -90 to 90 | -23.5505 |
| `longitude` | Decimal | Longitude para mapa | -180 to 180 | -46.6333 |
| `entrega_estados` | Array[] | Estados para entrega | Lista de UFs | ["SP", "RJ", "MG"] |
| `frete_gratis` | Boolean | Frete grátis | true/false | true |
| `taxa_entrega` | Decimal | Taxa de entrega (cobrada) | 0-5000 | 500.00 |

---

### 2.10 Dados de Análise IA (Calculados)

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `score_atratividade` | Integer | Score de atratividade (0-100) | 0-100 | 87 |
| `score_preco` | Integer | Score do preço (0-100) | 0-100 | 72 |
| `score_mercado` | Integer | Score de mercado (0-100) | 0-100 | 91 |
| `preco_sugerido` | Decimal | Preço sugerido pela IA | 0-1000000 | 112500.00 |
| `prob_venda_30d` | Decimal | Probabilidade de venda em 30 dias | 0.0-1.0 | 0.68 |
| `prob_venda_60d` | Decimal | Probabilidade de venda em 60 dias | 0.0-1.0 | 0.84 |
| `palavras_chave_sugeridas` | Array[] | Keywords para anúncios | Lista de strings | ["honda civic", "sedan esportivo", "turbo"] |
| `copy_sugerida` | Object | Copy sugerida para anúncios | Object | ver abaixo |
| `pontos_venda` | Array[] | Principais pontos de venda | Lista de strings | ["Motor turbo potente", "Tecnologia de ponta"] |
| `pontos_melhoria` | Array[] | Sugestões de melhoria | Lista de strings | ["Fotos com mais iluminação"] |

**Objeto Copy Sugerida**:
```json
{
  "headline": "Honda Civic Touring 2022 - Potência e Tecnologia",
  "descricao": "Experimente o prazer de dirigir um Civic Touring Turbo. Motor 2.0 de 173cv, câmbio automático CVT com paddle shifts, teto solar panorâmico e sistema de som premium. Único dono, 28.500km, documentação impecável.",
  "cta": "Agende seu Test Drive",
  "hashtags": ["#HondaCivic #CivicTouring #CarrosUsados #SaoPaulo"]
}
```

---

### 2.11 Dados de Performance nos Anúncios

| Campo | Tipo | Descrição | Validação | Exemplo |
|-------|------|-----------|-----------|---------|
| `campanhas_ativas` | Integer | Número de campanhas ativas | 0+ | 3 |
| `total_impressoes` | Integer | Total de impressões | 0+ | 45230 |
| `total_cliques` | Integer | Total de cliques | 0+ | 1247 |
| `ctr_medio` | Decimal | CTR médio | 0.0-1.0 | 0.0276 |
| `total_leads` | Integer | Leads gerados | 0+ | 45 |
| `conversao` | Decimal | Taxa de conversão | 0.0-1.0 | 0.0361 |
| `cpc_medio` | Decimal | CPC médio (R$) | 0+ | 2.45 |
| `cpl_medio` | Decimal | CPL médio (R$) | 0+ | 68.12 |
| `custo_total` | Decimal | Custo total em campanhas | 0+ | 3065.40 |
| `primeira_exibicao` | Timestamp | Data da primeira exibição | Timestamp | "2026-02-15T10:00:00Z" |
| `ultima_exibicao` | Timestamp | Data da última exibição | Timestamp | "2026-03-16T09:30:00Z" |

---

## 3. Validações e Regras de Negócio

### 3.1 Validações Obrigatórias

**Para Cadastro Básico**:
- [x] Marca, modelo, versão
- [x] Ano de fabricação e modelo
- [x] Preço de venda
- [x] Tipo de veículo
- [x] Tipo de combustível
- [x] Quilometragem
- [x] Cor
- [x] Placa
- [x] Mínimo de 5 fotos

**Para Publicação de Anúncio**:
- [x] Todos os campos básicos
- [x] Mínimo de 10 fotos
- [x] Descrição completa
- [x] Dados de contato da revenda
- [x] Localização

---

### 3.2 Regras de Negócio

**Preço**:
- Preço de venda deve estar entre 70% e 150% da FIPE
- Se fora dessa faixa, exigir justificativa
- Alerta se preço > 130% da FIPE

**Quilometragem**:
- KM deve ser coerente com o ano (média 15.000km/ano)
- Alerta se km > 25.000km/ano
- Alerta se km < 5.000km/ano (possível odometro alterado)

**Ano**:
- Ano modelo ≥ Ano fabricação
- Ano modelo ≤ Ano fabricação + 1

**Documentação**:
- Placa deve ser válida (formato antigo ou Mercosul)
- Chassi deve ter 17 caracteres alfanuméricos
- RENAVAM deve ter 11 dígitos

**Fotos**:
- Mínimo 5 fotos para cadastro
- Mínimo 10 fotos para anúncio
- Peso máximo: 10MB por foto
- Formatos aceitos: JPG, PNG, WEBP
- Resolução mínima: 800x600
- Resolução recomendada: 1920x1080

---

## 4. Integrações Externas

### 4.1 Tabela FIPE

**Endpoint**: `https://brasilapi.com.br/api/fipe/precos/v1/{codigo_fipe}`

**Uso**:
- Consulta preço médio de mercado
- Atualização diária dos valores
- Histórico de preços

**Campos Mapeados**:
- `valor` → `preco_fipe`
- `codigo_fipe` → armazenar para referência

---

### 4.2 Consulta de Débitos (Detran)

**Endpoint**: Vários serviços (Detran SP, etc.)

**Verifica**:
- Multas em aberto
- IPVA pendente
- Veículo roubado/furtado
- Bloqueios jurídicos

---

### 4.3 Consulta de Recall

**Endpoint**: APIs de montadoras ou terceiros

**Verifica**:
- Recalls pendentes
- Campanhas de serviço
- Atualizações de software

---

## 5. Schema do Banco de Dados (PostgreSQL)

```sql
CREATE TABLE veiculos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    revenda_id UUID NOT NULL REFERENCES revendas(id),

    -- Dados Básicos
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    versao VARCHAR(100) NOT NULL,
    ano_fabricacao INTEGER NOT NULL,
    ano_modelo INTEGER NOT NULL,
    cor VARCHAR(50) NOT NULL,
    placa VARCHAR(8) NOT NULL UNIQUE,
    chassi VARCHAR(17) NOT NULL UNIQUE,
    renavam VARCHAR(11) NOT NULL UNIQUE,

    -- Dados Técnicos
    tipo_veiculo VARCHAR(20) NOT NULL,
    tipo_combustivel VARCHAR[] NOT NULL,
    motor VARCHAR(100),
    potencia DECIMAL(5,1),
    torque DECIMAL(5,1),
    cilindradas INTEGER,
    cilindros INTEGER,
    valvulas INTEGER,
    transmissao VARCHAR(20),
    marchas INTEGER,
    tracao VARCHAR(20),
    km INTEGER NOT NULL,
    portas INTEGER,
    lugares INTEGER,
    consumo_urbano DECIMAL(4,1),
    consumo_rodoviario DECIMAL(4,1),
    tanque INTEGER,
    porta_mala INTEGER,

    -- Dados de Mercado
    preco_fipe DECIMAL(10,2),
    preco_fipe_data DATE,
    preco_venda DECIMAL(10,2) NOT NULL,
    preco_promocional DECIMAL(10,2),
    desconto_maximo DECIMAL(10,2),
    entrada_minima DECIMAL(10,2),
    parcela_maxima INTEGER,
    taxa_juros DECIMAL(5,2),

    -- Flags de Venda
    aceita_troca BOOLEAN DEFAULT false,
    financiamento_proprio BOOLEAN DEFAULT false,
    garantia_fabrica BOOLEAN DEFAULT false,
    garantia_loja BOOLEAN DEFAULT false,
    garantia_meses INTEGER,
    garantia_km INTEGER,
    ipva_pago BOOLEAN DEFAULT false,
    multas BOOLEAN DEFAULT false,
    veiculo_unico_dono BOOLEAN DEFAULT false,
    veiculo_nunca_batido BOOLEAN DEFAULT false,

    -- Histórico
    historico_proprietarios INTEGER DEFAULT 1,
    uf_placa CHAR(2),
    blindado BOOLEAN DEFAULT false,

    -- Localização
    localizacao_disponivel VARCHAR(100),

    -- Mídia
    foto_principal TEXT NOT NULL,
    fotos JSONB DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(20) DEFAULT 'disponivel',

    -- Dados de Análise IA
    score_atratividade INTEGER,
    score_preco INTEGER,
    score_mercado INTEGER,
    preco_sugerido DECIMAL(10,2),
    prob_venda_30d DECIMAL(3,2),
    prob_venda_60d DECIMAL(3,2),
    copy_sugerida JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_anomodelo CHECK (ano_modelo >= ano_fabricacao AND ano_modelo <= ano_fabricacao + 1),
    CONSTRAINT chk_km CHECK (km >= 0),
    CONSTRAINT chk_preco CHECK (preco_venda > 0)
);

CREATE INDEX idx_veiculos_revenda ON veiculos(revenda_id);
CREATE INDEX idx_veiculos_marca_modelo ON veiculos(marca, modelo);
CREATE INDEX idx_veiculos_preco ON veiculos(preco_venda);
CREATE INDEX idx_veiculos_ano ON veiculos(ano_modelo);
CREATE INDEX idx_veiculos_status ON veiculos(status);
CREATE INDEX idx_veiculos_kmpg ON veiculos(km, ano_fabricacao);

-- Tabela de fotos detalhadas
CREATE TABLE veiculo_fotos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    url_thumbnail TEXT,
    ordem INTEGER DEFAULT 0,
    tipo VARCHAR(20),
    descricao VARCHAR(200),
    tags TEXT[],
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fotos_veiculo ON veiculo_fotos(veiculo_id);

-- Tabela de histórico de manutenção
CREATE TABLE veiculo_manutencao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    tipo VARCHAR(30),
    descricao TEXT,
    km INTEGER,
    concessionaria VARCHAR(100),
    valor DECIMAL(10,2),
    comprovante_url TEXT
);

CREATE INDEX idx_manutencao_veiculo ON veiculo_manutencao(veiculo_id);
```

---

## 6. API Endpoints

### 6.1 CRUD Básico

```
GET    /api/veiculos                - Listar veículos (com filtros)
GET    /api/veiculos/:id            - Obter veículo específico
POST   /api/veiculos                - Criar novo veículo
PUT    /api/veiculos/:id            - Atualizar veículo
DELETE /api/veiculos/:id            - Deletar veículo (soft delete)
```

### 6.2 Endpoints Especiais

```
POST   /api/veiculos/:id/fotos      - Upload de fotos
GET    /api/veiculos/:id/analise    - Análise IA do veículo
GET    /api/veiculos/:id/sugerir    - Sugestões de melhoria
GET    /api/veiculos/similares/:id  - Veículos similares
GET    /api/veiculos/busca          - Busca avançada
GET    /api/veiculos/exportar       - Exportar para CSV/Excel
```

---

## 7. Exemplo de Payload Completo

```json
{
  "revenda_id": "uuid-da-revenda",
  "titulo": "Honda Civic Touring 2022 Turbo - Único Dono",
  "descricao": "Honda Civic Touring 2022/2023, motor 2.0 Turbo de 173cv, câmbio CVT com paddle shifts. Único dono, 28.500km, todos os opcionais. Teto solar, sistema de som premium, bancos em couro, sensor de fadiga, keyless, start/stop, faróis FULL LED. Documentação impecável, IPVA 2026 pago, revisões em dia na concessionária. Aceita troca e financiamento.",
  "marca": "Honda",
  "modelo": "Civic",
  "versao": "Touring Turbo 2.0 16V 4p Aut.",
  "ano_fabricacao": 2022,
  "ano_modelo": 2023,
  "cor": "Branco Pérola",
  "placa": "ABC1I234",
  "chassi": "9BWZZZ...",
  "renavam": "12345678901",

  "tipo_veiculo": "sedan",
  "tipo_combustivel": ["gasolina"],
  "motor": "2.0 Turbo 16V DOHC i-VTEC",
  "potencia": 173,
  "torque": 22.4,
  "cilindradas": 1998,
  "cilindros": 4,
  "valvulas": 16,
  "transmissao": "automatico",
  "marchas": 7,
  "tracao": "dianteira",
  "km": 28500,
  "portas": 4,
  "lugares": 5,
  "consumo_urbano": 9.5,
  "consumo_rodoviario": 13.2,
  "tanque": 47,

  "preco_fipe": 105000.00,
  "preco_fipe_data": "2026-03-16",
  "preco_venda": 115000.00,
  "desconto_maximo": 3000.00,
  "entrada_minima": 15000.00,
  "parcela_maxima": 60,

  "aceita_troca": true,
  "financiamento_proprio": true,
  "garantia_fabrica": true,
  "garantia_loja": true,
  "garantia_meses": 12,
  "garantia_km": 50000,
  "ipva_pago": true,
  "veiculo_unico_dono": true,
  "veiculo_nunca_batido": true,
  "todas_revisoes_agenda": true,

  "localizacao_disponivel": "São Paulo, SP",
  "uf_placa": "SP",
  "historico_proprietarios": 1,

  "fotos": [
    {
      "url": "https://cdn.revenda.com/civic/001.jpg",
      "tipo": "externa",
      "descricao": "Vista frontal",
      "ordem": 1
    }
  ]
}
```

---

**Próximo Documento**: [05-metricas-sucesso.md](./05-metricas-sucesso.md)
