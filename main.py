import os
import re
import io
import urllib.request
import threading
import yt_dlp
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

# LIBRERÍAS DE AUDIO Y METADATOS
from pydub import AudioSegment
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC, TDRC
from mutagen.mp3 import MP3

# 1. Crear las carpetas de trabajo
os.makedirs("downloads", exist_ok=True)
os.makedirs("finished", exist_ok=True)

class regisMakin(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("regisMakin")
        self.geometry("950x650")
        self.configure(fg_color="#312c40")

        self.track_widgets = [] # Guardará referencias a los tiempos y los inputs
        self.duracion_actual = float('inf') 
        
        # Variables para la imagen
        self.cover_original = None
        self.imscale = 1.0

        # --- TOP BAR ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(20, 5))

        self.url_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Ingrese enlace youtube aqui", 
                                      fg_color="white", text_color="black", height=35)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_local_audio = ctk.CTkButton(self.top_frame, text="📁", width=40, height=35, 
                                             fg_color="#e0e0e0", text_color="black", hover_color="#c0c0c0",
                                             command=self.abrir_audio_local)
        self.btn_local_audio.pack(side="right")

        # --- BOTÓN CHECK ---
        self.check_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.check_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.btn_check = ctk.CTkButton(self.check_frame, text="Check", fg_color="#b8e922", 
                                       text_color="black", hover_color="#9acd1c", 
                                       command=self.procesar_check_thread)
        self.btn_check.pack(side="left")

        # --- GRID PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_columnconfigure(2, weight=2)

        # ==========================================
        # COLUMNA 1: ALBUM COVER
        # ==========================================
        self.col_left = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.cover_canvas = tk.Canvas(self.col_left, width=200, height=200, bg="white", highlightthickness=0)
        self.cover_canvas.pack(pady=(0, 10))
        self.cover_canvas.create_text(100, 100, text="album\ncover", font=("Arial", 16), justify="center")
        
        # Bindings de Paneo
        self.cover_canvas.bind("<ButtonPress-1>", lambda e: self.cover_canvas.scan_mark(e.x, e.y))
        self.cover_canvas.bind("<B1-Motion>", lambda e: self.cover_canvas.scan_dragto(e.x, e.y, gain=1))
        # Bindings de Zoom (MouseWheel)
        self.cover_canvas.bind("<MouseWheel>", self.zoom_rueda) # Windows
        self.cover_canvas.bind("<Button-4>", self.zoom_rueda)   # Linux (Scroll Up)
        self.cover_canvas.bind("<Button-5>", self.zoom_rueda)   # Linux (Scroll Down)

        self.btn_local_cover = ctk.CTkButton(self.col_left, text="📁", width=40, fg_color="#e0e0e0", 
                                             text_color="black", command=self.abrir_cover_local)
        self.btn_local_cover.pack(pady=(0, 15))

        ctk.CTkLabel(self.col_left, text="Album:", text_color="white", font=("Arial", 12, "bold")).pack(anchor="w")
        self.entry_album = ctk.CTkEntry(self.col_left, fg_color="white", text_color="black")
        self.entry_album.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.col_left, text="Artista:", text_color="white", font=("Arial", 12, "bold")).pack(anchor="w")
        self.entry_artist = ctk.CTkEntry(self.col_left, fg_color="white", text_color="black")
        self.entry_artist.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.col_left, text="Año:", text_color="white", font=("Arial", 12, "bold")).pack(anchor="w")
        self.entry_year = ctk.CTkEntry(self.col_left, fg_color="white", text_color="black")
        self.entry_year.pack(fill="x", pady=(0, 10))

        # ==========================================
        # COLUMNA 2 Y 3: LISTA Y TIMESTAMPS
        # ==========================================
        self.col_mid = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.col_mid.grid(row=0, column=1, sticky="nsew", padx=10)

        self.track_list_frame = ctk.CTkScrollableFrame(self.col_mid, fg_color="white")
        self.track_list_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.btn_convertir = ctk.CTkButton(self.col_mid, text="CONVERTIR", fg_color="#e5b4c4", 
                                           text_color="#c83040", font=("Arial", 20, "bold"), height=50,
                                           border_width=3, border_color="#c83040", hover_color="#f0c0d0",
                                           command=self.iniciar_conversion)
        self.btn_convertir.pack(fill="x")

        self.col_right = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.col_right.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        self.txt_timestamps = ctk.CTkTextbox(self.col_right, fg_color="white", text_color="gray", font=("Arial", 14))
        self.txt_timestamps.pack(fill="both", expand=True)
        self.txt_timestamps.insert("0.0", "Ingresa las timestamps aqui...")

        # Truco para que el texto gris desaparezca al hacer clic y vuelva si lo dejas vacío
        def focus_in_txt(event):
            if self.txt_timestamps.get("1.0", "end-1c") == "Ingresa las timestamps aqui...":
                self.txt_timestamps.delete("1.0", "end")
                self.txt_timestamps.configure(text_color="black")

        def focus_out_txt(event):
            if not self.txt_timestamps.get("1.0", "end-1c").strip():
                self.txt_timestamps.configure(text_color="gray")
                self.txt_timestamps.insert("0.0", "Ingresa las timestamps aqui...")

        self.txt_timestamps.bind("<FocusIn>", focus_in_txt)
        self.txt_timestamps.bind("<FocusOut>", focus_out_txt)

        # ==========================================
        # BARRA INFERIOR (PROGRESO)
        # ==========================================
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.bottom_frame.pack(fill="x", side="bottom", padx=20, pady=10)

        self.lbl_status = ctk.CTkLabel(self.bottom_frame, text="", text_color="white", width=150, anchor="w")
        self.lbl_status.pack(side="left")

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame, mode="determinate", fg_color="#555555", progress_color="#b8e922")
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10)
        self.progress_bar.set(0)

        self.lbl_success = ctk.CTkLabel(self.bottom_frame, text="", text_color="#b8e922", width=150, anchor="e", font=("Arial", 12, "bold"))
        self.lbl_success.pack(side="right")

        self.bloquear_ui()

    # --- FUNCIONES DE IMAGEN Y ZOOM ---
    def abrir_cover_local(self):
        ruta = filedialog.askopenfilename(title="Seleccionar Carátula", filetypes=[("Imágenes", "*.jpg *.jpeg *.png")])
        if ruta:
            img = Image.open(ruta)
            self.poner_imagen_en_canvas(img)

    def poner_imagen_en_canvas(self, img):
        self.cover_original = img
        self.imscale = 1.0 # Reseteamos el zoom
        self.redibujar_imagen()

    def zoom_rueda(self, event):
        if not self.cover_original: return
        
        # Detectar la dirección de la rueda
        if event.num == 4 or event.delta > 0:
            self.imscale *= 1.1 # Acercar
        elif event.num == 5 or event.delta < 0:
            self.imscale *= 0.9 # Alejar
            
        self.redibujar_imagen()

    def redibujar_imagen(self):
        if not self.cover_original: return
        
        new_w = int(self.cover_original.width * self.imscale)
        new_h = int(self.cover_original.height * self.imscale)
        
        # Evitar que se achique hasta desaparecer
        if new_w < 20 or new_h < 20: return 
        
        img_resized = self.cover_original.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_cover = ImageTk.PhotoImage(img_resized)
        
        self.cover_canvas.delete("all")
        self.cover_canvas.create_image(100, 100, image=self.tk_cover)

    # --- FUNCIONES GENERALES ---
    def abrir_audio_local(self):
        ruta = filedialog.askopenfilename(title="Seleccionar Audio", filetypes=[("Audios", "*.mp3 *.wav *.m4a *.webm")])
        if ruta:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, ruta)

    def bloquear_ui(self):
        self.entry_album.configure(state="disabled")
        self.entry_artist.configure(state="disabled")
        self.entry_year.configure(state="disabled")
        self.btn_local_cover.configure(state="disabled")
        self.btn_convertir.configure(state="disabled")

    def desbloquear_ui(self):
        self.entry_album.configure(state="normal")
        self.entry_artist.configure(state="normal")
        self.entry_year.configure(state="normal")
        self.btn_local_cover.configure(state="normal")
        self.btn_convertir.configure(state="normal")

    def time_to_seconds(self, time_str):
        partes = time_str.split(':')
        if len(partes) == 2:
            return int(partes[0]) * 60 + int(partes[1])
        elif len(partes) == 3:
            return int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
        return -1

    # --- LÓGICA DEL CHECK ---
    def procesar_check_thread(self):
        self.btn_check.configure(state="disabled")
        self.lbl_status.configure(text="Validando...")
        threading.Thread(target=self.procesar_check, daemon=True).start()

    def procesar_check(self):
        url = self.url_entry.get().strip()
        timestamps_raw = self.txt_timestamps.get("1.0", "end-1c").strip()

        if not url or not timestamps_raw:
            self.after(0, lambda: messagebox.showerror("Error", "Falta enlace o timestamps."))
            self.after(0, self.restaurar_check)
            return

        if url.startswith("http"):
            try:
                ydl_opts = {'quiet': True, 'noplaylist': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    self.duracion_actual = info.get('duration') or float('inf')
                    
                    thumb_url = info.get('thumbnail')
                    if thumb_url:
                        raw_data = urllib.request.urlopen(thumb_url).read()
                        img = Image.open(io.BytesIO(raw_data))
                        self.after(0, self.poner_imagen_en_canvas, img)
            except Exception:
                self.after(0, lambda: messagebox.showerror("Error", "Enlace inválido o privado."))
                self.after(0, self.restaurar_check)
                return
        else:
            self.duracion_actual = float('inf') 

        lineas = timestamps_raw.split("\n")
        parsed_tracks = []
        ultimo_tiempo = -1

        for linea in lineas:
            linea = linea.strip()
            if not linea: continue

            match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)', linea)
            if not match:
                self.after(0, lambda l=linea: messagebox.showerror("Formato", f"Error de formato en: '{l}'"))
                self.after(0, self.restaurar_check)
                return
            
            time_str, track_name = match.groups()
            time_sec = self.time_to_seconds(time_str)

            if time_sec > self.duracion_actual:
                self.after(0, lambda t=time_str: messagebox.showerror("Tiempo", f"'{t}' supera el video."))
                self.after(0, self.restaurar_check)
                return
            
            if time_sec <= ultimo_tiempo:
                self.after(0, lambda t=time_str: messagebox.showerror("Orden", f"Tiempos desordenados en: '{t}'"))
                self.after(0, self.restaurar_check)
                return

            ultimo_tiempo = time_sec
            parsed_tracks.append((time_sec, track_name))
        
        self.after(0, self.dibujar_pistas, parsed_tracks)
        self.after(0, self.restaurar_check)
        self.after(0, self.desbloquear_ui)
        self.after(0, self.lbl_status.configure, {"text": "Listo para convertir."})

    def dibujar_pistas(self, pistas):
        for widget in self.track_list_frame.winfo_children():
            widget.destroy()
        
        self.track_widgets.clear()

        for i, (t_sec, t_name) in enumerate(pistas, start=1):
            row_frame = ctk.CTkFrame(self.track_list_frame, fg_color="white")
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row_frame, text=f"{i} - ", text_color="black", width=30).pack(side="left")
            
            track_entry = ctk.CTkEntry(row_frame, fg_color="white", text_color="black", border_width=0)
            track_entry.insert(0, t_name)
            track_entry.pack(side="left", fill="x", expand=True)
            
            btn_del = ctk.CTkButton(row_frame, text="X", width=25, fg_color="red", command=lambda r=row_frame: r.destroy())
            btn_del.pack(side="right", padx=5)

            # Guardamos la referencia para el recorte final
            self.track_widgets.append({'time': t_sec, 'entry': track_entry, 'row': row_frame})

    def restaurar_check(self):
        self.btn_check.configure(state="normal")
        if self.lbl_status.cget("text") == "Validando...":
            self.lbl_status.configure(text="")

    # --- CORTE, TAGS Y EXPORTACIÓN ---
    def iniciar_conversion(self):
        self.bloquear_ui()
        self.btn_check.configure(state="disabled")
        self.progress_bar.set(0)
        self.lbl_status.configure(text="Iniciando...")
        
        threading.Thread(target=self.proceso_conversion_thread, daemon=True).start()

    def proceso_conversion_thread(self):
        try:
            url = self.url_entry.get().strip()
            archivo_descargado = url

            # 1. DESCARGA (Si es URL)
            if url.startswith("http"):
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'downloads/%(title)s.%(ext)s',
                    'progress_hooks': [self.hook_progreso_yt],
                    'quiet': True,
                    'noplaylist': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if 'requested_downloads' in info:
                        archivo_descargado = info['requested_downloads'][0]['filepath']
                    else:
                        archivo_descargado = ydl.prepare_filename(info)

            # 2. CARGAR AUDIO EN MEMORIA
            self.after(0, self.lbl_status.configure, {"text": "Cargando audio a la licuadora..."})
            audio = AudioSegment.from_file(archivo_descargado)

            # 3. PREPARAR CARPETA Y COVER
            album_name = self.entry_album.get().strip() or "Album Desconocido"
            artist_name = self.entry_artist.get().strip() or "Artista Desconocido"
            year = self.entry_year.get().strip()
            
            album_dir = os.path.join("finished", album_name)
            os.makedirs(album_dir, exist_ok=True)

            cover_path = os.path.join(album_dir, "cover.jpg")
            if self.cover_original:
                # Transformamos la imagen a 1000x1000 estricto
                cover_export = self.cover_original.resize((1000, 1000), Image.Resampling.LANCZOS)
                cover_export.save(cover_path, format="JPEG")

            # Filtrar solo los temas que no hayan sido eliminados con la 'X'
            pistas_validas = [t for t in self.track_widgets if t['entry'].winfo_exists()]
            total = len(pistas_validas)

            # 4. RECORTAR Y EXPORTAR
            for i, pista in enumerate(pistas_validas):
                nombre_tema = pista['entry'].get().strip()
                start_ms = pista['time'] * 1000
                
                if i + 1 < total:
                    end_ms = pistas_validas[i+1]['time'] * 1000
                else:
                    end_ms = len(audio) # El último tema va hasta el final

                self.after(0, self.lbl_status.configure, {"text": f"Recortando: {nombre_tema}..."})
                
                # Cortar segmento
                segmento = audio[start_ms:end_ms]
                archivo_salida = os.path.join(album_dir, f"{i+1:02d} - {nombre_tema}.mp3")
                
                # Exportar MP3 a 320kbps
                segmento.export(archivo_salida, format="mp3", bitrate="320k")

                # Insertar Metadatos ID3
                audio_file = MP3(archivo_salida, ID3=ID3)
                if audio_file.tags is None:
                    audio_file.add_tags()
                
                audio_file.tags.add(TIT2(encoding=3, text=nombre_tema))
                audio_file.tags.add(TPE1(encoding=3, text=artist_name))
                audio_file.tags.add(TALB(encoding=3, text=album_name))
                audio_file.tags.add(TRCK(encoding=3, text=str(i+1)))
                if year:
                    audio_file.tags.add(TDRC(encoding=3, text=year))
                
                if os.path.exists(cover_path):
                    with open(cover_path, "rb") as img:
                        audio_file.tags.add(APIC(
                            encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=img.read()
                        ))
                audio_file.save()

                # Actualizar barra y texto
                porcentaje = (i + 1) / total
                self.after(0, self.progress_bar.set, porcentaje)
                self.after(0, self.lbl_status.configure, {"text": f"Tema {i+1} completado"})

            self.after(1000, self.mostrar_exito)

        except Exception as e:
            print(f"Error fatal: {e}")
            self.after(0, lambda err=e: messagebox.showerror("Error en conversión", f"Hubo un fallo:\n{err}"))
            self.after(0, self.lbl_status.configure, {"text": "Error."})
            self.after(0, self.desbloquear_ui)
            self.after(0, self.btn_check.configure, {"state": "normal"})

    def hook_progreso_yt(self, d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').replace('%','').strip()
            p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str)
            try:
                val = float(p_str) / 100.0
                self.after(0, self.progress_bar.set, val)
                self.after(0, self.lbl_status.configure, {"text": f"Descargando... {p_str}%"})
            except ValueError:
                pass

    def mostrar_exito(self):
        self.lbl_status.configure(text="")
        self.progress_bar.set(1)
        self.lbl_success.configure(text="¡Descarga con éxito!")
        
        self.after(2500, lambda: self.lbl_success.configure(text=""))
        self.after(2500, lambda: self.progress_bar.set(0))
        
        self.desbloquear_ui()
        self.btn_check.configure(state="normal")


if __name__ == "__main__":
    app = regisMakin()
    app.mainloop()