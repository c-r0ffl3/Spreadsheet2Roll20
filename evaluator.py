from lxml.html import builder as E
from lxml import html


def evaluate_script(script: str):
    evaluator = Evaluator()
    evaluated_value = evaluator.eval_given_script(script)
    return evaluated_value


class Evaluator():

    def __init__(self, attr_prefix: str = "attr_",
                 roll_prefix: str = "roll_",
                 default_roll_template: str = "default", ):
        self.ATTR_PREFIX = attr_prefix
        self.ROLL_PREFIX = roll_prefix
        self.DEFAULT_ROLL_TEMPLATE = default_roll_template
        return

    def eval_given_script(self, scr: str):
        script = self.remove_parentheses(scr)
        INPUT: callable = self.input_form
        BUTTON: callable = self.roll_button_form
        TEXTAREA: callable = self.textarea_form
        SELECT: callable = self.select_form
        evaluated = eval(script)

        if type(evaluated) == str:
            return self.simple_input_from(evaluated)

        return evaluated

    def remove_parentheses(self, script: str):
        return script.replace("<<", "").replace(">>", "")

    def simple_input_from(self, attr_name):
        return self.input_form(attr_name, "text")

    def input_form(self, attr_name: str, input_type: str,
                   value: str = "",
                   attributes: dict = None):
        input_form = E.INPUT(
            self.attribute_constructor(
                form_name=f"{self.ATTR_PREFIX}{attr_name}",
                form_type=input_type,
                form_value=value,
                form_attributes=attributes
            )
        )
        return input_form

    def roll_button_form(self, roll_name: str, value: str,
                         attributes: dict = None):
        button_form = E.BUTTON(
            self.attribute_constructor(
                form_name=f"{self.ROLL_PREFIX}{roll_name}",
                form_type="roll",
                form_value=value,
                form_attributes=attributes
            )
        )
        return button_form

    def textarea_form(self, attr_name: str,
                      attributes: dict = None):
        textarea_form = E.TEXTAREA(
            self.attribute_constructor(
                form_name=f"{self.ATTR_PREFIX}{attr_name}",
                form_type="text",
                form_attributes=attributes
            )
        )
        return textarea_form

    def select_form(self, attr_name: str, values: list,
                    attributes: dict = None):
        select_form = E.SELECT(
            *[E.OPTION(value, {"value": value}) for value in values],
            self.attribute_constructor(
                form_name=f"{self.ATTR_PREFIX}{attr_name}",
                form_type="text",
                form_attributes=attributes
            )
        )
        return select_form

    @staticmethod
    def attribute_constructor(form_name: str,
                              form_type: str,
                              form_value: str = "",
                              form_attributes: dict = None,
                              ):
        attribute_dict = {}
        if form_attributes:
            attribute_dict = form_attributes
        attributes: dict = {
            'name': f"{form_name}",
            'type': f"{form_type}",
            'value': f"{form_value}",
        }

        attributes.update(attribute_dict)
        return attributes


if __name__ == '__main__':
    evaluate_script(""" "공격력" """)
    evaluate_script(""" TEXTAREA("설명") """)
    evaluate_script(
        """ BUTTON("자기소개", '''&{template:LHZ} {{skill_name=@{name}}} {{skill_tag_1=@{종족}}} {{skill_tag_2=@{메인_직업}}} {{skill_tag_3=@{서브}}} {{skill_tag_4=@{인물태그}}} {{skill_tag_5=@{성별}}} {{explain=@{백스토리}}}''') """)
    evaluate_script(
        """<< SELECT("신드롬1", ["ANGEL HALO", "BALOR", "BLACK DOG", "BRAM=STOKER", "CHIMAERA", "EXILE", "HANUMAN", "MORPHEUS", "NEUMANN", "ORCUS", "SALAMANDRA", "SOLARIS", "OUROBOROS"]) >>"""
    )
