from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app) # for reverse proxy? meaning that the app is behind a reverse proxy. without
api = Api(
    app,
    version="1.0",
    title="Project Planner API",
    description="A planner to organise your projects",
)


ns = api.namespace("tasks", description="CRUD project tasks operations")


TODOS = {
    "1": {"task": "Build an API", "due_date": "2024-05-01"},
    "2": {"task": "Check with the team meeting", "due_date": "2024-06-02"},
    "3": {"task": "Deploy this API and inform clients", "due_date": "2024-07-03"},
}


TASKCOMPLETED = 0
todo = api.model(
    "Todo", {"task": fields.String(required=True, description="The task details!"),
             "due_date": fields.DateTime(dt_format='iso8601', required=True, description="The due date of the task")}
)

listed_todo = api.model(
    "ListedTodo",
    {
        "id": fields.String(required=True, description="The todo ID"),
        "todo": fields.Nested(todo, description="The Todo"),
    },
)




def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        api.abort(404, "Todo {} doesn't exist".format(todo_id))




parser = api.parser()
parser.add_argument(
    "task", type=str, required=True, help="The task details", location="form"
)
#add date for type date
parser.add_argument(
    "due_date", type=str, help="The due date of the task", location="form"
)






@ns.route("/<string:todo_id>")
@api.doc(responses={404: "Todo not found"}, params={"todo_id": "The Todo ID"})
class Todo(Resource):
    @api.doc(description="todo_id should be in {0}".format(", ".join(TODOS.keys())))
    @api.marshal_with(todo)
    def get(self, todo_id):
        """Retrieve specific task"""
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]


    @api.doc(responses={204: "Todo deleted"})
    def delete(self, todo_id):
        """Delete a task"""
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return "", 204


    @api.doc(parser=parser)
    @api.marshal_with(todo)
    def put(self, todo_id):
        """Update a task"""
        import datetime
        args = parser.parse_args()
        try:
            datetime.datetime.strptime(args["due_date"], '%Y-%m-%d')
        except ValueError:
           
            api.abort(400, "Date format is not correct, please use YYYY-MM-DD")
        task = {"task": args["task"], "due_date": args["due_date"]}
        TODOS[todo_id] = task
        return task
   
    @api.doc(responses={200: "Task completed"})
    def post(self, todo_id):
        """Completed a task"""
        abort_if_todo_doesnt_exist(todo_id)
        global TASKCOMPLETED
        TASKCOMPLETED += 1
        del TODOS[todo_id]
        return "Task completed for Todo ID: {}".format(todo_id), 200
   




   


@ns.route("/")
class TodoList(Resource):


    @api.marshal_list_with(listed_todo)
    def get(self):
        """List all tasks"""
        return [{"id": id, "todo": todo} for id, todo in TODOS.items()]


    @api.doc(parser=parser)
    @api.marshal_with(todo, code=201)
    def post(self):
        """Create a task"""
        import datetime
        args = parser.parse_args()
        try:
            datetime.datetime.strptime(args["due_date"], '%Y-%m-%d')
        except ValueError:
           
            api.abort(400, "Date format is not correct, please use YYYY-MM-DD")
        todo_id = "%d" % (len(TODOS) + 1)
        TODOS[todo_id] = {"task": args["task"], "due_date": args["due_date"]}
        return TODOS[todo_id], 201
   
@ns.route("/completed")
class TodoCompleted(Resource):
    @api.doc(responses={200: "You completed {} tasks".format(TASKCOMPLETED)})
    def get(self):
        """Display the number of tasks completed"""
        return "You completed {} tasks".format(TASKCOMPLETED), 200


if __name__ == "__main__":
    app.run(debug=True)



