from Bot import Bot
from Book import Book


def main():
    book = Book("assistant.data")
    bot = Bot(book)
    bot.run()

    pass


if __name__ == "__main__":
    main()
