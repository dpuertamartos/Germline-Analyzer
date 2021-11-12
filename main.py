import base64
from flask import Flask, g, render_template, redirect, url_for, flash, request, Response
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, email
from werkzeug.utils import secure_filename
from graph import getlist, dataframe_proccess
import os
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import matplotlib.pyplot as plt
import random

# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6bAB19951993"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Bootstrap(app)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        d = {}

        #create dictionary with all the files
        #flash error if files are not csv
        filenamelist=[]
        for file in files:
            if not allowed_file(file.filename):
                flash('Please upload only .csv (excel) files')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            filenamelist.append(filename)
            d[filename] = getlist(file)

        df = dataframe_proccess(d)

        #Create figure for the graph and plot it
        fig = Figure()
        fig.add_subplot(1, 1, 1).errorbar(df.index * 2, df.average, df.stddev, linestyle=':', marker='^', capsize=3,
                                          elinewidth=0.7)
        # Convert plot to PNG image
        pngImage = io.BytesIO()
        FigureCanvas(fig).print_png(pngImage)

        # Encode PNG image to base64 string
        pngImageB64String = "data:image/png;base64,"
        pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

        return render_template('index.html', image=pngImageB64String, files=filenamelist)

        # plt.title("MES-4::GFP", fontsize=12)
        # plt.gca().set_xlabel('Gonad length', fontsize=10)
        # plt.gca().set_ylabel('Fluorescence intensity', fontsize=10)

        #save files if we want
        # for file in files:
        #     if file and allowed_file(file.filename):
        #         filename = secure_filename(file.filename)
        #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('index.html')





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)