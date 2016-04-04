from drst import create_app
import sys

app = create_app()
sv = "test"

if (len(sys.argv) > 1):
    sv = sys.argv[1]

if __name__ == '__main__':
    if sv is "public" :
        app.run(host = '0.0.0.0', port = 80)
    else :
        app.run(port = 5000, debug=True)
