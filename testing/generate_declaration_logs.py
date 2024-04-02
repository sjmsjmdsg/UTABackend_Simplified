import json
import os
import glob
from os.path import join as pjoin
from jinja2 import Template

from uta.config import *

# HTML/CSS/JS Template
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
  table {
    width: 100%;
    border-collapse: collapse;
    overflow: scroll;
  }
  th, td {
    border: 1px solid black;
    text-align: left;
    padding: 8px;
    max-width: 800px;
    word-wrap: break-word;
  }
  pre {
    white-space: pre; /* Keeps the original formatting */
    overflow-x: auto; /* Allows horizontal scrolling */
    margin: 0;
  }
  tr:nth-child(even) {background-color: #f2f2f2;}
  .pink { background-color: pink; }
</style>
<script>
  function togglePink(element) {
    element.classList.toggle('pink');
  }
</script>
</head>
<body>

<h2>Declaration Table</h2>

<table>
  <!-- Table header -->
  <tr>
    <th>Task Dir</th>
    <th>Task</th>
    <th>Task Type</th>
    <th>Sub-Tasks</th>
    <th>Involved App</th>
    <th>Involved Package</th>
    <th>Step Hint</th>
    <th>Fail</th>
    <th>Records</th>
  </tr>

  <!-- Loop over tasks -->
  {% for task_dir_name, data in directories.items() %}
    <!-- First sub-row -->
    <tr>
      <td rowspan="3">{{task_dir_name}}</td>
      <td rowspan="3">{{data['task']}}</td>
      <td rowspan="3">{{data['task_type']}}</td>
      <td rowspan="3">{{data['subtasks']}}</td>
      <td rowspan="3">{{data['involved_app']}}</td>
      <td rowspan="3">{{data['involved_app_package']}}</td>
      <td rowspan="3">{{data['step_hint']}}</td>
      <td rowspan="3"><input type="radio" onclick="togglePink(this.parentNode)"></td>
      <!-- Loop for conversation assistant -->
      {% for (conv_id, conversation) in data['conversation_clarification']|dictsort %}
        <td>{{conversation['assistant']}}</td>
      {% endfor %}
    </tr>

    <!-- Second sub-row for conversation user -->
    <tr>
      {% for (conv_id, conversation) in data['conversation_clarification']|dictsort %}
        <td>{{conversation['user']}}</td>
      {% endfor %}
    </tr>

    <!-- Third sub-row for error -->
    <tr>
      <td colspan="20"><pre>Error: {{data['error']}}</pre></td>
    </tr>
  {% endfor %}
</table>

</body>
</html>
"""

user_id = 'user28'
directories = {}
for task_dir in glob.glob(pjoin(DATA_PATH, user_id) + '/task*'):
    task_dir_name = os.path.basename(task_dir)
    # if task_dir_name in ['task1']:
    #     continue
    data = {}
    with open(task_dir + '/task.json', 'r', encoding='utf-8') as file:
        print(task_dir)
        task_json = json.load(file)
        data['task'] = task_json['task_description']
        data['task_type'] = task_json['task_type']
        data['subtasks'] = str(task_json['subtasks'])
        data['involved_app'] = task_json['involved_app']
        data['involved_app_package'] = task_json['involved_app_package']
        data['step_hint'] = task_json['step_hint']
        data['conversation_clarification'] = {}

        for i in range(0, len(task_json['conversation_clarification']) - 1, 2):
            data['conversation_clarification'][i] = {'assistant': str(task_json['conversation_clarification'][i]),
                                                     'user': str(task_json['conversation_clarification'][i + 1])}
        i = len(task_json['conversation_clarification']) - 1
        if i >= 0:
            data['conversation_clarification'][i] = {'assistant': str(task_json['conversation_clarification'][i]),
                                                     'user': str(task_json['conversation_clarification'][i])}

        data['screenshot'] = {}
        for one_img in glob.glob(task_dir + '/*_annotated.png'):
            try:
                img_name = os.path.basename(one_img)
                idx_key = int(img_name.split('_')[0])
                data['screenshot'][idx_key] = {'img': one_img, 'info': {'rel': str(task_json['relations'][idx_key]),
                                                                        'act': str(task_json['actions'][idx_key])}}
            except:
                break

        if os.path.exists(task_dir + '/declaration_error.json'):
            with open(task_dir + '/declaration_error.json', 'r', encoding='utf-8') as error:
                error_json = json.load(error)
                data['error'] = error_json['traceback']
        else:
            data['error'] = "No error."

    if len(data) > 0:
        directories[task_dir_name] = data

# Generate the final HTML
template = Template(html_template)
html = template.render(directories=directories)

# Write the HTML file
with open(pjoin(DATA_PATH, user_id) + '/declaration_logs.html', 'w', encoding='utf-8') as file:
    file.write(html)

# Notify user
print("HTML file 'declaration_logs.html' generated successfully.")
