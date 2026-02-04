# IA Marketing Project - Documentación Completa

## 🎯 Propósito del Proyecto

El **IA Marketing Project** es un sistema inteligente de automatización de marketing basado en agentes de IA que integra Odoo 19 con tecnologías de LLM (Large Language Models) como OpenAI GPT-4 y bases de datos vectoriales. El proyecto permite gestionar estrategias de marketing, indexarlas en una base de datos vectorial (ChromaDB) y generar respuestas inteligentes basadas en RAG (Retrieval-Augmented Generation) para consultas de marketing en tiempo real.

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN (UI)                     │
│                      Odoo 19 Interface                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              CAPA DE NEGOCIO (Models + Tools)                    │
│                                                                  │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │ MarketingKnowledge│      │ VectorStoreTool  │                │
│  │ - name           │      │ - Embeddings     │                │
│  │ - content        │      │ - Persistencia   │                │
│  │ - category       │      │ - Sincronización │                │
│  │ - is_indexed     │      └──────────────────┘                │
│  └──────────────────┘                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│         CAPA DE ORQUESTACIÓN (LangGraph Agent)                  │
│                   marketing_graph.py                             │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐  │
│  │  Nodo RETRIEVE  │───▶│  Nodo GENERATE  │───▶│   OUTPUT   │  │
│  │ (Búsqueda RAG)  │    │  (LLM Response) │    │  (Respuesta)  │
│  └─────────────────┘    └─────────────────┘    └────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│             CAPA DE DATOS Y SERVICIOS EXTERNOS                   │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   ChromaDB VectorDB   │    │  OpenAI API      │                  │
│  │  (Almacenamiento)  │    │  (GPT-4, Embeddings)                  │
│  └──────────────────┘    └──────────────────┘                  │
│         (Persistencia)           (Procesamiento)                │
└────────────────────────────────────────────────────────────────┘
```

## 📦 Estructura de Carpetas

```
IA_Marketing_Project/
│
├── custom_addons/
│   └── marketing_ai_agent/                 # Módulo principal de Odoo
│       ├── __init__.py                     # Punto de entrada
│       ├── __manifest__.py                 # Metadatos del módulo
│       │
│       ├── models/
│       │   └── marketing_knowledge.py       # Modelo de datos
│       │
│       ├── tools/
│       │   └── vector_store_tool.py         # Herramienta de sincronización vectorial
│       │
│       └── engine/
│           └── marketing_graph.py           # Grafo LangGraph del agente IA
│
├── odoo/                                   # Instalación de Odoo 19
│   ├── addons/                             # Módulos nativos de Odoo
│   ├── setup.py
│   └── odoo-bin                            # Ejecutable principal
│
├── odoo.conf/
│   └── odoo.conf                           # Configuración de Odoo
│
├── .env                                    # Variables de entorno (API keys)
├── .gitignore                              # Archivo de exclusión git
└── IA_MARKETING_PROJECT.md                 # Este documento

