cd ../examples
rm examples.db
svn update examples.db
python manage.py runserver 1>/dev/null 2>/dev/null &
cd ../tests
java -jar ~/lib/java/selenium-server.jar 1>/dev/null 2>/dev/null &
sleep 5
python survey_selenium.py
kill %2
kill %1
cd ../examples
rm examples.db
svn update examples.db
cd ../tests
