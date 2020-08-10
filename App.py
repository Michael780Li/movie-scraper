import requests
from bs4 import BeautifulSoup as bs
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.utils import formataddr

# To send notification to email every 1 week (or at any set frequency)
# --from your email to itself--
# The website shows movies released in theatres pertaining to the week

URL = requests.get(
    'https://www.imdb.com/movies-in-theaters/?ref_=nv_mv_inth')

soup = bs(URL.content, 'html.parser')


# ask for email and password
def inputEmail():
    print("Please enter your email and password\nEmail:")
    sender_email = input()
    print("Password:")
    sender_password = input()
    sender_name = "Movies in Theatre python script"
    reciever_name = 'Subscribed Client'

    return sender_email, sender_password, sender_name, reciever_name


def main():
    # creating a SMTP session
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # encrypt email
    context = ssl.create_default_context()
    server.starttls(context=context)

    loop = True

    # loop until get email
    while(loop):
        try:
            sender_email, sender_password, sender_name, reciever_name = inputEmail()
            server.login(sender_email, sender_password)
            loop = False
            response = 'Y'
        except Exception as e:
            print("\n=====Error=====")
            response = 'N'
            loop = inputYN("Do you want to continue? (Y/N)")

    if(response == 'Y'):

        # ask if email should be sent weekly
        weekly = inputYN(
            "Would you like to be notified weekly? (Y => weekly || N => just once)")

        repeat = True
        while(repeat):
            # Web SCrape movie info from IMDB website and put into list_movies array
            container = soup.find('div', class_="list detail sub-list")

            date = container.find('h3').get_text()

            list_movies = []

            list_div_movies = soup.find_all('div', class_='list_item')

            for div_movie in list_div_movies:
                movie_title = div_movie.find('img').get('title')
                movie_cover = div_movie.find('img').get('src')
                movie_description = div_movie.find(
                    'div', class_='outline').get_text().strip()
                movie_length_tag = div_movie.find('time')
                movie_length = movie_length_tag['datetime'].strip(
                    'PT').strip('M')
                # movie_score = soup.find_all('span', class_='metascore')
                movie_score = div_movie.find('span', class_='metascore')
                if not movie_score:
                    movie_score = 'none'
                else:
                    movie_score = movie_score.get_text().strip()

                list_span_genre = div_movie.find_all('span', class_='')

                movie_genre = ''
                for ele in range(len(list_span_genre)-1):
                    movie_genre = movie_genre + \
                        list_span_genre[ele].get_text()+' '

                list_movies.append([movie_title, movie_cover, movie_description,
                                    movie_length, movie_score, movie_genre])

            # modify the html file and add movie elements
            email_html_file = open('email.html')
            email_html = email_html_file.read()

            soup_html = bs(email_html, 'html.parser')

            email_html_div = soup_html.find("div", {"id": "movie_container"})

            for index in range(len(list_movies)):
                # [movie_title, movie_cover, movie_description, movie_length, movie_score, movie_genre]
                movie_title = list_movies[index][0]
                movie_cover = list_movies[index][1]
                movie_description = list_movies[index][2]
                movie_length = list_movies[index][3]
                movie_score = list_movies[index][4]
                add_movie_html = bs('''
                <div class="card" style="background: #1d1e22;box-sizing: border-box;position: relative;display: flex;-webkit-box-orient: vertical;-webkit-box-direction: normal;-ms-flex-direction: column;flex-direction: column;min-width: 0;word-wrap: break-word;background-clip: border-box;border: 1px solid rgba(0,0,0,.125);border-radius: .25rem;">
                            <div class="row no-gutters" style="margin-left: 18%;margin-right: 0%;box-sizing: border-box;display: flex;-ms-flex-wrap: wrap;flex-wrap: wrap;">
                            <div class="col-sm-5" style="background: black;box-sizing: border-box;position: relative;width: 100%;min-height: 1px;padding-right: 15px;padding-left: 15px;-webkit-box-flex: 0;-ms-flex: 0 0 41.666667%;flex: 0 0 41.666667%;max-width: 41.666667%;">
                                <img src="'''+movie_cover+'''" class="card-img-top h-100" style="box-sizing: border-box;vertical-align: middle;border-style: none;page-break-inside: avoid;width: 100%;border-top-left-radius: calc(.25rem - 1px);border-top-right-radius: calc(.25rem - 1px);height: 100%!important;">
                            </div>
                            <div class="col-sm-7" style="background: black;max-width: 400px;box-sizing: border-box;position: relative;width: 100%;min-height: 1px;padding-right: 15px;padding-left: 15px;-webkit-box-flex: 0;-ms-flex: 0 0 58.333333%;flex: 0 0 58.333333%;">
                                <div class="card-body" style="box-sizing: border-box;-webkit-box-flex: 1;-ms-flex: 1 1 auto;flex: 1 1 auto;padding: 1.25rem;">
                                <h5 class="card-title" style="color: white;box-sizing: border-box;margin-top: 0;margin-bottom: .75rem;font-family: inherit;font-weight: 500;line-height: 1.2;font-size: 1.25rem;">'''+movie_title+'''</h5>
                                <p class="card-text" style="color: #a9a9a9;box-sizing: border-box;margin-top: 0;margin-bottom: 0;orphans: 3;widows: 3;">
                                    '''+movie_description+'''
                                    <br>
                                    <br>
                                    Movie Length: '''+movie_length+''' min<br>
                                    Metascore: ''' + movie_score + '''<br>
                                    Genre: '''+movie_genre+'''
                                </p>
                                </div>
                            </div>
                            </div>
                        </div>
                ''', 'html.parser')

                email_html_div.insert(1, add_movie_html)

            # send email
            email_body = soup_html
            msg = MIMEText(email_body, 'html')
            msg['To'] = formataddr((reciever_name, sender_email))
            msg['From'] = formataddr((sender_name, sender_email))
            msg['Subject'] = "Movies in Theater this Week " + "("+date+")"

            server.sendmail(
                sender_email,
                sender_email,
                msg.as_string()
            )
            print('\nEmail Sent!')
            if(weekly):
                # send email for every fixed amount of seconds
                time.sleep(604800)
            else:
                repeat = False

    else:
        # print email not sent if user doesn't want to continue
        print('\nEmail was not sent')
    server.quit()

# method that prints a message and returns true or false response


def inputYN(message):
    response = ''
    while (response != 'Y' and response != 'N'):
        print(message)
        response = input()

    return response == 'Y'


main()

# end of program
print('Program Terminated\n')
