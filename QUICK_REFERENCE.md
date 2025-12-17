# 🚀 Agent Assist Console - Quick Reference Card

## ⚡ Quick Start Commands

```powershell
# 1. Setup (first time only)
copy .env.example .env
# Edit .env and add GOOGLE_API_KEY

# 2. Start Application
.\start.ps1

# 3. Access
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 📁 File Structure Quick Guide

```
Agent-Assistance-Bot/
├── 📖 README.md                    ← Start here
├── 📐 ARCHITECTURE.md              ← System design
├── 📊 DIAGRAMS.md                  ← Visual diagrams
├── ✅ PROJECT_COMPLETE.md          ← Completion summary
├── 🚀 start.ps1                    ← Quick start script
│
├── 🎨 client/                      ← Frontend
│   ├── index.html                  ← Main UI
│   ├── styles.css                  ← Custom styles
│   └── app.js                      ← Application logic
│
└── ⚙️ server/                      ← Backend
    ├── app/
    │   ├── core/
    │   │   ├── orchestrator.py     ← Main pipeline
    │   │   └── prompts.py          ← System prompts
    │   ├── services/
    │   │   ├── data_loader.py      ← Product database
    │   │   ├── gemini_service.py   ← AI service
    │   │   └── freshdesk.py        ← Ticket integration
    │   ├── routers/
    │   │   ├── api.py              ← API endpoints
    │   │   └── health.py           ← Health checks
    │   └── main.py                 ← App entry point
    └── data/
        ├── product_catalog.csv     ← Product specs
        └── product_media.json      ← Media assets
```

---

## 🔧 Common Tasks

### Add a New Product

**1. CSV (Specifications):**
```csv
# Edit: server/data/product_catalog.csv
MODEL-123,Product Name,Price,Finish,Dimensions,...
```

**2. JSON (Media):**
```json
// Edit: server/data/product_media.json
{
  "MODEL-123": {
    "videos": [...],
    "images": [...],
    "documents": [...]
  }
}
```

**3. Restart:** Backend will auto-reload data

### Customize a Prompt

**Edit:** `server/app/core/prompts.py`

```python
@staticmethod
def get_synthesis_prompt() -> str:
    return """Your custom prompt here"""
```

### Add an API Endpoint

**Edit:** `server/app/routers/api.py`

```python
@router.post("/my-endpoint")
async def my_endpoint(data: MyModel):
    # Your logic
    return {"result": "..."}
```

### Change Frontend Styling

**Edit:** `client/styles.css`

```css
/* Your custom styles */
.my-class {
    /* ... */
}
```

---

## 🐛 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Backend won't start | Check `.env` has `GOOGLE_API_KEY` |
| No products found | Verify CSV/JSON in `server/data/` |
| CORS errors | Update origins in `server/app/main.py` |
| Freshdesk fails | Check `FRESHDESK_DOMAIN` and `FRESHDESK_API_KEY` |
| Port in use | Change port in `main.py` or kill process |

---

## 📡 API Endpoints Cheat Sheet

```
POST /api/chat
  → Process query, return answer + media

POST /api/freshdesk
  → Export to ticket

GET /health
  → System health status

GET /stats
  → Database statistics

GET /api/products
  → List all products

GET /api/product/{model}
  → Get product details
```

---

## 🎯 Query Examples

```
✓ "How do I install GC-303-T?"
✓ "What are the specs for 10.FGC.4003CP?"
✓ "Compare GC-303-T and 10.FGC.4003CP"
✓ "Show me glass clamps in chrome finish"
✓ "Troubleshoot leaking GC-303-T"
```

---

## 🔑 Environment Variables

```env
# Required
GOOGLE_API_KEY=your_key_here

# Optional
FILE_SEARCH_CORPUS_ID=your_corpus_id
FRESHDESK_DOMAIN=your_company
FRESHDESK_API_KEY=your_api_key
DATA_DIR=data
```

---

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

## 💡 Pro Tips

1. **Use Flash Mode** for quick lookups (2-3s)
2. **Use Reasoning Mode** for complex comparisons (5-10s)
3. **Include model numbers** in queries for best results
4. **Export to Freshdesk** to save research in tickets
5. **Check /health** endpoint if something's wrong
6. **View /docs** for interactive API testing

---

## 📊 System Health Checks

```powershell
# Backend health
curl http://localhost:8000/health

# Database stats
curl http://localhost:8000/stats

