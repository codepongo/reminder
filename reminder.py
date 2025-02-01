import gradio as gr
from datetime import datetime
import os
import json
import sys

TASKS_FILE = os.path.join(os.path.realpath('.'), 'tasks.json')
favicon = os.path.join(os.path.realpath('.'), 'favicon.ico')

server_port = 8002
password = 'passworD000' if 'PASSWORD' not in os.environ else os.environ['PASSWORD']

if len(sys.argv) > 1:
    try:
        server_port = int(sys.argv[1])
    except ValueError as e:
        pass


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding='utf-8') as f:
        json.dump(tasks, f)

priority_emoji = {
        '0-Hight': '❗❗❗',    # High
        '1-Medium': '❗❗',     # Medium
        '2-Low': '❗',          # Low
}

with gr.Blocks(theme=gr.themes.Default(primary_hue="emerald"),
                title="reminder",
) as demo:
    gr.HTML("<h1><center>Race against time and work towards the goals!</center></h1>")
    state = gr.State(True)
    @gr.render(inputs=state)
    def render(s):
        global state
        task_list = load_tasks()
        incomplete = []
        complete =[]
        for task in task_list:
            if task["status"] == "":
                incomplete.append(task)
            else:
                complete.append(task)
        with gr.Tab(f"Incomplete Tasks ({len(incomplete)})"):
            for task in incomplete:
                with gr.Column(variant='panel'):
                    with gr.Row():
                        title = gr.Textbox(task['title'], scale=9, placeholder="title", show_label=False, container=False)
                        def update_title(title, task=task):
                            task['title'] = title
                            save_tasks(task_list)
                            return
                        title.change(update_title, inputs=[title],outputs=None)
                    
                        done_btn = gr.Button("Done", scale=0, variant="primary")
                        def update_status(state, task=task):
                            task["status"] = 'Done'
                            save_tasks(task_list)
                            state = not state
                            return state
                        done_btn.click(update_status, [state], [state])
                        brief = f'''{priority_emoji[task['priority']]} | 📅 {task['ETA']}  📝{task['note']} '''
                    with gr.Accordion(brief,open=False):
                        note = gr.Textbox(value=task['note'], placeholder="note", lines=2,show_label=False, container=False)
                        priority = gr.Dropdown(choices=['0-Hight','1-Medium', '2-Low'],
                                                value=task['priority'],interactive=True)
                        with gr.Row():
                            ct = gr.DateTime(label="Creation Time", type='string', value=task['CT'], interactive=True)
                            eta = gr.DateTime(label="Estimated Time of Arrival", type='string', value=task['ETA'], interactive=True)
                            ee = gr.Number(label="Estimated Effort", value=task['EE'], step=0.25,minimum=0, maximum=5)
                        with gr.Row():
                            atd = gr.DateTime(label="Actual Time of Departure", type='string', value=task['ATD'], interactive=True)
                            ata = gr.DateTime(label="Actual Time of Arrival", type='string', value=task['ATA'], interactive=True)
                            ae = gr.Number(label="Actual Effort", value=task['AE'], step=0.25,minimum=0, maximum=5)
                        with gr.Row():
                            delete_btn = gr.Button("Delete", variant="stop")
                            def delete(state, task=task):
                                #task_list.remove(task)
                                task["status"] = 'Dropped'
                                save_tasks(task_list)
                                state = not state
                                return state
                            delete_btn.click(delete, [state], [state])

                            update_btn = gr.Button("Update")
                            def update(state, note, priority, ct, eta, ee, atd, ata, ae, task=task):
                                task['note'] = note
                                task['priority'] = priority
                                task['CT'] = ct
                                task['ETA'] = eta
                                task['EE'] = ee
                                task['ATD'] = atd
                                task['ATA'] = ata
                                task['AE'] = ae
                                save_tasks(task_list)
                                state = not state
                                return state
                            update_btn.click(update, [state, note,priority,ct, eta, ee, atd, ata, ae], [state])
            new_task = gr.Button("Add Task")
            def create(state):
                task_list.append({"title": "",
                                 "note":"",
                                 "priority":"2-Low",
                                 "CT":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 "ETA":"",
                                "ATD":"",
                                "ATA":"",
                                "EE":0,
                                "AE":0,
                                "status": ""})
                save_tasks(task_list)
                state = not state
                return state
            new_task.click(create, [state], [state])
        with gr.Tab(f"Complete Tasks ({len(complete)})"):
            for task in complete:
                status_emoji = {
                        "Done":"✔",
                        "done":"✔",
                        "Dropped":"❌",
                        "dropped":"❌",
                }
                brief = gr.HTML(value=f"<h2>{status_emoji[task['status']]}{priority_emoji[task['priority']]}<b>{task['title']}</b></h2><p>📅From:{task['ATD']} to {task['ATA']}({task['AE']})</p><p>{task['note']}</p>")
                redo = gr.Button(scale=1, value="Redo") 
                def update_status(state, task=task):
                    task["status"] = ''
                    save_tasks(task_list)
                    state = not state
                    return state
                redo.click(update_status, [state], [state])

demo.launch(server_name = '0.0.0.0',
            server_port = server_port,
            favicon_path=favicon,
            auth = ('zuohaitao', password),
        )

