import time

class Markdown:

    data = []
    widgets = []

    def __init__(self, data, widgets):
        self.data = data
        self.widgets = widgets

    def render(self):

        text = []
        for widget in self.widgets:
            text.append("\n*{}*".format(widget["title"]))
            for control in widget["controls"]:
                format = control["format"] if "format" in control else ""
                text.append("{}: {}".format(control["title"], self.format_value(format, self.data[control["statusTopic"]])))

        return "\n".join(text)


    def format_value(self, format, value):

        if format in ["temperature", "pressure", "energy"]:
            return "{:.1f}".format(float(value))

        elif format in ["humidity", "ppm", "ppb", "voltage", "power", "rpm"]:
            return "{}".format(int(float(value)))

        elif format == "current":
            return "{:.2f}".format(float(value))

        elif format == "datediff":
            return "{}".format(int((int(time.time()) - int(value)) / 60))

        elif format == "hours":
            hours = int(int(value) / 3600)
            minutes = int((int(value) - hours * 3600) / 60)

            return "{:02d}:{:02d}".format(hours, minutes)

        elif format == "checkbox":
            return "☑️" if value == "1" else "⚪️"


        return value
