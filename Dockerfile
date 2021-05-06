FROM python:3.7
ADD . /bot
WORKDIR /bot
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]