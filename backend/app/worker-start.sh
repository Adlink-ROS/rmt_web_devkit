#指明队列名称
ps -ux|grep 'celery'|grep -v grep|awk '{print $2}'|xargs kill -9
echo "Start running celery workers in the background"
nohup celery -A app.celery_app.worker.example worker -l info -Q example-queue -c 1 > celery.log &

