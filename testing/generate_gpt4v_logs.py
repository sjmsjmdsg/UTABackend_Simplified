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
    table-layout: auto;
  }
  th, td {
    border: 1px solid black;
    text-align: left;
    padding: 8px;
    word-wrap: break-word;
    overflow: hidden;
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

<h2>Screenshots and Action Table</h2>

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
    <tr>
      <td rowspan="3">{{task_dir_name}}</td>
      <td rowspan="3">{{data['task']}}</td>
      <td rowspan="3">{{data['task_type']}}</td>
      <td rowspan="3">{{data['subtasks']}}</td>
      <td rowspan="3">{{data['involved_app']}}</td>
      <td rowspan="3">{{data['involved_app_package']}}</td>
      <td rowspan="3">{{data['step_hint']}}</td>
      <td rowspan="3"><input type="radio" onclick="togglePink(this.parentNode)"></td>
      {% for (key, screenshot) in data['screenshot']|dictsort %}
        <td>
          <img src="{{screenshot['img']}}" alt="Screenshot_{{key}}" style="width:200px">
        </td>
      {% endfor %}
    </tr>

    <tr>
      {% for (key, screenshot) in data['screenshot']|dictsort %}
        <td>
          <input type="radio" onclick="togglePink(this.parentNode)">
          <p>Relation & Action: {{screenshot['info']['rel']}}</p>
        </td>
      {% endfor %}
    </tr>

    <!-- Sub-row for error -->
    <tr>
      <td colspan="20"><pre>Error: {{data['error']}}</pre></td>
    </tr>
  {% endfor %}
</table>

</body>
</html>
"""


user_id = '31'
user = 'user' + user_id
directories = {}
with open(pjoin(WORK_PATH, f'old_test_data/test/gpt-v/result{user_id}.json')) as filr:
    gpt4v_json = json.load(filr)
    for task_dir in glob.glob(pjoin(DATA_PATH, user) + '/task*'):
        task_dir_name = os.path.basename(task_dir)
        data = {}
        with open(task_dir + '/task.json', 'r', encoding='utf-8') as file:
            task_json = json.load(file)
            data['task'] = task_json['task_description']
            data['task_type'] = task_json['task_type']
            data['subtasks'] = str(task_json['subtasks'])
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
                    img_path = f".{one_img.split(user)[-1]}"
                    data['screenshot'][idx_key] = {'img': img_path, 'info': {'rel': str(gpt4v_json[task_dir_name]
                                                                                        [img_name.replace('_annotated', '')])}}
                except:
                    break

            data['error'] = "No error."

        if len(data) > 0:
            directories[task_dir_name] = data

# Generate the final HTML
template = Template(html_template)
html = template.render(directories=directories)

# Write the HTML file
with open(pjoin(DATA_PATH, user) + '/gpt4v_logs.html', 'w', encoding='utf-8') as file:
    file.write(html)

# Notify user
print("HTML file 'automation_logs.html' generated successfully.")