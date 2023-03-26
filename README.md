# Felix Break Reminder

A simple break reminder application that helps you maintain a healthy work routine by notifying you to take breaks after a specified duration of work.

## Features

- Customizable work duration, idle time threshold, and overdue nudge frequency
- Uses Windows native notifications and/or Tkinter-based custom notifications
- Checks user idle time (time since last keyboard/mouse input) to automatically reset the work timer

## Dependencies

Python 3.7 or higher
Plyer
Tkinter (included in the Python standard library)
Install the required package using the following command:

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the break_reminder.py script in your Python environment:

```
python break_reminder.py
```

### User-Configurable Parameters

There are three user-configurable parameters in the source code to customize the break reminder behavior:

1. `work_duration_minutes`: This parameter defines the maximum duration you should work before taking a break. Once you've been active for this duration, the application will notify you to take a break.

2. `idle_time_threshold_minutes`: This parameter represents the minimum duration of a break. The application considers a period of inactivity longer than this value as a break. After such a break, the work timer resets, and the notification cycle starts over.

3. `overdue_nudge_frequency_minutes`: If you continue working after the initial break reminder, the application will nudge you with additional reminders at this frequency until you take a break longer than `idle_time_threshold_minutes`.

By default, these parameters are set to 45, 3, and 5 minutes respectively.

Tailor the break reminder experience to your needs by setting your own values for these three parameters. For your convenience, they can be found close to the top of the `break_reminder.py` file. Open the file in any editor (such as notepad or vscode) and change the values. 

The application will run in the background and send notifications according to the user-configurable parameters.

## License

This project is licensed under the terms of the MIT License. See the LICENSE file for details.
