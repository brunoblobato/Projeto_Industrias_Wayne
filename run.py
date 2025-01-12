from project import create_app

app = create_app()

if __name__ == "__main__":
    # Executa o servidor no modo debug
    app.run(debug=True)
