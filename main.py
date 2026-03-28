"""
Gestionnaire de Dépenses - Version Android (Kivy + SQLite)
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

import sqlite3
import os
from datetime import datetime

# ── Couleurs ───────────────────────────────────────────────────────────────────
VERT      = get_color_from_hex("#2ECC71")
ROUGE     = get_color_from_hex("#E74C3C")
BLEU      = get_color_from_hex("#3498DB")
FOND      = get_color_from_hex("#1A1A2E")
CARTE     = get_color_from_hex("#16213E")
TEXTE     = get_color_from_hex("#EAEAEA")
GRIS      = get_color_from_hex("#7F8C8D")
OR        = get_color_from_hex("#F39C12")

# ── Base de données ────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.expanduser("~"), "depenses.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id  INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            description  TEXT NOT NULL,
            montant      REAL NOT NULL,
            date         TEXT NOT NULL,
            categorie_id INTEGER REFERENCES categories(id)
        )
    """)
    for cat in ("Alimentation", "Transport", "Logement", "Santé", "Loisirs", "Autre"):
        conn.execute("INSERT OR IGNORE INTO categories (nom) VALUES (?)", (cat,))
    conn.commit()
    conn.close()

def get_categories():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM categories ORDER BY nom").fetchall()
    conn.close()
    return rows

def get_depenses():
    conn = get_conn()
    rows = conn.execute("""
        SELECT d.id, d.description, d.montant, d.date, c.nom AS categorie
        FROM depenses d LEFT JOIN categories c ON d.categorie_id = c.id
        ORDER BY d.date DESC
    """).fetchall()
    conn.close()
    return rows

def ajouter_depense(description, montant, categorie_id):
    conn = get_conn()
    conn.execute(
        "INSERT INTO depenses (description, montant, date, categorie_id) VALUES (?,?,?,?)",
        (description, montant, datetime.now().strftime("%Y-%m-%d"), categorie_id)
    )
    conn.commit()
    conn.close()

def supprimer_depense(dep_id):
    conn = get_conn()
    conn.execute("DELETE FROM depenses WHERE id=?", (dep_id,))
    conn.commit()
    conn.close()

def get_total():
    conn = get_conn()
    row = conn.execute("SELECT COALESCE(SUM(montant),0) AS total FROM depenses").fetchone()
    conn.close()
    return row["total"]

# ── Widgets réutilisables ──────────────────────────────────────────────────────

def btn(text, color=BLEU, on_press=None, height=dp(50)):
    b = Button(
        text=text,
        background_color=color,
        background_normal="",
        color=TEXTE,
        size_hint_y=None,
        height=height,
        font_size=dp(16),
        bold=True,
    )
    if on_press:
        b.bind(on_press=on_press)
    return b

def label(text, size=16, color=TEXTE, bold=False, halign="left"):
    l = Label(
        text=text,
        font_size=dp(size),
        color=color,
        bold=bold,
        halign=halign,
        text_size=(None, None),
    )
    return l

# ── Écran principal ────────────────────────────────────────────────────────────

class AccueilScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        root.canvas.before.clear()

        # Titre
        root.add_widget(label("💰 Mes Dépenses", size=24, bold=True, color=OR, halign="center"))

        # Total
        self.total_label = label(f"Total : {get_total():.2f} DA", size=20, color=VERT, halign="center")
        root.add_widget(self.total_label)

        # Boutons navigation
        root.add_widget(btn("➕  Ajouter une dépense", VERT,   lambda x: self.go("ajouter")))
        root.add_widget(btn("📋  Voir les dépenses",   BLEU,   lambda x: self.go("liste")))
        root.add_widget(btn("📊  Statistiques",        OR,     lambda x: self.go("stats")))

        self.add_widget(root)

    def go(self, screen):
        self.manager.current = screen

    def on_enter(self):
        self.total_label.text = f"Total : {get_total():.2f} DA"


# ── Écran Ajouter ──────────────────────────────────────────────────────────────

class AjouterScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(14))

        root.add_widget(label("➕ Nouvelle dépense", size=20, bold=True, color=OR))

        root.add_widget(label("Description :"))
        self.desc_input = TextInput(
            hint_text="Ex: Déjeuner restaurant",
            multiline=False,
            size_hint_y=None, height=dp(45),
            background_color=CARTE, foreground_color=TEXTE,
            font_size=dp(15),
        )
        root.add_widget(self.desc_input)

        root.add_widget(label("Montant (DA) :"))
        self.montant_input = TextInput(
            hint_text="Ex: 500",
            multiline=False, input_filter="float",
            size_hint_y=None, height=dp(45),
            background_color=CARTE, foreground_color=TEXTE,
            font_size=dp(15),
        )
        root.add_widget(self.montant_input)

        root.add_widget(label("Catégorie :"))
        cats = [r["nom"] for r in get_categories()]
        self.cat_spinner = Spinner(
            text=cats[0] if cats else "Autre",
            values=cats,
            size_hint_y=None, height=dp(45),
            background_color=CARTE, color=TEXTE,
            font_size=dp(15),
        )
        root.add_widget(self.cat_spinner)

        self.msg = label("", color=VERT, halign="center")
        root.add_widget(self.msg)

        root.add_widget(btn("✅  Enregistrer", VERT, self.enregistrer))
        root.add_widget(btn("⬅️  Retour",      GRIS, lambda x: self.go_back()))

        self.add_widget(root)

    def enregistrer(self, *a):
        desc   = self.desc_input.text.strip()
        montant_s = self.montant_input.text.strip()

        if not desc or not montant_s:
            self.msg.color = ROUGE
            self.msg.text  = "⚠️ Remplis tous les champs !"
            return
        try:
            montant = float(montant_s)
        except ValueError:
            self.msg.color = ROUGE
            self.msg.text  = "⚠️ Montant invalide !"
            return

        # Trouver l'id de la catégorie
        cats = get_categories()
        cat_id = next((r["id"] for r in cats if r["nom"] == self.cat_spinner.text), 6)

        ajouter_depense(desc, montant, cat_id)
        self.msg.color = VERT
        self.msg.text  = f"✅ {desc} — {montant:.2f} DA ajouté !"
        self.desc_input.text    = ""
        self.montant_input.text = ""

    def go_back(self):
        self.manager.current = "accueil"


# ── Écran Liste ────────────────────────────────────────────────────────────────

class ListeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        root.add_widget(label("📋 Toutes les dépenses", size=20, bold=True, color=OR))

        scroll = ScrollView()
        grid   = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        rows = get_depenses()
        if not rows:
            grid.add_widget(label("Aucune dépense.", color=GRIS, halign="center"))
        else:
            for r in rows:
                card = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None, height=dp(60),
                    padding=dp(8), spacing=dp(6),
                )
                info = BoxLayout(orientation="vertical")
                info.add_widget(label(f"{r['description']}", size=14, bold=True))
                info.add_widget(label(f"{r['date']}  •  {r['categorie']}", size=12, color=GRIS))
                card.add_widget(info)
                card.add_widget(label(f"{r['montant']:.0f} DA", size=15, color=VERT, bold=True))

                dep_id = r["id"]
                del_btn = Button(
                    text="🗑",
                    size_hint=(None, None), size=(dp(40), dp(40)),
                    background_color=ROUGE, background_normal="",
                )
                del_btn.bind(on_press=lambda x, did=dep_id: self.supprimer(did))
                card.add_widget(del_btn)
                grid.add_widget(card)

        scroll.add_widget(grid)
        root.add_widget(scroll)
        root.add_widget(btn("⬅️  Retour", GRIS, lambda x: setattr(self.manager, "current", "accueil")))
        self.add_widget(root)

    def supprimer(self, dep_id):
        supprimer_depense(dep_id)
        self.on_enter()


# ── Écran Stats ────────────────────────────────────────────────────────────────

class StatsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        root.add_widget(label("📊 Statistiques", size=20, bold=True, color=OR))
        root.add_widget(label(f"Total général : {get_total():.2f} DA", size=18, color=VERT, bold=True))

        conn = get_conn()
        stats = conn.execute("""
            SELECT c.nom, COUNT(*) nb, SUM(d.montant) total
            FROM depenses d JOIN categories c ON d.categorie_id=c.id
            GROUP BY c.id ORDER BY total DESC
        """).fetchall()
        conn.close()

        if not stats:
            root.add_widget(label("Pas encore de données.", color=GRIS))
        else:
            for r in stats:
                row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
                row.add_widget(label(r["nom"], size=14))
                row.add_widget(label(f"{r['nb']} dépense(s)", size=13, color=GRIS))
                row.add_widget(label(f"{r['total']:.0f} DA", size=14, color=OR, bold=True))
                root.add_widget(row)

        root.add_widget(btn("⬅️  Retour", GRIS, lambda x: setattr(self.manager, "current", "accueil")))
        self.add_widget(root)


# ── Application principale ─────────────────────────────────────────────────────

class DepensesApp(App):
    def build(self):
        init_db()
        Window.clearcolor = FOND

        sm = ScreenManager()
        sm.add_widget(AccueilScreen(name="accueil"))
        sm.add_widget(AjouterScreen(name="ajouter"))
        sm.add_widget(ListeScreen(name="liste"))
        sm.add_widget(StatsScreen(name="stats"))
        return sm


if __name__ == "__main__":
    DepensesApp().run()
