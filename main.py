from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, make_response, Response
from dataframe import GermlineAnalyzer, files_to_dictionary, read_mitotic_file_into_average, \
    extract_length, calculate_average_length, determine_same_length_units, extract_min_length
from grapher import plotGermline, convert_plot_to_png, encode_png_to_base64, extract_x_label, extract_y_label, \
    calculate_x_axis_points
import pandas as pd
import os
from werkzeug.utils import secure_filename
import random
import sys
import zipfile
import io

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


def download_dataframes(dataframe_dict, format="csv"):
    single_file = len(dataframe_dict) == 1
    buffer = io.BytesIO()

    if single_file:
        # If only one dataframe, directly return the file
        key, df = next(iter(dataframe_dict.items()))
        if format == "csv":
            df.to_csv(buffer, index=False)
            mimetype = 'text/csv'
            filename = f"{key}.csv"
        elif format == "xls":
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            mimetype = 'application/vnd.ms-excel'
            filename = f"{key}.xlsx"
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.mimetype = mimetype
        return response
    else:
        # Create a Zip file if multiple dataframes
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, df in dataframe_dict.items():
                # Use a BytesIO buffer for each file in the zip
                file_buffer = io.BytesIO()
                if format == "csv":
                    df.to_csv(file_buffer, index=False)
                    file_buffer.seek(0)
                    zip_file.writestr(f"{filename}.csv", file_buffer.getvalue())
                elif format == "xls":
                    with pd.ExcelWriter(file_buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    file_buffer.seek(0)
                    zip_file.writestr(f"{filename}.xlsx", file_buffer.getvalue())
        buffer.seek(0)
        return Response(
            buffer.getvalue(),
            mimetype='application/zip',
            headers={'Content-Disposition': 'attachment;filename=data.zip'}
        )


def combine_dataframes_for_file(dataframes, additional_data=None):
    # Transpose dataframes and create a new DataFrame with each as a column
    combined_df = pd.DataFrame()

    for i, df in enumerate(dataframes):
        combined_df = pd.concat([combined_df, dataframes[i]], axis=1)

    # Add additional data columns if provided
    if additional_data:
        for key, value in additional_data.items():
            combined_df[key] = value

    c = combined_df.columns.tolist()
    if 'length_unit' in c and 'length_interval_start' in c:
        c.remove('length_unit')
        start_index = c.index('length_interval_start')
        c.insert(start_index + 1, 'length_unit')
        combined_df = combined_df[c]

    return combined_df


def process_plot_request(request, unit, min_length, can_absolute_length ):
    action = request.form.get('action')

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
                # micron to gcd ratio is hardcoded as 1/3.5
                convert_ratio_finale = convert_ratio / 3.5
            elif "micr" in unit:
                convert_ratio_finale = 1 / 3.5
            else:
                gcd = False
    return action, px, mc, gcd, convert_ratio_finale, convert_ratio, std, fld, per_fld, range_array, \
           mitotic_switched_on, abs_switched_on, abs, points, dpi, to_show_abs, range_start, range_end


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

        action, px, mc, gcd, convert_ratio_finale, convert_ratio, std, fld, per_fld, range_array, \
        mitotic_switched_on, abs_switched_on, abs, points, dpi, to_show_abs, range_start, range_end = process_plot_request(request, unit, min_length, can_absolute_length)

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

        if "Export" in action:
            additional_data = {
                'length_unit': extract_x_label([px, mc, gcd]),
                'fluorescence_unit': extract_y_label([std, fld, [range_start, range_end]])
            }

            x_axis_points_array = calculate_x_axis_points(list_of_dataframes_processed, convert_ratio_finale, abs,
                                                    average_length,
                                                    middle_point=False)

            x_axis_df = pd.DataFrame(x_axis_points_array, columns=['length_interval_start'])
            dataframes = {}
            for i, df in enumerate(list_of_dataframes_processed):
                final_dataframe = combine_dataframes_for_file([x_axis_df]+[df], additional_data)
                dataframes[strain_name_list[i]] = final_dataframe

            format = "csv" if action == "Export .csv" else "xls"
            return download_dataframes(dataframes, format)

        else:
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
    session["mitotic_zone"] = [22.89]
    session["mitotic_zone_error"] = [3.69]
    session["mitotic_mode"] = "True"
    id = str(random.randint(0, 100000))
    session["id"] = id
    strain_name_list = ["MES-4::GFP"]
    full_path = "C:/Users/David/PycharmProjects/Germline-Analyzer"
    files = ["/Values/Values1.csv", "/Values/Values2.csv", "/Values/Values3.csv",
             "/Values/Values4.csv", "/Values/Values5.csv", "/Values/Values6.csv"]
    files = [full_path+f for f in files]
    session["files_list_list"] = [[f.split("/")[-1] for f in files]]
    session["strain_name_list"] = strain_name_list
    #storing DF to database
    df_list = [pd.read_csv(f).to_json() for f in files]
    for i in range(len(files)):
        storage["MES-4::GFP"+files[i].split("/")[-1]+id] = df_list[i]

    return redirect(url_for('plot', strains=1))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)