```

## 🔧 Componentes Principales

### 1. **Modelo de Datos: MarketingKnowledge**
**Archivo:** `models/marketing_knowledge.py`

Es el modelo Odoo que almacena todo el conocimiento de marketing que será indexado en la base vectorial.

**Campos:**
- `name` (Char): Título del documento de marketing
- `content` (Text): Contenido completo del documento
- `category` (Selection): Tipo de información
  - `strategy`: Estrategias de marketing
  - `product`: Información de productos
  - `competitor`: Análisis de competencia
- `is_indexed` (Boolean): Indica si fue sincronizado a la base vectorial

**Función Principal:**
- `action_sync_to_vector_db()`: Sincroniza los registros a ChromaDB

### 2. **Herramienta de Almacenamiento Vectorial**
**Archivo:** `tools/vector_store_tool.py`

Gestiona la sincronización entre Odoo y ChromaDB.

**Función Principal:**
```python
sync_odoo_to_chroma(odoo_records)
```
- Convierte documentos de Odoo en embeddings de OpenAI
- Almacena los embeddings en ChromaDB de forma persistente
- Mantiene metadatos (origen, ID, categoría)

**Características:**
- Usa `text-embedding-3-small` de OpenAI para vectorización eficiente
- Almacena datos persistentemente en `~/IA_Marketing_Project/chroma_db`
- Permite búsquedas semánticas de documentos

### 3. **Motor de IA - LangGraph Workflow**
**Archivo:** `engine/marketing_graph.py`

Es el cerebro del sistema. Implementa un flujo de RAG (Retrieval-Augmented Generation) usando LangGraph.

**Estado Compartido (AgentState):**
```
{
  question: str     # Pregunta del usuario
  context: str      # Documentos recuperados
  answer: str       # Respuesta generada
}
```

**Nodos del Grafo:**

1. **RETRIEVE (Recuperación)**
   - Búsqueda semántica en ChromaDB
   - Retorna los 2 documentos más relevantes
   - Contextualiza la búsqueda

2. **GENERATE (Generación)**
   - Usa GPT-4 con temperatura 0 (determinístico)
   - Prompting con contexto de marketing
   - Genera respuesta fundamentada en los datos

**Flujo de Ejecución:**
```
START ──▶ RETRIEVE ──▶ GENERATE ──▶ END
```

### 4. **Configuración de Odoo**
**Archivo:** `odoo.conf/odoo.conf`

Configuración específica del servidor Odoo:
- Rutas de módulos (nativos + custom)
- Credenciales de base de datos
- Timeouts para procesos largos de IA (1200s CPU, 2400s real)
- Puerto XML-RPC: 8069

## 🔄 Flujo de Datos Completo

```
1. USUARIO EN ODOO
   │
   └──▶ Crea documento en marketing.knowledge
       (categoría: estrategia/producto/competencia)
       │
       └──▶ SINCRONIZACIÓN
           │
           ├─ Documento se envía a vector_store_tool
           │
           ├─ Se genera embedding con OpenAI
           │
           └─ Se almacena en ChromaDB con metadatos
              │
              └──▶ CONSULTA DE IA
                  │
                  ├─ Usuario hace pregunta
                  │
                  ├─ marketing_graph ejecuta:
                  │
                  │  1. RETRIEVE: Busca documentos similares
                  │     └─ ChromaDB retorna top 2 matches
                  │
                  │  2. GENERATE: Genera respuesta
                  │     └─ GPT-4 contextualizando con docs
                  │
                  └─ RESPUESTA GENERADA
                     └─ Entrega al usuario en Odoo
```

## 🚀 Flujos de Trabajo

### Workflow 1: Ingesta de Conocimiento
```
Documento Marketing (Odoo)
    ↓
[MarketingKnowledge Model]
    ↓
[vector_store_tool.sync_odoo_to_chroma()]
    ↓
[OpenAI Embeddings Generation]
    ↓
[ChromaDB Persistence]
    ↓
Listo para búsquedas semánticas
```

### Workflow 2: Consulta Inteligente
```
Pregunta de Usuario
    ↓
[marketing_graph.retrieve_knowledge()]
    ├─ Query en ChromaDB
    └─ Retorna documentos similares
    ↓
[marketing_graph.generate_response()]
    ├─ Construcción de prompt con contexto
    └─ Llamada a GPT-4
    ↓
