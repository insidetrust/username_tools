import requests
from bs4 import BeautifulSoup
import logging
import time
import argparse
import json
import re
import os


class LinkedInSearch(object):

    def __init__(self, token, proxy):
        self.token = token
        self.params = {}
        if proxy == '':
            self.verify = True
            self.proxy_dict = {}
        else:
            self.verify = False
            requests.packages.urllib3.disable_warnings()

            # Define burp proxy here
            http_proxy = "http://" + proxy
            https_proxy = "https://" + proxy
            ftp_proxy = "ftp://" + proxy

            self.proxy_dict = {
                "http": http_proxy,
                "https": https_proxy,
                "ftp": ftp_proxy
            }

        self.headers = {"Cookie": "li_at=" + token}
        self.found_names = {}

    def check_login(self):
        # If you want this to go through burp etc. use this proxy definition

        logging.getLogger("requests").setLevel(logging.WARNING)

        response = requests.get("https://www.linkedin.com/nhome", headers=self.headers,
                                proxies=self.proxy_dict, verify=self.verify)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            name_tag = soup.find('a', {'class': 'act-set-name-split-link', 'href': True})

            if name_tag is None:
                print("Login failed")
                exit(2)
            else:
                print("Login success")
                print name_tag.text

    def do_search(self, params):
        self.params = params
        r = requests.get("https://www.linkedin.com/vsearch/pj", params=self.params, headers=self.headers,
                         proxies=self.proxy_dict, verify=self.verify)

        if r.status_code == 200:
            if "reached the commercial use limit on search" in r.text:
                print("Oh dear! We've reached the commercial use limit on search. Use another account.")
                exit(0)
            if "<!DOCTYPE html>" in r.text:
                print(
                    "Not a JSON response = session has probably expired. Update the 'session_token' value to the"
                    "'li_at' cookie of a current session.")
                exit(0)
            json_data = json.loads(r.text)

            if len(json_data['content']['page']['voltron_unified_search_json']['search']['results']) == 0:
                print("No more results found")
                exit(0)
            for result in json_data['content']['page']['voltron_unified_search_json']['search']['results']:
                if 'person' in result:
                    # print result['person']['fmt_name']

                    linkedin_id = result['person']['id']

                    last_name_raw = result['person']['degree_result_person']['lNameP']

                    # People tend to put professional certs after their surname, we can strip this off
                    last_name = re.split(r"[\,\ \(\[]", last_name_raw)[0].lower()
                    # print(last_name, last_name_raw )

                    first_name = result['person']['degree_result_person']['fNameP'].lower()

                    description = result['person']['fmt_headline']

                    self.found_names[linkedin_id] = {"first_name": first_name, "last_name": last_name, "description": description}

                    # TODO problems printing this due to unicode chars?
                    # print(first_name + " " + last_name + " --- " + description + "Linkedin id = " + linkedin_id)

                    if first_name == "" or last_name == "":
                        continue
        else:
            print("HTTP response other than 200. Something went wrong!")

    def write_files(self, directory_name, email_domain):
        print()
        print("This is everything found")
        print(self.found_names)
        print("Writing files to %s" % directory_name)

        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        for linkedin_id, linkedin_names in self.found_names.iteritems():
            first_name = linkedin_names.get("first_name", "").split(' ', 1)[0]
            last_name = linkedin_names.get("last_name", "").split(' ', 1)[0]
            description = linkedin_names.get("description", "")
            print(first_name + "." + last_name)

            if first_name == "" or last_name == "":
                continue

            # TODO other formats worth doing at this point?
            # TODO tidy-up. This is an inefficient way to write files
            with open(os.path.join(directory_name, "linkedin-whos-who.txt"), "a") as myfile:
                myfile.write(first_name + " " + last_name + " --- " + description + "\n")

            if email_domain != '':
                with open(os.path.join(directory_name, "linkedin-john.smith-at-" + email_domain + ".txt"), "a") as myfile:
                    myfile.write(first_name + "." + last_name + "@" + email_domain + "\n")

            with open(os.path.join(directory_name, "linkedin-john.smith.txt"), "a") as myfile:
                myfile.write(first_name + "." + last_name + "\n")

            with open(os.path.join(directory_name, "linkedin-jsmith.txt"), "a") as myfile:
                myfile.write(first_name[0] + last_name + "\n")

            with open(os.path.join(directory_name, "linkedin-johns.txt"), "a") as myfile:
                myfile.write(first_name + last_name[0] + "\n")

            with open(os.path.join(directory_name, "linkedin-smith.txt"), "a") as myfile:
                myfile.write(last_name + "\n")

            with open(os.path.join(directory_name, "linkedin-john.txt"), "a") as myfile:
                myfile.write(first_name + "\n")

if __name__ == "__main__":

    title = '''

      _________.____     ____ ___  ________
     /   _____/|    |   |    |   \/  _____/
     \_____  \ |    |   |    |   /   \  ___
     /        \|    |___|    |  /\    \_\  \.
    /_______  /|_______ \______/  \______  /
            \/         \/                \/


        O) O)
         \\ |
         _\\|_
        (    `\,.      _,--._
        `--^  `. ``-~''   `  `.
         `,    `-_.~/ .    .   `,
           |            `  . `   `._   -----
            `_      _,--._   . .   / --------
              """"``      `"._.."` ----


    Simple LinkedIn Username Generator (SLUG)

    A tool for searching a targeted organisation on LinkedIn,
    and generating username lists (in common username formats),
    based on current and past employees.

    Ben Williams, NCC Group 2016


Example: python slug.py -e example.com XXXXXXXXXX-INSERT-TOKEN-XXXXXXXXXX "Example Plc" 10
    '''

    print(title)

    # TODO add proxy parameter

    logging.basicConfig(format="[%(levelname)s]-%(threadName)s: %(message)s", level=logging.DEBUG)
    directory_name = "usernames-%s" % time.time()
    parser = argparse.ArgumentParser()

    # Need to use an active session token to avoid LinkedIn's bot detection.
    parser.add_argument("token", help="LinkedIn session-token from a currently authenticated session"
                                      " ('li_at' cookie value - This is the big long cookie of around 150 chars).",
                        default='')

    parser.add_argument("company", help="Company or organisation to search on ('Example Plc').",
                        default='')

    parser.add_argument("pages", help="Number of pages to search (Take care, this burns monthly search allowance).",
                        default='')

    parser.add_argument("-p", "--past", help="Include employees who previously worked there (default is current only).",
                        action='store_true', default=False)

    parser.add_argument("--proxy", help="Use a HTTP(S) proxy (mainly for logging or troubleshooting purposes).",
                        default='')

    parser.add_argument("-e", "--emaildomain", help="Email domain to add if generating email addresses (optional). "
                                                    "For example 'example.com'.",
                        default='')

    args = parser.parse_args()

    if args.past:
        companyScope = "CP"  # CP = current and past
    else:
        companyScope = "C"  # C = current

    parser = LinkedInSearch(args.token, args.proxy)
    parser.check_login()
    for page_num in range(1, int(args.pages) + 1):
        # May need to update some of the additional parameters here at some point
        my_params = {'company': args.company,
                     'companyScope': companyScope,
                     'page_num': page_num,
                     # 'openAdvancedForm': "true",
                     # 'locationType': "Y",
                     # 'rsid': "5103664671466070488038",
                     # 'orig': "MDYS",
                     # 'pt': "people",
                     # 'rnd': "1466070506394"
                     }
        parser.do_search(my_params)
    parser.write_files(directory_name, args.emaildomain)

    print("\nFinished!")
