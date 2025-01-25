from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QPushButton, QLabel, QListWidgetItem, QDialog, QLineEdit,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon
from state_manager import StateManager

stop_icon="assets/stop.png"
play_icon="assets/play.png"

class WebRequestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.running_header = None
        self.console_header = None
        self.stop_button = None
        self.play_button = None
        self.add_task_button = None
        self.list_widget = None
        self.text_output = None
        self.state_manager = StateManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AppZoneAutomator")
        self.setGeometry(100, 100, 600, 400)

        # Layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # List Widget (Left)
        self.list_widget = QListWidget()
        self.populate_list()
        self.list_widget.currentItemChanged.connect(self.on_item_selected)

        # Task List
        task_list_layout = QVBoxLayout()
        self.add_task_button = QPushButton("Add Empty Task")
        self.add_task_button.clicked.connect(self.create_new_task)

        task_list_layout.addWidget(self.list_widget)

        # Play/Stop Buttons (First Row)
        button_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.play_button.clicked.connect(self.toggle_task)
        self.stop_button.clicked.connect(self.toggle_task)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)

        # Combine into Left Layout
        left_layout.addLayout(task_list_layout, Qt.AlignTop)  # Task list and 'Add Task' button
        left_layout.addLayout(button_layout, Qt.AlignTop)     # Play/Stop buttons
        left_layout.addWidget(self.add_task_button)      # Add new Task button

        # Console Header
        header_layout = QHBoxLayout()
        self.console_header = QLabel()
        self.console_header.setStyleSheet("font-size: 18px; font-weight: bold")
        self.running_header = QLabel()
        self.running_header.setStyleSheet("font-size: 18px; font-weight: bold")
        header_layout.addWidget(self.console_header)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        header_layout.addWidget(self.running_header)
        right_layout.addLayout(header_layout)

        # Text Output (Right)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("background-color: black; color: white; font-family: Consolas; font-size: 14px;")
        right_layout.addWidget(self.text_output)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        self.setLayout(main_layout)

    def populate_list(self):
        """Populate the list with items and their icons."""
        self.list_widget.clear()  # Clear the list first

        for task_name, is_running in self.state_manager.states.items():
            # Create a QListWidgetItem
            item = QListWidgetItem(self.list_widget)  # Pass the list widget as parent
            icon = QIcon(stop_icon if not is_running else play_icon)
            item.setIcon(icon)
            # Create a custom widget for the list item
            item_widget = TaskListItemWithButton(task_name, self.start_task_edit, self.delete_task)
            item.setSizeHint(item_widget.sizeHint())  # Set size hint
            # Set the custom widget for the QListWidgetItem
            self.list_widget.setItemWidget(item, item_widget)


    def update_list_item_icon(self, task):
        """Update the icon for a specific list item."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            custom_widget = self.list_widget.itemWidget(item)
            if isinstance(custom_widget, TaskListItemWithButton) and custom_widget.task_name == task:
                icon = QIcon(stop_icon if not self.state_manager.states[task] else play_icon)
                item.setIcon(icon)

    def on_item_selected(self, current, previous):
        if current:
            task = self.list_widget.itemWidget(current).task_name
            self.console_header.setText(f"{task}")
            self.running_header.setText(f"{self.state_manager.get_task_running_state(task)}")
            self.update_buttons(task)

    def update_buttons(self, task):
        if task:
            """Enable/disable buttons based on task state."""
            if self.state_manager.states[task]:
                self.play_button.setEnabled(False)
                self.stop_button.setEnabled(True)
            else:
                self.play_button.setEnabled(True)
                self.stop_button.setEnabled(False)

    def toggle_task(self):
        """Toggle task state and update UI."""
        current_item = self.list_widget.currentItem()
        if current_item:
            task = self.list_widget.itemWidget(current_item).task_name
            self.state_manager.toggle_state(task)
            self.console_header.setText(f"{task}")
            self.running_header.setText(f"{self.state_manager.get_task_running_state(task)}")
            self.update_list_item_icon(task)
            self.update_buttons(task)

    def create_new_task(self):
        task_name = f"New Task {len(self.state_manager.states) + 1}"
        self.state_manager.states[task_name] = False
        self.state_manager.save_task(task_name)
        self.populate_list()

    def delete_task(self, task_name=None):
        """Popup Window to delete the selected task."""
        if task_name:
            # Create a dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Delete Task: {task_name}")
            dialog.setModal(True)
            dialog.setGeometry(200, 200, 300, 150)

            # Dialog layout
            layout = QVBoxLayout()

            # Label and input field
            label = QLabel(f"Are you sure you want to delete {task_name}?")
            layout.addWidget(label)

            # Save and Cancel buttons
            button_layout = QHBoxLayout()
            delete_button = QPushButton("Yes, delete")
            cancel_button = QPushButton("No")
            button_layout.addWidget(delete_button)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)
            dialog.setLayout(layout)

            # Connect buttons
            delete_button.clicked.connect(lambda: self.execute_task_delete(dialog, task_name))
            cancel_button.clicked.connect(dialog.reject)

            # Show dialog
            dialog.exec_()

    def start_task_edit(self, task_name=None):
        """Popup Window to edit details for the selected task."""
        if task_name:
            # Create a dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Task: {task_name}")
            dialog.setModal(True)
            dialog.setGeometry(200, 200, 300, 150)

            # Dialog layout
            layout = QVBoxLayout()

            # Label and input field
            label = QLabel("Edit task details:")
            input_field = QLineEdit()
            input_field.setText(task_name)  # Prepopulate with current task name
            layout.addWidget(label)
            layout.addWidget(input_field)

            # Save and Cancel buttons
            button_layout = QHBoxLayout()
            save_button = QPushButton("Save")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(save_button)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)
            dialog.setLayout(layout)

            # Connect buttons
            save_button.clicked.connect(lambda: self.save_task_edit(dialog, input_field.text(), task_name))
            cancel_button.clicked.connect(dialog.reject)

            # Show dialog
            dialog.exec_()

    def execute_task_delete(self, dialog, task_name):
        if task_name:
            success = self.state_manager.delete_task(task_name)
            dialog.accept()
            if not success:
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("Error")
                error_dialog.setModal(True)
                error_layout = QVBoxLayout()
                error_message = QLabel("Couldn't delete Task!")
                close_button = QPushButton("Close")
                close_button.clicked.connect(error_dialog.accept)
                error_layout.addWidget(error_message)
                error_layout.addWidget(close_button)
                error_dialog.setLayout(error_layout)
                error_dialog.exec_()


    def save_task_edit(self, dialog, new_name, old_name):
        """Handle saving the edited task name."""
        if new_name.strip():
            # Update task name in state manager
            self.state_manager.update_task_name(old_name, new_name)

            # Update UI list
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                item_widget = self.list_widget.itemWidget(item)
                if item_widget.task_name == old_name:
                    item_widget.task_name = new_name
                    item_widget.task_label.setText(new_name)
                    break

            # Close dialog
            dialog.accept()
        else:
            # Optional: Show an error message if the input is empty
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Error")
            error_dialog.setModal(True)
            error_layout = QVBoxLayout()
            error_message = QLabel("Task name cannot be empty!")
            close_button = QPushButton("Close")
            close_button.clicked.connect(error_dialog.accept)
            error_layout.addWidget(error_message)
            error_layout.addWidget(close_button)
            error_dialog.setLayout(error_layout)
            error_dialog.exec_()

class TaskListItemWithButton(QWidget):
    def __init__(self, task_name, edit_callback, delete_callback):
        super().__init__()
        self.task_name = task_name
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback

        # Layout for the custom widget
        task_layout = QHBoxLayout()
        task_layout.setContentsMargins(0, 0, 0, 0)

        # Task name label
        self.task_label = QLabel(self.task_name)
        task_layout.addWidget(self.task_label)

        # Edit button
        self.edit_button = QPushButton("📝")
        self.edit_button.setFixedSize(22, 22)  # Small button
        self.edit_button.clicked.connect(self.edit_task)
        task_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("🗑")
        self.delete_button.setFixedSize(22, 22)  # Small button
        self.delete_button.clicked.connect(self.delete_task)
        task_layout.addWidget(self.delete_button)

        self.setLayout(task_layout)

    def edit_task(self):
        self.edit_callback(self.task_name)

    def delete_task(self):
        self.delete_callback(self.task_name)
