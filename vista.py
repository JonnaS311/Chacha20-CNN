import json
import flet as ft
from deepFace.generar import generar as genEmb
from deepFace.validacion import validacion as valEmb

# Paleta de colores renovada
COLORS = {
    "principal": "#E0E1DD",  # Fondo dominante (60%)
    "secundario": "#415A77",  # Elementos principales (30%)
    "oscuro": "#0D1B2A",       # Detalles/accentos (10%)
}


def validacion(e, nombre, modo, ruta, nom_salida, formato, page: ft.Page):
    print(nombre, modo, ruta, nom_salida, formato)
    # valEmb('sotelo', '0', './requirements.txt', 'pruebaGUI2', 1)
    valEmb(nombre, modo, ruta, nom_salida, formato)
    menu_principal(page)


def generar(e, nombre, page: ft.Page):
    print(nombre)
    genEmb(nombre)
    menu_principal(page)


def menu_gen_embedding(page):
    filepath = './deepFace/embedding.json'
    with open(filepath, 'r') as f:
        data = list()
        embeddings = json.load(f)
        for i in embeddings.keys():
            data.append(i)
    page.bgcolor = COLORS["principal"]
    page.clean()
    nombre = ft.TextField(label='Nombre del embedding', color=COLORS['oscuro'], border=ft.InputBorder.UNDERLINE,
                          focused_border_color=COLORS["oscuro"], label_style=ft.TextStyle(color=COLORS['oscuro']))
    page.add(
        ft.Container(
            content=ft.Row(controls=[ft.Column([
                ft.Text("Abrir cámara para capturar embedding",
                        size=20, color=COLORS["oscuro"]),
                nombre,
                ft.ElevatedButton(
                    "Generar embedding",
                    on_click=lambda e: generar(e, nombre.value, page),
                    bgcolor=COLORS["oscuro"],
                    color=COLORS["principal"],
                    width=220
                ),
                ft.ElevatedButton(
                    "Atras",
                    on_click=lambda _: menu_principal(page),
                    bgcolor=COLORS["oscuro"],
                    color=COLORS["principal"],
                    width=120
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                ft.Container(
                content=ft.Text(
                    f'Embeddings cargados: \n {data}', weight=ft.FontWeight.BOLD),
                height=300,  # Altura fija para habilitar el scroll
                bgcolor=COLORS["oscuro"],
                padding=10,
                width=300,
                border_radius=10,
            )

            ]),
            padding=15,
            alignment=ft.alignment.center
        )
    )


def menu_principal(page):
    page.bgcolor = COLORS["principal"]
    page.clean()
    # Cargar contenido del archivo
    archivo = "./deepFace/embedding.json"  # Cambia por el nombre de tu archivo
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
    except Exception as e:
        contenido = f"No se pudo leer el archivo:\n{e}"

    # Definir el área de texto con scrollbar
    area_texto = ft.Text(
        contenido,
        selectable=True,  # Permite seleccionar texto
        size=11,
        color=COLORS['principal'],
    )

    scrollable_container = ft.Container(
        content=ft.Column(
            controls=[ft.Text("Archivo Embedding.json (Rostros almacenados)",
                              color=COLORS["principal"], weight=ft.FontWeight.BOLD), area_texto],
            scroll=ft.ScrollMode.AUTO,  # Scroll vertical automático
        ),
        width=400,   # Ancho fijo
        height=400,  # Alto fijo
        padding=10,
        bgcolor=COLORS['oscuro'],
        border_radius=10,
    )

    page.add(
        ft.Container(
            content=ft.Column([ft.Text('Simulador Embeddings-chacha20 App', color=COLORS["oscuro"], size=20, weight=ft.FontWeight.BOLD),
                               ft.Row([
                                   ft.ElevatedButton(
                                       "Generar un embedding",
                                       on_click=lambda _: menu_gen_embedding(
                                           page),
                                       bgcolor=COLORS["oscuro"],
                                       color=COLORS["principal"],
                                       width=320
                                   ),
                                   ft.ElevatedButton(
                                       "Encriptar/Desencriptar archivo",
                                       on_click=lambda _: menu_encriptacion(
                                           page),
                                       bgcolor=COLORS["oscuro"],
                                       color=COLORS["principal"],
                                       width=320
                                   ),
                                   scrollable_container
                               ], alignment=ft.MainAxisAlignment.CENTER)]),
            padding=15,
            alignment=ft.alignment.center
        )
    )
    page.add(
        ft.Text("Proyecto redes de Comunicación III - Jonnathan Sotelo (20202020040)",
                color=COLORS['oscuro'])
    )


def menu_encriptacion(page):

    def file_chosen(e: ft.FilePickerResultEvent):
        file_name.value = e.files[0].path
        file_name.update()

    def valid_option(e):
        if int(e.control.value) == 1:
            formato.disabled = False
            formato.label_style = ft.TextStyle(color=COLORS['principal'])

        else:
            formato.value = None
            formato.disabled = True
            formato.label_style = ft.TextStyle(color=COLORS['oscuro'])
        formato.update()

    modo_uso = '''
# 😎 ¡Bienvenido a la Validación Facial de Archivos!

¡Hola! Aquí te explico de forma sencilla cómo usar la pantalla de **"Validación del Embedding"** para proteger o acceder a tus archivos usando tu rostro.

## ¿Qué es esto?

Esta pantalla te ayuda a verificar tu identidad con tu rostro para luego poder:

* **🔒 Encriptar:** Ponerle "candado" a un archivo para que solo tú puedas abrirlo.
* **🔓 Desencriptar:** Quitarle el "candado" a un archivo que ya estaba protegido.

## ¡Manos a la obra! Sigue estos pasos:

1.  **👦 Nombre del Embedding de la persona:**
    * Escribe aquí el **nombre exacto** que usaste cuando registraste tu rostro en el sistema. (Ej: `"Carlos López"`).

2.  **Nombre del archivo de salida:**
    * Piensa en un **nombre para el archivo nuevo** que se creará después de protegerlo o abrirlo. (Ej: `"MiDocumentoSecreto"`).

3.  **📄 Botón `Choose files...`:**
    * Haz clic aquí para **elegir el archivo** de tu computadora que quieres proteger (encriptar) o el que ya está protegido y quieres abrir (desencriptar).

4.  **¿Encriptar o Desencriptar?:**
    * **🔒 Encriptar:** Marca esta opción si quieres ponerle "candado" al archivo que elegiste.
    * **🔓 Desencriptar:** Marca esta si quieres quitarle el "candado" a un archivo ya protegido.

5.  **Formato de salida (Ejemplo: mp4, jpg, txt...):**
    * Escribe la **extensión** que tendrá tu archivo final.
        * Si estás *desencriptando*, usa la extensión original (ej: `mp4` para un video, `jpg` para una foto, `txt` para un texto).
        * Si estás *encriptando*, se usará la extención .cka para archivo procesados por el algoritmo chacha20. 

## ¿Listo? ¡A Verificar!

6.  **Botón `Verificar`:**
    * Cuando hayas llenado todo, ¡dale clic!
    * **¡Prepárate para la cámara!** Se encenderá tu cámara web.
    * Mira directamente a la cámara. El sistema comparará tu rostro con el que tienes registrado.
    * **Si te reconoce:** ¡Genial! El sistema hará la operación (encriptar o desencriptar) y guardará el archivo con el nombre y formato que indicaste.
    * **Si no te reconoce:** No te preocupes, no se hará nada con el archivo. Revisa que el nombre esté bien escrito, que haya buena luz y vuelve a intentarlo.

## Otros Botones:

* **Botón `Volver`:** Si quieres regresar a la pantalla anterior o cancelar, usa este botón.

## ¡Unos tips rápidos!

* Para que te reconozca bien, asegúrate de que haya **buena luz** y que tu **cara se vea clara** en la cámara.
* El **nombre del embedding** debe ser idéntico al que usaste al registrarte.

---

¡Así de fácil! Ahora puedes usar tu rostro para mantener tus archivos seguros.
    '''
    file_picker = ft.FilePicker(on_result=file_chosen)
    formato = ft.TextField(label="Formato de salida. Ejemplo: mp4, jpg, txt... (solo para desencriptar)", bgcolor=COLORS["oscuro"],
                           color=COLORS["principal"], disabled=True,  border=ft.InputBorder.UNDERLINE,
                           focused_border_color=COLORS["oscuro"], label_style=ft.TextStyle(color=COLORS['oscuro']))
    nombre = ft.TextField(label="Nombre del Embedding de la persona", bgcolor=COLORS["oscuro"], color=COLORS["principal"],
                          border=ft.InputBorder.UNDERLINE, focused_border_color=COLORS["oscuro"], label_style=ft.TextStyle(color=COLORS['principal']))
    salida = ft.TextField(label="Nombre del archivo de salida", bgcolor=COLORS["oscuro"], color=COLORS["principal"],
                          border=ft.InputBorder.UNDERLINE, focused_border_color=COLORS["oscuro"], label_style=ft.TextStyle(color=COLORS['principal']))
    page.overlay.append(file_picker)
    page.bgcolor = COLORS["principal"]
    page.clean()

    # Controls de flet
    file_name = ft.Text(color=COLORS["oscuro"])
    cg = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="0", label="Encriptar", fill_color=COLORS["oscuro"], label_style=ft.TextStyle(
                    color=COLORS["oscuro"])),
                ft.Radio(value="1", label="Desencriptar", fill_color=COLORS["oscuro"], label_style=ft.TextStyle(
                    color=COLORS["oscuro"])),
            ]
        ),
        on_change=valid_option
    )

    page.add(
        ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Validación del Embedding",
                            size=20, color=COLORS["oscuro"]),
                    nombre,
                    salida,
                    ft.ElevatedButton("Choose files...", icon=ft.Icons.UPLOAD_FILE,
                                      bgcolor=COLORS["oscuro"], color=COLORS["principal"],
                                      on_click=lambda _: file_picker.pick_files(allow_multiple=False)),
                    file_name,
                    cg,
                    formato,
                    ft.Row([
                        ft.ElevatedButton(
                            "Volver",
                            on_click=lambda _: menu_principal(page),
                            bgcolor=COLORS["oscuro"],
                            color=COLORS["principal"],
                            width=120
                        ),
                        ft.ElevatedButton(
                            "Verificar",
                            on_click=lambda e: validacion(
                                e, nombre.value, cg.value, file_name.value, salida.value, formato.value, page),
                            bgcolor=COLORS["oscuro"],
                            color=COLORS["principal"],
                            width=120
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                ft.Container(
                    content=ft.Column(
                        [ft.Markdown(modo_uso, selectable=True,
                                     extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.ADAPTIVE,
                        tight=True,
                        width=550,
                        height=300),
                    bgcolor=COLORS["oscuro"], padding=20, border_radius=10,)

            ]),
            padding=15,
            alignment=ft.alignment.center
        )
    )
    page.update()


def main(page: ft.Page):
    page.title = "Simulador Embeddings-chacha20 App"
    page.window_width = 400
    page.window_height = 300
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    menu_principal(page)


ft.app(target=main)