# Test query (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/api/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"test","model_mode":"flash"}'
```

---

## 🎨 UI Components

### Left Panel (Controls)
- LLM mode selector (Flash/Reasoning)
- Freshdesk ticket input
- Export button
- Quick action buttons

### Center Panel (Chat)
- Chat messages
- User input
- Send button
- Markdown rendering

### Right Panel (Media)
- Product specifications
- Video links
- Document links
- Image gallery

---

## 🔄 Development Workflow

```
1. Make changes to code
   ↓
2. Backend auto-reloads (--reload flag)
   ↓
3. Frontend: Refresh browser
   ↓
4. Test changes
   ↓
5. Commit to version control
```

---

## 📈 Monitoring

### What to Track
- Response times (target: <3s flash, <10s reasoning)
- Match confidence (target: >80%)
- Error rates (target: <1%)
- Daily queries (track adoption)
- Freshdesk exports (track usage)

### Where to Look
- Server logs: `docker-compose logs -f backend`
- Browser console: F12 → Console
- Network tab: F12 → Network
- Health endpoint: `/health`

---

## 🔒 Security Checklist

```
[ ] API keys in .env (not committed)
[ ] HTTPS enabled (production)
[ ] CORS configured correctly
[ ] Rate limiting enabled
[ ] Input validation active
[ ] Error messages sanitized
[ ] Logs don't expose secrets
```

---

## 🚀 Deployment Checklist

```
[ ] Update .env with production values
[ ] Test all features locally
[ ] Build Docker images
[ ] Deploy to production
[ ] Run smoke tests
[ ] Monitor for errors
[ ] Document any issues
```

---

## 📞 Support Resources

1. **Documentation**
   - [README.md](README.md) - Full guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Design details
   - [DIAGRAMS.md](DIAGRAMS.md) - Visual diagrams
   - http://localhost:8000/docs - API docs

2. **Logs**
   - Backend: `docker-compose logs backend`
   - Frontend: Browser console (F12)

3. **Health**
   - Status: http://localhost:8000/health
   - Stats: http://localhost:8000/stats

---

## 🎓 Learning Path

```
Day 1: Read README.md
       ↓
Day 2: Run locally, test features
       ↓
Day 3: Read ARCHITECTURE.md
       ↓
Day 4: Explore code, make small changes
       ↓
Day 5: Add custom product data
       ↓
Week 2: Deploy to production
       ↓
Month 1: Train team, gather feedback
```

---

## 🎯 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Response Time | <3s flash | Monitor logs |
| Match Accuracy | >80% | Track confidence |
| Uptime | >99% | Health checks |
| Agent Adoption | >75% | Query count |
| Customer Satisfaction | +20% | Surveys |

---

## 🌟 Feature Matrix

| Feature | Status | File to Edit |
|---------|--------|--------------|
| Model Detection | ✅ | `data_loader.py` |
| LLM Modes | ✅ | `gemini_service.py` |
| Media Panel | ✅ | `app.js` |
| Freshdesk Export | ✅ | `freshdesk.py` |
| Health Checks | ✅ | `health.py` |
| Custom Prompts | ✅ | `prompts.py` |

---

## 💬 Common Questions

**Q: How do I add my own products?**  
A: Edit `server/data/product_catalog.csv` and `product_media.json`

**Q: Can I use a different database?**  
A: Yes! Modify `data_loader.py` to load from your database

**Q: How do I change the UI colors?**  
A: Edit `client/styles.css` or Tailwind classes in `index.html`

**Q: Can I add authentication?**  
A: Yes! Add middleware in `server/app/main.py`

**Q: How do I scale for more users?**  
A: Use Docker Compose with multiple backend instances

---

## 📦 Dependencies

### Backend (Python)
- fastapi - Web framework
- uvicorn - ASGI server
- google-genai - AI SDK
- pandas - Data processing
- fuzzywuzzy - Fuzzy matching
- aiohttp - HTTP client

### Frontend (JavaScript)
- marked.js - Markdown parser
- Tailwind CSS - Styling

---

## 🎬 Next Actions

```
1. [ ] Copy .env.example to .env
2. [ ] Add GOOGLE_API_KEY
3. [ ] Run .\start.ps1
4. [ ] Test with sample queries
5. [ ] Add your product data
6. [ ] Configure Freshdesk (optional)
7. [ ] Train your team
8. [ ] Deploy to production
9. [ ] Monitor and improve
```

---

**Version:** 1.0.0  
**Quick Ref Updated:** December 16, 2025  
**Print This:** For quick desk reference! 📄
