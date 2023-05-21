FROM python:3.10-bullseye
RUN pip install watchdog
RUN pip install python-telegram-bot
RUN mkdir -p /home/app/podcasts
ADD scanAndPush.py . 
CMD ["python", "-u", "scanAndPush.py", "/home/app/podcasts"]