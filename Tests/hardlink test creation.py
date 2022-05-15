import subprocess

subprocess.run(f"""mklink /h \"{temp_project_path}/{item}\" \"{temp_project_path}/{item}\" """)