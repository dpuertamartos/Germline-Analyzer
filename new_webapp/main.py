from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from dataframe import GermlineAnalyzer, files_to_dictionary
from grapher import plotGermline, convert_plot_to_png, encode_png_to_base64
import os

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

cache = None
strain_cache = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #TODO 6: MAKE IT SAVE CONFIGURATION THAT YOU SEND
        #TODO 7: IMPROVE CACHE FUNCTIONALITY, FIRST YOU UPLOAD FILES, THEY GET STORED, THEN YOU PLAY WITH DATA
        #TODO 8: MAKE IT SWITCH MODE MITOTIC ZONE GRAPH

        global cache, strain_cache

        if 'files[]' not in request.files:

            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        strain = request.form.get('strainname').title()
        points = request.form.get("number_of_points")
        option = request.form.getlist('flexRadioDefault')
        std = option[0] == "std"
        fld = option[0] == "fold"
        per_fld = request.form.get("rslideValues")
        range_start = per_fld.split(" - ")[0]
        range_end = per_fld.split(" - ")[1]
        range_array = [int(range_start)/100,int(range_end)/100]
        print("per_fld",per_fld,range_start,range_end,range_array)

        #flash error if range for fold increase is not enough for 1 point
        if fld and int(int(points) * (range_array[1]-range_array[0])) == 0:
            flash('Range for fold increase comparison too small. Select larger range or more number of points. Number of points * Range must be > 100')
            return redirect(request.url)

        #flash error if files are not csv
        use_cache = False

        for file in files:
            if not allowed_file(file.filename):
                if cache is None:
                    flash('Please upload only .csv (excel) files')
                    return redirect(request.url)
                else:
                    use_cache = True
                    break

        if use_cache:
            dictionary_of_dataframes = cache
            strain = strain_cache
        else:
            dictionary_of_dataframes = files_to_dictionary(files)


        cache = dictionary_of_dataframes
        strain_cache = strain

        print("dict---------",dictionary_of_dataframes,"cache--------",cache)
        print("LONGITUD FILES", len(files))
        germline = GermlineAnalyzer(dictionary_of_dataframes, standarized=std, fold_increased=fld,
                                    number_of_points=int(points),
                                    percentage_for_fold_increase=range_array)

        fig = plotGermline([germline.process()], title="PRUEBA",
                           strain_name_list=[strain],
                           file_namelist_list=[germline.return_filenames()])
        png = convert_plot_to_png(fig)
        b64 = encode_png_to_base64(png)


        return render_template('index.html', image=b64, files_list_list=[germline.return_filenames()], strain_name_list=[strain])

    return render_template('index.html')

@app.route('/multiplestrains', methods=['GET', 'POST'])
def multiplestrains():
    if request.method == 'POST':
        n = int(request.form.get('strainsn'))
        return redirect(url_for('multiplestrains_plot', strainnumber=n))

    return render_template('multiplestrains.html')

@app.route('/multiplestrains/<int:strainnumber>', methods=['GET', 'POST'])
def multiplestrains_plot(strainnumber):
    if request.method == 'POST':
        #TODO: Copy configuration of single plot to multipleplot
        #TODO 3: Receive mitotic graphic
        #TODO 4: Reorganize imports , .env, .gitignore and all
        df_list=[]
        strain_name_list=[]
        file_namelist_list=[]
        for n in range(strainnumber):
            if f'files[]{n+1}' not in request.files:
                flash(f'No files for strain {n+1} part')
                return redirect(request.url)

            files = request.files.getlist(f'files[]{n+1}')
            strain = request.form.get(f'strainname{n+1}')

            for file in files:
                if not allowed_file(file.filename):
                    flash('Please upload only .csv (excel) files')
                    return redirect(request.url)

            germline = GermlineAnalyzer(files, standarized=True, number_of_points=50)
            df = germline.process()
            filenamelist = germline.return_filenames()

            df_list.append(df)
            strain_name_list.append(strain)
            file_namelist_list.append(filenamelist)

        #Create figure for the graph and plot it
        print(strain_name_list,file_namelist_list)
        fig = plotGermline(df_list, title="PRUEBA",
                           strain_name_list=strain_name_list,
                           file_namelist_list=file_namelist_list)
        png = convert_plot_to_png(fig)
        b64 = encode_png_to_base64(png)

        return render_template('multiplestrains_plot.html', lines=strainnumber, image_multiple=b64, files_list_list=file_namelist_list, strain_name_list=strain_name_list)

    return render_template('multiplestrains_plot.html', lines=strainnumber)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)