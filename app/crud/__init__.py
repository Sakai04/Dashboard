# app/crud/__init__.py
from .board import (
    create_board,
    get_board_by_index,  # get_board 대신 이 함수를 사용합니다.
    get_boards,
    update_board,
    delete_board
)
from .post import *  # 필요한 경우 Post 관련 함수도 import
