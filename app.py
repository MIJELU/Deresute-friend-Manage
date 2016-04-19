from drst import create_app
import sys

app = create_app()


if __name__ == '__main__':
    app.run(port = 5000, debug=True)
