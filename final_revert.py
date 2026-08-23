import re

# 1. Restore style.css from original and append overrides
with open('original_style.css', 'r') as f:
    css = f.read()

overrides = """
/* COMPACT UI OVERRIDES */
.navbar {
  min-height: 50px;
  padding: 8px 15px;
  flex-wrap: nowrap;
}

.brand {
  background: transparent !important;
}

.brand img {
  filter: invert(1) hue-rotate(180deg);
}

[data-theme="dark"] .brand img {
  filter: none;
}

.filter-bar {
  display: flex !important;
  flex-direction: row !important;
  gap: 5px !important;
  margin-bottom: 5px !important;
  padding: 8px !important;
}

.filter-bar input, .filter-bar select, .filter-bar button {
  padding: 8px 10px !important;
  margin: 0 !important;
}

.tab-nav {
  margin-bottom: 15px !important;
  border-bottom: none !important;
  padding-bottom: 0 !important;
  gap: 5px !important;
}

.tab-nav-item {
  padding: 6px 10px !important;
  font-size: 0.85rem !important;
}

.listings-grid {
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)) !important;
  gap: 12px !important;
}

.product-image {
  height: 120px !important;
}

.product-body {
  padding: 10px !important;
}

.product-title {
  font-size: 0.95rem !important;
  margin: 0 0 5px !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-meta {
  gap: 5px !important;
  margin-bottom: 10px !important;
  padding: 5px !important;
}

.product-actions {
  gap: 5px !important;
  margin-top: auto !important;
}

.product-actions button {
  padding: 6px !important;
  font-size: 0.8rem !important;
}
"""
with open('static/css/style.css', 'w') as f:
    f.write(css + overrides)


# 2. Restore customer_catalog.html from original and adjust layout order
with open('original_catalog.html', 'r') as f:
    html = f.read()

# Extract filter-bar
filter_match = re.search(r'<form method="GET".*?</form>', html, flags=re.DOTALL)
filter_html = filter_match.group(0)

# Remove filter-bar from original location
html = html.replace(filter_html, "")

# Insert filter-bar directly above tab-nav (since user wants them right below header/search)
# Actually, dashboard-wrapper -> filter_html -> tab-nav
new_header = f"""
    <div style="display: flex; flex-direction: column; gap: 5px; margin-bottom: 10px;">
        {filter_html}
    </div>
"""
html = html.replace('<div class="tab-nav">', new_header + '    <div class="tab-nav">')

# Also, update base.html cache buster to force the new css
with open('templates/base.html', 'r') as f:
    base_html = f.read()
base_html = re.sub(r'style\.css\?v=[0-9.]+', 'style.css?v=3.0', base_html)
with open('templates/base.html', 'w') as f:
    f.write(base_html)

with open('products/templates/customer_catalog.html', 'w') as f:
    f.write(html)
