import unittest
import requests
import re

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

    def test_badflow(self):
        resp = requests.post("http://localhost:8081/register", data={"uname": "user", "pword": "test"}).content
        self.assertTrue("failure" in resp.decode("utf-8"))
        resp = requests.post("http://localhost:8081/spell_check", data={"inputtext": "somestuff"}).content
        self.assertTrue("2-Factor Phonenumber:" in resp.decode("utf-8"))

if __name__ == '__main__':
    unittest.main()
