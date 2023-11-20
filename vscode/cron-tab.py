from crontab import CronTab
cron = CronTab(user='ECLD0092/Shang')
job = cron.new(command='echo hahahaha' )#'C:/Users/Shang/AppData/Local/Programs/Python/Python312 C:/Users/Shang/WorkSpace/Python/Crawl/vscode/crawl.py' )
job.minute.every(1)
cron.write()