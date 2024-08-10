from fasthtml.common import *
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()
metadata = MetaData()

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

import uvicorn

def render(todo):
    tid = f'todo-{todo.id}'
    toggle = A('Toggle', hx_get=f'/todos/{todo.id}', hx_swap='outerHTML', target_id=tid)
    delete = A('Delete', hx_delete=f'/todos/{todo.id}', hx_swap='outerHTML', target_id=tid)
    return Li(
            toggle,
            delete,
            todo.title + (' (done)' if todo.done else ''),
            id=tid
            )

def show(id:int):
    todo = state.app.db.query(Todo).get(id)
    todo.done = not todo.done
    state.app.db.add(todo)
    state.app.db.commit()
    return render(todo)

def delete(id:int): todos.delete(id)


def create_input():
    return  Input(name='title', id='title', placeholder='Enter todo', hx_swap_oob='true')


def index():
    todos = state.app.db.query(Todo).all()
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


def create(todo: Todo): 
    state.app.db.add(todo)
    state.app.db.commit()
    return render(todo), create_input()


class Routes:
    def init_app(self, app):
        app.route("/todos", methods=['get'])(index)
        app.route("/todos/{id}", methods=['get'])(show)
        #app.route("/todos/{id}", methods=['delete'])(delete)
        app.route("/todos/create", methods=['post'])(create)

from dataclasses import dataclass
@dataclass
class GlobalState:
    app: object


state = GlobalState(app=None)


def create_app():
    app, rt = fast_app()
    Db.init_app(app)
    Routes().init_app(app)
    # app.db.add(Todo(title='First todo', done=False))
    # app.db.add(Todo(title='Second todo', done=False))
    # app.db.add(Todo(title='Third todo', done=False))
    # app.db.commit()
    state.app = app
    return app

def main():
    app = create_app()
    uvicorn.run("main:create_app", reload=True)

if __name__ == '__main__':
    main()

