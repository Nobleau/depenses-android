# 💰 Gestionnaire de Dépenses — Android

Application Android de gestion de dépenses, construite avec **Python + Kivy + SQLite**.
L'APK est compilé automatiquement par **GitHub Actions**.

---

## 📱 Fonctionnalités

- ➕ Ajouter des dépenses (description, montant, catégorie)
- 📋 Lister et supprimer les dépenses
- 📊 Statistiques par catégorie
- 💾 Stockage local SQLite (fonctionne sans internet)

---

## 🚀 Télécharger l'APK

1. Va dans l'onglet **Actions** sur GitHub
2. Clique sur le dernier workflow **"Build APK Android"**
3. Télécharge **"depenses-app-debug"**
4. Installe le `.apk` sur ton téléphone Android

---

## 🛠️ Structure

```
depenses-android/
├── main.py              # Application Kivy
├── buildozer.spec       # Configuration de compilation
├── .github/
│   └── workflows/
│       └── build.yml   # GitHub Actions (compilation APK)
└── README.md
```

---

## ⚙️ Compiler soi-même (Linux uniquement)

```bash
pip install buildozer cython==0.29.33
buildozer android debug
```
