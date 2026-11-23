import json, uuid

BASE = "http://host.docker.internal:8300"


def nid():
    return str(uuid.uuid4())


nodes, conns = [], {}


def add(name, typ, params, pos, ver=1, creds=None, extra=None):
    n = {"id": nid(), "name": name, "type": typ, "typeVersion": ver, "position": pos, "parameters": params}
    if creds:
        n["credentials"] = creds
    if extra:
        n.update(extra)
    nodes.append(n)
    return name


def link(a, b, i=0):
    conns.setdefault(a, {"main": [[]]})
    while len(conns[a]["main"]) <= i:
        conns[a]["main"].append([])
    conns[a]["main"][i].append({"node": b, "type": "main", "index": 0})


YT = {"youTubeOAuth2Api": {"id": "YOUR_YOUTUBE_CREDENTIAL_ID", "name": "YouTube account"}}

# Branch A: nightly render
a1 = add("Render trigger 02:00", "n8n-nodes-base.scheduleTrigger", {"rule": {"interval": [{"field": "cronExpression", "expression": "0 2 * * *"}]}}, [0, 0], 1.2)
a2 = add("Render today's batch", "n8n-nodes-base.httpRequest", {"method": "POST", "url": BASE + "/render?n=4", "options": {"timeout": 30000}}, [240, 0], 4.2)
link(a1, a2)

# Branch B: morning upload
b1 = add("Upload trigger 09:00", "n8n-nodes-base.scheduleTrigger", {"rule": {"interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]}}, [0, 300], 1.2)
b2 = add("Get rendered videos", "n8n-nodes-base.httpRequest", {"method": "GET", "url": BASE + "/pending", "options": {"timeout": 30000}}, [240, 300], 4.2)
b3 = add("Split videos", "n8n-nodes-base.splitOut", {"fieldToSplitOut": "items", "options": {}}, [480, 300], 1)
b4 = add("One at a time", "n8n-nodes-base.splitInBatches", {"batchSize": 1, "options": {}}, [720, 300], 3)
b5 = add("Download video file", "n8n-nodes-base.httpRequest", {"method": "GET", "url": "=" + BASE + "/file/{{ $json.slug }}", "options": {"response": {"response": {"responseFormat": "file", "outputPropertyName": "data"}}, "timeout": 300000}}, [960, 300], 4.2)
b6 = add("Upload to YouTube", "n8n-nodes-base.youTube", {
    "resource": "video", "operation": "upload",
    "title": "={{ $('One at a time').item.json.title }}",
    "regionCode": "US", "categoryId": "27", "binaryProperty": "data",
    "options": {"description": "={{ $('One at a time').item.json.description }}", "privacyStatus": "public", "selfDeclaredMadeForKids": "={{ $('One at a time').item.json.made_for_kids }}", "defaultLanguage": "en", "notifySubscribers": False}},
    [1200, 300], 1, YT)
b7 = add("Declare AI-generated media", "n8n-nodes-base.httpRequest", {
    "method": "PUT", "url": "https://www.googleapis.com/youtube/v3/videos?part=status",
    "authentication": "predefinedCredentialType", "nodeCredentialType": "youTubeOAuth2Api",
    "sendBody": True, "specifyBody": "json",
    "jsonBody": "={\"id\": \"{{ $json.id }}\", \"status\": {\"privacyStatus\": \"public\", \"selfDeclaredMadeForKids\": {{ $('One at a time').item.json.made_for_kids }}, \"containsSyntheticMedia\": true}}",
    "options": {}}, [1440, 300], 4.2, YT)
b8 = add("Mark uploaded", "n8n-nodes-base.httpRequest", {"method": "POST", "url": "=" + BASE + "/uploaded/{{ $('One at a time').item.json.slug }}", "options": {}}, [1680, 300], 4.2)
b9 = add("Wait 40 min between videos", "n8n-nodes-base.wait", {"resume": "timeInterval", "amount": 40, "unit": "minutes"}, [1920, 300], 1.1)
link(b1, b2); link(b2, b3); link(b3, b4)
link(b4, b5, 1)  # loop output
link(b5, b6); link(b6, b7); link(b7, b8); link(b8, b9); link(b9, b4)


SMTP = {"smtp": {"id": "YOUR_SMTP_CREDENTIAL_ID", "name": "SMTP account"}}
b10 = add("Email daily summary", "n8n-nodes-base.emailSend", {
    "fromEmail": "you@example.com", "toEmail": "you@example.com",
    "subject": "={{ 'Daily videos: ' + $('Upload to YouTube').all().length + ' videos uploaded today' }}",
    "emailFormat": "text",
    "text": "={{ 'Uploaded today:\n\n' + $('Upload to YouTube').all().map(i => (i.json.snippet ? i.json.snippet.title : 'video') + '\nhttps://youtu.be/' + i.json.id).join('\n\n') + '\n\nQueue remaining: ' + $('Get rendered videos').first().json.queue_dir_remaining }}",
    "options": {}}, [960, 520], 2.1, SMTP)
link(b4, b10, 0)

wf = {"name": "Daily faceless video pipeline", "nodes": nodes, "connections": conns, "settings": {"executionOrder": "v1"}, "active": False, "id": "ytdailyvideos01"}
json.dump([wf], open("youtube-daily-videos.json", "w", encoding="utf-8"), indent=1)
print("workflow written")
