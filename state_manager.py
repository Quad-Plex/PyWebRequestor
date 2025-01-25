import os

import ui


class StateManager:
    def __init__(self, tasks_folder="tasks"):
        self.tasks_folder = tasks_folder
        self.states = {}
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from the 'tasks' folder. Each file represents a task."""
        if not os.path.exists(self.tasks_folder):
            os.makedirs(self.tasks_folder)

        for filename in os.listdir(self.tasks_folder):
            task_name, _ = os.path.splitext(filename)  # Use filename (without extension) as task name
            if task_name:  # Ignore empty filenames
                self.states[task_name] = False  # Default all tasks to "Stopped"

    def save_task(self, task_name):
        """Save a task to the 'tasks' folder."""
        file_path = os.path.join(self.tasks_folder, f"{task_name}.txt")
        with open(file_path, "w") as task_file:
            task_file.write("Task file placeholder.")  # Simple content for now

    def delete_task(self, task_name):
        """Delete a task from the state manager and its file."""
        if task_name in self.states:
            del self.states[task_name]
            return True
        else:
            return False

        file_path = os.path.join(self.tasks_folder, f"{task_name}.txt")
        if os.path.exists(file_path):
            os.remove(file_path)

    def toggle_state(self, task_name):
        """Toggle the state of a task."""
        if task_name in self.states:
            self.states[task_name] = not self.states[task_name]

    def update_task_name(self, old_name, new_name):
        """Update the task name in the state dictionary and rename the file."""
        if old_name in self.states:
            # Update the in-memory state
            self.states[new_name] = self.states.pop(old_name)

            # Rename the associated file
            old_path = os.path.join(self.tasks_folder, f"{old_name}.txt")
            new_path = os.path.join(self.tasks_folder, f"{new_name}.txt")
            if os.path.exists(old_path):
                os.rename(old_path, new_path)

    def is_task_running(self, task_name):
        return self.states.get(task_name, False)

    def get_task_running_state(self, task_name):
        return "Running" if self.is_task_running(task_name) else "Stopped"

    def get_task_running_icon(self, task_name):
        return ui.play_icon if self.is_task_running(task_name) else ui.stop_icon
