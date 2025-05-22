import flet as ft
import subprocess
import sys
import os
from deepFace.generar import generar as genEmb
from deepFace.validacion import validacion as valEmb

# Paleta de colores renovada
COLORS = {
    "principal": "#E0E1DD",  # Fondo dominante (60%)
    "secundario": "#415A77",  # Elementos principales (30%)
    "oscuro": "#0D1B2A",       # Detalles/accentos (10%)
}

def validacion(e):
    print('here')
    valEmb('sotelo', '0', './requirements.txt', 'pruebaGUI2', 1)    
    

def generar(e):
    print("here")
    genEmb('ahorasi')

def vista_abrir_camara(page):
    page.bgcolor = COLORS["principal"]
    page.clean()
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Abrir cámara para capturar embedding", size=20, color=COLORS["oscuro"]),
                ft.ElevatedButton(
                    "Atras",
                    on_click=lambda _: vista_generar_embedding(page),
                    bgcolor=COLORS["secundario"],
                    color=COLORS["principal"]
                ),
                 ft.ElevatedButton(
                    "Generar embedding",
                    on_click= generar,
                    bgcolor=COLORS["secundario"],
                    color=COLORS["principal"]
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            alignment=ft.alignment.center
        )
    )

def vista_generar_embedding(page):
    page.bgcolor = COLORS["principal"]
    page.clean()
    page.add(
        ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Generar un embedding",
                    on_click=lambda _: vista_abrir_camara(page),
                    bgcolor=COLORS["secundario"],
                    color=COLORS["principal"]
                ),
                ft.ElevatedButton(
                    "Validar un embedding",
                    on_click=lambda _: vista_nombre_embedding(page),
                    bgcolor=COLORS["secundario"],
                    color=COLORS["principal"]
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=15,
            alignment=ft.alignment.center
        )
    )

def vista_nombre_embedding(page):
    page.bgcolor = COLORS["principal"]
    page.clean()
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("Nombre del embedding", size=20, color=COLORS["oscuro"]),
                ft.TextField(label="Nombre", bgcolor=COLORS["secundario"], color=COLORS["principal"]),
                ft.ElevatedButton(
                    "Volver",
                    on_click=lambda _: vista_generar_embedding(page),
                    bgcolor=COLORS["secundario"],
                    color=COLORS["principal"]
                ),
                ft.ElevatedButton(
                    "Verificar",
                    on_click= validacion,
                    bgcolor=COLORS["secundario"],
                    color=COLORS["principal"]
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            alignment=ft.alignment.center
        )
    )

def main(page: ft.Page):
    page.title = "Embeddings App"
    page.window_width = 400
    page.window_height = 300
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    vista_generar_embedding(page)

ft.app(target=main)
