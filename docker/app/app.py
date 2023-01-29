#!/usr/bin/env python3

import logging
import os
import subprocess
import tarfile
from pathlib import Path

from docker.app.lib.gatekeeper import gatekeeper_io
from flask import Flask, jsonify, make_response, render_template, request, send_file
from flask_cors import CORS, cross_origin


STATIC_DIR = '/var/www/app/static/'
OPENSYNC_ROOT = os.getenv('OPENSYNC_ROOT', '/home/plume/fut-base')
BUILDS_DIR = f'{OPENSYNC_ROOT}/builds/'
REPORTS_DIR = f'{STATIC_DIR}/reports/'
ALLURE_PATH = '/opt/allure/bin/allure'
FUT_ENV_NAMES = ['DUT_CFG_FOLDER', 'REF_CFG_FOLDER', 'CLIENT_CFG_FOLDER']


app = Flask(__name__, static_folder='static')
fut_cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, expose_headers=["x-suggested-filename"])

gatekeeper_log_file = '/tmp/fut_gatekeeper.log'
gatekeeper_logger = logging.getLogger('GatekeeperLogger')
gatekeeper_logger_fh = logging.FileHandler(gatekeeper_log_file, mode='w')
gatekeeper_logger.setLevel(logging.DEBUG)
gatekeeper_logger.addHandler(gatekeeper_logger_fh)


@app.route("/")
@cross_origin()
def home():
    return render_template('home.html')


@app.route("/get_builds")
def get_builds():
    # not possible to use Path.lstat().st_mtime as key
    return jsonify({'success': True, 'data': [str(Path(i).absolute().name) for i in sorted(Path(BUILDS_DIR).iterdir(), key=os.path.getmtime, reverse=True)]})


@app.route("/get_allure")
def get_allure():
    build_name = request.args.get('build_name')
    rebuild = True if request.args.get('rebuild') in ['true', 'True', True] else False
    report_url = f'/static/reports/{build_name}/index.html'
    report_dir = REPORTS_DIR + build_name
    if Path(REPORTS_DIR + build_name).is_dir():
        if not rebuild:
            return jsonify({'success': True, 'url': report_url})
        else:
            os.system(f'sudo rm -rf {report_dir}')
    cmd = f'{ALLURE_PATH} generate -o {REPORTS_DIR}{build_name} {BUILDS_DIR}{build_name}'
    cmd = cmd.split()
    cmd_pass = subprocess.Popen(
        ['echo', 'plume'],
        stdout=subprocess.PIPE,
    )
    cmd_process = subprocess.Popen(
        ['sudo', '-S'] + cmd,
        stdin=cmd_pass.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    cmd_process.communicate()
    exit_code = cmd_process.returncode
    return jsonify(
        {
            'success': exit_code == 0,
            'msg': 'Error while generating' if exit_code != 0 else build_name,
            'url': report_url,
            'cmd': cmd,
        },
    )


@app.route("/download_allure")
def download_allure():
    build_name = request.args.get('build_name')
    report_folder = f'{REPORTS_DIR}/{build_name}/'
    tarfile_name = f'{build_name}.tar.gz'
    tarfile_path = f'{REPORTS_DIR}/{tarfile_name}'
    with tarfile.open(tarfile_path, "w:gz") as tar:
        tar.add(report_folder, arcname=Path(report_folder).name)
    result = send_file(tarfile_path,
                       mimetype="application/gzip",
                       as_attachment=True,
                       conditional=False)
    result.headers["x-suggested-filename"] = tarfile_name
    return result


@app.route("/delete_allure")
def delete_allure():
    build_name = request.args.get('build_name')
    report_folder = f'{REPORTS_DIR}/{build_name}/'
    build_folder = f'{BUILDS_DIR}/{build_name}/'
    res_1 = os.system(f'sudo rm -rf {report_folder}')
    res_2 = os.system(f'sudo rm -rf {build_folder}')
    return jsonify(
        {
            'success': res_1 == 0 and res_2 == 0,
        },
    )


@app.route('/fut-base/<path:path>')
def get_fut_file(path):
    return app.send_static_file('fut-base/' + path)


@app.route("/gatekeeper", methods=["GET", "POST"])
def gatekeeper_api():
    if request.method == "GET":
        m = "This is GET call"
        gatekeeper_logger.info(m)
        foo = {"foo": "foo_val", "bar": {"subbar": "subbar_val"}}
        response = make_response(jsonify(foo))
        return response

    if request.method == "POST":
        m = "This is POST call to gatekeeper"
        gatekeeper_logger.info(m)
        req = gatekeeper_io.Req(request, logger=gatekeeper_logger)
        response = req.deserialize()
        return response


@app.route("/gatekeeper/test/<path:path>", methods=["GET", "POST"])
def gatekeeper_test(path):
    return {
        'success': True,
        'url_path': f'fut.opensync.io/gatekeeper/test/{path}',
    }


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
