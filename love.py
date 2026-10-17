import tkinter as tk
import math
import random
import time
from datetime import datetime

# ============================================================
# KONFIGURASI
# ============================================================
WIDTH = 700
HEIGHT = 700
BG = "#10101c"
PINK = "#ff3f91"
LIGHT_PINK = "#ff9acb"
WHITE = "#fff4fa"
PURPLE = "#b58cff"

MESSAGES = [
    "Semoga malam ini membawa ketenangan untukmu. 💗",
    "Jangan lupa tersenyum hari ini, ya, cantik.",
    "Semoga semua lelahmu diganti dengan hal-hal baik.",
    "Di mana pun kamu berada, semoga kamu selalu bahagia. ✨",
    "Istirahat yang cukup, ya. Kamu sudah berusaha hari ini."
]


def greeting_for_hour(hour):
    if 4 <= hour < 11:
        return "Selamat Pagi, Cantik ☀"
    if 11 <= hour < 15:
        return "Selamat Siang, Cantik 🌤"
    if 15 <= hour < 18:
        return "Selamat Sore, Cantik 🌇"
    return "Selamat Malam, Cantik 🌙"


class InteractiveHeart:
    def __init__(self, root):
        self.root = root
        self.root.title("Untuk Kamu ♡")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        self.heart_center = (WIDTH // 2, 300)
        self.base_scale = 10.5
        self.phase = 0.0
        self.message_index = 0
        self.particles = []
        self.stars = []
        self.last_time = time.perf_counter()
        self.start_time = time.perf_counter()
        self.intro_duration = 3.0
        self.mouse_x = WIDTH / 2
        self.mouse_y = HEIGHT / 2
        self.running = True
        self.status_text = "Gerakkan mouse atau klik hati untuk mencoba ✨"

        self.build_scene()
        self.build_controls()
        self.create_stars()
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.animate()

    # --------------------------------------------------------
    # MEMBUAT OBJEK SEKALI SAJA: tidak menggambar ulang semua
    # objek setiap frame sehingga animasi lebih halus.
    # --------------------------------------------------------
    def build_scene(self):
        self.canvas.create_text(
            WIDTH // 2, 48,
            text="♡  SEBUAH PESAN KECIL UNTUKMU  ♡",
            fill=LIGHT_PINK, font=("Helvetica", 12, "bold")
        )

        self.greeting_id = self.canvas.create_text(
            WIDTH // 2, 95, text="",
            fill=WHITE, font=("Helvetica", 25, "bold")
        )
        self.clock_id = self.canvas.create_text(
            WIDTH // 2, 128, text="",
            fill="#c8b5d4", font=("Helvetica", 10)
        )

        # Lapisan hati dibuat terpisah untuk menciptakan glow.
        self.heart_glow_ids = []
        for color, width in [
            ("#3a1535", 30), ("#5d173d", 21),
            ("#8d2457", 13), ("#c72f75", 7)
        ]:
            item = self.canvas.create_polygon(
                0, 0, 1, 1, 2, 2,
                fill="", outline=color, width=width,
                smooth=True, splinesteps=24
            )
            self.heart_glow_ids.append(item)

        self.heart_id = self.canvas.create_polygon(
            0, 0, 1, 1, 2, 2,
            fill=PINK, outline=LIGHT_PINK,
            width=2, smooth=True, splinesteps=24
        )

        self.highlight_id = self.canvas.create_oval(
            0, 0, 0, 0, fill="#ffd8eb", outline=""
        )

        self.message_id = self.canvas.create_text(
            WIDTH // 2, 455, text=MESSAGES[0],
            fill=WHITE, font=("Helvetica", 12),
            width=560, justify="center"
        )
        self.hint_id = self.canvas.create_text(
            WIDTH // 2, 493,
            text="Gerakkan mouse, klik area hati, atau pilih tombol di bawah",
            fill=LIGHT_PINK, font=("Helvetica", 9)
        )
        self.tagline_id = self.canvas.create_text(
            WIDTH // 2, 535,
            text="♡  kamu pantas mendapatkan hal-hal baik  ♡",
            fill="#d5b4d5", font=("Helvetica", 11, "italic")
        )
        self.status_id = self.canvas.create_text(
            WIDTH // 2, 570, text=self.status_text,
            fill=PURPLE, font=("Helvetica", 9)
        )

        # Overlay intro.
        self.intro_title_id = self.canvas.create_text(
            WIDTH // 2, 320, text="",
            fill=WHITE, font=("Helvetica", 22, "bold"),
            justify="center"
        )
        self.intro_subtitle_id = self.canvas.create_text(
            WIDTH // 2, 357, text="",
            fill=LIGHT_PINK, font=("Helvetica", 11)
        )

        self.set_scene_visible(False)

    def set_scene_visible(self, visible):
        state = "normal" if visible else "hidden"
        ids = [
            self.greeting_id, self.clock_id,
            *self.heart_glow_ids, self.heart_id, self.highlight_id,
            self.message_id, self.hint_id, self.tagline_id, self.status_id
        ]
        for item in ids:
            self.canvas.itemconfigure(item, state=state)

    def build_controls(self):
        controls = tk.Frame(self.root, bg=BG)
        controls.pack(fill="x", pady=(0, 12))

        button_style = {
            "fg": WHITE, "activeforeground": WHITE,
            "relief": "flat", "cursor": "hand2",
            "font": ("Helvetica", 10, "bold"),
            "padx": 14, "pady": 8
        }

        self.message_button = tk.Button(
            controls, text="💌 Pesan untukmu",
            command=self.next_message,
            bg="#322039", activebackground="#55305c",
            **button_style
        )
        self.message_button.pack(side="left", padx=(18, 8))

        self.heart_button = tk.Button(
            controls, text="💖 Kirim cinta!",
            command=self.heart_burst,
            bg="#70264e", activebackground="#963765",
            **button_style
        )
        self.heart_button.pack(side="left", padx=8)

        self.reset_button = tk.Button(
            controls, text="↻ Ulangi",
            command=self.reset_effect,
            bg="#322039", activebackground="#55305c",
            **button_style
        )
        self.reset_button.pack(side="right", padx=(8, 18))

    # --------------------------------------------------------
    # BACKGROUND BINTANG
    # --------------------------------------------------------
    def create_stars(self):
        random.seed(23)
        for _ in range(75):
            x = random.randint(8, WIDTH - 8)
            y = random.randint(12, HEIGHT - 100)
            radius = random.uniform(0.7, 2.0)
            phase = random.uniform(0, 2 * math.pi)
            item = self.canvas.create_oval(
                x-radius, y-radius, x+radius, y+radius,
                fill="#72506e", outline=""
            )
            self.stars.append({
                "id": item, "x": x, "y": y,
                "r": radius, "phase": phase,
                "speed": random.uniform(0.7, 2.2)
            })
        random.seed()

        self.meteor = None
        self.meteor_timer = random.uniform(2.5, 5.0)

    def update_stars(self, dt, elapsed):
        for star in self.stars:
            twinkle = (math.sin(elapsed * star["speed"] + star["phase"]) + 1) / 2
            radius = star["r"] * (0.65 + twinkle * 0.65)
            x, y = star["x"], star["y"]
            self.canvas.coords(
                star["id"], x-radius, y-radius, x+radius, y+radius
            )
            shade = int(90 + twinkle * 100)
            color = f"#{shade:02x}{max(60, shade-35):02x}{max(100, shade+15):02x}"
            self.canvas.itemconfigure(star["id"], fill=color)

        self.meteor_timer -= dt
        if self.meteor is None and self.meteor_timer <= 0:
            x = random.randint(80, WIDTH - 80)
            y = random.randint(20, 180)
            line = self.canvas.create_line(
                x, y, x-45, y+20, fill="#ffd5e8",
                width=2, capstyle=tk.ROUND
            )
            self.meteor = {
                "id": line, "x": x, "y": y,
                "vx": -330, "vy": 150, "life": 0.65
            }
            self.meteor_timer = random.uniform(3.0, 6.0)

        if self.meteor:
            m = self.meteor
            m["x"] += m["vx"] * dt
            m["y"] += m["vy"] * dt
            m["life"] -= dt
            self.canvas.coords(
                m["id"], m["x"], m["y"],
                m["x"] - 45, m["y"] + 20
            )
            if m["life"] <= 0:
                self.canvas.delete(m["id"])
                self.meteor = None

    # --------------------------------------------------------
    # BENTUK DAN DETAK HATI
    # --------------------------------------------------------
    def heart_points(self, scale):
        points = []
        for i in range(240):
            t = (i / 240) * 2 * math.pi
            x = 16 * math.sin(t) ** 3
            y = (
                13 * math.cos(t)
                - 5 * math.cos(2*t)
                - 2 * math.cos(3*t)
                - math.cos(4*t)
            )
            points.extend((
                self.heart_center[0] + x * scale,
                self.heart_center[1] - y * scale
            ))
        return points

    def update_heart(self, elapsed, dt):
        # Detak dua tahap yang lembut dan berulang.
        beat_wave = (
            1
            + 0.045 * math.sin(self.phase)
            + 0.018 * math.sin(2 * self.phase + 0.6)
        )
        scale = self.base_scale * beat_wave
        points = self.heart_points(scale)

        for index, item in enumerate(self.heart_glow_ids):
            self.canvas.coords(item, *points)
            pulse = (math.sin(self.phase - index * 0.18) + 1) / 2
            widths = [22, 16, 10, 5]
            self.canvas.itemconfigure(
                item, width=widths[index] + pulse * (3 if index < 2 else 1)
            )

        self.canvas.coords(self.heart_id, *points)

        # Kilau di kiri atas mengikuti ukuran hati.
        cx, cy = self.heart_center
        self.canvas.coords(
            self.highlight_id,
            cx - 80 * beat_wave, cy - 82 * beat_wave,
            cx - 57 * beat_wave, cy - 67 * beat_wave
        )

    # --------------------------------------------------------
    # PARTIKEL
    # --------------------------------------------------------
    def add_particle(self, x, y, kind=None, power=1.0):
        if len(self.particles) > 260:
            return
        if kind is None:
            kind = random.choices(
                ["dot", "heart", "star"], weights=[6, 2, 2]
            )[0]

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(25, 115) * power
        size = random.uniform(2.0, 5.5)
        color = random.choice([PINK, LIGHT_PINK, "#ffd5e8", WHITE, PURPLE])

        if kind == "heart":
            item = self.canvas.create_text(
                x, y, text="♥", fill=color,
                font=("Helvetica", max(8, int(size * 2.2)))
            )
        elif kind == "star":
            item = self.canvas.create_text(
                x, y, text="✦", fill=color,
                font=("Helvetica", max(8, int(size * 2.2)))
            )
        else:
            item = self.canvas.create_oval(
                x-size, y-size, x+size, y+size,
                fill=color, outline=""
            )

        self.particles.append({
            "id": item, "x": x, "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed - random.uniform(5, 45),
            "size": size, "life": random.uniform(0.65, 1.5),
            "max_life": 1.5, "kind": kind,
            "gravity": random.uniform(8, 28)
        })

    def update_particles(self, dt):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += p["gravity"] * dt
            p["life"] -= dt

            if p["life"] <= 0:
                self.canvas.delete(p["id"])
                continue

            fade = max(0.12, min(1.0, p["life"] / p["max_life"]))

            if p["kind"] == "dot":
                # Oval membutuhkan empat koordinat: kiri, atas, kanan, bawah.
                radius = max(0.5, p["size"] * fade)
                self.canvas.coords(
                    p["id"],
                    p["x"] - radius, p["y"] - radius,
                    p["x"] + radius, p["y"] + radius
                )
            else:
                # Objek teks (♥ dan ✦) menggunakan dua koordinat: x dan y.
                self.canvas.coords(p["id"], p["x"], p["y"])
                self.canvas.itemconfigure(
                    p["id"],
                    font=("Helvetica", max(6, int(p["size"] * 2.2 * fade)))
                )
            alive.append(p)
        self.particles = alive

    def heart_burst(self):
        cx, cy = self.heart_center
        for _ in range(85):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 55)
            x = cx + math.cos(angle) * distance
            y = cy + math.sin(angle) * distance
            self.add_particle(
                x, y, random.choice(["heart", "star", "dot"]),
                power=random.uniform(1.1, 2.2)
            )
        self.set_status("Semoga harimu dipenuhi cinta ✨")

    def on_mouse_move(self, event):
        self.mouse_x, self.mouse_y = event.x, event.y
        if random.random() < 0.65:
            self.add_particle(event.x, event.y, power=0.45)

    def on_canvas_click(self, event):
        for _ in range(24):
            self.add_particle(
                event.x, event.y,
                random.choice(["heart", "star", "dot"]),
                power=random.uniform(0.8, 1.6)
            )
        self.set_status("Satu ledakan kecil khusus untukmu 💗")

    # --------------------------------------------------------
    # PESAN DAN INTRO
    # --------------------------------------------------------
    def next_message(self):
        self.message_index = (self.message_index + 1) % len(MESSAGES)
        self.canvas.itemconfigure(
            self.message_id, text=MESSAGES[self.message_index]
        )
        self.heart_burst()

    def set_status(self, message):
        self.status_text = message
        self.canvas.itemconfigure(self.status_id, text=message)

    def reset_effect(self):
        for p in self.particles:
            self.canvas.delete(p["id"])
        self.particles.clear()
        self.message_index = 0
        self.canvas.itemconfigure(self.message_id, text=MESSAGES[0])
        self.set_status("Gerakkan mouse atau klik hati untuk mencoba ✨")

    def update_intro(self, elapsed):
        progress = min(1.0, elapsed / self.intro_duration)
        # Ease-out cubic: gerakan awal cepat, lalu melambat secara halus.
        eased = 1 - (1 - progress) ** 3

        if progress < 0.28:
            self.canvas.itemconfigure(
                self.intro_title_id,
                text="Ssst... ada sesuatu untukmu"
            )
            self.canvas.itemconfigure(
                self.intro_subtitle_id, text="✦  sebuah kejutan kecil  ✦"
            )
        elif progress < 0.65:
            self.canvas.itemconfigure(
                self.intro_title_id, text="Mempersiapkan sedikit kebahagiaan..."
            )
            self.canvas.itemconfigure(
                self.intro_subtitle_id, text="♡  tunggu sebentar, ya  ♡"
            )
        else:
            self.canvas.itemconfigure(self.intro_title_id, text="Untuk kamu ♡")
            self.canvas.itemconfigure(
                self.intro_subtitle_id, text="dengan harapan baik"
            )

        # Judul intro memudar dan mengecil menjelang transisi.
        self.canvas.coords(
            self.intro_title_id, WIDTH // 2, 320 - eased * 12
        )
        if progress >= 1:
            self.canvas.itemconfigure(self.intro_title_id, state="hidden")
            self.canvas.itemconfigure(self.intro_subtitle_id, state="hidden")
            self.set_scene_visible(True)
            self.heart_burst()
            return True
        return False

    def update_text(self, now):
        self.canvas.itemconfigure(
            self.greeting_id, text=greeting_for_hour(now.hour)
        )
        self.canvas.itemconfigure(
            self.clock_id, text=now.strftime("%d-%m-%Y  •  %H:%M:%S")
        )

    # --------------------------------------------------------
    # LOOP ANIMASI BERDASARKAN DELTA TIME
    # --------------------------------------------------------
    def animate(self):
        if not self.running:
            return

        current = time.perf_counter()
        dt = min(current - self.last_time, 0.04)
        self.last_time = current
        elapsed = current - self.start_time
        self.phase += dt * 4.2

        self.update_stars(dt, elapsed)
        self.update_particles(dt)

        if elapsed < self.intro_duration:
            self.update_intro(elapsed)
        else:
            self.set_scene_visible(True)
            self.update_heart(elapsed, dt)
            self.update_text(datetime.now())

        self.root.after(16, self.animate)  # sekitar 60 FPS

    def close(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = InteractiveHeart(window)
    window.mainloop()
