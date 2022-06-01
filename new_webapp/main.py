from flask import Flask, render_template, redirect, url_for, flash, request
from dataframe import GermlineAnalyzer
from grapher import plotGermline, convert_plot_to_png, encode_png_to_base64

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6bAB19951993"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        strain = request.form.get('strainname').title()

        #flash error if files are not csv

        for file in files:
            if not allowed_file(file.filename):
                flash('Please upload only .csv (excel) files')
                return redirect(request.url)

        germline = GermlineAnalyzer(files, standarized=False, number_of_points=33)
        fig = plotGermline([germline.process()], title="PRUEBA",
                           strain_name_list=[strain],
                           file_namelist_list=[files])
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

            germline = GermlineAnalyzer(files, standarized=False, number_of_points=33)
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