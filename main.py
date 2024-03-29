from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from dataframe import GermlineAnalyzer, files_to_dictionary, read_mitotic_file_into_average, \
    extract_length, calculate_average_length, determine_same_length_units, extract_min_length
from grapher import plotGermline, convert_plot_to_png, encode_png_to_base64
import pandas as pd
import os
from werkzeug.utils import secure_filename
import random
import json
import sys
import webbrowser
import logging
from waitress import serve
import socket


if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['csv'])
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6bAB19951993"

# Using a Python dictionary as a temporary storage
storage = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        n = int(request.form.get('strainsn'))
        return redirect(url_for('multiplestrains_plot', strainnumber=n))

    return render_template('index.html')


@app.route('/multiplestrains/<int:strainnumber>', methods=['GET', 'POST'])
def multiplestrains_plot(strainnumber):
    if request.method == 'POST':
        # TODO 3: Fix get starter guide
        # TODO 4: Reorganize imports , .env, .gitignore and all
        # TODO OPTIONAL: Organize dataframes stored per user
        option = request.form.get('flexswitch')
        mitotic_graph = option == "on"
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

        id = str(random.randint(0,10000000))
        # storing DF to database(table name=strain name+file name)
        for i in range(len(df_list)):
            dfs_to_write = []
            for key in df_list[i]:
                dfs_to_write.append(df_list[i][key].to_json())
                storage[strain_name_list[i] + key + id] = df_list[i][key].to_json()

        session["id"] = id
        session["files_list_list"] = file_namelist_list
        session["strain_name_list"] = strain_name_list
        if mitotic_graph:
            return redirect(url_for('mitotic_graph',strains=strainnumber))
        else:
            session["mitotic_mode"] = "False"
            return redirect(url_for('plot', strains=strainnumber))

    return render_template('multiplestrains_plot.html', lines=strainnumber)

@app.route('/mitotic_graph/<int:strains>',methods=['GET','POST'])
def mitotic_graph(strains):
    strain_name_list = session.get("strain_name_list")
    if request.method == 'POST':
        result = []
        result_std = []
        for n in range(strains):

            file = request.files.getlist(f'file1{n}')[0]
            if not allowed_file(file.filename):
                flash('Please upload only .csv (excel) files')
                return redirect(request.url)
            av, dv = read_mitotic_file_into_average(file)
            result.append(av)
            result_std.append(dv)

        session["mitotic_zone"] = result
        session["mitotic_zone_error"] = result_std
        session["mitotic_mode"] = "True"
        return redirect(url_for('plot', strains=strains))

    return render_template('mitotic_graph.html', strains=strains, strains_names=strain_name_list)


