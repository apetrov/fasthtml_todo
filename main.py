from fasthtml.common import *

def render(todo):
    tid = f'todo-{todo.id}'
    toggle = A('Toggle', hx_get=f'/todo/{todo.id}/toggle', hx_swap='outerHTML', target_id=tid)
    delete = A('Delete', hx_delete=f'/todo/{todo.id}', hx_swap='outerHTML', target_id=tid)
    return Li(
            toggle,
            delete,
            todo.title + (' (done)' if todo.done else ''),
            id=tid
            )

app, rt, todos, Todo  = fast_app(db='data.db', tbls={'todos': {'id': int, 'title': str, 'done': bool, 'pk':'id', 'render': render}})


@rt("/todo/{id}/toggle")
def get(id:int):
    todo = todos[id]
    todo.done = not todo.done
    todos.update(todo)
    return todo

@rt("/todo/{id}")
def delete(id:int): todos.delete(id)


def create_input():
    return  Input(name='title', id='title', placeholder='Enter todo', hx_swap_oob='true')


@rt("/")
def get():
    form = Form(
            Group(
                create_input(),
                Button('Add')
                ),
            hx_post='/todo',
            target_id='todo-list',
            hx_swap='beforeend',
    )

    return Titled("Todos",
            Card(
                Ul( *todos(), id='todo-list'),
                header=form
            ))


@rt('/todo')
def post(todo: Todo): return todos.insert(todo), create_input()


serve()
