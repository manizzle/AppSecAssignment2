import unittest
import requests
import re
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import app
import thread
import time

class TestStringMethods(unittest.TestCase):

    def test_normalflow(self):
        session = requests.Session()
        resp = session.post("http://localhost:8081/register", data={"uname": "user", "pword": "test", "2fa": ""}).content
        self.assertTrue("success" in resp.decode("utf-8"))
        resp = session.post("http://localhost:8081/login", data={"uname": "user", "pword": "test", "2fa": ""}).content
        self.assertTrue("success" in resp.decode("utf-8"))
        resp = session.get("http://localhost:8081/spell_check").content
        token = re.findall("csrf-token.*>", resp.decode("utf-8"))[0].split("=")[1].split(">")[0]
        resp = session.post("http://localhost:8081/spell_check", data={"inputtext": "somestuff", "csrf-token": token}).content
        self.assertTrue("misspelled" in resp.decode("utf-8"))
        print("yay")

    def test_badflow(self):
        session = requests.Session()
        resp = session.post("http://localhost:8081/register", data={"uname": "user", "pword": "test"}).content
        print(resp)
        self.assertTrue("failure" in resp.decode("utf-8"))
        resp = session.post("http://localhost:8081/spell_check", data={"inputtext": "somestuff"}).content
        self.assertTrue("2-Factor Phonenumber:" in resp.decode("utf-8"))



if __name__ == '__main__':
    thread.start_new_thread(app.app.run, ("0.0.0.0", 8081, False),)
    time.sleep(1)
    unittest.main()
