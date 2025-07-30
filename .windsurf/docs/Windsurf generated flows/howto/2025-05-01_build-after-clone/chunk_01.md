> **Prompt:**
> howto: build the app after cloning from github onew dev pc, including frontend and backend and installing all necessary tools :howto

# How to Build the App After Cloning (Frontend & Backend)

This guide walks you through setting up your development environment, installing all necessary tools, and building bothe frontend and backend after cloning the repository from GitHub. It is designed to minimize holdups and ensure a smooth setup for new contributors.

---

## 1. Prerequisites
- **Windows 10/11** (or WSL2 for Linux tools)
- **Git** ([Download](https://git-scm.com/download/win))
- **Node.js** (LTS recommended, [Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Python 3.8+** (if backend uses Python, [Download](https://www.python.org/))
- **Visual Studio Code** (recommended, [Download](https://code.visualstudio.com/))
- Any other project-specific tools (see project README)

---

## 2. Clone the Repository
```sh
git clone https://github.com/sandraschi/kyoyu-ultra.git
cd kyoyu-ultra
```

---

## 3. Install Frontendependencies
```sh
cd frontend
npm install
```

---

## 4. Install Backendependencies
- If backend is in `backend/`:
```sh
cd ../backend
pip install -requirements.txt
```
- If backend uses Node.js:
```sh
cd ../backend
npm install
```
- Check for a backend README for additional steps.
