css = """
/* =========================================
   MODERN CATALOG UI
========================================= */

.modern-header {
  background: var(--surface);
  border-radius: 0 0 24px 24px;
  padding: 20px 20px 30px;
  margin: -30px -20px 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  position: relative;
  z-index: 10;
}

[data-theme="dark"] .modern-header {
  background: var(--surface);
}

.modern-header h1 {
  font-size: 1.8rem;
  margin-bottom: 20px;
}

.modern-search-bar {
  display: flex;
  background: var(--page);
  border-radius: 999px;
  padding: 8px 16px;
  align-items: center;
  border: 1px solid var(--border);
}

.modern-search-bar input {
  border: none;
  background: transparent;
  padding: 8px;
  flex-grow: 1;
  font-size: 1rem;
}

.modern-search-bar input:focus {
  outline: none;
}

.modern-search-bar button {
  border-radius: 999px;
  padding: 8px 16px;
  margin-left: 10px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 15px;
  color: var(--text);
}

.category-slider {
  display: flex;
  overflow-x: auto;
  gap: 12px;
  padding-bottom: 10px;
  margin-bottom: 25px;
  scrollbar-width: none;
}

.category-slider::-webkit-scrollbar {
  display: none;
}

.category-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 12px 16px;
  min-width: 90px;
  cursor: pointer;
  color: var(--muted);
  transition: all 0.2s;
  text-decoration: none;
}

.category-pill.active,
.category-pill:hover {
  background: var(--orange-soft);
  color: var(--orange-deep);
  border-color: var(--orange);
}

.category-pill svg {
  width: 24px;
  height: 24px;
}

.modern-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

@media (min-width: 768px) {
  .modern-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

.modern-card {
  background: var(--surface);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.04);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s;
}

.modern-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.modern-card-img {
  width: 100%;
  height: 220px;
  object-fit: cover;
  background: var(--page);
}

.modern-card-body {
  padding: 20px;
}

.modern-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.modern-card-title {
  font-size: 1.25rem;
  font-weight: 750;
  margin: 0;
  color: var(--text);
  line-height: 1.2;
}

.modern-card-subtitle {
  font-size: 0.85rem;
  color: var(--muted);
  margin-top: 4px;
}

.modern-card-price {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text);
  white-space: nowrap;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.modern-card-price-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
}

.modern-card-meta {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin: 15px 0;
  padding-top: 15px;
  border-top: 1px solid var(--border);
}

.meta-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--muted);
}

.meta-item svg {
  width: 18px;
  height: 18px;
  color: var(--orange-deep);
}

.modern-card-actions {
  display: flex;
  gap: 12px;
  margin-top: 15px;
}

.modern-card-actions button {
  flex: 1;
  border-radius: 12px;
  padding: 10px;
}
"""
with open("static/css/style.css", "a") as f:
    f.write(css)
