import subprocess

topics = subprocess.run(['kafka-topics', '--list', '--bootstrap-server', 'localhost:9092'], stdout=subprocess.PIPE)\
                   .stdout.decode('utf-8').strip().split('\n')


# Delete all topics
print("Starting deletion of Kafka topics...")
for topic in topics:
    subprocess.run(['kafka-topics', '--delete', '--topic', f'{topic}', '--bootstrap-server', 'localhost:9092'])
print("All topics have been deleted.")

# Create all topics
print("Starting creation of Kafka topics...")
for topic in topics:
    subprocess.run(['kafka-topics', '--create', '--topic', f'{topic}', '--bootstrap-server', 'localhost:9092',
                    '--partitions', '1', 'replication-factor', '1'])
print("All topics have been created.")