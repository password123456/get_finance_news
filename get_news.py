#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import time
from BeautifulSoup import BeautifulSoup

# LOG SETTING
LOG_HOME = '/data/script/python/naver_stock/logs'
LOG_FILE = '/data/script/python/naver_stock/logs/%s.txt' % time.strftime('%Y.%m.%d')


# ssl exceptions
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass
try:
    ssl._create_default_https_context = ssl._create_unverified_context  # SSL: CERTIFICATE_VERIFY_FAILED
except:
    pass


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def ARTICLE_IN_DB(_ARTICLE_NUM):
    try:
        if os.path.exists(LOG_FILE):
            mode = 'r'
        else:
            mode = 'w'

        with open(LOG_FILE, mode) as database:
            for line in database:
                if _ARTICLE_NUM in line:
                    return True
        return False
    except:
        pass


def NOTIFY_TO_TELEGRAM(to, msg):
    bot_id = "YOUR BIT ID"
    base_url = "https://api.telegram.org/bot" + bot_id + "/sendMessage"

    headers = { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36' }

    param = { 'chat_id': to, 'text': msg }

    try:
        r = requests.post(base_url, data=param, headers=headers, verify=False)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print "%s[-] Exception::%s%s" % (bcolors.WARNING, e, bcolors.ENDC)


def GET_PAGE_NUMBERS():
    try:
        url = 'https://finance.naver.com/news/mainnews.nhn?date=%s' % time.strftime('%Y-%m-%d')

        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
                    'content-type': 'text/html; charset=UTF-8'
                  }
                  
        r = requests.get(url, headers=headers)
        body = r.text
        soup = BeautifulSoup(body)
        result = soup.find('td', {'class': 'pgRR'})

        if result:
            result_url  = result.find('a').get('href')
            page_id_split = result_url.split('=')
            total_page_count = page_id_split[2]
            #print total_page_count
        else:
            total_page_count = 1

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print "%s[-] Exception::%s%s" % (bcolors.WARNING, e, bcolors.ENDC)
    else:
        r.close()

    #print total_page_count
    return total_page_count


def GET_NEWS():
    try:
        page_count = int(GET_PAGE_NUMBERS())

        total_parse_source = []
        for page_number in range(1, page_count+1):
            url = 'https://finance.naver.com/news/mainnews.nhn?date=%s' % time.strftime('%Y-%m-%d')
            headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
                        'content-type': 'text/html; charset=UTF-8'
                      }
            r = requests.get(url, headers=headers)
            body = r.text
            soup = BeautifulSoup(body)

            result = soup.findAll(['dt','dd'], {'class': 'articleSubject'})
            total_parse_source = total_parse_source + result

        r.close()

        if total_parse_source:
            message = ''

            for news_index in total_parse_source:
                result = news_index.find('a')
                news_url = result['href']
                news_title = result.text

                news_id_split = news_url.split('=')
                news_id_split1 = news_id_split[1]
                news_id_split2 = news_id_split1.split('&')
                news_id_num = news_id_split2[0]

                try:
                    if os.path.exists(LOG_FILE):
                        mode = 'a'
                    else:
                        mode = 'w'
                    with open(LOG_FILE, mode) as append_database:
                        if not ARTICLE_IN_DB(news_id_num):
                            append_database.write(str(news_id_num) + ',' + 'https://finance.naver.com' + news_url + '\n')
                            message_link = '[+] ' + news_title + '\n  https://finance.naver.com' + news_url + '\n'
                            message+=message_link
                    append_database.close()
                except Exception as e:
                    print "%s[-] Exception::%s%s" % (bcolors.WARNING, e, bcolors.ENDC)

            if message:
                NOTIFY_TO_TELEGRAM('CHAT_ROOM_NUMBER', message)
                print '%s%s%s' % (bcolors.OKBLUE, message, bcolors.ENDC)
            else:
                print '%sNO NEWS%s' % (bcolors.WARNING, bcolors.ENDC)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print "%s[-] Exception::%s%s" % (bcolors.WARNING, e, bcolors.ENDC)


def main():

    GET_NEWS()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception, e:
        print '%s[-] Exception::%s%s' % (bcolors.WARNING, e, bcolors.ENDC)
