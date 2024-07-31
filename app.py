from fasthtml.common import *
import uvicorn


def create(todo: dict):
    return Titled("hello", Div("world"))


def index():
    frm = Form(
        # Tags with a `name` attr will have `name` auto-set to the same as `id` if not provided
        Input(id='name', placeholder='Name'),
        Button('create'),
        action='/todos', method='post')

    return Titled("New todo", frm)

class Routes:
    def init_app(self, app):
        app.route("/todos", methods=['get'])(index)
        app.route("/todos", methods=['post'])(create)

def create_app():
    app, rt = fast_app()
    Routes().init_app(app)
    return app

def main():
    app = create_app()
    uvicorn.run("app:create_app", reload=True)

if __name__ == '__main__':
    main()

