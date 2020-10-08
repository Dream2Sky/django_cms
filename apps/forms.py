class FormMixin(object):

    def get_errors(self):
        if hasattr(self, "errors"):
            errors = self.errors.get_json_data()
            new_errors = dict()
            for key, errors_dicts in errors.items():
                message = list()
                for item in errors_dicts:
                    message.append(item.get("message"))

                new_errors[key] = message
            return new_errors
        else:
            return dict()
