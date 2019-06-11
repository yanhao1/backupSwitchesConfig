import time
import datetime
import pymysql
import pexpect
import sys
import os


def H3CAutoConfig(ip):
    ssh = pexpect.spawn('ssh -p 22 %s@%s ' % (sshUserName, ip[0]))

    try:
        ssh.expect('[Pp]assword:', timeout=5)
        ssh.sendline(sshPassword)
        sshInfo = ssh.expect(['>$', '[Pp]assword:'])
        if sshInfo == 0:
            ssh.sendline('screen-length disable')
            logfileid = open(LogFileName + "/" + ip[0] + ".txt",
                             "ab")
            ssh.logfile = logfileid
            ssh.expect([">$", "]$"])
            ssh.sendline("dis cur")
            ssh.expect([">$", "]$"])
            ssh.close()
        else:
            ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " Password Error. \n")
            ssh.close()
    except pexpect.EOF:
        ssh.close()
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " ssh failed.(EOF) \n")
    except pexpect.TIMEOUT:
        ssh.close()
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " ssh failed.(TIMEOUT) \n")


def HuaweiAutoConfig(ip):
    ssh = pexpect.spawn('ssh -p 22 %s@%s ' % (sshUserName, ip[0]))

    try:
        ssh.expect('[Pp]assword:', timeout=5)
        ssh.sendline(sshPassword)
        sshInfo = ssh.expect(['>$', '[Pp]assword:'])
        if sshInfo == 0:
            ssh.sendline('screen-length 0 temporary')
            logfileid = open(LogFileName + "/" + ip[0] + ".txt", "ab")
            ssh.logfile = logfileid
            ssh.expect([">$", "]$"])
            ssh.sendline("dis cur")
            ssh.expect([">$", "]$"])
            ssh.close()
        else:
            ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " Password Error. \n")
            ssh.close()

    except pexpect.EOF:
        ssh.close()
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " ssh failed.(EOF) \n")
    except pexpect.TIMEOUT:
        ssh.close()
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " ssh failed.(TIMEOUT) \n")


def RuijieAutoConfig(ip):
    ssh = pexpect.spawn('ssh -p 22 %s@%s ' % (sshUserName, ip[0]))

    try:
        ssh.expect('[Pp]assword: ', timeout=5)
        ssh.sendline(sshPassword)
        sshInfo = ssh.expect(['#$', '[Pp]assword:'])
        if sshInfo == 0:
            ssh.sendline('terminal length 0')
            logfileid = open(LogFileName + "/" + ip[0] + ".txt", "ab")
            ssh.logfile = logfileid
            ssh.expect("#$")
            ssh.sendline("sh run")
            ssh.expect("#$")
            ssh.close()
        else:
            ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " Password Error. \n")
            ssh.close()

    except pexpect.EOF:
        ssh.close()
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " ssh failed.(EOF) \n")
    except pexpect.TIMEOUT:
        ssh.close()
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " ssh failed.(TIMEOUT) \n")


sshUserName = 'yanhao'
sshPassword = 'yanhao@@@'

date_date = datetime.datetime.now().strftime("%Y-%m-%d")

LogFileName = "/home/tools/swtools/swConfigBackup/" + date_date
os.system("mkdir -p %s" % LogFileName)

ErrorLog = open(LogFileName + "/error-" + str(date_date) + ".log", "a")

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='test_scp', )
cur = conn.cursor()

cur.execute("SELECT swip,model,labname,vendor from network1.swinfo_conf ")

AllSwIP = cur.fetchall()
aliveIp = []
finishFping = 0
finishCommand = 0

for ip in AllSwIP:
    i = os.system("/usr/local/sbin/fping  -q %s" % ip[0])
    if i != 0:
        ErrorLog.write(ip[2] + " " + ip[1] + " " + ip[0] + " is unreachable \n")
        finishFping += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishFping) + '/' + str(len(AllSwIP)))
        sys.stdout.flush()
    else:
        aliveIp.append(ip)
        finishFping += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishFping) + '/' + str(len(AllSwIP)))
        sys.stdout.flush()

for ip in aliveIp:
    if ip[2] == 'H3C':
        H3CAutoConfig(ip)
        finishCommand += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishCommand) + '/' + str(len(aliveIp)))
        sys.stdout.flush()
    elif ip[2] == 'Huawei':
        HuaweiAutoConfig(ip)
        finishCommand += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishCommand) + '/' + str(len(aliveIp)))
        sys.stdout.flush()
    elif ip[2] == 'Ruijie':
        RuijieAutoConfig(ip)
        finishCommand += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishCommand) + '/' + str(len(aliveIp)))
        sys.stdout.flush()
    elif ip[2] == 'Cisco':
        RuijieAutoConfig(ip)
        finishCommand += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishCommand) + '/' + str(len(aliveIp)))
        sys.stdout.flush()
    else:
        # print("The vendor of %s is %s ,and this tool can not support" % (ip[0],ip[3]))
        ErrorLog.write(ip[0] + " " + ip[3] + " this tool can not support \n")
        finishCommand += 1
        sys.stdout.write('\r')
        sys.stdout.write(str(finishCommand) + '/' + str(len(aliveIp)))
        sys.stdout.flush()

ErrorLog.close()



NowTime = datetime.datetime.now()

BackupFileList = list(os.listdir("/home/tools/swtools/swConfigBackup"))
for BackupFile in BackupFileList:
    filetime = datetime.datetime.fromtimestamp(os.path.getmtime("/home/tools/swtools/swConfigBackup/%s" % BackupFile))
    if (NowTime - filetime).seconds > 2592000:
        os.system("rm -rf /home/tools/swtools/swConfigBackup/%s" % BackupFile)
        print("/home/tools/swtools/swConfigBackup/%s has been removed" % BackupFile)
