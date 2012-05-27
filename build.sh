
rm static/game/compiled.css
rm static/user/a.css
rm static/game/script.js
rm static/user/script.js
cat static/game/*.css | java -jar yuicompressor-2.4.2.jar --type css > static/game/compiled.css
cat static/user/*.css | java -jar yuicompressor-2.4.2.jar --type css > static/user/a.css
java -jar compiler.jar static/game/*.js > static/game/script.js
java -jar compiler.jar static/user/*.js > static/user/script.js


