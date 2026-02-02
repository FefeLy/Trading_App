# Trading Analysis App v1.0

## Qué es
Plataforma de análisis de trading manual.
Genera señales, riesgo y métricas. No ejecuta trades.

## Qué NO es
- No es bot
- No abre operaciones
- No conecta a brokers para ejecutar

## Arquitectura
app/
- api        → endpoints HTTP
- data       → carga de datos (Binance)
- features   → indicadores
- models     → ML / dataset
- signals    → BUY / SELL / HOLD
- risk       → gestión de riesgo
- services   → orquestación
- journal    → disciplina y equity real

## Flujo principal
data → features → models → signals → risk → checklist → journal

## Cómo correr
uvicorn app.main:app --reload
