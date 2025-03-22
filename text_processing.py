from config import TEMPLATE

def substitute_template(json_data, template_string=TEMPLATE):
    for key, value in json_data.items():
        placeholder = "{" + key + "}"
        if placeholder in template_string:
            template_string = template_string.replace(placeholder, str(value))
    return template_string
