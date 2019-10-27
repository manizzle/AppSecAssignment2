from flask import Flask, render_template, request, redirect, url_for, make_response
import os, os.path
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template")
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = "shitlick"
import threading
lock = threading.Lock()
import tempfile
import shlex
import subprocess
import hashlib
import os
import time

secret = "sup3rs3cr3t"

user_dict = {}
user_login = {}
csrf_tok = []


@app.route('/')
def root():
    return redirect(url_for('register'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        if (data["uname"] and data["pword"]) and data["uname"] not in user_dict:
            lock.acquire()
            try:
                user_dict[data["uname"]] = {"password": data["pword"], "2fa": data["2fa"]}
            finally:
                # Always called, even if exception is raised in try block
                lock.release()
            ret = "success"
        else:
            ret = "failure"
        return render_template("success.html", message=ret)
    else:
        return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        if (data["uname"] and data["pword"]) and (data["uname"] in user_dict) and (user_dict[data["uname"]]["password"] == data["pword"]):
            ret = "success"
            if user_dict[data["uname"]]["2fa"] and user_dict[data["uname"]]["2fa"] != data["2fa"]:
                ret = "Two-factor - failure"
        else:
            ret = "Incorrect"
        if ret == "success":
            resp = make_response(render_template("success_login.html", message=ret))
            ts = time.time()
            cookie = hashlib.sha256((data["uname"] + data["pword"] + data["2fa"] + str(ts) + secret).encode("utf-8")).hexdigest()
            user_login[cookie] = {"uname": data["uname"], "ts": ts}
            resp.set_cookie('auth', cookie)
            return resp
        return render_template("success_login.html", message=ret)
    else:
        return render_template("login.html")

@app.route("/spell_check", methods=["GET", "POST"])
def spellcheck():
    cookie = request.cookies.get('auth')
    if not cookie:
        return redirect(url_for('login'))
    if cookie not in user_login:
        return redirect(url_for('login'))
    if (time.time() - user_login[cookie]["ts"]) > (60*10):
        return redirect(url_for('login'))

    if request.method == "POST":

        data = request.form
        csrf_prot = data["csrf-token"]
        if not csrf_prot:
            return redirect(url_for('login'))
        if csrf_prot not in csrf_tok:
            return redirect(url_for('login'))
        csrf_tok.remove(csrf_prot)


        inputdata = ""
        for c in data["inputtext"]:
            if c in ":///\';\"%.?<>()":
                inputdata += "//" + c
            else:
                inputdata += c

        fp = tempfile.NamedTemporaryFile(delete=False)
        if not inputdata:
            return redirect(url_for('spell_check'))
        fp.write(inputdata.encode("utf-8"))
        fp.close()
        cmd = "./a.out %s wordlist.txt"
        args = shlex.split(cmd % fp.name)
        outs, errs = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        os.unlink(fp.name)
        if errs:
            return render_template("errors.html")
        bad_words = ",".join([o.split("misspelled word:")[1] for o in outs.decode("utf-8").splitlines()])
        return render_template("return.html", textout=inputdata, misspelled=bad_words)
    else:
        tok = hashlib.sha256((str(time.time()) + cookie).encode("utf-8")).hexdigest()
        csrf_tok.append(tok)
        return render_template("spellcheck.html", token=tok)

if __name__ == '__main__':
        app.run(host="0.0.0.0", port=8081, debug=True)