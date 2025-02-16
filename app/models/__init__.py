# app/models/__init__.py
from .board import Board
from .post import Post

models = {
    "Board": Board,
    "Post": Post
}
