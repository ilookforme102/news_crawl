from crontab import CronTab

# Create a new cron object
my_cron = CronTab(user=True)  # Use 'user=False' for system-wide crontab
my_cron = CronTab(user='Shang')

# Create a new job
job = my_cron.new(command='python crawl.py')

# Set the job schedule (e.g., every day at 5 am)
job.minute.every(5)


# Alternatively, use a cron-style syntax
# job.setall('0 5 * * *')  # This does the same as above

# Add a comment to the job
job.set_comment("Daily Script Run")

# Write the job to the crontab
my_cron.write()

# List all cron jobs for the current user
for job in my_cron:
    print(job)
