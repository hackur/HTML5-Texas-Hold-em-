
DIR="$( cd "$( dirname "$0" )" && pwd )"
echo $DIR
pypy $DIR/../robot.py -P 8001 -U human1 &
pypy $DIR/../robot.py -P 8001 -U human2 &
