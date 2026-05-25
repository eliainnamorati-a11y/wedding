with open('css/style.css', 'r') as f:
    css = f.read()

# Change max-width for the hero svg to make it larger
css = css.replace('.ed-svg-draw {\n  width: 100%;\n  max-width: 500px;', '.ed-svg-draw {\n  width: 100%;\n  max-width: 400px;')

# Add specific max-width for the hero svg
if '.h1-mega .ed-svg-draw {' not in css:
    css += "\n.h1-mega .ed-svg-draw {\n  max-width: 80vw;\n  width: 800px;\n}\n"

with open('css/style.css', 'w') as f:
    f.write(css)
