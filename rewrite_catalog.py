import re

with open('products/templates/customer_catalog.html', 'r') as f:
    html = f.read()

# 1. Remove SVGs from tab-nav
html = re.sub(r'<svg.*?</svg>', '', html, flags=re.DOTALL)
html = re.sub(r'<span>(.*?)</span>', r'\1', html)

# 2. Extract filter-bar
filter_bar_match = re.search(r'<form method="GET".*?</form>', html, flags=re.DOTALL)
if filter_bar_match:
    filter_bar = filter_bar_match.group(0)
    # Remove it from original position
    html = html.replace(filter_bar, '')
    
    # 3. Insert filter-bar right inside dashboard-wrapper, before tab-nav
    # Also wrap it in a compact container
    new_header = f"""
    <div style="display:flex; flex-direction:column; gap:5px; margin-bottom:15px;">
        {filter_bar}
    </div>
    """
    html = html.replace('<div class="dashboard-wrapper">', f'<div class="dashboard-wrapper">\n{new_header}')
    
    # Actually wait, the user wants the tabs "right below the header/search area".
    # We can just put the filter-bar first, then the tab-nav.
    # Let's do it cleanly:
    
# Save back
with open('products/templates/customer_catalog.html', 'w') as f:
    f.write(html)
