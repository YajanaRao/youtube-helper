from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import pafy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Playlist(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	yid = db.Column(db.String(20),unique=True)
	title = db.Column(db.String(80),unique=True)
	artist = db.Column(db.String(80))
	url = db.Column(db.String(500), unique=True, nullable=False)
	image = db.Column(db.String(500))
	desc = db.Column(db.String(500))

	def __repr__(self):
		return '<User %r>' % self.title


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/add/<youtu_id>')
def add(youtu_id):
	song = {}
	try:
		url = "https://www.youtube.com/watch?v=" + youtu_id
		video = pafy.new(url)

		audio = video.audiostreams[-1]
		song = Playlist(yid=youtu_id,title=video.title,artist=video.author,image=video.bigthumb,desc=video.description,url=audio.url)
		db.session.add(song)
		db.session.commit()
		return redirect(url_for('player'))
	except Exception as exc:
		print(exc)
		return render_template('player.html')

@app.route('/delete/<youtu_id>')
def delete(youtu_id):
	song = Playlist.query.filter_by(yid=youtu_id).first()
	db.session.delete(song)
	db.session.commit()
	return redirect(url_for('player'))

@app.route("/v/<youtu_id>")
def download(youtu_id):
	try:
		url = "https://www.youtube.com/watch?v=" + youtu_id
		video = pafy.new(url)
		best = video.getbest()
		strm = video.streams
		strm_url_list = []
		strm_res_list = []
		strm_ext_list = []
		for s in strm:
		    strm_url_list.append(s.url)
		    strm_res_list.append(s.resolution)
		    strm_ext_list.append(s.extension)

		stul = strm_url_list
		stres = strm_res_list
		stex = strm_ext_list

		audio = video.audiostreams[-1]
		audio_url = audio.url


		style = url_for('static', filename='style.css')

		return render_template('v.html', title=video.title,
				desc=video.description,
				best_url=best.url, ext=best.extension,
				res=best.resolution, sty=style,
				yid=youtu_id, author=video.author,
				views=video.viewcount,
				rating=round(video.rating),
				li_do=zip(stul, stres, stex),
				a_url=audio_url,
				)
	except:
		errsty = url_for('static', filename='error.css')
		error_title = "404 Not Found"
		error_string = "404 Not Found. Video Not Available"
		return render_template('v.html', er_tit=error_title,
                               er_str=error_string, erst=errsty)


@app.route('/watch/<youtu_id>')
def watch(youtu_id):
	song = Playlist.query.filter_by(yid=youtu_id).first()
	
	print("watch")
	return render_template('watch.html',song=song)

@app.route('/player')
def player():
	list = Playlist.query.all()
	return render_template('player.html',data=list)

@app.errorhandler(404)
def error404(e):
    return redirect("/", code=302)

if __name__ == "__main__":
	app.run(debug=True, port=8090)
