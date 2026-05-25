with open('js/main.js', 'r') as f:
    js = f.read()

js = js.replace('preloader.classList.add("hidden");', "preloader.classList.add('hidden');\n      document.querySelector('.hero').classList.add('expanded');")

with open('js/main.js', 'w') as f:
    f.write(js)
