from selenium import selenium
import unittest, time, re

class NewTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*firefox", "http://localhost:8000/")
        self.selenium.start()
    
    def test_new(self):
        sel = self.selenium
        sel.open("http://localhost:8000/")
        sel.click("link=admin")
        sel.wait_for_page_to_load("30000")
        sel.type("id_username", "admin")
        sel.type("id_password", "admin")
        sel.click("//input[@value='Log in']")
        sel.open("/admin/logout/")
        try: self.failUnless(sel.is_text_present("Logged out"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.open("/")
        try: self.failUnless(sel.is_text_present("Example Survey"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=Example Survey")
        sel.wait_for_page_to_load("30000")
        sel.select("id_1_3-answer", "label=third")
        sel.type("id_1_2-answer", "Test 3")
        sel.click("id_1_4-answer_0")
        sel.click("id_1_5-answer_1")
        sel.click("__vote")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Example Survey - Results (3 Submissions)"))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
