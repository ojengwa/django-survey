Description:
survey_selenium.py script will check admin is able to log-in and log-out.
Also, it will add a new answer record and test it was successfully stored.

Disclosure:
Selenium client shouln't be here but we don't have a better way yet.

To run the selenium tests:
$ . runtests.sh

Dependencies:
~/lib/java/selenium-server.jar is assumed to exist. If it doesn't exists
you can download the distro and copy just selenium-server.jar in ~/lib/java/
This test code was tested with trunk rev: 7322

The full selenium distro can be downloaded from:
http://release.openqa.org/selenium-remote-control/0.9.2/selenium-remote-control-0.9.2-dist.zip'