@app.route('/plot/<int:strains>', methods=['GET', 'POST'])
def plot(strains):
    #TODO 1: LET USER PERMANTENT STORE THEIR DATA
    #TODO 2: FIX MOBILE INTERFACE(NUMBER OF STRAINS SELECTOR AND POSS OTHER)
    #TODO 3: CLEAN CODE
    #TODO 5: IMPROVE AESTHETIC OF GONAD LENGTH

    id = session.get("id")
    mitotic_graph_info = session.get("mitotic_zone")
    mitotic_graph_error = session.get("mitotic_zone_error")
    mitotic_files_loaded = session.get("mitotic_mode") == "True"
    strain_name_list = session.get("strain_name_list")
    files_list_list = session.get("files_list_list")

    # def retrieve_from_db:
    dataframes = []
    for x in range(len(strain_name_list)):
        dictio = {}
        s = strain_name_list[x]
        for j in range(len(files_list_list[x])):
            f = files_list_list[x][j]
            raw = storage.get(s + f + id)
            dictio[f] = pd.read_json(raw)
        dataframes.append(dictio)

    #extract lenght info
    final_length_list = extract_length(dataframes)
    average_length = calculate_average_length(final_length_list, strain_name_list)
    min_length = extract_min_length(final_length_list)
    determine_units = determine_same_length_units(final_length_list)
    can_absolute_length = determine_units[0]
    unit = determine_units[1]



    if request.method == 'POST':
        option_switch = request.form.get('flexswitch2')
        abs_switch = request.form.get('flexswitchabs')
        mitotic_switched_on = option_switch == "on"
        abs_switched_on = abs_switch == "on"
        if abs_switched_on:
            mitotic_switched_on = False
        abs = None
        to_show_abs = int(min_length)
        if abs_switched_on:
            abs = int(request.form.get("abslengthtxt"))
            if abs > int(min_length):
                abs = int(min_length)
            to_show_abs = abs
        points = request.form.get("number_of_points")
        dpi = int(request.form.get("dpi"))
        if dpi > 500:
            dpi = 500
        option = request.form.getlist('flexRadioDefault')
        std = option[0] == "std"
        fld = option[0] == "fold"
        per_fld = request.form.get("rslideValues")
        range_start = per_fld.split(" - ")[0]
        range_end = per_fld.split(" - ")[1]
        range_array = [int(range_start) / 100, int(range_end) / 100]
        option2 = request.form.getlist('flexRadioLength')
        px = option2[0] == "px"
        mc = option2[0] == "mc"
        gcd = option2[0] == "gcd"
        convert_ratio = float(request.form.get("convert_ratio"))
        convert_ratio_finale = None
        if can_absolute_length:
            if px:
                if "pixel" in unit:
                    convert_ratio_finale = 1
                else:
                    px = False
            elif mc:
                if "pixel" in unit:
                    convert_ratio_finale = convert_ratio
                elif "micr" in unit:
                    convert_ratio_finale = 1
                else:
                    mc = False
            elif gcd:
                if "pixel" in unit:
                     #micron to gcd ratio is hardcoded as 1/3.5
                    convert_ratio_finale = convert_ratio / 3.5
                elif "micr" in unit:
                    convert_ratio_finale = 1 / 3.5
                else:
                    gcd = False


        # flash error if range for fold increase is not enough for 1 point
        if fld and int(int(points) * (range_array[1] - range_array[0])) == 0:
            flash(
                'Range for fold increase comparison too small. Select larger range or more number of points. Number of points * Range must be > 100')
            return redirect(request.url)

        list_of_dataframes_processed = []
        for i in range(len(dataframes)):
            germline = GermlineAnalyzer(dataframes[i], standarized=std, fold_increased=fld,
                                    number_of_points=int(points),
                                    percentage_for_fold_increase=range_array, absolute_length=abs)

            list_of_dataframes_processed.append(germline.process())
            

        fig = plotGermline(list_of_dataframes_processed, title="",
                           strain_name_list=strain_name_list,
                           file_namelist_list=files_list_list,
                           mitotic_mode=mitotic_switched_on,
                           strains_mitotic_percentage=mitotic_graph_info, strains_error=mitotic_graph_error,
                           dpi=dpi, average_length=average_length, absolute_cut=abs,
                           conversion=convert_ratio_finale,
                           x_label=[px, mc, gcd], y_label=[std, fld, [range_start, range_end]])
        png = convert_plot_to_png(fig)
        b64 = encode_png_to_base64(png)

        return render_template('plot.html', strains=strains, image=b64, files_list_list=files_list_list,
                               strain_name_list=strain_name_list, lengths_list_list=final_length_list,
                               min_length=min_length, current_length=to_show_abs,
                               average_length=average_length,
                               can_absolute_length=can_absolute_length, absolute_length_selected = abs_switched_on,
                               npoints=int(points), range_fold=per_fld,
                               range_fold_1=int(range_start), range_fold_2=int(range_end), std=std, fld=fld, dpi=dpi,
                               mitotic=mitotic_files_loaded, mitotic_switched_on=mitotic_switched_on, px=px, mc=mc, gcd=gcd, convert_ratio=convert_ratio)

    return render_template('plot.html', strains=strains, files_list_list=files_list_list,strain_name_list=strain_name_list,
                           lengths_list_list=final_length_list, min_length=min_length, current_length=min_length,
                           average_length=average_length,
                           can_absolute_length=can_absolute_length, absolute_length_selected=False,
                           npoints=50, range_fold="0-4", range_fold_1=0, range_fold_2=4, std=False, fld=False, dpi=100,
                           mitotic=mitotic_files_loaded, mitotic_switched_on=True, px=False, mc=False, gcd=False, convert_ratio=0.22)


@app.route('/trial', methods=['GET'])
def trial():
    def resource_path(relative_path):
        """ Get the absolute path for bundled data files in PyInstaller. """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    session["mitotic_zone"] = [22.89]
    session["mitotic_zone_error"] = [3.69]
    session["mitotic_mode"] = "True"
    id = str(random.randint(0, 100000))
    session["id"] = id
    strain_name_list = ["MES-4::GFP"]

    # Use the resource_path function to get the right path
    files = [
        resource_path("Values/Values1.csv"),
        resource_path("Values/Values2.csv"),
        resource_path("Values/Values3.csv"),
        resource_path("Values/Values4.csv"),
        resource_path("Values/Values5.csv"),
        resource_path("Values/Values6.csv"),
    ]

    session["files_list_list"] = [[f.split("/")[-1] for f in files]]
    session["strain_name_list"] = strain_name_list

    # Storing DF to database
    df_list = [pd.read_csv(f).to_json() for f in files]
    for i in range(len(files)):
        storage["MES-4::GFP" + files[i].split("/")[-1] + id] = df_list[i]

    return redirect(url_for('plot', strains=1))


if __name__ == "__main__":
    # Suppress Flask's default logs
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    # Suppress Waitress's warnings
    waitress_logger = logging.getLogger('waitress')
    waitress_logger.setLevel(logging.ERROR)

    # Determine the machine's local IP address
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        print("local ip could not be detected")
        print(f"complete error -> {str(e)}")
        local_ip = "error"

    # Display custom message
    print(f"Application will be deployed on http://{local_ip}:5000/")
    print("Opening browser...")

    # Open the web browser
    try:
        webbrowser.open(f"http://{local_ip}:5000/")
    except Exception as e:
        print(f"browser could not be automatically opened on http://{local_ip}:5000/ . You can open it manually")

    print("Close this window to finish 'Germline-Analyzer' execution")
    # Run the Flask app
    try:
        serve(app, host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Application could not be deployed in http://{local_ip}:5000/ , try to open port 5000")
        print(f"complete error -> {str(e)}")





