from flask import Flask, render_template, request, redirect
from Netease_music import Music

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/home',  methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')

    music_name = request.form.get("musicname", None)
    print(music_name)
    if not music_name:
        # 空
        return redirect('home.html')
    music = Music()
    response = music.search_music(music_name)
    # print(response)
    return render_template('home.html', res=response)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
