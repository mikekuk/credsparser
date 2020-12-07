import subprocess
import os
import psycopg2
from getpass import getpass
import re
import pandas as pd

password = getpass('Enter Password')

# file_name = 'data'

format1 = re.compile(r'\S+\@(\S+|^(:|;)):.+')
format2 = re.compile(r'\S+\@(\S+|^(:|;));.+')
colon_in_un = re.compile(r'\S+:\S+\@\S+\.\S+(:|;).+')

# parses content of text file into list of username, passowrd and dormain
def parse(file_name):
    rejected_lines = open('others.txt', 'a')

    def execute(un, pw, domain):
        cur.execute(f"""INSERT INTO test (username, password, domain) VALUES (\'{un}\', \'{pw}\', \'{domain}\');""")
    
    def replace_quotes(line):
        new_line = line.replace("""\'""", """\'\'""")
        newer_line = new_line.replace("""\"""", """\"\"""")
        return newer_line

    with open(file_name, encoding="latin-1") as text:
        conn = psycopg2.connect(f"dbname=Mike user=Mike password={password}")
        cur = conn.cursor()
        for line in text:
            if re.match(format1, line) and not re.match(colon_in_un, line):
                line = replace_quotes(line)
                try:
                    un, pw = line.split(':', 1)
                    pw = pw[:-1]
                except:
                    un = line
                    pw = None
                if "@" in un:
                    domain = un.split("@")[-1].lower()
                else:
                    domain = un
                execute(un, pw, domain)
            elif re.match(format2, line) and not re.match(colon_in_un, line):
                line = replace_quotes(line)
                try:
                    un, pw = line.split(';', 1)
                    pw = pw[:-1]
                except:
                    un = line
                    pw = None
                if "@" in un:
                    domain = un.split("@")[-1].lower()
                else:
                    domain = un
                execute(un, pw, domain)
            else:
                rejected_lines.write(line)
        conn.commit()


def exercute():
    colnames = ['file', 'status']
    files_done = pd.read_csv('log.csv', names=colnames)

    def file_done(file):
        return (file in files_done['file'].tolist())

    files = subprocess.run("find data -print | sort", shell=True, text=True, capture_output = True).stdout.split("\n")[:-1]
    count = 0
    total = len(files)
    for file in files:
        if not file_done(file):
            try:
                if os.path.isfile(file) and ("." not in file):
                    count += 1
                    print(f'starting {file}')
                    parse(file)
                    with open('log.csv', 'a') as log:
                        log.write(f'{file}, Sucess \n')
                    print(f"completed {count + len(files_done)} of {total} files")
            except:
                with open('log.csv', 'a') as log:
                        log.write(f'{file}, Fail \n')
                pass
        else:
          pass

exercute()





