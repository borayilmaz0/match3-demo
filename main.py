# main.py
from GameSession import GameSession
from Level1 import Level1


def main():
    level = Level1()
    session = GameSession(level)
    session.start()


if __name__ == "__main__":
    main()
