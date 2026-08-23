import re

with open('static/css/style.css', 'r') as f:
    css = f.read()

# 1. Navbar compact single-row
css = re.sub(r'\.navbar \{[^\}]+\}', """.navbar {
  min-height: 50px;
  padding: 8px 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-wrap: nowrap;
}""", css)

# 2. Brand invert fix (remove background: #000)
css = re.sub(r'\.brand \{[^\}]+\}', """.brand {
  display: inline-flex;
  align-items: center;
  width: 90px;
  height: 30px;
  overflow: hidden;
  border-radius: 6px;
  padding: 0 5px;
}""", css)

brand_img_css = """
.brand img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: left center;
  filter: invert(1) hue-rotate(180deg);
}
[data-theme="dark"] .brand img {
  filter: none;
}
"""
if "filter: invert" not in css:
    css = re.sub(r'\.brand img \{[^\}]+\}', brand_img_css, css)

# 3. Filter Bar tight stack
css = re.sub(r'\.filter-bar \{[^\}]+\}', """.filter-bar {
  display: flex;
  gap: 5px;
  margin-bottom: 0;
  background: var(--surface);
  padding: 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  align-items: center;
}""", css)

# 4. Tab Nav tight spacing
css = re.sub(r'\.tab-nav \{[^\}]+\}', """.tab-nav {
  display: flex;
  gap: 5px;
  margin-bottom: 15px;
  border-bottom: none;
  padding-bottom: 0;
  overflow-x: auto;
}""", css)

css = re.sub(r'\.tab-nav-item \{[^\}]+\}', """.tab-nav-item {
  background: transparent;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--muted);
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}""", css)

# 5. Product Cards compact grid
css = re.sub(r'\.listings-grid \{[^\}]+\}', """.listings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}""", css)

css = re.sub(r'\.product-image \{[^\}]+\}', """.product-image {
  height: 120px;
  background: var(--page);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  border-bottom: 1px solid var(--border);
}""", css)

css = re.sub(r'\.product-body \{[^\}]+\}', """.product-body {
  padding: 10px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}""", css)

css = re.sub(r'\.product-title \{[^\}]+\}', """.product-title {
  font-size: 0.95rem;
  font-weight: 750;
  margin: 0 0 4px;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}""", css)

css = re.sub(r'\.product-meta \{[^\}]+\}', """.product-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 10px;
  background: var(--page);
  padding: 6px;
  border-radius: 6px;
}""", css)

css = re.sub(r'\.product-actions \{[^\}]+\}', """.product-actions {
  display: flex;
  gap: 6px;
  margin-top: auto;
}""", css)

css = re.sub(r'\.product-actions button,\s*\.product-actions a \{[^\}]+\}', """.product-actions button,
.product-actions a {
  flex: 1;
  text-align: center;
  padding: 6px;
  font-size: 0.8rem;
}""", css)

with open('static/css/style.css', 'w') as f:
    f.write(css)
