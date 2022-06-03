from flask import Flask, render_template, redirect, url_for, flash, request, session
from dataframe import GermlineAnalyzer, files_to_dictionary
from grapher import plotGermline, convert_plot_to_png, encode_png_to_base64
import os
from werkzeug.utils import secure_filename
import json




# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, '/temp')

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6bAB19951993"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

cache = []

# @app.route('/plot', methods=['GET', 'POST'])
# def plot():
#     if request.method == 'POST':
#         # TODO 6: MAKE IT SAVE CONFIGURATION THAT YOU SEND
#         # TODO 7: IMPROVE CACHE FUNCTIONALITY, FIRST YOU UPLOAD FILES, THEY GET STORED, THEN YOU PLAY WITH DATA
#         # TODO 8: MAKE IT SWITCH MODE MITOTIC ZONE GRAPH
#
#         global cache, strain_cache
#
#         if 'files[]' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#
#         files = request.files.getlist('files[]')
#         strain = request.form.get('strainname').title()
#         points = request.form.get("number_of_points")
#         option = request.form.getlist('flexRadioDefault')
#         std = option[0] == "std"
#         fld = option[0] == "fold"
#         per_fld = request.form.get("rslideValues")
#         range_start = per_fld.split(" - ")[0]
#         range_end = per_fld.split(" - ")[1]
#         range_array = [int(range_start) / 100, int(range_end) / 100]
#         print("per_fld", per_fld, range_start, range_end, range_array)
#
#         # flash error if range for fold increase is not enough for 1 point
#         if fld and int(int(points) * (range_array[1] - range_array[0])) == 0:
#             flash(
#                 'Range for fold increase comparison too small. Select larger range or more number of points. Number of points * Range must be > 100')
#             return redirect(request.url)
#
#         # flash error if files are not csv
#         use_cache = False
#
#         for file in files:
#             if not allowed_file(file.filename):
#                 if cache is None:
#                     flash('Please upload only .csv (excel) files')
#                     return redirect(request.url)
#                 else:
#                     use_cache = True
#                     break
#
#         if use_cache:
#             dictionary_of_dataframes = cache
#             strain = strain_cache
#         else:
#             dictionary_of_dataframes = files_to_dictionary(files)
#
#         cache = dictionary_of_dataframes
#         strain_cache = strain
#
#         print("dict---------", dictionary_of_dataframes, "cache--------", cache)
#         print("LONGITUD FILES", len(files))
#         germline = GermlineAnalyzer(dictionary_of_dataframes, standarized=std, fold_increased=fld,
#                                     number_of_points=int(points),
#                                     percentage_for_fold_increase=range_array)
#
#         fig = plotGermline([germline.process()], title="PRUEBA",
#                            strain_name_list=[strain],
#                            file_namelist_list=[germline.return_filenames()])
#         png = convert_plot_to_png(fig)
#         b64 = encode_png_to_base64(png)
#
#         return render_template('plot.html', image=b64, files_list_list=[germline.return_filenames()],
#                                strain_name_list=[strain])
#
#     return render_template('plot.html')


# @app.route('/plot', methods=['GET',"POST"])
# def plot():
#     pass


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        n = int(request.form.get('strainsn'))
        return redirect(url_for('multiplestrains_plot', strainnumber=n))

    return render_template('index.html')


@app.route('/multiplestrains/<int:strainnumber>', methods=['GET', 'POST'])
def multiplestrains_plot(strainnumber):
    global cache
    if request.method == 'POST':
        # TODO: Store dataframes in database then retrieve them for each plot configuration
        # TODO 3: Receive mitotic graphic
        # TODO 4: Reorganize imports , .env, .gitignore and all
        # TODO OPTIONAL: Organize dataframes stored per user

        df_list = []
        strain_name_list = []
        file_namelist_list = []
        for n in range(strainnumber):
            if f'files[]{n + 1}' not in request.files:
                flash(f'No files for strain {n + 1} part')
                return redirect(request.url)

            files = request.files.getlist(f'files[]{n + 1}')
            strain = request.form.get(f'strainname{n + 1}')

            filenamelist = []
            for file in files:
                if not allowed_file(file.filename):
                    flash('Please upload only .csv (excel) files')
                    return redirect(request.url)
                filename = secure_filename(file.filename)
                filenamelist.append(filename)

            dictionary_of_dataframes = files_to_dictionary(files)
            df_list.append(dictionary_of_dataframes)
            strain_name_list.append(strain)
            file_namelist_list.append(filenamelist)

        #this need to be stored in database because is too big
        cache = df_list
        session["files_list_list"]=file_namelist_list
        session["strain_name_list"]=strain_name_list
        print(session)
        return redirect(url_for('plot', strains=strainnumber))

    return render_template('multiplestrains_plot.html', lines=strainnumber)

@app.route('/plot/<int:strains>', methods=['GET', 'POST'])
def plot(strains):

    #this need to be retrieved from database because is too big
    dataframes = cache
    strain_name_list = session.get("strain_name_list")
    files_list_list = session.get("files_list_list")
    print("retrieving session", strain_name_list,files_list_list,session["files_list_list"],dataframes)

    if request.method == 'POST':
        # TODO 8: MAKE IT SWITCH MODE MITOTIC ZONE GRAPH

        points = request.form.get("number_of_points")
        option = request.form.getlist('flexRadioDefault')
        std = option[0] == "std"
        fld = option[0] == "fold"
        per_fld = request.form.get("rslideValues")
        range_start = per_fld.split(" - ")[0]
        range_end = per_fld.split(" - ")[1]
        range_array = [int(range_start) / 100, int(range_end) / 100]
        print("per_fld", per_fld, range_start, range_end, range_array)

        # flash error if range for fold increase is not enough for 1 point
        if fld and int(int(points) * (range_array[1] - range_array[0])) == 0:
            flash(
                'Range for fold increase comparison too small. Select larger range or more number of points. Number of points * Range must be > 100')
            return redirect(request.url)

        list_of_dataframes_processed = []
        for i in range(len(dataframes)):
            germline = GermlineAnalyzer(dataframes[i], standarized=std, fold_increased=fld,
                                    number_of_points=int(points),
                                    percentage_for_fold_increase=range_array)

            list_of_dataframes_processed.append(germline.process())

        fig = plotGermline(list_of_dataframes_processed, title="PRUEBA",
                           strain_name_list=strain_name_list,
                           file_namelist_list=files_list_list)
        png = convert_plot_to_png(fig)
        b64 = encode_png_to_base64(png)

        return render_template('plot.html', strains=strains, image=b64, files_list_list=files_list_list,
                               strain_name_list=strain_name_list, npoints=int(points), range_fold=per_fld,
                               range_fold_1=int(range_start), range_fold_2=int(range_end), std=std, fld=fld)

    return render_template('plot.html', strains=strains, files_list_list=files_list_list,strain_name_list=strain_name_list,
                           npoints=50, range_fold="0-4", range_fold_1=0, range_fold_2=4, std=False, fld=False)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
