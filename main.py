from fasthtml.common import *
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean

from dataclasses import dataclass

import uvicorn

Base = declarative_base()

class Todo(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    done = Column(Boolean)

class Db:
    def init_app(app):
        engine = create_engine('sqlite:///data.db')
        Base.metadata.create_all(engine)
        app.db = sessionmaker(bind=engine)()
        return app


def create_input():
    return  Input(name='title', id='title', placeholder='Enter todo', hx_swap_oob='true')

def render(todo):
    tid = f'todo-{todo.id}'
    toggle = A('Toggle', hx_get=f'/todos/{todo.id}', hx_swap='outerHTML', target_id=tid)
    delete = A('Delete', hx_delete=f'/todos/{todo.id}', hx_swap='outerHTML', target_id=tid)
    return Li(
            toggle,
            delete,
            str(todo.title) + (' (done)' if todo.done else ''),
            id=tid
            )


@dataclass
class TodoRepo:
    db: object

    def all(self):
        return self.db.query(Todo).all()

    def get(self, id:int):
        return self.db.query(Todo).get(id)

    def save(self, todo: Todo):
        self.db.add(todo)
        self.db.commit()

    def destroy(self, id:int):
        todo = self.get(id)
        self.db.delete(todo)
        self.db.commit()

@dataclass
class TodosController:
    db: object

    def __post_init__(self):
        self.repo = TodoRepo(self.db)

    def show(self, id:int):
        todo = self.repo.get(id)
        todo.done = not todo.done
        self.repo.save(todo)
        return render(todo)

    def destroy(self, id:int):
        self.repo.destroy(id)

    def index(self):
        todos = self.repo.all()
        form = Form(
                Group(
                    create_input(),
                    Button('Add')
                    ),
                hx_post='/todos/create',
                target_id='todo-list',
                hx_swap='beforeend',
        )

        return Titled("Todos",
                Card(
                    Ul( *[render(t) for t in todos], id='todo-list'),
                    header=form
                ))

    def create(self, title: str):
        todo = Todo(title=title, done=False)
        self.repo.save(todo)
        return render(todo), create_input()

class Routes:
    def init_app(self, app):
        todo_controller = TodosController(app.db)
        app.route("/todos", methods=['get'])(todo_controller.index)
        app.route("/todos/{id}", methods=['get'])(todo_controller.show)
        app.route("/todos/{id}", methods=['delete'])(todo_controller.destroy)
        app.route("/todos/create", methods=['post'])(todo_controller.create)

def create_app():
    # doesn't work out of the box
    # app = FastHTML()
    app, rt = fast_app()
    Db.init_app(app)
    Routes().init_app(app)
    return app

def main():
    app = create_app()
    uvicorn.run("main:create_app", reload=True, factory=True)

if __name__ == '__main__':
    main()

