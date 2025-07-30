# How to Build the App After Cloning (Part 2)

---

## 5. Build & Run the Frontend
```sh
cd ../frontend
npm run build    # For production build
npm start        # For development server
```

---

## 6. Build & Run the Backend
- For Python (Flask/FastAPI/Django):
```sh
cd ../backend
python app.py    # or follow backend README
```
- For Node.js backend:
```sh
cd ../backend
npm start
```

---

## 7. Troubleshooting & Tips
- **Always check the terminal output for errors.**
- If a build fails, look for missing dependencies or version mismatches.
- Run all commands in verbose mode if possible (e.g., `npm run build --verbose`).
- If you get stuck, check the project README, or ask in the team chat.

---

## 8. Additional Setup
- Some projects requirenvironment variables (see `.env.example`).
- For databasetup, check the backend README.
- For agentic tools (like Windsurf/Cascade):
  - Follow their install instructions, ensure agenticoding rules are followed (logging, error catching, provenance, verbose builds).

---

**You should now have both frontend and backend running locally!**

---

*Update this guide as project requirements change or new tools are added.*
