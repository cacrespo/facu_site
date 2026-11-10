#!/usr/bin/env python3
"""
Script de inicio para el sitio de Facu de las Tortas.
Ejecuta: python run.py
"""

import uvicorn

if __name__ == "__main__":
    print("Iniciando servidor para el sitio de Facu de las Tortas...")
    print("Abrí tu navegador en: http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
