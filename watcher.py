import requests
import json
import configparser
from datetime import datetime
from pytz import timezone

TZ = None

# Get the previous event time from filename.
# If file doesn't exist, write the current time and use it as the previous event time.
def load_previous(filename):
    time_now = datetime.utcnow()
    conf = configparser.ConfigParser()
    conf.read(filename)

    event_str = conf['time']['last_event']
    commit_str = conf['time']['last_commit']

    changed = False
    if len(event_str) == 0:
        prev_event = time_now
        conf['time']['last_event'] = zulu(to_str, time_now)
        changed = True
    else:
        prev_event = zulu(to_datetime, event_str)

    if len(commit_str) == 0:
        prev_commit = time_now
        conf['time']['last_commit'] = zulu(to_str, time_now)
        changed = True
    else:
        prev_commit = zulu(to_datetime, commit_str)

    if changed:
        with open(filename, 'w') as f:
            conf.write(f)
        f.close()
    return prev_event, prev_commit


def save_new_time(filename, time, time_key):
    conf = configparser.ConfigParser()
    conf.read(filename)
    conf['time'][time_key] = zulu(to_str, time)

    with open(filename, 'w') as f:
        conf.write(f)
    f.close()
    


# Send a request to api_url and get the events json.
def get_events_json(api_url, username, token):
    response = requests.get(api_url, auth=(username, token))
    events = response.json()
    return events

def get_commits_json(api_url, username, token):
    response = requests.get(api_url, auth=(username,token))
    commits = response.json()
    return commits

# return a str of datetime object
def to_str(dt, tformat):
    return datetime.strftime(dt, tformat)

# return a datetime obj of timestr
def to_datetime(timestr, tformat):
    return datetime.strptime(timestr, tformat)

# Force Zulu time format for to_str and to_datetime
def zulu(func, param):
    zulu_format = '%Y-%m-%dT%H:%M:%SZ'
    return func(param, zulu_format)

# Returns a datetime object of a single event.
def get_event_time(event):
    return zulu(to_datetime, event['created_at'])

# Fetch all the new events.
# Potentially modifies the Timestamp obj.
def get_new_events(events, prev_time):
    new_events = []

    for e in events:
        event_time = get_event_time(e)
        if event_time > prev_time:
            print("    !new event at ", zulu(to_str, event_time))
            new_events.append(e)

    return new_events

def get_commit_time(commit):
    return zulu(to_datetime, commit['commit']['author']['date'])

def get_new_commits(commits, prev_time):
    new_commits = []

    for c in commits:
        commit_time = get_commit_time(c)
        if commit_time > prev_time:
            print("    !new commit at", zulu(to_str, commit_time))
            new_commits.append(c)

    return new_commits


# thanks, i hate it
def utc_to_local(naive_time):
    local_tz = timezone(TZ)
    utc_tz = timezone("UTC")

    time = utc_tz.localize(naive_time)
    local_time = local_tz.normalize(time)
    
    return local_time

# Parse the event and return a string describing the event.
def parse_event(event):
    user = event['actor']['display_login']
    action = event['type'].strip('Event')

    event_time = get_event_time(event)
    timestamp = utc_to_local(event_time)
    
    result = "{} by {} ({})".format(action, user, datetime.strftime(timestamp, "%a %b %d %I:%M %p"))
    return result

def parse_commit(commit):
    user = commit['commit']['committer']['name']
    msg = commit['commit']['message'].replace('\n', '; ')

    commit_time = get_commit_time(commit)
    timestamp = utc_to_local(commit_time)
    if len(msg) > 30:
        msg = msg[0:30] + "..."

    return "+ {} committed: '{}' ({})".format(user, msg, datetime.strftime(timestamp, "%a %b %d %I:%M %p"))

def run():
    global TZ
    time_file = 'timedata'
    
    config = configparser.ConfigParser()
    config.read('config')
    api_url = config['target']['repo'].strip('"/')
    TZ = config['other']['timezone'].strip('"')
    git_usr = config['target']['token']
    git_token = config['target']['token']


    prev_event_time, prev_commit_time = load_previous(time_file)

    events = get_events_json(api_url + '/events', git_usr, git_token)
    new_events = get_new_events(events, prev_event_time)
    
    commits = get_commits_json(api_url + '/commits', git_usr, git_token)
    new_commits = get_new_commits(commits, prev_commit_time)

    if len(new_events) > 0:
        save_new_time(time_file, get_event_time(new_events[0]), 'last_event')

    if len(new_commits) > 0:
        save_new_time(time_file, get_commit_time(new_commits[0]), 'last_commit')

    messages = []
    for e in new_events:
        text = parse_event(e)
        messages.append(text)

    for c in new_commits:
        text = parse_commit(c)
        messages.append(text)

    return '\n'.join(messages)

def main():
    new_event_msgs = run()
    print(new_event_msgs)

if __name__ == '__main__':
    main()
