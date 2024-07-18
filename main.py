from website import create_app

app = create_app()

#only when running file, will app execute
#specify debug befure
if(__name__ == '__main__'):
    app.run(debug=True) #everytime change code, webserver is rerun