Respuesta Contextualizada
```

## 💾 Dependencias de Integración

### Python Packages
- **odoo**: Framework ERP
- **langchain**: Abstraer LLMs y herramientas
- **langgraph**: Orquestación de flujos de agentes
- **langchain-openai**: Integración con OpenAI
- **langchain-chroma**: Integración con ChromaDB
- **chroma-db**: Base de datos vectorial
- **python-dotenv**: Gestión de variables de entorno

### Servicios Externos
- **OpenAI API**:
  - `text-embedding-3-small`: Generación de embeddings
  - `gpt-4o`: Generación de respuestas
- **ChromaDB**: Base de datos vectorial local (persistente)

## 🔐 Configuración de Seguridad

### Variables de Entorno (.env)
```
OPENAI_API_KEY=sk-...     # API Key de OpenAI (SENSIBLE)
```

### Exclusiones Git (.gitignore)
```
odoo/                      # No trackear la instalación de Odoo
.env                       # No trackear credenciales
```

## 📊 Casos de Uso

### 1. **Asistente de Estrategia Marketing**
- Usuario ingresa estrategias en `marketing.knowledge`
- IA responde preguntas sobre tácticas y mejores prácticas
- Retorna respuestas contextualizadas basadas en documentos almacenados

### 2. **Análisis Competitivo Automático**
- Documentos sobre competidores indexados
- Consultas sobre posicionamiento vs competencia
- Respuestas fundamentadas en datos específicos

### 3. **Generador de Propuestas de Campaña**
- Información de productos + estrategias
- IA sugiere campañas basadas en combinaciones de documentos
- Mantiene coherencia con historial de marketing

### 4. **Base de Conocimiento Inteligente**
- Toda la documentación de marketing búsquedable
- No requiere keywords exactos (búsqueda semántica)
- Mejora con el tiempo (más documentos = mejores respuestas)

## 🔌 Puntos de Extensión Futuros

1. **Modelos adicionales:**
   - `marketing.campaign` (campañas automatizadas)
   - `marketing.lead_scoring` (puntuación de leads con IA)
   - `marketing.email_template` (plantillas generadas por IA)

2. **Tools adicionales:**
   - Web scraping para análisis competitivo
   - Integración con Google Analytics
   - Procesamiento de audio/video

3. **Nodos adicionales en LangGraph:**
   - Validación de respuestas
   - Ranking de calidad
   - Retroalimentación del usuario
   - Multi-turno conversacional

4. **Bases de datos:**
   - PostgreSQL para escalabilidad
   - Redis para caché
   - ElasticSearch para búsqueda híbrida

## 🎓 Prompt para Otra IA

*Use este prompt si quiere que otra IA continúe desarrollando o manteniendo este proyecto:*

---

**CONTEXTO DEL PROYECTO:**

Este es un sistema de IA integrado en Odoo 19 que combina:
- **Backend**: Odoo 19 con modelo `marketing.knowledge`
- **Orquestación**: LangGraph para flujos de agentes
- **Vectorización**: ChromaDB + OpenAI Embeddings
- **Generación**: GPT-4 para respuestas contextualizadas

**ARQUITECTURA:**
1. Usuarios crean documentos en modelo MarketingKnowledge (Odoo)
2. Herramienta `vector_store_tool` sincroniza a ChromaDB con embeddings
3. LangGraph ejecuta 2 nodos: RETRIEVE (búsqueda) + GENERATE (respuesta)
4. Respuestas RAG entregadas al usuario

**ARCHIVOS CLAVE:**
- `models/marketing_knowledge.py`: Modelo de datos
- `tools/vector_store_tool.py`: Sincronización vectorial
- `engine/marketing_graph.py`: Flujo RAG con LangGraph

**PARA CONTINUAR:**
[Inserte aquí la tarea específica que desea que continúe la otra IA]

---

## 📝 Notas Técnicas

- **Temperatura de LLM**: 0 (respuestas determinísticas)
- **Modelo de embeddings**: text-embedding-3-small (eficiente)
- **Modelo de generación**: gpt-4o (más capaz)
- **K-neighbors en búsqueda**: 2 documentos por consulta
- **Persistencia**: ~/IA_Marketing_Project/chroma_db
- **Colección ChromaDB**: marketing_strategies

## 🛠️ Requisitos del Sistema

- Python 3.8+
- Odoo 19
- Acceso a OpenAI API
- 5GB+ espacio en disco (para chroma_db y Odoo)
- 4GB+ RAM (recomendado)

## 📞 Resumen Ejecutivo

El **IA Marketing Project** es una solución empresarial que democratiza el acceso a inteligencia de marketing mediante:

1. **Centralización**: Toda la estrategia en un modelo único (Odoo)
2. **Inteligencia**: Búsqueda semántica vs búsqueda por keywords
3. **Escalabilidad**: Crece con cada documento agregado
4. **Automatización**: Reduce análisis manual de marketing
5. **Integración**: Nativa en Odoo para equipos de marketing existentes

**Valor único**: RAG en tiempo real para marketing, sin necesidad de reentrenamiento.
