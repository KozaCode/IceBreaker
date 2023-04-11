from flask import Flask, render_template, request


app = Flask(__name__)
print(app.template_folder)

@app.errorhandler(404)
def page_not_found(e):
    print(request.url)

@app.route('/')
def index():
    return "Hello"

if __name__ == '__main__':
    app.run(debug=True)